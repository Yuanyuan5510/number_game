#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
测试服务器优化前后的性能对比
"""

import requests
import time
import threading
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
TEST_DURATION = 30  # 测试持续时间（秒）
CONCURRENT_USERS = 10  # 并发用户数

# 测试结果
results = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'total_response_time': 0,
    'response_times': []
}

# 测试锁
lock = threading.Lock()

class TestUser(threading.Thread):
    """测试用户线程"""
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.session = requests.Session()
    
    def run(self):
        start_time = time.time()
        while time.time() - start_time < TEST_DURATION:
            # 测试获取游戏状态
            self.test_get_game_state()
            # 测试创建新游戏
            self.test_new_game()
            # 测试移动操作
            self.test_move()
    
    def test_get_game_state(self):
        """测试获取游戏状态"""
        try:
            start = time.time()
            response = self.session.get(f"{BASE_URL}/api/game/state")
            end = time.time()
            response_time = end - start
            
            with lock:
                results['total_requests'] += 1
                if response.status_code == 200:
                    results['successful_requests'] += 1
                    results['total_response_time'] += response_time
                    results['response_times'].append(response_time)
                else:
                    results['failed_requests'] += 1
        except Exception as e:
            with lock:
                results['total_requests'] += 1
                results['failed_requests'] += 1
    
    def test_new_game(self):
        """测试创建新游戏"""
        try:
            start = time.time()
            response = self.session.post(f"{BASE_URL}/api/game/new", json={"size": 4})
            end = time.time()
            response_time = end - start
            
            with lock:
                results['total_requests'] += 1
                if response.status_code == 200:
                    results['successful_requests'] += 1
                    results['total_response_time'] += response_time
                    results['response_times'].append(response_time)
                else:
                    results['failed_requests'] += 1
        except Exception as e:
            with lock:
                results['total_requests'] += 1
                results['failed_requests'] += 1
    
    def test_move(self):
        """测试移动操作"""
        try:
            directions = ['left', 'right', 'up', 'down']
            for direction in directions:
                start = time.time()
                response = self.session.post(f"{BASE_URL}/api/game/move", json={"direction": direction})
                end = time.time()
                response_time = end - start
                
                with lock:
                    results['total_requests'] += 1
                    if response.status_code == 200:
                        results['successful_requests'] += 1
                        results['total_response_time'] += response_time
                        results['response_times'].append(response_time)
                    else:
                        results['failed_requests'] += 1
        except Exception as e:
            with lock:
                results['total_requests'] += 1
                results['failed_requests'] += 1

def run_performance_test():
    """运行性能测试"""
    print("开始性能测试...")
    print(f"测试配置: 并发用户数={CONCURRENT_USERS}, 测试持续时间={TEST_DURATION}秒")
    
    # 创建并启动测试用户线程
    threads = []
    for i in range(CONCURRENT_USERS):
        user = TestUser(i)
        threads.append(user)
        user.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 计算测试结果
    avg_response_time = 0
    if results['successful_requests'] > 0:
        avg_response_time = results['total_response_time'] / results['successful_requests']
    
    throughput = results['total_requests'] / TEST_DURATION
    success_rate = (results['successful_requests'] / results['total_requests']) * 100 if results['total_requests'] > 0 else 0
    
    # 输出测试结果
    print("\n性能测试结果:")
    print(f"总请求数: {results['total_requests']}")
    print(f"成功请求数: {results['successful_requests']}")
    print(f"失败请求数: {results['failed_requests']}")
    print(f"成功率: {success_rate:.2f}%")
    print(f"平均响应时间: {avg_response_time:.4f}秒")
    print(f"吞吐量: {throughput:.2f}请求/秒")
    
    # 获取服务器性能数据
    try:
        response = requests.get(f"{BASE_URL}/api/performance")
        if response.status_code == 200:
            performance_data = response.json()
            print("\n服务器性能数据:")
            print(f"服务器运行时间: {performance_data['uptime']:.2f}秒")
            print(f"内存使用: {performance_data['memory_usage']:.2f}MB")
            print(f"CPU使用率: {performance_data['cpu_usage']:.2f}%")
            print(f"活跃游戏数: {performance_data['active_games']}")
            print(f"活跃房间数: {performance_data['active_rooms']}")
    except Exception as e:
        print(f"获取服务器性能数据失败: {e}")

if __name__ == "__main__":
    run_performance_test()
