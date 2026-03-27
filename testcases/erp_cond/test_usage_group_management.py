import allure
import pytest
from pathlib import Path
import sys
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from . import ErpCondBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP条件模块")
@allure.feature("用途组管理")
class TestUsageGroupManagement(ErpCondBaseTest):
    """用途组管理测试类 - 覆盖用途组相关服务"""
    
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
        cls.usage_group_id = None
        cls.logger.info("用途组管理测试类初始化完成")
        
        # 初始化依赖数据，如果需要
        if cls.cond_cache_data:
            # 示例：如果需要模型ID等依赖
            pass

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="usage_group_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 用途组创建 ================
    @case_decorator(
        story="用途组管理",
        title="测试保存主数据",
        description="验证GEN_USAGE_GROUP_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["用途组", "创建", "GEN_USAGE_GROUP_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_save_master_data(self):
        """保存主数据用例 - GEN_USAGE_GROUP_CF_MASTER_DATA_SAVE_DATA_SERVICE"""
        try:
            # 准备测试数据
            code = self.mock_util.generate_unique_code(tag="UG")
            name = f"测试用途组_{self.mock_util.get_timestamp()}"
            
            set_dict = {
                "code": code,
                "name": name,
                # 示例字段，根据实际业务调整
                "remark": "测试用途组备注",
                "enabled": True
            }
            fields_to_filter = ["code", "name", "remark", "enabled"]
            
            # 标准化API调用
            response, extracted_data = self.standard_api_call(
                api_key="用途组-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="usage_group"
            )
            
            # 保存ID
            self.usage_group_id = extracted_data
            self.assert_util.assert_by_operator(self.usage_group_id, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 用途组查询 ================
    @case_decorator(
        story="用途组管理",
        title="测试根据ID查找数据",
        description="验证GEN_USAGE_GROUP_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=2,
        tags=["用途组", "详情查询", "GEN_USAGE_GROUP_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_by_id(self):
        """根据ID查找用例 - GEN_USAGE_GROUP_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.usage_group_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试分页数据查询",
        description="验证GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE功能",
        severity="critical",
        file_level_order=3,
        tags=["用途组", "分页查询", "GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE"]
    )
    def test_paging_query(self):
        """分页查询用例 - GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试特殊场景分页查询1",
        description="验证GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH3功能",
        severity="normal",
        file_level_order=4,
        tags=["用途组", "特殊分页1", "GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH3"]
    )
    def test_paging_query_special1(self):
        """特殊场景分页查询1 - GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH3"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "filters": {
                    "status": "ENABLED"
                }
            }
            fields_to_filter = ["pageable", "filters"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-分页数据服务_oyQmuH3",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试特殊场景分页查询2",
        description="验证GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH2功能",
        severity="normal",
        file_level_order=5,
        tags=["用途组", "特殊分页2", "GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH2"]
    )
    def test_paging_query_special2(self):
        """特殊场景分页查询2 - GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH2"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 15,
                    "needTotal": True,
                    "sortOrders": [{"field": "code", "direction": "ASC"}]
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-分页数据服务_oyQmuH2",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试单表ID查询",
        description="验证GEN_USAGE_GROUP_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=6,
        tags=["用途组", "单表查询", "GEN_USAGE_GROUP_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"]
    )
    def test_find_single_by_id(self):
        """单表ID查询用例 - GEN_USAGE_GROUP_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.usage_group_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-根据ID查找单表数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 用途组导出 ================
    @case_decorator(
        story="用途组管理",
        title="测试标准导出",
        description="验证GEN_USAGE_GROUP_CF_GEI_EXPORT_SERVICE功能",
        severity="normal",
        file_level_order=7,
        tags=["用途组", "导出", "GEN_USAGE_GROUP_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export(self):
        """标准导出用例 - GEN_USAGE_GROUP_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("用途组标准导出服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="用途组标准导出服务",
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

    @case_decorator(
        story="用途组管理",
        title="测试导出任务提交",
        description="验证GEN_USAGE_GROUP_CF_API_GEI_TASK_EXPORT_DIRECT_POST功能",
        severity="normal",
        file_level_order=8,
        tags=["用途组", "导出任务", "GEN_USAGE_GROUP_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_export_task(self):
        """导出任务用例 - GEN_USAGE_GROUP_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            # 复杂导出任务参数构造（按规范跳过）
            a.text("任务管理接口配置复杂，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 用途组导入 (跳过) ================
    @case_decorator(
        story="用途组管理",
        title="测试标准导入",
        description="验证GEN_USAGE_GROUP_CF_GEI_IMPORT_SERVICE功能",
        severity="normal",
        file_level_order=9,
        tags=["用途组", "导入", "GEN_USAGE_GROUP_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import(self):
        """标准导入用例 - GEN_USAGE_GROUP_CF_GEI_IMPORT_SERVICE"""
        try:
            # 导入需要文件上传，跳过
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试OSS导入任务",
        description="验证GEN_USAGE_GROUP_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        file_level_order=10,
        tags=["用途组", "导入任务", "GEN_USAGE_GROUP_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_oss_import_task(self):
        """OSS导入任务用例 - GEN_USAGE_GROUP_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            # OSS导入复杂，跳过
            a.text("OSS导入任务需要OSS配置，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 用途组删除 ================
    @case_decorator(
        story="用途组管理",
        title="测试批量删除",
        description="验证GEN_USAGE_GROUP_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=11,
        tags=["用途组", "批量删除", "GEN_USAGE_GROUP_CF_BATCH_DELETE_DATA_SERVICE"]
    )
    def test_batch_delete(self):
        """批量删除用例 - GEN_USAGE_GROUP_CF_BATCH_DELETE_DATA_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            # 创建第二个测试数据用于批量删除
            code2 = self.mock_util.generate_unique_code(tag="UG")
            name2 = f"第二个测试用途组_{self.mock_util.get_timestamp()}"
            
            set_dict2 = {
                "code": code2,
                "name": name2,
                "remark": "批量删除测试"
            }
            fields_to_filter2 = ["code", "name", "remark"]
            
            response2, second_id = self.standard_api_call(
                api_key="用途组-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量删除参数
            set_dict = {
                "ids": [self.usage_group_id, second_id]
            }
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.usage_group_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试单个删除",
        description="验证GEN_USAGE_GROUP_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=12,
        tags=["用途组", "删除", "GEN_USAGE_GROUP_CF_DELETE_DATA_BY_ID_SERVICE"]
    )
    def test_delete_by_id(self):
        """单个删除用例 - GEN_USAGE_GROUP_CF_DELETE_DATA_BY_ID_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.usage_group_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.usage_group_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 扩展服务 (复制等) ================
    @case_decorator(
        story="用途组管理",
        title="测试复制数据转换",
        description="验证GEN_USAGE_GROUP_CF_COPY_DATA_CONVERTER_SERVICE功能",
        severity="normal",
        file_level_order=13,
        tags=["用途组", "复制", "GEN_USAGE_GROUP_CF_COPY_DATA_CONVERTER_SERVICE"]
    )
    @pytest.mark.skip(reason="复制服务依赖特定业务场景，暂时跳过")
    def test_copy_data_converter(self):
        """复制数据转换用例 - GEN_USAGE_GROUP_CF_COPY_DATA_CONVERTER_SERVICE"""
        try:
            if not self.usage_group_id:
                self.test_save_master_data()
            
            set_dict = {"sourceId": self.usage_group_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试复制数据转换子服务",
        description="验证GEN_USAGE_GROUP_CF_COPY_DATA_CONVERTER_SERVICE_CHILD功能",
        severity="normal",
        file_level_order=14,
        tags=["用途组", "复制子服务", "GEN_USAGE_GROUP_CF_COPY_DATA_CONVERTER_SERVICE_CHILD"]
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
        story="用途组管理",
        title="测试用途组分页数据服务_oyQmuH2",
        description="验证GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH2功能",
        severity="normal",
        file_level_order=12,
        tags=["用途组", "特殊分页4", "GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH2"]
    )
    def test_paging_query_oyQmuH2(self):
        """用途组分页数据服务_oyQmuH2用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "specialParam": "oyQmuH2"  # 特殊参数标识
            }
            fields_to_filter = ["pageable", "specialParam"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-分页数据服务_oyQmuH2",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("用途组分页数据服务_oyQmuH2查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="用途组管理",
        title="测试用途组分页数据服务_oyQmuH3",
        description="验证GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH3功能",
        severity="normal",
        file_level_order=13,
        tags=["用途组", "特殊分页5", "GEN_USAGE_GROUP_CF_PAGING_DATA_SERVICE_oyQmuH3"]
    )
    def test_paging_query_oyQmuH3(self):
        """用途组分页数据服务_oyQmuH3用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 15,
                    "needTotal": True
                },
                "specialParam": "oyQmuH3"  # 特殊参数标识
            }
            fields_to_filter = ["pageable", "specialParam"]
            
            response, _ = self.standard_api_call(
                api_key="用途组-分页数据服务_oyQmuH3",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("用途组分页数据服务_oyQmuH3查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
