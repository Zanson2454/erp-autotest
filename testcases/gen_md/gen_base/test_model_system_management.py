from typing import Any

import allure

from testcases.gen_md import GenMdBaseTest
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
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("模型系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 模型系统通常是系统预设数据，不需要清理测试数据
            cls.logger.info("模型系统测试类结束")
        except Exception as e:
            cls.logger.error(f"测试类结束异常: {str(e)}")

        super().teardown_class()

    def _query_model_system_page(self):
        set_dict = {
            "modelKey": "GEN_MD$gen_coun_type_cf",
            "pageable": {
                "pageNo": 1,
                "pageSize": 10
            }
        }
        fields_to_filter = ["modelKey", "pageable"]

        response, _ = self.standard_api_call(
            api_key="模型系统分页查询服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter
        )
        self.assert_util.assert_response_data(response)

        data_list = response.get("data", {}).get("data", {}).get("data", []).get("data", [])
        if data_list:
            model_system_id = data_list[0].get("id")
            self.set_runtime_id("model_system", model_system_id)
            self.test_data["model_system_ids"] = [item.get("id") for item in data_list[:3] if item.get("id")]
            return model_system_id
        return self.get_runtime_id("model_system")

    def _ensure_query_model_system_page(self):
        model_system_id = self.get_runtime_id("model_system")
        if model_system_id:
            return model_system_id
        return self._query_model_system_page()

    # ================ 模型系统管理 ================
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
        """模型系统分页查询用例 - GEN_MODEL_SYSTEM_PAGING_ACTION_SERVICE"""
        try:
            self._query_model_system_page()
            
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
        """模型根据ID集合查询详情用例 - GEN_MODEL_SYSTEM_QUERY_BY_IDS_ACTION_SERVICE"""
        try:
            # 1. 确保有ID数据（原有依赖逻辑完全保留）
            model_system_id = self._ensure_query_model_system_page()

            # 2. 使用标准化API调用
            set_dict = {
                "ids": [model_system_id],
                "modelKey":"GEN_MD$gen_coun_type_cf"
            }
            fields_to_filter = ["ids", "modelKey"]
            
            response, _ = self.standard_api_call(
                api_key="模型根据ID集合查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
