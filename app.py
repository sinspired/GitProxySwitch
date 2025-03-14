import concurrent.futures
import os
import socket
import subprocess
import sys
import winreg
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QPoint, Qt, QSharedMemory
from PySide6.QtGui import QAction, QColor, QIcon, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QSystemTrayIcon,
    QWidgetAction,
)

from ContextMenu_ui import Ui_ContextMenu


class MainWindow(QMenu):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_ContextMenu()
        self.ui.setupUi(self)

        # 初始化变量
        self.default_port = 10808
        self.current_port = self.default_port
        self.preset_port: Dict[str, str] = {
            "V2Ray": "10808",
            "Clash": "7890",
            "SingBox": "10809",
        }

        # 设置样式表
        self.setStyleSheet(
            """
            #proxyButton {
                border-radius: 0px;
                background-color:rgba(161, 58, 58, 0.39);
            }
            #proxyButton:checked {
                background-color: rgb(0, 197, 144);
            }
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
            #exitButton {
                border-radius: 0px;
                background-color: transparent;
            }
            #exitButton:hover {
                background-color: rgba(130, 130, 130, 0.08);
            }
        """
        )

        self.status_label = self.ui.statusLabel
        self.proxy_button = self.ui.proxyButton
        self.port_input = self.ui.portInput
        self.port_list_button = self.ui.portListButton
        self.auto_start_button = self.ui.autoStartButton
        self.exit_button = self.ui.exitButton

        # 设置自定义端口初始值
        self.port_input.setText(str(self.current_port))

        # 创建系统托盘图标
        self.setup_tray()

        # 更新代理状态和tooltip
        self.init_git_proxy_status_and_tooltip()

        # 检查开机自启状态
        self.check_auto_start_status()

        # 连接信号
        self.setup_connections()

    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon()
        icon_path = resource_path("Icon/status_off.svg")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def setup_connections(self):
        """设置信号连接"""
        self.proxy_button.clicked.connect(self.toggle_proxy)
        self.port_input.editingFinished.connect(self.update_port)
        self.port_list_button.clicked.connect(self.show_port_list)
        self.auto_start_button.clicked.connect(self.toggle_auto_start)
        self.exit_button.clicked.connect(QApplication.instance().quit)

    def on_tray_icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Context:
            geometry = self.tray_icon.geometry()
            self.popup(QPoint(geometry.x(), geometry.y() - self.height()))
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.proxy_button.setChecked(not self.proxy_button.isChecked())
            self.toggle_proxy()

    def update_git_proxy_status_and_tooltip(
        self, git_proxy_enabled: bool, port: int = None, editMode=False
    ):
        """更新git代理状态和提示信息"""
        port = port if port is not None else self.current_port
        proxy_url = f"http://127.0.0.1:{port}"
        self.port_input.setText(str(port))
        port_name = {v: k for k, v in self.preset_port.items()}.get(str(port), "其他")
        tooltip = "Git Proxy Switch"
        tooltip += "\n端口: {}".format(port)

        if git_proxy_enabled:
            tooltip += "\n状态: 已启用"
            tooltip += "\n代理: {}".format(proxy_url)

            proxy_running, proxy_name, proxy_port = self._detect_proxy_port()
            if proxy_running:
                if int(proxy_port) == int(port):
                    self.tray_icon.setIcon(QIcon(resource_path("Icon/status_ok.svg")))
                else:
                    tooltip += "\n"
                    tooltip += "\n- 当前端口 {} 不可用".format(port)
                    tooltip += "\n- {} : {} 正在运行".format(proxy_name, proxy_port)
                    self.tray_icon.setIcon(
                        QIcon(resource_path("Icon/status_warning.svg"))
                    )
            else:
                self.tray_icon.setIcon(QIcon(resource_path("Icon/status_warning.svg")))
                tooltip += "\n"
                tooltip += "\n- 当前端口不可用！"
                tooltip += "\n- 请打开 {} 代理软件".format(port_name)

            status_label_text = f'<span style="color: green;">git代理已{"切换" if editMode else "启用"}<br/>{proxy_url}</span>'
            proxy_button_text = "禁用git代理"
            self.proxy_button.setChecked(False)

        else:
            tooltip += "\n状态: 已禁用"

            status_label_text = '<span style="color: gray;">git代理已禁用</span>'
            proxy_button_text = "启用git代理"
            self.proxy_button.setChecked(True)
            self.tray_icon.setIcon(QIcon(resource_path("Icon/status_off.svg")))

        tooltip += "\n\n左键点击: git代理开关"
        tooltip += "\n右键点击: 快捷菜单"

        self.status_label.setText(status_label_text)
        self.tray_icon.setToolTip(tooltip)
        self.proxy_button.setText(proxy_button_text)

    def get_git_proxy_status(self) -> Tuple[bool, Optional[str]]:
        try:
            result = subprocess.run(
                ["git", "config", "--global", "http.proxy"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
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
            self.update_git_proxy_status_and_tooltip(True, port_openning)
        else:
            self.update_git_proxy_status_and_tooltip(git_proxy_enabled, current_port)

    def set_git_proxy(self, switch: bool = True, port: int = None):
        """设置/取消git代理"""
        if switch:
            # 启用git代理
            proxy_url = f"http://127.0.0.1:{port}"
            subprocess.run(
                ["git", "config", "--global", "http.proxy", proxy_url],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            subprocess.run(
                ["git", "config", "--global", "https.proxy", proxy_url],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            # 禁用git代理
            subprocess.run(
                ["git", "config", "--global", "--unset", "http.proxy"],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            subprocess.run(
                ["git", "config", "--global", "--unset", "https.proxy"],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

    def toggle_proxy(self, editMode=False):
        """切换git代理事件"""
        try:
            if self.proxy_button.isChecked():
                # 禁用git代理并更新标签和提示信息
                self.set_git_proxy(False)
                self.update_git_proxy_status_and_tooltip(False)
            else:
                # 启用git代理并更新标签和提示信息
                self.set_git_proxy(True, self.current_port)
                self.update_git_proxy_status_and_tooltip(
                    True, self.current_port, editMode
                )
        except (subprocess.SubprocessError, OSError) as e:
            print(f"操作失败: {str(e)}")
            self.status_label.setText(
                f'<span style="color: red;">操作失败: {str(e)}</span>'
            )

    def update_port(self):
        """更新git端口设置"""
        try:
            port = self.port_input.text()
            # 检查是否为空或非数字
            if not port or not port.strip() or self.current_port == int(port):
                # 未修改端口，直接返回
                return

            port = int(port)
            if 1 <= port <= 65535:
                # 端口有效，保存设置
                self.current_port = port
                isEdit = True
                if self.proxy_button.isChecked():
                    # 更新状态信息
                    self.proxy_button.setChecked(False)
                    isEdit = False

                # 更新代理设置
                self.toggle_proxy(isEdit)
            else:
                # 端口无效，恢复上一个有效端口
                self.port_input.setText(str(self.current_port))
                self.status_label.setText(
                    f'<span style="color: red; font-weight: bold;">无效端口: {port}，应为1-65535</span>'
                )
        except (ValueError, TypeError):
            # 输入无效，恢复上一个有效端口
            self.port_input.setText(str(self.current_port))
            self.status_label.setText(
                '<span style="color: red; font-weight: bold;">请输入有效的数字端口</span>'
            )

    def show_port_list(self):
        """显示端口列表"""
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu::icon{ padding-left: 18px; }"
            "QMenu::item { padding: 4px 10px 4px 10px;}  "
            "QMenu::item:selected { background-color: rgba(130, 130, 130, 0.08); }"
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
            action = QAction(name, self)
            action.triggered.connect(lambda checked, p=port, a=action: self.set_port(p))

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
        self.port_input.setText(port)
        self.update_port()

    def toggle_auto_start(self):
        """设置/取消开机自启"""
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
        except WindowsError:
            # 如果无法访问注册表，默认为未启用
            self.auto_start_button.setChecked(False)
            self.auto_start_button.setText("设置开机自启动")

    def _check_system_proxy(self) -> bool:
        """检查系统代理是否开启"""
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
