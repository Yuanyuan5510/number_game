import sys
import traceback
import logging
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QDialog, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QPen


class ErrorDialog(QDialog):
    def __init__(self, error_info, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self.setWindowTitle("游戏错误报告")
        self.setFixedSize(600, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 设置窗口图标
        self.setup_window_icon()
        
        self.init_ui()
        self.center_on_screen()
    
    def setup_window_icon(self):
        """设置窗口图标，与启动动画图标保持一致"""
        try:
            # 创建2048图标
            icon_size = 32
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 绘制圆形背景
            gradient_color = QColor(76, 175, 80)
            painter.setBrush(gradient_color)
            painter.setPen(QPen(gradient_color.darker(120), 2))
            painter.drawEllipse(2, 2, icon_size-4, icon_size-4)
            
            # 绘制文字
            painter.setPen(Qt.white)
            font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "2048")
            
            painter.end()
            self.setWindowIcon(QIcon(pixmap))
        except Exception:
            pass
    
    def init_ui(self):
        """初始化错误对话框界面"""
        layout = QVBoxLayout()
        
        # 错误图标和标题
        header_layout = QHBoxLayout()
        
        error_icon = QLabel("⚠️")
        error_icon.setStyleSheet("font-size: 48px; margin-right: 10px;")
        header_layout.addWidget(error_icon)
        
        title_layout = QVBoxLayout()
        title_label = QLabel("游戏运行时遇到错误")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #d32f2f;")
        subtitle_label = QLabel("请查看下面的详细信息或联系技术支持")
        subtitle_label.setStyleSheet("color: #666;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 错误详情文本框
        self.error_text = QTextEdit()
        self.error_text.setPlainText(self.error_info)
        self.error_text.setReadOnly(True)
        self.error_text.setFont(QFont("Consolas", 9))
        self.error_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.error_text)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("复制错误信息")
        copy_button.clicked.connect(self.copy_error)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(copy_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def center_on_screen(self):
        """将窗口居中显示"""
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def copy_error(self):
        """复制错误信息到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.error_info)
        QMessageBox.information(self, "已复制", "错误信息已复制到剪贴板！")


class ErrorHandler:
    """全局错误处理器"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志记录"""
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
            self.logger = logging.getLogger('NumberGame')
            self.logger.info("日志系统已初始化")
        except Exception as e:
            print(f"日志初始化失败: {e}")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """全局异常处理函数"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 如果是键盘中断，使用默认处理
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 格式化错误信息
        error_info = """游戏运行时发生错误！

错误类型：{}
错误信息：{}

详细堆栈：
{}""".format(
            exc_type.__name__,
            str(exc_value),
            ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        )
        
        # 记录到日志文件
        try:
            self.logger.error(f"发生异常：{exc_value}", exc_info=(exc_type, exc_value, exc_traceback))
        except Exception:
            # 如果日志系统失败，回退到文件记录
            try:
                with open("error.log", "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(error_info)
                    f.write(f"\n{'='*50}\n")
            except Exception:
                pass
        
        # 显示错误对话框
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ErrorDialog(error_info)
        dialog.exec_()


def install_error_handler():
    """安装全局错误处理器"""
    error_handler = ErrorHandler()
    sys.excepthook = error_handler.handle_exception
    return error_handler