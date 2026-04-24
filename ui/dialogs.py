#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话框窗口模块
提供更新窗口、欢迎窗口、用户管理窗口
"""

import os
import sys
import json
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

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
                            QTableWidgetItem, QFrame, QHBoxLayout, QHeaderView, QCheckBox,
                            QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPalette
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QCategoryAxis

from .base import BaseWindow

logger = logging.getLogger('SW数字游戏.UI.Dialogs')


class UpdateWindow(BaseWindow):
    """更新日志窗口"""

    go_back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("SW数字游戏 - 更新日志", parent)
        self.resize(800, 600)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = self._central_layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtCore import Qt, QUrl

        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.setup_webchannel(self.web_view)

        if self._communicator:
            self._communicator.goBack.connect(self._on_go_back)

        main_layout.addWidget(self.web_view)

        file_path = get_resource_path('updates.html')
        if os.path.exists(file_path):
            self.web_view.load(QUrl.fromLocalFile(file_path))
            logger.info(f"加载更新日志页面: {file_path}")
        else:
            logger.warning(f"更新日志文件不存在: {file_path}")

        self.center_window(self)

    def _on_go_back(self):
        """返回游戏"""
        logger.info("用户请求从更新页面返回")
        self.go_back_signal.emit()
        self.close()


class WelcomeWindow(BaseWindow):
    """欢迎页面窗口"""

    open_updates_signal = pyqtSignal()
    go_back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("SW数字游戏 - 欢迎页面", parent)
        self.resize(900, 700)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = self._central_layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtCore import Qt, QUrl

        self.web_view = QWebEngineView()
        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # 设置WebChannel通信
        self.setup_webchannel(self.web_view)

        # 连接信号
        if self._communicator:
            self._communicator.openUpdates.connect(self._on_open_updates)
            self._communicator.goBack.connect(self._on_go_back)

        main_layout.addWidget(self.web_view)

        file_path = get_resource_path('welcome.html')
        if os.path.exists(file_path):
            self.web_view.load(QUrl.fromLocalFile(file_path))
            logger.info(f"加载欢迎页面: {file_path}")
        else:
            logger.warning(f"欢迎页面文件不存在: {file_path}")

        self.center_window(self)

    def _on_open_updates(self):
        """打开更新窗口"""
        logger.info("用户请求打开更新窗口")
        self.open_updates_signal.emit()
        self.close()

    def _on_go_back(self):
        """返回游戏"""
        logger.info("用户请求返回游戏")
        self.go_back_signal.emit()
        self.close()


class UserManagementWindow(BaseWindow):
    """用户管理窗口"""

    def __init__(self, parent=None):
        super().__init__("SW数字游戏 - 用户管理", parent)
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self._init_ui()
        self.center_window(self)

    def _init_ui(self):
        """初始化UI"""
        main_layout = self._central_layout
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("用户管理")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #667eea;")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)

        refresh_button = QPushButton("刷新用户列表")
        refresh_button.clicked.connect(self.refresh_user_list)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton:pressed {
                background-color: #4456b0;
            }
        """)
        control_layout.addWidget(refresh_button)
        control_layout.addStretch()

        list_frame = QFrame()
        list_frame.setFrameShape(QFrame.Shape.StyledPanel)
        list_frame.setFrameShadow(QFrame.Shadow.Raised)
        list_layout = QVBoxLayout(list_frame)

        self.user_list = QTableWidget()
        self.user_list.setColumnCount(4)
        self.user_list.setHorizontalHeaderLabels(["用户ID", "用户名", "分数", "删除"])
        self.user_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.user_list.setAlternatingRowColors(True)
        self.user_list.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #667eea;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #5568d3;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.user_list.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e7ff;
                border-radius: 8px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f4ff;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: #f8faff;
            }
        """)
        list_layout.addWidget(self.user_list)
        main_layout.addWidget(list_frame)
        main_layout.addSpacing(20)



        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.Shape.StyledPanel)
        chart_frame.setFrameShadow(QFrame.Shadow.Raised)
        chart_layout = QVBoxLayout(chart_frame)

        chart_title = QLabel("分数数据可视化")
        chart_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #667eea;")
        chart_layout.addWidget(chart_title)

        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        self.chart_view.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        chart_layout.addWidget(self.chart_view)

        main_layout.addWidget(chart_frame)

        self.refresh_user_list()

    def refresh_user_list(self):
        """刷新用户列表"""
        logger.info("刷新用户列表")
        self.user_list.setRowCount(0)

        # 添加加载状态提示
        self.user_list.insertRow(0)
        loading_item = QTableWidgetItem("加载中...")
        loading_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_list.setItem(0, 0, loading_item)
        self.user_list.setSpan(0, 0, 1, 4)

        try:
            users = self._load_local_users()
            self.user_list.setRowCount(0)
            if users:
                for i, user in enumerate(users):
                    self.user_list.insertRow(i)
                    self.user_list.setItem(i, 0, QTableWidgetItem(user.get("id", "")))
                    self.user_list.setItem(i, 1, QTableWidgetItem(user.get("name", "")))
                    self.user_list.setItem(i, 2, QTableWidgetItem(str(user.get("score", 0))))

                    delete_button = QPushButton("删除")
                    delete_button.clicked.connect(lambda checked, uid=user.get("id", ""): self.delete_user(uid))
                    delete_button.setStyleSheet("""
                        QPushButton {
                            background-color: #d32f2f;
                            color: #ffffff;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 3px;
                            font-size: 12px;
                            font-weight: bold;
                            text-align: center;
                        }
                        QPushButton:hover {
                            background-color: #b71c1c;
                        }
                        QPushButton:pressed {
                            background-color: #a31515;
                        }
                    """)
                    self.user_list.setCellWidget(i, 3, delete_button)

                self.update_chart(users)
            else:
                self._load_mock_users()
        except Exception as e:
            logger.error(f"加载用户列表失败: {e}")
            self.user_list.setRowCount(0)
            self._load_mock_users()

    def _load_local_users(self):
        """从本地加载用户数据"""
        try:
            import json
            from datetime import datetime
            leaderboard_path = get_resource_path('leaderboard.json')

            if os.path.exists(leaderboard_path):
                with open(leaderboard_path, 'r', encoding='utf-8') as f:
                    scores = json.load(f)
                users = []
                for score in scores:
                    entry_date = score.get('date', '')
                    if entry_date:
                        try:
                            entry_dt = datetime.strptime(entry_date, '%Y-%m-%d %H:%M')
                            days_diff = (datetime.now() - entry_dt).days
                            if days_diff > 10 and score.get('score', 0) < 300:
                                logger.info(f"清理过期用户数据: {score.get('player_name')}, 天数: {days_diff}, 分数: {score.get('score', 0)}")
                                continue
                        except ValueError:
                            pass
                    user = {
                        'id': score.get('player_name', ''),
                        'name': score.get('player_name', '匿名玩家'),
                        'score': score.get('score', 0)
                    }
                    users.append(user)
                return users
            else:
                logger.warning("排行榜文件未找到，使用模拟数据")
                return []
        except Exception as e:
            logger.error(f"加载本地用户数据失败: {e}")
            return []

    def _load_mock_users(self):
        """加载模拟用户数据"""
        users = [
            {"id": "1", "name": "玩家_123456", "score": 2048},
            {"id": "2", "name": "玩家_789012", "score": 4096},
            {"id": "3", "name": "玩家_345678", "score": 1024}
        ]

        for i, user in enumerate(users):
            self.user_list.insertRow(i)
            self.user_list.setItem(i, 0, QTableWidgetItem(user["id"]))
            self.user_list.setItem(i, 1, QTableWidgetItem(user["name"]))
            self.user_list.setItem(i, 2, QTableWidgetItem(str(user["score"])))

            delete_button = QPushButton("删除")
            delete_button.clicked.connect(lambda checked, uid=user["id"]: self.delete_user(uid))
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: #ffffff;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 12px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
                QPushButton:pressed {
                    background-color: #a31515;
                }
            """)
            self.user_list.setCellWidget(i, 3, delete_button)

        self.update_chart(users)

    def update_chart(self, users):
        """更新分数数据图表"""
        chart = QChart()
        chart.setTitle("用户分数分布")
        chart.setTitleFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))

        user_names = [user.get("name", "") for user in users]
        user_scores = [user.get("score", 0) for user in users]

        series = QBarSeries()
        bar_set = QBarSet("分数")
        bar_set.append(user_scores)
        bar_set.setColor(QColor(102, 126, 234))
        series.append(bar_set)

        chart.addSeries(series)

        axis_x = QCategoryAxis()
        axis_x.setLabelsFont(QFont("Microsoft YaHei", 10))
        axis_x.setTitleText("用户")
        axis_x.setTitleFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))

        for i, name in enumerate(user_names):
            axis_x.append(name, i + 1)

        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(user_scores) * 1.2 if user_scores else 1000)
        axis_y.setLabelsFont(QFont("Microsoft YaHei", 10))
        axis_y.setTitleText("分数")
        axis_y.setTitleFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("""
            QChartView {
                background-color: white;
                border: 1px solid #e0e7ff;
                border-radius: 5px;
            }
        """)

    def delete_user(self, user_id: str):
        """删除用户并同步到leaderboard.json"""
        logger.info(f"删除用户: {user_id}")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除用户 {user_id} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 同步删除leaderboard.json中的记录
                sync_success = self._sync_delete_to_leaderboard(user_id)
                
                if sync_success:
                    logger.info(f"用户 {user_id} 已删除并同步到leaderboard.json")
                    QMessageBox.information(self, "删除成功", f"用户 {user_id} 已成功删除")
                else:
                    logger.error(f"删除用户失败: 同步到leaderboard.json失败")
                    QMessageBox.warning(self, "删除失败", "删除用户失败: 同步到leaderboard.json失败")
            except Exception as e:
                logger.error(f"删除用户失败: {e}")
                QMessageBox.warning(self, "删除失败", f"删除用户失败: {e}")
            finally:
                self.refresh_user_list()

    def _sync_delete_to_leaderboard(self, user_id: str, max_retries: int = 3):
        """同步删除到leaderboard.json文件"""
        leaderboard_path = get_resource_path('leaderboard.json')
        
        for attempt in range(max_retries):
            try:
                if os.path.exists(leaderboard_path):
                    with open(leaderboard_path, 'r', encoding='utf-8') as f:
                        scores = json.load(f)
                    
                    # 过滤掉要删除的用户
                    updated_scores = [score for score in scores if score.get('player_name') != user_id]
                    
                    # 写回文件
                    with open(leaderboard_path, 'w', encoding='utf-8') as f:
                        json.dump(updated_scores, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"成功同步删除用户 {user_id} 到leaderboard.json, 尝试次数: {attempt + 1}")
                    return True
                else:
                    logger.warning("排行榜文件未找到")
                    return False
            except Exception as e:
                logger.error(f"同步删除到leaderboard.json失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # 等待1秒后重试
                else:
                    return False


