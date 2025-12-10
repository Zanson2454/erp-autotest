# -*- coding: utf-8 -*-
"""
ERP财务模块的测试初始化
提供配置加载等通用功能，为fin_ap, fin_ar, fin_iv等子模块提供基础支持
"""

import sys
from pathlib import Path
import json
import requests

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest,LoginService
# 移除非必要导入，使用父类或utils中的LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a  # Allure reporting utility (a.json, a.text)
from utils.yaml_util import YamlUtil  # yaml_util for loading configs

class FinBaseTest(BaseTest):
    """ERP财务模块的基础测试类，负责加载财务通用配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 门户配置（仅admin）
    _ADMIN_PORTAL_KEY = "TERP_PORTAL"
    
    # Mock单例
    _mock_instance = None
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载财务通用配置
        1. 调用父类初始化方法 (包括数据库连接、环境配置等)
        2. 仅登录admin门户，获取 session/user_info/headers
        3. 初始化财务配置文件路径 (erp_fin specific)
        4. 加载API路径和参数配置 (from fin_api_path.yaml / fin_api_params.yaml)
        5. 初始化 http 工具，自动带上admin门户请求头
        6. DataFactory和缓存初始化 (fin specific, fallback to md)
        7. 设置路径参数和用户信息
        """
        super().setup_class()
        
        # Mock单例初始化 (兼容子模块如 fin_iv 的 self.mock_util)
        if cls._mock_instance is None:
            cls._mock_instance = MockData()
        cls.mock_util = cls._mock_instance
        
        # 登录服务初始化 (使用utils中的LoginService)
        cls.login_service = LoginService(cls.env_config)
        
        # 仅登录admin门户
        tenant_key = "terp"
        admin_result = cls.login_service.login(portal_key=cls._ADMIN_PORTAL_KEY, tenant_key=tenant_key)
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 检查portal_url
        portal_url = admin_result.portal_url or ""
        if not isinstance(portal_url, str) or not portal_url:
            raise ValueError("admin portal_url 不能为空且必须为字符串")
        
        # 保存admin相关变量
        cls.session = admin_result.session
        cls.user_info = admin_result.user_info
        cls.portal_url = portal_url
        cls.portal_headers = admin_result.portal_headers
        
        # 初始化 http (仅admin)
        cls.http = HttpUtil(
            url=portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
        
        # 初始化配置文件路径 (erp_fin specific)
        cls.fin_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        cls.fin_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        
        # 加载API配置
        cls.yaml_util = YamlUtil()  # or inherit from super if available
        cls.apis = cls.yaml_util.read_yaml(cls.fin_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.fin_api_params).get("api_params", {})
        
        # DataFactory init (env=test)
        DataFactory.__init__(env_name="test")
        
      
        # MD cache reuse (for org_info, currency, etc. - shared with gen_md)
        # 需要先初始化 md_init_cache，然后再获取
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"),  # 主数据依赖的初始化sql
            db_config_name="erp_db",
            cache_key="md_init_cache",  # 缓存key
            cache_dir="testdata/cache"
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        cls.logger.info(f"md_cache_data: {cls.md_cache_data is not None}")
        
        # 缓存加载：财务主数据依赖 (use md_init_sql.yaml or fin specific like pur/sls_init_sql.yaml)
        # Fallback to md cache for org/currency, etc.
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "fin_init_sql.yaml"),  # base or fin specific
            db_config_name="erp_db",
            cache_key="fin_init_cache",  # fin specific cache key
            cache_dir="testdata/cache"
        )
        cls.fin_cache_data = CacheUtil.get('fin_init_cache')
        
        
        # 初始化配置数据 (from init_data, e.g., currency)
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
            cls.tax_rate = cls.init_data.get("tax_info",[])[0].get("tax")
            cls.tax_code_id = cls.init_data.get("tax_info",[])[0].get("id")
            cls.basic_unit_id = cls.init_data.get("uom_info",{}).get("qty_uom_info",[])[0].get("uom_id")
        
        # 初始化MD (org, partner, etc.)
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.sls_org_id = cls.md_cache_data.get("org_info",{}).get("sls_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
            cls.cust_id = cls.md_cache_data.get("partner_info",{}).get("cust_info",[])[0].get("id")
            cls.mat_id = cls.md_cache_data.get("mat_info",{}).get("mat_md",{}).get("FINP",[])[0].get("id")
            cls.mat_type_cf=cls.md_cache_data.get("mat_info",{}).get("mat_type_cf",{}).get("FINP",[])[0].get("id")
            
        if cls.fin_cache_data:
            sett_item_type_info_list = cls.fin_cache_data.get("sett_item_info",{}).get("sett_item_type_info",[])
            if sett_item_type_info_list:
                cls.sett_item_type_info = sett_item_type_info_list[0].get("id")
                cls.logger.info(f"获取到 sett_item_type_info: {cls.sett_item_type_info}")
            else:
                cls.sett_item_type_info = None
                cls.logger.warning("sett_item_type_info 为空，无法获取 sett_item_type_info")
            
            sett_doc_type_info_list = cls.fin_cache_data.get("sett_doc_info",{}).get("sett_doc_type_info",[])
            if sett_doc_type_info_list:
                cls.sett_doc_type_info = sett_doc_type_info_list[0].get("id")
                cls.logger.info(f"获取到 sett_doc_type_info: {cls.sett_doc_type_info}")
            else:
                cls.sett_doc_type_info = None
                cls.logger.warning("sett_doc_type_info 为空，无法获取 sett_doc_type_info")
            
            calender_head_info = cls.fin_cache_data.get("calender_info",{}).get("calender_head_info",[])
            
            calender_item_info = cls.fin_cache_data.get("calender_info",{}).get("calender_item_info",[])
            if calender_head_info:
                cls.calendar_head_id = calender_head_info[0].get("id")
                cls.logger.info(f"获取到 calendar_head_id: {cls.calendar_head_id}")
            else:
                cls.calendar_head_id = None
                cls.logger.warning("calender_head_info 为空，无法获取 calendar_head_id")
            # 从 calender_item_info 中筛选 period_type='MONTH' 的项
            month_items = [item for item in calender_item_info if item.get("period_type") == "MONTH"]
            if month_items:
                cls.calendar_item_id = month_items[0].get("id")
                cls.logger.info(f"获取到 calendar_item_id: {cls.calendar_item_id}, period_code: {month_items[0].get('period_code')}")
            else:
                cls.calendar_item_id = None
                cls.logger.warning("calender_item_info 中没有 period_type='MONTH' 的项，无法获取 calendar_item_id")

        # 设置路径参数和用户信息
        cls.path_params = {"tmodule": "FIN"}  # erp_fin module
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"] if cls.init_data and "user_info" in cls.init_data else "test_user"
        cls.user_id = cls.init_data["user_info"]['user_info']["id"] if cls.init_data and "user_info" in cls.init_data else 1
    
    def get_api_path(self, api_key):
        """
        获取API路径 (erp_fin specific, using ParamUtil)
        """
        return ParamUtil.get_api_path(self.apis, api_key)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL (erp_fin specific)
        """
        return ParamUtil.get_api_params(self.api_params, api_path, with_query_params)
    
    def create_settlement_item(self,status="CREATED"):
        """
        创建结算项公共方法(status: "CREATED"-已创建, "RECONCILED"-已对账)
        """
        api_path = self.get_api_path("SETT-ITEM-手动创建服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["settItemCode","settItemStatus","settItemTypeId","settDate",
            "partnerType","ptHeadId","remark","comOrgId","purSlsOrgType",
            "invOrgId","matId","taxRate","basicUnitId","genMatTypeCfId",
            "settQty","settDocPrice","settDocAmt","netDocAmt","taxAmt",
            "docCurrId","baseCurrId","exchRate","grossBaseAmt","netBaseAmt",
            "settDocTypeId","settDocId","dnCode","dnItemCode","poSoCode",
            "poSoItemCode","asyncExecutionStatus","partnerId","taxCodeId",
            "purSlsOrgId"],["params","request"])
        set_dict = {
            "settItemCode": "AUTOTEST-SETTI"+str(self.mock_util.get_timestamp(timestamp=True)),
            "settItemStatus": status,
            "settItemTypeId": {"id": self.sett_item_type_info},
            "settDate": self.mock_util.get_timestamp(timestamp=True),
            "partnerType": "CUSTOMER",
            "ptHeadId": None,
            "remark": "自动化测试创建结算项",
            "comOrgId": {"id": self.com_org_id},
            "purSlsOrgType": "SLS",
            "invOrgId": {"id": self.inv_org_id},
            "matId": {"id": self.mat_id},
            "taxRate": self.tax_rate,
            "basicUnitId": {"id": self.basic_unit_id},
            "genMatTypeCfId": {"id": self.mat_type_cf},
            "settQty": 10,
            "settDocPrice": 30,
            "settDocAmt": 300,
            "netDocAmt": 265.486726,
            "taxAmt": 34.513274,
            "docCurrId": {"id": self.curr_id},
            "baseCurrId": {"id": self.curr_id},
            "exchRate": 1.00,
            "grossBaseAmt": 300,
            "netBaseAmt": 265.486726,
            "settDocTypeId":{"id": self.sett_doc_type_info} ,
            "settDocId": None,
            "dnCode": None,
            "dnItemCode": None,
            "poSoCode": None,
            "poSoItemCode": None,
            "asyncExecutionStatus": "CREATED",
            "partnerId": {"id": self.cust_id},
            "taxCodeId": {"id": self.tax_code_id},
            "purSlsOrgId": {"id": self.sls_org_id},
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        result = self.http.post(url, json=filtered_params, description="创建结算项")
        self.assert_util.assert_response_success(result)
    @classmethod
    def teardown_class(cls):
        """测试类清理 (beyond super)"""
        # BaseTest 没有 teardown_class 方法，直接执行清理逻辑
        # fin specific cleanup if needed (e.g., clear fin_cache)
        cls.logger.info("ERP财务模块测试类清理完成")


if __name__ == "__main__":
    FinBaseTest.setup_class()
    test = FinBaseTest()
    test.create_settlement_item()
