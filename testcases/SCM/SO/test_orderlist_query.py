import os
import sys
import json
import pytest
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from testcases.SCM.base_test import BaseTest, DecimalEncoder
from utils.ExceptionUtil import safe_api_call

class TestOrderList(BaseTest):
    """销售订单列表测试类"""
    
    def setup_method(self, method=None):
        """每个测试方法执行前的准备工作
        
        Args:
            method: 当前执行的测试方法，可选参数
        """
        # 确保 base_url 已初始化
        if not hasattr(self, 'base_url') or not self.base_url:
            self.setup_class()
            
        # 调用父类的 setup_method
        super().setup_method(method)
        
        # 初始化测试数据
        self.test_data = {
            "so_code": None,
            "so_type_id": None,
            "so_status": None,
            "sls_org_id": None,
            "cust_id": None,
            "created_by": None   
        }
        
        # 如果提供了 method 参数，记录方法名
        if method and hasattr(method, '__name__'):
            logger.info(f"开始执行测试方法: {method.__name__}")
        else:
            logger.info("开始执行测试方法")
            
        logger.info("初始化测试数据完成")
    
    
    def _build_order_list_query_data(self,conditionGroup=None) -> Dict[str, Any]:
        """构建销售订单列表查询数据"""
        return {
            "params": {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "systemParams": {
                            "viewCondition": {
                                "conditionKey": "gYLG-UJ0RZbOCvMez5f7D",
                                "rightValues": {
                                    "jYJ-mOKGX5JJkeGr274TK": [
                                        {
                                            "constValue": "SALES",
                                            "fieldType": "Enum",
                                            "type": "ConstValue",
                                            "valueType": "CONST"
                                        },
                                        {
                                            "constValue": "ASS",
                                            "fieldType": "Enum",
                                            "type": "ConstValue",
                                            "valueType": "CONST"
                                        }
                                    ]
                                }
                            }
                        },
                        "conditionGroup": conditionGroup,
                        "sortOrders": [
                            {
                                "fieldAlias": "createdBy",
                                "sortType": "DESC"
                            }
                        ]
                    }
                }
            }
        }
    
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询销售订单列表失败")
    def test_01_query_orders(self):
        """测试查询销售订单列表"""
        
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        data = self._build_order_list_query_data()
        # 执行测试
        logger.info("\n准备发送请求...")
        response = self._make_request(url, data, "查询销售订单列表")
        
        # 检查响应结构并提取数据
        assert "data" in response, "响应格式错误：缺少 data 字段"
        assert "data" in response["data"], "响应格式错误：缺少 data.data 字段"
        assert "data" in response["data"]["data"], "响应格式错误：缺少 data.data.data 字段"
        
        # 如果有数据，验证返回的订单数据结构并提取测试数据
        if response["data"]['data']['data']:
            order = response["data"]["data"]["data"][0]
            logger.info(f"\n获取到订单数据: {json.dumps(order, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
            
            # 提取测试数据并验证
            self.test_data["so_code"] = order.get("soCode")
            self.test_data["so_type_id"] = order.get("soTypeId")
            self.test_data["so_status"] = order.get("soStatus")
            self.test_data["cust_id"] = order.get("custId")
            self.test_data["created_by"] = order.get("createdBy")
            self.test_data["sls_org_id"] = order.get("slsOrgId")
            # 验证数据完整性
            assert self.test_data["so_code"], "未获取到订单编号"
            assert self.test_data["so_type_id"], "未获取到订单类型"
            assert self.test_data["so_status"], "未获取到订单状态"
            assert self.test_data["cust_id"], "未获取到客户ID"
            assert self.test_data["created_by"], "未获取到创建者"
            assert self.test_data["sls_org_id"], "未获取到销售组织ID"
        else:
            logger.warning("\n警告：未获取到订单数据，无法提取测试数据")
            logger.debug(f"响应数据结构: {json.dumps(response['data'], cls=DecimalEncoder, ensure_ascii=False, indent=2)}")

    @pytest.mark.order(2)
    @safe_api_call(error_message="按订单编号查询销售订单列表失败")
    def test_02_query_orders_by_so_code(self):
        """测试按订单编号查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了订单编号
        if not self.test_data.get("so_code"):
            error_msg = "未获取到订单编号，无法执行按订单编号查询测试"
            logger.error(error_msg)
            pytest.fail(error_msg)
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        conditionGroup = {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": [
                                {
                                    "type": "ConditionGroup",
                                    "logicOperator": "AND",
                                    "conditions": [
                                        {
                                            "type": "ConditionGroup",
                                            "logicOperator": "AND",
                                            "conditions": [
                                                {
                                                    "key": "7JoifU09H-JVAGxFS7Jp9",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "akf0NzleWL_In83AFxvla",
                                                        "key": "akf0NzleWL_In83AFxvla",
                                                        "type": "VarValue",
                                                        "fieldType": "Text",
                                                        "valueType": "VAR",
                                                        "varValue": [
                                                            {
                                                                "valueKey": "soCode",
                                                                "valueName": "soCode"
                                                            }
                                                        ]
                                                    },
                                                    "operator": "CONTAINS",
                                                    "rightValue": {
                                                        "key": "3Inq2hwHhbWlMWnuCY4g6",
                                                        "type": "VarValue",
                                                        "fieldType": "Text",
                                                        "valueType": "CONST",
                                                        "constValue": self.test_data["so_code"]
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
        data = self._build_order_list_query_data(conditionGroup)
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 订单编号 = {self.test_data['so_code']}")
        
        # 获取完整响应
        full_response = self._make_request(url, data, "按订单编号查询销售订单列表")
        # logger.info(f"\n收到完整响应: {json.dumps(full_response, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, "按订单编号查询销售订单列表", extract_nested_data=True)
        logger.info(f"\n提取的嵌套数据: {json.dumps(nested_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data:
            assert self.test_data["so_code"] in order.get("soCode", ""), f"订单编号 {order.get('soCode')} 不匹配查询条件 {self.test_data['so_code']}"
            
        logger.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

    @pytest.mark.order(3)
    @pytest.mark.parametrize("so_status", ["DRAFT", "EFFECT", "APPROVING", "CANCELLED"])
    @safe_api_call(error_message="按单据状态查询销售订单列表失败")
    def test_03_query_orders_by_status(self, so_status):
        """测试按单据状态查询销售订单列表
        
        Args:
            so_status: 订单状态，通过参数化传入
        """
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        # 构建按单据状态筛选的查询条件
        condition_group = {
            "type": "ConditionGroup",
            "logicOperator": "AND",
            "conditions": [
                {
                    "type": "ConditionGroup",
                    "logicOperator": "AND",
                    "conditions": [
                        {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": [
                                {
                                    "key": "64B0O2CfJfcOoCi6rRYF1",
                                    "type": "ConditionLeaf",
                                    "leftValue": {
                                        "id": "XdGqXf0INwfXIncliBOF-",
                                        "key": "XdGqXf0INwfXIncliBOF-",
                                        "type": "VarValue",
                                        "fieldType": "Text",
                                        "valueType": "VAR",
                                        "varValue": [
                                            {
                                                "valueKey": "soStatus",
                                                "valueName": "soStatus"
                                            }
                                        ]
                                    },
                                    "operator": "IN",
                                    "rightValues": [
                                        {
                                            "key": "t5GpRIoC_DDU4SjW1WUi3",
                                            "type": "VarValue",
                                            "fieldType": "Text",
                                            "valueType": "CONST",
                                            "constValue": so_status
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        data = self._build_order_list_query_data(condition_group)
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 订单状态 = {so_status}")
        
        # 获取完整响应
        full_response = self._make_request(url, data, f"按单据状态 {so_status} 查询销售订单列表")
        # logger.info(f"\n收到完整响应: {json.dumps(full_response, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, f"按单据状态 {so_status} 查询销售订单列表", extract_nested_data=True)
        logger.info(f"\n提取的嵌套数据: {json.dumps(nested_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证查询结果
        if not nested_data:
            logger.warning(f"\n警告：未查询到状态为 {so_status} 的订单数据")
            return
            
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data:
            assert order.get("soStatus") == so_status, f"订单状态 {order.get('soStatus')} 不匹配查询条件 {so_status}"
            
        logger.info(f"\n成功查询到 {len(nested_data)} 条状态为 {so_status} 的订单数据")

    @pytest.mark.order(4)
    @safe_api_call(error_message="按单据类型查询销售订单列表失败")
    def test_04_query_orders_by_so_type(self):
        """测试按单据类型查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了订单类型ID
        if not self.test_data.get("so_type_id"):
            error_msg = "未获取到订单类型ID，无法执行按单据类型查询测试"
            logger.error(error_msg)
            pytest.fail(error_msg)
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        # 构建按单据类型筛选的查询条件
        conditionGroup = {
            "type": "ConditionGroup",
            "logicOperator": "AND",
            "conditions": [
                {
                    "type": "ConditionGroup",
                    "logicOperator": "AND",
                    "conditions": [
                        {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": [
                                {
                                    "key": "2uvCbH6DjO3wmCT3hgg5Q",
                                    "type": "ConditionLeaf",
                                    "leftValue": {
                                        "id": "FR0ZgfLRp3ZW5hpO-zwUe",
                                        "key": "FR0ZgfLRp3ZW5hpO-zwUe",
                                        "type": "VarValue",
                                        "fieldType": "Object",
                                        "valueType": "VAR",
                                        "varValue": [
                                            {
                                                "valueKey": "soTypeId",
                                                "valueName": "soTypeId"
                                            }
                                        ]
                                    },
                                    "operator": "IN",
                                    "rightValues": [
                                        {
                                            "key": "NUNjvcTQTuOcb0S9tdmjh",
                                            "type": "ConstValue",
                                            "fieldType": "Object",
                                            "valueType": "CONST",
                                            "constValue": self.test_data["so_type_id"]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        data = self._build_order_list_query_data(conditionGroup)
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 订单类型ID = {self.test_data['so_type_id']}")
        
        # 获取完整响应
        full_response = self._make_request(url, data, "按单据类型查询销售订单列表")
        # logger.info(f"\n收到完整响应: {json.dumps(full_response, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, "按单据类型查询销售订单列表", extract_nested_data=True)
        logger.info(f"\n提取的嵌套数据: {json.dumps(nested_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data:
            assert order.get("soTypeId") == self.test_data["so_type_id"], f"订单类型ID {order.get('soTypeId')} 不匹配查询条件 {self.test_data['so_type_id']}"
            
        logger.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

    @pytest.mark.order(5)
    @safe_api_call(error_message="按客户查询销售订单列表失败")
    def test_05_query_orders_by_customer(self):
        """测试按客户查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了客户ID
        if not self.test_data.get("cust_id"):
            error_msg = "未获取到客户ID，无法执行按客户查询测试"
            logger.error(error_msg)
            pytest.fail(error_msg)
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        # 构建按客户筛选的查询条件
        conditionGroup = {
            "type": "ConditionGroup",
            "logicOperator": "AND",
            "conditions": [
                {
                    "type": "ConditionGroup",
                    "logicOperator": "AND",
                    "conditions": [
                        {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": [
                                {
                                    "key": "reM0KaxiIEcYZS4LesejP",
                                    "type": "ConditionLeaf",
                                    "leftValue": {
                                        "id": "L4dbyACrC74gyXvFFedt-",
                                        "key": "L4dbyACrC74gyXvFFedt-",
                                        "type": "VarValue",
                                        "fieldType": "Object",
                                        "valueType": "VAR",
                                        "varValue": [
                                            {
                                                "valueKey": "custId",
                                                "valueName": "custId"
                                            }
                                        ]
                                    },
                                    "operator": "IN",
                                    "rightValues": [
                                        {
                                            "key": "QHpXogPNnAM3GdYSk17Fy",
                                            "type": "ConstValue",
                                            "fieldType": "Object",
                                            "valueType": "CONST",
                                            "constValue": self.test_data["cust_id"]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        data = self._build_order_list_query_data(conditionGroup)
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 客户ID = {self.test_data['cust_id']}")
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, "按客户查询销售订单列表", extract_nested_data=True)

        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data:
            assert order.get("custId") == self.test_data["cust_id"], f"客户ID {order.get('custId')} 不匹配查询条件 {self.test_data['cust_id']}"
            
        logger.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

if __name__ == "__main__":
    test = TestOrderList()
    test.setup_method()
    test.test_01_query_orders()
    # test.test_02_query_orders_by_so_code()
    # test.test_03_query_orders_by_status("DRAFT")
    # test.test_03_query_orders_by_status("EFFECT")
    # test.test_03_query_orders_by_status("APPROVING")
    # test.test_03_query_orders_by_status("CANCELLED")
    # test.test_04_query_orders_by_so_type()
    test.test_05_query_orders_by_customer()