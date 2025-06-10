"""
应付单保存服务测试用例
包含创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from data_factory.fin_ap_factory import FinApFactory
from datetime import datetime
import time
from pathlib import Path
from utils.yaml_util import YamlUtil
import decimal

# 工具：递归将Decimal转float
def _convert_decimal_to_float(obj):
    if isinstance(obj, dict):
        return {k: _convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApDocumentSave(BaseTest):
    ap_save_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ap_factory = FinApFactory()
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        base_api_path = project_root / "testdata" / "fin" / "fin_api_path.yaml"
        base_api_params = project_root / "testdata" / "fin" / "fin_api_params.yaml"
        yaml_util = YamlUtil()
        cls.apis = yaml_util.read_yaml(base_api_path).get("apis", {})
        cls.api_params = yaml_util.read_yaml(base_api_params).get("api_params", {})

    @ParamUtil.case_decorator(
        story="应付单保存",
        title="创建标准应付单",
        description="创建标准应付单并断言成功",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ap", "save", "draft"]
    )
    def test_create_draft_ap_doc(self):
        try:
            with a.step("创建标准应付单"):
                now = datetime.now()
                now_ts = int(now.timestamp() * 1000)
                com_org = self.ap_factory.create_org("COM")
                vend = self.ap_factory.create_vendor()
                pur_org = self.ap_factory.create_org("PUR")
                pay_org = com_org
                curr = self.ap_factory.create_currency()
                tax_code = self.ap_factory.create_tax_code()
                mat = self.ap_factory.create_material()
                mat_list = [mat, mat]
                tax_code_list = [tax_code, tax_code]
                ap_items = self.ap_factory.create_ap_items_full(mat_list, tax_code_list)
                for item in ap_items:
                    for k in ["grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt"]:
                        if k in item:
                            item[k] = float(item[k])
                total_amt = float(sum([item["grossDocAmt"] for item in ap_items]))
                net_doc_amt = float(sum([item["netDocAmt"] for item in ap_items]))
                gross_base_amt = float(sum([item["grossBaseAmt"] for item in ap_items]))
                net_base_amt = float(sum([item["netBaseAmt"] for item in ap_items]))
                ap_schl = self.ap_factory.create_ap_schl(amount=total_amt, due_date=now_ts)
                if isinstance(ap_schl, dict):
                    for k in ap_schl:
                        if hasattr(ap_schl[k], "__float__"):
                            ap_schl[k] = float(ap_schl[k])
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", "remark", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", "payClearingStatus", "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"],
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "docTypeId": {"id": 2002001},
                    "apDate": now_ts,
                    "comOrgId": com_org,
                    "purOrgId": pur_org,
                    "payOrgId": pay_org,
                    "apHeadCode": ParamUtil.generate_unique_code("AP"),
                    "remark": ParamUtil.generate_remark(),
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
                })
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                ap_doc_id = ParamUtil.extract_id(result)
                assert ap_doc_id, "创建应付单失败：未获取到单据ID"
                request_body = filtered_params["params"]["request"].copy()
                TestApDocumentSave.ap_save_info.update({
                    "ap_doc_id": ap_doc_id,
                    "apHeadCode": filtered_params["params"]["request"]["apHeadCode"],
                    "settPartnerId": vend,
                    "payOrgId": pay_org,
                    "comOrgId": com_org,
                    "purOrgId": pur_org,
                    "total_amt": total_amt,
                    "net_doc_amt": net_doc_amt,
                    "gross_base_amt": gross_base_amt,
                    "net_base_amt": net_base_amt,
                    "request_body": request_body
                })
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentSave.ap_save_info, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单编辑",
        title="编辑为标准暂估应付单",
        description="编辑为标准暂估应付单并保存",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ap", "edit", "estimate"]
    )
    def test_edit_ap_doc_to_estimate(self):
        try:
            with a.step("编辑为标准暂估应付单"):
                ap_doc_id = TestApDocumentSave.ap_save_info.get("ap_doc_id")
                assert ap_doc_id, "请先执行创建标准应付单用例"
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                base_request = TestApDocumentSave.ap_save_info.get("request_body", {}).copy()
                base_request["id"] = ap_doc_id
                base_request["docTypeId"] = {"id": 2002002}
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(base_request.keys()),
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, base_request)
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True
                assert isinstance(data.get("id"), int)
                assert data.get("docTypeId", {}).get("id") == 2002002
                assert data.get("apHeadCode")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单提交",
        title="提交应付单-AP_SUBMIT_WITH_HEAD_EVENT_SERVICE（动态单据）",
        description="用前置用例生成的单据进行提交并断言成功",
        severity="critical",
        order=3,
        smoke=False,
        tags=["ap", "submit"]
    )
    def test_submit_ap_doc(self):
        try:
            with a.step("提交应付单"):
                ap_doc_id = TestApDocumentSave.ap_save_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_save_info.get("apHeadCode")
                sett_partner_id = TestApDocumentSave.ap_save_info.get("settPartnerId")
                pay_org_id = TestApDocumentSave.ap_save_info.get("payOrgId")
                total_amt = TestApDocumentSave.ap_save_info.get("total_amt")
                net_doc_amt = TestApDocumentSave.ap_save_info.get("net_doc_amt")
                gross_base_amt = TestApDocumentSave.ap_save_info.get("gross_base_amt")
                net_base_amt = TestApDocumentSave.ap_save_info.get("net_base_amt")
                assert ap_doc_id and ap_head_code and sett_partner_id and pay_org_id, "请先执行创建用例，确保ap_doc_id、apHeadCode、settPartnerId和payOrgId已生成"
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付单-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    ["apHeadCode", "apStatus", "comOrgId", "purOrgId", "payOrgId", "grossDocAmt", "grossBaseAmt", "payClearingStatus", "invClearingStatus", "unpaidDocAmt", "uninvoicedDocAmt", "unpaidBaseAmt", "uninvoicedBaseAmt", "unoffsetDocAmt", "unoffsetBaseAmt", "headOffsetStatus", "asyncExecutionStatus", "id", "apItems", "apSchls", "settPartnerId", "netDocAmt", "netBaseAmt"],
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "apHeadCode": ap_head_code,
                    "apStatus": "CONFIRM",
                    "comOrgId": pay_org_id,
                    "purOrgId": pay_org_id,
                    "payOrgId": pay_org_id,
                    "grossDocAmt": total_amt,
                    "grossBaseAmt": gross_base_amt,
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": total_amt,
                    "uninvoicedDocAmt": total_amt,
                    "unpaidBaseAmt": net_base_amt,
                    "uninvoicedBaseAmt": total_amt,
                    "unoffsetDocAmt": total_amt,
                    "unoffsetBaseAmt": total_amt,
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id,
                    "apItems": [],
                    "apSchls": [],
                    "settPartnerId": {"id": sett_partner_id["id"]},
                    "netDocAmt": net_doc_amt,
                    "netBaseAmt": net_base_amt
                })
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                data = result.get("data", {}).get("data", {})
                assert data.get("apHeadCode") == ap_head_code
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单过账",
        title="应付单过账-AP_POST_ASYNC_EVENT_SERVICE（动态单据）",
        description="用前置用例生成的单据进行过账并断言成功",
        severity="critical",
        order=4,
        smoke=False,
        tags=["ap", "post"]
    )
    def test_post_ap_doc(self):
        try:
            with a.step("应付单过账"):
                ap_doc_id = TestApDocumentSave.ap_save_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_save_info.get("apHeadCode")
                sett_partner_id = TestApDocumentSave.ap_save_info.get("settPartnerId")
                pay_org_id = TestApDocumentSave.ap_save_info.get("payOrgId")
                total_amt = TestApDocumentSave.ap_save_info.get("total_amt")
                net_doc_amt = TestApDocumentSave.ap_save_info.get("net_doc_amt")
                gross_base_amt = TestApDocumentSave.ap_save_info.get("gross_base_amt")
                net_base_amt = TestApDocumentSave.ap_save_info.get("net_base_amt")
                assert ap_doc_id and ap_head_code and sett_partner_id and pay_org_id, "请先执行创建用例，确保ap_doc_id、apHeadCode、settPartnerId和payOrgId已生成"
                api_path = ParamUtil.get_api_path(self.apis, "应付单-过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    ["apHeadCode", "docTypeId", "apStatus", "comOrgId", "purOrgId", "payOrgId", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", "payClearingStatus", "invClearingStatus", "unpaidDocAmt", "uninvoicedDocAmt", "unpaidBaseAmt", "uninvoicedBaseAmt", "unoffsetDocAmt", "unoffsetBaseAmt", "headOffsetStatus", "asyncExecutionStatus", "id"],
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "apHeadCode": ap_head_code,
                    "docTypeId": {"id": 2002001},
                    "apStatus": "CONFIRM",
                    "comOrgId": pay_org_id,
                    "purOrgId": pay_org_id,
                    "payOrgId": pay_org_id,
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": sett_partner_id["id"]},
                    "docCurrId": {"id": pay_org_id["id"]},
                    "baseCurrId": {"id": pay_org_id["id"]},
                    "exchRate": 1,
                    "grossDocAmt": total_amt,
                    "netDocAmt": net_doc_amt,
                    "grossBaseAmt": gross_base_amt,
                    "netBaseAmt": net_base_amt,
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": total_amt,
                    "uninvoicedDocAmt": total_amt,
                    "unpaidBaseAmt": net_base_amt,
                    "uninvoicedBaseAmt": net_base_amt,
                    "unoffsetDocAmt": total_amt,
                    "unoffsetBaseAmt": total_amt,
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id
                })
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单状态校验",
        title="根据单据编号分页精简查询应付单状态",
        description="用apHeadCode分页精简查询应付单详情并断言状态（yaml参数自动获取）",
        severity="critical",
        order=5,
        smoke=False,
        tags=["ap", "check", "status", "by_code", "paging"]
    )
    def test_check_ap_doc_status_by_code_paging(self):
        try:
            with a.step("根据单据编号分页精简查询应付单状态"):
                ap_head_code = TestApDocumentSave.ap_save_info.get("apHeadCode")
                assert ap_head_code, "请先执行创建用例，确保apHeadCode已生成"
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                ParamUtil.set_request_params(params, {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 1,
                        "needTotal": False,
                        "conditionItems": {
                            "type": "ConditionItems",
                            "conditions": {
                                "apHeadCode": {
                                    "operator": "CONTAINS",
                                    "value": ap_head_code
                                }
                            },
                            "logicOperator": "AND"
                        }
                    }
                })
                max_wait = 60
                interval = 2
                waited = 0
                ap_status = None
                result = None
                while waited < max_wait:
                    result = self.http.post(url, json=params)
                    self.assert_util.assert_response_success(result)
                    data_list = result.get("data", {}).get("data", {}).get("data", [])
                    if data_list:
                        ap_status = data_list[0].get("apStatus")
                        if ap_status == "DONE":
                            break
                    time.sleep(interval)
                    waited += interval
                assert ap_status == "DONE", f"过账后单据状态应为DONE，实际为：{ap_status}"
                a.json(params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"apHeadCode": ap_head_code, "apStatus": ap_status}, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__]) 