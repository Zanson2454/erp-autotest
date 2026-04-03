from typing import Any

import allure
import pytest

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("税配置管理")
class TestTaxManagement(GenMdBaseTest):
    """税配置管理测试类 - 覆盖所有税配置相关服务"""
    
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
        cls.logger.info("税配置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_tax(self):
        tax_code = self.mock_util.generate_unique_code(tag="TAX")
        tax_name = f"测试税种_{self.mock_util.get_timestamp()}"

        set_dict = {
            "taxCode": tax_code,
            "taxName": tax_name,
            "taxRate": 0.13,
            "remark": f"税种描述_{self.mock_util.get_timestamp()}"
        }

        response, tax_id = self.standard_api_call(
            api_key="GEN-税配置-保存服务",
            set_dict=set_dict,
            fields_to_filter=["taxCode", "taxName", "taxRate", "remark"],
            store_id_as="tax"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("tax", tax_id)
        self.test_data["tax_code"] = tax_code
        return tax_id

    def _ensure_save_tax(self):
        tax_id = self.get_runtime_id("tax")
        if tax_id:
            return tax_id
        return self._create_tax()

    @case_decorator(
        story="税配置管理",
        title="测试新增税配置",
        description="验证GEN-税配置-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["税配置", "新增", "GEN_TAX_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_tax(self):
        """新增税配置用例"""
        try:
            self._create_tax()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试查询税配置分页列表",
        description="验证GEN-税配置-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["税配置", "查询", "GEN_TAX_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_tax_page(self):
        """查询税配置分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "taxRate", "type": "NUMBER"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-税配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试查询税配置详情",
        description="验证GEN-税配置-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["税配置", "查询", "GEN_TAX_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_tax_detail(self):
        """查询税配置详情用例"""
        try:
            tax_id = self._ensure_save_tax()
            set_dict = {"id": tax_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-税配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试税配置分页数据",
        description="验证税配置-分页数据服务功能",
        severity="normal",
        file_level_order=4,
        tags=["税配置", "分页数据", "GEN_TAX_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_paging_data(self):
        """税配置分页数据用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "taxRate", "type": "NUMBER"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="税配置-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试根据ID查找税配置数据",
        description="验证税配置-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=5,
        tags=["税配置", "ID查找", "GEN_TAX_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_find_tax_by_id(self):
        """根据ID查找税配置数据用例"""
        try:
            tax_id = self._ensure_save_tax()
            set_dict = {"id": tax_id}
            
            response, _ = self.standard_api_call(
                api_key="税配置-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试删除税配置",
        description="验证GEN-税配置-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["税配置", "删除", "GEN_TAX_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_tax(self):
        """删除税配置用例"""
        try:
            tax_id = self._ensure_save_tax()
            set_dict = {"id": tax_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-税配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 税配置导入导出管理 ================

    @case_decorator(
        story="税配置导入导出管理",
        title="测试税配置标准导出",
        description="验证税配置标准导出服务功能",
        severity="normal",
        file_level_order=8,
        tags=["税配置", "导出", "GEN_TAX_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_export(self):
        """税配置标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "taxRate", "type": "NUMBER"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="税配置标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="税配置任务管理",
        title="测试税配置导出任务",
        description="验证税配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["税配置", "任务管理", "GEN_TAX_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_export_task(self):
        """税配置导出任务用例"""
        try:
            set_dict = {
                "taskName": f"税配置导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "taxRate", "type": "NUMBER"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="税配置-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
