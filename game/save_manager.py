#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏保存管理器
支持游戏进度保存和恢复功能
"""

import json
import os
import pickle
from datetime import datetime
from typing import Dict, Any, Optional, List

class SaveManager:
    """游戏保存管理器"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        self.ensure_save_dir()
        
    def ensure_save_dir(self):
        """确保保存目录存在"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def get_save_path(self, save_name: str) -> str:
        """获取保存文件路径"""
        return os.path.join(self.save_dir, f"{save_name}.json")
        
    def save_game(self, game_state: Dict[str, Any], save_name: str = "auto_save") -> bool:
        """
        保存游戏状态
        
        Args:
            game_state: 游戏状态字典
            save_name: 保存名称
            
        Returns:
            bool: 保存是否成功
        """
        try:
            save_data = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'game_state': game_state,
                'version': '2.1.0'
            }
            
            with open(self.get_save_path(save_name), 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
            
    def load_game(self, save_name: str = "auto_save") -> Optional[Dict[str, Any]]:
        """
        加载游戏状态
        
        Args:
            save_name: 保存名称
            
        Returns:
            Optional[Dict[str, Any]]: 游戏状态字典，如果加载失败返回None
        """
        try:
            save_path = self.get_save_path(save_name)
            if not os.path.exists(save_path):
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            return save_data.get('game_state')
            
        except Exception as e:
            print(f"加载游戏失败: {e}")
            return None
            
    def list_saves(self) -> List[Dict[str, str]]:
        """
        列出所有保存的游戏
        
        Returns:
            List[Dict[str, str]]: 保存信息列表
        """
        saves = []
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    save_name = filename[:-5]  # 去掉.json后缀
                    save_path = os.path.join(self.save_dir, filename)
                    
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                            
                        saves.append({
                            'name': save_name,
                            'date': save_data.get('date', '未知时间'),
                            'version': save_data.get('version', '未知版本')
                        })
                    except:
                        continue
                        
        except Exception as e:
            print(f"列出保存文件失败: {e}")
            
        return sorted(saves, key=lambda x: x['date'], reverse=True)
        
    def delete_save(self, save_name: str) -> bool:
        """
        删除保存的游戏
        
        Args:
            save_name: 保存名称
            
        Returns:
            bool: 删除是否成功
        """
        try:
            save_path = self.get_save_path(save_name)
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            return False
            
        except Exception as e:
            print(f"删除保存文件失败: {e}")
            return False
            
    def should_auto_save(self, max_tile: int) -> bool:
        """
        判断是否达到自动保存条件
        
        Args:
            max_tile: 当前最大方块值
            
        Returns:
            bool: 是否应该自动保存
        """
        # 达到2048的倍数时自动保存
        return max_tile >= 2048 and max_tile % 2048 == 0
        
    def get_latest_save(self) -> Optional[Dict[str, str]]:
        """
        获取最新的保存文件信息
        
        Returns:
            Optional[Dict[str, str]]: 最新保存信息
        """
        saves = self.list_saves()
        return saves[0] if saves else None

# 全局保存管理器实例
save_manager = SaveManager()