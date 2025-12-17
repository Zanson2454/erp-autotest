"""
异步等待工具模块

提供通用的异步任务等待功能，支持轮询检查、超时控制、失败检测等。
主要用于测试异步任务执行状态，如异步过账、异步初始化等场景。
"""

import time
from typing import Callable, Dict, Any, Optional, Tuple
from enum import Enum
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.log_util import Loggers
from utils.report_util import a


class WaitStatus(Enum):
    """等待状态枚举"""
    SUCCESS = "success"  # 等待成功，条件满足
    TIMEOUT = "timeout"  # 等待超时
    FAILED = "failed"    # 任务失败
    ERROR = "error"      # 检查过程出错


class AsyncWaitResult:
    """异步等待结果数据类"""
    
    def __init__(self):
        self.status: WaitStatus = WaitStatus.TIMEOUT
        self.attempts: int = 0
        self.total_wait_time: float = 0.0
        self.last_data: Optional[Dict[str, Any]] = None
        self.error_message: Optional[str] = None
        self.polling_history: list = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "status": self.status.value,
            "attempts": self.attempts,
            "total_wait_time": round(self.total_wait_time, 2),
            "last_data": self.last_data,
            "error_message": self.error_message,
            "polling_history": self.polling_history
        }


class AsyncWaitUtil:
    """异步等待工具类"""
    
    @staticmethod
    def wait_for_condition(
        check_func: Callable[[], Tuple[bool, Optional[Dict[str, Any]], Optional[str]]],
        max_wait: int = 30,
        interval: float = 2.0,
        timeout_message: str = "等待超时",
        enable_polling_log: bool = True
    ) -> AsyncWaitResult:
        """
        等待条件满足（通用轮询方法）
        
        Args:
            check_func: 检查函数，返回 (是否满足条件, 当前数据, 错误信息)
                - 第一个返回值：True表示条件满足，False表示继续等待
                - 第二个返回值：当前查询到的数据（用于记录和最终返回）
                - 第三个返回值：如果任务失败，返回失败原因；否则返回None
            max_wait: 最大等待时间（秒），默认30秒
            interval: 轮询间隔（秒），默认2秒
            timeout_message: 超时提示信息
            enable_polling_log: 是否启用轮询日志，默认True
        
        Returns:
            AsyncWaitResult: 等待结果对象
        
        使用示例:
            ```python
            def check_status():
                # 查询状态
                response = self.http.post(url, json=params)
                data = response.get("data", {}).get("data", {})
                status = data.get("asyncExecutionStatus")
                
                # 判断条件
                if status == "SUCCEEDED":
                    return True, data, None  # 成功
                elif status == "FAILED":
                    return False, data, data.get("asyncExecutionFailureReason")  # 失败
                else:
                    return False, data, None  # 继续等待
            
            result = AsyncWaitUtil.wait_for_condition(
                check_func=check_status,
                max_wait=30,
                interval=2.0
            )
            
            if result.status == WaitStatus.SUCCESS:
                # 处理成功情况
                pass
            ```
        """
        result = AsyncWaitResult()
        start_time = time.time()
        waited = 0.0
        
        Loggers.info(f"开始异步等待，最大等待时间: {max_wait}秒，轮询间隔: {interval}秒")
        
        while waited < max_wait:
            try:
                # 调用检查函数
                condition_met, current_data, failure_reason = check_func()
                result.attempts += 1
                result.last_data = current_data
                
                # 记录轮询历史
                polling_info = {
                    "attempt": result.attempts,
                    "waited_time": round(waited, 2),
                    "data": current_data
                }
                result.polling_history.append(polling_info)
                
                if enable_polling_log:
                    Loggers.info(f"第{result.attempts}次检查 - 已等待: {round(waited, 2)}秒")
                    if current_data:
                        a.text(
                            f"第{result.attempts}次检查 - 已等待: {round(waited, 2)}秒\n"
                            f"当前数据: {current_data}",
                            "轮询检查"
                        )
                
                # 检查是否满足条件
                if condition_met:
                    result.status = WaitStatus.SUCCESS
                    result.total_wait_time = time.time() - start_time
                    Loggers.info(f"✅ 条件满足，等待成功！总耗时: {round(result.total_wait_time, 2)}秒，检查次数: {result.attempts}")
                    a.text(
                        f"✅ 等待成功！\n"
                        f"总耗时: {round(result.total_wait_time, 2)}秒\n"
                        f"检查次数: {result.attempts}次",
                        "等待结果"
                    )
                    break
                
                # 检查是否失败
                if failure_reason:
                    result.status = WaitStatus.FAILED
                    result.error_message = failure_reason
                    result.total_wait_time = time.time() - start_time
                    Loggers.error(f"❌ 任务失败: {failure_reason}")
                    a.text(
                        f"❌ 任务失败\n"
                        f"失败原因: {failure_reason}\n"
                        f"总耗时: {round(result.total_wait_time, 2)}秒\n"
                        f"检查次数: {result.attempts}次",
                        "等待结果"
                    )
                    break
                
                # 继续等待
                if waited + interval < max_wait:
                    time.sleep(interval)
                    waited += interval
                else:
                    # 最后一次检查后不再等待
                    break
                    
            except Exception as e:
                result.status = WaitStatus.ERROR
                result.error_message = str(e)
                result.total_wait_time = time.time() - start_time
                Loggers.error(f"检查过程出错: {str(e)}")
                a.text(f"检查过程出错: {str(e)}", "错误信息")
                break
        
        # 如果超时
        if result.status == WaitStatus.TIMEOUT:
            result.total_wait_time = time.time() - start_time
            result.error_message = timeout_message
            Loggers.warning(f"⏱️ 等待超时！总耗时: {round(result.total_wait_time, 2)}秒，检查次数: {result.attempts}")
            a.text(
                f"⏱️ 等待超时\n"
                f"总耗时: {round(result.total_wait_time, 2)}秒\n"
                f"检查次数: {result.attempts}次\n"
                f"最后数据: {result.last_data}",
                "等待结果"
            )
        
        # 记录最终结果
        a.json(result.to_dict(), "异步等待结果")
        
        return result
    
    @staticmethod
    def wait_for_async_status(
        query_func: Callable[[], Optional[Dict[str, Any]]],
        status_field: str = "asyncExecutionStatus",
        success_status: str = "SUCCEEDED",
        failed_status: str = "FAILED",
        failure_reason_field: str = "asyncExecutionFailureReason",
        max_wait: int = 30,
        interval: float = 2.0,
        additional_check: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> AsyncWaitResult:
        """
        等待异步任务状态（专用方法，简化异步状态检查）
        
        Args:
            query_func: 查询函数，返回包含状态的数据字典
            status_field: 状态字段名，默认 "asyncExecutionStatus"
            success_status: 成功状态值，默认 "SUCCEEDED"
            failed_status: 失败状态值，默认 "FAILED"
            failure_reason_field: 失败原因字段名，默认 "asyncExecutionFailureReason"
            max_wait: 最大等待时间（秒），默认30秒
            interval: 轮询间隔（秒），默认2秒
            additional_check: 额外的检查函数，接收数据字典，返回True表示满足额外条件
        
        Returns:
            AsyncWaitResult: 等待结果对象
        
        使用示例:
            ```python
            def query_init_status():
                response, _ = self.standard_api_call(
                    api_key="存货核算初始化配置-查询详情服务",
                    set_dict={"id": self.init_cf_id},
                    fields_to_filter=["id"]
                )
                return response.get("data", {}).get("data", {})
            
            result = AsyncWaitUtil.wait_for_async_status(
                query_func=query_init_status,
                success_status="SUCCEEDED",
                max_wait=60,
                interval=3.0
            )
            
            if result.status == WaitStatus.SUCCESS:
                self.assert_util.assert_by_operator(
                    result.last_data.get("asyncExecutionStatus"),
                    "=",
                    "SUCCEEDED"
                )
            ```
        """
        def check_status():
            """内部检查函数"""
            try:
                data = query_func()
                
                if not data:
                    return False, None, None
                
                current_status = data.get(status_field)
                
                # 检查是否成功
                if current_status == success_status:
                    # 如果有额外检查条件
                    if additional_check:
                        if additional_check(data):
                            return True, data, None
                        else:
                            return False, data, None
                    else:
                        return True, data, None
                
                # 检查是否失败
                if current_status == failed_status:
                    failure_reason = data.get(failure_reason_field, "未知原因")
                    return False, data, failure_reason
                
                # 继续等待
                return False, data, None
                
            except Exception as e:
                Loggers.error(f"查询状态出错: {str(e)}")
                return False, None, str(e)
        
        return AsyncWaitUtil.wait_for_condition(
            check_func=check_status,
            max_wait=max_wait,
            interval=interval,
            timeout_message=f"异步任务状态未在{max_wait}秒内变为{success_status}",
            enable_polling_log=True
        )


if __name__ == "__main__":
    # 测试示例
    def mock_check():
        """模拟检查函数"""
        import random
        status = random.choice(["CREATED", "PROCESSING", "SUCCEEDED", "FAILED"])
        data = {"status": status}
        
        if status == "SUCCEEDED":
            return True, data, None
        elif status == "FAILED":
            return False, data, "模拟失败原因"
        else:
            return False, data, None
    
    result = AsyncWaitUtil.wait_for_condition(
        check_func=mock_check,
        max_wait=10,
        interval=1.0
    )
    
    print(f"等待结果: {result.to_dict()}")

