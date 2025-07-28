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
@allure.feature("销售订单查询")
class TestSoQuery(SlsBase):
    """销售订单查询功能测试类"""

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

        # 初始化查询相关变量
        cls.so_head_id = None
        cls.so_code = None
        cls.created_orders = []  # 存储创建的测试订单
        
        a.text("销售订单查询测试类初始化完成", "初始化信息")

    @case_decorator(
        story="销售订单查询",
        title="销售订单分页查询服务",
        description="验证sls_so_head_paging_service接口",
        severity="critical",
        order=1,
        tags=["销售订单", "分页查询", "sls_so_head_paging_service"]
    )
    def test_sls_so_head_paging_service(self):
        """销售订单分页查询服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-正逆向分页服务")
            params, url = self.get_api_params(api_path)
            params['params']= {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "sortOrders": None,
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
                            "conditionGroup": None
                        }
                    }
                }
            response = self.http.post(url, json=params, description="销售订单分页查询")
            self.assert_util.assert_response_data(response)
            
            # 验证分页查询结果
            response_data = response.get("data", {}).get("data", {})

            
            # 获取订单列表数据
            order_list = response_data.get("data", [])
            total_count = response_data.get("total", 0)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"查询到 {len(order_list)} 条订单记录，总计 {total_count} 条", "查询结果")
            
            # 如果有数据，保存第一条用于后续测试
            if order_list and len(order_list) > 0:
                first_order = order_list[0]
                self.so_head_id = first_order.get("id")
                self.so_code = first_order.get("soCode")
                a.text(f"获取测试订单: ID={self.so_head_id}, Code={self.so_code}", "测试数据")
            
        except Exception as e:
            a.text(str(e), "分页查询失败原因")
            raise

    @case_decorator(
        story="销售订单查询",
        title="按订单号查询订单",
        description="验证按订单号查询订单接口",
        severity="critical",
        order=2,
        tags=["销售订单", "订单号查询"]
    )
    def test_query_orders_by_so_code(self):
        """按订单号查询订单"""
        try:
            # 确保有可查询的订单号
            if not self.so_code:
                self.test_sls_so_head_paging_service()

            api_path = self.get_api_path("SLS-销售订单-正逆向分页服务")
            params, url = self.get_api_params(api_path)
            
            # 构造按订单号查询的条件
            params['params'] =  {
                    "request": {
                        "pageable":{
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
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
                        "conditionGroup": {
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
                                                    "key": "lGyYDbJLZ1VPAY8yEkVcw",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "3jr1A95-RcRHzLcP_t4hz",
                                                        "key": "3jr1A95-RcRHzLcP_t4hz",
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
                                                        "key": "u9nxapbmbBWKjHizKr4oV",
                                                        "type": "VarValue",
                                                        "fieldType": "Text",
                                                        "valueType": "CONST",
                                                        "constValue": self.so_code
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                        
                    }
                }
            }
                    

            response = self.http.post(url, json=params, description="按订单号查询订单")
            self.assert_util.assert_response_data(response)
            
            # 验证查询结果
            response_data = response.get("data", {}).get("data", {})
            total_count = response_data.get("total", 0)
            self.assert_util.assert_by_operator(total_count, "=", 1,"未找到匹配的订单数据")
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
            a.text(f"成功查询到订单: {self.so_code}", "查询结果")
            
        except Exception as e:
            a.text(str(e), "按订单号查询失败原因")
            raise

    @case_decorator(
        story="销售订单查询",
        title="按订单状态查询订单",
        description="验证按订单状态查询订单接口",
        severity="critical",
        order=3,
        tags=["销售订单", "状态查询"]
    )
    @pytest.mark.parametrize("target_status", [["DRAFT", "EFFECT", "APPROVING", "CANCELLED"]])
    def test_query_orders_by_status(self,target_status):
        """按订单状态查询订单"""
        try:
            api_path = self.get_api_path("SLS-销售订单-正逆向分页服务")
            params, url = self.get_api_params(api_path)
            
            # 构造按状态查询的条件
            params['params'] = {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
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
                        "conditionGroup": {
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
                                                    "key": "soStatusCondition",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "soStatus_field",
                                                        "key": "soStatus_field",
                                                        "type": "VarValue",
                                                        "fieldType": "Enum",
                                                        "valueType": "VAR",
                                                        "varValue": [
                                                            {
                                                                "valueKey": "soStatus",
                                                                "valueName": "soStatus"
                                                            }
                                                        ]
                                                    },
                                                    "operator": "IN",
                                                    "rightValue": {
                                                        "key": "soStatus_value",
                                                        "type": "VarValue",
                                                        "fieldType": "Enum",
                                                        "valueType": "CONST",
                                                        "constValue": target_status
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }

            response = self.http.post(url, json=params, description="按状态查询订单")
            self.assert_util.assert_response_data(response)
            
            # 验证查询结果
            response_data = response.get("data", {}).get("data", {})
            order_list = response_data.get("data", [])
            total_count = response_data.get("total", 0)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
            # 验证返回结果中的状态都在请求的状态列表中
            if order_list and len(order_list) > 0:
                requested_status = set(target_status)
                actual_status = set(item.get("soStatus") for item in order_list if item.get("soStatus"))
                self.assert_util.assert_true(
                    actual_status.issubset(requested_status), 
                    f"查询结果包含未请求的状态: {actual_status - requested_status}"
                )
                a.text(f"查询到 {len(order_list)} 条符合状态条件的订单，状态包括: {actual_status}", "查询结果")
            else:
                a.text("未查询到符合状态条件的订单", "查询结果")
            
        except Exception as e:
            a.text(str(e), "按状态查询失败原因")
            raise

    @case_decorator(
        story="销售订单查询",
        title="按客户查询订单",
        description="验证按客户查询订单接口",
        severity="critical",
        order=4,
        tags=["销售订单", "客户查询"]
    )
    def test_query_orders_by_customer(self):
        """按客户查询订单"""
        try:
            api_path = self.get_api_path("SLS-销售订单-正逆向分页服务")
            params, url = self.get_api_params(api_path)
            
            # 构造按客户查询的条件
            params['params'] = {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
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
                        "conditionGroup": {
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
                                                    "key": "custIdCondition",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "custId_field",
                                                        "key": "custId_field",
                                                        "type": "VarValue",
                                                        "fieldType": "Integer",
                                                        "valueType": "VAR",
                                                        "varValue": [
                                                            {
                                                                "valueKey": "custId",
                                                                "valueName": "custId"
                                                            }
                                                        ]
                                                    },
                                                    "operator": "EQ",
                                                    "rightValue": {
                                                        "key": "custId_value",
                                                        "type": "VarValue",
                                                        "fieldType": "Integer",
                                                        "valueType": "CONST",
                                                        "constValue": self.cust_id
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }

            response = self.http.post(url, json=params, description="按客户查询订单")
            self.assert_util.assert_response_data(response)
            
            # 验证查询结果
            response_data = response.get("data", {}).get("data", {})
            order_list = response_data.get("data", [])
            total_count = response_data.get("total", 0)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
            # 验证查询结果中的客户ID是否匹配
            if order_list and len(order_list) > 0:
                for order in order_list:
                    order_cust_id = order.get("custId", {}).get("id") if isinstance(order.get("custId"), dict) else order.get("custId")
                    if order_cust_id:
                        self.assert_util.assert_eq(
                            str(order_cust_id), str(self.cust_id), 
                            f"订单客户ID {order_cust_id} 与查询条件 {self.cust_id} 不匹配"
                        )
                a.text(f"查询到客户 {self.cust_id} 的 {len(order_list)} 条订单", "查询结果")
            else:
                a.text(f"客户 {self.cust_id} 暂无订单数据", "查询结果")
            
        except Exception as e:
            a.text(str(e), "按客户查询失败原因")
            raise

    @case_decorator(
        story="销售订单查询",
        title="按日期范围查询订单",
        description="验证按订单日期范围查询订单接口",
        severity="critical",
        order=5,
        tags=["销售订单", "日期查询"]
    )
    def test_query_orders_by_date_range(self):
        """按日期范围查询订单"""
        try:
            api_path = self.get_api_path("SLS-销售订单-正逆向分页服务")
            params, url = self.get_api_params(api_path)
            
            # 设置查询日期范围（最近30天）
            start_date = self.mock_util.get_timestamp(timestamp=True, day_offset=-30)
            end_date = self.mock_util.get_timestamp(timestamp=True)
            
            # 构造按日期范围查询的条件
            params['params'] = {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
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
                        "conditionGroup": {
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
                                                    "key": "soDocDateGE",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "soDocDate_field1",
                                                        "key": "soDocDate_field1",
                                                        "type": "VarValue",
                                                        "fieldType": "Date",
                                                        "valueType": "VAR",
                                                        "varValue": [
                                                            {
                                                                "valueKey": "soDocDate",
                                                                "valueName": "soDocDate"
                                                            }
                                                        ]
                                                    },
                                                    "operator": "GE",
                                                    "rightValue": {
                                                        "key": "soDocDate_start",
                                                        "type": "VarValue",
                                                        "fieldType": "Date",
                                                        "valueType": "CONST",
                                                        "constValue": start_date
                                                    }
                                                },
                                                {
                                                    "key": "soDocDateLE",
                                                    "type": "ConditionLeaf",
                                                    "leftValue": {
                                                        "id": "soDocDate_field2",
                                                        "key": "soDocDate_field2",
                                                        "type": "VarValue",
                                                        "fieldType": "Date",
                                                        "valueType": "VAR",
                                                        "varValue": [
                                                            {
                                                                "valueKey": "soDocDate",
                                                                "valueName": "soDocDate"
                                                            }
                                                        ]
                                                    },
                                                    "operator": "LE",
                                                    "rightValue": {
                                                        "key": "soDocDate_end",
                                                        "type": "VarValue",
                                                        "fieldType": "Date",
                                                        "valueType": "CONST",
                                                        "constValue": end_date
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }

            response = self.http.post(url, json=params, description="按日期范围查询订单")
            self.assert_util.assert_response_data(response)
            
            # 验证查询结果
            response_data = response.get("data", {}).get("data", {})
            order_list = response_data.get("data", [])
            total_count = response_data.get("total", 0)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"查询日期范围 {start_date} 到 {end_date}，共 {len(order_list)} 条订单", "查询结果")
            
        except Exception as e:
            a.text(str(e), "按日期查询失败原因")
            raise