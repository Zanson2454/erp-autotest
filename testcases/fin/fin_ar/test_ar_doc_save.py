"""
应收单保存服务测试用例
覆盖创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from data_factory.fin_ar_factory import FinArFactory
from datetime import datetime
import time
from pathlib import Path
import decimal

# 工具：递归将Decimal转float
def _convert_decimal_to_float(obj):
    """递归转换Decimal类型为float"""
    if isinstance(obj, dict):
        return {k: _convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

@allure.epic("ERP通业财模块")
@allure.feature("应收管理")
class TestArDocumentSave(BaseTest):
    """应收单全流程自动化用例"""
    ar_save_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ar_factory = FinArFactory()
        # 初始化财务API配置
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params

    @ParamUtil.case_decorator(
        story="应收单保存",
        title="创建标准应收单",
        description="创建标准应收单并断言成功",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ar", "save", "draft"]
    )
    def test_create_draft_ar_doc(self):
        try:
            with a.step("创建标准应收单"):
                now = datetime.now()
                now_ts = int(now.timestamp() * 1000)
                # 主数据获取
                com_org_id = self.ar_factory.get_org_by_id(14373001)["id"]
                sls_org_id = self.ar_factory.get_org_by_id(14579001)["id"]
                pay_org_id = com_org_id
                curr_id = self.ar_factory.create_currency()["id"]
                customer_id = self.ar_factory.get_customer_by_id(14103001)["id"]
                mat_id = self.ar_factory.get_material_by_id(14672002)["id"]
                tax_code_id = self.ar_factory.get_tax_code_by_id(2002002)["id"]
                sett_item_type_id = self.ar_factory.get_sett_item_type_by_id(12)["id"]
                # 明细、计划全部由工厂生成，金额字段保持一致
                ar_items = [{
                    "matId": {"id": mat_id},
                    "taxCodeId": {"id": tax_code_id},
                    "settItemTypeId": {"id": sett_item_type_id},
                    "arQty": 100,
                    "grossDocPrice": 400,
                    "grossDocAmt": 40000,
                    "grossBaseAmt": 40000,
                    "netDocAmt": 40000,
                    "netBaseAmt": 40000,
                    "taxRate": 13,
                    "taxAmt": 4601.77
                }]
                ar_schls = [{
                    "dueDate": now_ts,
                    "arDocAmt": 40000,
                    "arBaseAmt": 40000,
                    "arPercent": 100,
                    "collectionClearingStatus": "UNCLEARED"
                }]
                doc_type_id = 14003001
                request_body = {
                    "docTypeId": {"id": doc_type_id},
                    "arDate": now_ts,
                    "comOrgId": {"id": com_org_id},
                    "slsOrgId": {"id": sls_org_id},
                    "payOrgId": {"id": pay_org_id},
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
                    "arSchls": ar_schls
                }
                api_path = ParamUtil.get_api_path(self.apis, "AR-应收单保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(request_body.keys()),
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, request_body)
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                ar_doc_id = ParamUtil.extract_id(result)
                assert ar_doc_id, "创建应收单失败：未获取到单据ID"
                TestArDocumentSave.ar_save_info.update({
                    "ar_doc_id": ar_doc_id,
                    "request_body": request_body
                })
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(_convert_decimal_to_float(TestArDocumentSave.ar_save_info), "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应收单编辑",
        title="编辑应收单",
        description="编辑应收单并保存",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ar", "edit"]
    )
    def test_edit_ar_doc(self):
        try:
            with a.step("编辑应收单"):
                ar_doc_id = TestArDocumentSave.ar_save_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行创建标准应收单用例"
                api_path = ParamUtil.get_api_path(self.apis, "AR-应收单保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                base_request = TestArDocumentSave.ar_save_info.get("request_body", {}).copy()
                base_request["id"] = ar_doc_id
                base_request["remark"] = f"应收单编辑场景自动化用例 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(base_request.keys()),
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, base_request)
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("arStatus") == "DRAFT", "单据状态不正确"
                assert data.get("remark") == base_request["remark"], "备注未正确变更"
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应收单提交",
        title="提交应收单-AR_SUBMIT_WITH_HEAD_EVENT_SERVICE",
        description="用前置用例生成的单据进行提交并断言成功",
        severity="critical",
        order=3,
        smoke=False,
        tags=["ar", "submit"]
    )
    def test_submit_ar_doc(self):
        try:
            with a.step("提交应收单"):
                ar_doc_id = TestArDocumentSave.ar_save_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_save_info.get("request_body", {}).copy()
                assert ar_doc_id and base_request, "请先执行编辑用例，确保ar_doc_id和request_body已生成"
                base_request["id"] = ar_doc_id
                base_request["arStatus"] = "CONFIRM"
                if base_request.get("arHeadCode") is None:
                    base_request["arHeadCode"] = ParamUtil.generate_unique_code("AR")
                ar_items = base_request.get("arItems", [])
                grossDocAmt = sum([item.get("grossDocAmt", 0) for item in ar_items])
                netDocAmt = sum([item.get("netDocAmt", 0) for item in ar_items])
                grossBaseAmt = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                netBaseAmt = sum([item.get("netBaseAmt", 0) for item in ar_items])
                base_request["grossDocAmt"] = grossDocAmt
                base_request["netDocAmt"] = netDocAmt
                base_request["grossBaseAmt"] = grossBaseAmt
                base_request["netBaseAmt"] = netBaseAmt
                api_path = ParamUtil.get_api_path(self.apis, "AR-应收单-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(base_request.keys()),
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, base_request)
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("arStatus") == "CONFIRM", "单据状态不正确"
                TestArDocumentSave.ar_save_info["request_body"]["arHeadCode"] = base_request["arHeadCode"]
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应收单过账",
        title="应收单过账-AR_POST_ASYNC_EVENT_SERVICE",
        description="用前置用例生成的单据进行过账并断言异步任务提交成功",
        severity="critical",
        order=4,
        smoke=False,
        tags=["ar", "post"]
    )
    def test_post_ar_doc(self):
        try:
            with a.step("应收单过账"):
                ar_doc_id = TestArDocumentSave.ar_save_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_save_info.get("request_body", {}).copy()
                assert ar_doc_id and base_request, "请先执行提交用例，确保ar_doc_id和request_body已生成"
                base_request["id"] = ar_doc_id
                base_request["arStatus"] = "CONFIRM"
                ar_items = base_request.get("arItems", [])
                base_request["grossDocAmt"] = sum([item.get("grossDocAmt", 0) for item in ar_items])
                base_request["netDocAmt"] = sum([item.get("netDocAmt", 0) for item in ar_items])
                base_request["grossBaseAmt"] = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                base_request["netBaseAmt"] = sum([item.get("netBaseAmt", 0) for item in ar_items])
                
                api_path = ParamUtil.get_api_path(self.apis, "应收单-过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(base_request.keys()),
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, base_request)
                filtered_params = _convert_decimal_to_float(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应收单状态校验",
        title="轮询分页查询应收单状态",
        description="根据arHeadCode分页查询应收单状态，轮询直至状态为DONE",
        severity="critical",
        order=5,
        smoke=False,
        tags=["ar", "check", "status", "by_code", "paging"]
    )
    def test_check_ar_doc_status_by_code_paging(self):
        try:
            with a.step("轮询分页查询应收单状态"):
                ar_head_code = None
                base_request = TestArDocumentSave.ar_save_info.get("request_body", {})
                if base_request:
                    ar_head_code = base_request.get("arHeadCode")
                assert ar_head_code, "请先执行提交用例，确保arHeadCode已生成"
                
                api_path = ParamUtil.get_api_path(self.apis, "应收单头表-分页数据服务_PmHKWs4")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                ParamUtil.set_request_params(params, {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 1,
                        "needTotal": False,
                        "conditionItems": {
                            "type": "ConditionItems",
                            "conditions": {
                                "arHeadCode": {
                                    "operator": "CONTAINS",
                                    "value": ar_head_code
                                }
                            },
                            "logicOperator": "AND"
                        }
                    }
                })
                
                max_wait = 60
                interval = 2
                waited = 0
                ar_status = None
                result = None
                while waited < max_wait:
                    result = self.http.post(url, json=params)
                    self.assert_util.assert_response_success(result)
                    data_list = result.get("data", {}).get("data", {}).get("data", [])
                    if data_list:
                        ar_status = data_list[0].get("arStatus")
                        if ar_status == "DONE":
                            break
                    time.sleep(interval)
                    waited += interval
                assert ar_status == "DONE", f"过账后单据状态应为DONE，实际为：{ar_status}"
                a.json(params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"arHeadCode": ar_head_code, "arStatus": ar_status}, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__]) 