import os
import sys
import json
import allure
import pytest   
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest, DecimalEncoder
from utils.exception_util import safe_api_call
from utils.yaml_util import YamlUtil

class TestOrderList(BaseTest):
    """销售订单列表测试类"""
    
    def setup_method(cls):
        """每个测试方法执行前的准备工作
        
        Args:
            method: 当前执行的测试方法，可选参数
        """
        super().setup_class()
        
        # 初始化测试数
        
         # 加载配置文件
        cls.base_api_path = Path(project_root) / "testdata" / "sls" / "sls_api_path.yaml"
        cls.base_config_path = Path(project_root) / "testdata" / "sls" / "so_api_params.yaml"
        
        # 当前用例集所需接口
        cls.yaml_util = YamlUtil()
        cls.so_path = cls.yaml_util.read_yaml(cls.base_api_path)["销售订单"]["订单管理"]
        
        # 前用例集所需参数
        cls.so_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})

    
    
    def _build_order_list_query_data(self, conditionGroup=None) -> Dict[str, Any]:
        """构建销售订单列表查询数据"""
        # 更新查询参数
        query_data = TestOrderList.common_params["pagination_query"]
        query_data["params"]["request"]["pageable"]["conditionGroup"] = conditionGroup
        
        # 设置视图条件
        query_data["params"]["request"]["pageable"]["systemParams"]["viewCondition"] = {
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
        
        return query_data
    
    @allure.title("查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询销售订单列表失败")
    def test_01_query_orders(self):
        """测试查询销售订单列表"""
        
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        
        data = self._build_order_list_query_data()
        # 执行测试
        self.log.info("\n准备发送请求...")
        response = self.http.post(url, json=data, description="查询销售订单列表")        
        # 打印完整响应结构
        self.log.info(f"\n完整响应结构: {json.dumps(response, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        if not response:
            self.log.warning("未查询到订单数据")
            return
            
        # 获取第一个订单数据
        order = response.get("data", {}).get("data", []).get("data", [])[0]
        self.log.info(f"\n第一个订单数据: {json.dumps(order, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 提取测试数据并验证
        self.test_data["so_code"] = order.get("soCode")
        self.test_data["so_type_id"] = order.get("soTypeId", {}).get("id") if order.get("soTypeId") else None
        self.test_data["so_status"] = order.get("soStatus")
        self.test_data["cust_id"] = order.get("custId", {}).get("id") if order.get("custId") else None
        self.test_data["created_by"] = order.get("createdBy", {}).get("id") if order.get("createdBy") else None
        self.test_data["sls_org_id"] = order.get("slsOrgId", {}).get("id") if order.get("slsOrgId") else None
        
        # 验证数据完整性
        self.assert_util.assert_id_exists(self.test_data["so_code"], "订单编号")
        self.assert_util.assert_id_exists(self.test_data["so_type_id"], "订单类型")
        self.assert_util.assert_id_exists(self.test_data["so_status"], "订单状态")
        self.assert_util.assert_id_exists(self.test_data["cust_id"], "客户ID")
        self.assert_util.assert_id_exists(self.test_data["created_by"], "创建者")
        self.assert_util.assert_id_exists(self.test_data["sls_org_id"], "销售组织ID")
        
        # 输出提取的测试数据
        self.log.info(f"\n提取的测试数据: {json.dumps(self.test_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 将测试数据保存到类属性，确保后续测试可以访问
        TestOrderList.test_data = self.test_data
        self.log.info("\n已将测试数据保存到类属性")

    
    @allure.title("按订单编号查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按订单编号查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(2)
    @safe_api_call(error_message="按订单编号查询销售订单列表失败")
    def test_02_query_orders_by_so_code(self):
        """测试按订单编号查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了订单编号
        if not self.test_data.get("so_code"):
            error_msg = "未获取到订单编号，无法执行按订单编号查询测试"
            self.log.error(error_msg)
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
        self.log.info("\n准备发送请求...")
        self.log.info(f"查询条件: 订单编号 = {self.test_data['so_code']}")

        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按订单编号查询销售订单列表")
        self.log.info(f"\n提取的嵌套数据: {json.dumps(nested_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data.get("data", {}).get("data", []).get("data", []):
            assert self.test_data["so_code"] in order.get("soCode", ""), f"订单编号 {order.get('soCode')} 不匹配查询条件 {self.test_data['so_code']}"
            
        self.log.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

    @allure.title("按单据状态查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按单据状态查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)    
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
        
        data = self._build_order_list_query_data(condition_group)
        
        # 执行测试
        self.log.info("\n准备发送请求...")
        self.log.info(f"查询条件: 订单状态 = {so_status}")
        
        # 获取完整响应
        full_response = self.http.post(url, json=data, description=f"按单据状态 {so_status} 查询销售订单列表")
        self.log.info(f"\n收到完整响应: {json.dumps(full_response, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description=f"按单据状态 {so_status} 查询销售订单列表")
        self.log.info(f"\n提取的嵌套数据: {json.dumps(nested_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        
        # 验证查询结果
        if not nested_data:
            self.log.warning(f"\n警告：未查询到状态为 {so_status} 的订单数据")
            return
            
        self.assert_util.assert_response_success(full_response)
            
        self.log.info(f"\n成功查询到 {len(nested_data)} 条状态为 {so_status} 的订单数据")


    @allure.title("按单据类型查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按单据类型查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(4)
    @safe_api_call(error_message="按单据类型查询销售订单列表失败")
    def test_04_query_orders_by_so_type(self):
        """测试按单据类型查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了订单类型ID
        if not self.test_data.get("so_type_id"):
            error_msg = "未获取到订单类型ID，无法执行按单据类型查询测试"
            self.log.error(error_msg)
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
        self.log.info("\n准备发送请求...")
        self.log.info(f"查询条件: 订单类型ID = {self.test_data['so_type_id']}")
        
        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按单据类型查询销售订单列表")
        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data.get("data", {}).get("data", []).get("data", []):
            # 根据实际结构进行断言
            if isinstance(order.get("soTypeId"), dict):
                # 如果soTypeId是对象，获取其id属性
                order_so_type_id = order.get("soTypeId", {}).get("id")
            else:
                # 如果soTypeId直接就是ID值
                order_so_type_id = order.get("soTypeId")
                
            # 根据实际结构进行断言
            if isinstance(self.test_data["so_type_id"], dict):
                # 如果测试数据中的so_type_id也是对象
                expected_id = self.test_data["so_type_id"].get("id")
            else:
                # 如果测试数据中的so_type_id直接就是ID值
                expected_id = self.test_data["so_type_id"]
                
            # 进行断言
            assert order_so_type_id == expected_id, f"订单类型ID {order_so_type_id} 不匹配查询条件 {expected_id}"
            
        self.log.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")


    @allure.title("按客户查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按客户查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(5)
    @safe_api_call(error_message="按客户查询销售订单列表失败")
    def test_05_query_orders_by_customer(self):
        """测试按客户查询销售订单列表"""
        
        # 确保第一个测试已经执行并获取了客户ID
        if not self.test_data.get("cust_id"):
            error_msg = "未获取到客户ID，无法执行按客户查询测试"
            self.log.error(error_msg)
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
        self.log.info("\n准备发送请求...")
        self.log.info(f"查询条件: 客户ID = {self.test_data['cust_id']}")
        
        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按客户查询销售订单列表")
        
        # 验证查询结果
        assert nested_data, "未查询到匹配的订单数据"
        
        # 验证所有返回的订单都匹配查询条件
        for order in nested_data.get("data", {}).get("data", []).get("data", []):
            # 根据实际结构进行断言
            if isinstance(order.get("custId"), dict):
                # 如果custId是对象，获取其id属性
                order_cust_id = order.get("custId", {}).get("id")
            else:
                # 如果custId直接就是ID值
                order_cust_id = order.get("custId")
                
            # 根据实际结构进行断言
            if isinstance(self.test_data["cust_id"], dict):
                # 如果测试数据中的cust_id也是对象
                expected_id = self.test_data["cust_id"].get("id")
            else:
                # 如果测试数据中的cust_id直接就是ID值
                expected_id = self.test_data["cust_id"]
                
            # 进行断言
            assert order_cust_id == expected_id, f"客户ID {order_cust_id} 不匹配查询条件 {expected_id}"
            
        self.log.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

if __name__ == "__main__":
    test = TestOrderList()
    test.setup_method()
    test.test_01_query_orders()
    test.test_02_query_orders_by_so_code()
    test.test_03_query_orders_by_status("DRAFT")
    test.test_03_query_orders_by_status("EFFECT")
    test.test_03_query_orders_by_status("APPROVING")
    test.test_03_query_orders_by_status("CANCELLED")
    test.test_04_query_orders_by_so_type()
    test.test_05_query_orders_by_customer()
    # allure_dir = os.path.join(project_root, "reports", "allure-results")
    # pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
    