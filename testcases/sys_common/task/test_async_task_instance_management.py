"""
异步任务-任务实例管理测试用例
覆盖任务实例查询等功能
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("异步任务-任务实例管理")
class TestAsyncTaskInstanceManagement(SysCommonBaseTest):
    """异步任务-任务实例管理测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("异步任务-任务实例管理测试类初始化完成")
    
    @case_decorator(
        story="异步任务-任务实例",
        title="测试查询今日任务状态",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_LATEST_GET功能 - 查询今日任务状态",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "async_task", "task_instance", "latest"]
    )
    def test_task_instance_latest_get(self):
        """测试查询今日任务状态 - API_ASYNC_TASK_TASK_INSTANCE_LATEST_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"appId":0,"teamId":0}}
            set_dict = {
                "appId": 0,
                "teamId": 0
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="异步任务-任务实例-查询今日任务状态(/api/async-task/task-instance/latest#GET)",
                set_dict=set_dict,
                param_path=["params"]  # 参数路径设置为["params"]，确保set_dict直接放在params层级
            )
            
            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            data = response.get("data", {}).get("data", {})
            # 验证返回数据不为空
            self.assert_util.assert_by_operator(
                data is not None,
                "=",
                True,
                "返回数据不应为空"
            )
            
            self.logger.info(f"查询今日任务状态成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务-任务实例",
        title="测试查询今日任务列表",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_TODAY_LIST_GET功能 - 查询今日任务列表",
        severity="normal",
        file_level_order=2,
        tags=["sys_common", "async_task", "task_instance", "today_list"]
    )
    def test_task_instance_today_list_get(self):
        """测试查询今日任务列表 - API_ASYNC_TASK_TASK_INSTANCE_TODAY_LIST_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"appId":0,"teamId":0}}
            set_dict = {
                "appId": 0,
                "teamId": 0
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="异步任务-任务实例-查询今日任务列表(/api/async-task/task-instance/today-list#GET)",
                set_dict=set_dict,
                param_path=["params"]  # 参数路径设置为["params"]，确保set_dict直接放在params层级
            )
            
            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            data = response.get("data", {}).get("data", {})
            # 验证返回数据不为空
            self.assert_util.assert_by_operator(
                data is not None,
                "=",
                True,
                "返回数据不应为空"
            )
            
            self.logger.info(f"查询今日任务列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="异步任务-任务实例",
        title="测试查询任务数量",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_COUNT_GET功能 - 查询异步任务数量",
        severity="normal",
        file_level_order=3,
        tags=["sys_common", "async_task", "task_instance", "count"]
    )
    @pytest.mark.skip(reason="接口配置缺失，暂时跳过")
    def test_task_instance_count_get(self):
        """测试查询任务数量 - API_ASYNC_TASK_TASK_INSTANCE_COUNT_GET"""
        try:
            response, _ = self.standard_api_call(
                api_key="异步任务-任务实例-查询任务数量(/api/async-task/task-instance/count#GET)",
                set_dict={},
                use_param_util=False,
                param_path=[]
            )
            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                data is not None,
                "=",
                True,
                "任务数量返回数据不应为空"
            )
            a.json(response, "任务数量响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
