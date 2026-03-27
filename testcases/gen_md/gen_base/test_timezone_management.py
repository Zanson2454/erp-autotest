import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("时区管理")
class TestTimezoneManagement(GenMdBaseTest):
    """时区管理测试类 - 覆盖所有时区配置相关服务"""
    
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
        # 数据存储
        cls.timezone_id = None
        cls.timezone_code = None
        cls.logger.info("时区管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_timezone_type_cf",
                where="timezone_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="时区配置管理",
        title="测试新增时区配置",
        description="验证GEN-时区配置-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["时区管理", "新增", "GEN_TIMEZONE_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_timezone(self):
        """新增时区配置用例"""
        try:
            timezone_code = self.mock_util.generate_unique_code(tag="TIMEZONE")
            timezone_name = f"测试时区_{self.mock_util.get_timestamp()}"

            set_dict = {
                "timezoneCode": timezone_code,
                "timezoneName": timezone_name,
                "offset": "+08:00",
                "remark": f"时区描述_{self.mock_util.get_timestamp()}"
            }
            
            response, timezone_id = self.standard_api_call(
                api_key="GEN-时区配置-保存服务",
                set_dict=set_dict,
                fields_to_filter=["timezoneCode", "timezoneName", "offset", "remark"],
                store_id_as="timezone"
            )
            
            self.timezone_code = timezone_code

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试查询时区配置分页列表",
        description="验证GEN-时区配置-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_timezone_page(self):
        """查询时区配置分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "offset", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-时区配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试查询时区配置详情",
        description="验证GEN-时区配置-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_timezone_detail(self):
        """查询时区配置详情用例"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            set_dict = {"id": self.timezone_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-时区配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试删除时区配置",
        description="验证GEN-时区配置-删除服务功能",
        severity="normal",
        file_level_order=4,
        tags=["时区管理", "删除", "GEN_TIMEZONE_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_timezone(self):
        """删除时区配置用例"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            set_dict = {"id": self.timezone_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-时区配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 时区配置导入导出管理 ================
    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置标准导入",
        description="验证时区配置标准导入服务功能",
        severity="normal",
        file_level_order=5,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_import(self):
        """时区配置标准导入用例"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_TIMEZONE"),
                    "name": f"导入测试时区_{self.mock_util.get_timestamp()}",
                    "offset": "+08:00",
                    "remark": "导入测试时区描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="时区配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置标准导出",
        description="验证时区配置标准导出服务功能",
        severity="normal",
        file_level_order=6,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_export(self):
        """时区配置标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "offset", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="时区配置标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置OSS导入任务",
        description="验证时区配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=7,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_oss_import_task(self):
        """时区配置OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_timezone_import.xlsx",
                "taskName": f"时区配置导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="时区配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置导出任务",
        description="验证时区配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_export_task(self):
        """时区配置导出任务用例"""
        try:
            set_dict = {
                "taskName": f"时区配置导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "offset", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="时区配置-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
