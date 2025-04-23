import time
from typing import Dict, Any
from loguru import logger
import psutil
import threading

class PerformanceTest:
    """性能测试支持类，用于收集性能指标"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self._timers: Dict[str, float] = {}
        self._resource_monitor = None
        self._stop_monitor = False
    
    def start_timer(self, key: str):
        """开始计时
        
        Args:
            key: 计时器键名
        """
        self._timers[key] = time.time()
    
    def stop_timer(self, key: str) -> float:
        """结束计时
        
        Args:
            key: 计时器键名
            
        Returns:
            耗时（秒）
        """
        if key not in self._timers:
            logger.warning(f"计时器不存在: {key}")
            return 0
            
        duration = time.time() - self._timers[key]
        self.metrics[f"{key}_duration"] = duration
        return duration
    
    def start_resource_monitor(self, interval: float = 1.0):
        """开始资源监控
        
        Args:
            interval: 监控间隔（秒）
        """
        self._stop_monitor = False
        self._resource_monitor = threading.Thread(
            target=self._monitor_resources,
            args=(interval,)
        )
        self._resource_monitor.start()
    
    def stop_resource_monitor(self):
        """停止资源监控"""
        self._stop_monitor = True
        if self._resource_monitor:
            self._resource_monitor.join()
    
    def _monitor_resources(self, interval: float):
        """监控系统资源使用情况
        
        Args:
            interval: 监控间隔（秒）
        """
        while not self._stop_monitor:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            self.metrics["cpu_percent"] = cpu_percent
            self.metrics["memory_percent"] = memory.percent
            time.sleep(interval)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标
        
        Returns:
            性能指标字典
        """
        return self.metrics.copy() 