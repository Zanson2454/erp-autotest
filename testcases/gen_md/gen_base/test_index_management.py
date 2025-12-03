import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("指标中心管理")
class TestIndexManagement(GenMdBaseTest):
    """指标中心管理测试类 - 覆盖所有指标中心相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.index_id = None
        cls.logger.info("指标中心管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_index_md",
                where="index_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="指标中心管理",
        title="测试新增指标",
        description="验证GEN-指标中心-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["指标中心", "新增", "GEN_INDEX_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_index(self):
        """新增指标用例"""
        try:
            index_code = self.mock_util.generate_unique_code(tag="INDEX")
            index_name = f"测试指标_{self.mock_util.get_timestamp()}"

            set_dict = {
                "indexCode": index_code,
                "indexName": index_name,
                "remark": f"指标描述_{self.mock_util.get_timestamp()}"
            }
            
            response, index_id = self.standard_api_call(
                api_key="GEN-指标中心-保存服务",
                set_dict=set_dict,
                fields_to_filter=["code", "name", "remark"],
                store_id_as="index"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试调用取号规则",
        description="验证指标中心表-调用取号规则服务功能",
        severity="normal",
        file_level_order=2,
        tags=["指标中心", "取号规则", "GEN_INDEX_MD_INVOKE_CODE_RULE_SERVICE"]
    )
    def test_invoke_code_rule(self):
        """调用取号规则用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"indexId": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心表-调用取号规则服务",
                set_dict=set_dict,
                fields_to_filter=["indexId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查询指标分页列表",
        description="验证GEN-指标中心-查询分页服务功能",
        severity="normal",
        file_level_order=3,
        tags=["指标中心", "查询", "GEN_INDEX_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_index_page(self):
        """查询指标分页列表用例"""
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
                api_key="GEN-指标中心-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查询指标详情",
        description="验证GEN-指标中心-查询详情服务功能",
        severity="normal",
        file_level_order=4,
        tags=["指标中心", "查询", "GEN_INDEX_MD_DETAIL_ACTION_SERVICE"]
    )
    def test_query_index_detail(self):
        """查询指标详情用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"id": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试根据父ID查询下级列表",
        description="验证GEN-指标中心-根据父ID查询下级列表服务功能",
        severity="normal",
        file_level_order=5,
        tags=["指标中心", "查询", "GEN_INDEX_MD_QUERY_BY_PARENT_ACTION_SERVICE"]
    )
    def test_query_by_parent(self):
        """根据父ID查询下级列表用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"parentId": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-根据父ID查询下级列表服务",
                set_dict=set_dict,
                fields_to_filter=["parentId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查找树子数据",
        description="验证指标中心表-查找树子数据服务功能",
        severity="normal",
        file_level_order=6,
        tags=["指标中心", "树形结构", "GEN_INDEX_MD_FIND_TREE_CHILDREN_DATA_SERVICE"]
    )
    def test_find_tree_children(self):
        """查找树子数据用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"parentId": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心表-查找树子数据服务",
                set_dict=set_dict,
                fields_to_filter=["parentId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试启用指标",
        description="验证GEN-指标中心-启用服务功能",
        severity="normal",
        file_level_order=7,
        tags=["指标中心", "启用", "GEN_INDEX_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_index(self):
        """启用指标用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"id": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试禁用指标",
        description="验证GEN-指标中心-禁用服务功能",
        severity="normal",
        file_level_order=8,
        tags=["指标中心", "禁用", "GEN_INDEX_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_index(self):
        """禁用指标用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"id": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试删除指标",
        description="验证GEN-指标中心-删除服务功能",
        severity="critical",
        file_level_order=9,
        tags=["指标中心", "删除", "GEN_INDEX_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_index(self):
        """删除指标用例"""
        try:
            if not self.index_id:
                self.test_save_index()

            set_dict = {"id": self.index_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 指标中心导入管理 ================
    @case_decorator(
        story="指标中心导入管理",
        title="测试指标中心标准导入",
        description="验证指标中心表标准导入服务功能",
        severity="normal",
        file_level_order=10,
        tags=["指标中心", "导入", "GEN_INDEX_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_index_import(self):
        """指标中心标准导入用例"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_INDEX"),
                    "name": f"导入测试指标_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试指标描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="指标中心表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心任务管理",
        title="测试指标中心OSS导入任务",
        description="验证指标中心表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=11,
        tags=["指标中心", "任务管理", "GEN_INDEX_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_index_oss_import_task(self):
        """指标中心OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_index_import_file.xlsx",
                "taskName": f"指标中心导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="指标中心表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
