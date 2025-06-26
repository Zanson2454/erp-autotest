"""
断言工具模块

提供了一系列用于API响应和数据处理断言的辅助方法。
主要用于测试用例中的结果验证。
"""

import os
import sys
from pathlib import  Path
from typing import Dict, Any, List, Optional, Union


# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))



from utils.log_util import Loggers
from utils.response_util import ResponseUtil

logger = Loggers()
logger
class AssertHelper:
    """断言辅助类，提供通用的断言方法"""

    @staticmethod
    def assert_response_success(response: Dict[str, Any], message: str = None) -> None:
        """
        断言响应成功
        
        Args:
            response: 响应数据字典
            message: 自定义错误消息
        """
        success = response.get("success", False)
        if not success:
            error_msg = message or "响应未成功"
            # 添加response原始报文到错误信息中
            logger.error(f"断言失败 - {error_msg}，原始响应: {response}")
            raise AssertionError(f"{error_msg}，原始响应: {response}")
        else:
            logger.info(f"响应成功断言通过: success={success}")

    @staticmethod
    def assert_response_data(response: Dict[str, Any], message: str = None) -> Any:
        """
        断言响应成功
        支持处理Response对象和字典类型的响应数据
        """
        # 1. 首先验证响应成功
        AssertHelper.assert_response_success(response)
        # 2. 使用 ResponseUtil 提取数据
        result = ResponseUtil.get_response_data(response)
        
        # 3. 验证结果不为 None
        assert result is not None, message or "未找到有效的响应数据"
        
        return result


    @staticmethod
    def assert_response_time(response: Union[Dict[str, Any], Any], max_time: int = 1000, unit: str = 'ms'):
        """
        验证接口响应时间
        支持处理Response对象和字典类型的响应数据
        
        Args:
            response: 响应对象或响应数据
            max_time: 最大允许时间
            unit: 时间单位，支持 's'(秒) 或 'ms'(毫秒)
        """
        if hasattr(response, 'elapsed'):
            elapsed = response.elapsed.total_seconds()
            # 如果单位是毫秒，进行转换
            if unit.lower() == 'ms':
                elapsed = elapsed * 1000
                max_time = max_time * 1000
                
            assert elapsed <= max_time, f"响应时间 {elapsed:.2f}{unit} 超过阈值 {max_time:.2f}{unit}"
            logger.info(f"接口响应时间：{elapsed:.2f}{unit}")
        else:
            logger.warning("响应对象中没有elapsed属性，无法验证响应时间")

    @staticmethod
    def assert_all_in(expected_list: List[Any], actual_list: List[Any], message: str = None) -> None:
        """
        断言所有期望的值都在实际列表中存在
        
        Args:
            expected_list: 期望值列表
            actual_list: 实际值列表
            message: 自定义错误消息
        """
        missing = [item for item in expected_list if item not in actual_list]
        if message is None:
            message = f"以下期望值在实际列表中未找到: {missing}"
        assert not missing, message

    @staticmethod
    def assert_by_operator(actual: Any, operator: str, expected: Any = None) -> None:
        """
        通用运算符断言
        :param actual: 实际值
        :param operator: 运算符（=, !=, in, not_in, contain, empty, not_empty）
        :param expected: 期望值（部分运算符可为 None）
        :return: None，断言失败抛出 AssertionError
        """
        result = False
        log = {
            "expect_value": expected,
            "actual_value": actual,
            "assert_symbol": operator
        }
        try:
            if operator == "=":
                result = actual == expected
            elif operator == ">":
                result = actual > expected
            elif operator == ">=":
                result = actual >= expected
            elif operator == "<":
                result = actual < expected
            elif operator == "<=":
                result = actual <= expected
            elif operator == "!=":
                result = actual != expected
            elif operator == "in":
                result = actual in expected
            elif operator == "not_in":
                result = actual not in expected
            elif operator == "contain":
                result = expected in actual
            elif operator == "empty":
                result = not actual or (hasattr(actual, '__len__') and len(actual) == 0)
            elif operator == "not_empty":
                result = actual is not None and (not hasattr(actual, '__len__') or len(actual) > 0)
            else:
                raise ValueError(f"不支持的断言运算符: {operator}")
        except Exception as e:
            log["assert_result"] = "fail"
            logger.error(f"断言异常: {e}, 日志: {log}")
            raise AssertionError(f"断言异常: {e}, 日志: {log}")
        if result:
            log["assert_result"] = "success"
            logger.info(f"断言通过: {log}")
        else:
            log["assert_result"] = "fail"
            logger.error(f"断言失败: {log}")
            raise AssertionError(f"断言失败: {log}")

if __name__ == "__main__":
    assert_helper = AssertHelper()
    assert_helper.assert_response_success({"success": True}) # 断言响应成功
    assert_helper.assert_response_time({"elapsed": 1000}) # 断言响应时间
    assert_helper.assert_all_in([1, 2, 3], [1, 2, 3]) # 断言所有期望的值都在实际列表中存在
    assert_helper.assert_by_operator(1, "=", 1) # 断言相等
    assert_helper.assert_by_operator(1, "!=", 2) # 断言不相等
    assert_helper.assert_by_operator(1, "in", [1, 2, 3]) # 断言包含
    assert_helper.assert_by_operator(1, "not_in", [4, 5, 6]) # 断言不包含
    assert_helper.assert_by_operator([], "empty", []) # 断言为空
    assert_helper.assert_by_operator(1, "not_empty", [1]) # 断言不为空含
    # assert_helper.assert_response_time({"elapsed": 1000})