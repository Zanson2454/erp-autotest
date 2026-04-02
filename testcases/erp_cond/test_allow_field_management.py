import allure
import pytest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from . import ErpCondBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from typing import Any


@allure.epic("ERP条件模块")
@allure.feature("允许字段管理")
class TestAllowFieldManagement(ErpCondBaseTest):
    """允许字段管理测试类 - 覆盖允许字段表相关服务"""
    
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
        cls.allow_field_id = None
        cls.logger.info("允许字段管理测试类初始化完成")
        
        # 初始化依赖数据，如果需要
        if cls.cond_cache_data:
            # 示例：如果需要模型ID等依赖
            pass

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="allow_field_item_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

        super().teardown_class()
    # ================ 允许字段创建 ================
    @case_decorator(
        story="允许字段管理",
        title="测试保存主数据",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["允许字段", "创建", "GEN_ALLOW_FIELD_ITEM_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_save_master_data(self):
        """保存主数据用例 - GEN_ALLOW_FIELD_ITEM_CF_MASTER_DATA_SAVE_DATA_SERVICE"""
        try:
            # 准备测试数据
            code = self.mock_util.generate_unique_code(tag="AF")
            name = f"测试允许字段_{self.mock_util.get_timestamp()}"
            
            set_dict = {
                "code": code,
                "name": name,
                "modelId": 1,  # 假设模型ID，需要根据实际调整
                "fieldType": "TEXT"
            }
            fields_to_filter = ["code", "name", "modelId", "fieldType"]
            
            # 标准化API调用
            response, extracted_data = self.standard_api_call(
                api_key="允许字段表-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="allow_field"
            )
            
            # 保存ID
            self.allow_field_id = extracted_data
            self.assert_util.assert_by_operator(self.allow_field_id, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 允许字段查询 ================
    @case_decorator(
        story="允许字段管理",
        title="测试查询允许模型下的字段",
        description="验证GEN_ALLOW_FIELD_ITEM_LIST__SERVICE功能",
        severity="critical",
        file_level_order=2,
        tags=["允许字段", "查询", "GEN_ALLOW_FIELD_ITEM_LIST__SERVICE"]
    )
    def test_query_model_fields(self):
        """查询允许模型下的字段用例 - GEN_ALLOW_FIELD_ITEM_LIST__SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {
                "modelId": 1  # 假设模型ID
            }
            fields_to_filter = ["modelId"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-查询允许模型下的字段",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试分页数据查询",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_PAGING_DATA_SERVICE功能",
        severity="critical",
        file_level_order=3,
        tags=["允许字段", "分页查询", "GEN_ALLOW_FIELD_ITEM_CF_PAGING_DATA_SERVICE"]
    )
    def test_paging_query(self):
        """分页查询用例 - GEN_ALLOW_FIELD_ITEM_CF_PAGING_DATA_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试根据ID查找数据",
        description="验证GEN_ALLOW_FIELD_ITEM_VO_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=4,
        tags=["允许字段", "详情查询", "GEN_ALLOW_FIELD_ITEM_VO_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_by_id(self):
        """根据ID查找用例 - GEN_ALLOW_FIELD_ITEM_VO_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段_普通模型-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 允许字段更新 ================
    @case_decorator(
        story="允许字段管理",
        title="测试保存数据服务",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_SAVE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=5,
        tags=["允许字段", "更新", "GEN_ALLOW_FIELD_ITEM_CF_SAVE_DATA_SERVICE"]
    )
    def test_save_data(self):
        """保存数据用例 - GEN_ALLOW_FIELD_ITEM_CF_SAVE_DATA_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {
                "id": self.allow_field_id,
                "name": f"更新允许字段_{self.mock_util.get_timestamp()}"
            }
            fields_to_filter = ["id", "name"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-保存数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 允许字段导出 ================
    @case_decorator(
        story="允许字段管理",
        title="测试普通模型分页数据服务",
        description="验证GEN_ALLOW_FIELD_ITEM_VO_PAGING_DATA_SERVICE功能 (用于导出)",
        severity="normal",
        file_level_order=6,
        tags=["允许字段", "导出查询", "GEN_ALLOW_FIELD_ITEM_VO_PAGING_DATA_SERVICE"]
    )
    def test_vo_paging_for_export(self):
        """普通模型分页用于导出 - GEN_ALLOW_FIELD_ITEM_VO_PAGING_DATA_SERVICE"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段_普通模型-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试允许字段模型选择分页",
        description="验证GEN_ALLOWD_MODEL_SELECT_VO_PAGING_DATA_SERVICE功能 (用于导出配置)",
        severity="normal",
        file_level_order=7,
        tags=["允许字段", "模型选择", "GEN_ALLOWD_MODEL_SELECT_VO_PAGING_DATA_SERVICE"]
    )
    def test_model_select_paging(self):
        """模型选择分页 - GEN_ALLOWD_MODEL_SELECT_VO_PAGING_DATA_SERVICE"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段模型选择-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试标准导出",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE (导出部分)",
        severity="normal",
        file_level_order=8,
        tags=["允许字段", "导出", "GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export(self):
        """标准导出用例 - GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("允许字段表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "fieldType", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="允许字段表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 允许字段导入 (跳过) ================
    @case_decorator(
        story="允许字段管理",
        title="测试标准导入",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE功能",
        severity="normal",
        file_level_order=9,
        tags=["允许字段", "导入", "GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import(self):
        """标准导入用例 - GEN_ALLOW_FIELD_ITEM_CF_GEI_IMPORT_SERVICE"""
        try:
            # 导入逻辑类似导出，但需要文件上传，跳过
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试OSS导入任务",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        file_level_order=10,
        tags=["允许字段", "导入任务", "GEN_ALLOW_FIELD_ITEM_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_oss_import_task(self):
        """OSS导入任务用例 - GEN_ALLOW_FIELD_ITEM_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            # OSS导入复杂，跳过
            a.text("OSS导入任务需要OSS配置，暂时跳过", "跳过说明")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试导入任务管理",
        description="验证导入相关服务",
        severity="normal",
        file_level_order=11,
        tags=["允许字段", "导入"]
    )
    @pytest.mark.skip(reason="导入任务配置复杂，暂时跳过")
    def test_import_task_management(self):
        """导入任务管理用例"""
        try:
            a.text("导入任务配置复杂，暂时跳过", "跳过说明")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 允许字段删除 ================
    @case_decorator(
        story="允许字段管理",
        title="测试根据ID删除",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=12,
        tags=["允许字段", "删除", "GEN_ALLOW_FIELD_ITEM_CF_DELETE_DATA_BY_ID_SERVICE"]
    )
    def test_delete_by_id(self):
        """根据ID删除用例 - GEN_ALLOW_FIELD_ITEM_CF_DELETE_DATA_BY_ID_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.allow_field_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 其他服务 (复制、树查询等) ================
    @case_decorator(
        story="允许字段管理",
        title="测试复制数据转换",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_COPY_DATA_CONVERTER_SERVICE功能",
        severity="normal",
        file_level_order=13,
        tags=["允许字段", "复制", "GEN_ALLOW_FIELD_ITEM_CF_COPY_DATA_CONVERTER_SERVICE"]
    )
    @pytest.mark.skip(reason="复制服务依赖特定业务场景，暂时跳过")
    def test_copy_data_converter(self):
        """复制数据转换用例 - GEN_ALLOW_FIELD_ITEM_CF_COPY_DATA_CONVERTER_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"sourceId": self.allow_field_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试复制数据转换子服务",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_COPY_DATA_CONVERTER_SERVICE_CHILD功能",
        severity="normal",
        file_level_order=14,
        tags=["允许字段", "复制子服务", "GEN_ALLOW_FIELD_ITEM_CF_COPY_DATA_CONVERTER_SERVICE_CHILD"]
    )
    @pytest.mark.skip(reason="子服务依赖父服务，暂时跳过")
    def test_copy_data_converter_child(self):
        """复制数据转换子服务用例"""
        try:
            a.text("子服务依赖父服务，暂时跳过", "跳过说明")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试查找树子数据",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_FIND_TREE_CHILDREN_DATA_SERVICE功能",
        severity="normal",
        file_level_order=15,
        tags=["允许字段", "树查询", "GEN_ALLOW_FIELD_ITEM_CF_FIND_TREE_CHILDREN_DATA_SERVICE"]
    )
    def test_find_tree_children(self):
        """查找树子数据用例 - GEN_ALLOW_FIELD_ITEM_CF_FIND_TREE_CHILDREN_DATA_SERVICE"""
        try:
            set_dict = {"parentId": None}  # 根节点
            fields_to_filter = ["parentId"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-查找树子数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试CF根据ID查找",
        description="验证GEN_ALLOW_FIELD_ITEM_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=16,
        tags=["允许字段", "详情查询CF", "GEN_ALLOW_FIELD_ITEM_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_cf_find_by_id(self):
        """CF根据ID查找用例 - GEN_ALLOW_FIELD_ITEM_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段表-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试允许字段删除",
        description="验证allow_field_delete功能",
        severity="critical",
        file_level_order=17,
        tags=["允许字段", "删除", "allow_field_delete"]
    )
    def test_allow_field_delete(self):
        """允许字段删除用例 - allow_field_delete"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段删除字段",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.allow_field_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试允许字段模型删除",
        description="验证allow_field_model_delete功能",
        severity="critical",
        file_level_order=18,
        tags=["允许字段", "模型删除", "allow_field_model_delete"]
    )
    def test_allow_field_model_delete(self):
        """允许字段模型删除用例 - allow_field_model_delete"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段模型删除",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试新允许字段保存",
        description="验证new_allowed_field_save_service功能",
        severity="blocker",
        file_level_order=19,
        tags=["允许字段", "保存", "new_allowed_field_save_service"]
    )
    def test_new_allowed_field_save_service(self):
        """新允许字段保存用例 - new_allowed_field_save_service"""
        try:
            # 准备测试数据
            code = self.mock_util.generate_unique_code(tag="AF")
            name = f"新测试允许字段_{self.mock_util.get_timestamp()}"
            
            set_dict = {
                "code": code,
                "name": name,
                "modelId": 1,  # 假设模型ID，需要根据实际调整
                "fieldType": "TEXT"
            }
            fields_to_filter = ["code", "name", "modelId", "fieldType"]
            
            # 标准化API调用
            response, extracted_data = self.standard_api_call(
                api_key="新允许字段保存",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="allow_field"
            )
            
            # 保存ID
            self.allow_field_id = extracted_data
            self.assert_util.assert_by_operator(self.allow_field_id, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试允许字段查看详情",
        description="验证allow_field_view_detail_service功能",
        severity="critical",
        file_level_order=20,
        tags=["允许字段", "详情查询", "allow_field_view_detail_service"]
    )
    def test_allow_field_view_detail_service(self):
        """允许字段查看详情用例 - allow_field_view_detail_service"""
        try:
            if not self.allow_field_id:
                self._ensure_save_master_data()
            
            set_dict = {"id": self.allow_field_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段查看详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试允许字段模型字段选择渲染",
        description="验证allow_select_model_render_service功能",
        severity="normal",
        file_level_order=21,
        tags=["允许字段", "渲染服务", "allow_select_model_render_service"]
    )
    def test_allow_select_model_render_service(self):
        """允许字段模型字段选择渲染用例 - allow_select_model_render_service"""
        try:
            set_dict = {
                "modelId": 1  # 假设模型ID
            }
            fields_to_filter = ["modelId"]
            
            response, _ = self.standard_api_call(
                api_key="允许字段模型字段选择渲染服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试根据模型选择字段数据源",
        description="验证allow_select_field_service功能",
        severity="normal",
        file_level_order=22,
        tags=["允许字段", "字段选择", "allow_select_field_service"]
    )
    def test_allow_select_field_service(self):
        """根据模型选择字段数据源用例 - allow_select_field_service"""
        try:
            set_dict = {
                "modelId": 1,  # 目标模型ID
                "fieldType": "SELECTABLE",  # 可选择字段类型
                "excludeSystemFields": True,  # 排除系统字段
                "includeCustomFields": True  # 包含自定义字段
            }
            fields_to_filter = ["modelId", "fieldType", "excludeSystemFields", "includeCustomFields"]
            
            response, _ = self.standard_api_call(
                api_key="根据模型选择字段数据源",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("根据模型选择字段数据源查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试模型数据选择服务",
        description="验证allow_mode_select_service功能",
        severity="normal",
        file_level_order=23,
        tags=["允许字段", "模型选择", "allow_mode_select_service"]
    )
    def test_allow_mode_select_service(self):
        """模型数据选择服务用例 - allow_mode_select_service"""
        try:
            set_dict = {
                "category": "MATCHING",  # 匹配相关模型类别
                "status": "ACTIVE",      # 活动状态
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 50,
                    "needTotal": True
                },
                "filters": {
                    "hasFields": True,  # 只返回有字段定义的模型
                    "allowCondition": True  # 支持条件规则的模型
                }
            }
            fields_to_filter = ["category", "status", "pageable", "filters"]
            
            response, _ = self.standard_api_call(
                api_key="模型数据选择服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("模型数据选择服务查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="允许字段管理",
        title="测试审单规则允许模型",
        description="验证gen_condition_rule_model_source功能 - GEN-条件-审单规则允许模型",
        severity="normal",
        file_level_order=22,
        tags=["允许字段", "审单规则", "gen_condition_rule_model_source", "GEN-条件-审单规则允许模型"]
    )
    def test_gen_condition_rule_model_source(self):
        """审单规则允许模型用例 - gen_condition_rule_model_source"""
        try:
            set_dict = {
                "ruleType": "APPROVAL",  # 审批规则类型
                "modelCategory": "CONDITION",  # 条件模型类别
                "status": "ACTIVE"  # 状态过滤
            }
            fields_to_filter = ["ruleType", "modelCategory", "status"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-条件-审单规则允许模型",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("审单规则允许模型查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
