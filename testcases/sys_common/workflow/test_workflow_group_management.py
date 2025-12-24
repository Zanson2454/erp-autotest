"""
审批流-审批流组管理测试用例
覆盖审批流组查询等功能
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
@allure.feature("审批流-审批流组管理")
class TestWorkflowGroupManagement(SysCommonBaseTest):
    """审批流-审批流组管理测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("审批流-审批流组管理测试类初始化完成")
    
    @case_decorator(
        story="审批流-审批流组管理",
        title="测试分页查询审批流组列表",
        description="验证API_TRANTOR_WORKFLOW_PORTAL_WORKFLOW_GROUP_PAGING_GET功能 - 分页查询审批流组列表",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "workflow", "workflow_group", "paging"]
    )
    def test_workflow_group_paging_get(self):
        """测试分页查询审批流组列表 - API_TRANTOR_WORKFLOW_PORTAL_WORKFLOW_GROUP_PAGING_GET"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"pageNo":"1","pageSize":"10"}}
            set_dict = {
                "pageNo": "1",
                "pageSize": "10"
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="审批流-审批流组管理-分页查询(/api/trantor/workflow/portal/workflow-group/paging#GET)",
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
            
            self.logger.info(f"分页查询审批流组列表成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

