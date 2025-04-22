import os
import sys
import json
import pytest
import random
from decimal import Decimal
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional


# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from common.login_manager import LoginManager
from config.config import Config
from testcases.SCM.scm_init import InitSQL
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers
from utils.MysqlUtil import DBManager
from utils.YamlUtil import YamlReader
from utils.HttpUtil import HttpUtil
from utils.ExceptionUtil import handle_exception, safe_api_call, handle_class_method_exception
from testcases.SCM.base_test import BaseTest

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Decimal 类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
                return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DecimalEncoder, self).default(obj)

class TestSalesOrderCreate(BaseTest):
    """销售订单创建测试类"""
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
        
        # 初始化测试数据
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
        cls.logger.info(f"初始化渲染数量: {cls.render_qty}")
        cls.logger.info("测试类初始化完成")

    @safe_api_call(error_message="销售订单创建初始化失败")
    def test_01_init_sales_order(self):
        """测试销售订单创建初始化"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_order_create_init_service"
        data = {"params": {"request": {"btClass": "SALES"}}}
        
        result = super()._make_request(url, data, "销售订单创建初始化", extract_nested_data=True)
        # 保存销售人员信息供后续使用
        self.sls_person_obj = result["slsPerson"]
        self.sls_phone = result["slsPhone"]
        self.sls_person_name = result["slsPerson"]["name"]
        logger.debug(f"销售人员信息: {self.sls_person_obj}")
        self.logger.info("销售订单创建初始化测试通过")

    @safe_api_call(error_message="查询客户信息失败")
    def test_02_query_customer_info(self):
        """测试查询客户信息"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_cust_select_render_service"
        data = {"params": {"custId": self.cust_id}}
        
        result = super()._make_request(url, data, "查询客户信息", extract_nested_data=True)
        # 记录响应数据
        logger.debug(f"客户信息查询响应: {result}")
        # 保存地址ID和地址信息供后续使用
        self.addr_id = result["addrId"]["id"]
        self.addr_detail = result["addrDetail"]
        self.cust_person_name = result["custPersonName"]
        self.cust_phone = result["custPhone"]
        self.logger.info("客户信息查询测试通过")

    def _build_partner_query_data(self) -> Dict[str, Any]:
        """构建相关方查询数据"""
        current_timestamp = int(datetime.now().timestamp() * 1000)
        current_date = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        
        return {
            "params": {
                "request": {
                    "reCalculate": False,
                    "soTypeId": self.so_type_id,
                    "soDocDate": current_date,
                    "priceCalcDate": current_timestamp,
                    "custId": {"id": self.cust_id},
                    "slsPerson": self.sls_person_obj,
                    "slsPhone": self.sls_phone,
                    "slsPersonName": self.sls_person_name,
                    "isFixedExchRate": False,
                    "currExchangeRateType": self.exchange_rate_type_id,
                    "soItems": [{"bomWhether": False, "soSchlDelDate": current_date}]
                }
            }
        }

    @safe_api_call(error_message="查询相关方失败")
    def test_03_query_partner(self):
        """测试查询相关方"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_QUERY_PARTNER_EVENT_SERVICE"
        data = self._build_partner_query_data()
        
        result = super()._make_request(url, data, "查询相关方", extract_nested_data=True)
        # 保存相关方信息供后续使用
        self.sls_partner_links = result["slsPartnerLinks"]
        self.so_items = result["soItems"]
        self.logger.info("相关方查询测试通过")

    @safe_api_call(error_message="查询销售组织列表失败")
    def test_04_query_sales_organization(self):
        """测试查询销售组织列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_organization_paging_service"
        data = {"params":{"request":{"pageable":{"pageNo":1,"pageSize":20,"conditionGroup":{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"key":"nr_nqTvXmIyHnHxKfmn3S","type":"ConditionLeaf","leftValue":{"id":"iJlX7JIkAyn7AIr9omqK-","key":"iJlX7JIkAyn7AIr9omqK-","type":"VarValue","fieldType":"Text","valueType":"VAR","varValue":[{"valueKey":"orgCode","valueName":"orgCode"}]},"operator":"CONTAINS","rightValue":{"key":"ggwEgoMfFc91CYI1zUwzb","type":"VarValue","fieldType":"Text","valueType":"CONST","constValue":"AUTOTEST_SLS_ORG"}}]}]},"sortOrders":None,"keyword":None}}}}
        result = super()._make_request(url, data, "查询销售组织列表", extract_nested_data=True)
        logger.debug(f"销售组织列表查询响应: {result}")
        # 直接使用列表的第一个元素
        self.sls_org_obj = result[0]
        self.sls_org_id = self.sls_org_obj["id"]
        logger.info(f"销售组织列表查询测试通过: {self.sls_org_obj}")
        self.logger.info("销售组织列表查询测试通过")

    @safe_api_call(error_message="查询物料列表失败")
    def test_05_query_materials(self):
        """测试查询物料列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$INV_MAT_PAGING_SERVICE"
        data = self._build_material_query_data()
        logger.debug(f"物料列表查询请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = super()._make_request(url, data, "查询物料列表", extract_nested_data=True)
        # 记录响应数据
        # 直接使用列表的第一个元素
        self.mat_obj = result[0]
        logger.debug(f"物料列表查询响应: {self.mat_obj}")
        self.logger.info("物料列表查询测试通过")

    def _build_material_query_data(self) -> Dict[str, Any]:
        """构建物料查询数据"""
        return {
            "params": {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "sortOrders": [
                            {"fieldAlias": "matCode", "id": "matCode-0", "sortType": "ASC"},
                            {"fieldAlias": "matName", "id": "matName-1", "sortType": "ASC"}
                        ],
                        "keyword": "TESTMAT1"
                    },
                    "slsOrgId": self.sls_org_id,  # 直接使用整数ID
                    "slsDcId": self.sls_dc_id
                }
            }
        }

    
    def _build_order_line_data(self) -> Dict[str, Any]:
        """构建订单行数据"""
        current_date = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        
        return {
            "params": {
                "request": {
                    "addrId": {"id": self.addr_id},
                    "baseCurrId": {"id": self.base_curr_id},
                    "custId": {"id": self.cust_id},
                    "invLoc": None,
                    "invOrg": None,
                    "slsComId": {"id": self.com_org_id},
                    "slsDcId": {"id": self.sls_dc_id},
                    "slsOrgId": {"id": self.sls_org_id},
                    "soDocDate": current_date,
                    "soTypeId": {"id": self.so_type_id},
                    "slsCurrId": {"id": self.sls_curr_id},
                    "currExchangeRateType": self.exchange_rate_type_id,
                    "slsPartnerLinks": self.sls_partner_links,
                    "slsPerson": self.sls_person_obj,
                    "slsPhone": self.sls_phone,
                    "slsPersonName": self.sls_person_name,
                    "soItems": [
                        {
                            "matId": {"id": self.mat_obj['id']},
                            "taxRateId": None,
                            "invOrgId": {"id": self.inv_org_id},
                            "invLocId": {"id": self.inv_loc_id},
                            "soItemSlsQty": self.render_qty,
                            "delAddrDetail": self.addr_detail,
                            "delAddrId": {"id": self.addr_id},
                            "delPersonName": self.cust_person_name,
                            "delPhone": self.cust_phone
                        }
                    ]
                }
            }
        }

    @safe_api_call(error_message="订单行渲染失败")
    def test_06_render_order_line(self):
        """测试订单行渲染"""
        # 确保物料已查询
        if not hasattr(self, 'mat_obj') or self.mat_obj is None:
            self.test_05_query_materials()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_AFTER_MAT_SELECT_RENDER_EVENT_SERVICE"
        data = self._build_order_line_data()
        logger.debug(f"订单行渲染请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        
        result = super()._make_request(url, data, "订单行渲染", extract_nested_data=True)
        # 保存订单行渲染结果供后续使用
        self.so_items = result["soItems"]
        self.logger.info("订单行渲染测试通过")


    @safe_api_call(error_message="自动定价失败")
    def test_07_calculate_pricing(self):
        """测试自动定价"""
        # 确保所有必要的信息都已获取
        if not hasattr(self, 'sls_person_obj') or self.sls_person_obj is None:
            self.test_01_init_sales_order()
        if not hasattr(self, 'addr_id') or self.addr_id is None:
            self.test_02_query_customer_info()
        if not hasattr(self, 'sls_org_obj') or self.sls_org_obj is None:
            self.test_04_query_sales_organization()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_AUTO_PRICE_EVENT_copy_SERVICE"
        data = {
            "params": {
                "request": {
                    "id": None,
                    "priceIdempotent": None,
                    "reCalculate": False,
                    "soTypeId": {"id": self.so_type_id},
                    "soDocDate": int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),
                    "priceCalcDate": int(datetime.now().timestamp() * 1000),
                    "custId": {"id": self.cust_id},
                    "addrId": {"id": self.addr_id},
                    "addrDetail": self.addr_detail,
                    "custPersonName": self.cust_person_name,
                    "custPhone": self.cust_phone,
                    "slsPerson": self.sls_person_obj,
                    "slsPhone": self.sls_phone,
                    "slsPersonName": self.sls_person_name,
                    "slsOrgId": self.sls_org_obj,  # 直接使用销售组织对象
                    "slsDcId": {"id": self.sls_dc_id},
                    "slsComId": {"id": self.com_org_id},
                    "slsCurrId": {"id": self.sls_curr_id},
                    "baseCurrId": {"id": self.base_curr_id},
                    "isFixedExchRate": False,
                    "currExchangeRateType": self.exchange_rate_type_id,
                    "exchRate": 1,
                    "soItems": self.so_items,
                    "slsPartnerLinks": self.sls_partner_links
                }
            }
        }
        result = super()._make_request(url, data, "自动定价", extract_nested_data=True)
        # 保存自动定价结果供后续使用
        self.so_price_data = result
        logger.debug(f"自动定价响应数据: {json.dumps(self.so_price_data, cls=DecimalEncoder, indent=2)}")
        self.logger.info("自动定价测试通过")

    @safe_api_call(error_message="保存销售订单失败")
    def test_08_save_sales_order(self):
        """测试保存销售订单"""
        
        self.test_06_render_order_line()
        # 确保所有必要的信息都已获取
        if not hasattr(self, 'so_price_data') or self.so_price_data is None:
            self.test_07_calculate_pricing()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_CREATE_SAVE_EVENT_NEW_SERVICE"
        data = {
            "params": {
                "request": {
                    **self.so_price_data,  # 直接使用 so_price_data，不再访问 data 字段
                    "soItems": self.so_items
                }
            }
        }
        logger.debug(f"保存销售订单请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = super()._make_request(url, data, "保存销售订单", extract_nested_data=True)
        logger.debug(f"保存销售订单响应数据: {json.dumps(result, cls=DecimalEncoder, indent=2)}")
        assert result is not None, "销售订单保存失败"
        self.order_id = result['id']  # 直接访问 id 字段
        logger.info(f"销售订单保存成功，订单ID: {self.order_id}")

    @pytest.mark.order(9)
    @safe_api_call(error_message="销售订单保存并提交失败")
    def test_09_submit_sales_order(self):
        """测试销售订单保存并提交"""
        self.test_06_render_order_line()
         # 确保所有必要的信息都已获取
        self.test_07_calculate_pricing()
            
        # 发送请求
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SALES_MANUAL_SAVE_EVENT?tmodule=ERP_SCM" 
        
        data = {
            "params": {
                "request": {
                    **self.so_price_data,  # 直接使用 so_price_data，不再访问 data 字段
                    "soItems": self.so_items,
                    "syncSubmit": True
                }
            }
        }
        
        result = super()._make_request(url, data, "销售订单保存并提交", extract_nested_data=True)
        assert result is not None, "销售订单保存并提交失败"
        logger.info("销售订单提交成功")
        
    

if __name__ == "__main__":
    # 使用 pytest 运行测试
    pytest.main(["-v", __file__])
    
    # # 或者按顺序直接调用
    # test = TestSalesOrderCreate()
    # test.setup_class()
    # # test.test_01_init_sales_order()
    # # test.test_02_query_customer_info()
    # # test.test_03_query_partner()
    # # test.test_04_query_sales_organization()
    # # test.test_05_query_materials()
    # # test.test_06_render_order_line()
    # # test.test_07_calculate_pricing()
    # test.test_08_save_sales_order()
    # # test.test_09_submit_sales_order()
