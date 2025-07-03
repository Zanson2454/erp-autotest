import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("系统管理")
class TestSystemManagement(GenMdBaseTest):
    """系统管理测试类 - 整合标签、属性、数据字典、BOM、日历等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.label_id = None
        cls.label_code = None
        cls.attr_id = None
        cls.attr_code = None
        cls.dict_id = None
        cls.dict_code = None
        cls.bom_id = None
        cls.bom_code = None
        cls.calendar_id = None
        cls.calendar_code = None
        cls.logger.info("系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_label_md", "gen_attr_md", "gen_dict_md", "gen_bom_md", "gen_calendar_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 标签管理 ================
    @case_decorator(
        story="标签管理",
        title="测试新增标签",
        description="验证新增标签功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["标签管理", "新增"]
    )
    def test_save_label(self):
        """新增标签用例"""
        try:
            label_code = self.mock_data.generate_unique_code(tag="Label")
            label_name = f"标签_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-标签表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["label_code", "label_name"], ["params", "request"]
            )
            set_dict = {"label_code": label_code, "label_name": label_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.label_id = response.get("data", {}).get("data", {})
            self.label_code = label_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签管理",
        title="测试查询标签列表",
        description="验证标签列表查询功能",
        severity="normal",
        order=2,
        tags=["标签管理", "查询"]
    )
    def test_query_label_list(self):
        """查询标签列表用例"""
        try:
            api_path = self.get_api_path("GEN-标签表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "label_code", "type": "TEXT"},
                    {"name": "label_name", "type": "TEXT"}
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
        story="标签管理",
        title="测试删除标签",
        description="验证删除标签功能",
        severity="normal",
        order=3,
        tags=["标签管理", "删除"]
    )
    def test_delete_label(self):
        """删除标签用例"""
        try:
            if not self.label_id:
                self.test_save_label()

            api_path = self.get_api_path("GEN-标签表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.label_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 属性管理 ================
    @case_decorator(
        story="属性管理",
        title="测试新增属性",
        description="验证新增属性功能",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["属性管理", "新增"]
    )
    def test_save_attr(self):
        """新增属性用例"""
        try:
            attr_code = self.mock_data.generate_unique_code(tag="Attr")
            attr_name = f"属性_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-特征定义表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["attr_code", "attr_name"], ["params", "request"]
            )
            set_dict = {"attr_code": attr_code, "attr_name": attr_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.attr_id = response.get("data", {}).get("data", {})
            self.attr_code = attr_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="属性管理",
        title="测试查询属性列表",
        description="验证属性列表查询功能",
        severity="normal",
        order=5,
        tags=["属性管理", "查询"]
    )
    def test_query_attr_list(self):
        """查询属性列表用例"""
        try:
            api_path = self.get_api_path("GEN-特征定义表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "attr_code", "type": "TEXT"},
                    {"name": "attr_name", "type": "TEXT"}
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
        story="属性管理",
        title="测试删除属性",
        description="验证删除属性功能",
        severity="normal",
        order=6,
        tags=["属性管理", "删除"]
    )
    def test_delete_attr(self):
        """删除属性用例"""
        try:
            if not self.attr_id:
                self.test_save_attr()

            api_path = self.get_api_path("GEN-特征类定义表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.attr_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 数据字典管理 ================
    @case_decorator(
        story="数据字典管理",
        title="测试新增数据字典",
        description="验证新增数据字典功能",
        severity="blocker",
        order=7,
        smoke=True,
        tags=["数据字典管理", "新增"]
    )
    def test_save_dict(self):
        """新增数据字典用例"""
        try:
            dict_code = self.mock_data.generate_unique_code(tag="Dict")
            dict_name = f"数据字典_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-数据字典类别-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["dict_code", "dict_name"], ["params", "request"]
            )
            set_dict = {"dict_code": dict_code, "dict_name": dict_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.dict_id = response.get("data", {}).get("data", {})
            self.dict_code = dict_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试查询数据字典列表",
        description="验证数据字典列表查询功能",
        severity="normal",
        order=8,
        tags=["数据字典管理", "查询"]
    )
    def test_query_dict_list(self):
        """查询数据字典列表用例"""
        try:
            api_path = self.get_api_path("GEN-数据字典类别-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "dict_code", "type": "TEXT"},
                    {"name": "dict_name", "type": "TEXT"}
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
        story="数据字典管理",
        title="测试删除数据字典",
        description="验证删除数据字典功能",
        severity="normal",
        order=9,
        tags=["数据字典管理", "删除"]
    )
    def test_delete_dict(self):
        """删除数据字典用例"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            api_path = self.get_api_path("GEN-数据字典类别-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.dict_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ BOM管理 ================
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM",
        description="验证新增BOM功能",
        severity="blocker",
        order=10,
        smoke=True,
        tags=["BOM管理", "新增"]
    )
    def test_save_bom(self):
        """新增BOM用例"""
        try:
            bom_code = self.mock_data.generate_unique_code(tag="Bom")
            bom_name = f"BOM_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-物料BOM头-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["bom_code", "bom_name"], ["params", "request"]
            )
            set_dict = {"bom_code": bom_code, "bom_name": bom_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_id = response.get("data", {}).get("data", {})
            self.bom_code = bom_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM列表",
        description="验证BOM列表查询功能",
        severity="normal",
        order=11,
        tags=["BOM管理", "查询"]
    )
    def test_query_bom_list(self):
        """查询BOM列表用例"""
        try:
            api_path = self.get_api_path("GEN-BOM状态配置表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "bom_code", "type": "TEXT"},
                    {"name": "bom_name", "type": "TEXT"}
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
        story="BOM管理",
        title="测试删除BOM",
        description="验证删除BOM功能",
        severity="normal",
        order=12,
        tags=["BOM管理", "删除"]
    )
    def test_delete_bom(self):
        """删除BOM用例"""
        try:
            if not self.bom_id:
                self.test_save_bom()

            api_path = self.get_api_path("GEN-BOM行项目类别配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.bom_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 日历管理 ================
    @case_decorator(
        story="日历管理",
        title="测试新增日历",
        description="验证新增日历功能",
        severity="blocker",
        order=13,
        smoke=True,
        tags=["日历管理", "新增"]
    )
    def test_save_calendar(self):
        """新增日历用例"""
        try:
            calendar_code = self.mock_data.generate_unique_code(tag="Calendar")
            calendar_name = f"日历_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-工作日日历头表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["calendar_code", "calendar_name"], ["params", "request"]
            )
            set_dict = {"calendar_code": calendar_code, "calendar_name": calendar_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.calendar_id = response.get("data", {}).get("data", {})
            self.calendar_code = calendar_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="日历管理",
        title="测试查询日历列表",
        description="验证日历列表查询功能",
        severity="normal",
        order=14,
        tags=["日历管理", "查询"]
    )
    def test_query_calendar_list(self):
        """查询日历列表用例"""
        try:
            api_path = self.get_api_path("GEN-工作日日历头表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "calendar_code", "type": "TEXT"},
                    {"name": "calendar_name", "type": "TEXT"}
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
        story="日历管理",
        title="测试删除日历",
        description="验证删除日历功能",
        severity="normal",
        order=15,
        tags=["日历管理", "删除"]
    )
    def test_delete_calendar(self):
        """删除日历用例"""
        try:
            if not self.calendar_id:
                self.test_save_calendar()

            api_path = self.get_api_path("GEN-工作日日历头表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.calendar_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 