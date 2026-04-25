# SWnumbergame 🚀

## 📖 项目简介
SWnumbergame是一款基于Python和PyQt6开发的数字游戏应用，具有现代化的用户界面和丰富的功能。本项目旨在提供一个功能完整、用户友好的游戏体验，包括欢迎页面、游戏主界面、用户管理等核心功能。

## 📝 版本信息
- **当前版本**：3.2.6
- **更新日期**：2026年4月
- **版本特点**：欢迎页面功能增强

## ✨ 主要功能

### 🎮 欢迎页面
- **返回游戏功能**：实现欢迎页面的"返回游戏"功能，用户可顺畅返回游戏主界面
- **查看更新功能**：优化欢迎页面的"查看更新"功能，确保能正确打开更新日志窗口
- **信号机制优化**：完善WebChannel通信机制，确保JavaScript与Python端的流畅交互
- **用户体验提升**：优化窗口切换流程，减少界面切换延迟

### 🎨 用户管理界面
- **界面美化**：重新设计颜色方案，采用蓝色主题提升视觉效果
- **输入禁止机制**：用户管理界面禁止用户直接编辑数据，确保数据安全
- **交替行颜色**：添加交替行颜色效果，提升数据可读性
- **按钮样式优化**：优化删除按钮样式，确保文字清晰可见

### 🔧 功能增强
- **资源加载修复**：解决介绍窗口与更新窗口的资源加载问题
- **用户管理优化**：移除数据加密功能，简化数据传输和存储
- **用户列表更新**：解决用户管理窗口打开后无法及时更新用户列表的问题
- **数据刷新机制**：优化数据刷新机制，确保显示最新用户信息

## 📋 软件属性
- **文件说明**：SWnumbergame
- **类型**：应用程序
- **文件版本**：3.2.6
- **产品名称**：SWnumbergame
- **产品版本**：3.26
- **版权**：Wangstation ©2025-2026
- **修改日期**：2026年4月

## 🚀 使用方法
1. **运行环境**：确保已安装Python 3.11
2. **启动程序**：使用Python运行main.py文件
3. **权限确认**：首次运行会弹出UAC权限申请，点击"是"确认
4. **界面访问**：
   - 游戏界面：程序启动后自动打开
   - 服务器地址：http://127.0.0.1:5000

## 📦 打包方法
1. **环境准备**：
   - 下载并安装Python 3.11
   - 安装打包工具：`pip install nuitka`

2. **执行打包命令**：
   ```bash
    venv\Scripts\python -m nuitka \
    --standalone \
    --enable-plugin=pyqt6 \
    --windows-disable-console \
    --windows-icon-from-ico=app_icon.ico \
    --include-data-dir=templates=templates \
    --include-data-dir=static=static \
    --include-data-file=updates.html=updates.html \
    --include-data-file=welcome.html=welcome.html \
    --include-data-file=game_config.json=game_config.json \
    --include-data-file=leaderboard.json=leaderboard.json \
    --output-dir=dist \
    main.py
   ```

3. **打包参数说明**：
   | 参数 | 说明 |
   |------|------|
   | `--standalone` | 创建独立可执行文件，不依赖系统Python环境 |
   | `--enable-plugin=pyqt6` | 启用PyQt6插件，确保PyQt6相关功能正常工作 |
   | `--windows-icon-from-ico=app_icon.ico` | 设置Windows应用程序图标 |
   | `--windows-disable-console` | 禁用控制台输出 |
   | `--include-data-dir=templates=templates` | 包含templates目录及其所有内容 |
   | `--include-data-dir=static=static` | 包含static目录及其所有内容 |
   | `--include-data-file=updates.html=updates.html` | 包含updates.html文件 |
   | `--include-data-file=welcome.html=welcome.html` | 包含welcome.html文件 |
   | `--include-data-file=game_config.json=game_config.json` | 包含game_config.json配置文件 |
   | `--include-data-file=leaderboard.json=leaderboard.json` | 包含leaderboard.json数据文件 |
   | `--output-dir=dist` | 指定输出目录为dist |
   | `main.py` | 主入口脚本文件 |

4. **运行打包文件**：打包完成后，在dist目录中找到main.exe文件即可运行

## ⚠️ 注意事项
- **权限要求**：首次运行需要管理员权限，后续运行可记住选择
- **网络访问**：如防火墙提示，请允许程序访问网络
- **数据存储**：游戏数据保存在本地，无需联网即可运行
- **依赖管理**：项目依赖已记录在requirements.txt文件中

## 📄 许可证
本项目采用Permissive Non-Commercial Software License v1.0 (International)许可证

## 👥 贡献
欢迎提交Issue和Pull Request来帮助改进这个项目！

