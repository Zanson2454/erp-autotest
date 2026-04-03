"""
销售交货单测试基类
提供销售订单创建和交货单相关功能
"""

import random
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_del import ScmDelBaseTest
from utils.param_util import ParamUtil


class SlsDelBaseTest(ScmDelBaseTest):
    """销售交货单测试基类，继承自 ScmDelBaseTest，并添加销售订单创建功能"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化 - 加载销售模块配置"""
        super().setup_class()
        cls.load_api_configs()
        cls.load_cache_data()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载销售交货依赖的销售 API 配置。"""
        # 加载销售模块API配置
        sls_api_path = Path(project_root) / "config" / "api" / "scm_sls" / "sls_api_path.yaml"
        sls_api_params_path = Path(project_root) / "config" / "api" / "scm_sls" / "sls_api_params.yaml"
        cls.sls_apis = cls.yaml_util.read_yaml(sls_api_path).get("apis", {})
        cls.sls_api_params = cls.yaml_util.read_yaml(sls_api_params_path).get("api_params", {})

    @classmethod
    def load_cache_data(cls):
        """加载销售交货依赖缓存。"""
        # 加载销售模块配置（用于创建销售订单）
        cls.sls_cache_data = cls.load_sql_cache(
            sql_config_path=project_root / "config" / "erp" / "sls_init_sql.yaml",
            cache_key="sls_init_cache",
            db_config_name="erp_db",
            cache_dir="testdata/cache",
        )

    @classmethod
    def bind_context(cls):
        """绑定销售交货上下文。"""
        # 初始化销售订单相关属性
        cls._init_sls_order_attributes()

        cls.logger.info(f"✅ sls_cache_data 加载完成: {cls.sls_cache_data is not None}")
    
    @classmethod
    def _init_sls_order_attributes(cls):
        """初始化销售订单相关的属性"""
        # 初始化订单配置数据
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.curr_id = currency_info[0].get("curr_id")
            else:
                cls.curr_id = 2000001  # 默认货币ID（人民币 CNY）
            
            exchange_rate_type_info = cls.init_data.get("exchange_rate_type_info") or []
            if exchange_rate_type_info:
                cls.exchange_rate_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                cls.exchange_rate_type_id = None
        else:
            cls.curr_id = 2000001
            cls.exchange_rate_type_id = None
        
        # 初始化MD数据
        if cls.md_cache_data:
            partner_info = cls.md_cache_data.get("partner_info") or {}
            cust_info = partner_info.get("cust_info") or []
            if cust_info:
                cls.cust_id = cust_info[0].get("id")
            
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
            
            mat_info = cls.md_cache_data.get("mat_info") or {}
            mat_md = mat_info.get("mat_md") or {}
            finp = mat_md.get("FINP") or []
            if finp:
                cls.mat_id = finp[0].get("id")
                cls.mat_code = finp[0].get("mat_code")
                cls.mat_name = finp[0].get("mat_name")
        
        # 初始化销售配置数据
        if cls.sls_cache_data:
            sls_config = cls.sls_cache_data.get("sls_config") or {}
            cls.so_type_info = sls_config.get("so_type_info") or []
            for so_type in cls.so_type_info:
                if so_type.get("so_type_code") == "STND":
                    cls.stnd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "THRD":
                    cls.thrd_so_type_id = so_type.get("id")
                if so_type.get("so_type_code") == "CENT":
                    cls.cent_so_type_id = so_type.get("id")
            
            cls.so_item_type_info = sls_config.get("so_item_type_info") or []
            for so_item_type in cls.so_item_type_info:
                if so_item_type.get("so_item_type_code") == "NORM":
                    cls.stnd_so_item_type_id = so_item_type.get("id")
        
        # 初始化销售订单相关临时变量
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
        cls.render_qty = random.randint(1,9)  # 生成1-9之间的随机整数
        cls.so_data_render = None
        cls.so_data_price = None
        cls.priceIdempotent = None
        cls.so_head_data = None
    
    def get_sls_api_path(self, api_key):
        """
        获取销售模块API路径
        """
        return ParamUtil.get_api_path(self.sls_apis, api_key)
    
    def get_sls_api_params(self, api_path, with_query_params=None):
        """
        获取销售模块API请求参数和完整URL
        """
        return ParamUtil.get_api_params(self.sls_api_params, api_path, with_query_params)

    def get_cross_module_api_path(self, module_name, api_key):
        if module_name == "sls":
            return ParamUtil.get_api_path(self.sls_apis, api_key)
        return super().get_api_path(api_key) if hasattr(super(), "get_api_path") else None

    def get_cross_module_api_params(self, module_name, api_path, with_query_params=None):
        if module_name == "sls":
            return ParamUtil.get_api_params(self.sls_api_params, api_path, with_query_params)
        return super().get_api_params(api_path, with_query_params=with_query_params) if hasattr(super(), "get_api_params") else (None, None)
    
    # ==================== 销售订单相关方法（从 scm_sls 复制）====================
    
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
            
            # 7. 保存或提交
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
        sls_api_key = "SLS-销售-订单创建初始化服务"
        api_path = self.get_sls_api_path(sls_api_key)
        params, url = self.get_sls_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["btClass"], ["params", "request"]
        )
        set_dict = {
            "btClass": "SALES"
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        
        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
        self.assert_util.assert_response_data(response)
        
        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
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
        sls_api_key = "SLS-销售-客户选择渲染处理"
        api_path = self.get_sls_api_path(sls_api_key)
        params, url = self.get_sls_api_params(api_path)
        params["params"] = {
            "custId": self.cust_id
        }
       
        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
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
        so_schl_del_date = self.mock_util.get_timestamp(timestamp=True, day_offset=3)

        sls_api_key = "销售订单获取相关方数据服务"
        api_path = self.get_sls_api_path(sls_api_key)
        params, url = self.get_sls_api_params(api_path)
        
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["custId", "slsPerson", "slsPhone", "slsPersonName", "currExchangeRateType", "soDocDate", "priceCalcDate", "soItems"], ["params", "request"]
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
        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
        self.assert_util.assert_response_data(response)
        self.sls_partner_links = response.get("data", {}).get("data", {}).get("slsPartnerLinks", [])

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

        sls_api_key = "SLS-销售-物料选择后渲染处理服务"
        api_path = self.get_sls_api_path(sls_api_key)
        params, url = self.get_sls_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params, [
                "addrId", "custId", "slsComId", "slsDcId", "slsOrgId", "invLoc", "invOrg", "soDocDate", "soTypeId", "baseCurrId", "slsCurrId",
                "slsPartnerLinks", "soItems"
            ], ["params", "request"]
        )
        set_dict = {
            "addrId": {"id": self.addr_id},
            "addrDetail": self.addr_detail,
            "baseCurrId": {"id": self.curr_id},
            "slsCurrId": {"id": self.curr_id},
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

        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
        self.so_data_render = response.get("data", {}).get("data", {})
        self.assert_util.assert_response_data(response)
        self.so_code = self.so_data_render.get("soCode")
        self.assert_util.assert_by_operator(self.so_code, "not_empty", message="检查订单号是否获取到")
        
    def _calculate_pricing(self):
        """自动定价"""
        
        if not self.so_data_render:
            self._render_order_line()
            
        sls_api_key = "SLS-销售订单-前端定价服务"
        api_path = self.get_sls_api_path(sls_api_key)
        params, url = self.get_sls_api_params(api_path)
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

        response, _ = self.standard_api_call(
            api_key=sls_api_key,
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            cross_module_name="sls",
        )
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
            if not self.so_data_price:
                self._calculate_pricing()

            sls_api_key = "SLS-销售订单-保存服务"
            api_path = self.get_sls_api_path(sls_api_key)
            params, url = self.get_sls_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "soCode", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                    "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                    "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                    "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks",
                    "soTypeId", "isFixedExchRate", "reCalculate", "rebateAmt", "netAmt"
                ], ["params", "request"]
            )
            
            set_dict = self.so_data_price
            set_dict["syncSubmit"] = "false"
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key=sls_api_key,
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                cross_module_name="sls",
            )
            self.assert_util.assert_response_data(response)
            
            # 保存订单ID供后续使用
            response_data = response.get("data", {}).get("data", {})
            self.so_head_id_save = response_data.get("id")
            self.so_head_data = response_data
            self.priceIdempotent = response_data.get("priceIdempotent")
            self.so_status = response_data.get("soStatus")
            self.so_item_data = response_data.get("soItems")
            self.so_item_id = response_data.get("soItems")[0].get("id")
            self.assert_util.assert_by_operator(self.so_head_id_save, "not_empty", message="保存订单失败，未返回订单ID")
            self.assert_util.assert_by_operator(self.priceIdempotent, "not_empty", message="保存订单失败，未返回价格幂等码")
            self.assert_util.assert_by_operator(self.so_status, "=", "DRAFT", message="保存订单失败，订单状态不是草稿")      
            
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

            sls_api_key = "SLS-销售订单-保存服务"
            api_path = self.get_sls_api_path(sls_api_key)
            params, url = self.get_sls_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "soCode", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                    "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                    "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                    "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks",
                    "soTypeId", "isFixedExchRate", "reCalculate", "syncSubmit"
                ], ["params", "request"]
            )
            
            set_dict = self.so_data_price
            set_dict["syncSubmit"] = "true"
            
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key=sls_api_key,
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                cross_module_name="sls",
            )
            self.assert_util.assert_response_data(response)
            self.so_head_id_submit = response.get("data", {}).get("data", {}).get("id")
            
            return self.so_head_id_submit
        except Exception as e:
            self.logger.error(f"提交订单失败: {str(e)}")
            raise
    
    # ==================== 交货单相关方法 ====================
    
    def create_delivery_order(self, so_id):
        """
        基于销售订单创建交货单的公共方法
        使用分组API获取草稿数据，然后调用保存并提交API
        :param so_id: 销售订单ID
        :return: 交货单ID（如果API返回的话）
        """
        try:
            # 1. 查询销售订单的完整数据
            order_data = self.query_service.query("""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = %s
            """, (so_id,))
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {so_id}")
            
            so_code = order_data[0].get('so_code')
            if not so_code:
                raise ValueError(f"销售订单没有订单号，订单ID: {so_id}")
            
            # 2. 获取订单行ID列表
            so_item_ids = []
            for item in order_data:
                if item.get('i.id'):
                    so_item_ids.append(item['i.id'])
            
            if not so_item_ids:
                raise ValueError(f"销售订单没有订单行数据，订单ID: {so_id}")
            
            # 3. 调用分组API获取交货单草稿数据
            group_response = self._group_sls_items(so_item_ids)
            dn_draft = self._extract_dn_draft(group_response)
            
            # 4. 调用保存并提交API
            self._save_submit_delivery_note(dn_draft, so_code)
            
            # 5. 查询交货单ID
            self._async_delay(1, "等待交货单创建完成")
            
            dn_id = None
            max_retries = 3
            for attempt in range(max_retries):
                wait_time = 0.5 + attempt * 0.5  # 0.5秒、1秒、1.5秒
                if attempt > 0:
                    self._async_delay(wait_time, "重试查询交货单ID")
                
                # 通过订单号查询交货单
                query_result = self.query_service.query("""
                    SELECT DISTINCT h.id as dn_id
                    FROM del_dn_head_tr h
                    INNER JOIN del_dn_item_tr i ON h.id = i.dn_id
                    WHERE i.doc_code = %s OR h.doc_code = %s
                    ORDER BY h.created_at DESC 
                    LIMIT 1
                """, (so_code, so_code))
                
                if query_result:
                    dn_id = query_result[0].get("dn_id")
                    self.logger.info(f"成功查询到交货单ID: {dn_id} (尝试 {attempt + 1}/{max_retries})")
                    break
            
            if not dn_id:
                self.logger.warning(f"创建交货单后无法查询到交货单ID，订单号: {so_code}, 订单ID: {so_id} (已重试 {max_retries} 次)，返回空字典")
                return {}
            
            self.logger.info(f"成功创建销售交货单: dn_id={dn_id}, so_id={so_id}, so_code={so_code}")
            return dn_id
            
        except Exception as e:
            self.logger.error(f"创建交货单失败: {str(e)}")
            raise
    
    def _group_sls_items(self, so_item_id_list):
        """调用销售订单行分组接口"""
        api_path = self.get_api_path("DEL-根据订单项目行分组查询创建交货单服务")
        params, url = self.get_api_params(api_path)
        
        # 构造请求参数：传入订单行ID列表
        request_items = []
        for item_id in so_item_id_list:
            request_items.append({"id": item_id})
        
        params["params"]["request"] = request_items
        
        # URL中添加 tmodule=SCM_SLS（与curl命令保持一致）
        url = f"{url}?tmodule=SCM_SLS" if "?" not in url else f"{url}&tmodule=SCM_SLS"
        
        response, _ = self.standard_api_call(
            api_key="DEL-根据订单项目行分组查询创建交货单服务",
            set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"]
        )
        self.assert_util.assert_response_success(response)
        
        return response
    
    def _extract_dn_draft(self, group_response):
        """从分组接口响应中提取交货单草稿"""
        # 分组API的响应结构：data.data 是一个数组，每个元素包含 values 字段
        dn_draft_list = group_response.get("data", {}).get("data", [])
        if not dn_draft_list:
            raise ValueError("销售订单行分组接口未返回交货单草稿数据")
        
        # 返回第一个分组的数据
        dn_draft = dn_draft_list[0].get("values", {})
        if not dn_draft:
            raise ValueError("销售订单行分组接口返回的交货单草稿数据为空")
        
        return dn_draft
    
    def _save_submit_delivery_note(self, dn_draft, so_code):
        """保存并提交交货单"""
        api_path = self.get_api_path("DEL-销售交货单保存并提交服务")
        params, url = self.get_api_params(api_path)
        
        # 构造请求参数：request 是一个数组，包含完整的交货单数据
        # 从草稿数据中获取必要字段，并确保 delStatus 为 "DRAFT"
        request_item = dn_draft.copy()
        
        # 确保必要字段存在
        if not request_item.get("delStatus"):
            request_item["delStatus"] = "DRAFT"
        
        if not request_item.get("dnCode"):
            # 如果没有dnCode，生成一个临时编码（实际应该由系统生成）
            import time
            timestamp = int(time.time() * 1000)
            request_item["dnCode"] = f"DN{timestamp}"
        
        # 设置 docCode 为销售订单号
        request_item["docCode"] = so_code
        
        params["params"]["request"] = [request_item]
        
        # URL中添加 tmodule=SCM_SLS（与curl命令保持一致）
        url = f"{url}?tmodule=SCM_SLS" if "?" not in url else f"{url}&tmodule=SCM_SLS"
        
        response, _ = self.standard_api_call(
            api_key="DEL-销售交货单保存并提交服务",
            set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"]
        )
        self.assert_util.assert_response_success(response)
        
        return response
    
    def _query_dn_by_so_code(self, so_code):
        """
        根据销售订单号查询交货单ID
        :param so_code: 销售订单号
        :return: 交货单ID
        """
        try:
            # 调用交货单查询API
            api_path = self.get_api_path("DEL-交货单公共-数据分页查询服务")
            params, url = self.get_api_params(api_path)
            
            # 构造查询条件：docCode CONTAINS so_code 且 btClass EQ "SLS"
            condition_group = {
                "type": "ConditionGroup",
                "logicOperator": "AND",
                "conditions": [
                    {
                        "type": "ConditionGroup",
                        "logicOperator": "AND",
                        "conditions": [
                            {
                                "key": "Ozo3U4Zl5AFSi6_w6feIM",
                                "type": "ConditionLeaf",
                                "leftValue": {
                                    "id": "vLLOT8u9AqMiky3ZDpmMJ",
                                    "key": "vLLOT8u9AqMiky3ZDpmMJ",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "VAR",
                                    "varValue": [{"valueKey": "docCode", "valueName": "docCode"}]
                                },
                                "operator": "CONTAINS",
                                "rightValue": {
                                    "key": "Fi2UVBJQH32Q7ZZl-N0jP",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "CONST",
                                    "constValue": so_code
                                }
                            },
                            {
                                "key": "xhLSNiWR2rv2jWnDblo0X",
                                "type": "ConditionLeaf",
                                "leftValue": {
                                    "id": "68FIYZH4E52oRK3Ao8Ajl",
                                    "key": "68FIYZH4E52oRK3Ao8Ajl",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "VAR",
                                    "varValue": [{"valueKey": "btClass", "valueName": "btClass"}]
                                },
                                "operator": "EQ",
                                "rightValue": {
                                    "key": "sKOsN5wFcRQPZot-rVk3M",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "CONST",
                                    "constValue": "SLS"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # 设置查询参数 - 注意：pageable 应该直接放在 request 下，而不是嵌套
            # 使用 ParamUtil.filter_post_body_fields 来过滤字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            
            # 设置查询参数
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionGroup": condition_group
                },
                "fields": [
                    {"name": "id", "type": "TEXT"},
                    {"name": "dnCode", "type": "TEXT"},
                    {"name": "docCode", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送查询请求
            query_response, _ = self.standard_api_call(
                api_key="DEL-交货单公共-数据分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(query_response)
            
            # 从响应中获取交货单ID
            query_data = query_response.get("data", {}).get("data", {})
            # 注意：响应结构可能是 {"total": 0, "data": []} 或直接是 {"records": []}
            records = query_data.get("records", []) or query_data.get("data", [])
            
            if records and len(records) > 0:
                # 返回第一个交货单的ID
                dn_id = records[0].get("id")
                if dn_id:
                    return dn_id
            
            raise ValueError(f"根据销售订单号 {so_code} 查询不到交货单")
            
        except Exception as e:
            self.logger.error(f"查询交货单失败: {str(e)}")
            raise
