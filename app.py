# app.py
import concurrent.futures
import os
import platform
import socket
import subprocess
import sys
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QPoint, QSharedMemory, Qt
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


class ContextMenuWidget(QWidget):
    """单独的上下文菜单窗口部件，用于包含UI组件"""

    def __init__(self, parent=None):
        super(ContextMenuWidget, self).__init__(parent)
        self.ui = Ui_ContextMenuWidget()
        self.ui.setupUi(self)

        # 应用样式表
        self.setup_style()

    def setup_style(self):
        """设置控件样式"""
        self.ui.proxyButton.setStyleSheet(
            """
            #proxyButton {
                border-radius: 0px;
                background-color:rgba(161, 58, 58, 0.39);
            }
            #proxyButton:checked {
                background-color: rgb(0, 197, 144);
            }
            """
        )

        self.ui.autoStartButton.setStyleSheet(
            """
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
            """
        )

        self.ui.exitButton.setStyleSheet(
            """
            #exitButton {
                border-radius: 0px;
                background-color: transparent;
            }
            #exitButton:hover {
                background-color: rgba(130, 130, 130, 0.08);
            }
            """
        )


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
            "SingBox": "10809",
        }

        # 检查是否为Linux系统
        self.is_linux = platform.system() == "Linux"

        # 初始化UI相关属性为None，防止在Linux下引用未初始化的属性
        self.ui = None
        self.status_label = None
        self.proxy_button = None
        self.port_input = None
        self.port_list_button = None
        self.auto_start_button = None
        self.exit_button = None

        # 初始化Linux特定菜单项
        self.status_action = None
        self.toggle_proxy_action = None

        # 创建托盘菜单
        self.create_tray_menu()

        # 创建系统托盘图标
        self.setup_tray()

        # 更新代理状态和tooltip
        self.init_git_proxy_status_and_tooltip()

        # 检查开机自启状态
        if platform.system() != "Windows":
            return
        else:
            self.check_auto_start_status()

        self.show_startup_message()

    def show_startup_message(self):
        self.tray_icon.showMessage(
            "Git Proxy Switch",
            "程序已启动并驻留在系统托盘",
            QSystemTrayIcon.MessageIcon.Information,
            10,
        )

    def create_tray_menu(self):
        """创建托盘菜单"""
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet(
            """
            QMenu {
            border-radius: 0px;
            }
            """
        )
        if self.is_linux:
            self.setup_linux_menu()
        else:
            self.setup_windows_menu()

    def setup_linux_menu(self):
        """设置Linux托盘菜单"""
        # 状态文本显示
        self.status_action = QAction("代理状态: 未启用", self.tray_menu)
        self.status_action.setEnabled(False)
        self.tray_menu.addAction(self.status_action)

        self.tray_menu.addSeparator()

        # 切换代理按钮
        self.toggle_proxy_action = QAction("启用git代理", self.tray_menu)
        self.toggle_proxy_action.triggered.connect(self.toggle_proxy)
        self.tray_menu.addAction(self.toggle_proxy_action)

        # 端口设置
        port_menu = QMenu("设置端口", self.tray_menu)
        self.tray_menu.addMenu(port_menu)

        # 添加预设端口
        for name, port in self.preset_port.items():
            action = QAction(f"{name}: {port}", port_menu)
            action.triggered.connect(lambda checked, p=port: self.set_port(p))
            port_menu.addAction(action)

        self.tray_menu.addSeparator()

        # 添加退出选项
        self.exit_action = QAction("退出", self.tray_menu)
        self.exit_action.triggered.connect(QApplication.instance().quit)
        self.tray_menu.addAction(self.exit_action)

    def setup_windows_menu(self):
        """设置Windows托盘菜单"""
        # 创建控件Action
        self.menu_action = ContextMenuAction(self.tray_menu)
        self.tray_menu.addAction(self.menu_action)

        # 获取UI引用
        self.ui = self.menu_action.get_ui()
        self.status_label = self.ui.statusLabel
        self.proxy_button = self.ui.proxyButton
        self.port_input = self.ui.portInput
        self.port_list_button = self.ui.portListButton
        self.auto_start_button = self.ui.autoStartButton
        self.exit_button = self.ui.exitButton

        # 设置初始端口值
        self.ui.portInput.setText(str(self.current_port))

        # 连接信号
        self.setup_connections()

    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon()
        icon_path = resource_path("icon/status_off.svg")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def setup_connections(self):
        """设置信号连接"""
        if not self.is_linux:
            # Windows下使用自定义UI控件的连接
            self.ui.proxyButton.clicked.connect(self.toggle_proxy)
            self.ui.portInput.editingFinished.connect(self.update_port)
            self.ui.portListButton.clicked.connect(self.show_port_list)
            self.ui.autoStartButton.clicked.connect(self.toggle_auto_start)
            self.ui.exitButton.clicked.connect(QApplication.instance().quit)

    def on_tray_icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Context:
            # 右键点击 - 显示菜单
            if self.is_linux:
                cursor_pos = QCursor.pos()
                self.tray_menu.popup(cursor_pos)
            else:
                geometry = self.tray_icon.geometry()
                self.tray_menu.popup(
                    QPoint(geometry.x(), geometry.y() - self.tray_menu.height())
                )
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左键单击
            if self.is_linux:
                # Linux下直接切换代理状态并显示菜单
                self.toggle_proxy()
            else:
                # Windows下使用UI控件的点击状态
                self.proxy_button.setChecked(not self.proxy_button.isChecked())
                self.toggle_proxy()

    def update_menu_status(self, git_proxy_enabled: bool, port: int = None):
        """更新菜单状态"""
        if self.is_linux:
            self.update_linux_menu_status(git_proxy_enabled, port)
        else:
            self.update_git_proxy_status_and_tooltip(git_proxy_enabled, port)

    def update_linux_menu_status(self, git_proxy_enabled: bool, port: int = None):
        """更新Linux菜单状态"""
        port = port if port is not None else self.current_port
        proxy_url = f"http://127.0.0.1:{port}"

        if git_proxy_enabled:
            self.status_action.setText(f"代理状态: 已启用 ({proxy_url})")
            self.toggle_proxy_action.setText("禁用git代理")
            proxy_running, proxy_name, proxy_port = self._detect_proxy_port()
            if proxy_running:
                if int(proxy_port) == int(port):
                    self.tray_icon.setIcon(QIcon(resource_path("icon/status_ok.svg")))
                else:
                    self.tray_icon.setIcon(
                        QIcon(resource_path("icon/status_warning.svg"))
                    )
            else:
                self.tray_icon.setIcon(QIcon(resource_path("icon/status_warning.svg")))
        else:
            self.status_action.setText("代理状态: 已禁用")
            self.toggle_proxy_action.setText("启用git代理")
            self.tray_icon.setIcon(QIcon(resource_path("icon/status_off.svg")))

    def update_git_proxy_status_and_tooltip(
        self, git_proxy_enabled: bool, port: int = None, editMode=False
    ):
        """更新git代理状态和提示信息"""
        port = port if port is not None else self.current_port
        proxy_url = f"http://127.0.0.1:{port}"
        self.ui.portInput.setText(str(port))
        port_name = {v: k for k, v in self.preset_port.items()}.get(str(port), "其他")
        tooltip = "Git Proxy Switch"
        tooltip += "\n端口: {}".format(port)

        if git_proxy_enabled:
            tooltip += "\n状态: 已启用"
            tooltip += "\n代理: {}".format(proxy_url)

            proxy_running, proxy_name, proxy_port = self._detect_proxy_port()
            if proxy_running:
                if int(proxy_port) == int(port):
                    self.tray_icon.setIcon(QIcon(resource_path("icon/status_ok.svg")))
                else:
                    tooltip += "\n"
                    tooltip += "\n- 当前端口 {} 不可用".format(port)
                    tooltip += "\n- {} : {} 正在运行".format(proxy_name, proxy_port)
                    self.tray_icon.setIcon(
                        QIcon(resource_path("icon/status_warning.svg"))
                    )
            else:
                self.tray_icon.setIcon(QIcon(resource_path("icon/status_warning.svg")))
                tooltip += "\n"
                tooltip += "\n- 当前端口不可用！"
                tooltip += "\n- 请打开 {} 代理软件".format(port_name)

            status_label_text = f'<span style="color: green;">git代理已{"切换" if editMode else "启用"}<br/>{proxy_url}</span>'
            proxy_button_text = "禁用git代理"
            self.ui.proxyButton.setChecked(False)

        else:
            tooltip += "\n状态: 已禁用"

            status_label_text = '<span style="color: gray;">git代理已禁用</span>'
            proxy_button_text = "启用git代理"
            self.ui.proxyButton.setChecked(True)
            self.tray_icon.setIcon(QIcon(resource_path("icon/status_off.svg")))

        tooltip += "\n\n左键点击: git代理开关"
        tooltip += "\n右键点击: 快捷菜单"

        self.ui.statusLabel.setText(status_label_text)
        self.tray_icon.setToolTip(tooltip)
        self.ui.proxyButton.setText(proxy_button_text)

    def get_git_proxy_status(self) -> Tuple[bool, Optional[str]]:
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
                proxy_url = result.stdout.strip()  # http://127.0.0.1:10808
                port = int(proxy_url.split(":")[-1])
                return True, port
            else:
                return False, None
        except (subprocess.SubprocessError, OSError):
            return False, None

    def init_git_proxy_status_and_tooltip(self):
        """初始化git代理状态和提示信息"""
        git_proxy_enabled, current_port = self.get_git_proxy_status()
        proxy_running, port_name_openning, port_openning = self._detect_proxy_port()
        if proxy_running:
            self.set_git_proxy(True, port_openning)
            self.update_menu_status(True, port_openning)
        else:
            self.update_menu_status(git_proxy_enabled, current_port)

    def set_git_proxy(self, switch: bool = True, port: int = None):
        """设置/取消git代理"""
        creationflags = (
            subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        if switch:
            # 启用git代理
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
            # 禁用git代理
            subprocess.run(
                ["git", "config", "--global", "--unset", "http.proxy"],
                creationflags=creationflags,
            )
            subprocess.run(
                ["git", "config", "--global", "--unset", "https.proxy"],
                creationflags=creationflags,
            )

    def toggle_proxy(self, editMode=False):
        """切换git代理事件"""
        try:
            # 获取当前代理状态
            git_proxy_enabled, _ = self.get_git_proxy_status()

            if git_proxy_enabled:
                # 当前已启用，则禁用
                self.set_git_proxy(False)
                self.update_menu_status(False)
            else:
                # 当前已禁用，则启用
                self.set_git_proxy(True, self.current_port)
                self.update_menu_status(True, self.current_port)
        except (subprocess.SubprocessError, OSError) as e:
            print(f"操作失败: {str(e)}")
            if not self.is_linux:
                self.ui.statusLabel.setText(
                    f'<span style="color: red;">操作失败: {str(e)}</span>'
                )

    def update_port(self):
        """更新git端口设置"""
        if self.is_linux:
            # Linux系统下通过菜单已经完成端口设置
            return

        try:
            port = self.ui.portInput.text()
            # 检查是否为空或非数字
            if not port or not port.strip() or self.current_port == int(port):
                # 未修改端口，直接返回
                return

            port = int(port)
            if 1 <= port <= 65535:
                # 端口有效，保存设置
                self.current_port = port
                isEdit = True
                if self.ui.proxyButton.isChecked():
                    # 更新状态信息
                    self.ui.proxyButton.setChecked(False)
                    isEdit = False

                # 更新代理设置
                self.toggle_proxy(isEdit)
            else:
                # 端口无效，恢复上一个有效端口
                self.ui.portInput.setText(str(self.current_port))
                self.ui.statusLabel.setText(
                    f'<span style="color: red; font-weight: bold;">无效端口: {port}，应为1-65535</span>'
                )
        except (ValueError, TypeError):
            # 输入无效，恢复上一个有效端口
            self.ui.portInput.setText(str(self.current_port))
            self.ui.statusLabel.setText(
                '<span style="color: red; font-weight: bold;">请输入有效的数字端口</span>'
            )

    def show_port_list(self):
        """显示端口列表"""
        if self.is_linux:
            # Linux系统下已通过菜单实现端口列表
            return

        menu = QMenu(self.port_list_button)  # 确保 QMenu 的父对象正确
        menu.setStyleSheet(
            """
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
            """
        )

        # 自定义标题行
        title_widget = QWidgetAction(menu)
        title_label = QLabel("常用端口")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setEnabled(False)
        title_widget.setDefaultWidget(title_label)
        menu.addAction(title_widget)

        # 添加分割线
        menu.addSeparator()

        # 添加端口列表项
        for name, port in self.preset_port.items():
            action = QAction(name, menu)
            action.triggered.connect(lambda checked, p=port: self.set_port(p))

            menu.addAction(action)

            # 如果是当前选中的端口，加上选中标记
            if str(port) == self.port_input.text():
                icon = QIcon(resource_path("icon/select.svg"))
                pixmap = icon.pixmap(4, 4)
                painter = QPainter(pixmap)
                gradient = QLinearGradient(0, 0, pixmap.width(), pixmap.height())
                gradient.setColorAt(0, QColor("#1b8094"))
                gradient.setColorAt(1, QColor("#4fc3f7"))
                painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                painter.fillRect(pixmap.rect(), gradient)
                painter.end()
                icon = QIcon(pixmap)
                action.setIcon(QIcon(icon))
        menu.popup(
            self.port_list_button.mapToGlobal(self.port_list_button.rect().bottomLeft())
        )

    def set_port(self, port):
        """设置端口并更新"""
        self.current_port = port
        self.set_git_proxy(port=self.current_port)
        self.update_menu_status(git_proxy_enabled=True, port=self.current_port)

    def toggle_auto_start(self):
        """设置/取消开机自启"""
        if platform.system() != "Windows" or not winreg:
            return  # 非 Windows 系统不支持此功能
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
        """检查开机自启状态"""
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
            # 如果无法访问注册表，默认为未启用
            self.auto_start_button.setChecked(False)
            self.auto_start_button.setText("设置开机自启动")

    def _check_system_proxy(self) -> bool:
        """检查系统代理是否开启"""
        if platform.system() != "Windows" or not winreg:
            return False  # 非Windows系统暂不支持检测系统代理

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

    def _detect_proxy_port(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """并发检测可用的代理端口"""

        def check_port(name, port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.1)
                    if sock.connect_ex(("127.0.0.1", int(port))) == 0:
                        return True, name, port
            except Exception:
                pass
            return False, None, None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_port = {
                executor.submit(check_port, name, port): (name, port)
                for name, port in self.preset_port.items()
            }
            for future in concurrent.futures.as_completed(future_to_port):
                success, name, port = future.result()
                if success:
                    return True, name, port

        return False, None, None


def resource_path(relative_path):
    """获取打包后资源文件的绝对路径"""
    if hasattr(sys, "_MEIPASS"):
        # 如果是打包后的环境
        base_path = sys._MEIPASS
    else:
        # 开发环境，直接使用当前路径
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
