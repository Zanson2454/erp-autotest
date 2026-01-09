# -*- coding: utf-8 -*-
"""
应付单（AP）测试模块
提供统一的基类和初始化配置管理
"""
import allure
from typing import Dict, Any
from datetime import datetime
import time
import decimal

from testcases.erp_fin import FinBaseTest
from data_factory.fin_ap_factory import FinApFactory
from utils.param_util import ParamUtil
from utils.report_util import a


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付单模块")
class ApBaseTest(FinBaseTest):
    """
    应付单测试基类
    
    功能说明：
    1. 继承 FinBaseTest，提供财务模块的基础能力
    2. 提供应付单相关的公共方法和工具函数
    3. 所有 fin_ap 模块下的测试类应继承此基类
    
    继承的能力：
    - APIs配置（apis、api_params）
    - Mock工具（mock_util）
    - 数据库连接（db）
    - HTTP客户端（http）
    - 缓存数据（md_cache_data、fin_cache_data）
    - 标准化API调用（standard_api_call）
    
    使用示例：
        from testcases.erp_fin.fin_ap import ApBaseTest
        
        class TestMyFeature(ApBaseTest):
            def test_something(self):
                # 可以直接使用 self.ap_factory、self.mock_util 等
                pass
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化 - 初始化应付单数据工厂"""
        super().setup_class()
        cls.ap_factory = FinApFactory()
        # mock_util 已在 FinBaseTest.setup_class() 中初始化
        cls.logger.info("应付单测试基类初始化完成")
    
    @staticmethod
    def convert_decimal_to_float(obj):
        """递归将字典/列表中的 Decimal 转为 float"""
        if isinstance(obj, dict):
            return {k: ApBaseTest.convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ApBaseTest.convert_decimal_to_float(i) for i in obj]
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return obj
    
    def create_ap_request_body(self, doc_type_id: int = 2002001, account_type: str = "FIN") -> Dict[str, Any]:
        """
        创建应付单请求体的通用方法
        
        :param doc_type_id: 单据类型ID，默认2002001
        :param account_type: 账户类型，默认"FIN"（财务），可选"EST"（暂估）
        :return: 包含请求体和基础数据的字典
        """
        now = datetime.now()
        now_ts = int(now.timestamp() * 1000)
        
        # 使用数据工厂生成基础数据
        com_org = self.ap_factory.create_org("COM")
        vend = self.ap_factory.create_vendor()
        pur_org = self.ap_factory.create_org("PUR")
        pay_org = com_org
        curr = self.ap_factory.create_currency()
        tax_code = self.ap_factory.create_tax_code()
        mat = self.ap_factory.create_material()
        
        # 创建应付单明细和计划
        mat_list = [mat, mat]
        tax_code_list = [tax_code, tax_code]
        ap_items = self.ap_factory.create_ap_items_full(mat_list, tax_code_list)
        
        # 转换金额类型
        for item in ap_items:
            for k in ["grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt"]:
                if k in item:
                    item[k] = float(item[k])
        
        # 计算总金额
        total_amt = float(sum([item["grossDocAmt"] for item in ap_items]))
        net_doc_amt = float(sum([item["netDocAmt"] for item in ap_items]))
        gross_base_amt = float(sum([item["grossBaseAmt"] for item in ap_items]))
        net_base_amt = float(sum([item["netBaseAmt"] for item in ap_items]))
        
        # 创建应付计划
        ap_schl = self.ap_factory.create_ap_schl(amount=total_amt, due_date=now_ts)
        if isinstance(ap_schl, dict):
            for k in ap_schl:
                if hasattr(ap_schl[k], "__float__"):
                    ap_schl[k] = float(ap_schl[k])
        
        # 构建请求体
        request_body = {
            "docTypeId": {"id": doc_type_id},
            "apDate": now_ts,
            "comOrgId": com_org,
            "purOrgId": pur_org,
            "payOrgId": pay_org,
            "apHeadCode": self.mock_util.generate_unique_code("AP"),
            "remark": f"自动化测试创建应付单 - {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "settPartnerType": "SUPPLIER",
            "settPartnerId": {"id": vend["id"]},
            "docCurrId": {"id": curr["id"]},
            "baseCurrId": {"id": curr["id"]},
            "exchRate": 1,
            "grossDocAmt": total_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_base_amt,
            "netBaseAmt": net_base_amt,
            "payClearingStatus": "UNCLEARED",
            "invClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "apItems": ap_items,
            "apSchls": [ap_schl]
        }
        
        if account_type == "EST":
            request_body["accountType"] = "EST"
        
        # 返回请求体和基础数据
        return {
            "request_body": request_body,
            "base_data": {
                "vend": vend,
                "pay_org": pay_org,
                "com_org": com_org,
                "pur_org": pur_org,
                "currency": curr,
                "total_amt": total_amt,
                "net_doc_amt": net_doc_amt,
                "gross_base_amt": gross_base_amt,
                "net_base_amt": net_base_amt
            }
        }
    
    def send_api_request(self, api_key: str, request_data: Dict[str, Any], 
                        fields: list = None) -> Dict[str, Any]:
        """
        发送API请求的通用方法（向后兼容方法）
        
        注意：推荐使用 standard_api_call 方法，此方法保留用于向后兼容
        
        :param api_key: API服务名称键
        :param request_data: 请求数据字典
        :param fields: 需要过滤的字段列表（可选）
        :return: 包含响应结果和请求参数的字典
        """
        api_path = ParamUtil.get_api_path(self.apis, api_key)
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        if fields:
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields, ["params", "request"]
            )
        else:
            filtered_params = params
        
        ParamUtil.set_request_params(filtered_params, request_data)
        filtered_params = self.convert_decimal_to_float(filtered_params)
        
        result = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(result)
        
        return {
            "result": result,
            "request_params": filtered_params
        }
    
    def wait_for_ap_status(self, ap_head_code: str, expected_status: str, 
                          max_wait: int = 30, interval: int = 2) -> bool:
        """
        等待应付单状态变更的通用方法
        
        :param ap_head_code: 应付单编码
        :param expected_status: 期望的状态值
        :param max_wait: 最大等待时间（秒），默认30秒
        :param interval: 轮询间隔（秒），默认2秒
        :return: 如果状态变更成功返回True，否则返回False
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # 查询应付单状态
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据编码查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["apHeadCode"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {"apHeadCode": ap_head_code})
                
                result = self.http.post(url, json=filtered_params)
                if result.get("success"):
                    data = result.get("data", {}).get("data", {})
                    current_status = data.get("apStatus")
                    async_status = data.get("asyncExecutionStatus")
                    
                    if current_status == expected_status and async_status == "SUCCEEDED":
                        a.text(f"应付单状态已变更为: {current_status}", "状态检查结果")
                        return True
                    elif async_status == "FAILED":
                        failure_reason = data.get("asyncExecutionFailureReason", "未知原因")
                        a.text(f"应付单异步执行失败: {failure_reason}", "失败原因")
                        raise Exception(f"应付单异步执行失败: {failure_reason}")
                
                time.sleep(interval)
                
            except Exception as e:
                a.text(f"状态检查异常: {str(e)}", "异常信息")
                time.sleep(interval)
        
        a.text(f"等待超时，应付单状态未变更为: {expected_status}", "超时信息")
        return False
    
    def query_ap_detail(self, ap_head_code: str) -> Dict[str, Any]:
        """
        查询应付单详情的通用方法（按编码查询）
        
        :param ap_head_code: 应付单编码
        :return: 应付单详情数据字典，如果查询失败或未找到则返回None
        """
        try:
            # 使用应付单数据查询服务按编码查询
            api_path = ParamUtil.get_api_path(self.apis, "AP-应付单-数据查询服务")
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["apHeadCode"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"apHeadCode": ap_head_code})
            
            result = self.http.post(url, json=filtered_params)
            
            if result.get("success"):
                data = result.get("data", {}).get("data", {})
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # 返回第一条记录
                elif isinstance(data, dict):
                    return data
            
            return None
            
        except Exception as e:
            a.text(f"查询应付单详情失败: {str(e)}", "查询异常")
            self.logger.error(f"查询应付单详情失败: {str(e)}")
            return None
    
    @staticmethod
    def safe_api_call(func):
        """
        安全API调用装饰器
        
        使用示例：
            @ApBaseTest.safe_api_call
            def my_api_method(self):
                # API调用逻辑
                pass
        """
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                a.text(str(e), "API调用失败")
                self.logger.error(f"API调用失败: {str(e)}")
                raise
        return wrapper 