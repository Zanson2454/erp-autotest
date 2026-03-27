"""
应付单创建采购发票测试用例
"""
import allure
from testcases.erp_fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from data_factory.fin_ap_factory import FinApFactory
from datetime import datetime
from decimal import Decimal
import time

@allure.epic("财务应付")
@allure.feature("应付单创建采购发票")
class TestApCreatePurchaseInvoice(ApBaseTest):
    ap_pi_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()

    def convert_data_for_json(self, obj):
        """数据转换方法"""
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
        story="应付单创建采购发票",
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
                
                # 使用基类方法创建应付单请求体
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
                self.assert_util.assert_not_empty(ap_doc_id, "创建应付单失败：未获取到单据ID")
                
                TestApCreatePurchaseInvoice.ap_pi_info = {
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
                
                # 应付单提交 - 完全参考现有用例的实现
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
                    "unpaidBaseAmt": base_data["gross_base_amt"],
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
                
                # 应付单过账 - 完全参考现有用例的实现
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
                
                # 等待过账完成
                self.wait_for_ap_status(ap_head_code, "DONE", max_wait=15)
                
                a.json(filtered_params, "应付单创建请求")
                a.json(result, "应付单创建结果")
                a.json({"apHeadCode": ap_head_code, "ap_doc_id": ap_doc_id}, "应付单信息汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="基于应付单生成采购发票",
        description="使用前置用例创建的应付单，生成采购发票",
        severity="critical",
        order=2,
        smoke=True,
        tags=["purchase_invoice", "create"]
    )
    def test_create_purchase_invoice_from_ap(self):
        try:
            with a.step("基于应付单生成采购发票"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                self.assert_util.assert_not_empty(info.get("ap_doc_id"), "请先执行创建标准应付单用例")
                
                # 生成采购发票编码 - 使用AUTO_时间戳格式
                import time
                timestamp = str(int(time.time() * 1000))
                pi_head_code = f"AUTO_{timestamp}"
                
                # 生成发票号 - 使用INV_时间戳格式
                invoice_no = f"INV_{timestamp}"
                
                pi_create_request = {
                    "apHeadCode": info["apHeadCode"],
                    "id": info["ap_doc_id"],
                    "apStatus": "DONE",
                    "comOrgId": info["comOrgId"],
                    "purOrgId": info["purOrgId"],
                    "payOrgId": info["payOrgId"],
                    "settPartnerId": info["settPartnerId"],
                    "docCurrId": info["docCurrId"],
                    "baseCurrId": info["baseCurrId"],
                    "grossDocAmt": info["total_amt"],
                    "grossBaseAmt": info["gross_base_amt"],
                    "netDocAmt": info["net_doc_amt"],
                    "netBaseAmt": info["net_base_amt"],
                    "piHeadCode": pi_head_code,
                    "asyncExecutionStatus": "SUCCEEDED",
                    # 修正发票相关字段
                    "inv_code": invoice_no,  # 发票号
                    "docTypeId": {"id": 2000008},  # 采购发票类型ID - 采购普通发票类型
                    "traParType": "SUPPLIER",  # 交易伙伴类型
                    "traParId": info["settPartnerId"],  # 交易伙伴ID
                    "piDate": int(time.time() * 1000),  # 采购发票日期
                    "createType": "MANUAL"  # 创建类型
                }
                
                # 使用标准API调用方式
                api_path = ParamUtil.get_api_path(self.apis, "应付单-行操作-应付单转化销售发票保存-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(pi_create_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pi_create_request)
                
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
                
                # 只断言success为true
                success = result.get("success")
                self.assert_util.assert_by_operator(success, "=", True, f"应付单创建采购发票失败，应付单编号: {info['apHeadCode']}")
                
                TestApCreatePurchaseInvoice.ap_pi_info.update({
                    "pi_create_success": True,
                    "pi_head_code": pi_head_code,
                    "pi_request_id": result.get("requestId"),
                    "invoice_no": invoice_no,  # 保存发票号
                    "pi_doc_type_id": 2000008  # 保存采购发票类型ID - 采购普通发票类型
                })
                
                a.json(filtered_params, "采购发票创建请求")
                a.json(result, "采购发票创建结果")
                a.json({"success": success, "pi_head_code": pi_head_code, "invoice_no": invoice_no, "requestId": result.get("requestId")}, "创建结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="应付单状态验证",
        description="验证应付单异步执行状态和开票中金额更新",
        severity="critical",
        order=3,
        smoke=True,
        tags=["ap", "status_check"]
    )
    def test_verify_ap_status_after_pi_create(self):
        try:
            with a.step("验证应付单状态更新"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                self.assert_util.assert_not_empty(info.get("pi_create_success"), "请先执行采购发票创建用例")
                
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
                            invoicing_doc_amt = ap_record.get("invoicingDocAmt", 0)
                            invoicing_base_amt = ap_record.get("invoicingBaseAmt", 0)
                            
                            self.assert_util.assert_by_operator(invoicing_doc_amt, "=", info["total_amt"], 
                                f"开票中金额不正确，期望: {info['total_amt']}，实际: {invoicing_doc_amt}")
                            self.assert_util.assert_by_operator(invoicing_base_amt, "=", info["gross_base_amt"], 
                                f"开票中本位币金额不正确，期望: {info['gross_base_amt']}，实际: {invoicing_base_amt}")
                            
                            a.json({
                                "apHeadCode": ap_head_code,
                                "asyncExecutionStatus": current_status,
                                "invoicingDocAmt": invoicing_doc_amt,
                                "invoicingBaseAmt": invoicing_base_amt,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED"
                            }, "状态验证结果")
                            
                            validation_success = True
                            break
                        
                        elif current_status == "FAILED":
                            failure_reason = ap_record.get("asyncExecutionFailureReason", "")
                            assert False, f"应付单异步执行失败，失败原因: {failure_reason}"
                        elif current_status in ["PROCESSING", "CREATED"] and attempt < max_attempts - 1:
                            time.sleep(interval)
                        else:
                            assert False, f"应付单异步执行状态异常: {current_status}"
                    elif attempt < max_attempts - 1:
                        time.sleep(interval)
                
                if not validation_success:
                    current_status = ap_record.get("asyncExecutionStatus") if ap_record else "未找到记录"
                    assert False, f"轮询{max_attempts}次后，应付单异步执行状态仍未变为SUCCEEDED，最后状态: {current_status}，单据编号: {ap_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="验证生成的采购发票包含正确的发票号和单据类型",
        description="验证生成的采购发票包含正确的发票号和单据类型",
        severity="critical",
        order=4,
        smoke=True,
        tags=["purchase_invoice", "validation"]
    )
    def test_verify_purchase_invoice_details(self):
        try:
            with a.step("验证采购发票信息完整性"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                self.assert_util.assert_not_empty(info.get("pi_create_success"), "请先执行采购发票创建用例")
                
                invoice_no = info.get("invoice_no")
                
                # 通过数据工厂查询采购发票信息
                factory = FinApFactory()
                pi_info = factory.query_purchase_invoice_by_inv_code(invoice_no)
                
                assert pi_info, f"数据工厂未查询到发票号 {invoice_no} 对应的采购发票信息"
                
                # 验证数据工厂查询结果
                self.assert_util.assert_by_operator(pi_info.get("inv_code"), "=", invoice_no, 
                    f"数据工厂查询：发票号不匹配，期望: {invoice_no}，实际: {pi_info.get('inv_code')}")
                
                # 获取采购发票ID和编码
                pi_id = pi_info.get("id")
                pi_head_code = pi_info.get("pi_head_code")
                
                # 使用采购发票编号进行分页查询验证
                query_request = {
                    "piHeadCode": pi_head_code,
                    "pageable": {"page": 0, "size": 10, "sort": []}
                }
                
                api_path = ParamUtil.get_api_path(self.apis, "采购发票头表-分页数据服务_PmHKWs2")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["piHeadCode", "pageable"], ["params", "request"]
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
                pi_record = None
                for record in records:
                    if record.get("piHeadCode") == pi_head_code:
                        pi_record = record
                        break
                
                assert pi_record, f"API未查询到采购发票编号 {pi_head_code} 对应的采购发票记录"
                
                # 验证API查询到的ID与数据工厂查询到的ID一致
                api_pi_id = pi_record.get("id")
                self.assert_util.assert_by_operator(api_pi_id, "=", pi_id, 
                    f"API查询的采购发票ID与数据工厂查询不一致，数据工厂: {pi_id}，API: {api_pi_id}")
                
                # 更新保存的信息
                TestApCreatePurchaseInvoice.ap_pi_info.update({
                    "db_pi_id": pi_id,
                    "db_pi_head_code": pi_head_code,
                    "api_pi_id": api_pi_id,
                    "validation_result": "PASSED"
                })
                
                a.json(pi_info, "数据工厂查询结果")
                a.json({
                    "piHeadCode": pi_head_code,
                    "invCode": invoice_no,
                    "db_pi_id": pi_id,
                    "api_pi_id": api_pi_id,
                    "id_match": pi_id == api_pi_id,
                    "validation_result": "PASSED"
                }, "验证结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="采购发票提交",
        description="提交前面创建的采购发票，验证提交成功",
        severity="critical",
        order=5,
        smoke=True,
        tags=["purchase_invoice", "submit"]
    )
    def test_submit_purchase_invoice(self):
        try:
            with a.step("提交采购发票"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                assert info.get("db_pi_id"), "请先执行采购发票验证用例"
                
                pi_id = info.get("db_pi_id")
                pi_head_code = info.get("db_pi_head_code")
                invoice_no = info.get("invoice_no")
                
                # 通过数据工厂查询当前采购发票的完整信息，包括税额
                factory = FinApFactory()
                pi_db_info = factory.query_purchase_invoice_by_inv_code(invoice_no)
                
                # 提取税额信息
                inv_doc_tax = pi_db_info.get("inv_doc_tax", 0.0) if pi_db_info else 0.0
                inv_base_tax = pi_db_info.get("inv_base_tax", 0.0) if pi_db_info else 0.0
                
                # 构建采购发票提交请求体（包含税额字段）
                submit_request = {
                    # 核心标识字段
                    "id": pi_id,
                    "piHeadCode": pi_head_code,
                    "piStatus": "DRAFT",
                    
                    # 基本金额字段
                    "invDocAmt": info.get("total_amt"),
                    "invBaseAmt": info.get("gross_base_amt"),
                    
                    # 税额字段（修复遗漏的税额数据）
                    "invDocTax": inv_doc_tax,  # 发票单据税额
                    "invBaseTax": inv_base_tax,  # 发票本位币税额
                    
                    # 钩稽金额字段（核心业务逻辑）
                    "clearingDocAmt": info.get("total_amt"),  # 清算中单据金额 = 发票金额合计
                    "clearingBaseAmt": info.get("gross_base_amt"),  # 清算中本位币金额 = 发票本位币金额合计
                    "unoffsetDocAmt": info.get("total_amt"),  # 未冲销单据金额
                    "unoffsetBaseAmt": info.get("gross_base_amt"),  # 未冲销本位币金额
                    
                    # 状态字段
                    "clearingStatus": "UNCLEARED",
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED"
                }
                
                # 使用标准API调用方式
                api_path = ParamUtil.get_api_path(self.apis, "PI-采购发票-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 过滤请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(submit_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, submit_request)
                
                # 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 发送提交请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(result)
                
                # 验证提交成功
                success = result.get("success")
                assert success, f"采购发票提交失败，采购发票编号: {pi_head_code}"
                
                # 更新保存的信息
                TestApCreatePurchaseInvoice.ap_pi_info.update({
                    "pi_submit_success": True,
                    "pi_submit_request_id": result.get("requestId"),
                    "inv_doc_tax": inv_doc_tax,  # 保存税额信息
                    "inv_base_tax": inv_base_tax
                })
                
                a.json(pi_db_info, "数据工厂查询的采购发票完整信息")
                a.json(filtered_params, "采购发票提交请求")
                a.json(result, "采购发票提交结果")
                a.json({
                    "piHeadCode": pi_head_code,
                    "invCode": invoice_no,
                    "invDocTax": inv_doc_tax,
                    "invBaseTax": inv_base_tax,
                    "success": success,
                    "requestId": result.get("requestId"),
                    "submit_result": "PASSED"
                }, "提交结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="验证采购发票提交后状态",
        description="验证采购发票提交后状态更新为已提交",
        severity="critical",
        order=6,
        smoke=True,
        tags=["purchase_invoice", "status_check"]
    )
    def test_verify_pi_status_after_submit(self):
        try:
            with a.step("验证采购发票提交后状态"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                assert info.get("pi_submit_success"), "请先执行采购发票提交用例"
                
                pi_head_code = info.get("db_pi_head_code")
                max_attempts = 8
                interval = 2
                validation_success = False
                
                for attempt in range(max_attempts):
                    # 查询采购发票状态
                    query_request = {
                        "piHeadCode": pi_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "采购发票头表-分页数据服务_PmHKWs2")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["piHeadCode", "pageable"], ["params", "request"]
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
                    pi_record = None
                    for record in records:
                        if record.get("piHeadCode") == pi_head_code:
                            pi_record = record
                            break
                    
                    if pi_record:
                        current_status = pi_record.get("piStatus")
                        async_status = pi_record.get("asyncExecutionStatus")
                        
                        # 验证状态变更
                        if current_status == "CONFIRM" or async_status == "SUCCEEDED":
                            # 更新保存的信息
                            TestApCreatePurchaseInvoice.ap_pi_info.update({
                                "final_pi_status": current_status,
                                "final_async_status": async_status
                            })
                            
                            a.json({
                                "piHeadCode": pi_head_code,
                                "piStatus": current_status,
                                "asyncExecutionStatus": async_status,
                                "polling_attempts": attempt + 1,
                                "validation_result": "PASSED"
                            }, "状态验证结果")
                            
                            validation_success = True
                            break
                        
                        elif async_status == "FAILED":
                            failure_reason = pi_record.get("asyncExecutionFailureReason", "")
                            assert False, f"采购发票异步执行失败，失败原因: {failure_reason}"
                        elif current_status in ["DRAFT"] and attempt < max_attempts - 1:
                            time.sleep(interval)
                        else:
                            # 记录当前状态继续等待
                            if attempt < max_attempts - 1:
                                time.sleep(interval)
                    elif attempt < max_attempts - 1:
                        time.sleep(interval)
                
                if not validation_success:
                    current_status = pi_record.get("piStatus") if pi_record else "未找到记录"
                    async_status = pi_record.get("asyncExecutionStatus") if pi_record else "未知"
                    assert False, f"轮询{max_attempts}次后，采购发票状态仍未变为CONFIRM，最后状态: {current_status}，异步状态: {async_status}，单据编号: {pi_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="采购发票过账校验与自动钩稽",
        description="校验过账金额是否与发票金额合计值一致，如果不一致则执行自动钩稽",
        severity="critical",
        order=7,
        smoke=True,
        tags=["purchase_invoice", "post_validation", "auto_match"]
    )
    def test_pi_post_validation_and_auto_match(self):
        try:
            with a.step("采购发票过账校验与自动钩稽"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                assert info.get("final_pi_status") == "CONFIRM", "请先执行采购发票提交用例"
                
                pi_id = info.get("db_pi_id")
                pi_head_code = info.get("db_pi_head_code")
                
                # 构建过账校验请求体（简化版本）
                validation_request = {
                    "id": pi_id,
                    "piHeadCode": pi_head_code,
                    "piStatus": "CONFIRM",
                    "invDocAmt": info.get("total_amt"),
                    "invBaseAmt": info.get("gross_base_amt"),
                    "clearingDocAmt": info.get("total_amt"),
                    "clearingBaseAmt": info.get("gross_base_amt"),
                    "unoffsetDocAmt": info.get("total_amt"),
                    "unoffsetBaseAmt": info.get("gross_base_amt")
                }
                
                # 第一步：执行过账校验
                val_api_path = ParamUtil.get_api_path(self.apis, "采购发票-过账校验金额一致服务")
                val_params, val_url = ParamUtil.get_api_params(self.api_params, val_api_path)
                val_filtered_params = ParamUtil.filter_post_body_fields(
                    val_params, list(validation_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(val_filtered_params, validation_request)
                
                # 转换数据类型以支持JSON序列化
                val_filtered_params = self.convert_data_for_json(val_filtered_params)
                
                # 发送过账校验请求
                val_result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=val_filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(val_result)
                
                # 获取校验结果
                validation_result = val_result.get("data", {}).get("data")
                result_flag = validation_result.get("result", True) if validation_result else True
                
                a.json(val_filtered_params, "过账校验请求")
                a.json(val_result, "过账校验结果")
                
                if result_flag:
                    # result = true，需要强制钩稽
                    TestApCreatePurchaseInvoice.ap_pi_info.update({
                        "post_validation_result": "FORCE_MATCH_REQUIRED",
                        "validation_message": "发票需强制钩稽，该用例中不考虑该情形"
                    })
                    
                    a.json({
                        "result": result_flag,
                        "message": "发票需强制钩稽，该用例中不考虑该情形",
                        "action": "跳过自动钩稽流程"
                    }, "校验结果处理")
                    
                else:
                    # result = false，自动执行钩稽
                    with a.step("执行采购发票自动钩稽"):
                        # 构建自动钩稽请求体（简化版本）
                        auto_match_request = {
                            "id": pi_id,
                            "piHeadCode": pi_head_code,
                            "piStatus": "CONFIRM",
                            "invDocAmt": info.get("total_amt"),
                            "invBaseAmt": info.get("gross_base_amt"),
                            "clearingDocAmt": info.get("total_amt"),
                            "clearingBaseAmt": info.get("gross_base_amt"),
                            "unoffsetDocAmt": info.get("total_amt"),
                            "unoffsetBaseAmt": info.get("gross_base_amt"),
                            "asyncExecutionStatus": "CREATED"
                        }
                        
                        # 执行自动钩稽
                        match_api_path = ParamUtil.get_api_path(self.apis, "采购发票自动钩稽-异步服务")
                        match_params, match_url = ParamUtil.get_api_params(self.api_params, match_api_path)
                        match_filtered_params = ParamUtil.filter_post_body_fields(
                            match_params, list(auto_match_request.keys()), ["params", "request"]
                        )
                        ParamUtil.set_request_params(match_filtered_params, auto_match_request)
                        
                        # 转换数据类型以支持JSON序列化
                        match_filtered_params = self.convert_data_for_json(match_filtered_params)
                        
                        # 发送自动钩稽请求
                        match_result, _ = self.standard_api_call(
                            api_key=self.apis,
                            set_dict=match_filtered_params.get("params", {}),
                            store_id_as=None,
                            use_param_util=False,
                            param_path=["params"]
                        )
                        self.assert_util.assert_response_success(match_result)
                        
                        # 验证自动钩稽成功
                        match_success = match_result.get("success")
                        assert match_success, f"采购发票自动钩稽失败，采购发票编号: {pi_head_code}"
                        
                        TestApCreatePurchaseInvoice.ap_pi_info.update({
                            "post_validation_result": "AUTO_MATCH_EXECUTED",
                            "auto_match_success": True,
                            "auto_match_request_id": match_result.get("requestId")
                        })
                        
                        a.json(match_filtered_params, "自动钩稽请求")
                        a.json(match_result, "自动钩稽结果")
                        a.json({
                            "piHeadCode": pi_head_code,
                            "validation_result": result_flag,
                            "auto_match_success": match_success,
                            "requestId": match_result.get("requestId"),
                            "process_result": "AUTO_MATCH_COMPLETED"
                        }, "钩稽流程结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="验证采购发票自动钩稽后状态",
        description="查询采购发票异步执行状态、发票状态、已钩稽金额和确认状态",
        severity="critical",
        order=8,
        smoke=True,
        tags=["purchase_invoice", "post_match_status", "final_verification"]
    )
    def test_verify_pi_status_after_auto_match(self):
        try:
            with a.step("验证采购发票自动钩稽后状态"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                post_validation_result = info.get("post_validation_result")
                
                # 如果是强制钩稽情况，跳过状态验证
                if post_validation_result == "FORCE_MATCH_REQUIRED":
                    a.json({
                        "message": "发票需强制钩稽，该用例中不考虑该情形",
                        "action": "跳过钩稽后状态验证",
                        "result": "SKIPPED"
                    }, "状态验证结果")
                    return
                
                # 验证自动钩稽已执行
                assert post_validation_result == "AUTO_MATCH_EXECUTED", "请先执行过账校验与自动钩稽用例"
                assert info.get("auto_match_success"), "自动钩稽未成功执行"
                
                pi_head_code = info.get("db_pi_head_code")
                expected_amount = info.get("total_amt")
                
                max_attempts = 10
                interval = 3
                validation_success = False
                
                for attempt in range(max_attempts):
                    # 查询采购发票状态
                    query_request = {
                        "piHeadCode": pi_head_code,
                        "pageable": {"page": 0, "size": 5, "sort": []}
                    }
                    
                    api_path = ParamUtil.get_api_path(self.apis, "采购发票头表-分页数据服务_PmHKWs2")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["piHeadCode", "pageable"], ["params", "request"]
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
                    pi_record = None
                    for record in records:
                        if record.get("piHeadCode") == pi_head_code:
                            pi_record = record
                            break
                    
                    if pi_record:
                        # 获取各项状态和金额
                        async_status = pi_record.get("asyncExecutionStatus")
                        pi_status = pi_record.get("piStatus")
                        cleared_doc_amt = pi_record.get("clearedDocAmt", 0)  # 已清算金额（已钩稽金额）
                        confirm_status = pi_record.get("confirmStatus")
                        
                        # 检查所有条件是否满足
                        conditions_met = {
                            "async_execution_status": async_status == "SUCCEEDED",
                            "pi_status": pi_status == "DONE",
                            "cleared_amount_match": cleared_doc_amt == expected_amount,  # 已钩稽金额 = 发票金额
                            "confirm_status": confirm_status == "CONFIRMED"
                        }
                        
                        a.json({
                            "attempt": attempt + 1,
                            "async_execution_status": async_status,
                            "pi_status": pi_status,
                            "cleared_doc_amt": cleared_doc_amt,  # 已钩稽金额
                            "expected_amount": expected_amount,
                            "confirm_status": confirm_status,
                            "conditions_met": conditions_met,
                            "all_conditions_satisfied": all(conditions_met.values())
                        }, f"第{attempt + 1}次状态检查")
                        
                        if all(conditions_met.values()):
                            # 所有条件都满足
                            TestApCreatePurchaseInvoice.ap_pi_info.update({
                                "final_async_status": async_status,
                                "final_pi_status": pi_status,
                                "final_cleared_amount": cleared_doc_amt,  # 已钩稽金额
                                "final_confirm_status": confirm_status,
                                "auto_match_verification": "PASSED"
                            })
                            
                            a.json({
                                "piHeadCode": pi_head_code,
                                "async_execution_status": async_status,
                                "pi_status": pi_status,
                                "cleared_doc_amt": cleared_doc_amt,  # 已钩稽金额
                                "confirm_status": confirm_status,
                                "polling_attempts": attempt + 1,
                                "verification_result": "ALL_CONDITIONS_MET",
                                "validation_summary": {
                                    "异步执行状态": f"{async_status} (✓ 已成功)",
                                    "发票状态": f"{pi_status} (✓ 完成)",
                                    "已钩稽金额": f"{cleared_doc_amt} = {expected_amount} (✓ 匹配)",
                                    "确认状态": f"{confirm_status} (✓ 已确认)"
                                }
                            }, "钩稽后状态验证成功")
                            
                            validation_success = True
                            break
                        
                        elif async_status == "FAILED":
                            failure_reason = pi_record.get("asyncExecutionFailureReason", "")
                            assert False, f"采购发票异步执行失败，失败原因: {failure_reason}"
                        elif attempt < max_attempts - 1:
                            time.sleep(interval)
                    elif attempt < max_attempts - 1:
                        time.sleep(interval)
                
                if not validation_success:
                    # 提供详细的失败信息
                    current_status = {
                        "async_execution_status": pi_record.get("asyncExecutionStatus") if pi_record else "未找到记录",
                        "pi_status": pi_record.get("piStatus") if pi_record else "未找到记录",
                        "cleared_doc_amt": pi_record.get("clearedDocAmt") if pi_record else "未找到记录",
                        "confirm_status": pi_record.get("confirmStatus") if pi_record else "未找到记录"
                    }
                    
                    expected_status = {
                        "async_execution_status": "SUCCEEDED",
                        "pi_status": "DONE", 
                        "cleared_doc_amt": expected_amount,
                        "confirm_status": "CONFIRMED"
                    }
                    
                    assert False, f"轮询{max_attempts}次后，采购发票状态未满足预期。\n" \
                                f"当前状态: {current_status}\n" \
                                f"预期状态: {expected_status}\n" \
                                f"单据编号: {pi_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单创建采购发票",
        title="验证应付单收票钩稽状态和已收票金额更新",
        description="查询应付单收票钩稽状态是否更新为已钩稽，已收票金额是否等于价税合计总额",
        severity="critical",
        order=9,
        smoke=True,
        tags=["ap", "invoice_clearing_status", "final_verification"]
    )
    def test_verify_ap_invoice_clearing_status(self):
        try:
            with a.step("验证应付单收票钩稽状态和已收票金额"):
                info = TestApCreatePurchaseInvoice.ap_pi_info
                auto_match_verification = info.get("auto_match_verification")
                
                # 如果采购发票是强制钩稽情况，跳过应付单状态验证
                if info.get("post_validation_result") == "FORCE_MATCH_REQUIRED":
                    a.json({
                        "message": "采购发票需强制钩稽，该用例中不考虑该情形",
                        "action": "跳过应付单收票钩稽状态验证",
                        "result": "SKIPPED"
                    }, "应付单状态验证结果")
                    return
                
                # 验证采购发票自动钩稽已完成
                assert auto_match_verification == "PASSED", "请先确保采购发票自动钩稽验证通过"
                
                ap_head_code = info.get("apHeadCode")
                expected_amount = info.get("total_amt")
                
                assert ap_head_code, "未找到应付单编号"
                assert expected_amount, "未找到应付单价税合计金额"
                
                # 查询应付单最新状态
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
                
                assert ap_record, f"未查询到应付单编号 {ap_head_code} 对应的应付单记录"
                
                # 获取关键状态和金额字段
                inv_clearing_status = ap_record.get("invClearingStatus")  # 收票钩稽状态
                invoiced_doc_amt = ap_record.get("invoicedDocAmt", 0)     # 已收票金额（原币）
                invoiced_base_amt = ap_record.get("invoicedBaseAmt", 0)   # 已收票金额（本位币）
                
                # 验证收票钩稽状态
                assert inv_clearing_status == "CLEARED", \
                    f"应付单收票钩稽状态应为CLEARED，实际为：{inv_clearing_status}"
                
                # 验证已收票金额（原币）等于价税合计
                assert invoiced_doc_amt == expected_amount, \
                    f"应付单已收票金额（原币）应等于价税合计 {expected_amount}，实际为：{invoiced_doc_amt}"
                
                # 验证已收票金额（本位币）等于价税合计
                expected_base_amount = info.get("gross_base_amt")
                assert invoiced_base_amt == expected_base_amount, \
                    f"应付单已收票金额（本位币）应等于价税合计 {expected_base_amount}，实际为：{invoiced_base_amt}"
                
                # 更新保存的信息
                TestApCreatePurchaseInvoice.ap_pi_info.update({
                    "final_inv_clearing_status": inv_clearing_status,
                    "final_invoiced_doc_amt": invoiced_doc_amt,
                    "final_invoiced_base_amt": invoiced_base_amt,
                    "ap_invoice_clearing_verification": "PASSED"
                })
                
                # 记录详细的验证结果
                a.json({
                    "apHeadCode": ap_head_code,
                    "invClearingStatus": inv_clearing_status,
                    "invoicedDocAmt": invoiced_doc_amt,
                    "invoicedBaseAmt": invoiced_base_amt,
                    "expectedDocAmount": expected_amount,
                    "expectedBaseAmount": expected_base_amount,
                    "verification_result": "ALL_CONDITIONS_MET",
                    "validation_summary": {
                        "收票钩稽状态": f"{inv_clearing_status} (✓ 已钩稽)",
                        "已收票金额（原币）": f"{invoiced_doc_amt} = {expected_amount} (✓ 匹配)",
                        "已收票金额（本位币）": f"{invoiced_base_amt} = {expected_base_amount} (✓ 匹配)"
                    }
                }, "应付单收票钩稽状态验证结果")
                
                a.json(ap_record, "应付单完整记录信息")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    test = TestApCreatePurchaseInvoice()
    test.setup_class()
    test.test_create_standard_ap_doc_full_process()
    test.test_create_purchase_invoice_from_ap()
    test.test_verify_ap_status_after_pi_create()
    test.test_verify_purchase_invoice_details()
    test.test_submit_purchase_invoice()
    test.test_verify_pi_status_after_submit()
    test.test_pi_post_validation_and_auto_match()
    test.test_verify_pi_status_after_auto_match()
    test.test_verify_ap_invoice_clearing_status() 
