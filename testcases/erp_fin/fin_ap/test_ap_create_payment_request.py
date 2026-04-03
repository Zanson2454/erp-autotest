"""
应付单创建付款申请单测试用例
"""
from datetime import datetime
from decimal import Decimal

from testcases.erp_fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


class TestApCreatePaymentRequest(ApBaseTest):
    ap_pr_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()

    def convert_data_for_json(self, obj):
        """数据转换方法，处理Decimal和datetime类型"""
        if obj is None:
            return None
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, dict):
            return {k: self.convert_data_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_data_for_json(item) for item in obj]
        else:
            return obj

    @case_decorator(
        story="应付单创建付款申请单",
        title="创建标准应付单并完成全流程",
        description="创建标准应付单，保存、提交、过账",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["ap", "full_process"]
    )
    def test_create_standard_ap_doc_full_process(self):
        try:
            with a.step("创建标准应付单并完成全流程"):
                # 使用mock_util生成测试数据
                ap_head_code = self.mock_util.generate_unique_code("APD")
                remark = self.mock_util.get_mock_remark()
                
                ap_data = self.create_ap_request_body(doc_type_id=2002001, account_type="FIN")
                request_body = ap_data["request_body"]
                base_data = ap_data["base_data"]
                
                # 更新生成的编码和备注
                request_body["apHeadCode"] = ap_head_code
                request_body["remark"] = remark
                
                fields = ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", 
                         "remark", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", 
                         "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", 
                         "payClearingStatus", "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"]
                
                # 使用标准API调用方式
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, fields, ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, request_body)
                
                # 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(filtered_params)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                ap_doc_id = ParamUtil.extract_id(result)
                self.assert_util.assert_by_operator(ap_doc_id, "not_empty", "创建应付单失败：未获取到单据ID")
                
                TestApCreatePaymentRequest.ap_pr_info = {
                    "ap_doc_id": ap_doc_id,
                    "apHeadCode": ap_head_code,
                    "settPartnerId": base_data["vend"],
                    "payOrgId": base_data["pay_org"],
                    "comOrgId": base_data["com_org"],
                    "purOrgId": base_data["pur_org"],
                    "total_amt": base_data["total_amt"],
                    "net_doc_amt": base_data["net_doc_amt"],
                    "gross_base_amt": base_data["gross_base_amt"],
                    "net_base_amt": base_data["net_base_amt"],
                    "docCurrId": base_data["currency"],
                    "baseCurrId": base_data["currency"]
                }
                
                # 应付单提交 - 使用标准API调用方式
                common_data = {
                    "apHeadCode": ap_head_code,
                    "comOrgId": base_data["com_org"],
                    "purOrgId": base_data["pur_org"],
                    "payOrgId": base_data["pay_org"],
                    "grossDocAmt": base_data["total_amt"],
                    "grossBaseAmt": base_data["gross_base_amt"],
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": base_data["total_amt"],
                    "uninvoicedDocAmt": base_data["total_amt"],
                    "unpaidBaseAmt": base_data["net_base_amt"],
                    "uninvoicedBaseAmt": base_data["total_amt"],
                    "unoffsetDocAmt": base_data["total_amt"],
                    "unoffsetBaseAmt": base_data["total_amt"],
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id,
                    "apItems": [],
                    "apSchls": [],
                    "settPartnerId": {"id": base_data["vend"]["id"]},
                    "netDocAmt": base_data["net_doc_amt"],
                    "netBaseAmt": base_data["net_base_amt"],
                    "apStatus": "CONFIRM"
                }
                
                submit_api_path = ParamUtil.get_api_path(self.apis, "AP-应付单-列表提交服务")
                submit_params, submit_url = ParamUtil.get_api_params(self.api_params, submit_api_path)
                submit_filtered_params = ParamUtil.filter_post_body_fields(
                    submit_params, list(common_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(submit_filtered_params, common_data)
                
                # 转换数据类型以支持JSON序列化
                submit_filtered_params = self.convert_data_for_json(submit_filtered_params)
                
                submit_result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=submit_filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(submit_result)
                
                submit_success = submit_result.get("success")
                self.assert_util.assert_by_operator(submit_success, "=", True, f"应付单提交API调用失败，单据编号: {ap_head_code}")
                
                # 应付单过账 - 使用标准API调用方式
                post_data = {**common_data, "apStatus": "DONE"}
                post_api_path = ParamUtil.get_api_path(self.apis, "应付单-过账-异步服务")
                post_params, post_url = ParamUtil.get_api_params(self.api_params, post_api_path)
                post_filtered_params = ParamUtil.filter_post_body_fields(
                    post_params, list(post_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(post_filtered_params, post_data)
                
                # 转换数据类型以支持JSON序列化
                post_filtered_params = self.convert_data_for_json(post_filtered_params)
                
                post_result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=post_filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(post_result)
                
                success = post_result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"应付单过账API调用失败，单据编号: {ap_head_code}")
                
                self.wait_for_ap_status(ap_head_code, "DONE", max_wait=15)
                
                a.json(filtered_params, "应付单创建请求")
                a.json(result, "应付单创建结果")
                a.json({"apHeadCode": ap_head_code, "ap_doc_id": ap_doc_id}, "应付单信息汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="基于应付单生成付款申请单",
        description="使用前置用例创建的应付单，生成付款申请单",
        severity="critical",
        order=2,
        smoke=True,
        tags=["payment_request", "create"]
    )
    def test_create_payment_request_from_ap(self):
        try:
            with a.step("基于应付单生成付款申请单"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("ap_doc_id"), "not_empty", "请先执行创建标准应付单用例")
                
                pr_create_request = {
                    "apHeadCode": info["apHeadCode"],
                    "id": info["ap_doc_id"],
                    "apStatus": "DONE",
                    "comOrgId": {"id": info["comOrgId"].get("id")},
                    "purOrgId": {"id": info["purOrgId"].get("id")},
                    "payOrgId": {"id": info["payOrgId"].get("id")},
                    "settPartnerId": {"id": info["settPartnerId"].get("id")},
                    "docCurrId": {"id": info["docCurrId"].get("id")},
                    "baseCurrId": {"id": info["baseCurrId"].get("id")},
                    "grossDocAmt": info["total_amt"],
                    "grossBaseAmt": info["gross_base_amt"],
                    "asyncExecutionStatus": "SUCCEEDED"
                }
                
                # 使用标准API调用方式
                api_path = ParamUtil.get_api_path(self.apis, "应付单转化付款申请单-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(pr_create_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pr_create_request)
                
                # 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(filtered_params)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"应付单创建付款申请单失败，应付单编号: {info['apHeadCode']}")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pr_create_success": True,
                    "pr_request_id": result.get("requestId")
                })
                
                a.json(filtered_params, "付款申请单创建请求")
                a.json(result, "付款申请单创建结果")
                a.json({"success": success, "requestId": result.get("requestId")}, "创建结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="应付单分页查询验证状态更新",
        description="查询应付单，验证异步执行状态为已成功",
        severity="critical",
        order=3,
        smoke=True,
        tags=["ap", "query", "status_check"]
    )
    def test_query_ap_doc_status_after_pr_create(self):
        try:
            with a.step("应付单分页查询验证状态更新"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("apHeadCode"), "not_empty", "请先执行前置用例")
                self.assert_util.assert_by_operator(info.get("pr_create_success"), "not_empty", "请先执行付款申请单创建用例")
                
                ap_head_code = info["apHeadCode"]
                max_attempts = 8
                interval = 2
                validation_success = False
                
                for attempt in range(max_attempts):
                    query_request = {
                        "apHeadCode": ap_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["apHeadCode", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, query_request)
                    
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    records = result.get("data", {}).get("data", {}).get("data", [])
                    ap_record = None
                    for record in records:
                        if record.get("apHeadCode") == ap_head_code:
                            ap_record = record
                            break
                    
                    if ap_record:
                        current_status = ap_record.get("asyncExecutionStatus")
                        
                        if current_status == "SUCCEEDED":
                            paying_doc_amt = ap_record.get("payingDocAmt", 0)
                            paying_base_amt = ap_record.get("payingBaseAmt", 0)
                            
                            self.assert_util.assert_by_operator(paying_doc_amt, "=", info["total_amt"], 
                                f"付款中金额不正确，期望: {info['total_amt']}，实际: {paying_doc_amt}")
                            self.assert_util.assert_by_operator(paying_base_amt, "=", info["gross_base_amt"], 
                                f"付款中本位币金额不正确，期望: {info['gross_base_amt']}，实际: {paying_base_amt}")
                            
                            a.json({
                                "apHeadCode": ap_head_code,
                                "asyncExecutionStatus": current_status,
                                "payingDocAmt": paying_doc_amt,
                                "payingBaseAmt": paying_base_amt,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED"
                            }, "状态验证结果")
                            
                            validation_success = True
                            break
                        
                        elif current_status == "FAILED":
                            failure_reason = ap_record.get("asyncExecutionFailureReason", "")
                            assert False, f"应付单异步执行失败，失败原因: {failure_reason}"
                        elif current_status in ["PROCESSING", "CREATED"] and attempt < max_attempts - 1:
                            self._async_delay(interval, reason="等待应付单异步执行状态更新")
                        else:
                            assert False, f"应付单异步执行状态异常: {current_status}"
                    elif attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待应付单记录可查询")
                
                if not validation_success:
                    current_status = ap_record.get("asyncExecutionStatus") if ap_record else "未找到记录"
                    assert False, f"轮询{max_attempts}次后，应付单异步执行状态仍未变为SUCCEEDED，最后状态: {current_status}，单据编号: {ap_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款申请单创建成功验证",
        description="通过数据库查询获取付款申请单编码，使用分页查询API验证付款申请单创建成功",
        severity="critical",
        order=4,
        smoke=True,
        tags=["payment_request", "verification"]
    )
    def test_verify_payment_request_creation(self):
        try:
            with a.step("付款申请单创建成功验证"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("ap_doc_id"), "not_empty", "请先执行前置用例")
                self.assert_util.assert_by_operator(info.get("pr_create_success"), "not_empty", "请先执行付款申请单创建用例")
                
                from erp_data_factory.compat.fin_ap_factory import FinApFactory
                
                ap_factory = FinApFactory()
                pr_info = ap_factory.query_payment_request_by_ap_id(info["ap_doc_id"])
                
                self.assert_util.assert_by_operator(pr_info, "not_empty", f"数据库中未找到应付单ID {info['ap_doc_id']} 对应的付款申请单记录")
                
                pr_head_code = pr_info.get("pr_head_code")
                self.assert_util.assert_by_operator(pr_head_code, "not_empty", "付款申请单编码为空")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "cm_pr_head_tr_id": pr_info.get("cm_pr_head_tr_id"),
                    "pr_head_code_from_db": pr_head_code,
                    "pr_status_from_db": pr_info.get("pr_status"),
                    "pr_doc_amt_from_db": pr_info.get("pr_doc_amt"),
                    "pr_base_amt_from_db": pr_info.get("pr_base_amt")
                })
                
                pr_query_request = {
                    "prHeadCode": pr_head_code,
                    "pageable": {"page": 0, "size": 5, "sort": []}
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务_PmHKWs3")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["prHeadCode", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pr_query_request)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                data_list = result.get("data", {}).get("data", {}).get("data", [])
                self.assert_util.assert_by_operator(data_list, "not_empty", f"付款申请单分页查询结果为空，付款申请单可能未创建成功：{pr_head_code}")
                
                pr_record = None
                for record in data_list:
                    if isinstance(record, dict) and record.get("prHeadCode") == pr_head_code:
                        pr_record = record
                        break
                
                self.assert_util.assert_by_operator(pr_record, "not_empty", f"在分页查询结果中未找到编码为 {pr_head_code} 的付款申请单记录")
                
                pr_doc_amt = pr_record.get("paymentRequestDocAmt", 0)
                pr_base_amt = pr_record.get("paymentRequestBaseAmt", 0)
                
                self.assert_util.assert_by_operator(pr_doc_amt, "=", info.get("total_amt", 0), 
                    f"付款申请单原币金额不一致，期望: {info.get('total_amt', 0)}，实际: {pr_doc_amt}")
                self.assert_util.assert_by_operator(pr_base_amt, "=", info.get("gross_base_amt", 0), 
                    f"付款申请单本位币金额不一致，期望: {info.get('gross_base_amt', 0)}，实际: {pr_base_amt}")
                
                verification_result = {
                    "pr_head_code": pr_head_code,
                    "pr_status": pr_record.get("prStatus"),
                    "pr_doc_amt": pr_doc_amt,
                    "pr_base_amt": pr_base_amt,
                    "cm_pr_head_tr_id": pr_info.get("cm_pr_head_tr_id"),
                    "verification_status": "SUCCESS",
                    "message": "付款申请单创建成功并通过数据库+API双重验证"
                }
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pr_verification_result": verification_result,
                    "final_verification_passed": True
                })
                
                a.json(self.convert_data_for_json(pr_info), "数据库查询的付款申请单信息")
                a.json(filtered_params, "付款申请单分页查询请求")
                a.json(pr_record, "分页查询返回的付款申请单记录")
                a.json(verification_result, "付款申请单验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款申请单过账",
        description="对创建成功的付款申请单执行过账操作",
        severity="critical",
        order=5,
        smoke=True,
        tags=["payment_request", "post"]
    )
    def test_payment_request_post(self):
        try:
            with a.step("付款申请单过账"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("final_verification_passed"), "not_empty", "请先执行付款申请单验证用例")
                self.assert_util.assert_by_operator(info.get("cm_pr_head_tr_id"), "not_empty", "未获取到付款申请单ID")
                
                pr_head_code = info.get("pr_head_code_from_db")
                self.assert_util.assert_by_operator(pr_head_code, "not_empty", "未获取到付款申请单编码")
                
                pr_post_request = {
                    "id": info["cm_pr_head_tr_id"],
                    "prHeadCode": pr_head_code,
                    "prStatus": "CONFIRM",
                    "comOrgId": {"id": info["comOrgId"].get("id")},
                    "payOrgId": {"id": info["payOrgId"].get("id")},
                    "settPartnerId": {"id": info["settPartnerId"].get("id")},
                    "docCurrId": {"id": info["docCurrId"].get("id")},
                    "baseCurrId": {"id": info["baseCurrId"].get("id")},
                    "grossDocAmt": info["total_amt"],
                    "grossBaseAmt": info["gross_base_amt"],
                    "asyncExecutionStatus": "CREATED"
                }
                
                # 使用标准API调用方式
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单-过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(pr_post_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pr_post_request)
                
                # 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(filtered_params)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"付款申请单过账失败，付款申请单编号: {pr_head_code}")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pr_post_success": True,
                    "pr_post_request_id": result.get("requestId")
                })
                
                a.json(filtered_params, "付款申请单过账请求")
                a.json(result, "付款申请单过账结果")
                a.json({"success": success, "requestId": result.get("requestId")}, "过账结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款申请单过账状态验证",
        description="查询付款申请单过账后的状态，验证pr_status更新为DONE",
        severity="critical",
        order=6,
        smoke=True,
        tags=["payment_request", "status_check"]
    )
    def test_verify_payment_request_post_status(self):
        try:
            with a.step("付款申请单过账状态验证"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pr_post_success"), "not_empty", "请先执行付款申请单过账用例")
                
                pr_head_code = info.get("pr_head_code_from_db")
                self.assert_util.assert_by_operator(pr_head_code, "not_empty", "未获取到付款申请单编码")
                
                max_attempts = 8
                interval = 2
                verification_success = False
                
                for attempt in range(max_attempts):
                    pr_query_request = {
                        "prHeadCode": pr_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务_PmHKWs3")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["prHeadCode", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, pr_query_request)
                    
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    data_list = result.get("data", {}).get("data", {}).get("data", [])
                    pr_record = None
                    for record in data_list:
                        if isinstance(record, dict) and record.get("prHeadCode") == pr_head_code:
                            pr_record = record
                            break
                    
                    if pr_record:
                        current_pr_status = pr_record.get("prStatus")
                        current_async_status = pr_record.get("asyncExecutionStatus")
                        
                        if current_pr_status == "DONE" and current_async_status == "SUCCEEDED":
                            self.assert_util.assert_by_operator(current_pr_status, "=", "DONE", 
                                f"付款申请单状态不正确，期望: DONE，实际: {current_pr_status}")
                            self.assert_util.assert_by_operator(current_async_status, "=", "SUCCEEDED", 
                                f"付款申请单异步执行状态不正确，期望: SUCCEEDED，实际: {current_async_status}")
                            
                            TestApCreatePaymentRequest.ap_pr_info.update({
                                "final_pr_status": current_pr_status,
                                "final_async_status": current_async_status,
                                "pr_post_verification_passed": True
                            })
                            
                            a.json({
                                "prHeadCode": pr_head_code,
                                "prStatus": current_pr_status,
                                "asyncExecutionStatus": current_async_status,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED"
                            }, "付款申请单过账状态验证结果")
                            
                            verification_success = True
                            break
                        
                        elif current_async_status == "FAILED":
                            failure_reason = pr_record.get("asyncExecutionFailureReason", "")
                            assert False, f"付款申请单异步执行失败，失败原因: {failure_reason}"
                        elif current_async_status in ["PROCESSING", "CREATED"] and attempt < max_attempts - 1:
                            self._async_delay(interval, reason="等待付款申请单异步执行状态更新")
                        else:
                            assert False, f"付款申请单异步执行状态异常: {current_async_status}"
                    elif attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款申请单记录可查询")
                
                if not verification_success:
                    current_pr_status = pr_record.get("prStatus") if pr_record else "未找到记录"
                    current_async_status = pr_record.get("asyncExecutionStatus") if pr_record else "未找到记录"
                    assert False, f"轮询{max_attempts}次后，付款申请单状态仍未更新完成。当前状态: pr_status={current_pr_status}, async_execution_status={current_async_status}，付款申请单编号: {pr_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款申请单创建付款单",
        description="基于已过账的付款申请单创建付款单",
        severity="critical",
        order=7,
        smoke=True,
        tags=["payment_note", "convert"]
    )
    def test_convert_payment_request_to_payment_note(self):
        try:
            with a.step("付款申请单创建付款单"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pr_post_verification_passed"), "not_empty", "请先执行付款申请单过账状态验证用例")
                self.assert_util.assert_by_operator(info.get("cm_pr_head_tr_id"), "not_empty", "未获取到付款申请单ID")
                
                pr_head_code = info.get("pr_head_code_from_db")
                self.assert_util.assert_by_operator(pr_head_code, "not_empty", "未获取到付款申请单编码")
                
                convert_request = {
                    "id": info["cm_pr_head_tr_id"],
                    "prHeadCode": pr_head_code,
                    "prStatus": "DONE",
                    "comOrgId": {"id": info["comOrgId"]["id"] if isinstance(info["comOrgId"], dict) else info["comOrgId"]},
                    "purOrgId": {"id": info["purOrgId"]["id"] if isinstance(info["purOrgId"], dict) else info["purOrgId"]},
                    "payOrgId": {"id": info["payOrgId"]["id"] if isinstance(info["payOrgId"], dict) else info["payOrgId"]},
                    "settPartnerType": "SUPPLIER",
                    "docCurrId": {"id": info["docCurrId"]["id"] if isinstance(info["docCurrId"], dict) else info["docCurrId"]},
                    "baseCurrId": {"id": info["baseCurrId"]["id"] if isinstance(info["baseCurrId"], dict) else info["baseCurrId"]},
                    "exchRate": 1.0,
                    "paymentRequestDocAmt": info["total_amt"],
                    "paymentRequestBaseAmt": info["gross_base_amt"],
                    "asyncExecutionStatus": "SUCCEEDED"
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "PN-基于付款申请单生成付款单服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id", "prHeadCode", "prStatus", "comOrgId", "purOrgId", "payOrgId", 
                            "settPartnerType", "docCurrId", "baseCurrId", "exchRate", 
                            "paymentRequestDocAmt", "paymentRequestBaseAmt", "asyncExecutionStatus"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, convert_request)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"付款申请单创建付款单失败，success: {success}")
                
                # 从API返回结果中提取付款单编码
                pn_head_code_from_api = result.get("data", {}).get("data", {}).get("pnHeadCode")
                self.assert_util.assert_by_operator(pn_head_code_from_api, "not_empty", "API返回结果中未找到付款单编码")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "convert_to_pn_success": True,
                    "convert_result": result,
                    "pn_head_code_from_api": pn_head_code_from_api
                })
                
                a.json(filtered_params, "付款申请单转付款单请求")
                a.json(result, "付款申请单转付款单结果")
                a.json({"success": success, "pnHeadCode": pn_head_code_from_api, "message": "付款申请单成功转换为付款单"}, "转换验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款单创建验证",
        description="使用付款申请单转付款单API返回的付款单编码，通过付款单分页查询API验证付款单创建成功",
        severity="critical",
        order=8,
        smoke=True,
        tags=["payment_note", "verification"]
    )
    def test_verify_payment_note_creation(self):
        try:
            with a.step("付款单创建验证"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("convert_to_pn_success"), "not_empty", "请先执行付款申请单创建付款单用例")
                
                pn_head_code = info.get("pn_head_code_from_api")
                self.assert_util.assert_by_operator(pn_head_code, "not_empty", "未获取到API返回的付款单编码")
                
                # 使用付款单分页查询API验证付款单创建成功
                pn_query_request = {
                    "pnHeadCode": pn_head_code,
                    "pageable": {"page": 0, "size": 5, "sort": []}
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务_PmHKWs2")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["pnHeadCode", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pn_query_request)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                data_list = result.get("data", {}).get("data", {}).get("data", [])
                self.assert_util.assert_by_operator(data_list, "not_empty", f"付款单分页查询结果为空，付款单可能未创建成功：{pn_head_code}")
                
                pn_record = None
                for record in data_list:
                    if isinstance(record, dict) and record.get("pnHeadCode") == pn_head_code:
                        pn_record = record
                        break
                
                self.assert_util.assert_by_operator(pn_record, "not_empty", f"在分页查询结果中未找到编码为 {pn_head_code} 的付款单记录")
                
                # 验证付款单基本信息
                pn_status = pn_record.get("pnStatus")
                pn_doc_amt = pn_record.get("arApDocAmt", 0)
                pn_base_amt = pn_record.get("arApBaseAmt", 0)
                cm_pn_head_tr_id = pn_record.get("id")
                
                self.assert_util.assert_by_operator(pn_status, "=", "DRAFT", 
                    f"付款单状态不正确，期望: DRAFT，实际: {pn_status}")
                
                expected_doc_amt = info.get("total_amt", 0)
                expected_base_amt = info.get("gross_base_amt", 0)
                
                self.assert_util.assert_by_operator(pn_doc_amt, "=", expected_doc_amt, 
                    f"付款单原币金额不一致，期望: {expected_doc_amt}，实际: {pn_doc_amt}")
                self.assert_util.assert_by_operator(pn_base_amt, "=", expected_base_amt, 
                    f"付款单本位币金额不一致，期望: {expected_base_amt}，实际: {pn_base_amt}")
                
                verification_result = {
                    "pn_head_code": pn_head_code,
                    "cm_pn_head_tr_id": cm_pn_head_tr_id,
                    "pn_status": pn_status,
                    "pn_doc_amt": pn_doc_amt,
                    "pn_base_amt": pn_base_amt,
                    "status_check": "PASSED",
                    "amount_check": "PASSED",
                    "verification_status": "SUCCESS",
                    "verification_method": "API_QUERY",
                    "message": "付款单创建成功并通过API验证"
                }
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pn_head_code_from_api": pn_head_code,
                    "cm_pn_head_tr_id_from_db": cm_pn_head_tr_id,
                    "pn_status_from_db": pn_status,
                    "pn_verification_result": verification_result,
                    "final_pn_verification_passed": True
                })
                
                a.json(filtered_params, "付款单分页查询请求")
                a.json(pn_record, "分页查询返回的付款单记录")
                a.json(verification_result, "付款单验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款单提交",
        description="对创建成功的付款单执行提交操作",
        severity="critical",
        order=9,
        smoke=True,
        tags=["payment_note", "submit"]
    )
    def test_submit_payment_note(self):
        try:
            with a.step("付款单提交"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("final_pn_verification_passed"), "not_empty", "请先执行付款单创建验证用例")
                
                pn_head_code = info.get("pn_head_code_from_api")
                cm_pn_head_tr_id = info.get("cm_pn_head_tr_id_from_db")
                self.assert_util.assert_by_operator(pn_head_code, "not_empty", "未获取到付款单编码")
                self.assert_util.assert_by_operator(cm_pn_head_tr_id, "not_empty", "未获取到付款单ID")
                
                submit_request = {
                    "id": cm_pn_head_tr_id,
                    "pnHeadCode": pn_head_code,
                    "pnStatus": "DRAFT"
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "PN-收付款-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id", "pnHeadCode", "pnStatus"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, submit_request)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"付款单提交失败，success: {success}")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pn_submit_success": True,
                    "pn_submit_result": result,
                    "pn_status_after_submit": "CONFIRM"
                })
                
                a.json(filtered_params, "付款单提交请求")
                a.json(result, "付款单提交结果")
                a.json({"success": success, "message": "付款单提交成功"}, "提交验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款申请单分页查询验证已付款金额更新",
        description="付款单提交后，查询付款申请单分页数据，验证已付款金额是否正确更新",
        severity="critical",
        order=10,
        smoke=True,
        tags=["payment_request", "amount_check", "submit_verification"]
    )
    def test_verify_payment_request_paid_amount_after_submit(self):
        try:
            with a.step("付款申请单分页查询验证已付款金额更新"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pn_submit_success"), "not_empty", "请先执行付款单提交用例")
                
                pr_head_code = info.get("pr_head_code_from_db")
                self.assert_util.assert_by_operator(pr_head_code, "not_empty", "未获取到付款申请单编码")
                
                max_attempts = 8
                interval = 2
                amount_verification_success = False
                
                for attempt in range(max_attempts):
                    pr_query_request = {
                        "prHeadCode": pr_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务_PmHKWs3")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["prHeadCode", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, pr_query_request)
                    
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    data_list = result.get("data", {}).get("data", {}).get("data", [])
                    pr_record = None
                    for record in data_list:
                        if isinstance(record, dict) and record.get("prHeadCode") == pr_head_code:
                            pr_record = record
                            break
                    
                    if pr_record:
                        # 获取关键金额字段
                        paid_doc_amt = pr_record.get("paidDocAmt", 0)
                        paid_base_amt = pr_record.get("paidBaseAmt", 0)
                        payment_request_doc_amt = pr_record.get("paymentRequestDocAmt", 0)
                        payment_request_base_amt = pr_record.get("paymentRequestBaseAmt", 0)
                        unpaid_doc_amt = pr_record.get("unpaidDocAmt", 0)
                        unpaid_base_amt = pr_record.get("unpaidBaseAmt", 0)
                        pr_status = pr_record.get("prStatus")
                        
                        expected_total_amt = info.get("total_amt", 0)
                        expected_base_amt = info.get("gross_base_amt", 0)
                        
                        # 验证已付款金额应该等于付款申请单总金额（付款单提交后应该更新）
                        if (paid_doc_amt == expected_total_amt and 
                            paid_base_amt == expected_base_amt and 
                            unpaid_doc_amt == 0 and 
                            unpaid_base_amt == 0):
                            
                            # 条件已验证金额正确，直接构建验证结果
                            paid_amount_verification = {
                                "prHeadCode": pr_head_code,
                                "prStatus": pr_status,
                                "paidDocAmt": paid_doc_amt,
                                "paidBaseAmt": paid_base_amt,
                                "unpaidDocAmt": unpaid_doc_amt,
                                "unpaidBaseAmt": unpaid_base_amt,
                                "paymentRequestDocAmt": payment_request_doc_amt,
                                "paymentRequestBaseAmt": payment_request_base_amt,
                                "expectedTotalAmt": expected_total_amt,
                                "expectedBaseAmt": expected_base_amt,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED",
                                "message": "付款申请单已付款金额验证通过，付款单提交后金额字段正确更新"
                            }
                            
                            TestApCreatePaymentRequest.ap_pr_info.update({
                                "pr_paid_amount_verification": paid_amount_verification,
                                "pr_paid_amount_verification_passed": True
                            })
                            
                            a.json(filtered_params, "付款申请单分页查询请求")
                            a.json(pr_record, "付款申请单分页查询结果")
                            a.json(paid_amount_verification, "付款申请单已付款金额验证结果")
                            
                            amount_verification_success = True
                            break
                        elif attempt < max_attempts - 1:
                            self._async_delay(interval, reason="等待付款申请单金额状态更新")
                        else:
                            # 最后一次尝试，输出详细的金额信息用于调试
                            amount_details = {
                                "current_paid_doc_amt": paid_doc_amt,
                                "current_paid_base_amt": paid_base_amt,
                                "current_unpaid_doc_amt": unpaid_doc_amt,
                                "current_unpaid_base_amt": unpaid_base_amt,
                                "current_payment_request_doc_amt": payment_request_doc_amt,
                                "current_payment_request_base_amt": payment_request_base_amt,
                                "current_pr_status": pr_status,
                                "expected_total_amt": expected_total_amt,
                                "expected_base_amt": expected_base_amt
                            }
                            a.json(amount_details, "付款申请单金额状态详情")
                            assert False, "付款申请单已付款金额状态未达到预期，详情见附件"
                    elif attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款申请单记录可查询")
                
                if not amount_verification_success:
                    assert False, f"轮询{max_attempts}次后，付款申请单已付款金额状态仍未达到预期，付款申请单编号: {pr_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款单过账",
        description="对提交成功的付款单执行过账操作",
        severity="critical",
        order=11,
        smoke=True,
        tags=["payment_note", "post"]
    )
    def test_payment_note_post(self):
        try:
            with a.step("付款单过账"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pr_paid_amount_verification_passed"), "not_empty", "请先执行付款申请单已付款金额验证用例")
                
                pn_head_code = info.get("pn_head_code_from_api")
                cm_pn_head_tr_id = info.get("cm_pn_head_tr_id_from_db")
                self.assert_util.assert_by_operator(pn_head_code, "not_empty", "未获取到付款单编码")
                self.assert_util.assert_by_operator(cm_pn_head_tr_id, "not_empty", "未获取到付款单ID")
                
                post_request = {
                    "id": cm_pn_head_tr_id,
                    "pnHeadCode": pn_head_code,
                    "pnStatus": "CONFIRM",
                    "comOrgId": {"id": info["comOrgId"]["id"] if isinstance(info["comOrgId"], dict) else info["comOrgId"]},
                    "payRecOrgId": {"id": info["payOrgId"]["id"] if isinstance(info["payOrgId"], dict) else info["payOrgId"]},
                    "baseCurrId": {"id": info["baseCurrId"]["id"] if isinstance(info["baseCurrId"], dict) else info["baseCurrId"]},
                    "currId": {"id": info["docCurrId"]["id"] if isinstance(info["docCurrId"], dict) else info["docCurrId"]},
                    "arApDocAmt": info["total_amt"],
                    "arApBaseAmt": info["gross_base_amt"],
                    "exchRate": 1.0,
                    "asyncExecutionStatus": "CREATED"
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "付款单过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id", "pnHeadCode", "pnStatus", "comOrgId", "payRecOrgId", 
                            "baseCurrId", "currId", "arApDocAmt", "arApBaseAmt", 
                            "exchRate", "asyncExecutionStatus"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, post_request)
                
                # 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(filtered_params)
                
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"付款单过账失败，success: {success}")
                
                TestApCreatePaymentRequest.ap_pr_info.update({
                    "pn_post_success": True,
                    "pn_post_result": result,
                    "pn_post_request_id": result.get("requestId")
                })
                
                a.json(filtered_params, "付款单过账请求")
                a.json(result, "付款单过账结果")
                a.json({"success": success, "requestId": result.get("requestId"), "message": "付款单过账成功"}, "过账验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="付款单过账状态验证",
        description="验证付款单过账后状态更新为DONE，并检查异步执行状态",
        severity="critical",
        order=12,
        smoke=True,
        tags=["payment_note", "status_check"]
    )
    def test_verify_payment_note_post_status(self):
        try:
            with a.step("付款单过账状态验证"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pn_post_success"), "not_empty", "请先执行付款单过账用例")
                
                pn_head_code = info.get("pn_head_code_from_api")  # 使用API返回的编码
                self.assert_util.assert_by_operator(pn_head_code, "not_empty", "未获取到付款单编码")
                
                max_attempts = 8
                interval = 2
                verification_success = False
                
                for attempt in range(max_attempts):
                    # 使用付款单分页查询API验证状态
                    pn_query_request = {
                        "pnHeadCode": pn_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务_PmHKWs2")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["pnHeadCode", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, pn_query_request)
                    
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    records = result.get("data", {}).get("data", {}).get("data", [])
                    pn_record = None
                    for record in records:
                        if record.get("pnHeadCode") == pn_head_code:
                            pn_record = record
                            break
                    
                    if pn_record:
                        current_pn_status = pn_record.get("pnStatus")
                        
                        if current_pn_status == "DONE":
                            # 状态已验证正确，直接更新结果
                            TestApCreatePaymentRequest.ap_pr_info.update({
                                "final_pn_status": current_pn_status,
                                "pn_post_verification_passed": True
                            })
                            
                            verification_result = {
                                "pn_head_code": pn_head_code,
                                "pn_status": current_pn_status,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED"
                            }
                            
                            a.json(pn_record, "付款单分页查询结果")
                            a.json(verification_result, "付款单过账状态验证结果")
                            
                            verification_success = True
                            break
                        elif current_pn_status in ["CONFIRM", "DRAFT"] and attempt < max_attempts - 1:
                            self._async_delay(interval, reason="等待付款单状态更新")
                        else:
                            assert False, f"付款单状态异常: {current_pn_status}"
                    elif attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款单记录可查询")
                
                if not verification_success:
                    current_pn_status = pn_record.get("pnStatus") if pn_record else "未找到记录"
                    assert False, f"轮询{max_attempts}次后，付款单状态仍未更新为DONE。当前状态: {current_pn_status}，付款单编号: {pn_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建付款申请单",
        title="应付单最终金额状态校验",
        description="验证付款单过账后，应付单的金额字段正确更新，包括已付金额、未付金额等",
        severity="critical",
        order=13,
        smoke=True,
        tags=["ap", "final_check", "amount_verification"]
    )
    def test_verify_ap_final_amount_status(self):
        try:
            with a.step("应付单最终金额状态校验"):
                info = TestApCreatePaymentRequest.ap_pr_info
                self.assert_util.assert_by_operator(info.get("pn_post_verification_passed"), "not_empty", "请先执行付款单过账状态验证用例")
                
                ap_head_code = info.get("apHeadCode")
                self.assert_util.assert_by_operator(ap_head_code, "not_empty", "未获取到应付单编码")
                
                max_attempts = 8
                interval = 2
                final_verification_success = False
                
                for attempt in range(max_attempts):
                    query_request = {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
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
                        },
                        "modelKey": "ERP_FIN$fin_apm_ap_head_tr"
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, query_request)
                    
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    query_data = result.get("data", {})
                    data_wrapper = query_data.get("data", {})
                    records = data_wrapper.get("data", [])
                    ap_record = None
                    for record in records:
                        if record.get("apHeadCode") == ap_head_code:
                            ap_record = record
                            break
                    
                    if ap_record:
                        paid_doc_amt = ap_record.get("paypaidDocAmt", 0)
                        paid_base_amt = ap_record.get("paypaidBaseAmt", 0)
                        unpaid_doc_amt = ap_record.get("unpaidDocAmt", 0)
                        unpaid_base_amt = ap_record.get("unpaidBaseAmt", 0)
                        paying_doc_amt = ap_record.get("payingDocAmt", 0)
                        paying_base_amt = ap_record.get("payingBaseAmt", 0)
                        
                        expected_total_amt = info.get("total_amt", 0)
                        expected_base_amt = info.get("gross_base_amt", 0)
                        
                        if (paid_doc_amt == expected_total_amt and 
                            paid_base_amt == expected_base_amt and 
                            unpaid_doc_amt == 0 and 
                            unpaid_base_amt == 0 and
                            paying_doc_amt == 0 and
                            paying_base_amt == 0):
                            
                            # 条件已验证所有金额字段正确，直接构建验证结果
                            final_amount_status = {
                                "apHeadCode": ap_head_code,
                                "paidDocAmt": paid_doc_amt,
                                "paidBaseAmt": paid_base_amt,
                                "unpaidDocAmt": unpaid_doc_amt,
                                "unpaidBaseAmt": unpaid_base_amt,
                                "payingDocAmt": paying_doc_amt,
                                "payingBaseAmt": paying_base_amt,
                                "expectedTotalAmt": expected_total_amt,
                                "expectedBaseAmt": expected_base_amt,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED",
                                "message": "应付单金额状态校验通过，所有金额字段符合预期"
                            }
                            
                            TestApCreatePaymentRequest.ap_pr_info.update({
                                "final_amount_verification": final_amount_status,
                                "all_tests_completed": True
                            })
                            
                            a.json(filtered_params, "应付单查询请求")
                            a.json(ap_record, "应付单查询结果")
                            a.json(final_amount_status, "应付单最终金额状态验证结果")
                            
                            final_verification_success = True
                            break
                        elif attempt < max_attempts - 1:
                            self._async_delay(interval, reason="等待应付单金额状态更新")
                        else:
                            amount_details = {
                                "current_paid_doc_amt": paid_doc_amt,
                                "current_paid_base_amt": paid_base_amt,
                                "current_unpaid_doc_amt": unpaid_doc_amt,
                                "current_unpaid_base_amt": unpaid_base_amt,
                                "current_paying_doc_amt": paying_doc_amt,
                                "current_paying_base_amt": paying_base_amt,
                                "expected_total_amt": expected_total_amt,
                                "expected_base_amt": expected_base_amt
                            }
                            a.json(amount_details, "金额状态详情")
                            assert False, "应付单金额状态未达到预期，详情见附件"
                    elif attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待应付单记录可查询")
                
                if not final_verification_success:
                    assert False, f"轮询{max_attempts}次后，应付单金额状态仍未达到预期，应付单编号: {ap_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApCreatePaymentRequest()
    test.setup_class()
    test.test_create_standard_ap_doc_full_process()
    test.test_create_payment_request_from_ap()
    test.test_query_ap_doc_status_after_pr_create()
    test.test_verify_payment_request_creation()
    test.test_payment_request_post()
    test.test_verify_payment_request_post_status()
    test.test_convert_payment_request_to_payment_note()
    test.test_verify_payment_note_creation()
    test.test_submit_payment_note()
    test.test_verify_payment_request_paid_amount_after_submit()
    test.test_payment_note_post()
    test.test_verify_payment_note_post_status()
    test.test_verify_ap_final_amount_status() 
