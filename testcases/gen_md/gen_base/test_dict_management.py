import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("数据字典管理")
class TestDictManagement(GenMdBaseTest):
    """数据字典管理测试类 - 覆盖所有数据字典类别相关服务"""
    
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
        cls.dict_id = None
        cls.dict_code = None
        cls.logger.info("数据字典管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_dict_item_cf",
                where="dict_head_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_dict_head_cf",
                where="code like %s",
                params=["AT_%"]
            )
 
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

        super().teardown_class()
    @case_decorator(
        story="数据字典管理",
        title="测试新增数据字典类别",
        description="验证GEN-数据字典类别-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["数据字典", "新增", "GEN_DICT_HEAD_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_dict(self):
        """新增数据字典类别用例"""
        try:
            dict_code = self.mock_util.generate_unique_code(tag="DICT")
            dict_name = f"测试字典_{self.mock_util.get_timestamp()}"

            set_dict = {
                "code": dict_code,
                "name": dict_name,
                "isSystem": False,
                "itemList":[
                    {
                        "code": self.mock_util.generate_unique_code(tag="DICT_ITEM"),
                        "name": f"测试字典项_{self.mock_util.get_timestamp()}",
                        "status": "ENABLED",
                        "sort": 1
                    }
                    ],
                "remark": f"字典描述_{self.mock_util.get_timestamp()}"
            }
            
            response, dict_id = self.standard_api_call(
                api_key="GEN-数据字典类别-保存服务",
                set_dict=set_dict,
                fields_to_filter=["code", "name", "remark"],
                store_id_as="dict"
            )
            
            self.dict_code = dict_code

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试查询数据字典类别分页列表",
        description="验证GEN-数据字典类别-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["数据字典", "查询", "GEN_DICT_HEAD_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_dict_page(self):
        """查询数据字典类别分页列表用例"""
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
                api_key="GEN-数据字典类别-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试查询数据字典类别详情",
        description="验证GEN-数据字典类别-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["数据字典", "查询", "GEN_DICT_HEAD_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_dict_detail(self):
        """查询数据字典类别详情用例"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            set_dict = {"id": self.dict_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-数据字典类别-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试启用数据字典类别",
        description="验证GEN-数据字典类别-启用服务功能",
        severity="normal",
        file_level_order=4,
        tags=["数据字典", "启用", "GEN_DICT_HEAD_CF_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_dict(self):
        """启用数据字典类别用例"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            set_dict = {"id": self.dict_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-数据字典类别-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试禁用数据字典类别",
        description="验证GEN-数据字典类别-禁用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["数据字典", "禁用", "GEN_DICT_HEAD_CF_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_dict(self):
        """禁用数据字典类别用例"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            set_dict = {"id": self.dict_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-数据字典类别-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试删除数据字典类别",
        description="验证GEN-数据字典类别-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["数据字典", "删除", "GEN_DICT_HEAD_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_dict(self):
        """删除数据字典类别用例"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            set_dict = {"id": self.dict_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-数据字典类别-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 数据字典导入导出管理 ================
    @case_decorator(
        story="数据字典导入导出管理",
        title="测试数据字典类别标准导入",
        description="验证数据字典类别标准导入服务功能",
        severity="normal",
        file_level_order=7,
        tags=["数据字典", "导入", "GEN_DICT_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_import(self):
        """数据字典类别标准导入用例"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_DICT"),
                    "name": f"导入测试字典_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试字典描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="数据字典类别标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典导入导出管理",
        title="测试数据字典类别标准导出",
        description="验证数据字典类别标准导出服务功能",
        severity="normal",
        file_level_order=8,
        tags=["数据字典", "导出", "GEN_DICT_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_export(self):
        """数据字典类别标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="数据字典类别标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典任务管理",
        title="测试数据字典类别OSS导入任务",
        description="验证数据字典类别-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=9,
        tags=["数据字典", "任务管理", "GEN_DICT_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_oss_import_task(self):
        """数据字典类别OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_dict_import_file.xlsx",
                "taskName": f"数据字典类别导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="数据字典类别-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典任务管理",
        title="测试数据字典类别导出任务",
        description="验证数据字典类别-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["数据字典", "任务管理", "GEN_DICT_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_export_task(self):
        """数据字典类别导出任务用例"""
        try:
            set_dict = {
                "taskName": f"数据字典类别导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="数据字典类别-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
