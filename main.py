#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW数字游戏主程序 - 重构版
集成局域网服务器管理版，支持本地游戏和局域网对战模式

架构说明：
- 使用模块化设计，UI逻辑在 ui/ 包中
- 使用 BaseWindow 作为窗口基类
- WebView 通过 WebViewManager 统一管理
- 修复了启动时 WebView 显示黑色的问题
"""

import sys
import os
import socket
import threading
import logging
from pathlib import Path
from datetime import datetime

def get_resource_path(relative_path):
    """获取资源文件的绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径
        
    Returns:
        资源文件的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # Nuitka打包环境
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def clean_leaderboard_data():
    """清理leaderboard.json数据，删除符合条件的记录
    
    删除条件：
    1. 清洗天数 > 10 天
    2. 分数 < 300 分
    """
    import json
    from datetime import datetime, timedelta
    
    leaderboard_path = get_resource_path('leaderboard.json')
    
    try:
        if not os.path.exists(leaderboard_path):
            logger.warning("排行榜文件不存在，跳过数据清理")
            return
        
        # 读取数据
        with open(leaderboard_path, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        
        # 计算当前日期
        current_date = datetime.now()
        logger.info(f"开始清理leaderboard数据，当前日期: {current_date}")
        
        # 过滤符合条件的记录
        filtered_scores = []
        deleted_count = 0
        
        for score in scores:
            try:
                # 解析时间戳
                timestamp_str = score.get('timestamp')
                if not timestamp_str:
                    logger.warning(f"记录缺少时间戳: {score}")
                    continue
                
                record_date = datetime.fromisoformat(timestamp_str)
                # 计算天数差
                days_diff = (current_date - record_date).days
                
                # 判断是否符合删除条件
                if days_diff > 10 and score.get('score', 0) < 300:
                    deleted_count += 1
                    logger.info(f"删除记录: {score['player_name']}, 分数: {score['score']}, 天数差: {days_diff}")
                else:
                    filtered_scores.append(score)
            except Exception as e:
                logger.error(f"处理记录时出错: {e}, 记录: {score}")
                # 保留有错误的记录
                filtered_scores.append(score)
        
        # 写回过滤后的数据
        if deleted_count > 0:
            with open(leaderboard_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_scores, f, ensure_ascii=False, indent=2)
            logger.info(f"数据清理完成，删除了 {deleted_count} 条记录")
        else:
            logger.info("没有符合条件的记录需要删除")
            
    except Exception as e:
        logger.error(f"清理leaderboard数据时出错: {e}")

def clean_log_files():
    """清理超过3天的日志文件
    
    清理条件：
    1. 创建时间超过3天的日志文件
    """
    from datetime import datetime, timedelta
    
    # 使用全局LOG_DIR变量
    log_dir = LOG_DIR
    
    try:
        if not os.path.exists(log_dir):
            logger.warning("日志目录不存在，跳过日志清理")
            return
        
        # 计算3天前的日期
        three_days_ago = datetime.now() - timedelta(days=3)
        logger.info(f"开始清理日志文件，清理3天前({three_days_ago})的文件")
        
        # 遍历日志目录
        deleted_count = 0
        for file_name in os.listdir(log_dir):
            file_path = os.path.join(log_dir, file_name)
            
            # 检查是否是文件
            if os.path.isfile(file_path):
                # 获取文件创建时间
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 判断是否超过3天
                if file_mtime < three_days_ago:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"删除日志文件: {file_name}")
                    except Exception as e:
                        logger.error(f"删除日志文件失败: {e}, 文件: {file_name}")
        
        logger.info(f"日志清理完成，删除了 {deleted_count} 个文件")
        
    except Exception as e:
        logger.error(f"清理日志文件时出错: {e}")

VERSION = "3.2.7"

# 日志文件保存在用户可访问的位置
if os.name == 'nt':
    # Windows系统
    LOG_DIR = Path(os.path.expanduser('~')) / 'AppData' / 'Local' / 'SW数字游戏' / 'logs'
else:
    # 其他系统
    LOG_DIR = Path(os.path.expanduser('~')) / '.sw_number_game' / 'logs'

LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'app_{datetime.now().strftime("%Y%m%d")}.log'

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SW数字游戏')

ui_logger = logging.getLogger('SW数字游戏.UI')
ui_logger.setLevel(logging.DEBUG)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                            QMessageBox, QStatusBar, QToolBar, QSplashScreen)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtWebEngineCore import QWebEngineSettings

from ui.base import BaseWindow
from ui.dialogs import UpdateWindow, WelcomeWindow, UserManagementWindow



