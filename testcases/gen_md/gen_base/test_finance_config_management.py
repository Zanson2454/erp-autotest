import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("财务配置管理")
class TestFinanceConfigManagement(GenMdBaseTest):
    """财务配置管理测试类 - 整合币种、汇率等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.curr_id = None
        cls.curr_code = None
        cls.exchange_rate_id = None
        cls.exchange_rate_code = None
        cls.logger.info("财务配置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_curr_md", "gen_exchange_rate_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 币种管理 ================
    @case_decorator(
        story="币种管理",
        title="测试新增币种",
        description="验证新增币种功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["币种管理", "新增"]
    )
    def test_save_curr(self):
        """新增币种用例"""
        try:
            curr_code = self.mock_data.generate_unique_code(tag="Curr")
            curr_name = f"币种_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-币种配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["curr_code", "curr_name"], ["params", "request"]
            )
            set_dict = {"curr_code": curr_code, "curr_name": curr_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.curr_id = response.get("data", {}).get("data", {})
            self.curr_code = curr_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种管理",
        title="测试查询币种列表",
        description="验证币种列表查询功能",
        severity="normal",
        order=2,
        tags=["币种管理", "查询"]
    )
    def test_query_curr_list(self):
        """查询币种列表用例"""
        try:
            api_path = self.get_api_path("币种配置-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "curr_code", "type": "TEXT"},
                    {"name": "curr_name", "type": "TEXT"}
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
        story="币种管理",
        title="测试查询币种详情",
        description="验证币种详情查询功能",
        severity="normal",
        order=3,
        tags=["币种管理", "查询"]
    )
    def test_query_curr_detail(self):
        """查询币种详情用例"""
        try:
            if not self.curr_id:
                self.test_save_curr()

            api_path = self.get_api_path("币种配置-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.curr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种管理",
        title="测试删除币种",
        description="验证删除币种功能",
        severity="normal",
        order=4,
        tags=["币种管理", "删除"]
    )
    def test_delete_curr(self):
        """删除币种用例"""
        try:
            if not self.curr_id:
                self.test_save_curr()

            api_path = self.get_api_path("GEN-币种配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.curr_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 汇率管理 ================
    @case_decorator(
        story="汇率管理",
        title="测试新增汇率",
        description="验证新增汇率功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["汇率管理", "新增"]
    )
    def test_save_exchange_rate(self):
        """新增汇率用例"""
        try:
            exchange_rate_code = self.mock_data.generate_unique_code(tag="ExchangeRate")
            exchange_rate_name = f"汇率_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-汇率定义-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["exchange_rate_code", "exchange_rate_name"], ["params", "request"]
            )
            set_dict = {"exchange_rate_code": exchange_rate_code, "exchange_rate_name": exchange_rate_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.exchange_rate_id = response.get("data", {}).get("data", {})
            self.exchange_rate_code = exchange_rate_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试查询汇率列表",
        description="验证汇率列表查询功能",
        severity="normal",
        order=6,
        tags=["汇率管理", "查询"]
    )
    def test_query_exchange_rate_list(self):
        """查询汇率列表用例"""
        try:
            api_path = self.get_api_path("GEN-汇率定义-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "exchange_rate_code", "type": "TEXT"},
                    {"name": "exchange_rate_name", "type": "TEXT"}
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
        story="汇率管理",
        title="测试查询汇率详情",
        description="验证汇率详情查询功能",
        severity="normal",
        order=7,
        tags=["汇率管理", "查询"]
    )
    def test_query_exchange_rate_detail(self):
        """查询汇率详情用例"""
        try:
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            api_path = self.get_api_path("GEN-汇率定义-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.exchange_rate_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试删除汇率",
        description="验证删除汇率功能",
        severity="normal",
        order=8,
        tags=["汇率管理", "删除"]
    )
    def test_delete_exchange_rate(self):
        """删除汇率用例"""
        try:
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            api_path = self.get_api_path("GEN-汇率定义-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.exchange_rate_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 