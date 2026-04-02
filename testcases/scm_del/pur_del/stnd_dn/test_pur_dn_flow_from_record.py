import allure
import pytest

from testcases.scm_del import ScmDelBaseTest
from utils.report_util import a, case_decorator


@allure.epic("交货管理")
@allure.feature("采购交货录制流")
class TestPurDnFlowFromRecord(ScmDelBaseTest):
    """基于 recorded_flow_003 的采购交货查询用例。"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
        cls.dn_head_id = None

    @classmethod
    def bind_context(cls):
        super().bind_context()
        cls.logger.info("采购交货录制流测试类初始化完成")

    def _query_pur_dn_page(self):
        response, _ = self.standard_api_call(
            api_key="DEL-交货单公共-数据分页查询服务",
            set_dict={
                "btClass": "PUR",
                "pageable": {"pageNo": 1, "pageSize": 20, "sortOrders": None, "conditionGroup": None},
            },
            fields_to_filter=["btClass", "pageable"],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_DEL"},
        )
        self.assert_util.assert_response_data(response)
        return response

    def _ensure_dn_head_id(self):
        if self.__class__.dn_head_id:
            return self.__class__.dn_head_id
        response = self._query_pur_dn_page()
        rows = response.get("data", {}).get("data", {}).get("data", []) or []
        if rows:
            self.__class__.dn_head_id = rows[0].get("id")
        return self.__class__.dn_head_id

    @case_decorator(
        story="采购交货单",
        title="测试采购交货单分页查询",
        description="验证 DEL-交货单公共-数据分页查询服务",
        severity="normal",
        file_level_order=4,
        tags=["scm_del", "pur_dn", "paging", "recorded_flow_003"],
    )
    def test_query_pur_dn_page_from_record(self):
        try:
            response = self._query_pur_dn_page()
            rows = response.get("data", {}).get("data", {}).get("data", []) or []
            self.assert_util.assert_by_operator(isinstance(rows, list), "=", True, "分页结果应为列表")
            if rows:
                self.__class__.dn_head_id = rows[0].get("id")
            a.json(response, "采购交货单分页查询响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购交货单",
        title="测试采购交货单按项目行分组查询",
        description="验证 DN-采购-项目行分组服务",
        severity="normal",
        file_level_order=5,
        tags=["scm_del", "pur_dn", "group", "recorded_flow_003"],
    )
    def test_group_pur_dn_items_from_record(self):
        try:
            dn_head_id = self._ensure_dn_head_id()
            if not dn_head_id:
                pytest.skip("未查询到可用采购交货单，跳过项目行分组查询")

            response, _ = self.standard_api_call(
                api_key="DN-采购-项目行分组服务",
                set_dict=[{"id": dn_head_id}],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_DEL"},
                use_param_util=False,
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "采购交货单项目行分组响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
