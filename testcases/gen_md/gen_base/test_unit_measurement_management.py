import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("计量单位管理")
class TestUnitMeasurementManagement(GenMdBaseTest):
    """计量单位管理测试类 - 整合计量单位、转换、换算等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 各模块数据存储
        cls.uom_id = None
        cls.uom_code = None
        cls.uom_conversion_id = None
        cls.uom_conversion_code = None
        cls.uom_formula_id = None
        cls.uom_formula_code = None
        cls.logger.info("计量单位管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理各模块测试数据
            tables = [
                "gen_uom_md",
                "gen_uom_conversion_md", 
                "gen_uom_formula_md"
            ]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="code like %s OR uom_code like %s OR conversion_code like %s OR formula_code like %s",
                        params=["AT_%", "AT_%", "AT_%", "AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 计量单位管理 ================
    @case_decorator(
        story="计量单位管理",
        title="测试新增计量单位",
        description="验证新增计量单位功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["计量单位管理", "新增"]
    )
    def test_save_uom(self):
        """新增计量单位用例"""
        try:
            uom_code = self.mock_data.generate_unique_code(tag="Uom")
            uom_name = f"计量单位_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位转换-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["uom_code", "uom_name"], ["params", "request"]
            )
            set_dict = {"uom_code": uom_code, "uom_name": uom_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_id = response.get("data", {}).get("data", {})
            self.uom_code = uom_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位管理",
        title="测试查询计量单位列表",
        description="验证计量单位列表查询功能",
        severity="normal",
        order=2,
        tags=["计量单位管理", "查询"]
    )
    def test_query_uom_list(self):
        """查询计量单位列表用例"""
        try:
            api_path = self.get_api_path("GEN-计量单位转换-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "uom_code", "type": "TEXT"},
                    {"name": "uom_name", "type": "TEXT"}
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
        story="计量单位管理",
        title="测试查询计量单位详情",
        description="验证计量单位详情查询功能",
        severity="normal",
        order=3,
        tags=["计量单位管理", "查询"]
    )
    def test_query_uom_detail(self):
        """查询计量单位详情用例"""
        try:
            if not self.uom_id:
                self.test_save_uom()

            api_path = self.get_api_path("GEN-计量单位转换-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位管理",
        title="测试删除计量单位",
        description="验证删除计量单位功能",
        severity="normal",
        order=4,
        tags=["计量单位管理", "删除"]
    )
    def test_delete_uom(self):
        """删除计量单位用例"""
        try:
            if not self.uom_id:
                self.test_save_uom()

            api_path = self.get_api_path("GEN-计量单位-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.uom_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 计量单位换算管理 ================
    @case_decorator(
        story="计量单位换算管理",
        title="测试新增计量单位换算",
        description="验证新增计量单位换算功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["计量单位换算管理", "新增"]
    )
    def test_save_uom_conversion(self):
        """新增计量单位换算用例"""
        try:
            uom_conversion_code = self.mock_data.generate_unique_code(tag="UomConversion")
            uom_conversion_name = f"计量单位换算_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位换算定义-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["uom_conversion_code", "uom_conversion_name"], ["params", "request"]
            )
            set_dict = {"uom_conversion_code": uom_conversion_code, "uom_conversion_name": uom_conversion_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_conversion_id = response.get("data", {}).get("data", {})
            self.uom_conversion_code = uom_conversion_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位换算管理",
        title="测试查询计量单位换算列表",
        description="验证计量单位换算列表查询功能",
        severity="normal",
        order=6,
        tags=["计量单位换算管理", "查询"]
    )
    def test_query_uom_conversion_list(self):
        """查询计量单位换算列表用例"""
        try:
            api_path = self.get_api_path("GEN-计量单位换算定义-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "uom_conversion_code", "type": "TEXT"},
                    {"name": "uom_conversion_name", "type": "TEXT"}
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
        story="计量单位换算管理",
        title="测试删除计量单位换算",
        description="验证删除计量单位换算功能",
        severity="normal",
        order=7,
        tags=["计量单位换算管理", "删除"]
    )
    def test_delete_uom_conversion(self):
        """删除计量单位换算用例"""
        try:
            if not self.uom_conversion_id:
                self.test_save_uom_conversion()

            api_path = self.get_api_path("GEN-计量单位换算定义-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.uom_conversion_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 计量单位转换管理 ================
    @case_decorator(
        story="计量单位转换管理",
        title="测试新增计量单位转换",
        description="验证新增计量单位转换功能",
        severity="blocker",
        order=8,
        smoke=True,
        tags=["计量单位转换管理", "新增"]
    )
    def test_save_uom_formula(self):
        """新增计量单位转换用例"""
        try:
            uom_formula_code = self.mock_data.generate_unique_code(tag="UomFormula")
            uom_formula_name = f"计量单位转换_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位转换-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["uom_formula_code", "uom_formula_name"], ["params", "request"]
            )
            set_dict = {"uom_formula_code": uom_formula_code, "uom_formula_name": uom_formula_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_formula_id = response.get("data", {}).get("data", {})
            self.uom_formula_code = uom_formula_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位转换管理",
        title="测试查询计量单位转换列表",
        description="验证计量单位转换列表查询功能",
        severity="normal",
        order=9,
        tags=["计量单位转换管理", "查询"]
    )
    def test_query_uom_formula_list(self):
        """查询计量单位转换列表用例"""
        try:
            api_path = self.get_api_path("GEN-计量单位转换-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "uom_formula_code", "type": "TEXT"},
                    {"name": "uom_formula_name", "type": "TEXT"}
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
        story="计量单位转换管理",
        title="测试查询计量单位转换详情",
        description="验证计量单位转换详情查询功能",
        severity="normal",
        order=10,
        tags=["计量单位转换管理", "查询"]
    )
    def test_query_uom_formula_detail(self):
        """查询计量单位转换详情用例"""
        try:
            if not self.uom_formula_id:
                self.test_save_uom_formula()

            api_path = self.get_api_path("GEN-计量单位转换-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_formula_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位转换管理",
        title="测试删除计量单位转换",
        description="验证删除计量单位转换功能",
        severity="normal",
        order=11,
        tags=["计量单位转换管理", "删除"]
    )
    def test_delete_uom_formula(self):
        """删除计量单位转换用例"""
        try:
            if not self.uom_formula_id:
                self.test_save_uom_formula()

            api_path = self.get_api_path("GEN-计量单位转换-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.uom_formula_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 