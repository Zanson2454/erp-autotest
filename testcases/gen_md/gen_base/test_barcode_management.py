import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("条码系统管理")
class TestBarcodeSystemManagement(GenMdBaseTest):
    """条码系统管理测试类 - 覆盖条码主数据、条码规则、条码字段等功能"""
    
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
        cls.barcode_md_id = None
        cls.barcode_md_code = None
        cls.barcode_rule_id = None
        cls.barcode_rule_code = None
        cls.barcode_field_id = None
        cls.barcode_field_code = None
        cls.logger.info("条码系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_barcode_md(self):
        obj_code = self.mock_util.generate_unique_code(tag="BARCODE_MD")
        set_dict = {
            "obj_code": obj_code,
            "type": "MAT",
            "label": obj_code,
            "create_label_amount": 1,
            "print_amt": 1,
            "print_time": self.mock_util.get_timestamp(),
            "status": "ENABLED"
        }
        response, barcode_md_id = self.standard_api_call(
            api_key="GEN-条码主数据-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "description"],
            store_id_as="barcode_md"
        )
        self.assert_util.assert_response_data(response)
        self.barcode_md_id = barcode_md_id
        self.barcode_md_code = obj_code
        return barcode_md_id

    def _ensure_save_barcode_md(self):
        if self.barcode_md_id:
            return self.barcode_md_id
        return self._create_barcode_md()

    def _create_barcode_field(self):
        biz_field_key = self.mock_util.generate_unique_code(tag="BARCODE_FIELD")
        biz_field_name = f"条码字段_{self.mock_util.get_timestamp()}"
        set_dict = {
            "bizFieldKey": biz_field_key,
            "bizFieldName": biz_field_name,
            "bizType": "MAT"
        }
        response, barcode_field_id = self.standard_api_call(
            api_key="GEN-条码字段-保存服务",
            set_dict=set_dict,
            fields_to_filter=["bizFieldKey", "bizFieldName", "bizType"],
            store_id_as="barcode_field"
        )
        self.assert_util.assert_response_data(response)
        self.barcode_field_id = barcode_field_id
        self.barcode_field_code = biz_field_key
        return barcode_field_id

    def _ensure_save_barcode_field(self):
        if self.barcode_field_id:
            return self.barcode_field_id
        return self._create_barcode_field()

    def _create_barcode_rule(self):
        if not self.barcode_field_id:
            self._ensure_save_barcode_field()
        prefix = self.mock_util.generate_unique_code(tag="BARCODE_RULE")
        rule_name = f"条码规则_{self.mock_util.get_timestamp()}"
        set_dict = {
            "prefix": prefix,
            "name": rule_name,
            "remark": f"条码规则描述_{self.mock_util.get_timestamp()}",
            "isUseBarcodeLabel": True,
            "delimiter": "-",
            "bizType": "MAT",
            "bizFieldId": {"id": self.barcode_field_id}
        }
        response, barcode_rule_id = self.standard_api_call(
            api_key="GEN-条码规则-保存服务",
            set_dict=set_dict,
            fields_to_filter=["prefix", "name", "remark", "isUseBarcodeLabel", "delimiter", "bizType", "bizFieldId"],
            store_id_as="barcode_rule"
        )
        self.assert_util.assert_response_data(response)
        self.barcode_rule_id = barcode_rule_id
        self.barcode_rule_code = prefix
        return barcode_rule_id

    def _ensure_save_barcode_rule(self):
        if self.barcode_rule_id:
            return self.barcode_rule_id
        return self._create_barcode_rule()

    # ================ 条码主数据管理 ================
    @case_decorator(
        story="条码主数据管理",
        title="测试新增条码主数据",
        description="验证GEN-条码主数据-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["条码主数据", "新增", "GEN_BARCODE_MD_SAVE_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_save_barcode_md(self):
        """新增条码主数据用例 - GEN_BARCODE_MD_SAVE_ACTION_SERVICE"""
        try:
            self._create_barcode_md()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据管理",
        title="测试查询条码主数据分页列表",
        description="验证GEN-条码主数据-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["条码主数据", "查询", "GEN_BARCODE_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_query_barcode_md_page(self):
        """查询条码主数据分页列表用例 - GEN_BARCODE_MD_QUERY_PAGE_ACTION_SERVICE"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码主数据-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据管理",
        title="测试查询条码主数据详情",
        description="验证GEN-条码主数据-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["条码主数据", "查询", "GEN_BARCODE_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_query_barcode_md_detail(self):
        """查询条码主数据详情用例 - GEN_BARCODE_MD_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.barcode_md_id:
                self._ensure_save_barcode_md()

            set_dict = {"id": self.barcode_md_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码主数据-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据管理",
        title="测试启用条码主数据",
        description="验证GEN-条码主数据-启用服务功能",
        severity="normal",
        file_level_order=4,
        tags=["条码主数据", "启用", "GEN_BARCODE_MD_ENABLED_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_enable_barcode_md(self):
        """启用条码主数据用例 - GEN_BARCODE_MD_ENABLED_ACTION_SERVICE"""
        try:
            if not self.barcode_md_id:
                self._ensure_save_barcode_md()

            set_dict = {"id": self.barcode_md_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码主数据-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据管理",
        title="测试禁用条码主数据",
        description="验证GEN-条码主数据-禁用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["条码主数据", "禁用", "GEN_BARCODE_MD_DISABLED_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_disable_barcode_md(self):
        """禁用条码主数据用例 - GEN_BARCODE_MD_DISABLED_ACTION_SERVICE"""
        try:
            if not self.barcode_md_id:
                self._ensure_save_barcode_md()

            set_dict = {"id": self.barcode_md_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码主数据-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据管理",
        title="测试删除条码主数据",
        description="验证GEN-条码主数据-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["条码主数据", "删除", "GEN_BARCODE_MD_DELETE_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_delete_barcode_md(self):
        """删除条码主数据用例 - GEN_BARCODE_MD_DELETE_ACTION_SERVICE"""
        try:
            if not self.barcode_md_id:
                self._ensure_save_barcode_md()

            set_dict = {"id": self.barcode_md_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码主数据-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码规则管理 ================
    @case_decorator(
        story="条码规则管理",
        title="测试新增条码规则",
        description="验证GEN-条码规则-保存服务功能",
        severity="blocker",
        file_level_order=7,
        smoke=True,
        tags=["条码规则", "新增", "GEN_BARCODE_RULE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_barcode_rule(self):
        """新增条码规则用例 - GEN_BARCODE_RULE_CF_SAVE_ACTION_SERVICE"""
        try:
            self._create_barcode_rule()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试查询条码规则分页列表",
        description="验证GEN-条码规则-查询分页服务功能",
        severity="normal",
        file_level_order=8,
        tags=["条码规则", "查询", "GEN_BARCODE_RULE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_barcode_rule_page(self):
        """查询条码规则分页列表用例 - GEN_BARCODE_RULE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "prefix", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码规则-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试查询条码规则详情",
        description="验证GEN-条码规则-查询详情服务功能",
        severity="normal",
        file_level_order=9,
        tags=["条码规则", "查询", "GEN_BARCODE_RULE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_barcode_rule_detail(self):
        """查询条码规则详情用例 - GEN_BARCODE_RULE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.barcode_rule_id:
                self._ensure_save_barcode_rule()

            set_dict = {"id": self.barcode_rule_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码规则-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则管理",
        title="测试删除条码规则",
        description="验证GEN-条码规则-删除服务功能",
        severity="critical",
        file_level_order=10,
        tags=["条码规则", "删除", "GEN_BARCODE_RULE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_barcode_rule(self):
        """删除条码规则用例 - GEN_BARCODE_RULE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.barcode_rule_id:
                self._ensure_save_barcode_rule()

            set_dict = {"id": self.barcode_rule_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码规则-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码字段管理 ================
    @case_decorator(
        story="条码字段管理",
        title="测试新增条码字段",
        description="验证GEN-条码字段-保存服务功能",
        severity="blocker",
        file_level_order=11,
        smoke=True,
        tags=["条码字段", "新增", "GEN_BARCODE_FILED_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_barcode_field(self):
        """新增条码字段用例 - GEN_BARCODE_FILED_CF_SAVE_ACTION_SERVICE"""
        try:
            self._create_barcode_field()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码字段管理",
        title="测试查询条码字段分页列表",
        description="验证GEN-条码字段-查询分页服务功能",
        severity="normal",
        file_level_order=12,
        tags=["条码字段", "查询", "GEN_BARCODE_FILED_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_barcode_field_page(self):
        """查询条码字段分页列表用例 - GEN_BARCODE_FILED_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "bizFieldKey", "type": "TEXT"},
                    {"name": "bizFieldName", "type": "TEXT"},
                    {"name": "bizType", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码字段-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码字段管理",
        title="测试查询条码字段详情",
        description="验证GEN-条码字段-查询详情服务功能",
        severity="normal",
        file_level_order=13,
        tags=["条码字段", "查询", "GEN_BARCODE_FILED_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_barcode_field_detail(self):
        """查询条码字段详情用例 - GEN_BARCODE_FILED_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.barcode_field_id:
                self._ensure_save_barcode_field()

            set_dict = {"id": self.barcode_field_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码字段-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码字段管理",
        title="测试删除条码字段",
        description="验证GEN-条码字段-删除服务功能",
        severity="critical",
        file_level_order=14,
        tags=["条码字段", "删除", "GEN_BARCODE_FILED_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_barcode_field(self):
        """删除条码字段用例 - GEN_BARCODE_FILED_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.barcode_field_id:
                self._ensure_save_barcode_field()

            set_dict = {"id": self.barcode_field_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-条码字段-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码主数据导入导出管理 ================
    @case_decorator(
        story="条码主数据导入导出管理",
        title="测试条码主数据标准导入",
        description="验证条码主数据标准导入服务功能",
        severity="normal",
        file_level_order=15,
        tags=["条码主数据", "导入", "GEN_BARCODE_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_md_import(self):
        """条码主数据标准导入用例 - GEN_BARCODE_MD_GEI_IMPORT_SERVICE"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_BARCODE_MD"),
                    "name": f"导入测试条码主数据_{self.mock_util.get_timestamp()}",
                    "description": "导入测试条码主数据描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="条码主数据标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据导入导出管理",
        title="测试条码主数据标准导出",
        description="验证条码主数据标准导出服务功能",
        severity="normal",
        file_level_order=16,
        tags=["条码主数据", "导出", "GEN_BARCODE_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_md_export(self):
        """条码主数据标准导出用例 - GEN_BARCODE_MD_GEI_EXPORT_SERVICE"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="条码主数据标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据任务管理",
        title="测试条码主数据OSS导入任务",
        description="验证条码主数据-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=17,
        tags=["条码主数据", "任务管理", "GEN_BARCODE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_md_oss_import_task(self):
        """条码主数据OSS导入任务用例 - GEN_BARCODE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            set_dict = {
                "fileKey": "test_barcode_md_import_file.xlsx",
                "taskName": f"条码主数据导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="条码主数据-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码主数据任务管理",
        title="测试条码主数据导出任务",
        description="验证条码主数据-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=18,
        tags=["条码主数据", "任务管理", "GEN_BARCODE_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_md_export_task(self):
        """条码主数据导出任务用例 - GEN_BARCODE_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            set_dict = {
                "taskName": f"条码主数据导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="条码主数据-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码规则导入导出管理 ================
    @case_decorator(
        story="条码规则导入导出管理",
        title="测试条码规则标准导入",
        description="验证条码规则标准导入服务功能",
        severity="normal",
        file_level_order=19,
        tags=["条码规则", "导入", "GEN_BARCODE_RULE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_rule_import(self):
        """条码规则标准导入用例 - GEN_BARCODE_RULE_CF_GEI_IMPORT_SERVICE"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_BARCODE_RULE"),
                    "name": f"导入测试条码规则_{self.mock_util.get_timestamp()}",
                    "description": "导入测试条码规则描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="条码规则标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则导入导出管理",
        title="测试条码规则标准导出",
        description="验证条码规则标准导出服务功能",
        severity="normal",
        file_level_order=20,
        tags=["条码规则", "导出", "GEN_BARCODE_RULE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_rule_export(self):
        """条码规则标准导出用例 - GEN_BARCODE_RULE_CF_GEI_EXPORT_SERVICE"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则任务管理",
        title="测试条码规则OSS导入任务",
        description="验证条码规则-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=21,
        tags=["条码规则", "任务管理", "GEN_BARCODE_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_rule_oss_import_task(self):
        """条码规则OSS导入任务用例 - GEN_BARCODE_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            set_dict = {
                "fileKey": "test_barcode_rule_import_file.xlsx",
                "taskName": f"条码规则导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则任务管理",
        title="测试条码规则导出任务",
        description="验证条码规则-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=22,
        tags=["条码规则", "任务管理", "GEN_BARCODE_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_rule_export_task(self):
        """条码规则导出任务用例 - GEN_BARCODE_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            set_dict = {
                "taskName": f"条码规则导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 条码规则允许业务字段管理 ================
    @case_decorator(
        story="条码规则允许业务字段管理",
        title="测试条码规则允许业务字段标准导入",
        description="验证条码规则允许业务字段标准导入服务功能",
        severity="normal",
        file_level_order=23,
        tags=["条码字段", "导入", "GEN_BARCODE_FIELD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_field_import(self):
        """条码规则允许业务字段标准导入用例 - GEN_BARCODE_FIELD_CF_GEI_IMPORT_SERVICE"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_BARCODE_FIELD"),
                    "name": f"导入测试条码规则允许业务字段_{self.mock_util.get_timestamp()}",
                    "description": "导入测试条码规则允许业务字段描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="条码规则允许业务字段标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则允许业务字段管理",
        title="测试条码规则允许业务字段标准导出",
        description="验证条码规则允许业务字段标准导出服务功能",
        severity="normal",
        file_level_order=24,
        tags=["条码字段", "导出", "GEN_BARCODE_FIELD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_field_export(self):
        """条码规则允许业务字段标准导出用例 - GEN_BARCODE_FIELD_CF_GEI_EXPORT_SERVICE"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则允许业务字段标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则允许业务字段任务管理",
        title="测试条码规则允许业务字段OSS导入任务",
        description="验证条码规则允许业务字段-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=25,
        tags=["条码字段", "任务管理", "GEN_BARCODE_FIELD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_field_oss_import_task(self):
        """条码规则允许业务字段OSS导入任务用例 - GEN_BARCODE_FIELD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            set_dict = {
                "fileKey": "test_barcode_field_import_file.xlsx",
                "taskName": f"条码规则允许业务字段导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则允许业务字段-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="条码规则允许业务字段任务管理",
        title="测试条码规则允许业务字段导出任务",
        description="验证条码规则允许业务字段-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=26,
        tags=["条码字段", "任务管理", "GEN_BARCODE_FIELD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_barcode_field_export_task(self):
        """条码规则允许业务字段导出任务用例 - GEN_BARCODE_FIELD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            set_dict = {
                "taskName": f"条码规则允许业务字段导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="条码规则允许业务字段-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
