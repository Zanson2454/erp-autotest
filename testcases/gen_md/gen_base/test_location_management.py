import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("地理位置管理")
class TestLocationManagement(GenMdBaseTest):
    """地理位置管理测试类 - 整合地址、国家、时区等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.addr_id = None
        cls.addr_code = None
        cls.country_id = None
        cls.country_code = None
        cls.timezone_id = None
        cls.timezone_code = None
        cls.logger.info("地理位置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_addr_md", "gen_country_md", "gen_timezone_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 地址管理 ================
    @case_decorator(
        story="地址管理",
        title="测试新增地址",
        description="验证新增地址功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["地址管理", "新增"]
    )
    def test_save_addr(self):
        """新增地址用例"""
        try:
            addr_code = self.mock_data.generate_unique_code(tag="Addr")
            addr_name = f"地址_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-地址库-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["addr_code", "addr_name"], ["params", "request"]
            )
            set_dict = {"addr_code": addr_code, "addr_name": addr_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.addr_id = response.get("data", {}).get("data", {})
            self.addr_code = addr_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址管理",
        title="测试查询地址列表",
        description="验证地址列表查询功能",
        severity="normal",
        order=2,
        tags=["地址管理", "查询"]
    )
    def test_query_addr_list(self):
        """查询地址列表用例"""
        try:
            api_path = self.get_api_path("GEN-地址库-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "addr_code", "type": "TEXT"},
                    {"name": "addr_name", "type": "TEXT"}
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
        story="地址管理",
        title="测试删除地址",
        description="验证删除地址功能",
        severity="normal",
        order=3,
        tags=["地址管理", "删除"]
    )
    def test_delete_addr(self):
        """删除地址用例"""
        try:
            if not self.addr_id:
                self.test_save_addr()

            api_path = self.get_api_path("GEN-地址库-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.addr_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 国家管理 ================
    @case_decorator(
        story="国家管理",
        title="测试新增国家",
        description="验证新增国家功能",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["国家管理", "新增"]
    )
    def test_save_country(self):
        """新增国家用例"""
        try:
            country_code = self.mock_data.generate_unique_code(tag="Country")
            country_name = f"国家_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-国家配置表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["country_code", "country_name"], ["params", "request"]
            )
            set_dict = {"country_code": country_code, "country_name": country_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.country_id = response.get("data", {}).get("data", {})
            self.country_code = country_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家管理",
        title="测试查询国家列表",
        description="验证国家列表查询功能",
        severity="normal",
        order=5,
        tags=["国家管理", "查询"]
    )
    def test_query_country_list(self):
        """查询国家列表用例"""
        try:
            api_path = self.get_api_path("GEN-国家配置表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "country_code", "type": "TEXT"},
                    {"name": "country_name", "type": "TEXT"}
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

    # ================ 时区管理 ================
    @case_decorator(
        story="时区管理",
        title="测试新增时区",
        description="验证新增时区功能",
        severity="blocker",
        order=6,
        smoke=True,
        tags=["时区管理", "新增"]
    )
    def test_save_timezone(self):
        """新增时区用例"""
        try:
            timezone_code = self.mock_data.generate_unique_code(tag="Timezone")
            timezone_name = f"时区_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-时区配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["timezone_code", "timezone_name"], ["params", "request"]
            )
            set_dict = {"timezone_code": timezone_code, "timezone_name": timezone_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.timezone_id = response.get("data", {}).get("data", {})
            self.timezone_code = timezone_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区管理",
        title="测试查询时区列表",
        description="验证时区列表查询功能",
        severity="normal",
        order=7,
        tags=["时区管理", "查询"]
    )
    def test_query_timezone_list(self):
        """查询时区列表用例"""
        try:
            api_path = self.get_api_path("GEN-时区配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "timezone_code", "type": "TEXT"},
                    {"name": "timezone_name", "type": "TEXT"}
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