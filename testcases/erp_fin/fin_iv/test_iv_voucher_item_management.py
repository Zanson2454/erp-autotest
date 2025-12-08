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

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货价值凭证行")
class TestIvVoucherItemManagement(FinBaseTest):
    """存货价值凭证行测试类"""
    
    voucher_item_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.voucher_item_id = None
        cls.logger.info("存货价值凭证行测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
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
        order=1,
        tags=["iv", "voucher", "item", "paging"]
    )
    def test_paging_voucher_item(self):
        """测试分页查询凭证行"""
        try:
            api_path = self.get_api_path("FIN_IV_VOUCHER_ITEM_TR_PAGING_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            pageable = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pageable": pageable})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试根据ID查找凭证行",
        description="验证根据ID查找存货价值凭证行功能",
        severity="normal",
        order=2,
        tags=["iv", "voucher", "item", "find"]
    )
    def test_find_voucher_item_by_id(self):
        """测试根据ID查找凭证行"""
        try:
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_ITEM_TR_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.voucher_item_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            item_data = response.get("data", {}).get("data", {})
            assert item_data.get("id") == self.voucher_item_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试保存凭证行",
        description="验证保存存货价值凭证行功能",
        severity="critical",
        order=3,
        smoke=True,
        tags=["iv", "voucher", "item", "save"]
    )
    def test_save_voucher_item(self):
        """测试保存凭证行"""
        try:
            item_code = self.mock_util.generate_unique_code(tag="IV_ITEM")
            item_name = f"凭证行_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_ITEM_TR_SAVE_DATA_SERVICE")  # 假设保存服务
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": item_code,
                "name": item_name,
                "quantity": 10,
                "amount": 100.0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.voucher_item_id = response.get("data", {}).get("data", {}).get("id")
            assert self.voucher_item_id, "保存凭证行失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试更新凭证行",
        description="验证更新存货价值凭证行功能",
        severity="normal",
        order=4,
        tags=["iv", "voucher", "item", "update"]
    )
    def test_update_voucher_item(self):
        """测试更新凭证行"""
        try:
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_ITEM_TR_SAVE_DATA_SERVICE")  # 假设更新用保存
            params, url = self.get_api_params(api_path)
            
            updated_name = f"更新凭证行_{self.mock_util.get_timestamp()}"
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "name", "quantity"], ["params", "request"]
            )
            set_dict = {
                "id": self.voucher_item_id,
                "name": updated_name,
                "quantity": 20
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "更新响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证行",
        title="测试删除凭证行",
        description="验证删除存货价值凭证行功能",
        severity="normal",
        order=5,
        tags=["iv", "voucher", "item", "delete"]
    )
    def test_delete_voucher_item(self):
        """测试删除凭证行"""
        try:
            if not self.voucher_item_id:
                self.test_save_voucher_item()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_ITEM_TR_DELETE_DATA_BY_ID_SERVICE")  # 假设删除服务
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.voucher_item_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
