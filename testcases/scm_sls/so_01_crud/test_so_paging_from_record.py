import allure
import pytest
from testcases.scm_sls import SlsBase
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单分页查询")
class TestSoPagingFromRecord(SlsBase):
    """基于录制流的销售订单分页查询用例"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        super().bind_context()
        cls.logger.info("销售订单分页查询测试类初始化完成")

    def _get_one_so_item_id(self):
        """通过销售订单行分页接口获取一个订单行ID。"""
        response, _ = self.standard_api_call(
            api_key="分页查询销售订单行",
            set_dict={"pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True}},
            fields_to_filter=["pageable"],
            param_path=["params"],
            query_params={"tmodule": "SCM_SLS"}
        )
        self.assert_util.assert_response_data(response)
        data = response.get("data", {}).get("data", {})
        records = data.get("records", []) or data.get("data", []) if isinstance(data, dict) else []
        if not records:
            return None
        return records[0].get("id")

    @case_decorator(
        story="销售报价单",
        title="测试销售报价单分页查询",
        description="验证 SLS-销售报价单-分页查询 接口",
        severity="normal",
        file_level_order=1,
        tags=["scm_sls", "quote", "paging"]
    )
    def test_query_so_quote_page(self):
        """测试销售报价单分页查询"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            response, _ = self.standard_api_call(
                api_key="SLS-销售报价单-分页查询",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                param_path=["params"],
                query_params={"tmodule": "SCM_SLS"}
            )
            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            records = data.get("records", []) or data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(
                isinstance(records, list),
                "=",
                True,
                "报价单分页结果应为列表"
            )
            a.json(response, "销售报价单分页响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="测试销售订单正逆向分页查询",
        description="验证 SLS-销售订单-正逆向分页服务 接口",
        severity="normal",
        file_level_order=2,
        tags=["scm_sls", "so", "paging"]
    )
    def test_query_so_head_page(self):
        """测试销售订单正逆向分页查询"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单-正逆向分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_SLS"}
            )
            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            records = data.get("records", []) or data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(
                isinstance(records, list),
                "=",
                True,
                "销售订单分页结果应为列表"
            )
            a.json(response, "销售订单正逆向分页响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单行",
        title="测试销售订单行分页查询",
        description="验证 分页查询销售订单行 接口",
        severity="normal",
        file_level_order=3,
        tags=["scm_sls", "so_item", "paging"]
    )
    def test_query_so_item_page(self):
        """测试销售订单行分页查询"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            response, _ = self.standard_api_call(
                api_key="分页查询销售订单行",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                param_path=["params"],
                query_params={"tmodule": "SCM_SLS"}
            )
            self.assert_util.assert_response_data(response)

            data = response.get("data", {}).get("data", {})
            records = data.get("records", []) or data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(
                isinstance(records, list),
                "=",
                True,
                "销售订单行分页结果应为列表"
            )
            a.json(response, "销售订单行分页响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单行",
        title="测试按ID查询销售订单行详情",
        description="验证 销售订单项目行表-根据ID查找数据服务 接口",
        severity="normal",
        file_level_order=4,
        tags=["scm_sls", "so_item", "detail", "by_id"]
    )
    def test_query_so_item_detail_by_id(self):
        """测试按ID查询销售订单行详情"""
        try:
            so_item_id = self._get_one_so_item_id()
            if not so_item_id:
                pytest.skip("未查询到可用于详情查询的销售订单行数据")

            response, _ = self.standard_api_call(
                api_key="销售订单项目行表-根据ID查找数据服务",
                set_dict={"id": so_item_id},
                fields_to_filter=["id"],
                param_path=["params", "request"]
            )
            self.assert_util.assert_response_data(response)
            detail = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                detail is not None,
                "=",
                True,
                "订单行详情不应为空"
            )
            a.json(response, "销售订单行详情响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
