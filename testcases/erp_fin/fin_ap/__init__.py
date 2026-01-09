# -*- coding: utf-8 -*-
"""
应付单（AP）测试模块
提供统一的基类和初始化配置管理
"""
import allure
from typing import Dict, Any
from datetime import datetime
import time
import decimal

from testcases.erp_fin import FinBaseTest
from data_factory.fin_ap_factory import FinApFactory
from utils.param_util import ParamUtil
from utils.report_util import a


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付单模块")
class ApBaseTest(FinBaseTest):
    """
    应付单测试基类
    
    功能说明：
    1. 继承 FinBaseTest，提供财务模块的基础能力
    2. 在 setup_class 中自动初始化财务初始化配置
    3. 如果配置已存在则复用，不存在则创建并完成初始化流程
    4. 所有 fin_ap 模块下的测试类应继承此基类
    
    初始化流程：
    1. 查询是否已存在初始化配置（根据公司组织ID和moduleCode=AP）
    2. 如果不存在，则创建初始化配置
    3. 启用配置
    
    使用示例：
        from testcases.erp_fin.fin_ap import ApBaseTest
        
        class TestMyFeature(ApBaseTest):
            def test_something(self):
                # 可以直接使用 self.ap_init_id
                pass
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化 - 自动初始化财务初始化配置"""
        super().setup_class()
        
        # 初始化MD数据（从md_cache_data获取主数据）
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            com_org_info = cls.md_cache_data.get("org_info", {}).get("com_org_info", [])
            cls.com_org_id = com_org_info[0].get("id") if com_org_info else None
            cls.gr_com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
        
        
        cls.logger.info("应付单测试基类初始化完成")
    
   