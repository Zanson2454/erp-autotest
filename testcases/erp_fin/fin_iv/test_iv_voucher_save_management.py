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

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货价值凭证")
class TestIvVoucherSaveManagement(FinBaseTest):
    """存货价值凭证测试类"""
    
    voucher_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.voucher_id = None
        cls.logger.info("存货价值凭证测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
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
        order=1,
        smoke=True,
        tags=["iv", "voucher", "save", "event"]
    )
    def test_save_doc_event(self):
        """测试保存业务单据记录"""
        try:
            # 准备测试数据
            doc_code = self.mock_util.generate_unique_code(tag="IV_VOUCH")
            doc_date = self.mock_util.get_timestamp()
            
            # 调用API
            api_path = self.get_api_path("IV_SAVE_DOC_TR_EVENT_SERVICE")
            params, url = self.get_api_params(api_path)
            
            # 参数处理（示例字段）
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "invOrgId", "docCode", "docDate"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "invOrgId": self.inv_org_id,
                "docCode": doc_code,
                "docDate": doc_date,
                "docType": "VOUCHER",  # 示例类型
                "amount": 1000.0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存数据
            self.voucher_id = response.get("data", {}).get("data", {}).get("id")
            assert self.voucher_id, "保存凭证失败，未获取到ID"
            
            a.json(filtered_params, "保存请求数据")
            a.json(response, "保存响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证",
        title="测试查询保存的凭证",
        description="验证查询已保存的存货价值凭证",
        severity="normal",
        order=2,
        tags=["iv", "voucher", "query"]
    )
    def test_query_saved_voucher(self):
        """测试查询保存的凭证"""
        try:
            if not self.voucher_id:
                self.test_save_doc_event()
            
            # 假设使用通用查询服务或头表查询
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_FIND_DATA_BY_ID_SERVICE")  # 关联头表查询
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            voucher_data = response.get("data", {}).get("data", {})
            assert voucher_data.get("id") == self.voucher_id, "查询凭证ID不匹配"
            
            a.json(response, "查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
