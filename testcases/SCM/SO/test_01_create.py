import os
import sys
import json
import pytest
import random
from decimal import Decimal
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional
import allure


# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from common.login_manager import LoginManager
from testcases.SCM.scm_init import InitSQL
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers
from common.config_manager import ConfigManager
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

    def _init_sales_order(self):
        """初始化销售订单"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_order_create_init_service"
        data = {"params": {"request": {"btClass": "SALES"}}}
        
        result = super()._make_request(url, data, "销售订单创建初始化", extract_nested_data=True)
        # 保存销售人员信息供后续使用
        self.sls_person_obj = result["slsPerson"]
        self.sls_phone = result["slsPhone"]
        self.sls_person_name = result["slsPerson"]["name"]
        logger.debug(f"销售人员信息: {self.sls_person_obj}")
        self.logger.info("销售订单创建初始化完成")

    def _query_customer_info(self):
        """查询客户信息"""
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
        
        assert self.addr_id is not None, "地址ID为空"
        assert self.addr_detail is not None, "地址信息为空"
        assert self.cust_person_name is not None, "客户姓名为空"
        assert self.cust_phone is not None, "客户电话为空"
        self.logger.info("客户信息查询完成")

    def _query_partner(self):
        """查询相关方"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SO_QUERY_PARTNER_EVENT_SERVICE"
        data = {
                "params": {
                    "request": {
                        "reCalculate": False,
                        "soTypeId":self.so_type_id, #初始化
                        "soDocDate": int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),
                        "priceCalcDate": int(datetime.now().timestamp() * 1000),
                        "custId": self.cust_id,
                        "slsPerson": self.sls_person_obj,
                        "slsPhone": self.sls_phone,
                        "slsPersonName": self.sls_person_name,
                        "isFixedExchRate": False,
                        "currExchangeRateType": 2000001,
                        "soItems":[{
                            "bomWhether": False,
                            "soSchlDelDate": int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),                   
                        }]
                    }
                }
             }
        logger.debug(f"相关方查询请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = super()._make_request(url, data, "查询相关方", extract_nested_data=True)
        # 保存相关方信息供后续使用
        logger.debug(f"相关方查询响应: {json.dumps(result, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")
        self.sls_partner_links = result["slsPartnerLinks"]
        self.logger.info("相关方查询完成")
        assert self.sls_partner_links is not None, "相关方信息为空"

    def _query_sales_organization(self):
        """查询销售组织列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_sales_organization_paging_service"
        data = {"params":{"request":{"pageable":{"pageNo":1,"pageSize":20,"conditionGroup":{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"type":"ConditionGroup","logicOperator":"AND","conditions":[{"key":"nr_nqTvXmIyHnHxKfmn3S","type":"ConditionLeaf","leftValue":{"id":"iJlX7JIkAyn7AIr9omqK-","key":"iJlX7JIkAyn7AIr9omqK-","type":"VarValue","fieldType":"Text","valueType":"VAR","varValue":[{"valueKey":"orgCode","valueName":"orgCode"}]},"operator":"CONTAINS","rightValue":{"key":"ggwEgoMfFc91CYI1zUwzb","type":"VarValue","fieldType":"Text","valueType":"CONST","constValue":"AUTOTEST_SLS_ORG"}}]}]},"sortOrders":None,"keyword":None}}}}
        result = super()._make_request(url, data, "查询销售组织列表", extract_nested_data=True)
        logger.debug(f"销售组织列表查询响应: {result}")
        # 直接使用列表的第一个元素
        self.sls_org_obj = result[0]
        self.sls_org_id = self.sls_org_obj["id"]
        logger.info(f"销售组织列表查询完成: {self.sls_org_obj}")
        self.logger.info("销售组织列表查询完成")
        assert self.sls_org_obj is not None, "销售组织信息为空"
        assert self.sls_org_id is not None, "销售组织ID为空"

    def _query_materials(self):
        """查询物料列表"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$INV_MAT_PAGING_SERVICE"
        data = {
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
        logger.debug(f"物料列表查询请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        
        result = super()._make_request(url, data, "查询物料列表", extract_nested_data=True)
        # 记录响应数据
        # 直接使用列表的第一个元素
        self.mat_obj = result[0]
        # 添加默认价格字段
        self.mat_obj["matBasePrice"] = 100.00  # 设置默认价格
        logger.debug(f"物料列表查询响应: {self.mat_obj}")
        self.logger.info("物料列表查询完成")
        assert self.mat_obj is not None, "物料信息为空"

    def _render_order_line(self):
        """渲染订单行"""
        # 确保物料已查询
        if not hasattr(self, 'mat_obj') or self.mat_obj is None:
            self._query_materials()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_AFTER_MAT_SELECT_RENDER_EVENT_SERVICE"
        curr_time = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        data = {
                "params": {
                    "request": {
                        "addrId": {"id": self.addr_id},
                        "custId": {"id": self.cust_id},
                        "invLoc": None,
                        "invOrg": None,
                        "slsComId": {"id": self.com_org_id},
                        "slsDcId": {"id": self.sls_dc_id},
                        "slsOrgId": {"id": self.sls_org_id},
                        "slsPerson": self.sls_person_obj,
                        "slsPhone": self.sls_phone,
                        "slsPersonName": self.sls_person_name,
                        "soDocDate": curr_time,
                        "soTypeId": {"id": self.so_type_id},
                        "baseCurrId": {"id": self.base_curr_id},
                        "slsCurrId": {"id": self.sls_curr_id},
                        "currExchangeRateType": self.exchange_rate_type_id,
                        "slsPartnerLinks": self.sls_partner_links,
                        "soItems":[
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

        logger.debug(f"订单行渲染请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        
        result = super()._make_request(url, data, "订单行渲染", extract_nested_data=True)
        # 保存订单行渲染结果供后续使用
        self.so_items = result["soItems"]
        self.logger.info("订单行渲染完成")
        assert self.so_items is not None, "订单行信息为空"
        logger.debug(f"订单行渲染结果: {json.dumps(self.so_items, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")
        
        # 检查渲染结果中的税率ID等信息
        if self.so_items and len(self.so_items) > 0:
            first_item = self.so_items[0]
            logger.debug(f"订单行渲染结果中的税率ID: {first_item.get('taxRateId')}")
            logger.debug(f"订单行渲染结果中的单位ID: {first_item.get('uomSlsId')}")
            logger.debug(f"订单行渲染结果中的物料类型ID: {first_item.get('matTypeId')}")

    def _calculate_pricing(self):
        """自动定价"""
        try:
            # 1. 准备请求参数
            with allure.step("准备定价参数"):
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
                            "slsOrgId": self.sls_org_obj,
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
                allure.attach(
                    json.dumps(data, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                    "定价请求参数",
                    allure.attachment_type.JSON
                )
                self.logger.info(f"自动定价请求参数: {json.dumps(data, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")

            # 2. 发送请求
            with allure.step("发送定价请求"):
                try:
                    result = super()._make_request(url, data, "自动定价", extract_nested_data=True)
                    allure.attach(
                        json.dumps(result, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                        "响应数据",
                        allure.attachment_type.JSON
                    )
                    
                    # 检查定价结果中的税率ID等信息
                    if result and "soItems" in result and len(result["soItems"]) > 0:
                        first_item = result["soItems"][0]
                        logger.debug(f"定价结果中的税率ID: {first_item.get('taxRateId')}")
                        logger.debug(f"定价结果中的单位ID: {first_item.get('uomSlsId')}")
                        logger.debug(f"定价结果中的物料类型ID: {first_item.get('matTypeId')}")
                            
                except Exception as e:
                    error_msg = f"自动定价请求失败: {str(e)}"
                    if hasattr(e, 'response'):
                        error_msg += f"\n响应状态码: {e.response.status_code}"
                        error_msg += f"\n响应内容: {e.response.text}"
                    self.logger.error(error_msg)
                    raise

            # 3. 验证响应
            with allure.step("验证响应数据"):
                assert result is not None, "定价响应数据为空"
                assert "soItems" in result, "响应中缺少订单项"
                
                # 保存定价信息
                self.so_price_data = result
                
                allure.attach(
                    json.dumps(self.so_price_data, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                    "定价信息",
                    allure.attachment_type.JSON
                )
                self.logger.info("自动定价完成")

        except Exception as e:
            error_msg = f"自动定价失败: {str(e)}"
            self.logger.error(error_msg)
            if hasattr(e, 'response'):
                self.logger.error(f"响应状态码: {e.response.status_code}")
                self.logger.error(f"响应内容: {e.response.text}")
            raise

    def _save_or_submit_order(self, is_submit: bool = False):
        """保存或提交销售订单
        
        Args:
            is_submit: 是否提交订单，True为提交，False为保存
        """
        try:
            # 1. 渲染订单行
            with allure.step("初始化销售订单"):
                self._init_sales_order()
            with allure.step("查询客户信息"):
                self._query_customer_info()
            with allure.step("查询相关方"):
                self._query_partner()
            with allure.step("查询销售组织"):
                self._query_sales_organization()
            with allure.step("查询物料"):
                self._query_materials()
            with allure.step("渲染订单行"):
                self._render_order_line()
                assert self.so_items is not None, "订单行信息为空"
                logger.debug(f"订单行信息: {json.dumps(self.so_items, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")

            # 2. 自动定价
            with allure.step("自动定价"):
                self._calculate_pricing()
                assert self.so_price_data is not None, "定价信息为空"
                logger.debug(f"定价信息: {json.dumps(self.so_price_data, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")

            # 3. 保存或提交订单
            with allure.step("保存或提交订单"):
                url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SALES_MANUAL_SAVE_EVENT?tmodule=ERP_SCM"
                data = {
                    "params": {
                        "request": {
                            **self.so_price_data,
                            "soItems": self.so_items,
                            "syncSubmit": is_submit
                        }
                    }
                }
                allure.attach(
                    json.dumps(data, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                    f"{'提交' if is_submit else '保存'}订单请求参数",
                    allure.attachment_type.JSON
                )
                logger.debug(f"{'提交' if is_submit else '保存'}销售订单请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
                
                result = super()._make_request(url, data, f"销售订单{'提交' if is_submit else '保存'}", extract_nested_data=True)
                assert result is not None, f"销售订单{'提交' if is_submit else '保存'}失败"
                
                allure.attach(
                    json.dumps(result, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                    f"{'提交' if is_submit else '保存'}订单响应数据",
                    allure.attachment_type.JSON
                )
                logger.debug(f"{'提交' if is_submit else '保存'}销售订单响应数据: {json.dumps(result, cls=DecimalEncoder, indent=2)}")
                
                if not is_submit:
                    self.order_id = result['id']
                    logger.info(f"销售订单保存成功，订单ID: {self.order_id}")
                else:
                    logger.info("销售订单提交成功")

        except Exception as e:
            error_msg = f"销售订单{'提交' if is_submit else '保存'}失败: {str(e)}"
            self.logger.error(error_msg)
            if hasattr(e, 'response'):
                self.logger.error(f"响应状态码: {e.response.status_code}")
                self.logger.error(f"响应内容: {e.response.text}")
            raise

    @allure.title("销售订单保存")
    @allure.description("""
    测试步骤：
    1. 渲染订单行
    2. 自动定价
    3. 保存销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @safe_api_call(error_message="销售订单保存失败")
    def test_save_sales_order(self):
        """测试销售订单保存"""
        self._save_or_submit_order(is_submit=False)

    @allure.title("销售订单提交")
    @allure.description("""
    测试步骤：
    1. 渲染订单行
    2. 自动定价
    3. 提交销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @safe_api_call(error_message="销售订单提交失败")
    def test_submit_sales_order(self):
        """测试销售订单提交"""
        self._save_or_submit_order(is_submit=True)




if __name__ == "__main__":
    # pytest.main(["-v", __file__, "--alluredir=./reports/allure-results"])
    test = TestSalesOrderCreate()
    test.setup_class()
    test.test_save_sales_order()
    test.test_submit_sales_order()
    