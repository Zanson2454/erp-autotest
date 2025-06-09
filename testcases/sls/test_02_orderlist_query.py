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

from testcases.comm.base_test import BaseTest
from utils.exception_util import safe_api_call
from utils.yaml_util import YamlUtil
from testcases.sls import SlsBase

class TestOrderList(BaseTest,SlsBase):
    """销售订单列表测试类"""
    
    @classmethod
    def setup_class(cls):
        """每个测试方法执行前的准备工作
        
        Args:
            method: 当前执行的测试方法，可选参数
        """
        super().setup_class()

        # testdata
        cls.test_data = {}

    @allure.title("查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @safe_api_call(error_message="查询销售订单列表失败")
    def _query_orders(self):
        """测试查询销售订单列表"""
        url = self.sls_api_paths["订单管理"]["查询订单"]
        data = self.sls_api_params[url]
        response = self.http.post(url, json=data, description="查询销售订单列表")
        self.logger.info(f"接口原始响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        orders = response.get("data", {}).get("data", {}).get("data", [])
        if not orders:
            self.logger.error("查询结果为空，未获取到任何订单数据")
            pytest.fail("查询结果为空，未获取到任何订单数据")
        order = orders[0]
        
        # 提取测试数据并验证
        self.test_data["so_code"] = order.get("soCode")
        self.test_data["so_type_id"] = order.get("soTypeId", {}).get("id") if order.get("soTypeId") else None
        self.logger.info(f"so_type_id: {self.test_data['so_type_id']}")
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
        
        self.logger.info(f"\n提取的测试数据: {json.dumps(self.test_data,  ensure_ascii=False, indent=2)}")
        TestOrderList.test_data = self.test_data
        self.logger.info("\n已将测试数据保存到类属性test_data")

    
    @allure.title("按订单编号查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按订单编号查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="按订单编号查询销售订单列表失败")
    def test_01_query_orders_by_so_code(self):
        """测试按订单编号查询销售订单列表"""
        
        # 若test_data无值则自动初始化
        if not self.test_data.get("so_code"):
            self._query_orders()
            
        url = self.sls_api_paths["订单管理"]["查询订单"]
        data = self.sls_api_params[url]
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
        data["params"]["request"]["pageable"]["conditionGroup"] =conditionGroup
        
        # 执行测试
        self.logger.info(f"查询条件: 订单编号 = {self.test_data['so_code']}")

        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按订单编号查询销售订单列表")
        result =  nested_data.get("data", {}).get("data", []).get("data", [])
        self.assert_util.assert_not_empty(result, "未查询到匹配的订单数据")
        # 验证所有返回的订单都匹配查询条件
        for order in result:
            assert self.test_data["so_code"] in order.get("soCode", ""), f"订单编号 {order.get('soCode')} 不匹配查询条件 {self.test_data['so_code']}"
            
        self.logger.info(f"\n成功查询到 {len(result)} 条匹配的订单数据")

    @allure.title("按单据状态查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按单据状态查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(2)
    @pytest.mark.parametrize("so_status", ["DRAFT", "EFFECT", "APPROVING", "CANCELLED"])
    @safe_api_call(error_message="按单据状态查询销售订单列表失败")
    def test_02_query_orders_by_status(self, so_status):
        """测试按单据状态查询销售订单列表
        
        Args:
            so_status: 订单状态，通过参数化传入
        """
        url = self.sls_api_paths["订单管理"]["查询订单"]
        data = self.sls_api_params[url]
        
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
                                        "constValue": self.ids.get("user_id")
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        data["params"]["request"]["pageable"]["conditionGroup"] = condition_group
        
        # 执行测试
        self.logger.info(f"查询条件: 订单状态 = {so_status}")
        
        # 获取完整响应
        full_response = self.http.post(url, json=data, description=f"按单据状态 {so_status} 查询销售订单列表")
        
        # 获取提取后的嵌套数据
        result =  full_response.get("data", {}).get("data", []).get("data", [])
        
        # 验证查询结果
        if not result:
            self.logger.warning(f"\n警告：未查询到状态为 {so_status} 的订单数据")
            return
        self.assert_util.assert_not_empty(result, "未查询到匹配的订单数据")
        self.assert_util.assert_response_success(full_response)
            
        self.logger.info(f"\n成功查询到 {len(result)} 条状态为 {so_status} 的订单数据")


    @allure.title("按单据类型查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按单据类型查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(3)
    @safe_api_call(error_message="按单据类型查询销售订单列表失败")
    def test_03_query_orders_by_so_type(self):
        """测试按单据类型查询销售订单列表"""
        
        # 若test_data无值则自动初始化
        if not self.test_data.get("so_type_id"):
            self._query_orders()
            
        url = self.sls_api_paths["订单管理"]["查询订单"]
        data = self.sls_api_params[url]
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
        data["params"]["request"]["pageable"]["conditionGroup"] = conditionGroup
        # 构建按单据类型筛选的查询条件
        # 执行测试
        self.logger.info(f"查询条件: 订单类型ID = {self.test_data['so_type_id']}")
        
        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按单据类型查询销售订单列表")
        result =  nested_data.get("data", {}).get("data", []).get("data", [])
        # 验证查询结果
        self.assert_util.assert_not_empty(result, "未查询到匹配的订单数据")
        
        # 验证所有返回的订单都匹配查询条件
        for order in result:
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
            
        self.logger.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")


    @allure.title("按客户查询销售订单列表")
    @allure.description("""
    测试步骤：
    1. 按客户查询销售订单列表
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(4)
    @safe_api_call(error_message="按客户查询销售订单列表失败")
    def test_04_query_orders_by_customer(self):
        """测试按客户查询销售订单列表"""
        
        # 若test_data无值则自动初始化
        if not self.test_data.get("cust_id"):
            self._query_orders()
            
        url = self.sls_api_paths["订单管理"]["查询订单"]
        data = self.sls_api_params[url]
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
        data["params"]["request"]["pageable"]["conditionGroup"] = conditionGroup
        
        # 执行测试
        self.logger.info(f"查询条件: 客户ID = {self.test_data['cust_id']}")
        
        # 获取提取后的嵌套数据
        nested_data = self.http.post(url, json=data, description="按客户查询销售订单列表")
        result =  nested_data.get("data", {}).get("data", []).get("data", [])
        # 验证查询结果
        self.assert_util.assert_not_empty(result, "未查询到匹配的订单数据")
        
        # 验证所有返回的订单都匹配查询条件
        for order in result:
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
            
        self.logger.info(f"\n成功查询到 {len(nested_data)} 条匹配的订单数据")

if __name__ == "__main__":
    test = TestOrderList()
    test.setup_class()
    test.test_01_query_orders()
    test.test_02_query_orders_by_so_code()
    test.test_03_query_orders_by_status("DRAFT")
    test.test_03_query_orders_by_status("EFFECT")
    test.test_03_query_orders_by_status("APPROVING")
    test.test_03_query_orders_by_status("CANCELLED")
    test.test_04_query_orders_by_so_type()
    test.test_05_query_orders_by_customer()
   # project_root = Path(__file__).resolve().parent.parent
   # allure_dir = Path(project_root) / "reports" / "allure-results"
   # pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
    