# -*- coding: utf-8 -*-
"""
应收单测试模块
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from data_factory.fin_ar_factory import FinArFactory
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import time

def convert_decimal_to_float(obj):
    """递归转换Decimal类型为float - 公共工具函数"""
    if isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

@allure.epic("ERP通业财模块")
@allure.feature("应收管理")
class ArBaseTest(BaseTest):
    """应收单测试基类，提供通用功能"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ar_factory = FinArFactory()
        
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params

    def create_ar_request_body(self, now_ts, output_dict):
        """创建应收单请求体，结果存储到output_dict中"""
        com_org_id = self.ar_factory.get_org_by_id(14373001)["id"]
        sls_org_id = self.ar_factory.get_org_by_id(14579001)["id"]
        curr_id = self.ar_factory.create_currency()["id"]
        customer_id = self.ar_factory.get_customer_by_id(14103001)["id"]
        mat_id = self.ar_factory.get_material_by_id(14672002)["id"]
        tax_code_id = self.ar_factory.get_tax_code_by_id(2002002)["id"]
        sett_item_type_id = self.ar_factory.get_sett_item_type_by_id(12)["id"]
        
        ar_items = self.ar_factory.create_ar_items_full(mat_id, tax_code_id, sett_item_type_id)
        ar_schls = self.ar_factory.create_ar_schls_full(due_date=now_ts)
        
        gross_doc_amt = sum([item.get("grossDocAmt", 0) for item in ar_items])
        net_doc_amt = sum([item.get("netDocAmt", 0) for item in ar_items])
        gross_base_amt = sum([item.get("grossBaseAmt", 0) for item in ar_items])
        net_base_amt = sum([item.get("netBaseAmt", 0) for item in ar_items])
        tax_amt = sum([item.get("taxAmt", 0) for item in ar_items])
        
        output_dict.update({
            "docTypeId": {"id": 14003001},
            "arDate": now_ts,
            "comOrgId": {"id": com_org_id},
            "slsOrgId": {"id": sls_org_id},
            "payOrgId": {"id": com_org_id},
            "docCurrId": {"id": curr_id},
            "baseCurrId": {"id": curr_id},
            "exchRate": 1,
            "settPartnerType": "CUSTOMER",
            "settPartnerId": {"id": customer_id},
            "arStatus": "DRAFT",
            "collectionClearingStatus": "UNCLEARED",
            "billingClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "remark": ParamUtil.generate_remark(),
            "arItems": ar_items,
            "arSchls": ar_schls,
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_base_amt,
            "netBaseAmt": net_base_amt,
            "taxAmt": tax_amt,
            "uncollectedDocAmt": gross_doc_amt,
            "uncollectedBaseAmt": gross_base_amt,
            "unbilledDocAmt": gross_doc_amt,
            "unbilledBaseAmt": gross_base_amt,
            "unoffsetDocAmt": gross_doc_amt,
            "unoffsetBaseAmt": gross_base_amt
        })

    def send_api_request(self, api_key, request_data, result_dict):
        """发送API请求，结果存储到result_dict中"""
        api_path = ParamUtil.get_api_path(self.apis, api_key)
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        filtered_params = ParamUtil.filter_post_body_fields(
            params, list(request_data.keys()), ["params", "request"]
        )
        ParamUtil.set_request_params(filtered_params, request_data)
        filtered_params = convert_decimal_to_float(filtered_params)
        
        result = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(result)
        
        a.json(filtered_params, "请求数据")
        a.json(result, "响应结果数据")
        
        result_dict.update(result)

    def wait_for_ar_status(self, ar_head_code, target_status, status_result, max_wait=60, interval=2):
        """等待应收单状态变更，结果存储到status_result中"""
        api_path = ParamUtil.get_api_path(self.apis, "应收单头表-分页数据服务_PmHKWs4")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        ParamUtil.set_request_params(params, {
            "pageable": {
                "pageNo": 1,
                "pageSize": 1,
                "needTotal": False,
                "conditionItems": {
                    "type": "ConditionItems",
                    "conditions": {"arHeadCode": {"operator": "CONTAINS", "value": ar_head_code}},
                    "logicOperator": "AND"
                }
            }
        })
        
        waited = 0
        while waited < max_wait:
            result = self.http.post(url, json=params)
            self.assert_util.assert_response_success(result)
            
            data_list = result.get("data", {}).get("data", {}).get("data", [])
            if data_list and data_list[0].get("arStatus") == target_status:
                status_result.update({
                    "status": target_status,
                    "success": True,
                    "waited_time": waited
                })
                break
            
            time.sleep(interval)
            waited += interval
        else:
            status_result.update({
                "status": None,
                "success": False,
                "waited_time": waited
            })

    def query_ar_detail(self, ar_doc_id, ar_detail):
        """查询应收单详情，结果存储到ar_detail中"""
        api_path = ParamUtil.get_api_path(self.apis, "应收单头表-根据ID查找数据服务")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        query_params = {
            "sceneKey": "ERP_FIN$FIN_ARM_FROM_DS",
            "viewKey": "ERP_FIN$FIN_ARM_FROM_DS:detail",
            "containerKey": "ERP_FIN$FIN_ARM_FROM_DS-TERP_MIGRATE$FIN_ARM_230706-detailView-detail",
            "appId": 0,
            "teamId": 22,
            "serviceKey": "ERP_FIN$FIN_ARM_AR_HEAD_TR_FIND_DATA_BY_ID_SERVICE",
            "params": {"request": {"id": str(ar_doc_id)}}
        }
        
        result = self.http.post(url, json=query_params)
        self.assert_util.assert_response_success(result)
        ar_detail.update(result.get("data", {}).get("data", {}))

    def build_sb_request_params(self, sb_record, sb_id, bil_code, status, output_dict):
        """构建销售发票请求参数，结果存储到output_dict中"""
        core_fields = [
            "id", "sbStatus", "sbHeadCode", "bilCode", "sbDate", 
            "docTypeId", "comOrgId", "slsOrgId", "docCurrId", "baseCurrId", 
            "exchRate", "traParType", "traParId", "bilDocAmt", "bilBaseAmt", 
            "clearingDocAmt", "clearingBaseAmt", "bilDocTax", "bilBaseTax", "version"
        ]
        
        request_data = {
            "id": sb_id,
            "sbStatus": status,
            "sbHeadCode": sb_record.get("sbHeadCode"),
            "bilCode": bil_code,
            "sbDate": sb_record.get("sbDate"),
            "docTypeId": {"id": sb_record.get("docTypeId", {}).get("id")},
            "comOrgId": {"id": sb_record.get("comOrgId", {}).get("id")},
            "slsOrgId": {"id": sb_record.get("slsOrgId", {}).get("id")},
            "docCurrId": {"id": sb_record.get("docCurrId", {}).get("id")},
            "baseCurrId": {"id": sb_record.get("baseCurrId", {}).get("id")},
            "exchRate": sb_record.get("exchRate", 1),
            "traParType": sb_record.get("traParType"),
            "traParId": {"id": sb_record.get("traParId", {}).get("id")},
            "bilDocAmt": sb_record.get("bilDocAmt", 0),
            "bilBaseAmt": sb_record.get("bilBaseAmt", 0),
            "clearingDocAmt": sb_record.get("clearingDocAmt", 0),
            "clearingBaseAmt": sb_record.get("clearingBaseAmt", 0),
            "bilDocTax": sb_record.get("bilDocTax", 0),
            "bilBaseTax": sb_record.get("bilBaseTax", 0),
            "version": sb_record.get("version", 0)
        }
        
        output_dict.update({
            "core_fields": core_fields,
            "request_data": request_data
        }) 