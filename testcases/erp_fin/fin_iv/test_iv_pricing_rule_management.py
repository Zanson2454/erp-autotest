# -*- coding: utf-8 -*-
"""
存货计价规则测试用例
"""

import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货计价规则")
class TestIvPricingRuleManagement(IvBaseTest):
    """存货计价规则测试类"""
    
    pricing_rule_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.pricing_rule_id = None
        cls.logger.info("存货计价规则测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="存货计价规则",
        title="测试分页查询计价规则",
        description="验证存货计价规则分页查询功能",
        severity="normal",
        file_level_order=1,
        tags=["iv", "pricing", "rule", "paging"]
    )
    def test_paging_pricing_rule(self):
        """测试分页查询计价规则"""
        try:
            # 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="计价规则分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则",
        title="测试保存计价规则",
        description="验证保存存货计价规则功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["iv", "pricing", "rule", "save"]
    )
    def test_save_pricing_rule(self):
        """测试保存计价规则"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            rule_code = self.mock_util.generate_unique_code(tag="IV_RULE")
            rule_name = f"计价规则_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": rule_code,
                "name": rule_name,
                "ruleType": "FIFO",
                "priority": 1,
                "description": "自动化测试规则"
            }
            fields_to_filter = ["comOrgId", "code", "name", "ruleType", "priority", "description"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存计价规则数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="pricing_rule"  # 自动存储为 self.pricing_rule_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则",
        title="测试根据ID查找计价规则",
        description="验证根据ID查找存货计价规则功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "pricing", "rule", "find"]
    )
    def test_find_pricing_rule_by_id(self):
        """测试根据ID查找计价规则"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_rule_id:
                self._ensure_save_pricing_rule()
            
            # 使用标准化API调用
            set_dict = {"id": self.pricing_rule_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查找计价规则数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            rule_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(rule_data.get("id"), "=", self.pricing_rule_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则",
        title="测试批量删除计价规则",
        description="验证批量删除存货计价规则功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "pricing", "rule", "batch_delete"]
    )
    def test_batch_delete_pricing_rule(self):
        """测试批量删除计价规则"""
        try:
            # 先创建多个记录用于批量删除
            rule_ids = []
            for _ in range(2):
                # 保存记录并收集ID
                rule_code = self.mock_util.generate_unique_code(tag="IV_RULE")
                rule_name = f"计价规则_{self.mock_util.get_timestamp()}"
                set_dict = {
                    "comOrgId": self.com_org_id,
                    "code": rule_code,
                    "name": rule_name,
                    "ruleType": "FIFO",
                    "priority": 1,
                    "description": "自动化测试规则"
                }
                fields_to_filter = ["comOrgId", "code", "name", "ruleType", "priority", "description"]
                response, extracted_id = self.standard_api_call(
                    api_key="保存计价规则数据服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter,
                    store_id_as=None
                )
                self.assert_util.assert_response_data(response)
                if extracted_id:
                    rule_ids.append(extracted_id)
            
            if not rule_ids:
                raise ValueError("未创建到测试数据，无法进行批量删除测试")
            
            # 使用标准化API调用
            set_dict = {"ids": rule_ids}
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="批量删除计价规则数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则",
        title="测试复制数据转换",
        description="验证存货计价规则复制数据转换功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "pricing", "rule", "copy"]
    )
    def test_copy_data_converter_rule(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_rule_id:
                self._ensure_save_pricing_rule()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.pricing_rule_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="计价规则复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="存货计价规则",
        title="测试标准导出服务",
        description="验证存货计价规则标准导出服务功能",
        severity="minor",
        file_level_order=7,
        tags=["iv", "pricing", "rule", "export", "standard"]
    )
    def test_standard_export_rule(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_rule_id:
                self._ensure_save_pricing_rule()
            
            # 使用标准化API调用
            set_dict = {
                "ruleIds": [self.pricing_rule_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["ruleIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="计价规则标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
