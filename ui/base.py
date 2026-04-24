#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口基类模块
提供所有窗口的公共功能
"""

import os
import sys
import logging
from typing import Optional

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
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, pyqtSlot, QObject, pyqtSignal

logger = logging.getLogger('SW数字游戏.UI')

class WindowCommunicator(QObject):
    """窗口通信类，用于JavaScript和Python之间的通信"""
    goBack = pyqtSignal()
    openUpdates = pyqtSignal()

    def __init__(self, window: 'BaseWindow'):
        super().__init__()
        self.window = window

    @pyqtSlot()
    def goBackToGame(self):
        """处理返回游戏按钮点击"""
        logger.info("用户点击返回游戏按钮")
        self.goBack.emit()

    @pyqtSlot()
    def open_updates(self):
        """处理查看更新按钮点击"""
        logger.info("用户点击查看更新按钮")
        self.openUpdates.emit()


class BaseWindow(QMainWindow):
    """窗口基类，提供公共功能"""

    DEFAULT_BACKGROUND_COLOR = "#f0f0f0"

    def __init__(self, title: str = "SW数字游戏", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self._communicator: Optional[WindowCommunicator] = None
        self._web_view: Optional[QWebEngineView] = None
        self._channel: Optional[QWebChannel] = None
        self._setup_base_ui()
        logger.debug(f"BaseWindow初始化: {title}")

    def _setup_base_ui(self):
        """初始化基础UI结构"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {self.DEFAULT_BACKGROUND_COLOR};")
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self._central_layout = layout

    def create_webview(self) -> QWebEngineView:
        """创建并配置WebView"""
        web_view = QWebEngineView()
        web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        settings = web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        self._web_view = web_view
        return web_view

    def setup_webchannel(self, web_view: QWebEngineView):
        """设置WebChannel用于JavaScript通信"""
        self._channel = QWebChannel()
        self._communicator = WindowCommunicator(self)
        self._channel.registerObject("communicator", self._communicator)
        web_view.page().setWebChannel(self._channel)

    def load_html_file(self, relative_path: str, base_dir: Optional[str] = None) -> bool:
        """加载HTML文件

        Args:
            relative_path: 相对于base_dir的路径
            base_dir: 基础目录，默认为main.py所在目录

        Returns:
            是否加载成功
        """
        if base_dir is None:
            file_path = get_resource_path(relative_path)
        else:
            file_path = os.path.join(base_dir, relative_path)

        if os.path.exists(file_path):
            if self._web_view:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    file_dir = os.path.dirname(file_path)
                    self._web_view.setHtml(html_content, QUrl.fromLocalFile(file_dir))
                    logger.info(f"加载HTML文件: {file_path}")
                    return True
                except Exception as e:
                    logger.error(f"读取HTML文件失败: {e}")
                    return False
            else:
                logger.error("WebView未初始化")
                return False
        else:
            logger.warning(f"HTML文件不存在: {file_path}")
            return False

    def load_html_content(self, html_content: str, base_url: Optional[str] = None):
        """加载HTML内容

        Args:
            html_content: HTML内容字符串
            base_url: 基础URL（用于相对路径）
        """
        if self._web_view:
            self._web_view.setHtml(html_content, baseUrl=QUrl.fromLocalFile(base_url) if base_url else QUrl())
            logger.debug("HTML内容已加载")
        else:
            logger.error("WebView未初始化，无法加载HTML内容")

    def add_webview_to_layout(self, web_view: QWebEngineView):
        """将WebView添加到布局"""
        self._central_layout.addWidget(web_view)

    def get_webview(self) -> Optional[QWebEngineView]:
        """获取WebView实例"""
        return self._web_view

    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.debug(f"关闭窗口: {self.windowTitle()}")
        if self._web_view:
            self._web_view.stop()
            self._web_view.deleteLater()
        event.accept()

    def set_background_color(self, color: str):
        """设置背景颜色

        Args:
            color: CSS颜色值，如 '#f0f0f0'
        """
        self.setStyleSheet(f"background-color: {color};")

    @staticmethod
    def center_window(window: 'QMainWindow'):
        """将窗口居中显示"""
        from PyQt6.QtGui import QScreen
        from PyQt6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if not screen:
            return

        screen_geometry = screen.availableGeometry()

        width = int(screen_geometry.width() * 0.7)
        height = int(screen_geometry.height() * 0.8)

        if screen_geometry.width() < 1024:
            width = max(600, min(width, 800))
            height = max(500, min(height, 600))
        else:
            width = max(800, min(width, 1200))
            height = max(600, min(height, 900))

        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2

        window.setGeometry(x, y, width, height)
