"""
销售管理模块的测试初始化
提供配置加载等通用功能
"""
import sys
import random
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
        cls.sls_api_path = Path(project_root) / "testdata" / "scm_sls" / "sls_api_path.yaml"
        cls.sls_api_params = Path(project_root) / "testdata" / "scm_sls" / "sls_api_params.yaml"
        
        # 加载API路径配置和参数配置
        cls.apis = cls.yaml_util.read_yaml(cls.sls_api_path).get("apis", {})
        cls.api_params = cls.yaml_util.read_yaml(cls.sls_api_params).get("api_params", {})
        
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
        
        
        
    # 初始化订单配置数据
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
            cls.coun_id = cls.init_data.get("country_info",[])[0].get("coun_id")
            cls.exchange_rate_type_id = cls.init_data.get("exchange_rate_type_info",[])[0].get("exchange_rate_type_id")
        # 初始化MD
        if cls.md_cache_data:
            cls.cust_id = cls.md_cache_data.get("partner_info",{}).get("cust_info",[])[0].get("id")
            cls.logger.info(f"cust_id: {cls.cust_id}")
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.sls_dc_id = cls.md_cache_data.get("org_info",{}).get("sls_dc_md",[])[0].get("id")
            cls.sls_org_id = cls.md_cache_data.get("org_info",{}).get("sls_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
            cls.inv_loc_id = cls.md_cache_data.get("org_info",{}).get("inv_loc_info",[])[0].get("id")
            cls.partner_type_id = cls.md_cache_data.get("partner_info",{}).get("partner_type_cf",{}).get("sls_partner_type",[])[0].get("id")
            cls.mat_id = cls.md_cache_data.get("mat_info",{}).get("mat_md",{}).get("FINP",[])[0].get("id")
        
        if cls.sls_cache_data:
            cls.so_type_info = cls.sls_cache_data.get("sls_config",{}).get("so_type_info",[])
            for so_type  in  cls.so_type_info:
                if so_type.get("so_type_code") == "STND":
                    cls.stnd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "THRD":
                    cls.thrd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "CENT":
                    cls.cent_so_type_id = so_type.get("id")
            cls.so_item_type_info = cls.sls_cache_data.get("sls_config",{}).get("so_item_type_info",[])
            for so_item_type in cls.so_item_type_info:
                if so_item_type.get("so_item_type_code") == "NORM":
                    cls.stnd_so_item_type_id = so_item_type.get("id")

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
    
    def create_sales_order(self, order_type="STND", submit=False):
        """
        创建销售订单的公共方法
        :param order_type: 订单类型（STND/THRD/CENT），默认为STND
        :param submit: 是否提交订单（True=提交，False=保存为草稿）
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
                    "soTypeId", "isFixedExchRate", "reCalculate"
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

if __name__ == "__main__":
    SlsBase.setup_class()
    print(SlsBase.nickname)
    print(SlsBase.ORDER_TYPES)
    print(SlsBase.ORDER_LINE_TYPES)
    print(SlsBase.ORDER_TYPE_LINE_COMBINATIONS)