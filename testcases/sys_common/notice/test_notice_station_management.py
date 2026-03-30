import allure
from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("站内信管理")
class TestNoticeStationManagement(SysCommonBaseTest):
    """站内信管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        super().bind_context()
        cls.logger.info("站内信管理测试类初始化完成")

    @case_decorator(
        story="站内信管理",
        title="测试未读站内信分页查询",
        description="验证站内信APP服务-分页查询站内信接口",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "notice", "station", "paging"]
    )
    def test_query_unread_notice_station_page(self):
        """测试未读站内信分页查询"""
        try:
            set_dict = {
                "readStatus": "UNREAD",
                "pageSize": 10,
                "pageNo": 1
            }
            response, _ = self.standard_api_call(
                api_key="站内信APP服务-分页查询站内信(/api/notice/station/paging#POST)",
                set_dict=set_dict,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            page_data = data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(
                isinstance(page_data, list),
                "=",
                True,
                "站内信分页结果应为列表"
            )
            a.json(response, "站内信分页查询响应")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
