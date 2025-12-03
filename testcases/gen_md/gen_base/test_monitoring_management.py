import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("监控管理")
class TestMonitoringManagement(GenMdBaseTest):
    """监控管理测试类 - 监控方案和监控预警结果信息管理"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.monitoring_id = None
        cls.monitoring_plan_id = None
        cls.monitoring_alert_id = None
        cls.logger.info("监控管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_monitoring_md",
                where="monitoring_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_monitoring_plan_info_md",
                where="plan_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_monitoring_alert_result_md",
                where="alert_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="监控管理",
        title="测试新增监控管理",
        description="验证新增监控管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["监控管理", "新增"]
    )
    def test_save_monitoring(self):
        """新增监控管理用例"""
        try:
            monitoring_code = self.mock_util.generate_unique_code(tag="MONITORING")
            monitoring_name = f"测试监控_{self.mock_util.get_timestamp()}"

            set_dict = {
                "monitoringCode": monitoring_code,
                "monitoringName": monitoring_name,
                "remark": f"监控描述_{self.mock_util.get_timestamp()}"
            }
            
            response, monitoring_id = self.standard_api_call(
                api_key="GEN-监控管理-保存服务",
                set_dict=set_dict,
                fields_to_filter=["code", "name", "remark"],
                store_id_as="monitoring"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控管理",
        title="测试查询监控管理列表",
        description="验证监控管理列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["监控管理", "查询"]
    )
    def test_query_monitoring_list(self):
        """查询监控管理列表用例"""
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
                api_key="GEN-监控管理-查询列表服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控管理",
        title="测试查询监控管理详情",
        description="验证监控管理详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["监控管理", "查询"]
    )
    def test_query_monitoring_detail(self):
        """查询监控管理详情用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            set_dict = {"id": self.monitoring_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控管理-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控管理",
        title="测试删除监控管理",
        description="验证删除监控管理功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["监控管理", "删除"]
    )
    def test_delete_monitoring(self):
        """删除监控管理用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            set_dict = {"id": self.monitoring_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控管理-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控方案管理 ================
    @case_decorator(
        story="监控方案管理",
        title="测试监控方案查询分页服务",
        description="验证监控方案-查询分页服务功能",
        severity="normal",
        file_level_order=5,
        tags=["监控方案管理", "查询", "GEN_MONITORING_PLAN_INFO_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_monitoring_plan_page(self):
        """监控方案查询分页服务用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "planCode", "type": "TEXT"},
                    {"name": "planName", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控方案-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控方案管理",
        title="测试监控方案启用服务",
        description="验证监控方案-启用服务功能",
        severity="normal",
        file_level_order=6,
        tags=["监控方案管理", "启用", "GEN_MONITORING_PLAN_INFO_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_monitoring_plan(self):
        """监控方案启用服务用例"""
        try:
            if not self.monitoring_plan_id:
                # 创建示例监控方案
                plan_code = self.mock_util.generate_unique_code(tag="PLAN")
                set_dict = {
                    "planCode": plan_code,
                    "planName": f"测试监控方案_{self.mock_util.get_timestamp()}",
                    "remark": "测试监控方案描述"
                }
                response, self.monitoring_plan_id = self.standard_api_call(
                    api_key="GEN-监控方案-保存服务",
                    set_dict=set_dict,
                    fields_to_filter=["planCode", "planName", "remark"],
                    store_id_as="monitoring_plan"
                )

            set_dict = {"id": self.monitoring_plan_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控方案-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控方案管理",
        title="测试监控方案删除服务",
        description="验证监控方案-删除服务功能",
        severity="normal",
        file_level_order=7,
        tags=["监控方案管理", "删除", "GEN_MONITORING_PLAN_INFO_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_monitoring_plan(self):
        """监控方案删除服务用例"""
        try:
            if not self.monitoring_plan_id:
                # 创建示例监控方案
                plan_code = self.mock_util.generate_unique_code(tag="PLAN")
                set_dict = {
                    "planCode": plan_code,
                    "planName": f"测试监控方案_{self.mock_util.get_timestamp()}",
                    "remark": "测试监控方案描述"
                }
                response, self.monitoring_plan_id = self.standard_api_call(
                    api_key="GEN-监控方案-保存服务",
                    set_dict=set_dict,
                    fields_to_filter=["planCode", "planName", "remark"],
                    store_id_as="monitoring_plan"
                )

            set_dict = {"id": self.monitoring_plan_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控方案-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控预警结果管理 ================
    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息保存服务",
        description="验证监控预警结果信息-保存服务功能",
        severity="normal",
        file_level_order=8,
        tags=["监控预警结果管理", "保存", "GEN_MONITORING_ALERT_RESULT_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_monitoring_alert_result(self):
        """监控预警结果信息保存服务用例"""
        try:
            alert_code = self.mock_util.generate_unique_code(tag="ALERT")
            alert_name = f"测试预警结果_{self.mock_util.get_timestamp()}"

            set_dict = {
                "alertCode": alert_code,
                "alertName": alert_name,
                "remark": f"预警结果描述_{self.mock_util.get_timestamp()}"
            }
            
            response, alert_id = self.standard_api_call(
                api_key="GEN-监控预警结果信息-保存服务",
                set_dict=set_dict,
                fields_to_filter=["alertCode", "alertName", "remark"],
                store_id_as="monitoring_alert"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息查询详情服务",
        description="验证监控预警结果信息-查询详情服务功能",
        severity="normal",
        file_level_order=9,
        tags=["监控预警结果管理", "查询", "GEN_MONITORING_ALERT_RESULT_MD_DETAIL_ACTION_SERVICE"]
    )
    def test_query_monitoring_alert_result_detail(self):
        """监控预警结果信息查询详情服务用例"""
        try:
            if not self.monitoring_alert_id:
                self.test_save_monitoring_alert_result()

            set_dict = {"id": self.monitoring_alert_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控预警结果信息-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息删除服务",
        description="验证监控预警结果信息-删除服务功能",
        severity="normal",
        file_level_order=10,
        tags=["监控预警结果管理", "删除", "GEN_MONITORING_ALERT_RESULT_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_monitoring_alert_result(self):
        """监控预警结果信息删除服务用例"""
        try:
            if not self.monitoring_alert_id:
                self.test_save_monitoring_alert_result()

            set_dict = {"id": self.monitoring_alert_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-监控预警结果信息-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控方案导入导出管理 ================
    @case_decorator(
        story="监控方案导入导出管理",
        title="测试监控方案标准导入服务",
        description="验证监控方案标准导入服务功能",
        severity="normal",
        file_level_order=11,
        tags=["监控方案管理", "导入", "GEN_MONITORING_PLAN_INFO_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_import(self):
        """监控方案标准导入服务用例"""
        try:
            import_data = [
                {
                    "planCode": self.mock_util.generate_unique_code(tag="IMPORT_PLAN"),
                    "planName": f"导入测试监控方案_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试监控方案描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="监控方案标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控方案导入导出管理",
        title="测试监控方案标准导出服务",
        description="验证监控方案标准导出服务功能",
        severity="normal",
        file_level_order=12,
        tags=["监控方案管理", "导出", "GEN_MONITORING_PLAN_INFO_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_export(self):
        """监控方案标准导出服务用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "planCode", "type": "TEXT"},
                    {"name": "planName", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="监控方案标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果导入导出管理",
        title="测试监控预警结果信息标准导入服务",
        description="验证监控预警结果信息标准导入服务功能",
        severity="normal",
        file_level_order=13,
        tags=["监控预警结果管理", "导入", "GEN_MONITORING_ALERT_RESULT_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_import(self):
        """监控预警结果信息标准导入服务用例"""
        try:
            import_data = [
                {
                    "alertCode": self.mock_util.generate_unique_code(tag="IMPORT_ALERT"),
                    "alertName": f"导入测试预警结果_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试预警结果描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="监控预警结果信息标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果导入导出管理",
        title="测试监控预警结果信息标准导出服务",
        description="验证监控预警结果信息标准导出服务功能",
        severity="normal",
        file_level_order=14,
        tags=["监控预警结果管理", "导出", "GEN_MONITORING_ALERT_RESULT_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_export(self):
        """监控预警结果信息标准导出服务用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "alertCode", "type": "TEXT"},
                    {"name": "alertName", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="监控预警结果信息标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控方案任务管理 ================
    @case_decorator(
        story="监控方案任务管理",
        title="测试监控方案OSS导入任务",
        description="验证监控方案-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=15,
        tags=["监控方案管理", "任务管理", "GEN_MONITORING_PLAN_INFO_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_oss_import_task(self):
        """监控方案OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_monitoring_plan_import.xlsx",
                "taskName": f"监控方案导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="监控方案-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控方案任务管理",
        title="测试监控方案导出任务",
        description="验证监控方案-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=16,
        tags=["监控方案管理", "任务管理", "GEN_MONITORING_PLAN_INFO_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_export_task(self):
        """监控方案导出任务用例"""
        try:
            set_dict = {
                "taskName": f"监控方案导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "planCode", "type": "TEXT"},
                        {"name": "planName", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="监控方案-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控预警结果任务管理 ================
    @case_decorator(
        story="监控预警结果任务管理",
        title="测试监控预警结果信息OSS导入任务",
        description="验证监控预警结果信息-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=17,
        tags=["监控预警结果管理", "任务管理", "GEN_MONITORING_ALERT_RESULT_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_oss_import_task(self):
        """监控预警结果信息OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_alert_result_import.xlsx",
                "taskName": f"监控预警结果导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="监控预警结果信息-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果任务管理",
        title="测试监控预警结果信息导出任务",
        description="验证监控预警结果信息-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=18,
        tags=["监控预警结果管理", "任务管理", "GEN_MONITORING_ALERT_RESULT_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_export_task(self):
        """监控预警结果信息导出任务用例"""
        try:
            set_dict = {
                "taskName": f"监控预警结果导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "alertCode", "type": "TEXT"},
                        {"name": "alertName", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="监控预警结果信息-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
