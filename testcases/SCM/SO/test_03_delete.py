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

class TestOrderDelete(BaseTest):
    """销售订单删除测试类"""
    
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
        
        # 初始化测试数据，但保留已有的数据
        if not hasattr(self, 'test_data') or not self.test_data:
            # 如果类属性中有测试数据，使用类属性中的数据
            if hasattr(TestOrderDelete, 'test_data') and TestOrderDelete.test_data:
                self.test_data = TestOrderDelete.test_data
                logger.info("使用类属性中的测试数据")
            else:
                self.test_data = {
                    "so_id": None,
                    "so_code": None
                }
                logger.info("初始化新的测试数据")
        
        # 如果提供了 method 参数，记录方法名
        if method and hasattr(method, '__name__'):
            logger.info(f"开始执行测试方法: {method.__name__}")
        else:
            logger.info("开始执行测试方法")
            
        logger.info("初始化测试数据完成")
    
    def _build_delete_order_data(self, order_id: str) -> Dict[str, Any]:
        """构建删除销售订单的请求数据
        
        Args:
            order_id: 要删除的订单ID
            
        Returns:
            Dict[str, Any]: 删除订单的请求数据
        """
        return {
            "params": {
                "request": {
                    "id": order_id
                },
                "modelKey": "ERP_SCM$sls_so_head_tr"
            }
        }
    
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询销售订单列表失败")
    def test_01_query_orders(self):
        """测试查询销售订单列表，获取要删除的订单ID"""
        
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        # 构建查询条件，获取草稿状态的订单
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
                                            "constValue": "DRAFT"
                                        }
                                    ]
                                },
                                {
                                    "key": "fa7hlBBPOhnPZZWIFeCvy",
                                    "type": "ConditionLeaf",
                                    "leftValue": {
                                        "id": "i_p4wT0Gew5Xnx1AInwPH",
                                        "key": "i_p4wT0Gew5Xnx1AInwPH",
                                        "type": "VarValue",
                                        "fieldType": "Object",
                                        "valueType": "VAR",
                                        "varValue": [
                                            {
                                                "valueKey": "createdBy",
                                                "valueName": "createdBy"
                                            }
                                        ]
                                    },
                                    "operator": "EQ",
                                    "rightValue": {
                                        "key": "oDkbT7tIhBcvbHsvqzLHN",
                                        "type": "ConstValue",
                                        "fieldType": "Object",
                                        "valueType": "CONST",
                                        "constValue": self.user_id
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        data = {
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
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 订单状态 = DRAFT, 创建人 = {self.user_id}")
        
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, "查询销售订单列表", extract_nested_data=True)
        
        # 验证查询结果
        assert nested_data, "未查询到草稿状态的订单数据"
        
        # 保存所有订单数据到 test_data
        self.test_data["orders"] = nested_data
        
        # 提取第一个订单的ID和编号
        order = nested_data[0]
        self.test_data["so_id"] = order.get("id")
        self.test_data["so_code"] = order.get("soCode")
        
        # 验证数据完整性
        assert self.test_data["so_id"], "未获取到订单ID"
        assert self.test_data["so_code"], "未获取到订单编号"
        
        # 输出提取的测试数据
        logger.info(f"\n提取的测试数据: {json.dumps(self.test_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 将测试数据保存到类属性，确保后续测试可以访问
        TestOrderDelete.test_data = self.test_data
        logger.info("\n已将测试数据保存到类属性")
    
    @pytest.mark.order(2)
    @safe_api_call(error_message="删除销售订单失败")
    def test_02_delete_order(self):
        """测试删除销售订单"""
        
        # 确保第一个测试已经执行并获取了订单ID
        if not self.test_data.get("so_id"):
            error_msg = "未获取到订单ID，无法执行删除测试"
            logger.error(error_msg)
            pytest.fail(error_msg)
            
        # 添加URL参数
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_DeleteDataByIdService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_head_tr"
        
        # 构建删除订单的请求数据
        data = self._build_delete_order_data(self.test_data["so_id"])
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"删除订单: ID = {self.test_data['so_id']}, 编号 = {self.test_data['so_code']}")
        
        # 发送删除请求
        response = self._make_request(url, data, "删除销售订单")
        
        # 验证删除结果
        assert response.get("success", False), f"删除订单失败: {response.get('message', '未知错误')}"
        
        logger.info(f"\n成功删除订单: {self.test_data['so_code']}")
    
    @pytest.mark.order(3)
    @safe_api_call(error_message="验证订单删除结果失败")
    def test_03_verify_order_deleted(self):
        """测试验证订单是否已删除"""
        
        # 确保第一个测试已经执行并获取了订单ID
        if not self.test_data.get("so_id"):
            error_msg = "未获取到订单ID，无法执行验证测试"
            logger.error(error_msg)
            pytest.fail(error_msg)
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        # 构建查询条件，查询已删除的订单
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
        
        data = {
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
        
        # 执行测试
        logger.info("\n准备发送请求...")
        logger.info(f"查询条件: 订单编号 = {self.test_data['so_code']}")
        
        # 获取提取后的嵌套数据
        nested_data = self._make_request(url, data, "验证订单删除结果", extract_nested_data=True)
        
        # 验证查询结果，应该找不到已删除的订单
        assert not nested_data, f"订单 {self.test_data['so_code']} 仍然存在，删除失败"
        
        logger.info(f"\n验证成功: 订单 {self.test_data['so_code']} 已成功删除")

    @pytest.mark.order(4)
    @safe_api_call(error_message="批量删除销售订单失败")
    def test_04_batch_delete_orders(self):
        """测试批量删除销售订单"""
        # 调用 test_01_query_orders 获取订单ID
        logger.info("调用 test_01_query_orders 获取订单ID")
        self.test_01_query_orders()
        
        # 从响应结果中获取前两条订单的ID
        order_ids = []
        if hasattr(self, 'test_data') and 'orders' in self.test_data:
            orders = self.test_data['orders']
            logger.info(f"查询到 {len(orders)} 条订单")
            for order in orders[:2]:  # 只取前两条
                if "id" in order:
                    order_ids.append(order["id"])
                    logger.info(f"订单ID: {order['id']}, 订单编号: {order.get('soCode', 'N/A')}")
        
        if not order_ids:
            error_msg = "没有找到可删除的订单"
            logger.error(error_msg)
            pytest.fail(error_msg)
        
        # 准备批量删除请求
        delete_url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sales_order_batch_delete_service"
        delete_data = {
            "params": {
                "request": {
                    "ids": order_ids
                }
            }
        }
        
        # 发送批量删除请求
        logger.info(f"\n准备批量删除订单，订单ID: {order_ids}")
        response = self._make_request(delete_url, delete_data, "批量删除销售订单")
        
        # 验证删除结果
        assert response.get("success", False), "批量删除订单失败"
        logger.info(f"成功批量删除订单，订单ID: {order_ids}")

if __name__ == "__main__":
    print("\n开始销售订单删除测试...")
    
    # 创建测试类实例
    test = TestOrderDelete()
    test.setup_method()
    
    # 执行测试方法
    test.test_01_query_orders()  # 先查询获取订单ID
    test.test_02_delete_order()  # 删除单个订单
    test.test_03_verify_order_deleted()  # 验证订单删除
    test.test_04_batch_delete_orders()  # 批量删除订单
    
    print("\n销售订单删除测试完成!")