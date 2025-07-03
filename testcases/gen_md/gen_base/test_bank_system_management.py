import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("银行系统管理")
class TestBankSystemManagement(GenMdBaseTest):
    """银行系统管理测试类 - 整合银行、银行支行等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.bank_id = None
        cls.bank_code = None
        cls.sub_bank_id = None
        cls.sub_bank_code = None
        cls.logger.info("银行系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_bank_md", "gen_sub_bank_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 银行管理 ================
    @case_decorator(
        story="银行管理",
        title="测试新增银行",
        description="验证新增银行功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["银行管理", "新增"]
    )
    def test_save_bank(self):
        """新增银行用例"""
        try:
            bank_code = self.mock_data.generate_unique_code(tag="Bank")
            bank_name = f"银行_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-银行-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["bank_code", "bank_name"], ["params", "request"]
            )
            set_dict = {"bank_code": bank_code, "bank_name": bank_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bank_id = response.get("data", {}).get("data", {})
            self.bank_code = bank_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试查询银行列表",
        description="验证银行列表查询功能",
        severity="normal",
        order=2,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_list(self):
        """查询银行列表用例"""
        try:
            api_path = self.get_api_path("GEN-银行-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "bank_code", "type": "TEXT"},
                    {"name": "bank_name", "type": "TEXT"}
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
        story="银行管理",
        title="测试查询银行详情",
        description="验证银行详情查询功能",
        severity="normal",
        order=3,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_detail(self):
        """查询银行详情用例"""
        try:
            if not self.bank_id:
                self.test_save_bank()

            api_path = self.get_api_path("GEN-银行-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.bank_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试删除银行",
        description="验证删除银行功能",
        severity="normal",
        order=4,
        tags=["银行管理", "删除"]
    )
    def test_delete_bank(self):
        """删除银行用例"""
        try:
            if not self.bank_id:
                self.test_save_bank()

            api_path = self.get_api_path("GEN-银行-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.bank_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行支行管理 ================
    @case_decorator(
        story="银行支行管理",
        title="测试新增银行支行",
        description="验证新增银行支行功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["银行支行管理", "新增"]
    )
    def test_save_sub_bank(self):
        """新增银行支行用例"""
        try:
            sub_bank_code = self.mock_data.generate_unique_code(tag="SubBank")
            sub_bank_name = f"银行支行_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-银行支行-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sub_bank_code", "sub_bank_name"], ["params", "request"]
            )
            set_dict = {"sub_bank_code": sub_bank_code, "sub_bank_name": sub_bank_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.sub_bank_id = response.get("data", {}).get("data", {})
            self.sub_bank_code = sub_bank_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试查询银行支行列表",
        description="验证银行支行列表查询功能",
        severity="normal",
        order=6,
        tags=["银行支行管理", "查询"]
    )
    def test_query_sub_bank_list(self):
        """查询银行支行列表用例"""
        try:
            api_path = self.get_api_path("GEN-银行支行-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "sub_bank_code", "type": "TEXT"},
                    {"name": "sub_bank_name", "type": "TEXT"}
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
        story="银行支行管理",
        title="测试查询银行支行详情",
        description="验证银行支行详情查询功能",
        severity="normal",
        order=7,
        tags=["银行支行管理", "查询"]
    )
    def test_query_sub_bank_detail(self):
        """查询银行支行详情用例"""
        try:
            if not self.sub_bank_id:
                self.test_save_sub_bank()

            api_path = self.get_api_path("GEN-银行支行-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.sub_bank_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试删除银行支行",
        description="验证删除银行支行功能",
        severity="normal",
        order=8,
        tags=["银行支行管理", "删除"]
    )
    def test_delete_sub_bank(self):
        """删除银行支行用例"""
        try:
            if not self.sub_bank_id:
                self.test_save_sub_bank()

            api_path = self.get_api_path("GEN-银行支行-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.sub_bank_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 