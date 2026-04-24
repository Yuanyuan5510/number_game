#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志文件路径测试脚本
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import LOG_DIR, LOG_FILE


def test_log_path():
    """测试日志文件路径"""
    print("测试日志文件路径...")
    print(f"日志目录: {LOG_DIR}")
    print(f"日志文件: {LOG_FILE}")
    
    # 检查日志目录是否存在
    if os.path.exists(LOG_DIR):
        print("日志目录已存在")
    else:
        print("日志目录不存在，将创建")
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            print("日志目录创建成功")
        except Exception as e:
            print(f"创建日志目录失败: {e}")
            return False
    
    # 检查日志文件是否可写
    try:
        with open(LOG_FILE, 'a') as f:
            f.write("测试日志写入\n")
        print("日志文件写入成功")
        return True
    except Exception as e:
        print(f"日志文件写入失败: {e}")
        return False


if __name__ == "__main__":
    print("开始日志文件路径测试...")
    success = test_log_path()
    if success:
        print("\n日志文件路径测试通过！")
    else:
        print("\n日志文件路径测试失败！")
