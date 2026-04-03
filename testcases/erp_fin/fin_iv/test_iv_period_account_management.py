# -*- coding: utf-8 -*-
"""
存货价值期间账测试用例
"""

import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值期间账")
class TestIvPeriodAccountManagement(IvBaseTest):
    """存货价值期间账测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.period_account_id = None
        cls.logger.info("存货价值期间账测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="存货价值期间账",
        title="测试分页查询期间账",
        description="验证存货价值期间账分页查询功能",
        severity="normal",
        file_level_order=1,
        tags=["iv", "period", "account", "paging"]
    )
    def test_paging_period_account(self):
        """测试分页查询期间账"""
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
                api_key="期间账分页数据服务",
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
        story="存货价值期间账",
        title="测试保存期间账",
        description="验证保存存货价值期间账功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["iv", "period", "account", "save"]
    )
    def test_save_period_account(self):
        """测试保存期间账"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            period_code = self.mock_util.generate_unique_code(tag="IV_PERIOD")
            period_name = f"期间账_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": period_code,
                "name": period_name,
                "periodStart": "2025-01-01",
                "periodEnd": "2025-12-31",
                "balance": 0.0
            }
            fields_to_filter = ["comOrgId", "code", "name", "periodStart", "periodEnd", "balance"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存期间账数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="period_account"  # 自动存储为 self.period_account_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试根据ID查找期间账",
        description="验证根据ID查找存货价值期间账功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "period", "account", "find"]
    )
    def test_find_period_account_by_id(self):
        """测试根据ID查找期间账"""
        try:
            # 检查并创建依赖数据
            if not self.period_account_id:
                self._ensure_save_period_account()
            
            # 使用标准化API调用
            set_dict = {"id": self.period_account_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查找期间账数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            account_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(account_data.get("id"), "=", self.period_account_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试复制数据转换",
        description="验证存货价值期间账复制数据转换功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "period", "account", "copy"]
    )
    def test_copy_data_converter_period(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.period_account_id:
                self._ensure_save_period_account()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.period_account_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="期间账复制数据转换服务",
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
        story="存货价值期间账",
        title="测试标准导出服务",
        description="验证存货价值期间账标准导出服务功能",
        severity="minor",
        file_level_order=6,
        tags=["iv", "period", "account", "export", "standard"]
    )
    def test_standard_export_period(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.period_account_id:
                self._ensure_save_period_account()
            
            # 使用标准化API调用
            set_dict = {
                "accountIds": [self.period_account_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["accountIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="FIN_IV_ACC_PERIOD_TR_GEI_EXPORT_SERVICE",
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
        story="存货价值期间账",
        title="测试期间账分页查询",
        description="验证期间账分页查询服务",
        severity="normal",
        file_level_order=7,
        tags=["iv", "period", "account", "page"]
    )
    def test_page_service_period(self):
        """测试期间账分页查询"""
        try:
            # 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]
            
            response, _ = self.standard_api_call(
                api_key="期间账分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
