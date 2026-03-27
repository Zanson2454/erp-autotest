# -*- coding: utf-8 -*-
"""
存货价值凭证行测试用例
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值凭证行")
class TestIvVoucherItemManagement(IvBaseTest):
    """存货价值凭证行测试类"""
    
    voucher_item_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.voucher_item_id = None
        cls.logger.info("存货价值凭证行测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_voucher_item_tr",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试分页查询凭证行",
        description="验证存货价值凭证行分页查询功能",
        severity="normal",
        file_level_order=1,
        tags=["iv", "voucher", "item", "paging"]
    )
    def test_paging_voucher_item(self):
        """测试分页查询凭证行"""
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
                api_key="凭证行分页数据服务",
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
        story="存货价值凭证行",
        title="测试根据ID查找凭证行",
        description="验证根据ID查找存货价值凭证行功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "voucher", "item", "find"]
    )
    def test_find_voucher_item_by_id(self):
        """测试根据ID查找凭证行"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            # 使用标准化API调用
            set_dict = {"id": self.voucher_item_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查找凭证行数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            item_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(item_data.get("id"), "=", self.voucher_item_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试保存凭证行",
        description="验证保存存货价值凭证行功能",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["iv", "voucher", "item", "save"]
    )
    def test_save_voucher_item(self):
        """测试保存凭证行"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            item_code = self.mock_util.generate_unique_code(tag="IV_ITEM")
            item_name = f"凭证行_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": item_code,
                "name": item_name,
                "quantity": 10,
                "amount": 100.0
            }
            fields_to_filter = ["comOrgId", "code", "name", "quantity", "amount"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存凭证行数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="voucher_item"  # 自动存储为 self.voucher_item_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试更新凭证行",
        description="验证更新存货价值凭证行功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "voucher", "item", "update"]
    )
    def test_update_voucher_item(self):
        """测试更新凭证行"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            # 使用标准化API调用
            updated_name = f"更新凭证行_{self.mock_util.get_timestamp()}"
            set_dict = {
                "id": self.voucher_item_id,
                "name": updated_name,
                "quantity": 20
            }
            fields_to_filter = ["id", "name", "quantity"]
            
            response, _ = self.standard_api_call(
                api_key="更新凭证行数据服务",
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
        story="存货价值凭证行",
        title="测试删除凭证行",
        description="验证删除存货价值凭证行功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "voucher", "item", "delete"]
    )
    def test_delete_voucher_item(self):
        """测试删除凭证行"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            # 使用标准化API调用
            set_dict = {"id": self.voucher_item_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="删除凭证行数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
