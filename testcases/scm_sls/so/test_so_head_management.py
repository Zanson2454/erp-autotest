from sqlite3.dbapi2 import Timestamp
import pytest
import json
import random
from datetime import datetime
from pathlib import Path
import allure
import sys


# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.report_util import a, case_decorator
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil


@allure.epic("销售管理")
@allure.feature("销售订单主表管理")
class TestSoHeadManagement(SlsBase):
    """销售订单主表（so_head）增删改查及接口专项测试类"""

    # 定义要测试的订单类型
    TEST_ORDER_TYPES = ["STND", "THRD", "CENT"]

    @classmethod
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
             
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

        a.text(f"初始化渲染数量: {cls.render_qty}", "初始化信息")
        a.text("测试类初始化完成", "初始化信息")

    @case_decorator(
        story="销售订单",
        title="初始化销售订单",
        description="验证销售订单初始化接口",
        severity="critical",
        order=1,
        tags=["销售订单", "初始化"]
    )
    def test_init_sales_order(self, order_type="STND"):
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
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        self.assert_util.assert_response_success(response)
    
        # 从嵌套结构中获取数据
        response_data = response.get("data", {}).get("data", {})

        # 保存销售人员信息供后续使用
        self.sls_person_obj = response_data.get("slsPerson")
        self.sls_phone = response_data.get("slsPhone")
        if self.sls_person_obj:
            self.sls_person_name = self.sls_person_obj.get("name")

        a.json(self.sls_person_obj, "销售人员信息")
        a.text(f"销售订单创建初始化完成，订单类型: {order_type}", "初始化完成")

        # 验证必要字段
        assert self.sls_person_obj is not None, "销售人员信息为空"
        assert self.sls_phone is not None, "销售人员电话为空"
        assert self.sls_person_name is not None, "销售人员姓名为空"

    @case_decorator(
        story="销售订单",
        title="查询客户信息",
        description="验证客户信息查询接口",
        severity="critical",
        order=2,
        tags=["销售订单", "客户信息"]
    )
    def test_query_customer_info(self):
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
        self.logger.info(f"response_data: {response_data}")
        self.addr_id = response_data.get("addrId").get("id")
        self.addr_detail = response_data.get("addrDetail")
        self.cust_person_name = response_data.get("custPersonName")
        self.cust_phone = response_data.get("custPhone")
        
        a.text("客户信息查询完成", "步骤信息")
        a.json(response,"响应数据")
       

    @case_decorator(
        story="销售订单",
        title="查询相关方",
        description="验证相关方查询接口",
        severity="critical",
        order=3,
        tags=["销售订单", "相关方"]
    )
    def test_query_partner(self):
        """查询相关方"""
        if not self.sls_person_obj:
            self.test_init_sales_order()
        if not self.sls_phone or not self.sls_person_name:
            self.test_query_customer_info()
            
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
        
        a.text("相关方查询完成", "步骤信息")
        a.json(responese, "响应数据")


    @case_decorator(
        story="销售订单",
        title="渲染订单行",
        description="验证订单行渲染接口",
        severity="critical",
        order=70,
        tags=["销售订单", "订单行渲染"]
    )
    def test_render_order_line(self, order_type="STND"):
        """渲染订单行

        Args:
            order_type: 订单类型，默认为标准销售(STND)
        """
        if not self.sls_person_obj:
            self.test_init_sales_order()
        if not self.sls_phone or not self.sls_person_name:
            self.test_query_customer_info()
        if not self.sls_partner_links:
            self.test_query_partner()
        if not self.addr_id:
            self.test_query_customer_info()

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
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")

        

    @case_decorator(
        story="销售订单",
        title="自动定价",
        description="验证销售订单自动定价接口",
        severity="critical",
        order=80,
        tags=["销售订单", "定价"]
    )
    def test_calculate_pricing(self):
        """自动定价"""
        
        if not self.so_data_render:
            self.test_render_order_line()
            
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
    
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
       

    

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-保存服务",
        description="验证SLS_SO_SAVE_ACTION_SERVICE接口",
        severity="critical",
        order=90,
        tags=["销售订单", "保存", "SLS_SO_SAVE_ACTION_SERVICE"]
    )
    def test_so_save(self):
        """SLS-销售订单-保存服务"""
        try:
            # 确保有可保存的订单数据
            if  not self.so_data_price:
                self.test_calculate_pricing()

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
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"销售订单保存成功，订单ID: {self.so_head_id_save}", "保存结果")
            
        except Exception as e:
            a.text(str(e), "保存失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-提交服务",
        description="验证SLS_SO_SUBMIT_ACTION_SERVICE接口",
        severity="critical",
        order=110,
        tags=["销售订单", "提交", "SLS_SO_SUBMIT_ACTION_SERVICE"]
    )
    def test_so_submit(self):
        """SLS-销售订单-提交服务"""
        try:
            # 确保有可提交的订单
            if not self.so_data_price:
                self.test_calculate_pricing()

            api_path = self.get_api_path("SLS-销售订单-提交服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,  [
                    "soCode", "soDocDate", "priceCalcDate", "custId", "addrId", "addrDetail",
                    "custPersonName", "custPhone", "slsPerson", "slsPhone", "slsPersonName",
                    "slsOrgId", "slsDcId", "slsComId", "slsCurrId", "baseCurrId",
                    "currExchangeRateType", "exchRate", "soItems", "slsPartnerLinks",
                    "soTypeId", "isFixedExchRate", "reCalculate"
                ], ["params", "request"]
            )
            
            set_dict = self.so_data_price
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="提交销售订单")
            self.assert_util.assert_response_data(response)
            self.so_head_id_submit = response.get("data", {}).get("data", {}).get("id")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"销售订单提交成功，订单ID: {self.so_head_id_submit}", "提交结果")
            
        except Exception as e:
            a.text(str(e), "提交失败原因")
            raise

   


    # @case_decorator(
    #     story="销售订单",
    #     title="SLS-销售订单-触发行项目类型变更",
    #     description="验证sls_so_item_change_render_service接口",
    #     severity="critical",
    #     order=140,
    #     tags=["销售订单", "项目类型变更", "sls_so_item_change_render_service"]
    # )
    # def test_so_item_change_render_service(self):
    #     """SLS-销售订单-触发行项目类型变更"""
    #     try:
    #         # 确保有订单行数据
    #         if not hasattr(self, 'so_items') or not self.so_items:
    #             self.test_07_render_order_line()

    #         api_path = self.get_api_path("SLS-销售订单-触发行项目类型变更")
    #         params, url = self.get_api_params(api_path)
    #         # 使用已有的订单行数据
    #         params['params']['request']['soItemId'] = self.so_items[0]['id']
    #         params['params']['request']['newItemTypeId'] = SlsBase.get_order_line_type_id("SERV")  # 切换为服务类型
    #         response = self.http.post(url, json=params)
    #         a.json(params, "请求数据")
    #         a.json(response, "响应数据")
    #         self.assert_util.assert_response_success(response)
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="按订单号查询订单",
    #     description="验证按订单号查询订单接口",
    #     severity="critical",
    #     order=150,
    #     tags=["销售订单", "查询", "订单号查询"]
    # )
    # def test_query_orders_by_so_code(self):
    #     """按订单号查询订单"""
    #     try:
    #         # 确保有可查询的订单
    #         if not hasattr(self, 'order_id') or not self.order_id:
    #             self.test_submit_multiple_order_types()

    #         url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         data = self.sls_api_params.get(url, {})
    #         # 构建按订单号查询的条件
    #         data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "soCode",
    #                     "operator": "EQ",
    #                     "rightValue": {
    #                         "constValue": self.order_id
    #                     }
    #                 }]
    #             }]
    #         }

    #         result = self.http.post(url, json=data, description="按订单号查询订单")
    #         response_data = result.get("data", {}).get("data", {}).get("data", [])
    #         a.json(data, "查询请求参数")
    #         a.json(response_data, "查询结果数据")

    #         self.assert_util.assert_response_success(result)
    #         self.assert_util.assert_gt(len(response_data), 0, "未找到匹配的订单数据")
    #         self.assert_util.assert_eq(response_data[0]["id"], self.order_id, "查询到的订单ID与创建的订单ID不匹配")
    #     except Exception as e:
    #         a.text(str(e), "查询失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="按状态查询订单",
    #     description="验证按状态查询订单接口",
    #     severity="critical",
    #     order=160,
    #     tags=["销售订单", "查询", "状态查询"]
    # )
    # def test_query_orders_by_status(self):
    #     """按状态查询订单"""
    #     try:
    #         url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         data = self.sls_api_params.get(url, {})
    #         # 构建按状态查询的条件
    #         data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "status",
    #                     "operator": "IN",
    #                     "rightValue": {
    #                         "constValue": ["DRAFT", "EFFECT", "APPROVING", "CANCELLED"]
    #                     }
    #                 }]
    #             }]
    #         }

    #         result = self.http.post(url, json=data, description="按状态查询订单")
    #         response_data = result.get("data", {}).get("data", {}).get("data", [])
    #         a.json(data, "查询请求参数")
    #         a.json(response_data, "查询结果数据")

    #         self.assert_util.assert_response_success(result)
    #         self.assert_util.assert_gt(len(response_data), 0, "未找到匹配的订单数据")

    #         # 验证返回结果中的状态都在请求的状态列表中
    #         requested_status = set(["DRAFT", "EFFECT", "APPROVING", "CANCELLED"])
    #         actual_status = set(item["status"] for item in response_data)
    #         self.assert_util.assert_true(actual_status.issubset(requested_status), f"查询结果包含未请求的状态: {actual_status - requested_status}")
    #     except Exception as e:
    #         a.text(str(e), "查询失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="删除单个订单",
    #     description="验证单个订单删除接口",
    #     severity="critical",
    #     order=170,
    #     tags=["销售订单", "删除", "单个删除"]
    # )
    # def test_delete_single_order(self):
    #     """删除单个销售订单"""
    #     try:
    #         # 确保有可删除的订单
    #         if not hasattr(self, 'order_id') or not self.order_id:
    #             self.test_submit_multiple_order_types()

    #         url = self.sls_api_paths["订单管理"]["删除订单"]
    #         data = self.sls_api_params.get(url, {})
    #         data['params']['request']['orderId'] = self.order_id

    #         result = self.http.post(url, json=data, description="删除单个订单")
    #         a.json(data, "删除请求参数")
    #         a.json(result, "删除响应数据")

    #         self.assert_util.assert_response_success(result)

    #         # 验证订单已被删除
    #         query_url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         query_data = self.sls_api_params.get(query_url, {})
    #         query_data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "id",
    #                     "operator": "EQ",
    #                     "rightValue": {
    #                         "constValue": self.order_id
    #                     }
    #                 }]
    #             }]
    #         }

    #         query_result = self.http.post(query_url, json=query_data, description="验证订单是否已删除")
    #         query_response_data = query_result.get("data", {}).get("data", {}).get("data", [])
    #         self.assert_util.assert_eq(len(query_response_data), 0, f"订单删除失败，仍能查询到订单ID: {self.order_id}")
    #     except Exception as e:
    #         a.text(str(e), "删除失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="批量删除订单",
    #     description="验证批量订单删除接口",
    #     severity="critical",
    #     order=180,
    #     tags=["销售订单", "删除", "批量删除"]
    # )
    # def test_batch_delete_orders(self):
    #     """批量删除销售订单"""
    #     try:
    #         # 创建多个订单用于批量删除测试
    #         order_ids = []
    #         for _ in range(3):
    #             self.order_id = None
    #             self.so_items = None
    #             self.so_price_data = None
    #             self.test_01_init_sales_order()
    #             self.test_07_render_order_line()
    #             self.test_08_calculate_pricing()
    #             order_id = self._save_or_submit_order(submit=True)
    #             order_ids.append(order_id)

    #         url = self.sls_api_paths["订单管理"]["批量删除订单"]
    #         data = self.sls_api_params.get(url, {})
    #         data['params']['request']['orderIds'] = order_ids

    #         result = self.http.post(url, json=data, description="批量删除订单")
    #         a.json(data, "批量删除请求参数")
    #         a.json(result, "批量删除响应数据")

    #         self.assert_util.assert_response_success(result)

    #         # 验证所有订单已被删除
    #         query_url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         query_data = self.sls_api_params.get(query_url, {})
    #         query_data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "id",
    #                     "operator": "IN",
    #                     "rightValue": {
    #                         "constValue": order_ids
    #                     }
    #                 }]
    #             }]
    #         }

    #         query_result = self.http.post(query_url, json=query_data, description="验证订单是否已删除")
    #         query_response_data = query_result.get("data", {}).get("data", {}).get("data", [])
    #         self.assert_util.assert_eq(len(query_response_data), 0, f"批量删除失败，仍能查询到{len(query_response_data)}个订单")
    #     except Exception as e:
    #         a.text(str(e), "批量删除失败原因")
    #         raise

    @case_decorator(
        story="销售订单",
        title="销售订单页面完整查询",
        description="验证SLS_SO_QUERY_DETAIL_EVENT_SERVICE接口",
        severity="critical",
        order=120,
        tags=["销售订单", "查询", "SLS_SO_QUERY_DETAIL_EVENT_SERVICE"]
    )
    def test_so_query_detail_event_service(self):
        """销售订单页面完整查询"""
        try:
            # 确保有可查询的订单ID
            if not self.so_head_id_save:
                self.test_so_save()

            api_path = self.get_api_path("销售订单页面完整查询")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {
                "id": self.so_head_id_save
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="销售订单页面完整查询")
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "查询失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SO-查看定价记录服务",
        description="验证SO_QUERY_PRICE_RECORDS_EVENT_SERVICE接口",
        severity="critical",
        order=130,
        tags=["销售订单", "定价记录", "SO_QUERY_PRICE_RECORDS_EVENT_SERVICE"]
    )
    def test_so_query_price_records_event_service(self):
        """SO-查看定价记录服务"""
        try:
            # 确保有可查询定价记录的订单ID和幂等码
            if not self.so_head_id_save or not self.priceIdempotent:
                self.test_so_save()

            api_path = self.get_api_path("SO-查看定价记录服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["soId", "priceIdempotent"], ["params", "request"]
            )
            set_dict = {
                "soItem": self.so_item_data[0],
                "soPartnerLinks": self.sls_partner_links,
                "priceIdempotent": self.priceIdempotent
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="查看定价记录")
            self.assert_util.assert_response_data(response)
            so_priceItem_records = response.get("data", {}).get("data", {}).get("soPriceItemRecords", [])
            self.assert_util.assert_by_operator(so_priceItem_records, "not_empty",message="定价记录ID不能为空")
         
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            # 验证返回的定价记录数据
        

        except Exception as e:
            a.text(str(e), "查询定价记录失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SO-维护发货计划行服务",
        description="验证SO_INIT_SCHEDULE_LINE_EVENT_SERVICE接口",
        severity="critical",
        order=140,
        tags=["销售订单", "发货计划", "SO_INIT_SCHEDULE_LINE_EVENT_SERVICE"]
    )
    def test_so_init_schedule_line_event_service(self):
        """SO-维护发货计划行服务"""
        try:
            # 确保有可维护发货计划的订单行ID
            if not self.so_item_id:
                self.test_so_save()

            api_path = self.get_api_path("SO-维护发货计划行服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["currentItem", "soHeader", "soItems"], ["params", "request"]
            )
            
            # 设置发货计划参数
            schedule_date = self.mock_util.get_timestamp(timestamp=True, day_offset=7)  # 7天后发货
            set_dict = {
                "currentItem": self.so_item_data[0],
                "soHeader": self.so_head_data,  # 使用渲染时的数量
                "soItems": self.so_item_data
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params, description="维护发货计划行")
            self.assert_util.assert_response_data(response)
        
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"发货计划行维护完成，计划发货日期: {schedule_date}", "维护结果")
            
        except Exception as e:
            a.text(str(e), "维护发货计划行失败原因")
            raise
