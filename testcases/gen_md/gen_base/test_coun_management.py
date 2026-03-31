import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("国家管理")
class TestCountryManagement(GenMdBaseTest):
    """国家管理测试类 - 覆盖所有国家配置相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.country_id = None
        cls.country_code = None
        cls.logger.info("国家管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="国家配置管理",
        title="测试新增国家配置",
        description="验证GEN-国家配置表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["国家管理", "新增", "GEN_COUN_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_country(self):
        """新增国家配置用例"""
        try:
            country_code = self.mock_util.generate_unique_code(tag="COUN")
            country_name = f"测试国家_{self.mock_util.get_timestamp()}"

            set_dict = {
                "counCode": country_code,
                "counName": country_name,
                "counNameEn": f"Test Country_{self.mock_util.get_timestamp()}",
                "counPhoneCode": "+86",
                "counCurrency": "CNY",
                "counCurrencyEn": "Chinese Yuan"
            }
            
            response, country_id = self.standard_api_call(
                api_key="GEN-国家配置表-保存服务",
                set_dict=set_dict,
                fields_to_filter=["counCode", "counName", "counNameEn", "counPhoneCode", "counCurrency", "counCurrencyEn"],
                store_id_as="country"
            )
            
            self.country_code = country_code

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试查询国家配置分页列表",
        description="验证GEN-国家配置表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_country_page(self):
        """查询国家配置分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "nameEn", "type": "TEXT"},
                    {"name": "phoneCode", "type": "TEXT"},
                    {"name": "currency", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-国家配置表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试查询国家配置详情",
        description="验证GEN-国家配置表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_country_detail(self):
        """查询国家配置详情用例"""
        try:
            if not self.country_id:
                self.test_save_country()

            set_dict = {"id": self.country_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-国家配置表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试删除国家配置",
        description="验证GEN-国家配置表-删除服务功能",
        severity="normal",
        file_level_order=4,
        tags=["国家管理", "删除", "GEN_COUN_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_country(self):
        """删除国家配置用例"""
        try:
            if not self.country_id:
                self.test_save_country()

            set_dict = {"id": self.country_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-国家配置表-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 国家配置导入导出管理 ================
    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置标准导入",
        description="验证国家配置标准导入服务功能",
        severity="normal",
        file_level_order=5,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_import(self):
        """国家配置标准导入用例"""
        try:
            import_data = [
                {
                    "counCode": self.mock_util.generate_unique_code(tag="IMPORT_COUN"),
                    "counName": f"导入测试国家_{self.mock_util.get_timestamp()}",
                    "counNameEn": "Import Test Country",
                    "counPhoneCode": "+1",
                    "counCurrency": "USD"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="国家配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置标准导出",
        description="验证国家配置标准导出服务功能",
        severity="normal",
        file_level_order=6,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_export(self):
        """国家配置标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "nameEn", "type": "TEXT"},
                    {"name": "phoneCode", "type": "TEXT"},
                    {"name": "currency", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="国家配置标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置OSS导入任务",
        description="验证国家配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=7,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_oss_import_task(self):
        """国家配置OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_country_import.xlsx",
                "taskName": f"国家配置导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="国家配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置导出任务",
        description="验证国家配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_export_task(self):
        """国家配置导出任务用例"""
        try:
            set_dict = {
                "taskName": f"国家配置导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "nameEn", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="国家配置-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
