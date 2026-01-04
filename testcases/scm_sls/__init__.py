"""
销售管理模块的测试初始化
提供配置加载等通用功能
"""
import sys
import random
import time
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from typing import Any, Dict
from testcases.comm.base_test import BaseTest, LoginService
from data_factory.base import DataFactory
from utils.cache_util import CacheUtil
from utils.request_util import HttpUtil
from utils.param_util import ParamUtil
from utils.report_util import a



class SlsBase(BaseTest):
    """销售管理模块的基础测试类，负责加载销售配置和提供API访问方法"""
    
    # 类型提示：继承的动态属性
    yaml_util: Any
    
    # 登录两个门户，分别保存 session/user_info 并初始化 http 工具
    _PORTAL_TYPE_KEYS: Dict[str, str] = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载销售配置
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 多门户多用户登录，获取 session
        3. 初始化销售配置文件路径
        4. 加载API路径和参数配置
        5. 初始化 http 工具，自动带上门户请求头
        6. 加载销售缓存数据
        """
        super().setup_class()

        cls.login_service = LoginService(cls.env_config)  # 初始化一次登录服务，避免重复创建
        # 登录 admin
        admin_result = cls.login_service.login(portal_key=cls._PORTAL_TYPE_KEYS["admin"])
        if admin_result.status != admin_result.status.SUCCESS:
            raise RuntimeError(f"admin 登录失败: {admin_result.error_message}")
        
        # 初始化 cust 的 headers
        cls.admin_headers = admin_result.portal_headers
        if cls.admin_headers:
            cls.cust_portal_headers = cls.admin_headers.copy()  
        cust_portal_referer = cls.env_config.get("portal_config",{}).get('terp',{}).get("TERP_CUST_PC",{}).get("portal_referer")
        cls.cust_portal_headers["Referer"] = cust_portal_referer
        cls.logger.info(f"cust_portal_headers: {cls.cust_portal_headers}")
  
        # 初始化 http 实例
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
     
        # 初始化配置文件路径
        cls.sls_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "sls_api_path.yaml"
        cls.sls_api_params = Path(project_root) / "config" / "api" / "scm_sls" / "sls_api_params.yaml"
        cls.reb_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "reb_api_path.yaml"
        cls.reb_api_params = Path(project_root) / "config" / "api" / "scm_sls" / "reb_api_params.yaml"
        cls.common_api_path = Path(project_root) / "config" / "api" / "sys_common" / "common_api_path.yaml"
        cls.common_api_params = Path(project_root) / "config" / "api" / "sys_common" / "common_api_params.yaml"
        cls.acc_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "acc_api_path.yaml"
        cls.acc_api_params = Path(project_root) / "config" / "api" / "scm_sls" / "acc_api_params.yaml"
        cls.price_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "price_api_path.yaml"
        cls.price_api_params = Path(project_root) / "config" / "api" / "scm_sls" / "price_api_params.yaml"
        cls.cond_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "cond_api_path.yaml"
        cls.cond_api_params = Path(project_root) / "config" / "api" / "scm_sls" / "cond_api_params.yaml"
        cls.del_api_path = Path(project_root) / "config" / "api" / "scm_del" / "del_api_path.yaml"
        cls.del_api_params = Path(project_root) / "config" / "api" / "scm_del" / "del_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.sls_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.sls_api_params).get("api_params", {})
        
        # 加载返利API路径配置和参数配置，合并到apis和api_params中
        reb_apis = cls.yaml_util.read_yaml(cls.reb_api_path).get("apis", {})
        reb_api_params = cls.yaml_util.read_yaml(cls.reb_api_params).get("api_params", {})
        cls.apis.update(reb_apis)
        cls.api_params.update(reb_api_params)
        
        # 加载系统通用API路径配置和参数配置，合并到apis和api_params中（用于待办任务等通用功能）
        common_apis = cls.yaml_util.read_yaml(cls.common_api_path).get("apis", {})
        common_api_params = cls.yaml_util.read_yaml(cls.common_api_params).get("api_params", {})
        cls.apis.update(common_apis)
        cls.api_params.update(common_api_params)
        
        # 加载账户管理API路径配置和参数配置，合并到apis和api_params中（用于返利账户流水查询等）
        acc_apis = cls.yaml_util.read_yaml(cls.acc_api_path).get("apis", {})
        acc_api_params = cls.yaml_util.read_yaml(cls.acc_api_params).get("api_params", {})
        cls.apis.update(acc_apis)
        cls.api_params.update(acc_api_params)
        
        # 加载价格模块API路径配置和参数配置，合并到apis和api_params中（用于价格调整、价格维护等）
        price_apis = cls.yaml_util.read_yaml(cls.price_api_path).get("apis", {})
        price_api_params = cls.yaml_util.read_yaml(cls.price_api_params).get("api_params", {})
        cls.apis.update(price_apis)
        cls.api_params.update(price_api_params)
        
        # 加载条件模块API路径配置和参数配置，合并到apis和api_params中（用于匹配记录查询等）
        cond_apis = cls.yaml_util.read_yaml(cls.cond_api_path).get("apis", {})
        cond_api_params = cls.yaml_util.read_yaml(cls.cond_api_params).get("api_params", {})
        cls.apis.update(cond_apis)
        cls.api_params.update(cond_api_params)
        
        # 加载交货管理API路径配置和参数配置，合并到apis和api_params中（用于交货单操作等）
        del_apis = cls.yaml_util.read_yaml(cls.del_api_path).get("apis", {})
        del_api_params = cls.yaml_util.read_yaml(cls.del_api_params).get("api_params", {})
        cls.apis.update(del_apis)
        cls.api_params.update(del_api_params)
        
        # 初始化DataFactory（必须在init_sql_cache之前调用）
        DataFactory.__init__(env_name="test")
        
             # 加载缓存数据
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "md_init_sql.yaml"), # 主数据依赖的初始化sql 存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="md_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.md_cache_data = CacheUtil.get('md_init_cache')
        
        
        DataFactory.init_sql_cache(
            sql_config_path=str(project_root / "config" / "erp" / "sls_init_sql.yaml"), # 销售管理依赖的初始化sql 存放路径
            db_config_name="erp_db", # 数据库配置名称
            cache_key="sls_init_cache", # 缓存key
            cache_dir="testdata/cache" # 缓存目录
        )
        cls.sls_cache_data = CacheUtil.get('sls_init_cache')

        cls.path_params = {"tmodule": "SCM_SLS"}
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.user_id = cls.init_data["user_info"]['user_info']["id"]

        
    # ==================== 销售订单相关方法 ====================
        
    # 初始化订单配置数据
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.curr_id = currency_info[0].get("curr_id")
            else:
                # 默认货币ID（人民币 CNY）
                cls.curr_id = 2000001
            
            country_info = cls.init_data.get("country_info") or []
            if country_info:
                cls.coun_id = country_info[0].get("coun_id")
            else:
                cls.coun_id = None
            
            exchange_rate_type_info = cls.init_data.get("exchange_rate_type_info") or []
            if exchange_rate_type_info:
                cls.exchange_rate_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                cls.exchange_rate_type_id = None
        else:
            # 当 init_data 为空时，设置默认值
            cls.curr_id = 2000001  # 默认货币ID（人民币 CNY）
            cls.coun_id = None
            cls.exchange_rate_type_id = None
        # 初始化MD
        if cls.md_cache_data:
            partner_info = cls.md_cache_data.get("partner_info") or {}
            cust_info = partner_info.get("cust_info") or []
            if cust_info:
                cls.cust_id = cust_info[0].get("id")
                cls.logger.info(f"cust_id: {cls.cust_id}")
            
            org_info = cls.md_cache_data.get("org_info") or {}
            gr_come_org_info = org_info.get("gr_come_org_info") or []
            if gr_come_org_info:
                cls.com_org_id = gr_come_org_info[0].get("id")
            
            sls_dc_md = org_info.get("sls_dc_md") or []
            if sls_dc_md:
                cls.sls_dc_id = sls_dc_md[0].get("id")
            
            sls_org_info = org_info.get("sls_org_info") or []
            if sls_org_info:
                cls.sls_org_id = sls_org_info[0].get("id")
            
            inv_org_info = org_info.get("inv_org_info") or []
            if inv_org_info:
                cls.inv_org_id = inv_org_info[0].get("id")
            
            inv_loc_info = org_info.get("inv_loc_info") or []
            if inv_loc_info:
                cls.inv_loc_id = inv_loc_info[0].get("id")
            
            partner_type_cf = partner_info.get("partner_type_cf") or {}
            sls_partner_type = partner_type_cf.get("sls_partner_type") or []
            if sls_partner_type:
                cls.partner_type_id = sls_partner_type[0].get("id")
            
            mat_info = cls.md_cache_data.get("mat_info") or {}
            mat_md = mat_info.get("mat_md") or {}
            finp = mat_md.get("FINP") or []
            if finp:
                cls.mat_id = finp[0].get("id")
                cls.mat_code = finp[0].get("mat_code")
                cls.mat_name = finp[0].get("mat_name")
        
        if cls.sls_cache_data:
            sls_config = cls.sls_cache_data.get("sls_config") or {}
            cls.so_type_info = sls_config.get("so_type_info") or []
            cls.ORDER_TYPES = cls.so_type_info  # 添加缺失的属性
            for so_type  in  cls.so_type_info:
                if so_type.get("so_type_code") == "STND":
                    cls.stnd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "THRD":
                    cls.thrd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "CENT":
                    cls.cent_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "QUOTE":
                    cls.quote_so_type_id = so_type.get("id")
            cls.so_item_type_info = sls_config.get("so_item_type_info") or []
            cls.ORDER_LINE_TYPES = cls.so_item_type_info  # 添加缺失的属性
            for so_item_type in cls.so_item_type_info:
                if so_item_type.get("so_item_type_code") == "NORM":
                    cls.stnd_so_item_type_id = so_item_type.get("id")
            
            # 初始化返利政策相关属性
            cls.rebate_type_info = sls_config.get("rebate_type_info") or []
            for rebate_type in cls.rebate_type_info:
                if rebate_type.get("rebate_type_code") == "STND":
                    cls.stnd_rebate_type_id = rebate_type.get("id")
            
            # 添加订单类型和订单行类型的组合
            cls.ORDER_TYPE_LINE_COMBINATIONS = []
            for so_type in cls.so_type_info:
                for so_item_type in cls.so_item_type_info:
                    cls.ORDER_TYPE_LINE_COMBINATIONS.append({
                        "so_type": so_type,
                        "so_item_type": so_item_type
                    })

        # 初始化销售配置数据
        # cls.so_type_id = cls.ids.get("so_type_id")
        cls.addr_id = None
        cls.addr_detail = None
        cls.cust_person_name = None
        cls.cust_phone = None
        cls.sls_person_obj = None
        cls.sls_phone = None
        cls.sls_person_name = None
        cls.sls_partner_links = None
        cls.so_items = None
        cls.sls_org_obj = None
        cls.mat_obj = None
        cls.so_head_id_save = None
        cls.so_head_id_submit = None
        cls.so_item_id = None
        cls.so_item_data = None
        cls.render_qty = random.randint(1, 99)  # 生成1-99之间的随机整数
        cls.so_data_render = None
        cls.so_data_price = None
        cls.priceIdempotent=None
        cls.so_head_data = None

    def get_api_path(self, api_key):
        """
        获取API路径
        """
        return super().get_api_path(api_key, self.apis)
    
    def get_api_params(self, api_path, with_query_params=None):
        """
        获取API请求参数和完整URL
        """
        return super().get_api_params(api_path, self.api_params, with_query_params)
    
    def create_sales_order(self, order_type="STND", submit=False, rebate_amount=None):
        """
        创建销售订单的公共方法
        :param order_type: 订单类型（STND/THRD/CENT），默认为STND
        :param submit: 是否提交订单（True=提交，False=保存为草稿）
        :param rebate_amount: 返利金额，如果提供则会在订单行中添加返利金额
        :return: 订单ID
        """
        try:
            # 1. 初始化订单
            self._init_sales_order(order_type)
            # 2. 查询客户信息
            self._query_customer_info()
            # 3. 查询相关方
            self._query_partner()
            
            # 4. 渲染订单行
            self._render_order_line(order_type)
            
            # 5. 定价
            self._calculate_pricing()
            
            # 6. 如果提供了返利金额，添加到订单行中
            if rebate_amount is not None:
                self._add_rebate_amount(rebate_amount)
            
            # 4. 保存或提交
            if submit:
                self._so_submit()
                return self.so_head_id_submit  # 返回提交后的订单ID
            else:
                self._so_save()
                return self.so_head_id_save  # 返回草稿订单ID

        except Exception as e:
            self.logger.error(f"创建订单失败: {str(e)}")
            raise
    
   
    def _init_sales_order(self, order_type="STND"):
        """初始化销售订单

        Args:
            order_type: 订单类型，默认为标准销售(STND)
        """
        api_path = self.get_api_path("SLS-销售-订单创建初始化服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["btClass"], ["params", "request"]
        )
        set_dict = {
            "btClass": "SALES"
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        
        # 4. 发送请求和断言
        response = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_data(response)
    
        
        response = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
    
        # 从嵌套结构中获取数据
        response_data = response.get("data", {}).get("data", {})

        # 保存销售人员信息供后续使用
        self.sls_person_obj = response_data.get("slsPerson")
        self.sls_phone = response_data.get("slsPhone")
        if self.sls_person_obj:
            self.sls_person_name = self.sls_person_obj.get("name")
        # 验证必要字段
        assert self.sls_person_obj is not None, "销售人员信息为空"

    def _query_customer_info(self):
        """查询客户信息"""
        api_path = self.get_api_path("SLS-销售-客户选择渲染处理")
        params, url = self.get_api_params(api_path)
        params["params"] = {
            "custId": self.cust_id
        }
       
        response = self.http.post(url, json=params)
        self.assert_util.assert_response_success(response)
        # 从嵌套结构中获取数据
        response_data = response.get("data", {}).get("data", {})
        self.addr_id = response_data.get("addrId").get("id")
        self.addr_detail = response_data.get("addrDetail")
        self.cust_person_name = response_data.get("custPersonName")
        self.cust_phone = response_data.get("custPhone")
        
        
    def _query_partner(self):
        """查询相关方"""
        if not self.sls_person_obj:
            self._init_sales_order()
        if not self.sls_phone or not self.sls_person_name:
            self._query_customer_info()
            
        so_doc_date = self.mock_util.get_timestamp(timestamp=True)
        price_calc_date = self.mock_util.get_timestamp(timestamp=True)
        so_schl_del_date = self.mock_util.get_timestamp(timestamp=True,day_offset=3)

        api_path = self.get_api_path("销售订单获取相关方数据服务")
        params, url = self.get_api_params(api_path)
        
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["custId", "slsPerson", "slsPhone", "slsPersonName", "currExchangeRateType", "soDocDate", "priceCalcDate", "soItems"], ["params","request"]
        )
        set_dict = {
            "custId": {"id": self.cust_id},
            "isFixedExchRate": False,
            "priceCalcDate": price_calc_date,
            "reCalculate": False,
            "slsPerson": self.sls_person_obj,
            "slsPhone": self.sls_phone,
            "slsPersonName": self.sls_person_name,
            "soDocDate": so_doc_date,
            "soTypeId": {"id": self.stnd_so_type_id},
            "soItems": [{
                "bomWhether": False,
                "soSchlDelDate": so_schl_del_date,
            }]
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        responese = self.http.post(url, json=filtered_params, description="查询相关方")
        self.assert_util.assert_response_data(responese)
        self.sls_partner_links = responese.get("data", {}).get("data", {}).get("slsPartnerLinks",[])

    def _render_order_line(self, order_type="STND"):
        """渲染订单行

        Args:
            order_type: 订单类型，默认为标准销售(STND)
        """
        if not self.sls_person_obj:
            self._init_sales_order()
        if not self.sls_phone or not self.sls_person_name:
            self._query_customer_info()
        if not self.sls_partner_links:
            self._query_partner()
        if not self.addr_id:
            self._query_customer_info()

        api_path = self.get_api_path("SLS-销售-物料选择后渲染处理服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, [
                "addrId",  "custId", "slsComId", "slsDcId", "slsOrgId","invLoc", "invOrg", "soDocDate", "soTypeId", "baseCurrId", "slsCurrId",
                "slsPartnerLinks", "soItems"
            ], ["params", "request"]
        )
        set_dict = {
            "addrId": {"id": self.addr_id},
            "addrDetail": self.addr_detail,
            "baseCurrId": {"id":self.curr_id},
            "slsCurrId": {"id":self.curr_id},
            "custId": {"id": self.cust_id},
            "custPersonName": self.cust_person_name,
            "custPhone": self.cust_phone,
            "invLoc": None,
            "invOrg": None,
            "slsPerson": self.sls_person_obj,
            "slsPhone": self.sls_phone,
            "slsPersonName": self.sls_person_name,
            "slsComId": {"id": self.com_org_id},
            "slsDcId": {"id": self.sls_dc_id},
            "slsOrgId": {"id": self.sls_org_id},
            "slsPartnerLinks": self.sls_partner_links,
            "soDocDate": self.mock_util.get_timestamp(timestamp=True),
            "soTypeId": {"id": self.stnd_so_type_id},
            "soItems": [
                {
                "matId": {"id": self.mat_id},
                "soItemSlsQty": None,
                "taxRateId": None,
                "usageType": None,
                "invLocId": None,
                "invOrgId": None,
            }
                ]
        }
        ParamUtil.set_request_params(filtered_params, set_dict)

        response = self.http.post(url, json=filtered_params, description="订单行渲染")
        self.so_data_render = response.get("data", {}).get("data", {})
        self.assert_util.assert_response_data(response)
        self.so_code = self.so_data_render.get("soCode")
        self.assert_util.assert_by_operator(self.so_code, "not_empty",message="检查订单号是否获取到")
        
        
    def _calculate_pricing(self):
        """自动定价"""
        
        if not self.so_data_render:
            self._render_order_line()
            
        api_path = self.get_api_path("SLS-销售订单-前端定价服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, [
                "soTypeId", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks"
            ], ["params", "request"]
        )

        # 方法1：使用字典更新，更简洁
        pricing_updates = {
            "priceCalcDate": self.mock_util.get_timestamp(timestamp=True),
            "currExchangeRateType": self.exchange_rate_type_id,
            "exchRate": 1,
            "isFixedExchRate": False,
            "soDesc": f"自动化测试_{self.mock_util.get_timestamp()}"
        }
        self.so_data_render.update(pricing_updates)
        
        # 方法2：使用字典推导式更新订单行
        so_item_updates = {
            "soItemSlsQty": self.render_qty,
            "soItemDelQty": 0,
            "soItemTransferQty": 0,
            "soItemBaseQty": 1,
            "soItemPrice": self.mock_util.get_mock_price(),
            "invLocId": {"id": self.inv_loc_id},
            "invOrgId": {"id": self.inv_org_id}
        }
        self.so_data_render["soItems"][0].update(so_item_updates)
        
        set_dict = self.so_data_render
        ParamUtil.set_request_params(filtered_params, set_dict)

        response = self.http.post(url, json=filtered_params, description="自动定价")
        self.assert_util.assert_response_data(response)
        self.so_data_price = response.get("data", {}).get("data", {})
    
    def _add_rebate_amount(self, rebate_amount):
        """添加返利金额到订单行中"""
        try:
            if self.so_data_price and "soItems" in self.so_data_price:
                for item in self.so_data_price["soItems"]:
                    # 添加返利金额字段
                    item["rebateAmt"] = rebate_amount
                    # 计算净金额 = 销售金额 - 返利金额
                    if "salesAmt" in item:
                        item["netAmt"] = item["salesAmt"] - rebate_amount
                    elif "grossTradeAmt" in item:
                        item["netAmt"] = item["grossTradeAmt"] - rebate_amount
                
                self.logger.info(f"已添加返利金额 {rebate_amount} 到订单行中")
        except Exception as e:
            self.logger.error(f"添加返利金额失败: {str(e)}")
            raise
    
    def _so_save(self):
        """SLS-销售订单-保存服务"""
        try:
            # 确保有可保存的订单数据
            if  not self.so_data_price:
                self._calculate_pricing()

            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "soCode", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                    "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                    "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                    "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks",
                    "soTypeId", "isFixedExchRate", "reCalculate", "rebateAmt", "netAmt"
                ], ["params", "request"]
            )
            
            # 使用定价后的数据作为保存请求
            set_dict = self.so_data_price
            set_dict["syncSubmit"] = "false" # 不同步提交
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="保存销售订单")
            self.assert_util.assert_response_data(response)
            
            # 保存订单ID供后续使用
            response_data = response.get("data", {}).get("data", {})
            self.so_head_id_save = response_data.get("id")
            self.so_head_data = response_data
            self.priceIdempotent = response_data.get("priceIdempotent")
            self.so_status = response_data.get("soStatus")
            self.so_item_data = response_data.get("soItems")
            self.so_item_id = response_data.get("soItems")[0].get("id")
            self.assert_util.assert_by_operator(self.so_head_id_save, "not_empty",message="保存订单失败，未返回订单ID")
            self.assert_util.assert_by_operator(self.priceIdempotent, "not_empty",message="保存订单失败，未返回价格幂等码")
            self.assert_util.assert_by_operator(self.so_status, "=", "DRAFT",message="保存订单失败，订单状态不是草稿")      
            
            return self.so_head_id_save
        except Exception as e:
            self.logger.error(f"保存订单失败: {str(e)}")
            raise
        
    def _so_submit(self):
        """SLS-销售订单-提交服务"""
        try:
            # 确保有可提交的订单
            if not self.so_data_price:
                self._calculate_pricing()

            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,  [
                    "soCode", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                    "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                    "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                    "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks",
                    "soTypeId", "isFixedExchRate", "reCalculate","syncSubmit"
                ], ["params", "request"]
            )
            
            set_dict = self.so_data_price
            set_dict["syncSubmit"] = "true" # 同步提交
            
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="提交销售订单")
            self.assert_util.assert_response_data(response)
            self.so_head_id_submit = response.get("data", {}).get("data", {}).get("id")
            
            return self.so_head_id_submit
        except Exception as e:
            self.logger.error(f"提交订单失败: {str(e)}")
            raise

    # ==================== 报价单相关方法 ====================
    
    def create_quote(self, submit=False):
        """
        创建报价单的公共方法
        :param submit: 是否提交（True=已生效态，False=草稿态）
        :return: 报价单ID
        """
        try:
            # 1. 准备报价单基础数据
            self._prepare_quote_data()
            
            # 2. 直接保存或提交（跳过定价步骤）
            if submit:
                self._quote_submit()
                return self.quote_id_submit  # 返回提交后的报价单ID
            else:
                self._quote_save()
                return self.quote_id_save  # 返回草稿报价单ID

        except Exception as e:
            self.logger.error(f"创建报价单失败: {str(e)}")
            raise
    
    def _prepare_quote_data(self):
        """准备报价单基础数据"""
        try:
            # 生成报价单编码和描述
            quote_code = self.mock_util.generate_unique_code(tag="QT")
            quote_name = f"自动化测试报价_{self.mock_util.get_timestamp()}"
            
            # 准备报价单基础数据
            # 报价单类型需要有效截止时间（effectiveAt）
            import time
            current_time = int(time.time() * 1000)
            effective_at = current_time + (5 * 24 * 60 * 60 * 1000)  # 5天后
            
            self.quote_data = {
                "soCode": quote_code,
                "soDesc": quote_name,
                "custId": {"id": self.cust_id},
                "slsOrgId": {"id": self.sls_org_id},
                "slsComId": {"id": self.com_org_id},
                "slsDcId": {"id": self.sls_dc_id},
                "soTypeId": {"id": self.quote_so_type_id if hasattr(self, 'quote_so_type_id') and self.quote_so_type_id else self.stnd_so_type_id},
                "baseCurrId": {"id": self.curr_id},
                "slsCurrId": {"id": self.curr_id},
                "effectiveAt": effective_at,  # 报价单类型必需字段
                "soItems": [
                    {
                        "matId": {"id": self.mat_id},
                        "matCode": "AUTOTEST_MAT_FINP",
                        "matName": "成品物料(自动化-带批次)",
                        "soItemSlsQty": 10,
                        "soItemGrossPrice": 100.0,
                        "uomSlsId": {"id": 2004001},
                        "uomBaseId": {"id": 2004001},
                        "soItemTypeId": {"id": self.stnd_so_item_type_id},
                        "invOrgId": {"id": self.inv_org_id},
                        "invLocId": {"id": self.inv_loc_id},
                        "soSchlDelDate": self.mock_util.get_timestamp(timestamp=True, day_offset=1)
                    }
                ]
            }
            
            self.logger.info(f"报价单基础数据准备完成: {quote_code}")
            
        except Exception as e:
            self.logger.error(f"准备报价单数据失败: {str(e)}")
            raise
    
    def _quote_calculate_pricing(self):
        """报价单定价计算"""
        try:
            # 确保有可定价的数据
            if not self.quote_data:
                self._prepare_quote_data()
            
            api_path = self.get_api_path("SLS-销售订单-前端定价服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, self.quote_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存定价后的数据
            self.quote_data_price = response.get("data", {}).get("data", {})
            self.quote_id_price = self.quote_data_price.get("id")
            
            self.logger.info(f"报价单定价计算完成，报价单ID: {self.quote_id_price}")
            
        except Exception as e:
            self.logger.error(f"报价单定价计算失败: {str(e)}")
            raise
    
    def _quote_save(self):
        """报价单保存服务"""
        try:
            # 确保有可保存的报价单数据
            if not self.quote_data:
                self._prepare_quote_data()
            
            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, self.quote_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存草稿报价单ID
            response_data = response.get("data", {}).get("data", {})
            self.quote_id_save = response_data.get("id")
            
            self.logger.info(f"报价单保存成功，ID: {self.quote_id_save}")
            
        except Exception as e:
            self.logger.error(f"报价单保存失败: {str(e)}")
            raise
    
    def _quote_submit(self):
        """报价单提交服务（使用syncSubmit同步提交，不触发审批流程）"""
        try:
            # 确保有可提交的报价单数据
            if not self.quote_data:
                self._prepare_quote_data()
            
            # 使用保存服务，设置syncSubmit为true来同步提交（与手动创建保持一致，不触发审批）
            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "effectiveAt", "soItems", "syncSubmit"], 
                ["params", "request"]
            )
            
            # 设置syncSubmit为true，实现同步提交（不触发审批流程）
            set_dict = self.quote_data.copy()
            set_dict["syncSubmit"] = "true"
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存提交后的报价单ID
            response_data = response.get("data", {}).get("data", {})
            self.quote_id_submit = response_data.get("id")
            
            self.logger.info(f"报价单提交成功，ID: {self.quote_id_submit}")
            
        except Exception as e:
            self.logger.error(f"报价单提交失败: {str(e)}")
            raise

    # ==================== 交货单相关方法 ====================
    
    def query_delivery_notes_by_so_code(self, so_code):
        """
        根据销售订单号查询关联的交货单ID列表
        :param so_code: 销售订单号
        :return: 交货单ID列表
        """
        try:
            # 通过doc_code字段查询关联的交货单
            query_sql = """
                SELECT DISTINCT h.id as dn_id, h.dn_code, h.del_status
                FROM del_dn_head_tr h
                INNER JOIN del_dn_item_tr i ON h.id = i.dn_id
                WHERE (i.doc_code = %s OR h.doc_code = %s) 
                  AND h.bt_class = 'SLS'
                  AND h.del_status != 'DISCARDED'
                ORDER BY h.created_at DESC
            """
            result = self.db.query(query_sql, (so_code, so_code))
            if result:
                dn_ids = [item['dn_id'] for item in result]
                self.logger.info(f"查询到订单 {so_code} 关联的交货单: {dn_ids}")
                return dn_ids
            return []
        except Exception as e:
            self.logger.error(f"查询交货单失败: {str(e)}")
            return []
    
    def discard_delivery_note(self, dn_id):
        """
        作废交货单
        :param dn_id: 交货单ID
        :return: 是否成功
        """
        try:
            api_path = self.get_api_path("DEL-交货单作废服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": dn_id})
            
            response = self.http.post(url, json=filtered_params, params={"tmodule": "SCM_DEL"})
            self.assert_util.assert_response_success(response)
            
            self.logger.info(f"交货单 {dn_id} 作废成功")
            return True
        except Exception as e:
            self.logger.error(f"作废交货单失败，dn_id: {dn_id}, 错误: {str(e)}")
            raise
    
    def approve_sales_order_or_quote(self, order_id):
        """
        审批销售订单或报价单通过（如果状态为审批中）
        :param order_id: 订单或报价单ID
        :return: 是否成功审批（如果已经是生效状态则返回True但不执行审批）
        """
        try:
            # 1. 查询订单状态
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[order_id]
            )
            
            if not order_status:
                raise ValueError(f"未找到订单数据，订单ID: {order_id}")
            
            current_status = order_status[0]['so_status']
            
            # 2. 如果已经是生效状态，无需审批
            if current_status == "EFFECT":
                self.logger.info(f"订单已经是生效状态，无需审批。订单ID: {order_id}")
                return True
            
            # 3. 如果不是审批中状态，记录警告但继续尝试审批
            if current_status != "APPROVING":
                self.logger.warning(f"订单状态不是审批中，当前状态: {current_status}。订单ID: {order_id}")
            
            # 4. 查询完整的订单数据
            order_data = self.db.query(f"""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = {order_id}
            """)
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {order_id}")
            
            # 5. 调用审批通过API
            api_path = self.get_api_path("SLS-销售订单-审批同意服务")
            params, url = self.get_api_params(api_path)
            
            # 6. 构造完整的订单数据传递给API
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "soCode", "soTitle", "soStatus", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 7. 获取订单行项目数据
            so_items = []
            for item in order_data:
                if item.get('i.id'):  # 确保是订单行数据（使用别名）
                    so_items.append({
                        "id": item['i.id'],
                        "soItemCode": item['so_item_code'],
                        "matId": {"id": item['mat_id']},
                        "matCode": item['mat_code'],
                        "matName": item['mat_name'],
                        "soItemSlsQty": float(item['so_item_sls_qty']) if item['so_item_sls_qty'] else 0,
                        "soItemDelQty": float(item['so_item_del_qty']) if item['so_item_del_qty'] else 0,
                        "soItemTransferQty": float(item['so_item_transfer_qty']) if item['so_item_transfer_qty'] else 0,
                        "soItemPrice": float(item['so_item_price']) if item['so_item_price'] else 0,
                        "uomSlsId": {"id": item['uom_sls_id']},
                        "invOrgId": {"id": item['inv_org_id']},
                        "invLocId": {"id": item['inv_loc_id']}
                    })
            
            set_dict = {
                "id": order_id,
                "soCode": order_data[0]['so_code'],
                "soTitle": order_data[0].get('so_title'),
                "soStatus": order_data[0]['so_status'],
                "custId": {"id": order_data[0]['cust_id']},
                "slsOrgId": {"id": order_data[0]['sls_org_id']},
                "slsComId": {"id": order_data[0]['sls_com_id']},
                "slsDcId": {"id": order_data[0]['sls_dc_id']},
                "soTypeId": {"id": order_data[0]['so_type_id']},
                "baseCurrId": {"id": order_data[0]['base_curr_id']},
                "slsCurrId": {"id": order_data[0]['sls_curr_id']},
                "soItems": so_items
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 8. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 9. 等待订单状态更新
            time.sleep(2)
            
            # 10. 查询订单状态，验证是否为已生效（添加重试机制）
            actual_status = None
            for attempt in range(5):
                order_status = self.db.query(
                    "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                    params=[order_id]
                )
                if order_status:
                    actual_status = order_status[0]['so_status']
                    if actual_status == "EFFECT":
                        break
                time.sleep(1)
            
            if actual_status != "EFFECT":
                self.logger.warning(f"审批后订单状态不是已生效，当前状态: {actual_status}。订单ID: {order_id}")
            
            self.logger.info(f"订单审批通过成功，订单ID: {order_id}，状态: {actual_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"审批订单失败，订单ID: {order_id}, 错误: {str(e)}")
            raise
    
    def create_delivery_order(self, so_id):
        """
        基于销售订单创建交货单的公共方法
        :param so_id: 销售订单ID
        :return: 交货单ID（如果API返回的话）
        """
        try:
            # 1. 查询销售订单的完整数据
            order_data = self.db.query("""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = %s
            """, (so_id,))
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {so_id}")
            
            # 2. 调用创建交货单API
            api_path = self.get_api_path("SO-销售订单自动创建交货单服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 构造完整的销售订单数据传递给API
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "soCode", "soTitle", "soStatus", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 4. 获取订单行项目数据
            so_items = []
            for item in order_data:
                if item.get('i.id'):  # 确保是订单行数据（使用别名）
                    so_items.append({
                        "id": item['i.id'],
                        "soItemCode": item['so_item_code'],
                        "matId": {"id": item['mat_id']},
                        "matCode": item['mat_code'],
                        "matName": item['mat_name'],
                        "soItemSlsQty": float(item['so_item_sls_qty']) if item['so_item_sls_qty'] else 0,
                        "soItemDelQty": float(item['so_item_del_qty']) if item['so_item_del_qty'] else 0,
                        "soItemTransferQty": float(item['so_item_transfer_qty']) if item['so_item_transfer_qty'] else 0,
                        "soItemPrice": float(item['so_item_price']) if item['so_item_price'] else 0,
                        "uomSlsId": {"id": item['uom_sls_id']},
                        "invOrgId": {"id": item['inv_org_id']},
                        "invLocId": {"id": item['inv_loc_id']}
                    })
            
            set_dict = {
                "id": so_id,
                "soCode": order_data[0]['so_code'],
                "soTitle": order_data[0]['so_title'],
                "soStatus": order_data[0]['so_status'],
                "custId": {"id": order_data[0]['cust_id']},
                "slsOrgId": {"id": order_data[0]['sls_org_id']},
                "slsComId": {"id": order_data[0]['sls_com_id']},
                "slsDcId": {"id": order_data[0]['sls_dc_id']},
                "soTypeId": {"id": order_data[0]['so_type_id']},
                "baseCurrId": {"id": order_data[0]['base_curr_id']},
                "slsCurrId": {"id": order_data[0]['sls_curr_id']},
                "soItems": so_items
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 5. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 6. 保存交货单ID（如果API返回的话）
            delivery_id = response.get("data", {}).get("data", {})
            
            # 7. 记录创建结果
            self.logger.info(f"交货单创建成功 - 销售订单ID: {so_id}, 交货单ID: {delivery_id}")
            
            return delivery_id
            
        except Exception as e:
            self.logger.error(f"创建交货单失败: {str(e)}")
            raise

    # ==================== 返利政策相关方法 ====================
    
    def create_and_approve_rebate_policy(self, policy_name=None, policy_code=None):
        """
        创建、提交并审批通过返利政策的完整流程公共方法
        
        :param policy_name: 返利政策名称，如果为None则自动生成
        :param policy_code: 返利政策编码，如果为None则自动生成
        :return: 包含返利政策ID、编码、名称和状态的字典
        """
        try:
            # 1. 生成返利政策基本信息
            if not policy_name:
                policy_name = f"自动化返利政策_{self.mock_util.get_timestamp()}"
            if not policy_code:
                policy_code = self.mock_util.generate_unique_code(tag="AT_REB")
            
            self.logger.info(f"开始创建返利政策: {policy_name} ({policy_code})")
            
            # 2. 创建返利政策
            api_path = self.get_api_path("REB-返利政策-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 设置返利政策参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["policyName", "policyCode", "periodBeginAt", "periodEndAt", "status", "rebDocType", "comOrgId", "acquireType", "settAccTypeId", "periodType"], ["params", "request"]
            )
            
            # 设置返利政策数据
            current_time = int(time.time() * 1000)
            set_dict = {
                "policyName": policy_name,
                "policyCode": policy_code,
                "periodBeginAt": current_time,
                "periodEndAt": current_time + 365 * 24 * 60 * 60 * 1000,  # 一年后
                "status": "DRAFT",
                "rebDocType": "SO",
                "comOrgId": {"id": 14507001},
                "acquireType": "AMT",
                "settAccTypeId": {"id": 14007001},
                "periodType": "MONTH"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送创建请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 获取创建的返利政策ID
            policy_data = response.get("data", {}).get("data", {})
            policy_id = policy_data.get("id")
            self.logger.info(f"返利政策创建成功，ID: {policy_id}")
            
            # 3. 提交返利政策
            api_path = self.get_api_path("REB-返利政策-提交审批服务")
            params, url = self.get_api_params(api_path)
            
            # 设置提交参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": policy_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送提交请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            self.logger.info(f"返利政策提交成功，ID: {policy_id}")
            
            # 4. 审批通过返利政策
            # 等待一下，确保审批任务已创建
            time.sleep(2)
            
            # 直接使用返利政策审批通过服务
            api_path = self.get_api_path("REB-返利政策-审批通过服务")
            params, url = self.get_api_params(api_path)
            
            # 设置审批参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": policy_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送审批请求
            approve_response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(approve_response)
            
            self.logger.info(f"返利政策审批通过成功，政策ID: {policy_id}")
            
            # 5. 验证返利政策状态
            time.sleep(2)  # 等待状态更新
            policy_info = self.db.query(
                "SELECT id, policy_code, status FROM rebate_policy_head_tr WHERE id = %s",
                [policy_id]
            )
            
            if policy_info:
                status = policy_info[0]['status']
                self.logger.info(f"返利政策最终状态: {status}")
                
                if status != "ENABLED":
                    self.logger.warning(f"返利政策状态不是ENABLED，当前状态: {status}")
            
            # 6. 记录结果
            result = {
                "policy_id": policy_id,
                "policy_code": policy_code,
                "policy_name": policy_name,
                "status": "ENABLED"
            }
            
            a.json(result, "返利政策创建和审批结果")
            self.logger.info(f"返利政策完整流程完成: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建和审批返利政策失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    SlsBase.setup_class()
    print(SlsBase.nickname)
    print(SlsBase.ORDER_TYPES)
    print(SlsBase.ORDER_LINE_TYPES)
    print(SlsBase.ORDER_TYPE_LINE_COMBINATIONS)