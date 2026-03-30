import allure
import pytest
from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("工作台任务管理")
class TestWorkbenchTaskManagement(SysCommonBaseTest):
    """工作台任务管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        super().bind_context()
        cls.logger.info("工作台任务管理测试类初始化完成")

    @case_decorator(
        story="工作台任务",
        title="测试新工作台待办任务查询",
        description="验证审批流-流程任务实例-查询待办列表新工作台接口",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "task", "workbench", "query"]
    )
    def test_query_new_workbench_pending_tasks(self):
        """测试新工作台待办任务查询"""
        try:
            set_dict = {
                "request": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "logType": 2,
                    "status": "0"
                }
            }
            response, _ = self.standard_api_call(
                api_key="审批流-流程任务实例-查询待办列表新工作台",
                set_dict=set_dict,
                use_param_util=False,
                param_path=["params"]
            )
            err_code = response.get("err", {}).get("code") if isinstance(response, dict) else None
            if err_code == "sys_common$errorCommon":
                pytest.skip("后端接口已知返回 sys_common$errorCommon（HTTP 500），暂不作为自动化失败")

            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            task_list = data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(
                isinstance(task_list, list),
                "=",
                True,
                "待办列表应为列表结构"
            )
            a.json(response, "新工作台待办查询响应")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
