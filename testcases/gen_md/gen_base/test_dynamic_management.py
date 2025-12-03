import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("动态表单管理")
class TestDynamicManagement(GenMdBaseTest):
    """动态表单管理测试类 - 覆盖所有动态表单相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.template_id = None
        cls.logger.info("动态表单管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_dynamic_form_template_md",
                where="template_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="动态表单管理",
        title="测试创建动态表单模板",
        description="验证GEN-动态表单-创建修改动态表单模板服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,          
        tags=["动态表单", "创建", "GEN_DYNAMIC_CREATE_UPDATE_TEMPLATE_SERVICE"]
    )
    def test_create_template(self):
        """创建动态表单模板用例"""
        try:
            template_code = self.mock_util.generate_unique_code(tag="TEMPLATE")
            template_name = f"测试表单模板_{self.mock_util.get_timestamp()}"

            set_dict = {
                "templateCode": template_code,
                "templateName": template_name,
                "formJson": {
                    "fields": [
                        {"id": "field1", "name": "测试字段1", "type": "text"},
                        {"id": "field2", "name": "测试字段2", "type": "number"}
                    ]
                },
                "remark": f"表单模板描述_{self.mock_util.get_timestamp()}"
            }
            
            response, template_id = self.standard_api_call(
                api_key="GEN-动态表单-创建修改动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["templateCode", "templateName", "formJson", "remark"],
                store_id_as="template"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试创建修改动态表单模板（备用服务）",
        description="验证GEN-创建修改动态表单模板服务功能",
        severity="normal",
        file_level_order=2,
        tags=["动态表单", "创建修改", "GEN_CREATE_DYNAMIC_FORM_TEMPLATE_SERVICE"]
    )
    @pytest.mark.skip(reason="dynamic_form场景.菜单未引用,业务用不上")
    def test_create_dynamic_form_template(self):
        """创建修改动态表单模板（备用服务）用例"""
        try:
            set_dict = {
                "templateCode": self.mock_util.generate_unique_code(tag="TEMPLATE_BACKUP"),
                "templateName": f"备用模板_{self.mock_util.get_timestamp()}",
                "formJson": {"fields": [{"id": "backup", "name": "备份字段", "type": "text"}]}
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-创建修改动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["templateCode", "templateName", "formJson"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试分页查询动态表单模板",
        description="验证GEN-动态表单-分页查询动态表单模板服务功能",
        severity="normal",
        file_level_order=3,
        tags=["动态表单", "查询", "GEN_DYNAMIC_PAGING_TEMPLATE_SERVICE"]
    )
    def test_paging_template(self):
        """分页查询动态表单模板用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "templateCode", "type": "TEXT"},
                    {"name": "templateName", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-分页查询动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试根据ID查询动态表单模板",
        description="验证GEN-动态表单-根据id查询动态表单模板服务功能",
        severity="normal",
        file_level_order=4,
        tags=["动态表单", "查询", "GEN_DYNAMIC_FIND_BY_ID_TEMPLATE_SERVICE"]
    )
    def test_find_by_id_template(self):
        """根据ID查询动态表单模板用例"""
        try:
            if not self.template_id:
                self.test_create_template()

            set_dict = {"id": self.template_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-根据id查询动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试根据IDs查询动态表单模板集合",
        description="验证GEN-动态表单-根据ids查询动态表单模板集合服务功能",
        severity="normal",
        file_level_order=5,
        tags=["动态表单", "批量查询", "GEN_DYNAMIC_FIND_BY_IDS_TEMPLATE_SERVICE"]
    )
    def test_find_by_ids_template(self):
        """根据IDs查询动态表单模板集合用例"""
        try:
            if not self.template_id:
                self.test_create_template()

            set_dict = {"ids": [self.template_id]}
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-根据ids查询动态表单模板集合服务",
                set_dict=set_dict,
                fields_to_filter=["ids"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试启用动态表单模板",
        description="验证GEN-动态表单-启用动态表单模板服务功能",
        severity="normal",
        file_level_order=6,
        tags=["动态表单", "启用", "GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE"]
    )
    def test_enable_template(self):
        """启用动态表单模板用例"""
        try:
            if not self.template_id:
                self.test_create_template()

            set_dict = {"id": self.template_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-启用动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试禁用动态表单模板",
        description="验证GEN-动态表单-禁用动态表单模板服务功能",
        severity="normal",
        file_level_order=7,
        tags=["动态表单", "禁用", "GEN_DYNAMIC_DISABLE_TEMPLATE_SERVICE"]
    )
    def test_disable_template(self):
        """禁用动态表单模板用例"""
        try:
            if not self.template_id:
                self.test_create_template()

            set_dict = {"id": self.template_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-禁用动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试删除动态表单模板",
        description="验证GEN-动态表单-删除动态表单模板服务功能",
        severity="critical",
        file_level_order=8,
        tags=["动态表单", "删除", "GEN_DYNAMIC_DELETE_TEMPLATE_SERVICE"]
    )
    def test_delete_template(self):
        """删除动态表单模板用例"""
        try:
            if not self.template_id:
                self.test_create_template()

            set_dict = {"id": self.template_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-动态表单-删除动态表单模板服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 动态表单导入导出管理 ================
    @case_decorator(
        story="动态表单导入导出管理",
        title="测试动态表单模板标准导入",
        description="验证动态表单模板类标准导入服务功能",
        severity="normal",
        file_level_order=9,
        tags=["动态表单", "导入", "GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_import(self):
        """动态表单模板标准导入用例"""
        try:
            import_data = [
                {
                    "templateCode": self.mock_util.generate_unique_code(tag="IMPORT_TEMPLATE"),
                    "templateName": f"导入测试模板_{self.mock_util.get_timestamp()}",
                    "formJson": {"fields": [{"id": "import_field", "name": "导入字段", "type": "text"}]}
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="动态表单模板类标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单导入导出管理",
        title="测试动态表单模板标准导出",
        description="验证动态表单模板类标准导出服务功能",
        severity="normal",
        file_level_order=10,
        tags=["动态表单", "导出", "GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_export(self):
        """动态表单模板标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "templateCode", "type": "TEXT"},
                    {"name": "templateName", "type": "TEXT"},
                    {"name": "formJson", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="动态表单模板类标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单任务管理",
        title="测试动态表单模板OSS导入任务",
        description="验证动态表单模板类-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=11,
        tags=["动态表单", "任务管理", "GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_oss_import_task(self):
        """动态表单模板OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_template_import.xlsx",
                "taskName": f"动态表单模板导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="动态表单模板类-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单任务管理",
        title="测试动态表单模板导出任务",
        description="验证动态表单模板类-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=12,
        tags=["动态表单", "任务管理", "GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_export_task(self):
        """动态表单模板导出任务用例"""
        try:
            set_dict = {
                "taskName": f"动态表单模板导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "templateCode", "type": "TEXT"},
                        {"name": "templateName", "type": "TEXT"},
                        {"name": "formJson", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="动态表单模板类-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
