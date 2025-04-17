import os
import sys
import json
import pytest
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

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Decimal 类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
                return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DecimalEncoder, self).default(obj)

class TestSalesOrderCreate:
    """销售订单创建测试类"""
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        # 初始化基础组件
        cls.logger = Loggers()
        cls.db = DBManager()
        cls.http = HttpUtil()
        cls.assert_util = AssertHelper()
        
        # 初始化SQL工具并获取初始化数据（利用缓存机制）
        cls.init_sql = InitSQL()
        init_data = cls.init_sql.init_sql()
        
        # 只获取需要的配置信息
        cls.init_data = {
            "base_info": {
                "so_type_info": init_data["base_info"]["so_type_info"],
                "sales_channel_info": init_data["base_info"]["sales_channel_info"],
                "exchange_rate_type_info": init_data["base_info"]["exchange_rate_type_info"],
                "currency_info": init_data["base_info"]["currency_info"]
            },
            "org_info": {
                "sls_org_info": init_data["org_info"]["sls_org_info"],
                "pur_org_info": init_data["org_info"]["pur_org_info"],
                "inv_org_info": init_data["org_info"]["inv_org_info"],
                "com_org_info": init_data["org_info"]["com_org_info"]
            },
            "partner_info": {
                "cust_info": init_data["partner_info"]["cust_info"]
            },
            "material_info": {
                "inv_loc_info": init_data["material_info"]["inv_loc_info"]
            }
        }
        
        # 提取必要的ID
        cls._extract_ids()
        
        # 初始化登录和API配置
        cls.login_manager = LoginManager()
        cls.session = cls.login_manager.login()
        cls.base_url = Config.get_api_base_url()
        
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
        cls.logger.info("测试类初始化完成")

    @classmethod
    def _extract_ids(cls) -> None:
        """提取必要的ID并验证"""
        id_mappings = {
            'cust_id': ('partner_info', 'cust_info', 'id'),
            'so_type_id': ('base_info', 'so_type_info', 'id'),
            'sls_org_id': ('org_info', 'sls_org_info', 'id'),
            'pur_org_id': ('org_info', 'pur_org_info', 'id'),
            'inv_org_id': ('org_info', 'inv_org_info', 'id'),
            'com_org_id': ('org_info', 'com_org_info', 'id'),
            'sls_dc_id': ('base_info', 'sales_channel_info', 'id'),
            'inv_loc_id': ('material_info', 'inv_loc_info', 'id'),
            'exchange_rate_type_id': ('base_info', 'exchange_rate_type_info', 'exchange_rate_type_id'),
            'base_curr_id': ('base_info', 'currency_info', 'curr_id'),
            'sls_curr_id': ('base_info', 'currency_info', 'curr_id')
        }
        
        for attr_name, path in id_mappings.items():
            value = cls.init_data
            for key in path:
                value = value[key]
            setattr(cls, attr_name, value)
            cls.assert_util.assert_id_exists(value, f"{attr_name.replace('_', ' ').title()}")

    def setup_method(self, method):
        """每个测试方法执行前的准备工作"""
        # 记录测试方法开始
        self.logger.info(f"开始执行测试方法: {method.__name__}")

    def _make_request(self, url: str, data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """发送API请求并处理响应"""
        response = self.session.post(url, params={"tmodule": "ERP_SCM"}, json=data)
        self.assert_util.assert_http_status(response)
        response_data = response.json()
        self.assert_util.assert_response_status(response_data)
        return response_data["data"]

    @safe_api_call(error_message="销售订单创建初始化失败")
    def test_01_init_sales_order(self):
        """测试销售订单创建初始化"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_order_create_init_service"
        data = {"params": {"request": {"btClass": "SALES"}}}
        
        result = self._make_request(url, data, "销售订单创建初始化")
        # 保存销售人员信息供后续使用
        self.sls_person_obj = result['data']["slsPerson"]
        self.sls_phone = result['data']["slsPhone"]
        self.sls_person_name = result['data']["slsPerson"]["name"]
        logger.debug(f"销售人员信息: {self.sls_person_obj}")
        self.logger.info("销售订单创建初始化测试通过")


    @safe_api_call(error_message="查询客户信息失败")
    def test_02_query_customer_info(self):
        """测试查询客户信息"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_cust_select_render_service"
        data = {"params": {"custId": self.cust_id}}
        
        result = self._make_request(url, data, "查询客户信息")
        # 记录响应数据
        logger.debug(f"客户信息查询响应: {result}")
        # 保存地址ID和地址信息供后续使用
        self.addr_id = result['data']["addrId"]["id"]
        self.addr_detail = result['data']["addrDetail"]
        self.cust_person_name = result['data']["custPersonName"]
        self.cust_phone = result['data']["custPhone"]
        self.logger.info("客户信息查询测试通过")


    @safe_api_call(error_message="查询相关方失败")
    def test_03_query_partner(self):
        """测试查询相关方"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_QUERY_PARTNER_EVENT_SERVICE"
        data = self._build_partner_query_data()
        
        result = self._make_request(url, data, "查询相关方")
        # 保存相关方信息供后续使用
        self.sls_partner_links = result['data']["slsPartnerLinks"]
        self.so_items = result['data']["soItems"]
        self.logger.info("相关方查询测试通过")

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

    @safe_api_call(error_message="查询销售组织列表失败")
    def test_04_query_sales_organization(self):
        """测试查询销售组织列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_organization_paging_service"
        data = {"params":{"request":{"pageable":{"pageNo":1,"pageSize":20,"conditionGroup":{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"key":"nr_nqTvXmIyHnHxKfmn3S","type":"ConditionLeaf","leftValue":{"id":"iJlX7JIkAyn7AIr9omqK-","key":"iJlX7JIkAyn7AIr9omqK-","type":"VarValue","fieldType":"Text","valueType":"VAR","varValue":[{"valueKey":"orgCode","valueName":"orgCode"}]},"operator":"CONTAINS","rightValue":{"key":"ggwEgoMfFc91CYI1zUwzb","type":"VarValue","fieldType":"Text","valueType":"CONST","constValue":"AUTOTEST_SLS_ORG"}}]}]},"sortOrders":None,"keyword":None}}}}
        result = self._make_request(url, data, "查询销售组织列表")
        logger.debug(f"销售组织列表查询响应: {result}")
        self.sls_org_obj = result['data']['data'][0]
        self.sls_org_id = self.sls_org_obj['id']
        logger.info(f"销售组织列表查询测试通过: {self.sls_org_obj}")
        self.logger.info("销售组织列表查询测试通过")


    @safe_api_call(error_message="查询物料列表失败")
    def test_05_query_materials(self):
        """测试查询物料列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$INV_MAT_PAGING_SERVICE"
        data = self._build_material_query_data()
        logger.debug(f"物料列表查询请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = self._make_request(url, data, "查询物料列表")
        # 记录响应数据
        self.mat_obj = result['data']['data'][0]
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
                            "invOrgId": None,
                            "invLocId": None,
                            "soItemSlsQty": None
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
        
        result = self._make_request(url, data, "订单行渲染")
        # 保存订单行渲染结果供后续使用
        self.so_items = result['data']["soItems"]
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
        result = self._make_request(url, data, "自动定价")
        # 保存自动定价结果供后续使用
        self.so_price_data = result
        logger.debug(f"自动定价响应数据: {json.dumps(self.so_price_data, cls=DecimalEncoder, indent=2)}")
        self.logger.info("自动定价测试通过")

    @safe_api_call(error_message="保存销售订单失败")
    def test_08_save_sales_order(self):
        """测试保存销售订单"""
        # 确保所有必要的信息都已获取
        if not hasattr(self, 'so_price_data') or self.so_price_data is None:
            self.test_07_calculate_pricing()
            
        # 确保订单行已渲染
        if not hasattr(self, 'so_items') or self.so_items is None:
            self.test_06_render_order_line()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_CREATE_SAVE_EVENT_NEW_SERVICE"
        data = {
            "params": {
                "request": {
                    **self.so_price_data["data"],
                    "soItems": self.so_items
                }
            }
        }
        logger.debug(f"保存销售订单请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = self._make_request(url, data, "保存销售订单")
        logger.debug(f"保存销售订单响应数据: {json.dumps(result, cls=DecimalEncoder, indent=2)}")
        assert result is not None, "销售订单保存失败"
        self.order_id = result['data']['id']  # 保存订单ID
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
                    **self.so_price_data["data"],
                    "soItems": self.so_items,
                    "syncSubmit": True
                }
            }
        }
          
        
        # 打印请求信息
        logger.info(f"\n请求数据: {json.dumps(data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        response = self.session.post(url, json=data)
        
        # 打印响应信息
        logger.info(f"\n响应数据: {json.dumps(response.json(), cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证响应
        self.assert_util.assert_http_status(response)
        response_data = response.json()
        self.assert_util.assert_response_status(response_data)
        result = response_data["data"]
        
        assert result is not None, "销售订单保存并提交失败"
    

    @pytest.mark.order(10)
    @safe_api_call(error_message="销售订单列表提交失败")
    def test_10_manual_submit_sales_order(self):
        """测试销售订单列表提交"""
        # 检查必要数据
        if not hasattr(self, 'order_id') or self.order_id is None:
            self.test_08_save_sales_order()
        
        # 发送请求
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_MANUAL_SUBMIT?tmodule=ERP_SCM"
        data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        logger.debug(f"销售订单手动提交请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = self._make_request(url, data, "销售订单手动提交")
        logger.debug(f"销售订单手动提交响应数据: {json.dumps(result, cls=DecimalEncoder, indent=2)}")
        # 验证响应
        assert result is not None, "销售订单手动提交失败"
        logger.info("销售订单手动提交成功")


if __name__ == "__main__":
    # 使用 pytest 运行测试
    # pytest.main(["-v", __file__])
    
    #或者按顺序直接调用
    test = TestSalesOrderCreate()
    test.setup_class()
    test.test_01_init_sales_order()
    test.test_02_query_customer_info()
    test.test_03_query_partner()
    test.test_04_query_sales_organization()
    test.test_05_query_materials()
    test.test_06_render_order_line()
    test.test_07_calculate_pricing()
    test.test_08_save_sales_order()
    test.test_09_submit_sales_order()
    # test.test_10_manual_submit_sales_order()
