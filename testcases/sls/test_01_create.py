import os
import sys
import json
import pytest
import random
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import allure


# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_util import YamlUtil
from utils.exception_util import handle_exception, safe_api_call, handle_class_method_exception
from utils.cache_util import CacheUtil
from testcases.comm.base_test import BaseTest


class TestSalesOrderCreate(BaseTest):
    """销售订单创建测试类"""
    
    # 定义要测试的订单类型
    TEST_ORDER_TYPES = ["STND", "THRD", "CENT"]
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
        
        # 初始化缓存工具并加载销售订单缓存
        cache_file_path = project_root / "testdata" / "cache" / "sls_cache.json"
        CacheUtil.init(cache_dir="testdata/cache")  # 先初始化缓存工具
        CacheUtil.load_sls_cache(str(cache_file_path))  # 再加载缓存文件
        
        # 初始化测试数据
        cls.so_type_id = cls.ids.get("so_type_id")
        cls.cust_id = cls.ids.get("cust_id")
        cls.com_org_id = cls.ids.get("com_org_id")
        cls.sls_dc_id = cls.ids.get("sls_dc_id")
        cls.sls_org_id = cls.ids.get("sls_org_id")
        cls.inv_org_id = cls.ids.get("inv_org_id")
        cls.inv_loc_id = cls.ids.get("inv_loc_id")
        cls.exchange_rate_type_id = cls.ids.get("exchange_rate_type_id")
        cls.cust_id = cls.ids.get("cust_id")
        cls.sls_curr_id = cls.ids.get("sls_curr_id")
        cls.base_curr_id = cls.ids.get("base_curr_id")
        
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
        
        # 加载配置文件
        cls.base_api_path = project_root / "testdata" / "sls" / "sls_api_path.yaml"
        cls.base_config_path = project_root / "testdata" / "sls" / "sls_api_params.yaml"
        
        # 当前用例集所需接口
        cls.yaml_util = YamlUtil()
        cls.so_path = cls.yaml_util.read_yaml(cls.base_api_path)["销售订单"]["订单管理"]
        
        # 前用例集所需参数
        cls.so_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})

        cls.logger.info(f"初始化渲染数量: {cls.render_qty}")
        cls.logger.info("测试类初始化完成")

    def _init_sales_order(self, order_type="STND"):
        """初始化销售订单
        
        Args:
            order_type: 订单类型，默认为标准销售(STND)
        """
        url = self.so_path["初始化订单"]
        data = self.so_params.get(url, {})
        
        # 获取订单类型和订单行类型的ID
        order_type_id = CacheUtil.get_order_type_id(order_type)
        order_line_type_id = CacheUtil.get_order_line_type_id("NORM")  # 默认使用常规销售行类型
        
        # 更新请求参数
        data['params']['request']['orderTypeId'] = order_type_id
        data['params']['request']['orderLineTypeId'] = order_line_type_id
        
        result = self.http.post(url, json=data, description="销售订单创建初始化")
        
        # 从嵌套结构中获取数据
        response_data = result.get("data", {}).get("data", {})
        
        # 保存销售人员信息供后续使用
        self.sls_person_obj = response_data.get("slsPerson")
        self.sls_phone = response_data.get("slsPhone")
        if self.sls_person_obj:
            self.sls_person_name = self.sls_person_obj.get("name")
        
        self.logger.debug(f"销售人员信息: {self.sls_person_obj}")
        self.logger.info(f"销售订单创建初始化完成，订单类型: {order_type}")
        
        self.assert_util.assert_response_success(result)
        
        # 验证必要字段
        assert self.sls_person_obj is not None, "销售人员信息为空"
        assert self.sls_phone is not None, "销售人员电话为空"
        assert self.sls_person_name is not None, "销售人员姓名为空"

    def _render_order_line(self, order_type="STND"):
        """渲染订单行
        
        Args:
            order_type: 订单类型，默认为标准销售(STND)
        """
        # 确保物料已查询
        if not hasattr(self, 'mat_obj') or self.mat_obj is None:
            self._query_materials()
        
        url = self.so_path["渲染订单行"]
        curr_time = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        data = self.so_params.get(url, {})
        
        # 获取订单类型和订单行类型的ID
        order_type_id = CacheUtil.get_order_type_id(order_type)
        order_line_type_id = CacheUtil.get_order_line_type_id("NORM")  # 默认使用常规销售行类型
        
        # 更新请求参数
        data['params']['request']['orderTypeId'] = order_type_id
        data['params']['request']['orderLineTypeId'] = order_line_type_id
        data['params']['request']['addrId'] = {"id": self.addr_id}
        data['params']['request']['custId'] = {"id": self.cust_id}
        data['params']['request']['slsComId'] = {"id": self.com_org_id}
        data['params']['request']['slsDcId'] = {"id": self.sls_dc_id}
        data['params']['request']['slsOrgId'] = {"id": self.sls_org_id}
        data['params']['request']['slsPerson'] = self.sls_person_obj
        data['params']['request']['slsPhone'] = self.sls_phone
        data['params']['request']['slsPersonName'] = self.sls_person_name
        data['params']['request']['soDocDate'] = curr_time
        data['params']['request']['soTypeId'] = {"id": self.so_type_id}
        data['params']['request']['baseCurrId'] = {"id": self.base_curr_id}
        data['params']['request']['slsCurrId'] = {"id": self.sls_curr_id}
        data['params']['request']['currExchangeRateType'] = self.exchange_rate_type_id
        data['params']['request']['slsPartnerLinks'] = self.sls_partner_links
        data['params']['request']['soItems'][0]['matId'] = {"id": self.mat_obj['id']}
        data['params']['request']['soItems'][0]['soItemSlsQty'] = self.render_qty
        data['params']['request']['soItems'][0]['delAddrDetail'] = self.addr_detail
        data['params']['request']['soItems'][0]['delAddrId'] = {"id": self.addr_id}
        data['params']['request']['soItems'][0]['delPersonName'] = self.cust_person_name
        data['params']['request']['soItems'][0]['delPhone'] = self.cust_phone
        data['params']['request']['soItems'][0]['invOrgId'] = {"id": self.inv_org_id}
        data['params']['request']['soItems'][0]['invLocId'] = {"id": self.inv_loc_id}
        
        result = self.http.post(url, json=data, description="订单行渲染")
        result = result.get("data", {}).get("data", {})
        
        if "soItems" not in result:
            self.logger.error(f"订单行渲染响应缺少soItems字段，响应内容: {result}")
            raise KeyError("订单行渲染响应缺少soItems字段。")

        self.so_items = result.get("soItems")
        self.logger.info(f"订单行渲染完成，订单类型: {order_type}")
        
        try:
            assert self.so_items is not None, "订单行信息为空"
        except AssertionError as e:
            self.logger.error(f"订单行渲染原始响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            raise

    def _save_or_submit_order(self, order_type="STND", is_submit=False):
        """保存或提交销售订单
        
        Args:
            order_type: 订单类型，默认为标准销售(STND)
            is_submit: 是否提交订单，True为提交，False为保存
        """
        try:
            # 1. 渲染订单行
            with allure.step(f"初始化{order_type}类型销售订单"):
                self._init_sales_order(order_type)
            with allure.step("查询客户信息"):
                self._query_customer_info()
            with allure.step("查询相关方"):
                self._query_partner()
            with allure.step("查询销售组织"):
                self._query_sales_organization()
            with allure.step("查询物料"):
                self._query_materials()
            with allure.step(f"渲染{order_type}类型订单行"):
                self._render_order_line(order_type)
                assert self.so_items is not None, "订单行信息为空"

            # 2. 自动定价
            with allure.step("自动定价"):
                self._calculate_pricing()
                assert self.so_price_data is not None, "定价信息为空"

            # 3. 保存或提交订单
            with allure.step(f"{'提交' if is_submit else '保存'}{order_type}类型订单"):
                url = self.so_path["保存订单"]
                
                # 获取订单类型和订单行类型的ID
                order_type_id = CacheUtil.get_order_type_id(order_type)
                order_line_type_id = CacheUtil.get_order_line_type_id("NORM")  # 默认使用常规销售行类型
                
                # 记录订单类型信息
                self.logger.info(f"订单类型: {order_type}")
                self.logger.info(f"订单类型ID: {order_type_id}")
                self.logger.info(f"订单行类型ID: {order_line_type_id}")
                
                # 构建请求数据
                request_data = {
                    **self.so_price_data,
                    "soItems": self.so_items,
                    "syncSubmit": is_submit,
                    "soTypeId": {"id": order_type_id},
                    "orderTypeId": {"id": order_type_id},
                    "orderLineTypeId": {"id": order_line_type_id},
                    "slsOrgId": {"id": self.sls_org_id},
                    "slsDcId": {"id": self.sls_dc_id},
                    "slsComId": {"id": self.com_org_id},
                    "custId": {"id": self.cust_id},
                    "addrId": {"id": self.addr_id},
                    "addrDetail": self.addr_detail,
                    "custPersonName": self.cust_person_name,
                    "custPhone": self.cust_phone,
                    "slsPerson": self.sls_person_obj,
                    "slsPhone": self.sls_phone,
                    "slsPersonName": self.sls_person_name,
                    "slsPartnerLinks": self.sls_partner_links
                }
                
                data = {
                    "params": {
                        "request": request_data
                    }
                }
                
                # 记录请求数据
                self.logger.info(f"保存订单请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                result = self.http.post(url, json=data, description=f"销售订单{'提交' if is_submit else '保存'}")
                
                # 记录响应数据
                self.logger.info(f"保存订单响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                assert result is not None, f"销售订单{'提交' if is_submit else '保存'}失败"
                
                if not is_submit:
                    self.order_id = result.get("data", {}).get("data", {}).get("id")
                    self.logger.info(f"{order_type}类型销售订单保存成功，订单ID: {self.order_id}")
                else:
                    self.logger.info(f"{order_type}类型销售订单提交成功")

        except Exception as e:
            error_msg = f"{order_type}类型销售订单{'提交' if is_submit else '保存'}失败: {str(e)}"
            self.logger.error(error_msg)
            if hasattr(e, 'response'):
                self.logger.error(f"响应状态码: {e.response.status_code}")
                self.logger.error(f"响应内容: {e.response.text}")
            raise

    @allure.title("测试多种类型销售订单保存")
    @allure.description("""
    测试步骤：
    1. 遍历不同类型的订单
    2. 渲染订单行
    3. 自动定价
    4. 保存销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @safe_api_call(error_message="多种类型销售订单保存失败")
    def test_save_multiple_order_types(self):
        """测试多种类型销售订单保存"""
        for order_type in self.TEST_ORDER_TYPES:
            with allure.step(f"保存{order_type}类型订单"):
                self._save_or_submit_order(order_type=order_type, is_submit=False)

    @allure.title("测试多种类型销售订单提交")
    @allure.description("""
    测试步骤：
    1. 遍历不同类型的订单
    2. 渲染订单行
    3. 自动定价
    4. 提交销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @safe_api_call(error_message="多种类型销售订单提交失败")
    def test_submit_multiple_order_types(self):
        """测试多种类型销售订单提交"""
        for order_type in self.TEST_ORDER_TYPES:
            with allure.step(f"提交{order_type}类型订单"):
                self._save_or_submit_order(order_type=order_type, is_submit=True)

    
    def teardown_class(self):
        self.clear_so
        self.logger.info("销售订单创建测试类清理")


if __name__ == "__main__":
    # allure_dir = os.path.join(project_root, "reports", "allure-results")
    # pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
    test = TestSalesOrderCreate()
    test.setup_class()
    test.test_save_multiple_order_types()
    test.test_submit_multiple_order_types()
    