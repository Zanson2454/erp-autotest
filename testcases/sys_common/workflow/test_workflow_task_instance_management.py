"""
审批流-流程任务实例管理测试用例
覆盖任务实例查询、统计等功能
"""
import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("审批流-流程任务实例管理")
class TestWorkflowTaskInstanceManagement(SysCommonBaseTest):
    """审批流-流程任务实例管理测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("审批流-流程任务实例管理测试类初始化完成")
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试统计待办数量",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_COUNT_GET功能 - 统计待办任务数量",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "workflow", "task_instance", "count"]
    )
    def test_task_instance_count_get(self):
        """测试统计待办数量 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_COUNT_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"params":{"appId":0,"teamId":0},"teamId":0}}
            # 由于参数结构复杂（嵌套的params），使用use_param_util=False直接构造参数
            set_dict = {
                "params": {
                    "appId": 0,
                    "teamId": 0
                },
                "teamId": 0
            }
            
            # 2. 使用标准化API调用
            # use_param_util=False 用于复杂参数结构，param_path=["params"] 确保参数在params层级
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-统计待办数量(/api/trantor/workflow/v2/task-instance/count#GET)",
                set_dict=set_dict,
                use_param_util=False,  # 复杂参数，直接使用set_dict
                param_path=["params"]  # 参数路径设置为["params"]，确保set_dict放在params层级
            )
            
            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            data = response.get("data", {}).get("data", {})
            # 验证返回的是数字类型（待办数量）
            self.assert_util.assert_by_operator(
                isinstance(data, (int, dict)), 
                "=", True, 
                "返回数据应为数字或包含数字的字典"
            )
            
            self.logger.info(f"统计待办数量成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询待办列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询待办任务列表",
        severity="normal",
        file_level_order=2,
        tags=["sys_common", "workflow", "task_instance", "search"]
    )
    def test_task_instance_search_get(self):
        """测试查询待办列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"appId":0,"logType":2,"teamId":0,"status":0,"pageNo":1,"pageSize":20}}
            set_dict = {
                "appId": 0,
                "logType": 2,
                "teamId": 0,
                "status": 0,
                "pageNo": 1,
                "pageSize": 20
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询待办列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询已处理列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询已处理的审批任务列表",
        severity="normal",
        file_level_order=3,
        tags=["sys_common", "workflow", "task_instance", "search", "processed"]
    )
    def test_task_instance_search_processed_get(self):
        """测试查询已处理列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，已处理任务的参数结构为: {"params":{"logType":2,"tabKey":"1,-1,-2","pageNo":"1","pageSize":"20","statusListStr":"1,-1,-2"}}
            # 已处理任务使用 statusListStr 参数，而不是 status 参数
            # statusListStr: "1,-1,-2" 表示已处理任务的状态列表（1:已通过, -1:已拒绝, -2:已撤回等）
            set_dict = {
                "logType": 2,
                "tabKey": "1,-1,-2",
                "pageNo": "1",
                "pageSize": "20",
                "statusListStr": "1,-1,-2"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询已处理列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询待处理列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询待处理的审批任务列表",
        severity="normal",
        file_level_order=4,
        tags=["sys_common", "workflow", "task_instance", "search", "pending"]
    )
    def test_task_instance_search_pending_get(self):
        """测试查询待处理列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，待处理任务的参数结构为: {"params":{"logType":2,"tabKey":"0","pageNo":"1","pageSize":"20","status":"0"}}
            # 待处理任务使用 status: "0" 参数（字符串类型），tabKey: "0" 表示待处理标签
            # 注意：与 test_task_instance_search_get 的区别是参数类型（字符串 vs 数字）和参数结构（没有 appId 和 teamId）
            set_dict = {
                "logType": 2,
                "tabKey": "0",
                "pageNo": "1",
                "pageSize": "20",
                "status": "0"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询待处理列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询我发起的未完成任务列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询我发起的未完成的审批任务列表",
        severity="normal",
        file_level_order=5,
        tags=["sys_common", "workflow", "task_instance", "search", "my_initiated", "incomplete"]
    )
    def test_task_instance_search_my_initiated_incomplete_get(self):
        """测试查询我发起的未完成任务列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，我发起的未完成任务的参数结构为: {"params":{"logType":1,"tabKey":"0","pageNo":"1","pageSize":"20","statusListStr":"1,-1,-2"}}
            # logType: 1 表示我发起的任务（区别于 logType: 2 表示待办任务）
            # tabKey: "0" 表示未完成标签
            # statusListStr: "1,-1,-2" 表示任务状态列表（1:已通过, -1:已拒绝, -2:已撤回等）
            set_dict = {
                "logType": 1,
                "tabKey": "0",
                "pageNo": "1",
                "pageSize": "20",
                "statusListStr": "1,-1,-2"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询我发起的未完成任务列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询我发起的已完成任务列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询我发起的已完成的审批任务列表",
        severity="normal",
        file_level_order=6,
        tags=["sys_common", "workflow", "task_instance", "search", "my_initiated", "completed"]
    )
    def test_task_instance_search_my_initiated_completed_get(self):
        """测试查询我发起的已完成任务列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，我发起的已完成任务的参数结构为: {"params":{"logType":1,"tabKey":"0","pageNo":"1","pageSize":"20","statusListStr":"1,-1,-2"}}
            # logType: 1 表示我发起的任务（区别于 logType: 2 表示待办任务）
            # tabKey: "0" 表示已完成标签（注意：URL中的tabKey是"1,-1,-2"，但请求体中为"0"）
            # statusListStr: "1,-1,-2" 表示已完成任务的状态列表（1:已通过, -1:已拒绝, -2:已撤回等）
            # 注意：与 test_task_instance_search_my_initiated_incomplete_get 的区别在于业务含义（已完成 vs 未完成）
            set_dict = {
                "logType": 1,
                "tabKey": "0",
                "pageNo": "1",
                "pageSize": "20",
                "statusListStr": "1,-1,-2"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询我发起的已完成任务列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="审批流-流程任务实例",
        title="测试查询抄送我的任务列表",
        description="验证API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET功能 - 查询抄送我的审批任务列表",
        severity="normal",
        file_level_order=7,
        tags=["sys_common", "workflow", "task_instance", "search", "cc_to_me"]
    )
    def test_task_instance_search_cc_to_me_get(self):
        """测试查询抄送我的任务列表 - API_TRANTOR_WORKFLOW_V2_TASK_INSTANCE_SEARCH_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，抄送我的任务的参数结构为: {"params":{"logType":3,"tabKey":"1,-1,-2","pageNo":"1","pageSize":"20"}}
            # logType: 3 表示抄送我的任务（区别于 logType: 1 表示我发起的任务，logType: 2 表示待办任务）
            # tabKey: "1,-1,-2" 表示已完成标签（1:已通过, -1:已拒绝, -2:已撤回等）
            # 注意：此接口没有 statusListStr 参数，只使用 tabKey 来过滤状态
            set_dict = {
                "logType": 3,
                "tabKey": "1,-1,-2",
                "pageNo": "1",
                "pageSize": "20"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表(/api/trantor/workflow/v2/task-instance/search#GET)",
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
            
            self.logger.info(f"查询抄送我的任务列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
