#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器管理器
管理Flask服务器的启动和运行
"""

import threading
import socket
from typing import Optional

try:
    from server.flask_app import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    create_app = None

from utils.config import GameConfig

class ServerManager:
    """服务器管理器"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.app = None
        self.server_thread = None
        self.is_running = False
    
    def get_local_ip(self) -> str:
        """获取本地IP地址"""
        try:
            # 创建一个UDP socket来获取本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'
    
    def start_server(self):
        """启动服务器"""
        if self.is_running:
            return
            
        if not FLASK_AVAILABLE:
            raise ImportError("Flask依赖未安装，无法启动服务器")
        
        # 检查网络连接
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except (socket.error, OSError):
            try:
                socket.create_connection(("192.168.1.1", 80), timeout=3)
            except (socket.error, OSError):
                raise ConnectionError("未检测到网络连接，无法启动服务器")
        
        self.app = create_app()
        
        # 创建服务器线程
        def run_server():
            host = self.config.get('server.host', '0.0.0.0')
            port = self.config.get('server.port', 5000)
            debug = self.config.get('server.debug', False)
            
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=False,
                threaded=True
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
    
    def stop_server(self):
        """停止服务器"""
        # 注意：根据需求，服务器启动后不能关闭
        # 这个方法主要用于程序退出时的清理
        if self.app and hasattr(self.app, 'shutdown'):
            try:
                self.app.shutdown()
            except:
                pass
        self.is_running = False