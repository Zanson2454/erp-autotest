# -*- coding: utf-8 -*-
"""
存货价值初始化配置表测试用例
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
@allure.feature("存货价值初始化配置表")
class TestIvInitValueConfig(FinBaseTest):
    """存货价值初始化配置表测试类"""
    
    value_config_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.value_config_id = None
        cls.logger.info("存货价值初始化配置表测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_init_cf_value",  # 假设表名
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试保存数据",
        description="验证保存存货价值初始化配置表数据",
        severity="normal",
        order=1,
        tags=["iv", "init", "value", "save"]
    )
    def test_save_data(self):
        """测试保存数据"""
        try:
            config_code = self.mock_util.generate_unique_code(tag="IV_VAL")
            name = f"价值配置_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("FIN_IV_INIT_CF_SAVE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": config_code,
                "name": name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.value_config_id = response.get("data", {}).get("data", {}).get("id")
            a.json(filtered_params, "保存请求数据")
            a.json(response, "保存响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试分页数据",
        description="验证分页查询存货价值初始化配置表",
        severity="normal",
        order=2,
        tags=["iv", "init", "value", "paging"]
    )
    def test_paging_data(self):
        """测试分页数据"""
        try:
            if not self.value_config_id:
                self.test_save_data()
            
            api_path = self.get_api_path("FIN_IV_INIT_CF_PAGING_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            pageable = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pageable": pageable})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert any(record.get("id") == self.value_config_id for record in records), "未找到保存的数据"
            
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # Add more methods: test_delete_by_id, test_find_by_id, test_batch_delete, etc.
