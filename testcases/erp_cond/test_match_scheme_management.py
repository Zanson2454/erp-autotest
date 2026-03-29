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
@allure.feature("匹配方案管理")
class TestMatchSchemeManagement(ErpCondBaseTest):
    """匹配方案管理测试类 - 覆盖匹配方案相关服务"""
    
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
        cls.match_scheme_id = None
        cls.logger.info("匹配方案管理测试类初始化完成")
        
        # 初始化依赖数据，如果需要
        if cls.cond_cache_data:
            # 示例：如果需要模型ID等依赖
            pass

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="match_scheme_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

        super().teardown_class()
    # ================ 匹配方案创建 ================
    @case_decorator(
        story="匹配方案管理",
        title="测试保存主数据",
        description="验证GEN_MATCH_SCHEME_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["匹配方案", "创建", "GEN_MATCH_SCHEME_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_save_master_data(self):
        """保存主数据用例 - GEN_MATCH_SCHEME_CF_MASTER_DATA_SAVE_DATA_SERVICE"""
        try:
            # 准备测试数据
            code = self.mock_util.generate_unique_code(tag="MS")
            name = f"测试匹配方案_{self.mock_util.get_timestamp()}"
            
            set_dict = {
                "code": code,
                "name": name,
                # 示例字段，根据实际业务调整
                "remark": "测试匹配方案备注",
                "enabled": True
            }
            fields_to_filter = ["code", "name", "remark", "enabled"]
            
            # 标准化API调用
            response, extracted_data = self.standard_api_call(
                api_key="匹配方案-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="match_scheme"
            )
            
            # 保存ID
            self.match_scheme_id = extracted_data
            self.assert_util.assert_by_operator(self.match_scheme_id, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 匹配方案查询 ================
    @case_decorator(
        story="匹配方案管理",
        title="测试根据ID查找数据",
        description="验证GEN_MATCH_SCHEME_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=2,
        tags=["匹配方案", "详情查询", "GEN_MATCH_SCHEME_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_by_id(self):
        """根据ID查找用例 - GEN_MATCH_SCHEME_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_scheme_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_scheme_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试单表ID查询",
        description="验证GEN_MATCH_SCHEME_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=3,
        tags=["匹配方案", "单表查询", "GEN_MATCH_SCHEME_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"]
    )
    def test_find_single_by_id(self):
        """单表ID查询用例 - GEN_MATCH_SCHEME_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_scheme_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_scheme_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-根据ID查找单表数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试标准分页查询",
        description="验证GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE功能",
        severity="critical",
        file_level_order=4,
        tags=["匹配方案", "分页查询", "GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE"]
    )
    def test_paging_query(self):
        """标准分页查询用例 - GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE"""
        try:
            if not self.match_scheme_id:
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
                api_key="匹配方案-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试特殊场景分页查询",
        description="验证GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE_oyQmuH1功能",
        severity="normal",
        file_level_order=5,
        tags=["匹配方案", "特殊分页", "GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE_oyQmuH1"]
    )
    def test_paging_query_special(self):
        """特殊场景分页查询用例 - GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE_oyQmuH1"""
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
                api_key="匹配方案-分页数据服务_oyQmuH1",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试匹配方案分页数据服务_oyQmuH1",
        description="验证GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE_oyQmuH1功能",
        severity="normal",
        file_level_order=6,
        tags=["匹配方案", "特殊分页2", "GEN_MATCH_SCHEME_CF_PAGING_DATA_SERVICE_oyQmuH1"]
    )
    def test_paging_query_oyQmuH1(self):
        """匹配方案分页数据服务_oyQmuH1用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "specialParam": "oyQmuH1"  # 特殊参数标识
            }
            fields_to_filter = ["pageable", "specialParam"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-分页数据服务_oyQmuH1",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("匹配方案分页数据服务_oyQmuH1查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 匹配方案删除 ================
    @case_decorator(
        story="匹配方案管理",
        title="测试批量删除",
        description="验证GEN_MATCH_SCHEME_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=6,
        tags=["匹配方案", "批量删除", "GEN_MATCH_SCHEME_CF_BATCH_DELETE_DATA_SERVICE"]
    )
    def test_batch_delete(self):
        """批量删除用例 - GEN_MATCH_SCHEME_CF_BATCH_DELETE_DATA_SERVICE"""
        try:
            if not self.match_scheme_id:
                self.test_save_master_data()
            
            # 创建第二个测试数据用于批量删除
            code2 = self.mock_util.generate_unique_code(tag="MS")
            name2 = f"第二个测试匹配方案_{self.mock_util.get_timestamp()}"
            
            set_dict2 = {
                "code": code2,
                "name": name2,
                "remark": "批量删除测试"
            }
            fields_to_filter2 = ["code", "name", "remark"]
            
            response2, second_id = self.standard_api_call(
                api_key="匹配方案-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量删除参数
            set_dict = {
                "ids": [self.match_scheme_id, second_id]
            }
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.match_scheme_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试单个删除",
        description="验证GEN_MATCH_SCHEME_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=7,
        tags=["匹配方案", "删除", "GEN_MATCH_SCHEME_CF_DELETE_DATA_BY_ID_SERVICE"]
    )
    def test_delete_by_id(self):
        """单个删除用例 - GEN_MATCH_SCHEME_CF_DELETE_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_scheme_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_scheme_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.match_scheme_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 扩展服务 (复制等) ================
    @case_decorator(
        story="匹配方案管理",
        title="测试复制数据转换",
        description="验证GEN_MATCH_SCHEME_CF_COPY_DATA_CONVERTER_SERVICE功能",
        severity="normal",
        file_level_order=8,
        tags=["匹配方案", "复制", "GEN_MATCH_SCHEME_CF_COPY_DATA_CONVERTER_SERVICE"]
    )
    @pytest.mark.skip(reason="复制服务依赖特定业务场景，暂时跳过")
    def test_copy_data_converter(self):
        """复制数据转换用例 - GEN_MATCH_SCHEME_CF_COPY_DATA_CONVERTER_SERVICE"""
        try:
            if not self.match_scheme_id:
                self.test_save_master_data()
            
            set_dict = {"sourceId": self.match_scheme_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="匹配方案-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="匹配方案管理",
        title="测试复制数据转换子服务",
        description="验证GEN_MATCH_SCHEME_CF_COPY_DATA_CONVERTER_SERVICE_CHILD功能",
        severity="normal",
        file_level_order=9,
        tags=["匹配方案", "复制子服务", "GEN_MATCH_SCHEME_CF_COPY_DATA_CONVERTER_SERVICE_CHILD"]
    )
    @pytest.mark.skip(reason="子服务依赖父服务，暂时跳过")
    def test_copy_data_converter_child(self):
        """复制数据转换子服务用例"""
        try:
            a.text("子服务依赖父服务，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
