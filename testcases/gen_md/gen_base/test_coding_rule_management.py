import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("编码规则管理")
class TestCodingRuleManagement(GenMdBaseTest):
    """编码规则管理测试类 - 整合取号规则、动态表单等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.number_rule_id = None
        cls.number_rule_code = None
        cls.dynamic_form_id = None
        cls.dynamic_form_code = None
        cls.logger.info("编码规则管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_number_rule_md", "gen_dynamic_form_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 取号规则管理 ================
    @case_decorator(
        story="取号规则管理",
        title="测试新增取号规则",
        description="验证新增取号规则功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["取号规则管理", "新增"]
    )
    def test_save_number_rule(self):
        """新增取号规则用例"""
        try:
            number_rule_code = self.mock_data.generate_unique_code(tag="NumberRule")
            number_rule_name = f"取号规则_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-编码规则-新增规则服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["number_rule_code", "number_rule_name"], ["params", "request"]
            )
            set_dict = {"number_rule_code": number_rule_code, "number_rule_name": number_rule_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.number_rule_id = response.get("data", {}).get("data", {})
            self.number_rule_code = number_rule_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="取号规则管理",
        title="测试查询取号规则列表",
        description="验证取号规则列表查询功能",
        severity="normal",
        order=2,
        tags=["取号规则管理", "查询"]
    )
    def test_query_number_rule_list(self):
        """查询取号规则列表用例"""
        try:
            api_path = self.get_api_path("GEN-编码规则-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "number_rule_code", "type": "TEXT"},
                    {"name": "number_rule_name", "type": "TEXT"}
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
        story="取号规则管理",
        title="测试查询取号规则详情",
        description="验证取号规则详情查询功能",
        severity="normal",
        order=3,
        tags=["取号规则管理", "查询"]
    )
    def test_query_number_rule_detail(self):
        """查询取号规则详情用例"""
        try:
            if not self.number_rule_id:
                self.test_save_number_rule()

            api_path = self.get_api_path("GEN-编码规则-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.number_rule_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="取号规则管理",
        title="测试修改取号规则",
        description="验证修改取号规则功能",
        severity="normal",
        order=4,
        tags=["取号规则管理", "修改"]
    )
    def test_update_number_rule(self):
        """修改取号规则用例"""
        try:
            if not self.number_rule_id:
                self.test_save_number_rule()

            api_path = self.get_api_path("GEN-编码规则-编辑规则服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "number_rule_code", "number_rule_name"], ["params", "request"]
            )
            set_dict = {
                "id": self.number_rule_id,
                "number_rule_code": self.number_rule_code,
                "number_rule_name": f"修改_取号规则_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 动态表单管理 ================
    @case_decorator(
        story="动态表单管理",
        title="测试新增动态表单",
        description="验证新增动态表单功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["动态表单管理", "新增"]
    )
    def test_save_dynamic_form(self):
        """新增动态表单用例"""
        try:
            dynamic_form_code = self.mock_data.generate_unique_code(tag="DynamicForm")
            dynamic_form_name = f"动态表单_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-创建修改动态表单模板")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["dynamic_form_code", "dynamic_form_name"], ["params", "request"]
            )
            set_dict = {"dynamic_form_code": dynamic_form_code, "dynamic_form_name": dynamic_form_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.dynamic_form_id = response.get("data", {}).get("data", {})
            self.dynamic_form_code = dynamic_form_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试查询动态表单列表",
        description="验证动态表单列表查询功能",
        severity="normal",
        order=6,
        tags=["动态表单管理", "查询"]
    )
    def test_query_dynamic_form_list(self):
        """查询动态表单列表用例"""
        try:
            api_path = self.get_api_path("GEN-动态表单-查询模板列表服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "dynamic_form_code", "type": "TEXT"},
                    {"name": "dynamic_form_name", "type": "TEXT"}
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
        story="动态表单管理",
        title="测试修改动态表单",
        description="验证修改动态表单功能",
        severity="normal",
        order=7,
        tags=["动态表单管理", "修改"]
    )
    def test_update_dynamic_form(self):
        """修改动态表单用例"""
        try:
            if not self.dynamic_form_id:
                self.test_save_dynamic_form()

            api_path = self.get_api_path("GEN-创建修改动态表单模板")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "dynamic_form_code", "dynamic_form_name"], ["params", "request"]
            )
            set_dict = {
                "id": self.dynamic_form_id,
                "dynamic_form_code": self.dynamic_form_code,
                "dynamic_form_name": f"修改_动态表单_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试删除动态表单",
        description="验证删除动态表单功能",
        severity="normal",
        order=8,
        tags=["动态表单管理", "删除"]
    )
    def test_delete_dynamic_form(self):
        """删除动态表单用例"""
        try:
            if not self.dynamic_form_id:
                self.test_save_dynamic_form()

            api_path = self.get_api_path("GEN-动态表单-删除动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.dynamic_form_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 