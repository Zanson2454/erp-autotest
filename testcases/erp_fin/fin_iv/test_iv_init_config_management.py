# -*- coding: utf-8 -*-
"""
存货核算初始化配置测试用例
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
@allure.feature("存货核算初始化配置")
class TestIvInitConfigManagement(FinBaseTest):
    """存货核算初始化配置测试类"""
    
    init_config_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.init_config_id = None
        cls.logger.info("存货核算初始化配置测试类初始化完成")
        # 初始化配置数据
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
        
        # 初始化MD
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_init_cf",  # 假设表名
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货核算初始化配置",
        title="测试期初确认",
        description="验证存货核算初始化配置期初确认功能",
        severity="critical",
        order=1,
        tags=["iv", "init", "confirm"]
    )
    def test_confirm_begin(self):
        """测试期初确认"""
        try:
            # 准备测试数据
            config_code = self.mock_util.generate_unique_code(tag="IV_INIT")
            config_name = f"初始化配置_{self.mock_util.get_timestamp()}"
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_INIT_CF_CONFIRM_BEGIN_SERVICE")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "invOrgId"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "invOrgId": self.inv_org_id,
                "configCode": config_code
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 保存数据
            self.init_config_id = response.get("data", {}).get("data", {})
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置",
        title="测试执行初始化",
        description="验证存货核算初始化配置执行初始化功能",
        severity="critical",
        order=2,
        tags=["iv", "init", "execute"]
    )
    def test_execute_initialization(self):
        """测试执行初始化"""
        try:
            if not self.init_config_id:
                self.test_confirm_begin()
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_INIT_CF_EXECUTE_INITIALIZATION_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["configId"], ["params", "request"]
            )
            set_dict = {"configId": self.init_config_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "执行初始化响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # Add more test methods for other services in this category...
    # For example: test_reverse_initialization, test_close_account, etc.
