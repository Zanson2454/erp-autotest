import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("工作日日历管理")
class TestWcManagement(GenMdBaseTest):
    """工作日日历管理测试类 - 覆盖所有工作日日历相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.wc_head_id = None
        cls.wc_head_code = None
        cls.logger.info("工作日日历管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_wc_head_cf",
                where="wc_head_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="工作日日历管理",
        title="测试新增工作日日历",
        description="验证GEN-工作日日历头表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["工作日日历", "新增", "GEN_WC_HEAD_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_wc(self):
        """新增工作日日历用例"""
        try:
            wc_head_code = self.mock_util.generate_unique_code(tag="WC")
            wc_head_name = f"测试工作日历_{self.mock_util.get_timestamp()}"

            set_dict = {
                "wcHeadCode": wc_head_code,
                "wcHeadName": wc_head_name,
                "remark": f"工作日历描述_{self.mock_util.get_timestamp()}",
                "effectiveDate": self.mock_util.get_timestamp(),
                "expireDate": self.mock_util.get_timestamp() + 365 * 24 * 3600  # 一年后
            }
            
            response, wc_head_id = self.standard_api_call(
                api_key="GEN-工作日日历头表-保存服务",
                set_dict=set_dict,
                fields_to_filter=["wcHeadCode", "wcHeadName", "remark", "effectiveDate", "expireDate"],
                store_id_as="wc_head"
            )
            
            self.wc_head_code = wc_head_code

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试工作日日历生成",
        description="验证GEN-工作日日历头表-日历生成服务功能",
        severity="critical",
        file_level_order=2,
        tags=["工作日日历", "日历生成", "GEN_WC_GENERATE_ACTION_SERVICE"]
    )
    def test_generate_wc(self):
        """工作日日历生成本例"""
        try:
            if not self.wc_head_id:
                self.test_save_wc()

            set_dict = {
                "wcHeadId": self.wc_head_id,
                "generateType": "MONTHLY",
                "startDate": self.mock_util.get_timestamp(),
                "endDate": self.mock_util.get_timestamp() + 30 * 24 * 3600  # 30天后
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-日历生成服务",
                set_dict=set_dict,
                fields_to_filter=["wcHeadId", "generateType", "startDate", "endDate"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试查询工作日日历分页列表",
        description="验证GEN-工作日日历头表-查询分页服务功能",
        severity="normal",
        file_level_order=3,
        tags=["工作日日历", "查询", "GEN_WC_HEAD_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_wc_page(self):
        """查询工作日日历分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试查询工作日日历详情",
        description="验证GEN-工作日日历头表-查询详情服务功能",
        severity="normal",
        file_level_order=4,
        tags=["工作日日历", "查询", "GEN_WC_HEAD_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_wc_detail(self):
        """查询工作日日历详情用例"""
        try:
            if not self.wc_head_id:
                self.test_save_wc()

            set_dict = {"id": self.wc_head_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试启用工作日日历",
        description="验证GEN-工作日日历头表-启用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["工作日日历", "启用", "GEN_WC_HEAD_CF_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_wc(self):
        """启用工作日日历用例"""
        try:
            if not self.wc_head_id:
                self.test_save_wc()

            set_dict = {"id": self.wc_head_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试停用工作日日历",
        description="验证GEN-工作日日历头表-停用服务功能",
        severity="normal",
        file_level_order=6,
        tags=["工作日日历", "停用", "GEN_WC_HEAD_CF_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_wc(self):
        """停用工作日日历用例"""
        try:
            if not self.wc_head_id:
                self.test_save_wc()

            set_dict = {"id": self.wc_head_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-停用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历管理",
        title="测试删除工作日日历",
        description="验证GEN-工作日日历头表-删除服务功能",
        severity="critical",
        file_level_order=7,
        tags=["工作日日历", "删除", "GEN_WC_HEAD_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_wc(self):
        """删除工作日日历用例"""
        try:
            if not self.wc_head_id:
                self.test_save_wc()

            set_dict = {"id": self.wc_head_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-工作日日历头表-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 工作日日历导入导出管理 ================
    @case_decorator(
        story="工作日日历导入导出管理",
        title="测试工作日日历标准导入",
        description="验证工作日日历头表标准导入服务功能",
        severity="normal",
        file_level_order=8,
        tags=["工作日日历", "导入", "GEN_WC_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_wc_import(self):
        """工作日日历标准导入用例"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_WC"),
                    "name": f"导入测试工作日历_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试工作日历描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="工作日日历头表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历导入导出管理",
        title="测试工作日日历标准导出",
        description="验证工作日日历头表标准导出服务功能",
        severity="normal",
        file_level_order=9,
        tags=["工作日日历", "导出", "GEN_WC_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_wc_export(self):
        """工作日日历标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="工作日日历头表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历任务管理",
        title="测试工作日日历OSS导入任务",
        description="验证工作日日历头表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=10,
        tags=["工作日日历", "任务管理", "GEN_WC_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_wc_oss_import_task(self):
        """工作日日历OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_wc_import_file.xlsx",
                "taskName": f"工作日日历导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="工作日日历头表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工作日日历任务管理",
        title="测试工作日日历导出任务",
        description="验证工作日日历头表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=11,
        tags=["工作日日历", "任务管理", "GEN_WC_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_wc_export_task(self):
        """工作日日历导出任务用例"""
        try:
            set_dict = {
                "taskName": f"工作日日历导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="工作日日历头表-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
