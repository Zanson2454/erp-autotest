import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import gevent

class LocustTestUser(HttpUser):
    """Locust测试用户基类"""
    wait_time = between(1, 3)  # 默认等待时间1-3秒
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data = {}
        self.base_test = None

    def on_start(self):
        """用户启动时执行"""
        pass

    def on_stop(self):
        """用户停止时执行"""
        pass

class LocustRunner:
    """Locust运行器"""
    def __init__(self, user_class: type, host: str, base_test=None):
        """初始化Locust运行器
        
        Args:
            user_class: Locust用户类
            host: 目标服务器地址
            base_test: 基础测试类实例
        """
        self.user_class = user_class
        self.host = host
        self.base_test = base_test
        self.env = Environment(user_classes=[user_class])
        self.env.create_local_runner()
        self.stats = self.env.stats

    def run_test(self, 
                num_users: int = 10, 
                spawn_rate: int = 1, 
                run_time: Optional[str] = None) -> Dict[str, Any]:
        """运行测试
        
        Args:
            num_users: 并发用户数
            spawn_rate: 每秒增加的用户数
            run_time: 运行时间，例如 "1m", "1h"
            
        Returns:
            Dict: 测试结果统计
        """
        # 启动统计打印
        gevent.spawn(stats_printer(self.stats))
        
        # 启动测试
        self.env.runner.start(num_users, spawn_rate=spawn_rate)
        
        # 设置运行时间
        if run_time:
            gevent.spawn_later(self._parse_time(run_time), lambda: self.env.runner.quit())
        
        # 等待测试完成
        self.env.runner.greenlet.join()
        
        # 收集测试结果
        return self._collect_results()

    def _parse_time(self, time_str: str) -> int:
        """解析时间字符串为秒数
        
        Args:
            time_str: 时间字符串，如 "1m", "1h"
            
        Returns:
            int: 秒数
        """
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        else:
            return value

    def _collect_results(self) -> Dict[str, Any]:
        """收集测试结果
        
        Returns:
            Dict: 测试结果统计
        """
        return {
            "total_requests": self.stats.total.num_requests,
            "failed_requests": self.stats.total.num_failures,
            "total_response_time": self.stats.total.avg_response_time,
            "requests_per_second": self.stats.total.current_rps,
            "user_count": self.env.runner.user_count
        }

def run_performance_test(test_class: type, base_test, num_users: int = 10, spawn_rate: int = 1, run_time: str = "1m") -> Dict[str, Any]:
    """运行性能测试
    
    Args:
        test_class: 测试类，需要继承自LocustTestUser并实现具体的测试任务
        base_test: 基础测试类实例
        num_users: 并发用户数
        spawn_rate: 每秒增加的用户数
        run_time: 运行时间
        
    Returns:
        Dict: 测试结果
    """
    runner = LocustRunner(test_class, base_test.base_url, base_test)
    return runner.run_test(num_users, spawn_rate, run_time)

# 使用示例：
"""
from testcases.comm.base_test import BaseTest
from utils.LocustUtil import LocustTestUser, run_performance_test

# 定义测试类
class MemberTestUser(LocustTestUser):
    def on_start(self):
        self.base_test = base_test  # 设置基础测试实例
        
    @task
    def create_member(self):
        # 复用已有的测试用例代码
        test_case = TestMemberCreate()
        test_case.test_create_member()

# 初始化基础测试类
base_test = BaseTest()
base_test.setup_class()

# 运行性能测试
result = run_performance_test(
    test_class=MemberTestUser,
    base_test=base_test,
    num_users=10,      # 10个并发用户
    spawn_rate=1,      # 每秒增加1个用户
    run_time="1m"      # 运行1分钟
)

print(f"测试结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
""" 