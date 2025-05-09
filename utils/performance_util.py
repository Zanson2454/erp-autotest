import time
import functools
from typing import Callable, Any, Optional
from loguru import logger
import psutil
import threading
import allure


def measure_time(
    name: Optional[str] = None,
    log_level: str = "DEBUG",
    allure_step: bool = True
) -> Callable:
    """测量函数执行时间的装饰器
    
    Args:
        name: 计时器名称，默认使用函数名
        log_level: 日志级别，可选 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        allure_step: 是否在 Allure 报告中记录步骤
        
    Returns:
        Callable: 装饰器函数
        
    使用示例：
    ```python
    @measure_time(name="创建订单", log_level="INFO")
    def create_order():
        # 创建订单的代码
        pass
    ```
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            timer_name = name or func.__name__
            start_time = time.time()
            
            # 记录开始时间
            logger.log(log_level.upper(), f"开始执行 {timer_name}")
            
            try:
                # 使用 Allure 步骤记录
                if allure_step:
                    with allure.step(f"执行 {timer_name}"):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                    
                # 计算执行时间
                duration = time.time() - start_time
                
                # 记录执行时间
                logger.log(
                    log_level.upper(),
                    f"完成执行 {timer_name}, 耗时: {duration:.3f}秒"
                )
                
                # 添加到 Allure 报告
                if allure_step:
                    allure.attach(
                        f"执行时间: {duration:.3f}秒",
                        name=f"{timer_name} 执行时间",
                        attachment_type=allure.attachment_type.TEXT
                    )
                
                return result
                
            except Exception as e:
                # 记录异常情况下的执行时间
                duration = time.time() - start_time
                logger.error(
                    f"{timer_name} 执行失败, 耗时: {duration:.3f}秒, 错误: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator


class PerformanceMetrics:
    """性能指标收集器
    
    用于收集和记录测试用例的性能指标。
    支持与 Allure 报告集成。
    
    使用示例：
    ```python
    metrics = PerformanceMetrics()
    
    @metrics.measure
    def test_case():
        # 测试用例代码
        pass
    ```
    """
    
    def __init__(self):
        self.metrics: dict[str, float] = {}
    
    def measure(self, name: Optional[str] = None) -> Callable:
        """测量函数执行时间的装饰器
        
        Args:
            name: 计时器名称，默认使用函数名
            
        Returns:
            Callable: 装饰器函数
        """
        return measure_time(name=name)
    
    def get_metrics(self) -> dict[str, float]:
        """获取性能指标
        
        Returns:
            dict[str, float]: 性能指标字典
        """
        return self.metrics.copy()


class PerformanceTest:
    """性能测试支持类，用于收集性能指标"""
    
    def __init__(self):
        self.metrics: dict[str, float] = {}
        self._timers: dict[str, float] = {}
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
    
    def get_metrics(self) -> dict[str, float]:
        """获取性能指标
        
        Returns:
            dict[str, float]: 性能指标字典
        """
        return self.metrics.copy() 