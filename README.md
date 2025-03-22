# Git Proxy Switch

Git Proxy Switch 是一个用于管理 Git 代理设置的工具，支持在多个代理端口之间快速切换。

程序启动和切换端口时自动检测当前代理端口是否可用，并分别以绿色、黄色、灰色的系统托盘图标显示。

## 功能

- 系统托盘图标
  - 单击切换 git 代理开关
- 右键快捷菜单
  - 启用/禁用 Git 代理
  - 设置自定义代理端口
  - 开机自启动设置

## 截图

![alt text](screenshot.png)

## 安装

1. 克隆仓库到本地：

   ```bash
   git clone https://github.com/yourusername/GitProxySwitch.git
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用程序：
   ```bash
   python app.py
   ```

## 使用

1. 启动应用程序后，系统托盘会出现一个图标。
2. 单击托盘图标，切换 git 代理开关；右键点击托盘图标，打开快捷菜单。
3. 在菜单中可以启用/禁用 Git 代理、设置自定义端口、查看常用端口列表、设置开机自启动等。

## 常见问题

### 如何更改默认端口？

在 `app.py` 文件中，找到以下代码并修改默认端口：

```python
self.default_port = 10808
```

### 如何添加新的常用端口？

在 `app.py` 文件中，找到以下代码并添加新的端口：

```python
self.preset_port = {
    "V2Ray": "10808",
    "Clash": "7890",
    "SingBox": "10809",
    "NewProxy": "12345",  # 新增端口
}
```

## 贡献

欢迎提交问题和拉取请求来改进此项目。

## 许可证

此项目使用 MIT 许可证。有关更多信息，请参阅 [LICENSE](LICENSE) 文件。
