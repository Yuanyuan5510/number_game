#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地游戏窗口
使用PyQt5实现的电脑端游戏界面
"""

import sys
from typing import List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QGridLayout, 
                             QMessageBox, QComboBox, QFrame, QDialog, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QKeyEvent, QIcon, QPixmap

from game.game_logic import Game2048
try:
    from game.server_manager import ServerManager, FLASK_AVAILABLE
except ImportError:
    ServerManager = None
    FLASK_AVAILABLE = False
from utils.config import GameConfig

class GameTile(QLabel):
    """游戏方块组件"""
    
    def __init__(self, value: int = 0, parent=None):
        super().__init__(parent)
        self.value = value
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(60, 60)
        self.setMaximumSize(60, 60)
        self.update_style()
    
    def update_style(self):
        """更新方块样式"""
        if self.value == 0:
            self.setText("")
            self.setStyleSheet("""
                QLabel {
                    background-color: #cdc1b4;
                    border: 1px solid #bbada0;
                    border-radius: 3px;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
        else:
            self.setText(str(self.value))
            
            # 根据数值选择颜色
            colors = {
                2: ("#eee4da", "#776e65"),
                4: ("#ede0c8", "#776e65"),
                8: ("#f2b179", "#f9f6f2"),
                16: ("#f59563", "#f9f6f2"),
                32: ("#f67c5f", "#f9f6f2"),
                64: ("#f65e3b", "#f9f6f2"),
                128: ("#edcf72", "#f9f6f2"),
                256: ("#edcc61", "#f9f6f2"),
                512: ("#edc850", "#f9f6f2"),
                1024: ("#edc53f", "#f9f6f2"),
                2048: ("#edc22e", "#f9f6f2")
            }
            
            bg_color, text_color = colors.get(self.value, ("#3c3a32", "#f9f6f2"))
            
            # 根据数值大小调整字体大小和样式
            value = str(self.value)
            if value == 'M':
                font_size = 20  # 更大的字体
                bg_color = "#ff4757"  # 鲜艳的红色背景，更醒目
                text_color = "#ffffff"  # 白色文字
                border_color = "#ff3742"  # 边框颜色
            elif isinstance(self.value, int):
                if self.value >= 1000:
                    font_size = 14
                elif self.value >= 100:
                    font_size = 16
                else:
                    font_size = 18
            else:
                font_size = 18
            
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid #bbada0;
                    border-radius: 3px;
                    font-size: {font_size}px;
                    font-weight: bold;
                }}
            """)
    
    def set_value(self, value: int):
        """设置方块值"""
        self.value = value
        self.update_style()

class GameGrid(QWidget):
    """游戏网格组件"""
    
    def __init__(self, size: int = 4, parent=None):
        super().__init__(parent)
        self.size = size
        self.tiles = []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QGridLayout()
        layout.setSpacing(5)
        
        self.tiles = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                tile = GameTile(0)
                layout.addWidget(tile, i, j)
                row.append(tile)
            self.tiles.append(row)
        
        self.setLayout(layout)
    
    def update_grid(self, grid: List[List[int]]):
        """更新网格显示"""
        for i in range(self.size):
            for j in range(self.size):
                self.tiles[i][j].set_value(grid[i][j])
    
    def resize_grid(self, new_size: int):
        """调整网格大小"""
        self.size = new_size
        
        # 清除旧布局
        if self.layout():
            old_layout = self.layout()
            for i in reversed(range(old_layout.count())):
                widget = old_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            import sip
            sip.delete(old_layout)
        
        # 重新创建网格
        self.init_ui()

class LocalGameWindow(QMainWindow):
    """本地游戏主窗口"""
    
    def __init__(self, config: GameConfig):
        super().__init__()
        self.config = config
        self.game = Game2048(4)
        self.server_manager = None
        self.server_thread = None
        
        # 初始化UI后再处理Flask相关设置
        
        # 设置窗口图标（与启动动画一致）
        self.setup_window_icon()
        
        self.init_ui()
        self.update_display()
        
        # 设置适宜大小的窗口并居中
        self.setFixedSize(600, 700)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 600) // 2
        y = (screen.height() - 700) // 2
        self.move(x, y)
    
    def setup_window_icon(self):
        """设置窗口图标 - SW主题"""
        icon_size = 64
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制SW橙色渐变背景
        from PyQt5.QtGui import QColor
        painter.setBrush(QColor(255, 107, 53))  # SW橙色
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pixmap.rect().adjusted(4, 4, -4, -4), 8, 8)
        
        # 绘制白色"SW"
        painter.setPen(Qt.white)
        font = QFont("Arial", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "SW")
        
        painter.end()
        
        self.setWindowIcon(QIcon(pixmap))
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('SW数字游戏')
        self.setMinimumSize(800, 600)
        # 启动时全屏显示
        self.showMaximized()
        self.setWindowState(Qt.WindowMaximized)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        # 分数显示
        self.score_label = QLabel('分数: 0')
        self.score_label.setFont(QFont('Arial', 14))
        control_layout.addWidget(self.score_label)
        
        # 最高分显示
        self.high_score_label = QLabel('最高分: 0')
        self.high_score_label.setFont(QFont('Arial', 14))
        control_layout.addWidget(self.high_score_label)
        
        # 移动次数
        self.moves_label = QLabel('移动: 0')
        self.moves_label.setFont(QFont('Arial', 14))
        control_layout.addWidget(self.moves_label)
        
        # 网格大小选择 - 限制最大8x8
        self.size_combo = QComboBox()
        for size in range(4, 9):  # 4到8
            self.size_combo.addItem(f'{size}×{size}', size)
        self.size_combo.currentTextChanged.connect(self.change_grid_size)
        control_layout.addWidget(QLabel('网格大小:'))
        control_layout.addWidget(self.size_combo)
        
        # 游戏操作按钮
        self.new_game_btn = QPushButton('新游戏')
        self.new_game_btn.clicked.connect(self.new_game)
        control_layout.addWidget(self.new_game_btn)
        
        # 联机游戏按钮
        self.online_btn = QPushButton('局域网对战')
        self.online_btn.clicked.connect(self.toggle_online_mode)
        control_layout.addWidget(self.online_btn)
        
        main_layout.addLayout(control_layout)
        
        # 游戏网格
        self.game_grid = GameGrid(4)
        main_layout.addWidget(self.game_grid, alignment=Qt.AlignCenter)
        
        # 游戏说明
        help_label = QLabel('使用方向键 ↑ ↓ ← → 控制移动')
        help_label.setFont(QFont('Arial', 12))
        help_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(help_label)
        
        central_widget.setLayout(main_layout)
        
        # 如果没有Flask，禁用联机功能
        if not FLASK_AVAILABLE:
            self.online_btn.setEnabled(False)
            self.online_btn.setText("联机功能不可用")
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件 - 只允许方向键控制移动"""
        key = event.key()
        
        # ESC键退出
        if key == Qt.Key_Escape:
            self.close()
            return
        
        # 空格键重新开始
        if key == Qt.Key_Space:
            self.new_game()
            return
        
        # 游戏方向控制 - 只允许方向键控制移动
        if not self.game.game_over:
            moved = False
            
            if key == Qt.Key_Left:
                moved = self.game.move_left()
            elif key == Qt.Key_Right:
                moved = self.game.move_right()
            elif key == Qt.Key_Up:
                moved = self.game.move_up()
            elif key == Qt.Key_Down:
                moved = self.game.move_down()
            else:
                # 忽略其他所有按键，包括数字键
                return
            
            if moved:
                # 添加新方块并检查游戏状态
                self.game.add_new_tile()
                self.game.update_score()
                
                # 检查游戏是否结束
                if self.game.is_game_over():
                    self.game.game_over = True
                    self.show_game_over()
                elif self.game.won and not hasattr(self.game, '_won_shown'):
                    self.game._won_shown = True
                    self.show_game_won()
                
                self.update_display()
    
    def update_display(self):
        """更新显示"""
        self.game_grid.update_grid(self.game.grid)
        self.score_label.setText(f'分数: {self.game.score}')
        self.high_score_label.setText(f'最高分: {self.game.high_score}')
        self.moves_label.setText(f'移动: {self.game.moves}')
    
    def new_game(self):
        """开始新游戏"""
        self.game.reset()
        self.update_display()
    
    def change_grid_size(self, text):
        """改变网格大小"""
        size = self.size_combo.currentData()
        if size != self.game.size:
            self.game = Game2048(size)
            self.game_grid.resize_grid(size)
            self.update_display()
    
    def show_game_over(self):
        """显示游戏结束对话框并记录分数"""
        # 记录分数
        self.save_score()
        
        # 显示排行榜
        self.show_leaderboard()
        
        msg = QMessageBox()
        msg.setWindowTitle('😢 游戏结束')
        msg.setText(f'游戏结束！\n\n最终分数: {self.game.score}\n移动次数: {self.game.moves}\n\n点击任意位置自动开启新游戏！')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setButtonText(QMessageBox.Ok, "开始新游戏")
        msg.setDefaultButton(QMessageBox.Ok)
        
        # 无论用户选择什么，都会开始新游戏
        msg.exec_()
        self.new_game()
    
    def show_leaderboard(self):
        """显示排行榜"""
        try:
            import os
            import json
            
            scores_file = os.path.join('saves', 'scores.json')
            if not os.path.exists(scores_file):
                return
                
            with open(scores_file, 'r', encoding='utf-8') as f:
                scores = json.load(f)
            
            if not scores:
                return
                
            # 按分数排序
            scores.sort(key=lambda x: x['score'], reverse=True)
            
            # 创建排行榜文本
            leaderboard_text = "🏆 排行榜\n"
            for i, score in enumerate(scores[:10], 1):
                leaderboard_text += f"{i}. {score['name']}: {score['score']}分\n"
            
            msg = QMessageBox()
            msg.setWindowTitle('🏆 排行榜')
            msg.setText(leaderboard_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
        except Exception as e:
            print(f"显示排行榜失败: {e}")
    
    def show_game_won(self):
        """显示游戏胜利对话框"""
        msg = QMessageBox()
        msg.setWindowTitle('🎉 游戏胜利！')
        msg.setText(f'🎊 恭喜！您已达到2048！\n\n当前分数: {self.game.score}\n移动次数: {self.game.moves}\n\n您可以选择继续游戏挑战更高分数，或开始新游戏。')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setButtonText(QMessageBox.Yes, "继续游戏")
        msg.setButtonText(QMessageBox.No, "开始新游戏")
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.No:
            self.new_game()
    
    def toggle_online_mode(self):
        """切换联机模式"""
        if not FLASK_AVAILABLE:
            QMessageBox.warning(
                self,
                '提示',
                '联机功能需要安装Flask，请运行：\n\npip install flask flask-socketio'
            )
            return
            
        if self.server_manager is None:
            self.start_online_mode()
        else:
            self.stop_online_mode()
    
    def start_online_mode(self):
        """启动联机模式"""
        try:
            from game.server_manager import ServerManager
            
            # 创建服务器管理器
            self.server_manager = ServerManager(self.config)
            self.server_manager.start_server()
            
            self.online_btn.setText('停止局域网')
            self.setWindowTitle('数字消消乐 - 局域网模式')
            
            # 显示服务器信息
            QMessageBox.information(
                self, '局域网对战', 
                f'服务器已启动！\n\n'
                f'局域网地址: http://{self.server_manager.get_local_ip()}:5000\n'
                f'告诉你的朋友访问这个地址加入游戏！\n\n'
                f'注意：服务器启动后不能关闭，直到程序退出。'
            )
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'启动服务器失败: {str(e)}')
    
    def stop_online_mode(self):
        """停止联机模式"""
        if self.server_manager:
            # 注意：根据需求，服务器启动后不能关闭
            QMessageBox.information(
                self, '提示', 
                '服务器已启动，不能关闭！\n'
                '程序退出时服务器会自动停止。'
            )
    
    def save_score(self, player_name=None):
        """记录分数"""
        try:
            import os
            import json
            from datetime import datetime
            
            # 创建分数记录文件
            scores_file = os.path.join('saves', 'scores.json')
            os.makedirs('saves', exist_ok=True)
            
            # 读取现有分数
            scores = []
            if os.path.exists(scores_file):
                try:
                    with open(scores_file, 'r', encoding='utf-8') as f:
                        scores = json.load(f)
                except:
                    scores = []
            
            # 确定玩家名称
            if player_name:
                name = player_name
            elif self.server_manager:
                # 局域网模式，根据IP或其他标识确定玩家名称
                name = self.get_lan_player_name()
            else:
                name = 'You'
            
            # 添加新分数
            new_score = {
                'name': name,
                'score': self.game.score,
                'moves': self.game.moves,
                'grid_size': self.game.size,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': 'LAN' if self.server_manager else 'Local'
            }
            scores.append(new_score)
            
            # 保存分数
            with open(scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存分数失败: {e}")
    
    def get_lan_player_name(self):
        """获取局域网玩家名称"""
        # 简单的局域网玩家命名
        if not hasattr(self, '_player_counter'):
            self._player_counter = 0
        
        self._player_counter += 1
        return f'朋友{self._player_counter}'
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.server_manager:
            reply = QMessageBox.question(
                self, '确认退出',
                '确定要退出游戏吗？\n'
                '局域网服务器将停止运行。',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.server_manager:
                    self.server_manager.stop_server()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()