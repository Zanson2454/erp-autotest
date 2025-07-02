import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("基础配置管理")
class TestBasicConfigManagement(GenMdBaseTest):
    """基础配置管理测试类 - 整合地址、国家、时区、币种、汇率等管理功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 各模块数据存储
        cls.addr_id = None
        cls.addr_code = None
        cls.country_id = None
        cls.country_code = None
        cls.timezone_id = None
        cls.timezone_code = None
        cls.curr_id = None
        cls.curr_code = None
        cls.exchange_rate_id = None
        cls.exchange_rate_code = None
        cls.logger.info("基础配置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理各模块测试数据
            tables = [
                "gen_addr_md",
                "gen_country_md", 
                "gen_timezone_md",
                "gen_curr_md",
                "gen_exchange_rate_md"
            ]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="code like %s OR addr_code like %s OR country_code like %s OR timezone_code like %s OR curr_code like %s OR exchange_rate_code like %s",
                        params=["AT_%", "AT_%", "AT_%", "AT_%", "AT_%", "AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 地址管理 ================
    @case_decorator(
        story="地址管理",
        title="测试新增地址管理",
        description="验证新增地址管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["地址管理", "新增"]
    )
    def test_save_addr(self):
        """新增地址管理用例"""
        try:
            addr_code = self.mock_data.generate_unique_code(tag="Addr")
            addr_name = f"地址管理_{self.mock_data.get_timestamp()}"

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
        title="测试查询地址管理列表",
        description="验证地址管理列表查询功能",
        severity="normal",
        order=2,
        tags=["地址管理", "查询"]
    )
    def test_query_addr_list(self):
        """查询地址管理列表用例"""
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
        title="测试删除地址管理",
        description="验证删除地址管理功能",
        severity="normal",
        order=3,
        tags=["地址管理", "删除"]
    )
    def test_delete_addr(self):
        """删除地址管理用例"""
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
        title="测试新增国家管理",
        description="验证新增国家管理功能",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["国家管理", "新增"]
    )
    def test_save_country(self):
        """新增国家管理用例"""
        try:
            country_code = self.mock_data.generate_unique_code(tag="Country")
            country_name = f"国家管理_{self.mock_data.get_timestamp()}"

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
        title="测试查询国家管理列表",
        description="验证国家管理列表查询功能",
        severity="normal",
        order=5,
        tags=["国家管理", "查询"]
    )
    def test_query_country_list(self):
        """查询国家管理列表用例"""
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

    @case_decorator(
        story="国家管理",
        title="测试删除国家管理",
        description="验证删除国家管理功能",
        severity="normal",
        order=6,
        tags=["国家管理", "删除"]
    )
    def test_delete_country(self):
        """删除国家管理用例"""
        try:
            if not self.country_id:
                self.test_save_country()

            api_path = self.get_api_path("GEN-国家配置表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.country_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 时区管理 ================
    @case_decorator(
        story="时区管理",
        title="测试新增时区管理",
        description="验证新增时区管理功能",
        severity="blocker",
        order=7,
        smoke=True,
        tags=["时区管理", "新增"]
    )
    def test_save_timezone(self):
        """新增时区管理用例"""
        try:
            timezone_code = self.mock_data.generate_unique_code(tag="Timezone")
            timezone_name = f"时区管理_{self.mock_data.get_timestamp()}"

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
        title="测试查询时区管理列表",
        description="验证时区管理列表查询功能",
        severity="normal",
        order=8,
        tags=["时区管理", "查询"]
    )
    def test_query_timezone_list(self):
        """查询时区管理列表用例"""
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

    @case_decorator(
        story="时区管理",
        title="测试删除时区管理",
        description="验证删除时区管理功能",
        severity="normal",
        order=9,
        tags=["时区管理", "删除"]
    )
    def test_delete_timezone(self):
        """删除时区管理用例"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            api_path = self.get_api_path("GEN-时区配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.timezone_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 币种管理 ================
    @case_decorator(
        story="币种管理",
        title="测试新增币种管理",
        description="验证新增币种管理功能",
        severity="blocker",
        order=10,
        smoke=True,
        tags=["币种管理", "新增"]
    )
    def test_save_curr(self):
        """新增币种管理用例"""
        try:
            curr_code = self.mock_data.generate_unique_code(tag="Curr")
            curr_name = f"币种管理_{self.mock_data.get_timestamp()}"

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
        title="测试查询币种管理列表",
        description="验证币种管理列表查询功能",
        severity="normal",
        order=11,
        tags=["币种管理", "查询"]
    )
    def test_query_curr_list(self):
        """查询币种管理列表用例"""
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
        title="测试删除币种管理",
        description="验证删除币种管理功能",
        severity="normal",
        order=12,
        tags=["币种管理", "删除"]
    )
    def test_delete_curr(self):
        """删除币种管理用例"""
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
        title="测试新增汇率管理",
        description="验证新增汇率管理功能",
        severity="blocker",
        order=13,
        smoke=True,
        tags=["汇率管理", "新增"]
    )
    def test_save_exchange_rate(self):
        """新增汇率管理用例"""
        try:
            exchange_rate_code = self.mock_data.generate_unique_code(tag="ExchangeRate")
            exchange_rate_name = f"汇率管理_{self.mock_data.get_timestamp()}"

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
        title="测试查询汇率管理列表",
        description="验证汇率管理列表查询功能",
        severity="normal",
        order=14,
        tags=["汇率管理", "查询"]
    )
    def test_query_exchange_rate_list(self):
        """查询汇率管理列表用例"""
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
        title="测试删除汇率管理",
        description="验证删除汇率管理功能",
        severity="normal",
        order=15,
        tags=["汇率管理", "删除"]
    )
    def test_delete_exchange_rate(self):
        """删除汇率管理用例"""
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