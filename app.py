# app.py
import concurrent.futures
import configparser
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QPoint, QSharedMemory, Qt, QThread, Signal
from PySide6.QtGui import QAction, QColor, QCursor, QIcon, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QSystemTrayIcon,
    QWidget,
    QWidgetAction,
)

from ContextMenu_ui import Ui_ContextMenuWidget

if platform.system() == "Windows":
    import winreg
else:
    winreg = None


class PortScannerWorker(QThread):
    """后台异步端口检测线程，防止网络请求阻塞UI线程"""

    scan_finished = Signal(bool, str, str)  # 信号：(是否成功, 代理名称, 端口号)

    def __init__(self, target_port, preset_ports):
        super().__init__()
        self.target_port = target_port
        self.preset_ports = preset_ports

    def run(self):
        def check_port(name, port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    # 本地通信，300ms足以保证结果返回且不占用过久后台资源
                    sock.settimeout(0.3)
                    if sock.connect_ex(("127.0.0.1", int(port))) == 0:
                        return True, name, str(port)
            except Exception:
                pass
            return False, None, None

        ports_to_check = self.preset_ports.copy()
        if self.target_port is not None:
            target_str = str(self.target_port)
            if target_str not in ports_to_check.values():
                ports_to_check["自定义"] = target_str

        open_ports = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(check_port, name, port)
                for name, port in ports_to_check.items()
            ]
            for future in concurrent.futures.as_completed(futures):
                success, name, port = future.result()
                if success:
                    open_ports[port] = name

        if not open_ports:
            self.scan_finished.emit(False, "", "")
            return

        target_str = str(self.target_port)
        if self.target_port is not None and target_str in open_ports:
            self.scan_finished.emit(True, open_ports[target_str], target_str)
        else:
            port = next(iter(open_ports.keys()))
            self.scan_finished.emit(True, open_ports[port], port)


class ContextMenuWidget(QWidget):
    """单独的上下文菜单窗口部件，用于包含UI组件"""

    def __init__(self, parent=None):
        super(ContextMenuWidget, self).__init__(parent)
        self.ui = Ui_ContextMenuWidget()
        self.ui.setupUi(self)
        self.setup_style()

    def setup_style(self):
        """设置控件样式"""
        self.ui.proxyButton.setStyleSheet("""
            #proxyButton {
                border-radius: 0px;
                background-color:rgba(161, 58, 58, 0.39);
            }
            #proxyButton:checked {
                background-color: rgb(0, 197, 144);
            }
            """)

        self.ui.autoStartButton.setStyleSheet("""
            #autoStartButton {
                border-radius: 0px;
                background-color: transparent;
            }
            #autoStartButton:hover {
                background-color: rgba(130, 130, 130, 0.08);
            }
            #autoStartButton:checked {
                background-color: rgba(130, 130, 130, 0.08);
                color: #836d6d;
            }
            """)

        self.ui.exitButton.setStyleSheet("""
            #exitButton {
                border-radius: 0px;
                background-color: transparent;
            }
            #exitButton:hover {
                background-color: rgba(130, 130, 130, 0.08);
            }
            """)


class ContextMenuAction(QWidgetAction):
    """将UI控件包装为QAction以便在QMenu中使用"""

    def __init__(self, parent=None):
        super(ContextMenuAction, self).__init__(parent)
        self.context_menu_widget = ContextMenuWidget()
        self.setDefaultWidget(self.context_menu_widget)

    def get_ui(self):
        """获取UI控件引用"""
        return self.context_menu_widget.ui


