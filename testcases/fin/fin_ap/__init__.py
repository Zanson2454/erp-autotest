# -*- coding: utf-8 -*-
"""
应付单测试模块
"""
from pathlib import Path
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import time
import decimal

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.comm.base_test import BaseTest
from data_factory.fin_ap_factory import FinApFactory
from utils.param_util import ParamUtil
from utils.allure_simple import a


class ApBaseTest(BaseTest):
    """应付单测试基类，提供公共方法和配置"""
    
    @classmethod
    def setup_class(cls):
        """初始化测试类配置"""
        super().setup_class()
        cls.ap_factory = FinApFactory()
        
        # 初始化财务API配置
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params
    
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
        """创建应付单请求体的通用方法"""
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
            "apHeadCode": ParamUtil.generate_unique_code("AP"),
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
        """发送API请求的通用方法"""
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
        """等待应付单状态变更的通用方法"""
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
        """查询应付单详情的通用方法（按编码查询）"""
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
            return None
    
    def safe_api_call(func):
        """安全API调用装饰器"""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                a.text(str(e), "API调用失败")
                raise
        return wrapper 