from typing import Any

import allure

from testcases.gen_md import GenMdBaseTest
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
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("属性管理测试类初始化完成")
        cls.attr_field_list = []

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _query_available_bind_fields(self):
        set_dict = {"id": 0}
        response, _ = self.standard_api_call(
            api_key="查询属性可以绑定的字段服务",
            set_dict=set_dict,
            fields_to_filter=["id"],
            store_id_as=None
        )

        fields_data = response.get("data", {}).get("data", []).get("availableFiledMap", [])
        self.attr_field_list = list(fields_data)
        self.assert_util.assert_by_operator(len(fields_data), ">", 0)
        return self.attr_field_list

    def _ensure_query_available_bind_fields(self):
        if self.attr_field_list:
            return self.attr_field_list
        return self._query_available_bind_fields()

    def _create_attr(self):
        attr_code = self.mock_util.generate_unique_code(tag="ATTR")
        attr_name = f"测试属性_{self.mock_util.get_timestamp()}"
        attr_field_list = self._ensure_query_available_bind_fields()
        attr_field = attr_field_list[0]

        set_dict = {
            "attrCode": attr_code,
            "attrName": attr_name,
            "attrDataType": "CHAR",
            "attrClassCode": "ORG",
            "attrField": attr_field,
            "attrLength": 40,
            "attrIsMulti": False,
            "attrIsRequired": False,
            "objectMeta": {}
        }

        response, attr_id = self.standard_api_call(
            api_key="GEN-属性表-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "attrType", "dataType", "description"],
            store_id_as="attr"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("attr", attr_id)
        self.test_data["attr_code"] = attr_code
        return attr_id

    def _ensure_save_attr(self):
        attr_id = self.get_runtime_id("attr")
        if attr_id:
            return attr_id
        return self._create_attr()
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
            self._create_attr()

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
            
            response, _ = self.standard_api_call(
                api_key="GEN-属性表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

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
            attr_id = self._ensure_save_attr()
            set_dict = {"id": attr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-属性表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

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
            self._query_available_bind_fields()

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
            attr_id = self._ensure_save_attr()
            set_dict = {"id": attr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-属性表-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

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
            attr_id = self._ensure_save_attr()
            set_dict = {"id": attr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-属性表-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

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
            attr_id = self._ensure_save_attr()
            set_dict = {"id": attr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-属性表-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
