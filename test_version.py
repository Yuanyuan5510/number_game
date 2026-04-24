#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本验证逻辑测试脚本
"""

import sys
import os

# 添加当前目录到路径，以便导入main.py中的VersionChecker
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import VersionChecker


def test_version_comparison():
    """测试版本比较算法"""
    checker = VersionChecker("3.2.6")
    
    # 测试场景1: 本地版本低于远程版本
    result = checker._compare_versions("3.2.7", "3.2.6")
    print(f"测试场景1 (3.2.7 > 3.2.6): {result} (期望: 1)")
    assert result == 1, f"测试场景1失败，期望1，实际{result}"
    
    # 测试场景2: 本地版本高于远程版本
    result = checker._compare_versions("3.2.5", "3.2.6")
    print(f"测试场景2 (3.2.5 < 3.2.6): {result} (期望: -1)")
    assert result == -1, f"测试场景2失败，期望-1，实际{result}"
    
    # 测试场景3: 版本号相同
    result = checker._compare_versions("3.2.6", "3.2.6")
    print(f"测试场景3 (3.2.6 == 3.2.6): {result} (期望: 0)")
    assert result == 0, f"测试场景3失败，期望0，实际{result}"
    
    # 测试场景4: 版本号位数不同
    result = checker._compare_versions("3.2", "3.2.6")
    print(f"测试场景4 (3.2 < 3.2.6): {result} (期望: -1)")
    assert result == -1, f"测试场景4失败，期望-1，实际{result}"
    
    # 测试场景5: 版本号包含v前缀
    result = checker._compare_versions("v3.2.7", "3.2.6")
    print(f"测试场景5 (v3.2.7 > 3.2.6): {result} (期望: 1)")
    assert result == 1, f"测试场景5失败，期望1，实际{result}"
    
    # 测试场景6: 无效版本号
    result = checker._compare_versions("invalid", "3.2.6")
    print(f"测试场景6 (invalid < 3.2.6): {result} (期望: -1)")
    assert result == -1, f"测试场景6失败，期望-1，实际{result}"
    
    print("所有版本比较测试通过！")


def test_version_fetching():
    """测试版本获取功能"""
    checker = VersionChecker("3.2.6")
    
    # 测试获取远程版本
    print("\n测试获取远程版本...")
    try:
        # 测试国际版URL
        remote_version = checker._fetch_version(checker.international_url)
        print(f"国际版URL获取版本: {remote_version}")
        
        # 测试中国版URL
        remote_version_cn = checker._fetch_version(checker.china_url)
        print(f"中国版URL获取版本: {remote_version_cn}")
        
        print("版本获取测试完成！")
    except Exception as e:
        print(f"版本获取测试失败: {e}")


if __name__ == "__main__":
    print("开始版本验证逻辑测试...")
    test_version_comparison()
    test_version_fetching()
    print("\n所有测试完成！")
