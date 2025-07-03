import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("税务系统管理")
class TestTaxSystemManagement(GenMdBaseTest):
    """税务系统管理测试类 - 整合税配置、客户税分类、物料税分类等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.tax_id = None
        cls.tax_code = None
        cls.cust_tax_id = None
        cls.cust_tax_code = None
        cls.mat_tax_id = None
        cls.mat_tax_code = None
        cls.logger.info("税务系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_tax_md", "gen_cust_tax_md", "gen_mat_tax_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 税配置管理 ================
    @case_decorator(
        story="税配置管理",
        title="测试新增税配置",
        description="验证新增税配置功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["税配置管理", "新增"]
    )
    def test_save_tax(self):
        """新增税配置用例"""
        try:
            tax_code = self.mock_data.generate_unique_code(tag="Tax")
            tax_name = f"税配置_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-物料税分类-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["tax_code", "tax_name"], ["params", "request"]
            )
            set_dict = {"tax_code": tax_code, "tax_name": tax_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.tax_id = response.get("data", {}).get("data", {})
            self.tax_code = tax_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试查询税配置列表",
        description="验证税配置列表查询功能",
        severity="normal",
        order=2,
        tags=["税配置管理", "查询"]
    )
    def test_query_tax_list(self):
        """查询税配置列表用例"""
        try:
            api_path = self.get_api_path("GEN-税配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "tax_code", "type": "TEXT"},
                    {"name": "tax_name", "type": "TEXT"}
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
        story="税配置管理",
        title="测试查询税配置详情",
        description="验证税配置详情查询功能",
        severity="normal",
        order=3,
        tags=["税配置管理", "查询"]
    )
    def test_query_tax_detail(self):
        """查询税配置详情用例"""
        try:
            if not self.tax_id:
                self.test_save_tax()

            api_path = self.get_api_path("GEN-物料税分类-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试删除税配置",
        description="验证删除税配置功能",
        severity="normal",
        order=4,
        tags=["税配置管理", "删除"]
    )
    def test_delete_tax(self):
        """删除税配置用例"""
        try:
            if not self.tax_id:
                self.test_save_tax()

            api_path = self.get_api_path("GEN-客户税分类-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.tax_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 客户税分类管理 ================
    @case_decorator(
        story="客户税分类管理",
        title="测试新增客户税分类",
        description="验证新增客户税分类功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["客户税分类管理", "新增"]
    )
    def test_save_cust_tax(self):
        """新增客户税分类用例"""
        try:
            cust_tax_code = self.mock_data.generate_unique_code(tag="CustTax")
            cust_tax_name = f"客户税分类_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-客户税分类配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["cust_tax_code", "cust_tax_name"], ["params", "request"]
            )
            set_dict = {"cust_tax_code": cust_tax_code, "cust_tax_name": cust_tax_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.cust_tax_id = response.get("data", {}).get("data", {})
            self.cust_tax_code = cust_tax_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="客户税分类管理",
        title="测试查询客户税分类列表",
        description="验证客户税分类列表查询功能",
        severity="normal",
        order=6,
        tags=["客户税分类管理", "查询"]
    )
    def test_query_cust_tax_list(self):
        """查询客户税分类列表用例"""
        try:
            api_path = self.get_api_path("客户税分类配置-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "cust_tax_code", "type": "TEXT"},
                    {"name": "cust_tax_name", "type": "TEXT"}
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

    # ================ 物料税分类管理 ================
    @case_decorator(
        story="物料税分类管理",
        title="测试新增物料税分类",
        description="验证新增物料税分类功能",
        severity="blocker",
        order=7,
        smoke=True,
        tags=["物料税分类管理", "新增"]
    )
    def test_save_mat_tax(self):
        """新增物料税分类用例"""
        try:
            mat_tax_code = self.mock_data.generate_unique_code(tag="MatTax")
            mat_tax_name = f"物料税分类_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-物料税分类配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["mat_tax_code", "mat_tax_name"], ["params", "request"]
            )
            set_dict = {"mat_tax_code": mat_tax_code, "mat_tax_name": mat_tax_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.mat_tax_id = response.get("data", {}).get("data", {})
            self.mat_tax_code = mat_tax_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料税分类管理",
        title="测试查询物料税分类列表",
        description="验证物料税分类列表查询功能",
        severity="normal",
        order=8,
        tags=["物料税分类管理", "查询"]
    )
    def test_query_mat_tax_list(self):
        """查询物料税分类列表用例"""
        try:
            api_path = self.get_api_path("物料税分类配置-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "mat_tax_code", "type": "TEXT"},
                    {"name": "mat_tax_name", "type": "TEXT"}
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