# 禁用GPU硬件加速以解决WebView黑屏问题
os.environ['QTWEBENGINE_DISABLE_GPU'] = '1'
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu'
os.environ['QT_OPENGL'] = 'software'


class ServerManager(QObject):
    """局域网服务器管理器"""
    server_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.app = None
        self.running = False
        self.port = 5000

    def check_network_connection(self):
        """检查网络连接状态"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            logger.info("网络连接检查成功")
            return result == 0
        except Exception as e:
            logger.error(f"网络检查错误: {e}")
            return True

    def check_admin_privileges(self):
        """检查是否具有管理员权限"""
        try:
            import ctypes
            result = ctypes.windll.shell32.IsUserAnAdmin()
            logger.info(f"管理员权限检查: {'是' if result else '否'}")
            return result
        except Exception as e:
            logger.warning(f"管理员权限检查失败: {e}")
            return False

    def start_server(self):
        """启动Flask服务器"""
        if self.running:
            logger.info("服务器已在运行中")
            return True

        logger.info("正在启动局域网服务器...")

        try:
            from server.flask_app import create_app
            app = create_app()
            logger.info("Flask应用创建成功")

            self.port = 5000
            self.app = app

            def run_server():
                try:
                    app.run(
                        host='0.0.0.0',
                        port=5000,
                        debug=False,
                        use_reloader=False,
                        threaded=True,
                        processes=1
                    )
                    logger.info("服务器启动成功 - 生产环境")
                except Exception as e:
                    logger.error(f"服务器运行错误: {e}")
                    self.running = False

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()

            import time
            time.sleep(2)

            max_attempts = 3
            for attempt in range(max_attempts):
                if self._test_server_connection(5000):
                    self.running = True
                    self.server_started.emit()
                    logger.info("服务器启动成功")
                    return True
                else:
                    time.sleep(1)

            logger.warning("服务器启动验证失败，但仍继续运行")
            self.running = True
            return True

        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            self.running = True
            return True

    def _test_server_connection(self, port):
        """测试服务器连接"""
        try:
            import requests
            response = requests.get(f'http://127.0.0.1:{port}/desktop', timeout=3)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"服务器连接测试失败: {e}")
            return False


class VersionChecker:
    """后台版本检查器"""

    def __init__(self, current_version):
        self.current_version = current_version
        self.international_url = "https://raw.githubusercontent.com/Yuanyuan5510/number_game/main/version.txt"
        self.china_url = "https://gitee.com/yuanyuan5510/1110/raw/main/version.txt"
        self.region_check_url = "https://api-website-2.yuanyuan5510-692.workers.dev/.netlify/functions/ip"

    def check_version_async(self):
        """异步检查版本"""
        thread = threading.Thread(target=self._check_version, daemon=True)
        thread.start()

    def _check_version(self):
        """执行版本检查"""
        try:
            is_international = self._check_region()
            version_url = self.international_url if is_international else self.china_url
            logger.info(f"区域检查完成: {'国际' if is_international else '中国'}，版本URL: {version_url}")

            remote_version = self._fetch_version(version_url)
            if remote_version is None:
                logger.error("无法获取远程版本信息")
                return

            if self._compare_versions(remote_version, self.current_version) > 0:
                logger.info(f"发现新版本: {remote_version} > 当前版本: {self.current_version}")
                self._show_update_prompt(remote_version)
            elif self._compare_versions(remote_version, self.current_version) < 0:
                logger.info("当前版本高于远程版本，可能是开发版本")
            else:
                logger.info("当前版本已是最新版本")

        except Exception as e:
            logger.error(f"版本检查失败: {e}")

    def _check_region(self):
        """检查用户区域"""
        try:
            import requests
            response = requests.get(self.region_check_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"区域检查失败，使用中国区域: {e}")
            return False

    def _fetch_version(self, url):
        """获取远程版本号"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                version = response.text.strip()
                logger.info(f"获取到远程版本: {version}")
                return version
            else:
                logger.warning(f"获取版本失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"无法连接到版本服务器: {e}")
            return None

    def _compare_versions(self, remote, current):
        """比较版本号"""
        def parse_version(v):
            try:
                parts = v.lstrip('v').split('.')
                return [int(x) for x in parts]
            except:
                return [0]

        remote_parts = parse_version(remote)
        current_parts = parse_version(current)

        # 比较相同长度的部分
        for r, c in zip(remote_parts, current_parts):
            if r > c:
                return 1
            elif r < c:
                return -1
        
        # 如果前面的部分都相同，那么长度较长的版本号更大
        if len(remote_parts) > len(current_parts):
            return 1
        elif len(remote_parts) < len(current_parts):
            return -1
        return 0

    def _show_update_prompt(self, new_version):
        """显示更新提示"""
        logger.info(f"发现新版本 {new_version}，提示用户更新")


class MainWindow(BaseWindow):
    """主窗口类"""

    def __init__(self):
        self.server_manager = ServerManager()
        self.loading_completed = False
        self.splash_duration = 5000

        super().__init__(f"SW数字游戏 v{VERSION}")

        ui_logger.debug("开始初始化MainWindow")
        logger.info("MainWindow初始化")

        # 执行leaderboard数据清理
        clean_leaderboard_data()
        
        # 执行日志文件清理
        clean_log_files()

        self.show_splash_screen()

        self.loading_thread = threading.Thread(target=self.load_background_data, daemon=True)
        self.loading_thread.start()

        QTimer.singleShot(500, self.init_ui)
        QTimer.singleShot(self.splash_duration, self.close_splash_screen)

        self.version_checker = VersionChecker(VERSION)
        QTimer.singleShot(2000, lambda: self.version_checker.check_version_async())

    def show_splash_screen(self):
        """显示启动动画"""
        ui_logger.debug("开始创建启动画面")
        logger.info("显示启动画面")

        self.splash = QSplashScreen()

        pixmap = QPixmap(400, 240)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        painter.fillRect(pixmap.rect(), QColor("#667eea"))

        painter.setPen(QColor("white"))
        font = QFont("Microsoft YaHei", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignmentFlag.AlignCenter, "SW数字游戏")

        font = QFont("Microsoft YaHei", 10)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(pixmap.rect().adjusted(0, 90, 0, 0), Qt.AlignmentFlag.AlignCenter, f"版本 {VERSION}")

        painter.setPen(QColor(255, 255, 255, 150))
        font = QFont("Microsoft YaHei", 8)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 130, 0, 0), Qt.AlignmentFlag.AlignCenter, "正在加载...")

        painter.end()

        self.splash.setPixmap(pixmap)
        self.splash.show()

    def close_splash_screen(self):
        """关闭启动动画"""
        ui_logger.debug("开始关闭启动画面")
        logger.info("关闭启动画面")

        if hasattr(self, 'splash'):
            self.splash.close()
            ui_logger.debug("延迟显示主窗口，确保WebView已完全加载")
            QTimer.singleShot(500, self.show_main_window)
        else:
            ui_logger.debug("启动画面不存在")

    def show_main_window(self):
        """显示主窗口"""
        ui_logger.debug("显示主窗口")
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()
        ui_logger.debug(f"主窗口可见性: {self.isVisible()}")

        if self.web_view:
            ui_logger.debug(f"WebView可见性: {self.web_view.isVisible()}")
            ui_logger.debug(f"WebView大小: {self.web_view.size()}")

    def load_background_data(self):
        """后台加载数据"""
        logger.info("开始后台数据加载")

        import time

        logger.info("加载游戏配置")
        time.sleep(0.5)

        game_path = get_resource_path('templates/desktop_local.html')
        logger.info(f"游戏文件检查: {'存在' if os.path.exists(game_path) else '不存在'}")

        updates_path = get_resource_path('updates.html')
        logger.info(f"更新文件检查: {'存在' if os.path.exists(updates_path) else '不存在'}")

        welcome_path = get_resource_path('welcome.html')
        logger.info(f"欢迎页面检查: {'存在' if os.path.exists(welcome_path) else '不存在'}")

        logger.info("检查网络连接")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            logger.info(f"网络连接: {'正常' if result == 0 else '不可用'}")
        except Exception as e:
            logger.warning(f"网络连接检查失败: {e}")

        logger.info("启动动画结束，继续后台数据预加载")

        logger.info("预加载游戏资源")
        time.sleep(0.5)

        logger.info("检查Flask依赖")
        try:
            import flask
            logger.info(f"Flask版本: {flask.__version__}")
        except ImportError:
            logger.warning("Flask未安装，局域网模式将不可用")

        logger.info("检查其他依赖")
        try:
            import requests
            logger.info(f"Requests版本: {requests.__version__}")
        except ImportError:
            logger.warning("Requests未安装，网络功能可能受限")

        logger.info("检查静态资源")
        static_dir = get_resource_path('static')
        if os.path.exists(static_dir):
            logger.info("静态资源目录: 存在")
            css_dir = os.path.join(static_dir, 'css')
            if os.path.exists(css_dir):
                logger.info("CSS文件: 存在")
        else:
            logger.warning("静态资源目录: 不存在")

        time.sleep(0.5)

        self.loading_completed = True
        logger.info("后台数据加载完成")

    def init_ui(self):
        """初始化UI - 重构版本"""
        logger.info("开始初始化UI")

        self.setMinimumSize(800, 600)
        
        # 实现窗口大小自适应配置
        self.adjust_window_size()

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ffffff;")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        self.create_toolbar()

        self._init_webview(main_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("就绪")

        self.server_manager.server_started.connect(self.on_server_started)

        logger.info("UI初始化完成")

    def adjust_window_size(self):
        """自动调整窗口大小"""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QRect
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        logger.info(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 计算合适的窗口大小（屏幕的80%）
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 确保窗口大小不小于最小值
        window_width = max(window_width, 800)
        window_height = max(window_height, 600)
        
        # 确保窗口大小不超过屏幕大小
        window_width = min(window_width, screen_width - 100)
        window_height = min(window_height, screen_height - 100)
        
        logger.info(f"自动调整窗口大小为: {window_width}x{window_height}")
        
        # 设置窗口大小
        self.resize(window_width, window_height)
        
        # 居中显示
        self.center_window(self)

    def _get_error_html(self, game_path: str = "") -> str:
        """生成简化的错误页面

        Args:
            game_path: 游戏文件路径

        Returns:
            HTML字符串
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>SW数字游戏 - 文件缺失</title>
    <style>
        body {{ background: #2c3e50; color: white; font-family: Arial;
               text-align: center; padding: 50px; }}
        .msg {{ font-size: 18px; margin: 20px; }}
        .path {{ font-size: 12px; color: #ccc; }}
    </style>
</head>
<body>
    <h2>⚠️ 游戏文件未找到</h2>
    <div class="msg">点击"启动局域网"按钮启动在线版本</div>
    <div class="path">{game_path}</div>
</body>
</html>
"""

    def _init_webview(self, layout):
        """初始化WebView - 完全按照旧版本方式实现

        修复原理：直接创建QWebEngineView实例，避免WebViewManager的复杂性
        """
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        from PyQt6.QtCore import Qt, QUrl

        ui_logger.debug("创建WebView")
        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        ui_logger.debug("配置WebView设置")
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)

        ui_logger.debug("添加WebView到布局")
        layout.addWidget(self.web_view)

        # 预加载本地游戏页面 - 使用不依赖Flask的版本
        game_path = get_resource_path('templates/desktop_local_noflask.html')
        if os.path.exists(game_path):
            ui_logger.debug(f"预加载本地游戏页面: {game_path}")
            self.web_view.load(QUrl.fromLocalFile(game_path))
        else:
            # 回退到原来的版本
            game_path = get_resource_path('templates/desktop_local.html')
            if os.path.exists(game_path):
                ui_logger.debug(f"回退到Flask版本: {game_path}")
                self.web_view.load(QUrl.fromLocalFile(game_path))
            else:
                ui_logger.debug("本地游戏页面不存在，显示错误页面")
                self.web_view.setHtml(self._get_error_html(game_path))

        logger.info("WebView初始化完成")

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.server_action = QAction("启动局域网", self)
        self.server_action.triggered.connect(self.toggle_server)
        toolbar.addAction(self.server_action)

        toolbar.addSeparator()

        updates_action = QAction("查看更新", self)
        updates_action.triggered.connect(self.show_updates)
        toolbar.addAction(updates_action)

        welcome_action = QAction("查看介绍", self)
        welcome_action.triggered.connect(self.show_welcome)
        toolbar.addAction(welcome_action)

        toolbar.addSeparator()

        user_management_action = QAction("用户管理", self)
        user_management_action.triggered.connect(self.show_user_management)
        toolbar.addAction(user_management_action)

    def toggle_server(self):
        """切换服务器状态"""
        if self.server_manager.running:
            QMessageBox.warning(
                self,
                '无法关闭',
                '局域网服务器启动后无法关闭，这是为了保证游戏体验连续性。\n\n'
                '如需关闭，请直接退出整个应用程序。',
                QMessageBox.Ok
            )
        else:
            self.update_status("正在启动局域网服务器...")

            def start_server_async():
                if self.server_manager.start_server():
                    self.server_action.setText("局域网已启动")
                    self.server_action.setEnabled(False)
                    self.update_status("局域网服务器运行中 - http://127.0.0.1:5000/desktop")

                    QMessageBox.information(
                        self,
                        "启动成功",
                        "局域网服务器启动成功！\n"
                        "本地访问：http://127.0.0.1:5000/desktop\n"
                        "局域网访问：http://" + self.get_local_ip() + ":5000/desktop\n\n"
                        "服务器现已运行，无法手动关闭。"
                    )

                    from PyQt6.QtCore import QUrl
                    self.web_view.load(QUrl("http://127.0.0.1:5000/desktop"))
                else:
                    self.update_status("局域网服务器启动失败")
                    QMessageBox.critical(self, "启动失败", "局域网服务器启动失败，请检查端口是否被占用！")

            QTimer.singleShot(100, start_server_async)

    def on_server_started(self):
        """服务器启动回调"""
        logger.info("服务器启动信号已接收")
        self.server_action.setText("局域网已启动")
        self.server_action.setEnabled(False)
        self.update_status("局域网服务器运行中 - http://127.0.0.1:5000/desktop")

    def show_updates(self):
        """显示更新日志"""
        logger.info("打开更新日志窗口")
        updates_window = UpdateWindow(self)
        updates_window.go_back_signal.connect(self.on_welcome_go_back)
        updates_window.show()

    def show_welcome(self):
        """显示欢迎页面"""
        logger.info("打开欢迎页面窗口")
        welcome_window = WelcomeWindow(self)
        welcome_window.open_updates_signal.connect(self.show_updates)
        welcome_window.go_back_signal.connect(self.on_welcome_go_back)
        self.hide()
        welcome_window.show()

    def on_welcome_go_back(self):
        """从欢迎页面返回游戏"""
        logger.info("从欢迎页面返回游戏")
        self.show()

    def show_user_management(self):
        """显示用户管理窗口"""
        logger.info("打开用户管理窗口")
        user_management_window = UserManagementWindow(self)
        user_management_window.show()

    def get_local_ip(self):
        """获取本地IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)
        logger.info(f"状态更新: {message}")

    def closeEvent(self, event):
        """关闭事件"""
        logger.info("应用程序关闭")
        try:
            event.accept()

            def cleanup():
                try:
                    if self.web_view:
                        self.web_view.stop()
                        self.web_view.deleteLater()

                    if self.server_manager and self.server_manager.running:
                        logger.info("服务器正在运行，将随应用程序一起关闭")
                except Exception as e:
                    logger.error(f"清理资源时出错: {e}")

            cleanup_thread = threading.Thread(target=cleanup, daemon=True)
            cleanup_thread.start()

        except Exception as e:
            logger.error(f"关闭应用时出错: {e}")
            if not event.isAccepted():
                event.accept()


def create_app_icon():
    """创建应用图标"""
    icon_size = 64
    pixmap = QPixmap(icon_size, icon_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient_rect = pixmap.rect().adjusted(4, 4, -4, -4)
    painter.setBrush(QColor(255, 107, 53))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(gradient_rect, 8, 8)

    painter.setPen(Qt.GlobalColor.white)
    font = QFont("Arial", 18, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SW")

    painter.end()
    return QIcon(pixmap)


def center_window(window):
    """将窗口居中显示并自适应屏幕大小"""
    from PyQt6.QtGui import QScreen
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()

    # 根据屏幕分辨率自动调整窗口大小
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    # 计算合适的窗口大小
    if screen_width < 1024:
        # 小屏幕
        width = max(600, min(int(screen_width * 0.9), 800))
        height = max(500, min(int(screen_height * 0.85), 600))
    elif screen_width < 1920:
        # 中等屏幕
        width = max(800, min(int(screen_width * 0.8), 1000))
        height = max(600, min(int(screen_height * 0.8), 700))
    else:
        # 大屏幕
        width = max(1000, min(int(screen_width * 0.7), 1200))
        height = max(700, min(int(screen_height * 0.75), 900))

    # 确保窗口大小不小于最小尺寸
    width = max(width, 800)
    height = max(height, 600)

    # 计算居中位置
    x = (screen_geometry.width() - width) // 2
    y = (screen_geometry.height() - height) // 2

    # 设置窗口几何属性
    window.setGeometry(x, y, width, height)
    logger.info(f"窗口大小设置为: {width}x{height}，位置: ({x}, {y})")


def main():
    """主函数"""
    logger.info(f"SW数字游戏 v{VERSION} 启动")
    logger.info(f"日志文件: {LOG_FILE}")

    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    logger.info("初始化QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName("SW数字游戏")
    app.setApplicationVersion(VERSION)

    app.setWindowIcon(create_app_icon())

    logger.info("创建主窗口")
    window = MainWindow()
    center_window(window)
    window.show()

    logger.info("应用程序已显示，进入事件循环")
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
