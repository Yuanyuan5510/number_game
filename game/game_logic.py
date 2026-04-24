#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏核心逻辑
实现2048游戏的核心算法
"""

import random
import copy
import json
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

class Game2048:
    """2048游戏核心逻辑类"""
    
    def __init__(self, size: int = 4):
        """初始化游戏
        
        Args:
            size: 游戏网格大小，默认为4
        """
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.score = 0
        self.high_score = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        self.special_tiles = []  # 特殊方块位置
        self.save_dir = "saves"
        
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        # 初始化游戏
        self.add_new_tile()
        self.add_new_tile()
        self.update_score()  # 初始化分数
    
    def add_new_tile(self) -> bool:
        """添加新的数字方块"""
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            # 检查是否真的无法移动
            if self.is_game_over():
                self.game_over = True
            return False
        
        row, col = random.choice(empty_cells)
        
        # 新方块生成概率：2(90%)、4(10%)
        rand = random.random()
        if rand < 0.9:
            value = 2
        else:
            value = 4
            
        self.grid[row][col] = value
        
        return True
    
    def move_left(self) -> bool:
        """向左移动
        
        Returns:
            是否有方块移动或合并
        """
        moved = False
        new_grid = []
        special_merged = False
        
        for row in self.grid:
            # 处理特殊方块M
            new_row = []
            for val in row:
                if val != 0 and val != 'M':
                    new_row.append(val)
                elif val == 'M':
                    new_row.append('M')
            
            # 合并相同的数字
            merged = []
            i = 0
            while i < len(new_row):
                if i + 1 < len(new_row) and new_row[i] == new_row[i + 1] and new_row[i] != 'M':
                    merged_value = new_row[i] * 2
                    merged.append(merged_value)
                    if merged_value == 2048 and not self.won:
                        self.won = True
                    i += 2
                elif new_row[i] == 'M' and i + 1 < len(new_row) and new_row[i + 1] == 'M':
                    # 两个M结合，消除附近方块
                    merged.append(0)  # 消除M
                    special_merged = True
                    i += 2
                else:
                    merged.append(new_row[i])
                    i += 1
            
            # 填充零
            merged.extend([0] * (self.size - len(merged)))
            new_grid.append(merged)
            
            if merged != row:
                moved = True
        
        if moved or special_merged:
            if special_merged:
                self.clear_surrounding_tiles()
            self.grid = new_grid
            self.moves += 1
            self.add_new_tile()
            self.update_score()  # 更新分数
            self.check_game_over()  # 检查游戏结束
        
        return moved or special_merged
    
    def move_right(self) -> bool:
        """向右移动"""
        # 反转每一行，然后向左移动，再反转回来
        reversed_grid = [row[::-1] for row in self.grid]
        self.grid = reversed_grid
        moved = self.move_left()
        self.grid = [row[::-1] for row in self.grid]
        return moved
    
    def move_up(self) -> bool:
        """向上移动"""
        # 转置矩阵，向左移动，再转置回来
        transposed = [list(row) for row in zip(*self.grid)]
        self.grid = transposed
        moved = self.move_left()
        self.grid = [list(row) for row in zip(*self.grid)]
        return moved
    
    def move_down(self) -> bool:
        """向下移动"""
        # 转置矩阵，向右移动，再转置回来
        transposed = [list(row) for row in zip(*self.grid)]
        reversed_transposed = [row[::-1] for row in transposed]
        self.grid = reversed_transposed
        moved = self.move_left()
        self.grid = [row[::-1] for row in self.grid]
        self.grid = [list(row) for row in zip(*self.grid)]
        return moved
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束
        
        Returns:
            True如果游戏结束，False否则
        """
        # 检查是否有空格
        for row in self.grid:
            if 0 in row:
                return False
            if 'M' in row:
                return False  # 特殊方块M可以继续游戏
        
        # 检查是否有可以合并的相邻方块
        for i in range(self.size):
            for j in range(self.size):
                current = self.grid[i][j]
                # 检查右边
                if j + 1 < self.size and self.grid[i][j + 1] == current:
                    return False
                # 检查下面
                if i + 1 < self.size and self.grid[i + 1][j] == current:
                    return False
                # 检查特殊方块M
                if current == 'M':
                    # 检查是否有另一个M相邻
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + dr, j + dc
                        if 0 <= ni < self.size and 0 <= nj < self.size and self.grid[ni][nj] == 'M':
                            return False
        
        return True
    
    def can_move(self) -> bool:
        """检查是否可以移动"""
        if not self.is_game_over():
            return True
        
        # 创建临时游戏状态检查是否可以移动
        temp_game = copy.deepcopy(self)
        return (temp_game.move_left() or 
                temp_game.move_right() or 
                temp_game.move_up() or 
                temp_game.move_down())
    
    def check_game_over(self) -> bool:
        """检查并设置游戏结束状态"""
        if self.is_game_over():
            self.game_over = True
            return True
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """获取游戏状态"""
        return {
            'grid': self.grid,
            'score': self.score,
            'high_score': self.high_score,
            'moves': self.moves,
            'game_over': self.game_over,
            'won': self.won,
            'size': self.size,
            'max_tile': self.get_max_tile()
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """设置游戏状态"""
        self.grid = state['grid']
        self.score = state['score']
        self.high_score = max(self.high_score, state.get('high_score', 0))
        self.moves = state['moves']
        self.game_over = state['game_over']
        self.won = state['won']
        self.size = state['size']
    
    def reset(self) -> None:
        """重置游戏"""
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        
        self.add_new_tile()
        self.add_new_tile()
        self.update_score()  # 重置后更新分数
    
    def save_game(self, save_name: str = "auto_save") -> bool:
        """保存游戏"""
        try:
            save_data = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'game_state': self.get_state(),
                'version': '2.1.0'
            }
            
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, save_name: str = "auto_save") -> bool:
        """加载游戏"""
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            if not os.path.exists(save_path):
                return False
                
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            game_state = save_data.get('game_state')
            if game_state:
                self.set_state(game_state)
                return True
                
        except Exception as e:
            print(f"加载游戏失败: {e}")
        return False
    
    def list_saves(self) -> list:
        """列出所有保存的游戏"""
        saves = []
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    save_name = filename[:-5]
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
    
    def check_auto_save(self) -> bool:
        """检查是否应该自动保存"""
        max_tile = self.get_max_tile()
        return max_tile >= 2048 and max_tile % 2048 == 0
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """获取空单元格位置"""
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells
    
    def get_max_tile(self) -> int:
        """获取最大方块值"""
        try:
            return max(max(val for val in row if isinstance(val, int)) for row in self.grid if any(isinstance(val, int) for val in row))
        except ValueError:
            return 0
    
    def calculate_total_score(self) -> int:
        """计算网格内所有数字的总和作为分数"""
        total = 0
        for row in self.grid:
            for val in row:
                if isinstance(val, int) and val > 0:
                    total += val
        return total
    
    def clear_surrounding_tiles(self) -> None:
        """清除特殊方块周围的方块"""
        # 找到所有M的位置
        m_positions = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 'M':
                    m_positions.append((i, j))
        
        # 清除每个M周围的方块
        for row, col in m_positions:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < self.size and 0 <= new_col < self.size:
                        if isinstance(self.grid[new_row][new_col], int):
                            self.score += self.grid[new_row][new_col]  # 加分
                        self.grid[new_row][new_col] = 0
    
    def get_animated_moves(self, direction: str) -> list:
        """获取带有动画的移动序列
        
        Args:
            direction: 移动方向 ('left', 'right', 'up', 'down')
            
        Returns:
            动画帧列表，每帧包含网格状态
        """
        frames = []
        original_grid = [row[:] for row in self.grid]
        
        # 根据方向执行移动
        if direction == 'left':
            self.move_left()
        elif direction == 'right':
            self.move_right()
        elif direction == 'up':
            self.move_up()
        elif direction == 'down':
            self.move_down()
        
        # 添加动画帧（简化版本）
        frames.append({
            'grid': original_grid,
            'score': self.score,
            'moves': self.moves
        })
        
        frames.append({
            'grid': [row[:] for row in self.grid],
            'score': self.score,
            'moves': self.moves
        })
        
        return frames
    
    def update_score(self) -> None:
        """更新分数为网格内所有数字的总和"""
        self.score = self.calculate_total_score()
        if self.score > self.high_score:
            self.high_score = self.score

    def __str__(self) -> str:
        """字符串表示"""
        lines = []
        for row in self.grid:
            line = ' '.join(f'{num:4d}' if num != 0 else '   .' for num in row)
            lines.append(line)
        return '\n'.join(lines)