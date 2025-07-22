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
        cls.so_price_data = None
        cls.sls_org_obj = None
        cls.mat_obj = None
        cls.order_id = None
        cls.render_qty = random.randint(1, 99)  # 生成1-99之间的随机整数
        cls.so_data_render = None
        cls.so_data_price = None

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
            "baseCurrId": {"id":self.curr_id},
            "slsCurrId": {"id":self.curr_id},
            "custId": {"id": self.cust_id},
            "invLoc": None,
            "invOrg": None,
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
        self.so_data = response.get("data", {}).get("data", {})
        self.assert_util.assert_response_data(response)
        self.so_code = self.so_data.get("soCode")
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
        
        if not self.so_data:
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

        self.so_data["priceCalcDate"] = self.mock_util.get_timestamp(timestamp=True)
        self.so_data["currExchangeRateType"] = self.exchange_rate_type_id
        self.so_data["exchRate"] = 1
        self.so_data["isFixedExchRate"] = False
        self.so_data["soItems"][0]["soItemSlsQty"] = self.render_qty
        set_dict = self.so_data
        ParamUtil.set_request_params(filtered_params, set_dict)

        response = self.http.post(url, json=filtered_params, description="自动定价")
        self.assert_util.assert_response_data(response)
    
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
       

    # def _save_or_submit_order(self, submit=True, order_type="STND"):
    #     """保存或提交订单

    #     Args:
    #         submit: 是否提交订单，True为提交，False为保存
    #         order_type: 订单类型

    #     Returns:
    #         订单ID
    #     """
    #     # 确保所有前置条件已满足
    #     if not hasattr(self, 'so_price_data') or not self.so_price_data:
    #         self.test_08_calculate_pricing()

    #     url = self.sls_api_paths["订单管理"]["提交订单"] if submit else self.sls_api_paths["订单管理"]["保存订单"]
    #     action = "提交" if submit else "保存"

    #     data = self.sls_api_params.get(url, {})
    #     curr_time = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)

    #     # 构建请求参数
    #     data['params']['request']['soTypeId'] = {"id": self.so_type_id}
    #     data['params']['request']['soDocDate'] = curr_time
    #     data['params']['request']['custId'] = {"id": self.cust_id}
    #     data['params']['request']['addrId'] = {"id": self.addr_id}
    #     data['params']['request']['addrDetail'] = self.addr_detail
    #     data['params']['request']['custPersonName'] = self.cust_person_name
    #     data['params']['request']['custPhone'] = self.cust_phone
    #     data['params']['request']['slsPerson'] = self.sls_person_obj
    #     data['params']['request']['slsPhone'] = self.sls_phone
    #     data['params']['request']['slsPersonName'] = self.sls_person_name
    #     data['params']['request']['slsOrgId'] = {"id": self.sls_org_id}
    #     data['params']['request']['slsDcId'] = {"id": self.sls_dc_id}
    #     data['params']['request']['slsComId'] = {"id": self.com_org_id}
    #     data['params']['request']['slsCurrId'] = {"id": self.sls_curr_id}
    #     data['params']['request']['baseCurrId'] = {"id": self.base_curr_id}
    #     data['params']['request']['currExchangeRateType'] = self.exchange_rate_type_id
    #     data['params']['request']['exchRate'] = 1
    #     data['params']['request']['soItems'] = self.so_price_data.get("soItems", [])
    #     data['params']['request']['slsPartnerLinks'] = self.sls_partner_links
    #     data['params']['request']['totalAmt'] = self.so_price_data.get("totalAmt", 0)
    #     data['params']['request']['taxAmt'] = self.so_price_data.get("taxAmt", 0)
    #     data['params']['request']['netAmt'] = self.so_price_data.get("netAmt", 0)

    #     # 如果是提交订单，添加提交相关参数
    #     if submit:
    #         data['params']['request']['submitDate'] = curr_time
    #         data['params']['request']['submitter'] = self.sls_person_name

    #     self.logger.info(f"{action}订单请求参数: {json.dumps(data, indent=2, ensure_ascii=False)}")
    #     a.json(data, f"{action}订单请求参数")

    #     result = self.http.post(url, json=data, description=f"{action}销售订单")
    #     response_data = result.get("data", {}).get("data", {})

    #     # 提取订单ID
    #     order_id = response_data.get("id") or response_data.get('orderId')
    #     if not order_id:
    #         error_msg = f"{action}订单失败，未返回订单ID: {response_data}"
    #         self.logger.error(error_msg)
    #         a.text(error_msg, "错误")
    #         raise ValueError(error_msg)

    #     self.order_id = order_id
    #     a.text(f"销售订单{action}成功，订单ID: {order_id}", f"{action}结果")
    #     self.logger.info(f"销售订单{action}成功，订单ID: {order_id}")

    #     return order_id

    # @case_decorator(
    #     story="销售订单",
    #     title="保存多种类型订单",
    #     description="测试保存不同类型的销售订单",
    #     severity="critical",
    #     order=90,
    #     tags=["销售订单", "保存订单", "多类型"]
    # )
    # def test_save_multiple_order_types(self):
    #     """测试保存多种类型的销售订单"""
    #     for order_type in self.TEST_ORDER_TYPES:
    #         with allure.step(f"保存{order_type}类型订单"):
    #             self.logger.info(f"开始保存{order_type}类型订单")
    #             # 重新初始化订单数据
    #             self.order_id = None
    #             self.so_items = None
    #             self.so_price_data = None

    #             # 初始化订单
    #             self.test_01_init_sales_order(order_type)
    #             # 重新渲染订单行
    #             self.test_07_render_order_line(order_type)
    #             # 重新计算定价
    #             self.test_08_calculate_pricing()
    #             # 保存订单
    #             order_id = self._save_or_submit_order(submit=False, order_type=order_type)

    #             self.assert_util.assert_not_none(order_id, f"保存{order_type}类型订单失败，未生成订单ID")
    #             a.text(f"{order_type}类型订单保存成功，订单ID: {order_id}", "保存结果")

    # @case_decorator(
    #     story="销售订单",
    #     title="提交多种类型订单",
    #     description="测试提交不同类型的销售订单",
    #     severity="critical",
    #     order=100,
    #     tags=["销售订单", "提交订单", "多类型"]
    # )
    # def test_submit_multiple_order_types(self):
    #     """测试提交多种类型的销售订单"""
    #     for order_type in self.TEST_ORDER_TYPES:
    #         with allure.step(f"提交{order_type}类型订单"):
    #             self.logger.info(f"开始提交{order_type}类型订单")
    #             # 重新初始化订单数据
    #             self.order_id = None
    #             self.so_items = None
    #             self.so_price_data = None

    #             # 初始化订单
    #             self.test_01_init_sales_order(order_type)
    #             # 重新渲染订单行
    #             self.test_07_render_order_line(order_type)
    #             # 重新计算定价
    #             self.test_08_calculate_pricing()
    #             # 提交订单
    #             order_id = self._save_or_submit_order(submit=True, order_type=order_type)

    #             self.assert_util.assert_not_none(order_id, f"提交{order_type}类型订单失败，未生成订单ID")
    #             a.text(f"{order_type}类型订单提交成功，订单ID: {order_id}", "提交结果")

    # @case_decorator(
    #     story="销售订单",
    #     title="SLS-销售订单-提交服务",
    #     description="验证SLS_SO_SUBMIT_ACTION_SERVICE接口",
    #     severity="critical",
    #     order=110,
    #     tags=["销售订单", "提交", "SLS_SO_SUBMIT_ACTION_SERVICE"]
    # )
    # def test_submit_action_service(self):
    #     """SLS-销售订单-提交服务"""
    #     try:
    #         # 确保有可提交的订单
    #         if not hasattr(self, 'order_id') or not self.order_id:
    #             self.test_submit_multiple_order_types()

    #         api_path = self.get_api_path("SLS-销售订单-提交服务")
    #         params, url = self.get_api_params(api_path)
    #         # 使用已创建的订单ID
    #         params['params']['request']['orderId'] = self.order_id
    #         response = self.http.post(url, json=params)
    #         a.json(params, "请求数据")
    #         a.json(response, "响应数据")
    #         self.assert_util.assert_response_success(response)
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="物料选择后重新渲染",
    #     description="验证SLS_AFTER_MAT_SELECT_RENDER_SERVICE接口",
    #     severity="critical",
    #     order=120,
    #     tags=["销售订单", "渲染", "SLS_AFTER_MAT_SELECT_RENDER_SERVICE"]
    # )
    # def test_after_mat_select_render(self):
    #     """物料选择后重新渲染"""
    #     try:
    #         # 确保有订单行数据
    #         if not hasattr(self, 'so_items') or not self.so_items:
    #             self.test_07_render_order_line()

    #         api_path = self.get_api_path("物料选择后重新渲染")
    #         params, url = self.get_api_params(api_path)
    #         # 使用已选择的物料和订单行数据
    #         params['params']['request']['matId'] = self.mat_obj['id']
    #         params['params']['request']['soItemId'] = self.so_items[0]['id'] if self.so_items else None
    #         params['params']['request']['soItemSlsQty'] = self.render_qty
    #         response = self.http.post(url, json=params)
    #         a.json(params, "请求数据")
    #         a.json(response, "响应数据")
    #         self.assert_util.assert_response_success(response)
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="SLS-销售订单-保存服务",
    #     description="验证SLS_SO_SAVE_ACTION_SERVICE接口",
    #     severity="critical",
    #     order=130,
    #     tags=["销售订单", "保存", "SLS_SO_SAVE_ACTION_SERVICE"]
    # )
    # def test_save_action_service(self):
    #     """SLS-销售订单-保存服务"""
    #     try:
    #         # 确保有可保存的订单数据
    #         if not hasattr(self, 'so_price_data') or not self.so_price_data:
    #             self.test_08_calculate_pricing()

    #         api_path = self.get_api_path("SLS-销售订单-保存服务")
    #         params, url = self.get_api_params(api_path)
    #         # 使用已计算的订单数据
    #         params['params']['request']['soItems'] = self.so_price_data.get('soItems', [])
    #         params['params']['request']['totalAmt'] = self.so_price_data.get('totalAmt', 0)
    #         params['params']['request']['taxAmt'] = self.so_price_data.get('taxAmt', 0)
    #         params['params']['request']['netAmt'] = self.so_price_data.get('netAmt', 0)
    #         response = self.http.post(url, json=params)
    #         a.json(params, "请求数据")
    #         a.json(response, "响应数据")
    #         self.assert_util.assert_response_success(response)
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

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
