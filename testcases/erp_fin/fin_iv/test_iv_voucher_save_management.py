# -*- coding: utf-8 -*-
"""
存货价值凭证测试用例
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
@allure.feature("存货价值凭证")
class TestIvVoucherSaveManagement(IvBaseTest):
    """存货价值凭证测试类"""
    
    voucher_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.voucher_id = None
        cls.logger.info("存货价值凭证测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="iv_doc_tr",  # 假设表名
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值凭证",
        title="测试保存业务单据记录",
        description="验证IV-存货价值凭证保存业务单据记录功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "voucher", "save", "event"]
    )
    def test_save_doc_event(self):
        """测试保存业务单据记录"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            if not self.inv_org_id:
                raise ValueError("inv_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            doc_code = self.mock_util.generate_unique_code(tag="IV_VOUCH")
            doc_date = self.mock_util.get_timestamp()
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "invOrgId": self.inv_org_id,
                "docCode": doc_code,
                "docDate": doc_date,
                "docType": "VOUCHER",
                "amount": 1000.0
            }
            fields_to_filter = ["comOrgId", "invOrgId", "docCode", "docDate", "docType", "amount"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存业务单据记录服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="voucher"  # 自动存储为 self.voucher_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证",
        title="测试查询保存的凭证",
        description="验证查询已保存的存货价值凭证",
        severity="normal",
        file_level_order=2,
        tags=["iv", "voucher", "query"]
    )
    def test_query_saved_voucher(self):
        """测试查询保存的凭证"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_id:
                self.test_save_doc_event()
            
            # 使用标准化API调用
            set_dict = {"id": self.voucher_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查询凭证头数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            voucher_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(voucher_data.get("id"), "=", self.voucher_id, "查询凭证ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
