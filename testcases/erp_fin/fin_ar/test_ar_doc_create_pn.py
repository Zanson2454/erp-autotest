import allure
from testcases.fin.fin_ar import ArBaseTest, convert_decimal_to_float
from utils.param_util import ParamUtil
from utils.mock_util import MockData
from utils.report_util import a, case_decorator
from data_factory.fin_ar_factory import FinArFactory
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import time

@allure.epic("ERP通业财模块")
@allure.feature("应收管理")
class TestArDocCreatePn(ArBaseTest):
    """基于应收单创建收款单测试类"""
    
    # 类变量存储测试数据
    ar_info = {}
    mock_data = MockData()

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()

    @case_decorator(
        story="应收单创建",
        title="创建并过账标准应收单",
        description="创建标准应收单并过账",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ar", "save", "post"]
    )
    def test_01_create_and_post_ar_doc(self):
        """创建并过账标准应收单"""
        try:
            with a.step("创建标准应收单"):
                now_ts = int(datetime.now().timestamp() * 1000)
                request_body = {}
                self.create_ar_request_body(now_ts, request_body)
                
                result = {}
                self.send_api_request("AR-应收单保存服务", request_body, result)
                ar_doc_id = ParamUtil.extract_id(result)
                assert ar_doc_id, "创建应收单失败：未获取到单据ID"
                
                TestArDocCreatePn.ar_info.update({
                    "ar_doc_id": ar_doc_id,
                    "request_body": request_body
                })
                
                a.json(convert_decimal_to_float(TestArDocCreatePn.ar_info), "断言结果")

            with a.step("提交应收单"):
                base_request = request_body.copy()
                base_request.update({
                    "id": ar_doc_id,
                    "arStatus": "CONFIRM",
                    "arHeadCode": self.mock_data.generate_unique_code("AR")
                })
                
                submit_result = {}
                self.send_api_request("AR-应收单-列表提交服务", base_request, submit_result)
                
                TestArDocCreatePn.ar_info["ar_head_code"] = base_request["arHeadCode"]

            with a.step("过账应收单"):
                post_result = {}
                self.send_api_request("应收单-过账-异步服务", base_request, post_result)

            with a.step("等待过账完成"):
                status_result = {}
                self.wait_for_ar_status(base_request["arHeadCode"], "DONE", status_result)
                assert status_result.get("success") and status_result.get("status") == "DONE", \
                    f"过账后单据状态应为DONE，实际为：{status_result.get('status')}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单创建（异步任务）",
        title="基于应收单创建收款单",
        description="基于应收单创建收款单",
        severity="critical",
        order=2,
        smoke=True,
        tags=["ar", "pn", "create"]
    )
    def test_02_create_pn_by_ar(self):
        """基于应收单创建收款单"""
        try:
            with a.step("基于应收单创建收款单"):
                ar_doc_id = TestArDocCreatePn.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行创建应收单用例，确保ar_doc_id已生成"
                
                pn_request = {
                    "params": {
                        "request": {
                            "id": ar_doc_id,
                            "docTypeId": {"id": 20000011}
                        }
                    }
                }
                
                api_path = "/api/trantor/service/engine/execute/ERP_FIN$PN_CREATE_BY_AR_ASYNC_EVENT_SERVICE"
                result = self.http.post(api_path, json=pn_request)
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {})
                assert response_data, "创建收款单失败：未获取到响应数据"
                
                TestArDocCreatePn.ar_info.update({
                    "pn_result": response_data
                })
                
                a.json(pn_request, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestArDocCreatePn.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单付款中金额更新查询",
        title="查询应收单收款中金额",
        description="查询应收单收款中金额并校验与含税总额一致",
        severity="critical",
        order=3,
        smoke=True,
        tags=["ar", "pn", "query"]
    )
    def test_03_check_ar_collecting_amt(self):
        """查询应收单收款中金额并校验"""
        try:
            with a.step("查询应收单收款中金额"):
                ar_doc_id = TestArDocCreatePn.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行应收单创建用例，确保ar_doc_id已生成"
                
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
                
                waited = 0
                while waited < 10:
                    result = self.http.post(url, json=query_params)
                    self.assert_util.assert_response_success(result)
                    
                    ar_data = result.get("data", {}).get("data", {})
                    if ar_data:
                        async_status = ar_data.get("asyncExecutionStatus")
                        collecting_base_amt = ar_data.get("collectingBaseAmt", 0)
                        
                        if async_status == "DONE" and collecting_base_amt > 0:
                            break
                        elif async_status == "FAILED":
                            failure_reason = ar_data.get("asyncExecutionFailureReason", "未知原因")
                            raise AssertionError(f"异步任务执行失败：{failure_reason}")
                    
                    time.sleep(2)
                    waited += 2

                assert ar_data, "未查询到应收单数据"
                
                collecting_base_amt = ar_data.get("collectingBaseAmt", 0)
                gross_doc_amt = ar_data.get("grossDocAmt", 0)
                assert collecting_base_amt == gross_doc_amt, f"应收单头上的收款中金额应等于价税合计总额，收款中金额：{collecting_base_amt}，价税合计总额：{gross_doc_amt}"
                
                ar_schls = ar_data.get("arSchls", [])
                assert ar_schls, "未找到应收计划行数据"
                
                for i, schl in enumerate(ar_schls):
                    receiving_doc_amt = schl.get("receivingDocAmt", 0)
                    ar_doc_amt = schl.get("arDocAmt", 0)
                    assert receiving_doc_amt == ar_doc_amt, f"应收单计划行收款中金额应等于价税合计总额，收款中金额：{receiving_doc_amt}，价税合计总额：{ar_doc_amt}"
                
                a.json({
                    "arDocId": ar_doc_id,
                    "collectingBaseAmt": collecting_base_amt,
                    "grossDocAmt": gross_doc_amt,
                    "asyncExecutionStatus": async_status,
                    "arSchlsCheck": [
                        {
                            "index": i+1,
                            "receivingDocAmt": schl.get("receivingDocAmt", 0),
                            "arDocAmt": schl.get("arDocAmt", 0)
                        } for i, schl in enumerate(ar_schls)
                    ]
                }, "断言结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单状态验证",
        title="验证收款单创建状态",
        description="通过数据工厂查询收款单信息并验证状态为DRAFT",
        severity="critical",
        order=4,
        smoke=True,
        tags=["ar", "pn", "verify"]
    )
    def test_04_verify_pn_status(self):
        try:
            with a.step("查询收款单信息并验证状态"):
                ar_doc_id = TestArDocCreatePn.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行应收单创建用例，确保ar_doc_id已生成"
                
                pn_info = self.ar_factory.get_pn_info_by_ar_id(ar_doc_id)
                assert pn_info, f"未找到应收单ID为{ar_doc_id}对应的收款单信息"
                
                pn_head_id = pn_info["pn_head_id"]
                expected_pn_head_code = pn_info["pn_head_code"]
                
                api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务_PmHKWs3")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                ParamUtil.set_request_params(params, {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 1,
                        "needTotal": False,
                        "conditionItems": {
                            "type": "ConditionItems",
                            "conditions": {
                                "pnHeadCode": {
                                    "operator": "CONTAINS",
                                    "value": expected_pn_head_code
                                }
                            },
                            "logicOperator": "AND"
                        }
                    }
                })
                
                result = self.http.post(url, json=params)
                self.assert_util.assert_response_success(result)
                
                data_list = result.get("data", {}).get("data", {}).get("data", [])
                assert data_list, f"未查询到收款单编码为{expected_pn_head_code}的数据"
                
                pn_data = data_list[0]
                actual_pn_head_id = pn_data.get("id")
                actual_pn_head_code = pn_data.get("pnHeadCode")
                pn_status = pn_data.get("pnStatus")
                
                assert actual_pn_head_id == pn_head_id, f"收款单ID不匹配，期望：{pn_head_id}，实际：{actual_pn_head_id}"
                assert actual_pn_head_code == expected_pn_head_code, f"收款单编码不匹配，期望：{expected_pn_head_code}，实际：{actual_pn_head_code}"
                assert pn_status == "DRAFT", f"收款单状态应为DRAFT，实际为：{pn_status}"
                
                TestArDocCreatePn.ar_info.update({
                    "pn_head_id": pn_head_id,
                    "pn_head_code": expected_pn_head_code,
                    "pn_status": pn_status
                })
                
                a.json({
                    "arDocId": ar_doc_id,
                    "pnHeadId": pn_head_id,
                    "expectedPnHeadCode": expected_pn_head_code,
                    "actualPnHeadCode": actual_pn_head_code,
                    "actualPnHeadId": actual_pn_head_id,
                    "pnStatus": pn_status,
                    "验证结果": "收款单ID、编码和状态验证通过"
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单提交",
        title="提交收款单",
        description="使用PN_SUBMIT_WITH_HEAD_EVENT_SERVICE提交收款单",
        severity="critical",
        order=5,
        smoke=True,
        tags=["ar", "pn", "submit"]
    )
    def test_05_submit_pn(self):
        try:
            with a.step("提交收款单"):
                pn_head_id = TestArDocCreatePn.ar_info.get("pn_head_id")
                pn_head_code = TestArDocCreatePn.ar_info.get("pn_head_code")
                assert pn_head_id and pn_head_code, "请先执行收款单状态验证用例，确保pn_head_id和pn_head_code已获取"
                
                submit_data = {
                    "id": pn_head_id,
                    "pnHeadCode": pn_head_code,
                    "pnStatus": "DRAFT"
                }
                
                result = {}
                self.send_api_request("PN-收付款-列表提交服务", submit_data, result)
                response_data = result.get("data", {})
                assert response_data, "提交收款单失败：未获取到响应数据"
                
                TestArDocCreatePn.ar_info.update({
                    "pn_status": "CONFIRM",
                    "submit_result": response_data
                })
                
                a.json({
                    "pnHeadId": pn_head_id,
                    "pnHeadCode": pn_head_code,
                    "submitResult": response_data,
                    "验证结果": "收款单提交成功"
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单过账",
        title="收款单过账异步任务",
        description="使用PCC_PN_REC_POST_ASYNC_EVENT_SERVICE过账收款单",
        severity="critical",
        order=6,
        smoke=True,
        tags=["ar", "pn", "post"]
    )
    def test_06_post_pn(self):
        try:
            with a.step("过账收款单"):
                pn_head_id = TestArDocCreatePn.ar_info.get("pn_head_id")
                pn_head_code = TestArDocCreatePn.ar_info.get("pn_head_code")
                assert pn_head_id and pn_head_code, "请先执行收款单提交用例，确保pn_head_id和pn_head_code已获取"
                
                post_data = {
                    "id": pn_head_id,
                    "pnHeadCode": pn_head_code,
                    "pnStatus": "CONFIRM"
                }
                
                result = {}
                self.send_api_request("收款单过账-异步服务", post_data, result)
                response_data = result.get("data", {})
                assert response_data, "过账收款单失败：未获取到响应数据"
                
                TestArDocCreatePn.ar_info.update({
                    "pn_status": "DONE",
                    "post_result": response_data
                })
                
                a.json({
                    "pnHeadId": pn_head_id,
                    "pnHeadCode": pn_head_code,
                    "postResult": response_data,
                    "验证结果": "收款单过账成功"
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单过账状态验证",
        title="验证收款单过账后状态",
        description="通过分页查询验证收款单过账后的异步执行状态和金额钩稽状态",
        severity="critical",
        order=7,
        smoke=True,
        tags=["ar", "pn", "verify", "post"]
    )
    def test_07_verify_pn_post_status(self):
        try:
            with a.step("查询收款单过账后状态"):
                pn_head_code = TestArDocCreatePn.ar_info.get("pn_head_code")
                assert pn_head_code, "请先执行收款单过账用例，确保pn_head_code已获取"
                
                api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务_PmHKWs3")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                ParamUtil.set_request_params(params, {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 1,
                        "needTotal": False,
                        "conditionItems": {
                            "type": "ConditionItems",
                            "conditions": {
                                "pnHeadCode": {
                                    "operator": "CONTAINS",
                                    "value": pn_head_code
                                }
                            },
                            "logicOperator": "AND"
                        }
                    }
                })
                
                waited = 0
                pn_data = None
                
                while waited < 15:
                    result = self.http.post(url, json=params)
                    self.assert_util.assert_response_success(result)
                    
                    data_list = result.get("data", {}).get("data", {}).get("data", [])
                    if data_list:
                        pn_data = data_list[0]
                        async_execution_status = pn_data.get("asyncExecutionStatus")
                        
                        if async_execution_status in ["SUCCEEDED", "FAILED"]:
                            break
                    
                    time.sleep(3)
                    waited += 3

                assert pn_data, f"未查询到收款单编码为{pn_head_code}的数据"
                
                async_execution_status = pn_data.get("asyncExecutionStatus")
                cleared_doc_amt = pn_data.get("clearedDocAmt", 0)
                ar_ap_doc_amt = pn_data.get("arApDocAmt", 0)
                clearing_status = pn_data.get("clearingStatus")
                pn_status = pn_data.get("pnStatus")
                async_failure_reason = pn_data.get("asyncExecutionFailureReason")
                
                assert async_execution_status == "SUCCEEDED", f"异步执行状态应为SUCCEEDED，实际为：{async_execution_status}，失败原因：{async_failure_reason or '无'}"
                assert cleared_doc_amt == ar_ap_doc_amt, f"已钩稽金额应等于应收应付金额，已钩稽金额：{cleared_doc_amt}，应收应付金额：{ar_ap_doc_amt}"
                assert clearing_status == "CLEARED", f"钩稽状态应为CLEARED，实际为：{clearing_status}"
                assert pn_status == "DONE", f"单据状态应为DONE，实际为：{pn_status}"
                
                verification_result = {
                    "pnHeadCode": pn_head_code,
                    "asyncExecutionStatus": async_execution_status,
                    "clearedDocAmt": cleared_doc_amt,
                    "arApDocAmt": ar_ap_doc_amt,
                    "clearingStatus": clearing_status,
                    "pnStatus": pn_status,
                    "验证结果": "收款单过账成功，所有状态验证通过"
                }
                
                if async_failure_reason:
                    verification_result["asyncExecutionFailureReason"] = async_failure_reason
                
                TestArDocCreatePn.ar_info.update({
                    "final_pn_data": pn_data,
                    "verification_result": verification_result
                })
                
                a.json(verification_result, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单状态验证",
        title="验证收款单过账后应收单状态更新",
        description="通过应收单头表分页查询验证收款单过账后应收单的收款金额和钩稽状态是否正确更新",
        severity="critical",
        order=8,
        smoke=True,
        tags=["ar", "pn", "verify", "post", "clearing"]
    )
    def test_08_verify_ar_after_pn_post(self):
        try:
            with a.step("查询收款单过账后应收单更新状态"):
                ar_doc_id = TestArDocCreatePn.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行应收单创建用例，确保ar_doc_id已生成"
                
                ar_data = {}
                self.query_ar_detail(ar_doc_id, ar_data)
                assert ar_data, f"未查询到应收单ID为{ar_doc_id}的数据"
                
                collected_doc_amt = ar_data.get("collectedDocAmt", 0)
                gross_doc_amt = ar_data.get("grossDocAmt", 0)
                collection_clearing_status = ar_data.get("collectionClearingStatus")
                ar_schls = ar_data.get("arSchls", [])
                
                head_verification = {
                    "collectedDocAmt": collected_doc_amt,
                    "grossDocAmt": gross_doc_amt,
                    "collectionClearingStatus": collection_clearing_status,
                    "头表验证结果": "通过" if collected_doc_amt == gross_doc_amt and collection_clearing_status == "CLEARED" else "失败"
                }
                
                schl_verification_results = []
                if ar_schls:
                    for i, schl in enumerate(ar_schls):
                        received_doc_amt = schl.get("receivedDocAmt", 0)
                        ar_doc_amt = schl.get("arDocAmt", 0)
                        clearing_status = schl.get("clearingStatus")
                        
                        schl_result = {
                            "receivedDocAmt": received_doc_amt,
                            "arDocAmt": ar_doc_amt,
                            "clearingStatus": clearing_status,
                            "验证结果": "通过" if received_doc_amt == ar_doc_amt and clearing_status == "CLEARED" else "失败"
                        }
                        schl_verification_results.append(schl_result)
                else:
                    schl_verification_results.append({"说明": "未找到应收计划行数据，可能由于收款单过账异常导致"})
                
                verification_result = {
                    "arDocId": ar_doc_id,
                    "应收单头表验证": head_verification,
                    "应收计划行验证": schl_verification_results
                }
                
                if collected_doc_amt == gross_doc_amt and collection_clearing_status == "CLEARED":
                    if ar_schls:
                        all_schls_passed = all(
                            schl.get("receivedDocAmt", 0) == schl.get("arDocAmt", 0) and 
                            schl.get("clearingStatus") == "CLEARED" 
                            for schl in ar_schls
                        )
                        if all_schls_passed:
                            verification_result["总体验证结果"] = "收款单过账后应收单状态更新正确，所有断言通过"
                        else:
                            verification_result["总体验证结果"] = "应收单头表状态正确，但计划行状态异常，请检查收款单过账是否异常"
                            raise AssertionError("应收计划行状态验证失败，请检查收款单过账是否异常")
                    else:
                        verification_result["总体验证结果"] = "应收单头表状态正确，但未找到计划行数据"
                else:
                    verification_result["总体验证结果"] = "应收单头表状态异常，请检查收款单过账是否异常"
                    error_details = []
                    if collected_doc_amt != gross_doc_amt:
                        error_details.append(f"已收款金额({collected_doc_amt})不等于价税合计总额({gross_doc_amt})")
                    if collection_clearing_status != "CLEARED":
                        error_details.append(f"收款钩稽状态({collection_clearing_status})不等于CLEARED")
                    raise AssertionError(f"应收单头表状态验证失败：{'; '.join(error_details)}，请检查收款单过账是否异常")
                
                TestArDocCreatePn.ar_info.update({
                    "ar_after_pn_post_data": ar_data,
                    "ar_verification_result": verification_result
                })
                
                a.json(verification_result, "断言结果")
                
        except Exception as e:
            error_msg = f"收款单过账后应收单更新状态验证失败：{str(e)}，请检查收款单过账是否异常"
            a.text(error_msg, "失败原因")
            raise AssertionError(error_msg)

if __name__ == "__main__":
    test = TestArDocCreatePn()
    test.setup_class()
    test.test_01_create_and_post_ar_doc()
    test.test_02_create_pn_by_ar()
    test.test_03_check_ar_collecting_amt()
    test.test_04_verify_pn_status()
    test.test_05_submit_pn()
    test.test_06_post_pn()
    test.test_07_verify_pn_post_status()
    test.test_08_verify_ar_after_pn_post() 