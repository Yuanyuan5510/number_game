#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件端网页集成界面
直接在软件内显示网页版游戏，解决方向键问题
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QHBoxLayout, QPushButton, QLabel,
                             QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer

class WebGameWindow(QMainWindow):
    """网页游戏窗口 - 集成网页版游戏到软件中"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SW数字游戏 - 网页集成版')
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建主部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建顶部工具栏
        self.create_toolbar()
        
        # 创建网页视图
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        
        # 加载网页版游戏
        self.load_game()
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8E53;
            }
            QPushButton:pressed {
                background-color: #E55A2B;
            }
        """)
    
    def create_toolbar(self):
        """创建顶部工具栏（仅保留更新和介绍按钮）"""
        toolbar = QHBoxLayout()
        
        # 标题
        title = QLabel('SW数字游戏 - 网页版')
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        # 查看更新按钮
        updates_btn = QPushButton('查看更新')
        updates_btn.clicked.connect(self.show_updates)
        toolbar.addWidget(updates_btn)
        
        # 查看介绍按钮
        welcome_btn = QPushButton('查看介绍')
        welcome_btn.clicked.connect(self.show_welcome)
        toolbar.addWidget(welcome_btn)
        
        self.layout.addLayout(toolbar)
    
    def load_game(self):
        """加载网页版游戏"""
        # 加载本地网页版游戏 - 使用本地文件路径
        game_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'desktop_local.html')
        game_url = QUrl.fromLocalFile(game_path)
        self.web_view.load(game_url)
        
        # 设置网页视图属性
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.LocalStorageEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.LocalContentCanAccessFileUrls, True)

    def show_updates(self):
        """显示更新日志"""
        updates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'updates.html')
        updates_url = QUrl.fromLocalFile(updates_path)
        self.web_view.load(updates_url)
        
        # 5秒后自动返回游戏
        QTimer.singleShot(5000, self.return_to_game)

    def show_welcome(self):
        """显示介绍页面"""
        welcome_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'welcome.html')
        welcome_url = QUrl.fromLocalFile(welcome_path)
        self.web_view.load(welcome_url)
        
        # 5秒后自动返回游戏
        QTimer.singleShot(5000, self.return_to_game)
    
    def return_to_game(self):
        """返回游戏"""
        self.load_game()
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出游戏吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebGameWindow()
    window.show()
    sys.exit(app.exec_())