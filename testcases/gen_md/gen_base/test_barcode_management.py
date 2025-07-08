import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("条码系统管理")
class TestBarcodeSystemManagement(GenMdBaseTest):
    """条码系统管理测试类 - 整合条码规则、条码字段等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.barcode_id = None
        cls.barcode_code = None
        cls.barcode_rule_id = None
        cls.barcode_rule_code = None
        cls.logger.info("条码系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_barcode_md", "gen_barcode_rule_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 条码字段管理 ================
    @case_decorator(
        story="条码字段管理",
        title="测试新增条码字段",
        description="验证新增条码字段功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["条码字段管理", "新增"]
    )
    def test_save_barcode(self):
        """新增条码字段用例"""
        try:
            barcode_code = self.mock_data.generate_unique_code(tag="Barcode")
            barcode_name = f"条码字段_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-条码字段-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["barcode_code", "barcode_name"], ["params", "request"]
            )
            set_dict = {"barcode_code": barcode_code, "barcode_name": barcode_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.barcode_id = response.get("data", {}).get("data", {})
            self.barcode_code = barcode_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码字段管理",
        title="测试查询条码字段列表",
        description="验证条码字段列表查询功能",
        severity="normal",
        order=2,
        tags=["条码字段管理", "查询"]
    )
    def test_query_barcode_list(self):
        """查询条码字段列表用例"""
        try:
            api_path = self.get_api_path("GEN-条码字段-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "barcode_code", "type": "TEXT"},
                    {"name": "barcode_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码字段管理",
        title="测试查询条码字段详情",
        description="验证条码字段详情查询功能",
        severity="normal",
        order=3,
        tags=["条码字段管理", "查询"]
    )
    def test_query_barcode_detail(self):
        """查询条码字段详情用例"""
        try:
            if not self.barcode_id:
                self.test_save_barcode()

            api_path = self.get_api_path("GEN-条码字段-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.barcode_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码规则管理 ================
    @case_decorator(
        story="条码规则管理",
        title="测试新增条码规则",
        description="验证新增条码规则功能",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["条码规则管理", "新增"]
    )
    def test_save_barcode_rule(self):
        """新增条码规则用例"""
        try:
            barcode_rule_code = self.mock_data.generate_unique_code(tag="BarcodeRule")
            barcode_rule_name = f"条码规则_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-条码规则-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["barcode_rule_code", "barcode_rule_name"], ["params", "request"]
            )
            set_dict = {"barcode_rule_code": barcode_rule_code, "barcode_rule_name": barcode_rule_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.barcode_rule_id = response.get("data", {}).get("data", {})
            self.barcode_rule_code = barcode_rule_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试查询条码规则列表",
        description="验证条码规则列表查询功能",
        severity="normal",
        order=5,
        tags=["条码规则管理", "查询"]
    )
    def test_query_barcode_rule_list(self):
        """查询条码规则列表用例"""
        try:
            api_path = self.get_api_path("GEN-条码规则-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "barcode_rule_code", "type": "TEXT"},
                    {"name": "barcode_rule_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试查询条码规则详情",
        description="验证条码规则详情查询功能",
        severity="normal",
        order=6,
        tags=["条码规则管理", "查询"]
    )
    def test_query_barcode_rule_detail(self):
        """查询条码规则详情用例"""
        try:
            if not self.barcode_rule_id:
                self.test_save_barcode_rule()

            api_path = self.get_api_path("GEN-条码规则-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.barcode_rule_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试删除条码规则",
        description="验证删除条码规则功能",
        severity="normal",
        order=7,
        tags=["条码规则管理", "删除"]
    )
    def test_delete_barcode_rule(self):
        """删除条码规则用例"""
        try:
            if not self.barcode_rule_id:
                self.test_save_barcode_rule()

            api_path = self.get_api_path("GEN-条码规则-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.barcode_rule_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 