# -*- coding: utf-8 -*-
"""
ERP财务模块的测试初始化
提供配置加载等通用功能，为fin_ap, fin_ar, fin_iv等子模块提供基础支持
"""

import sys
from pathlib import Path
import json
import requests
import time
import random

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
            # 确保tax_rate是float类型（从数据库查询的Decimal类型已在data_factory/base.py中转换）
            tax_rate_value = cls.init_data.get("tax_info",[])[0].get("tax")
            cls.tax_rate = float(tax_rate_value) if tax_rate_value is not None else None
            cls.tax_code_id = cls.init_data.get("tax_info",[])[0].get("id")
            cls.basic_unit_id = cls.init_data.get("uom_info",{}).get("qty_uom_info",[])[0].get("uom_id")
        
        # 初始化MD (org, partner, etc.)
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.sls_org_id = cls.md_cache_data.get("org_info",{}).get("sls_org_info",[])[0].get("id")
            cls.pur_org_id = cls.md_cache_data.get("org_info",{}).get("pur_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
            
            cls.com_org_id_2 = cls.md_cache_data.get("org_info",{}).get("com_org_info",[])[0].get("id")
            cls.inv_org_id_2 = cls.md_cache_data.get("org_info",{}).get("inv_org_info2",[])[0].get("id")
            cls.sls_org_id_2 = cls.md_cache_data.get("org_info",{}).get("sls_org_info2",[])[0].get("id")
            cls.pur_org_id_2 = cls.md_cache_data.get("org_info",{}).get("pur_org_info2",[])[0].get("id")
            
            cls.cust_id = cls.md_cache_data.get("partner_info",{}).get("cust_info",[])[0].get("id")
            cls.vend_id = cls.md_cache_data.get("partner_info",{}).get("vend_info",[])[0].get("id")
            cls.mat_id = cls.md_cache_data.get("mat_info",{}).get("mat_md",{}).get("FINP",[])[0].get("id")
            cls.mat_type_cf=cls.md_cache_data.get("mat_info",{}).get("mat_type_cf",{}).get("FINP",[])[0].get("id")
            
        if cls.fin_cache_data:
            sett_item_type_info_list = cls.fin_cache_data.get("sett_item_info",{}).get("sett_item_type_info",[])
            # 过滤掉sett_item_type_code为None的项，并构建字典
            cls.sett_item_type_info = {
                item.get("sett_item_type_code"): item 
                for item in sett_item_type_info_list 
                if item.get("sett_item_type_code")
            }
            available_codes = list(cls.sett_item_type_info.keys())
            cls.logger.info(f"获取到 sett_item_type_info，可用code列表: {available_codes}")

            
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
            sb_type_info_list = cls.fin_cache_data.get("sb_type_info",{}).get("sb_type_info",[])
            if sb_type_info_list:
                cls.sb_type_info = sb_type_info_list[0].get("id")
                cls.logger.info(f"获取到 sb_type_info: {cls.sb_type_info}")
            else:
                cls.sb_type_info = None
                cls.logger.warning("sb_type_info 为空，无法获取 sb_type_info")
       
       
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
    
    
    def create_settlement_item(self,sett_item_type_code="E_SLS_GOODS",org=1):
        """
        创建结算项公共方法，通过结算行项目类型编码创建不同结算项
        """
        if org == 1:
            com_org_id = self.com_org_id
            inv_org_id = self.inv_org_id
            sls_org_id = self.sls_org_id
            pur_org_id = self.pur_org_id
        elif org == 2:
            com_org_id = self.com_org_id_2
            inv_org_id = self.inv_org_id_2
            sls_org_id = self.sls_org_id_2
            pur_org_id = self.pur_org_id_2
        else:
            raise ValueError("org 参数错误，请输入 1 或 2")
        #获取对应key的sett_item_type_info的值
        if not self.sett_item_type_info:
            raise ValueError("sett_item_type_info 未初始化，请检查 setup_class 是否正确执行")
        sett_item_type_info = self.sett_item_type_info.get(sett_item_type_code)
        if not sett_item_type_info:
            available_codes = list(self.sett_item_type_info.keys())
            raise ValueError(
                f"未找到对应key的sett_item_type_info: {sett_item_type_code}\n"
                f"可用的sett_item_type_code列表: {available_codes}"
            )
        sett_item_type_name = sett_item_type_info.get("sett_item_type_name")
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
            "settItemStatus": "CREATED",
            "settItemTypeId": {"id": sett_item_type_info.get("id")},
            "settDate": self.mock_util.get_timestamp(timestamp=True),
            "partnerType": "CUSTOMER" if sett_item_type_info.get("bt_class") == "SALES" else "SUPPLIER",
            "ptHeadId": None,
            "remark": f"自动化测试创建结算项-{sett_item_type_name}",
            "comOrgId": {"id": com_org_id},
            "purSlsOrgType": "SLS" if sett_item_type_info.get("bt_class") == "SALES" else "PUR",
            "invOrgId": {"id": inv_org_id},
            "matId": {"id": self.mat_id},
            "taxRate": self.tax_rate,
            "basicUnitId": {"id": self.basic_unit_id},
            "genMatTypeCfId": {"id": self.mat_type_cf},
            "settQty": 10 if sett_item_type_info.get("is_count_qty") else None,
            "settDocPrice": 30 if sett_item_type_info.get("is_count_qty") else None,
            "settDocAmt": 300,
            "netDocAmt": 265.486726,
            "taxAmt": 34.513274,
            "docCurrId": {"id": self.curr_id},
            "baseCurrId": {"id": self.curr_id},
            "exchRate": 1.00,
            "grossBaseAmt": 300,
            "netBaseAmt": 265.486726,
            "settDocTypeId":{"id": sett_item_type_info.get("sett_doc_type_code")} ,
            "settDocId": None,
            "dnCode": None,
            "dnItemCode": None,
            "poSoCode": None,
            "poSoItemCode": None,
            "asyncExecutionStatus": "CREATED",
            "partnerId": {"id": self.cust_id if sett_item_type_info.get("bt_class") == "SALES" else self.vend_id},
            "taxCodeId": {"id": self.tax_code_id},
            "purSlsOrgId": {"id": sls_org_id if sett_item_type_info.get("bt_class") == "SALES" else pur_org_id},
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        result = self.http.post(url, json=filtered_params, description="创建结算项")
        self.assert_util.assert_response_success(result)
        # 响应数据是列表格式，取第一个元素的id
        data_list = result.get("data", {}).get("data", [])
        if not data_list or len(data_list) == 0:
            raise ValueError("创建结算项失败：响应数据为空")
        return data_list[0].get("id")
    def create_settlement_doc(self, sett_item_type_code="E_SLS_GOODS",org=1):
        """
        创建结算单公共方法,通过结算项类型编码创建不同结算单
        """
        sett_item_id=self.create_settlement_item(sett_item_type_code,org)
        api_path = self.get_api_path("SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
        params, url = self.get_api_params(api_path)
        data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
        data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
        data["params"]["request"][0]["id"] = sett_item_id
        result = self.http.post(url, json=data, description=f"结算项对账确认 - ID: {sett_item_id}")
        self.assert_util.assert_response_success(result)
        
        #等待异步任务执行完成，当状态为PROCESSING时一直等待，最长超时10秒
        start_time = time.time()
        timeout = 10
        while True:
            sql = "select id, sett_item_status, async_execution_status, sett_doc_id from sett_item_tr where deleted=0 and id=%s limit 1"
            sql_result = self.db.query(sql, (sett_item_id,))
            if not sql_result:
                raise ValueError(f"结算项对账确认失败: 未找到结算项ID {sett_item_id}")
            if sql_result[0].get("async_execution_status") != "PROCESSING":
                break
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"等待异步任务执行超时（{timeout}秒）")
            time.sleep(0.5)
        
        sett_doc_id = sql_result[0].get("sett_doc_id")
        if sett_doc_id is None:
            raise ValueError(f"结算项对账确认失败: 结算项ID {sett_item_id} 未生成结算单")
        return sett_doc_id
        
    def create_confirmed_settlement_doc(self, sett_item_type_code="E_SLS_GOODS",org=1):
        """
        创建已确认结算单公共方法,返回结算单id
        """
        api_path = self.get_api_path("SETT-DOC-运营端结算单确认下推应收应付-异步服务")
        params, url = self.get_api_params(api_path)
        data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
        data = ParamUtil.convert_param_type(data, ["params", "request","id"], "array")
        data["params"]["request"]["id"][0] = self.create_settlement_doc(sett_item_type_code,org)
        result = self.http.post(url, json=data, description=f"结算单确认 - ID: {data['params']['request']['id'][0]}")
        self.assert_util.assert_response_success(result)
        #等待异步任务执行完成，当状态为PROCESSING时一直等待，最长超时10秒
        sett_doc_id = data["params"]["request"]["id"][0]
        if sett_doc_id is None:
            raise ValueError("结算单确认失败: 结算单ID不能为None")
        start_time = time.time()
        timeout = 10
        while True:

            sql = "select id, sett_doc_status, trading_doc_id from sett_doc_tr where deleted=0 and id=%s limit 1"
            sql_result = self.db.query(sql, (sett_doc_id,))
            if not sql_result:
                raise ValueError(f"结算单确认失败: 未找到结算单ID {sett_doc_id}")
            if sql_result[0].get("trading_doc_id") is not None:
                break
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"等待异步任务执行超时（{timeout}秒）")
            time.sleep(0.5)
        return sett_doc_id
    
    
    def create_ar_doc(self, ar_type="STND", org=1):
        """
        创建应收单公共方法,返回应收单id
        :param ar_type: 应收单类型代码，默认"STND"（标准财务应收单）
        :param org: 组织编号，1或2，默认1
        :return: 应收单ID
        """
        # 根据org参数选择组织
        if org == 1:
            com_org_id = self.com_org_id
            sls_org_id = self.sls_org_id
            inv_org_id = self.inv_org_id
        elif org == 2:
            com_org_id = self.com_org_id_2
            sls_org_id = self.sls_org_id_2
            inv_org_id = self.inv_org_id_2
        else:
            raise ValueError("org 参数错误，请输入 1 或 2")
        
        # 检查必要的基础数据
        if not com_org_id or not sls_org_id or not self.cust_id or not self.curr_id:
            raise ValueError("缺少必要的基础数据，请检查init_data和md_cache_data")
        
        # 获取税率，如果没有则使用默认值13.0
        tax_rate = self.tax_rate if self.tax_rate else 13.0
        
        # 应收日期（当前时间戳，毫秒）
        ar_date = int(time.time() * 1000)
        
        # 应收单行项基础参数（使用随机数）
        ar_qty = random.randint(10, 1000)  # 数量：随机10-1000
        gross_doc_price = round(random.uniform(1.0, 100.0), 2)  # 含税单价：随机1.0-100.0，保留2位小数
        
        # 计算金额（动态计算，不写死）
        gross_doc_amt = ar_qty * gross_doc_price  # 含税金额 = 数量 × 含税单价
        tax_amt = round(gross_doc_amt * tax_rate / (100 + tax_rate), 2)  # 税额 = 含税金额 × 税率 / (100 + 税率)
        net_doc_amt = round(gross_doc_amt - tax_amt, 2)  # 不含税金额 = 含税金额 - 税额
        if ar_type == "STND":
            sett_item_type_id = self.sett_item_type_info.get("E_SLS_GOODS").get("id")
        else:
            raise ValueError("ar_type 参数错误，请输入 STND")
        # 应收单行项数据
        ar_item = {
            "settItemTypeId": {"id": sett_item_type_id},
            "taxAmt": tax_amt,
            "grossBaseAmt": gross_doc_amt,
            "netBaseAmt": net_doc_amt,
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "matId": {"id": self.mat_id},
            "taxCodeId": {"id": self.tax_code_id},
            "taxRate": tax_rate,
            "arQty": ar_qty,
            "grossDocPrice": gross_doc_price,
            "invOrgId": inv_org_id  
        }
        
        # 应收单计划行数据
        ar_schl = {
            "dueDate": ar_date,
            "arDocAmt": gross_doc_amt,
            "arBaseAmt": gross_doc_amt,
            "arPercent": 100,
            "receivedDocAmt": 0,
            "unreceivedDocAmt": gross_doc_amt,
            "receivedBaseAmt": 0,
            "unreceivedBaseAmt": gross_doc_amt,
            "collectionClearingStatus": "UNCLEARED"
        }
        
        # 构建应收单请求体
        set_dict = {
            "docTypeId": {"id": 14003001, "arTypeCode": ar_type},  # 标准财务应收单
            "comOrgId": {"id": com_org_id},
            "slsOrgId": {"id": sls_org_id},
            "payOrgId": {"id": com_org_id},
            "arDate": ar_date,
            "settPartnerId": {"id": self.cust_id},
            "settPartnerType": "CUSTOMER",
            "docCurrId": {"id": self.curr_id},
            "baseCurrId": {"id": self.curr_id},
            "exchRate": 1.0,
            "arStatus": "DRAFT",
            "collectionClearingStatus": "UNCLEARED",
            "billingClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "arItems": [ar_item],
            "arSchls": [ar_schl],
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_doc_amt,
            "netBaseAmt": net_doc_amt,
            "taxAmt": tax_amt,
            "uncollectedDocAmt": gross_doc_amt,
            "uncollectedBaseAmt": gross_doc_amt,
            "unbilledDocAmt": gross_doc_amt,
            "unbilledBaseAmt": gross_doc_amt,
            "unoffsetDocAmt": gross_doc_amt,
            "unoffsetBaseAmt": gross_doc_amt
        }
        
        # 需要过滤的字段列表
        fields_to_filter = [
            "docTypeId", "comOrgId", "slsOrgId", "payOrgId", "arDate",
            "settPartnerId", "settPartnerType", "docCurrId", "baseCurrId",
            "exchRate", "arStatus", "collectionClearingStatus", "billingClearingStatus",
            "headOffsetStatus", "arItems", "arSchls", "grossDocAmt", "netDocAmt",
            "grossBaseAmt", "netBaseAmt", "taxAmt", "uncollectedDocAmt",
            "uncollectedBaseAmt", "unbilledDocAmt", "unbilledBaseAmt",
            "unoffsetDocAmt", "unoffsetBaseAmt"
        ]
        
        # 使用标准化API调用
        response, extracted_id = self.standard_api_call(
            api_key="AR-应收单保存服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter
        )
        
        # 业务断言
        self.assert_util.assert_response_data(response)
        
        # 返回应收单ID
        if extracted_id is None:
            # 如果standard_api_call没有提取到ID，从响应中获取
            data = response.get("data", {}).get("data", {})
            extracted_id = data.get("id")
            if extracted_id is None:
                raise ValueError("应收单保存失败：未返回应收单ID")
        
        return extracted_id
        
    @classmethod
    def teardown_class(cls):
        """测试类清理 (beyond super)"""
        # BaseTest 没有 teardown_class 方法，直接执行清理逻辑
        # fin specific cleanup if needed (e.g., clear fin_cache)
        cls.logger.info("ERP财务模块测试类清理完成")


if __name__ == "__main__":
    FinBaseTest.setup_class()
    test = FinBaseTest()
    test.create_ar_doc()