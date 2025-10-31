import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("属性管理")
class TestAttrManagement(GenMdBaseTest):
    """属性管理测试类 - 覆盖所有属性表相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.attr_id = None
        cls.attr_code = None
        cls.logger.info("属性管理测试类初始化完成")
        cls.attr_field_list = []

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_attr_cf"]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="attr_code like %s",
                        params=["AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 属性表基础管理 ================
    @case_decorator(
        story="属性管理",
        title="测试新增属性",
        description="验证GEN-属性表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["属性管理", "新增", "GEN_ATTR_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_attr(self):
        """新增属性用例 - GEN_ATTR_CF_SAVE_ACTION_SERVICE"""
        try:
            attr_code = self.mock_util.generate_unique_code(tag="ATTR")
            attr_name = f"测试属性_{self.mock_util.get_timestamp()}"
            if self.attr_field_list:
                attr_field = self.attr_field_list[0]
            else:
                self.test_query_available_bind_fields()
                attr_field = self.attr_field_list[0]

            api_path = self.get_api_path("GEN-属性表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "attrType", "dataType", "description"], ["params", "request"]
            )
            set_dict = {
                "attrCode": attr_code,
                "attrName": attr_name,
                "attrDataType": "CHAR",
                "attrClassCode": "ORG", 
                "attrField": attr_field,
                "attrLength": 40,
                "attrIsMulti": False, 
                "attrIsRequired": False,
                "objectMeta":{}
            }
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
        title="测试查询属性分页列表",
        description="验证GEN-属性表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["属性管理", "查询", "GEN_ATTR_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_attr_page(self):
        """查询属性分页列表用例 - GEN_ATTR_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-属性表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "attrType", "type": "TEXT"},
                    {"name": "dataType", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
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
        story="属性管理",
        title="测试查询属性详情",
        description="验证GEN-属性表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["属性管理", "查询", "GEN_ATTR_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_attr_detail(self):
        """查询属性详情用例 - GEN_ATTR_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.attr_id:
                self.test_save_attr()

            api_path = self.get_api_path("GEN-属性表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.attr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="属性管理",
        title="测试查询属性可绑定字段",
        description="验证查询属性可以绑定的字段服务功能",
        severity="normal",
        file_level_order=4,
        tags=["属性管理", "字段绑定", "GEN_ATTR_QUERY_AVAILABLE_BIND_FILED_ACTION_SERVICE"]
    )
    def test_query_available_bind_fields(self):
        """查询属性可绑定字段用例 - GEN_ATTR_QUERY_AVAILABLE_BIND_FILED_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("查询属性可以绑定的字段服务")
            params, url = self.get_api_params(api_path)
            params = {
                "teamId": "22",
                "portalKey": "TERP_PORTAL",
                "params": {
                    "request": None
                }
            }
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            # 验证返回的字段列表
            fields_data = response.get("data", {}).get("data", []).get("availableFiledMap",[])
            for field in fields_data:
                self.attr_field_list.append(field)
            self.assert_util.assert_by_operator(len(fields_data), ">", 0)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="属性管理",
        title="测试启用属性",
        description="验证GEN-属性表-启用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["属性管理", "启用", "GEN_ATTR_CF_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_attr(self):
        """启用属性用例 - GEN_ATTR_CF_ENABLED_ACTION_SERVICE"""
        try:
            if not self.attr_id:
                self.test_save_attr()

            api_path = self.get_api_path("GEN-属性表-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.attr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="属性管理",
        title="测试禁用属性",
        description="验证GEN-属性表-禁用服务功能",
        severity="normal",
        file_level_order=6,
        tags=["属性管理", "禁用", "GEN_ATTR_CF_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_attr(self):
        """禁用属性用例 - GEN_ATTR_CF_DISABLED_ACTION_SERVICE"""
        try:
            if not self.attr_id:
                self.test_save_attr()

            api_path = self.get_api_path("GEN-属性表-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.attr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="属性管理",
        title="测试删除属性",
        description="验证GEN-属性表-删除服务功能",
        severity="critical",
        file_level_order=7,
        tags=["属性管理", "删除", "GEN_ATTR_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_attr(self):
        """删除属性用例 - GEN_ATTR_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.attr_id:
                self.test_save_attr()

            api_path = self.get_api_path("GEN-属性表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.attr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