class MainWindow:
    def __init__(self):
        # 初始化变量
        self.default_port = 10808
        self.current_port = self.default_port
        self.preset_port: Dict[str, str] = {
            "V2Ray": "10808",
            "Clash": "7890",
            "SingBox": "60011",
        }

        self.is_linux = platform.system() == "Linux"

        self.ui = None
        self.status_label = None
        self.proxy_button = None
        self.port_input = None
        self.port_list_button = None
        self.auto_start_button = None
        self.exit_button = None

        self.status_action = None
        self.toggle_proxy_action = None

        self.scanner_worker = None

        # 缓存所有图像资源（极大减少磁盘IO与重绘）
        self.icons = {
            "ok": QIcon(resource_path("icon/status_ok.svg")),
            "warning": QIcon(resource_path("icon/status_warning.svg")),
            "off": QIcon(resource_path("icon/status_off.svg")),
            "selected": self._generate_selected_icon(),
        }

        self.create_tray_menu()
        self.setup_tray()

        self.init_git_proxy_status_and_tooltip()

        if platform.system() == "Windows":
            self.check_auto_start_status()

        self.show_startup_message()

    def _generate_selected_icon(self) -> QIcon:
        """提前缓存高亮选中的图标，避免每次展开菜单时重绘"""
        icon = QIcon(resource_path("icon/select.svg"))
        if not icon.isNull():
            pixmap = icon.pixmap(4, 4)
            painter = QPainter(pixmap)
            gradient = QLinearGradient(0, 0, pixmap.width(), pixmap.height())
            gradient.setColorAt(0, QColor("#1b8094"))
            gradient.setColorAt(1, QColor("#4fc3f7"))
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), gradient)
            painter.end()
            return QIcon(pixmap)
        return QIcon()

    def show_startup_message(self):
        self.tray_icon.showMessage(
            "Git Proxy Switch",
            "程序已启动并驻留在系统托盘",
            QSystemTrayIcon.MessageIcon.Information,
            10,
        )

    def create_tray_menu(self):
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet("""
            QMenu {
                border-radius: 0px;
            }
            """)
        if self.is_linux:
            self.setup_linux_menu()
        else:
            self.setup_windows_menu()

    def setup_linux_menu(self):
        self.status_action = QAction("代理状态: 未启用", self.tray_menu)
        self.status_action.setEnabled(False)
        self.tray_menu.addAction(self.status_action)
        self.tray_menu.addSeparator()

        self.toggle_proxy_action = QAction("启用git代理", self.tray_menu)
        self.toggle_proxy_action.triggered.connect(self.toggle_proxy)
        self.tray_menu.addAction(self.toggle_proxy_action)

        port_menu = QMenu("设置端口", self.tray_menu)
        self.tray_menu.addMenu(port_menu)

        for name, port in self.preset_port.items():
            action = QAction(f"{name}: {port}", port_menu)
            action.triggered.connect(lambda checked, p=port: self.set_port(p))
            port_menu.addAction(action)

        self.tray_menu.addSeparator()
        self.exit_action = QAction("退出", self.tray_menu)
        self.exit_action.triggered.connect(QApplication.instance().quit)
        self.tray_menu.addAction(self.exit_action)

    def setup_windows_menu(self):
        self.menu_action = ContextMenuAction(self.tray_menu)
        self.tray_menu.addAction(self.menu_action)

        self.ui = self.menu_action.get_ui()
        self.status_label = self.ui.statusLabel
        self.proxy_button = self.ui.proxyButton
        self.port_input = self.ui.portInput
        self.port_list_button = self.ui.portListButton
        self.auto_start_button = self.ui.autoStartButton
        self.exit_button = self.ui.exitButton

        self.ui.portInput.setText(str(self.current_port))
        self.setup_connections()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.icons["off"])
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def setup_connections(self):
        if not self.is_linux:
            self.ui.proxyButton.clicked.connect(self.toggle_proxy)
            self.ui.portInput.editingFinished.connect(self.update_port)
            self.ui.portListButton.clicked.connect(self.show_port_list)
            self.ui.autoStartButton.clicked.connect(self.toggle_auto_start)
            self.ui.exitButton.clicked.connect(QApplication.instance().quit)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Context:
            if self.is_linux:
                cursor_pos = QCursor.pos()
                self.tray_menu.popup(cursor_pos)
            else:
                geometry = self.tray_icon.geometry()
                self.tray_menu.popup(
                    QPoint(geometry.x(), geometry.y() - self.tray_menu.height())
                )
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.is_linux:
                self.toggle_proxy()
            else:
                self.proxy_button.setChecked(not self.proxy_button.isChecked())
                self.toggle_proxy()

    def update_menu_status(
        self, git_proxy_enabled: bool, port: int = None, editMode=False, init_mode=False
    ):
        """第一阶段：立即更新界面的响应（零卡顿）"""
        if self.is_linux:
            self.update_linux_menu_status_ui(git_proxy_enabled, port)
        else:
            self.update_git_proxy_status_ui(git_proxy_enabled, port, editMode)

        # 触发第二阶段：后台异步扫描端口确认图标变色
        self.check_ports_async(git_proxy_enabled, port, init_mode)

    def update_linux_menu_status_ui(self, git_proxy_enabled: bool, port: int = None):
        """Linux UI文本更新"""
        port = port if port is not None else self.current_port
        proxy_url = f"http://127.0.0.1:{port}"

        if git_proxy_enabled:
            self.status_action.setText(f"代理状态: 已启用 ({proxy_url})")
            self.toggle_proxy_action.setText("禁用git代理")
        else:
            self.status_action.setText("代理状态: 已禁用")
            self.toggle_proxy_action.setText("启用git代理")

    def update_git_proxy_status_ui(
        self, git_proxy_enabled: bool, port: int = None, editMode=False
    ):
        """Windows UI文本更新"""
        port = port if port is not None else self.current_port
        proxy_url = f"http://127.0.0.1:{port}"
        self.ui.portInput.setText(str(port))

        if git_proxy_enabled:
            status_label_text = f'<span style="color: green;">git代理已{"切换" if editMode else "启用"}<br/>{proxy_url}</span>'
            self.ui.proxyButton.setText("禁用git代理")
            self.ui.proxyButton.setChecked(False)
        else:
            status_label_text = '<span style="color: gray;">git代理已禁用</span>'
            self.ui.proxyButton.setText("启用git代理")
            self.ui.proxyButton.setChecked(True)

        self.ui.statusLabel.setText(status_label_text)

    def check_ports_async(self, git_proxy_enabled, port, init_mode=False):
        """后台异步检测端口"""
        port = port if port is not None else self.current_port

        # 释放旧的线程连接以防连击污染
        if hasattr(self, "scanner_worker") and self.scanner_worker is not None:
            try:
                self.scanner_worker.scan_finished.disconnect()
            except Exception:
                pass

        self.scanner_worker = PortScannerWorker(port, self.preset_port)
        self.scanner_worker.scan_finished.connect(
            lambda success, name, p: self._on_scan_finished(
                success, name, p, git_proxy_enabled, port, init_mode
            )
        )
        self.scanner_worker.start()

    def _on_scan_finished(
        self,
        proxy_running,
        proxy_name,
        proxy_port,
        git_proxy_enabled,
        target_port,
        init_mode,
    ):
        """第二阶段：扫描完成后的回调，更新Tooltip和托盘Icon"""

        # 兼容启动时的自启逻辑
        if init_mode and proxy_running and not git_proxy_enabled:
            self.set_git_proxy(True, int(proxy_port))
            git_proxy_enabled = True
            target_port = int(proxy_port)
            self.current_port = target_port
            # 重刷UI
            if self.is_linux:
                self.update_linux_menu_status_ui(git_proxy_enabled, target_port)
            else:
                self.update_git_proxy_status_ui(git_proxy_enabled, target_port)

        port_name = {v: k for k, v in self.preset_port.items()}.get(
            str(target_port), "其他"
        )
        proxy_url = f"http://127.0.0.1:{target_port}"

        tooltip = "Git Proxy Switch"
        tooltip += f"\n端口: {target_port}"

        if git_proxy_enabled:
            tooltip += "\n状态: 已启用"
            tooltip += f"\n代理: {proxy_url}"

            if proxy_running:
                if int(proxy_port) == int(target_port):
                    self.tray_icon.setIcon(self.icons["ok"])
                else:
                    tooltip += f"\n\n- 当前端口 {target_port} 不可用"
                    tooltip += f"\n- {proxy_name} : {proxy_port} 正在运行"
                    self.tray_icon.setIcon(self.icons["warning"])
            else:
                self.tray_icon.setIcon(self.icons["warning"])
                tooltip += "\n\n- 当前端口不可用！"
                tooltip += f"\n- 请打开 {port_name} 代理软件"
        else:
            tooltip += "\n状态: 已禁用"
            self.tray_icon.setIcon(self.icons["off"])

        tooltip += "\n\n左键点击: git代理开关"
        tooltip += "\n右键点击: 快捷菜单"
        self.tray_icon.setToolTip(tooltip)

    def get_git_proxy_status(self) -> Tuple[bool, Optional[int]]:
        """极速解析 git 配置获取状态，解决 Subprocess 启动慢问题"""
        try:
            # 优先读文件解析，耗时 < 1ms
            gitconfig_path = Path.home() / ".gitconfig"
            if gitconfig_path.exists():
                config = configparser.ConfigParser(strict=False)
                config.read(gitconfig_path, encoding="utf-8")
                if "http" in config and "proxy" in config["http"]:
                    proxy_url = config["http"]["proxy"]
                    port = int(proxy_url.split(":")[-1])
                    return True, port
        except Exception:
            pass

        # 容错：回退到传统进程读取
        try:
            creationflags = (
                subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            result = subprocess.run(
                ["git", "config", "--global", "http.proxy"],
                capture_output=True,
                text=True,
                creationflags=creationflags,
            )
            if result.returncode == 0 and result.stdout.strip():
                proxy_url = result.stdout.strip()
                port = int(proxy_url.split(":")[-1])
                return True, port
        except (subprocess.SubprocessError, OSError):
            pass

        return False, getattr(self, "current_port", self.default_port)

    def init_git_proxy_status_and_tooltip(self):
        """初始化git代理状态并无缝触发后台更新"""
        git_proxy_enabled, current_port = self.get_git_proxy_status()
        if current_port is not None:
            self.current_port = current_port

        # init_mode=True 允许扫描到别的端口激活时，自动覆盖设置
        self.update_menu_status(git_proxy_enabled, self.current_port, init_mode=True)

    def set_git_proxy(self, switch: bool = True, port: int = None):
        creationflags = (
            subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        if switch:
            proxy_url = f"http://127.0.0.1:{port}"
            subprocess.run(
                ["git", "config", "--global", "http.proxy", proxy_url],
                creationflags=creationflags,
            )
            subprocess.run(
                ["git", "config", "--global", "https.proxy", proxy_url],
                creationflags=creationflags,
            )
        else:
            subprocess.run(
                ["git", "config", "--global", "--unset", "http.proxy"],
                creationflags=creationflags,
            )
            subprocess.run(
                ["git", "config", "--global", "--unset", "https.proxy"],
                creationflags=creationflags,
            )

    def toggle_proxy(self, editMode=False):
        try:
            git_proxy_enabled, _ = self.get_git_proxy_status()

            if git_proxy_enabled:
                self.set_git_proxy(False)
                self.update_menu_status(False, editMode=editMode)
            else:
                self.set_git_proxy(True, self.current_port)
                self.update_menu_status(True, self.current_port, editMode=editMode)
        except (subprocess.SubprocessError, OSError) as e:
            print(f"操作失败: {str(e)}")
            if not self.is_linux:
                self.ui.statusLabel.setText(
                    f'<span style="color: red;">操作失败: {str(e)}</span>'
                )

    def update_port(self):
        if self.is_linux:
            return

        try:
            port_text = self.ui.portInput.text()
            if not port_text or not port_text.strip():
                return
            port = int(port_text)

            if self.current_port == port:
                return

            if 1 <= port <= 65535:
                self.current_port = port
                isEdit = True
                if self.ui.proxyButton.isChecked():
                    self.ui.proxyButton.setChecked(False)
                    isEdit = False

                self.toggle_proxy(editMode=isEdit)
            else:
                self.ui.portInput.setText(str(self.current_port))
                self.ui.statusLabel.setText(
                    '<span style="color: red; font-weight: bold;">无效端口: 1-65535</span>'
                )
        except (ValueError, TypeError):
            self.ui.portInput.setText(str(self.current_port))
            self.ui.statusLabel.setText(
                '<span style="color: red; font-weight: bold;">请输入有效的数字端口</span>'
            )

    def show_port_list(self):
        if self.is_linux:
            return

        menu = QMenu(self.port_list_button)
        menu.setStyleSheet("""
            QMenu {
                border-radius: 6px;
            }
            QMenu::icon {
                padding-left: 18px;
            }
            QMenu::item {
                padding: 4px 10px;
            }
            QMenu::item:selected {
                background-color: rgba(130, 130, 130, 0.08);
            }
            """)

        title_widget = QWidgetAction(menu)
        title_label = QLabel("常用端口")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setEnabled(False)
        title_widget.setDefaultWidget(title_label)
        menu.addAction(title_widget)
        menu.addSeparator()

        for name, port in self.preset_port.items():
            action = QAction(name, menu)
            action.triggered.connect(lambda checked, p=port: self.set_port(p))
            menu.addAction(action)

            # 使用内存缓存的勾选Icon
            if str(port) == self.ui.portInput.text():
                action.setIcon(self.icons["selected"])

        menu.popup(
            self.port_list_button.mapToGlobal(self.port_list_button.rect().bottomLeft())
        )

    def set_port(self, port):
        self.current_port = int(port)
        self.set_git_proxy(port=self.current_port)
        self.update_menu_status(git_proxy_enabled=True, port=self.current_port)

    def toggle_auto_start(self):
        if platform.system() != "Windows" or not winreg:
            return
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            if self.auto_start_button.isChecked():
                exe_path = os.path.abspath(sys.executable)
                script_path = os.path.abspath(__file__)
                winreg.SetValueEx(
                    key,
                    "GitProxyManager",
                    0,
                    winreg.REG_SZ,
                    f'"{exe_path}" "{script_path}"',
                )
                self.auto_start_button.setText("取消开机自启动")
            else:
                try:
                    winreg.DeleteValue(key, "GitProxyManager")
                except FileNotFoundError:
                    pass
                self.auto_start_button.setText("设置开机自启动")
        finally:
            winreg.CloseKey(key)

    def check_auto_start_status(self):
        if platform.system() != "Windows" or not winreg:
            self.auto_start_button.setChecked(False)
            self.auto_start_button.setVisible(False)
            return
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            try:
                winreg.QueryValueEx(key, "GitProxyManager")
                self.auto_start_button.setChecked(True)
                self.auto_start_button.setText("取消开机自启动")
            except FileNotFoundError:
                self.auto_start_button.setChecked(False)
                self.auto_start_button.setText("设置开机自启动")
            finally:
                winreg.CloseKey(key)
        except Exception:
            self.auto_start_button.setChecked(False)
            self.auto_start_button.setText("设置开机自启动")

    def _check_system_proxy(self) -> bool:
        if platform.system() != "Windows" or not winreg:
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0,
                winreg.KEY_READ,
            )
            proxy_enable = winreg.QueryValueEx(key, "ProxyEnable")[0]
            return proxy_enable == 1
        except Exception:
            return False


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    shared_memory = QSharedMemory("GitProxyManager")
    if not shared_memory.create(1):
        print("应用程序已经在运行中。")
        sys.exit(0)

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
