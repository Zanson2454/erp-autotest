import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("模型系统管理")
class TestModelSystemManagement(GenMdBaseTest):
    """模型系统管理测试类 - 覆盖模型系统分页查询和根据ID集合查询详情功能"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("模型系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 模型系统通常不涉及测试数据清理
            cls.logger.info("模型系统管理测试类清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="模型系统管理",
        title="测试模型系统分页查询",
        description="验证模型系统分页查询服务功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["模型系统", "分页查询", "GEN_MODEL_SYSTEM_PAGING_ACTION_SERVICE"]
    )
    def test_query_model_system_page(self):
        """模型系统分页查询用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "modelCode", "type": "TEXT"},
                    {"name": "modelName", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-模型系统-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="模型系统管理",
        title="测试模型根据ID集合查询详情",
        description="验证模型根据ID集合查询详情服务功能",
        severity="critical",
        file_level_order=2,
        tags=["模型系统", "查询详情", "GEN_MODEL_SYSTEM_QUERY_BY_IDS_ACTION_SERVICE"]
    )
    def test_query_model_system_by_ids(self):
        """模型根据ID集合查询详情用例"""
        try:
            # 使用示例 IDs 或从缓存数据获取
            sample_ids = [1, 2, 3]  # 实际使用时应从测试数据获取
            
            set_dict = {"ids": sample_ids}
            
            response, _ = self.standard_api_call(
                api_key="GEN-模型系统-根据ID集合查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["ids"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
