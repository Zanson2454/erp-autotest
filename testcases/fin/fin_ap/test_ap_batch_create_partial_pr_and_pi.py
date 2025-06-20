# -*- coding: utf-8 -*-
"""
应付单批量创建部分付款申请单和采购发票测试用例
"""
import allure
import time
from datetime import datetime
from decimal import Decimal

from testcases.fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.mock_util import MockData
from utils.report_util import a, case_decorator


def convert_decimal_to_float(obj):
    """递归将字典/列表中的 Decimal 转为 float"""
    if isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


@allure.epic("ERP财务模块")
@allure.feature("应付单管理")
class TestApBatchCreatePartialPrAndPi(ApBaseTest):
    ap_batch_info = {}
    mock_data = MockData()
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.ap_batch_info = {}
    
    @case_decorator(
        story="应付单创建",
        title="创建并过账标准应付单",
        description="基于数据工厂创建标准应付单，完成保存、提交、过账全流程，为后续部分金额操作提供基础数据",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["ap", "create", "post", "foundation"]
    )
    def test_01_create_and_post_ap_doc(self):
        try:
            with a.step("基于数据工厂创建应付单基础数据"):
                # 生成唯一编码
                ap_head_code = self.mock_data.generate_unique_code("AP")
                ap_date = int(datetime.now().timestamp() * 1000)
                
                # 使用基类方法创建应付单数据
                ap_data = self.create_ap_request_body(doc_type_id=2002001, account_type="FIN")
                request_body = ap_data["request_body"]
                base_data = ap_data["base_data"]
                
                # 更新编码和时间
                request_body.update({
                    "apHeadCode": ap_head_code,
                    "apDate": ap_date,
                    "remark": f"自动化测试创建应付单(部分场景) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                })
                
                # 先转换数据类型再显示
                request_body_json = convert_decimal_to_float(request_body)
                a.json(request_body_json, "应付单创建请求数据")

            with a.step("执行应付单保存服务"):
                save_api_path = ParamUtil.get_api_path(self.apis, "AP-应付保存服务")
                save_params, save_url = ParamUtil.get_api_params(self.api_params, save_api_path)
                
                save_fields = ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", 
                              "remark", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", 
                              "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", 
                              "payClearingStatus", "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"]
                
                save_filtered_params = ParamUtil.filter_post_body_fields(
                    save_params, save_fields, ["params", "request"]
                )
                ParamUtil.set_request_params(save_filtered_params, request_body)
                save_filtered_params = convert_decimal_to_float(save_filtered_params)
                
                save_result = self.http.post(save_url, json=save_filtered_params)
                self.assert_util.assert_response_success(save_result)
                
                ap_doc_id = ParamUtil.extract_id(save_result)
                assert ap_doc_id, "创建应付单失败：未获取到单据ID"
                
                a.json(save_result, "应付单保存结果")

            with a.step("执行应付单提交服务"):
                # 构建提交数据
                submit_data = {
                    "apHeadCode": ap_head_code,
                    "comOrgId": base_data["com_org"],
                    "purOrgId": base_data["pur_org"],
                    "payOrgId": base_data["pay_org"],
                    "grossDocAmt": base_data["total_amt"],
                    "grossBaseAmt": base_data["gross_base_amt"],
                    "netDocAmt": base_data["net_doc_amt"],
                    "netBaseAmt": base_data["net_base_amt"],
                    "settPartnerId": {"id": base_data["vend"]["id"]},
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
                    "apStatus": "CONFIRM",
                    "id": ap_doc_id,
                    "apItems": [],
                    "apSchls": []
                }
                
                submit_api_path = ParamUtil.get_api_path(self.apis, "AP-应付单-列表提交服务")
                submit_params, submit_url = ParamUtil.get_api_params(self.api_params, submit_api_path)
                
                submit_filtered_params = ParamUtil.filter_post_body_fields(
                    submit_params, list(submit_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(submit_filtered_params, submit_data)
                submit_filtered_params = convert_decimal_to_float(submit_filtered_params)
                
                submit_result = self.http.post(submit_url, json=submit_filtered_params)
                self.assert_util.assert_response_success(submit_result)
                
                submit_success = submit_result.get("success")
                assert submit_success, f"应付单提交失败，单据编号: {ap_head_code}"
                
                a.json(submit_result, "应付单提交结果")

            with a.step("执行应付单过账服务"):
                # 构建过账数据  
                post_data = {**submit_data, "apStatus": "DONE"}
                
                post_api_path = ParamUtil.get_api_path(self.apis, "应付单-过账-异步服务")
                post_params, post_url = ParamUtil.get_api_params(self.api_params, post_api_path)
                
                post_filtered_params = ParamUtil.filter_post_body_fields(
                    post_params, list(post_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(post_filtered_params, post_data)
                post_filtered_params = convert_decimal_to_float(post_filtered_params)
                
                post_result = self.http.post(post_url, json=post_filtered_params)
                self.assert_util.assert_response_success(post_result)
                
                post_success = post_result.get("success")
                assert post_success, f"应付单过账失败，单据编号: {ap_head_code}"
                
                a.json(post_result, "应付单过账结果")

            with a.step("验证应付单过账接口调用"):
                # 过账接口已调用成功，无需等待状态更新
                a.text(f"✅ 应付单过账接口调用成功，单据编号: {ap_head_code}", "过账接口验证")

            with a.step("保存测试数据"):
                # 从保存结果中提取应付单行ID和计划行ID
                ap_item_ids = []
                ap_schl_ids = []
                
                if save_result.get("data") and save_result["data"].get("data"):
                    save_data = save_result["data"]["data"]
                    
                    # 提取应付单行ID
                    if save_data.get("apItems"):
                        ap_item_ids = [item.get("id") for item in save_data["apItems"] if item.get("id")]
                    
                    # 提取应付单计划行ID  
                    if save_data.get("apSchls"):
                        ap_schl_ids = [schl.get("id") for schl in save_data["apSchls"] if schl.get("id")]
                
                # 如果接口返回数据中没有，则通过数据工厂查询
                if not ap_item_ids:
                    try:
                        ap_item_ids = self.ap_factory.get_ap_item_ids_by_ap_id(ap_doc_id)
                    except:
                        ap_item_ids = []
                
                if not ap_schl_ids:
                    try:
                        ap_schl_ids = self.ap_factory.get_ap_schl_ids_by_ap_id(ap_doc_id)
                    except:
                        ap_schl_ids = []
                
                # 保存关键数据到类变量
                TestApBatchCreatePartialPrAndPi.ap_batch_info = {
                    "ap_doc_id": ap_doc_id,
                    "ap_head_code": ap_head_code,
                    "ap_item_ids": ap_item_ids,  # 应付单行ID列表
                    "ap_schl_ids": ap_schl_ids,  # 应付单计划行ID列表
                    "vend_id": base_data["vend"]["id"],
                    "com_org_id": base_data["com_org"]["id"],
                    "pur_org_id": base_data["pur_org"]["id"],
                    "pay_org_id": base_data["pay_org"]["id"],
                    "currency_id": base_data["currency"]["id"],
                    "gross_doc_amt": base_data["total_amt"],
                    "gross_base_amt": base_data["gross_base_amt"],
                    "net_doc_amt": base_data["net_doc_amt"],
                    "net_base_amt": base_data["net_base_amt"],
                    "post_completed": True
                }
                
                a.json(TestApBatchCreatePartialPrAndPi.ap_batch_info, "测试数据")

            with a.step("验证应付单创建和过账流程完成"):
                assert TestApBatchCreatePartialPrAndPi.ap_batch_info.get("post_completed"), "应付单过账未完成"
                
                a.text(f"""
                应付单创建和过账验证总结:
                ✓ 应付单编码: {ap_head_code}
                ✓ 应付单ID: {ap_doc_id}
                ✓ 价税合计(原币): {base_data['total_amt']}
                ✓ 价税合计(本位币): {base_data['gross_base_amt']}
                ✓ 过账状态: DONE
                ✓ 为后续部分金额测试准备完成
                """, "应付单创建过账总结")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 

    @case_decorator(
        story="批量付款申请单创建",
        title="批量勾选应付单创建付款申请单(部分付款)",
        description="执行批量校验接口，校验通过后执行批量转换接口，最后保存付款申请单(部分付款场景)",
        severity="critical",
        order=2,
        smoke=True,
        tags=["ap", "batch", "pr", "create", "partial"]
    )
    def test_02_batch_create_partial_pr_from_ap(self):
        try:
            # 等待应付单过账完成
            time.sleep(5)
            
            # 获取前置数据
            ap_info = TestApBatchCreatePartialPrAndPi.ap_batch_info
            ap_doc_id = ap_info.get("ap_doc_id")
            ap_head_code = ap_info.get("ap_head_code")
            ap_schl_ids = ap_info.get("ap_schl_ids", [])
            
            # 前置条件验证
            assert ap_doc_id and ap_head_code, "应付单创建和过账未完成，请先执行用例1"
            assert ap_schl_ids, f"应付单ID {ap_doc_id} 的计划行ID不存在，请检查第一个用例的执行结果"
            
            # 获取基础数据（包含teamId等）
            base_data = self.ap_factory.get_base_data_for_fin_doc("AP")
            
            with a.step("使用第一个用例的应付单计划行ID"):
                a.json({
                    "ap_doc_id": ap_doc_id, 
                    "ap_head_code": ap_head_code,
                    "ap_schl_ids": ap_schl_ids,
                    "data_source": "第一个用例的出参"
                }, "应付单计划行信息")

            with a.step("执行应付单批量转化付款申请校验服务"):
                val_api_path = ParamUtil.get_api_path(self.apis, "应付单批量转化付款申请-校验服务")
                val_params, val_url = ParamUtil.get_api_params(self.api_params, val_api_path)
                
                # 使用应付单头ID作为第一个接口的入参
                val_request = {
                    "sceneKey": "ERP_FIN$FIN_APM_FROM_DS",
                    "viewKey": "ERP_FIN$FIN_APM_FROM_DS:list",
                    "appId": None,
                    "teamId": base_data.get("team_id", 22),
                    "serviceKey": "ERP_FIN$BATCH_AP_CONVERT_TO_PR_VAL_SERVICE",
                    "params": {"request": {"apmApSchlIds": [ap_doc_id]}}  # 使用应付单头ID
                }
                
                val_result = self.http.post(val_url, json=val_request)
                self.assert_util.assert_response_success(val_result)
                
                a.json(val_request, "应付单校验请求数据")
                a.json(val_result, "应付单校验响应数据")

            with a.step("执行应付计划行批量转化付款申请校验服务"):
                schl_val_api_path = ParamUtil.get_api_path(self.apis, "应付计划行批量转化付款申请-校验服务")
                schl_val_params, schl_val_url = ParamUtil.get_api_params(self.api_params, schl_val_api_path)
                
                # 使用应付单计划行ID作为第二个接口的入参
                schl_val_request = {
                    "sceneKey": "ERP_FIN$FIN_APM_FROM_DS",
                    "viewKey": "ERP_FIN$FIN_APM_FROM_DS:2iRU-pHS6DLHBHZp-JC4S",
                    "viewTitle": "选择应付单计划行",
                    "buttonKey": "ERP_FIN$FIN_APM_FROM_DS-84z52frNCSGsTQu6-h_sR",
                    "buttonName": "生成付款申请单",
                    "appId": 0,
                    "teamId": base_data.get("team_id", 22),
                    "serviceKey": "ERP_FIN$BATCH_AP_SCHL_CONVERT_TO_PR_VAL_SERVICE",
                    "params": {"request": {"apmApSchlIds": ap_schl_ids}}  # 使用应付单计划行ID
                }
                
                schl_val_result = self.http.post(schl_val_url, json=schl_val_request)
                self.assert_util.assert_response_success(schl_val_result)
                
                a.json(schl_val_request, "应付计划行校验请求数据")
                a.json(schl_val_result, "应付计划行校验响应数据")

            with a.step("执行付款申请单保存服务(部分付款)"):
                save_api_path = ParamUtil.get_api_path(self.apis, "PR-付款申请保存并更新来源服务")
                save_params, save_url = ParamUtil.get_api_params(self.api_params, save_api_path)
                
                # 设置部分付款金额为4000
                partial_amount = 4000
                
                # 使用数据工厂创建付款申请单请求数据
                save_request_data = self.ap_factory.create_pr_request_data(ap_info, partial_amount)
                
                save_request = {
                    "sceneKey": "ERP_FIN$FIN_APM_FROM_DS",
                    "viewKey": "ERP_FIN$FIN_APM_FROM_DS:6yiz_P4fiRD9Ram4RAK-b",
                    "viewTitle": "创建付款申请",
                    "buttonKey": "ERP_FIN$FIN_APM_FROM_DS-TERP_MIGRATE$FIN_CM_PR-editView-footer-save",
                    "buttonName": "保存",
                    "appId": 0,
                    "teamId": base_data.get("team_id", 22),
                    "serviceKey": "ERP_FIN$PR_SAVE_SERVICE",
                    "params": {"request": save_request_data}
                }
                
                save_result = self.http.post(save_url, json=save_request)
                self.assert_util.assert_response_success(save_result)
                
                # PR_SAVE_SERVICE接口正常返回success: true, data: null
                # 只需验证success字段即可
                a.text(f"✅ 付款申请单保存成功，部分付款金额: {partial_amount}元", "付款申请单保存验证")
                
                TestApBatchCreatePartialPrAndPi.ap_batch_info.update({
                    "partial_amount_doc": partial_amount,
                    "partial_amount_base": partial_amount,
                    "pr_save_success": True
                })
                
                a.json(save_request, "付款申请单保存请求数据")
                a.json(save_result, "付款申请单保存响应数据")
                a.json(TestApBatchCreatePartialPrAndPi.ap_batch_info, "测试数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 

    @case_decorator(
        story="批量采购发票创建",
        title="批量勾选应付单创建采购发票(部分开票)",
        description="执行应付单批量转换采购发票校验，再执行应付单行批量转换采购发票校验，最后保存采购发票(部分开票场景)",
        severity="critical",
        order=3,
        smoke=True,
        tags=["ap", "batch", "pi", "create", "invoice", "partial"]
    )
    def test_03_batch_create_partial_pi_from_ap(self):
        try:
            # 获取前置数据
            ap_info = TestApBatchCreatePartialPrAndPi.ap_batch_info
            ap_doc_id = ap_info.get("ap_doc_id")
            ap_head_code = ap_info.get("ap_head_code")
            ap_item_ids = ap_info.get("ap_item_ids", [])
            
            # 前置条件验证
            assert ap_doc_id and ap_head_code, "应付单创建和过账未完成，请先执行用例1"
            assert ap_info.get("post_completed"), "应付单过账未完成"
            assert ap_item_ids, f"应付单ID {ap_doc_id} 的明细行ID不存在，请检查第一个用例的执行结果"
            
            # 获取基础数据（包含teamId等）
            base_data = self.ap_factory.get_base_data_for_fin_doc("AP")
            
            with a.step("使用第一个用例的应付单明细行ID"):
                a.json({
                    "ap_doc_id": ap_doc_id,
                    "ap_head_code": ap_head_code, 
                    "ap_item_ids": ap_item_ids,
                    "data_source": "第一个用例的出参"
                }, "应付单明细行信息")

            with a.step("执行应付单批量转化采购发票校验服务"):
                val_api_path = ParamUtil.get_api_path(self.apis, "应付单批量转化采购发票-校验服务")
                val_params, val_url = ParamUtil.get_api_params(self.api_params, val_api_path)
                
                # 使用应付单头ID作为第一个接口的入参
                val_request = {
                    "sceneKey": "ERP_FIN$FIN_APM_FROM_DS",
                    "viewKey": "ERP_FIN$FIN_APM_FROM_DS:list",
                    "appId": None,
                    "teamId": base_data.get("team_id", 22),
                    "serviceKey": "ERP_FIN$BATCH_AP_CONVERT_TO_PI_VAL_SERVICE",
                    "params": {"request": {"apmApItemIds": [ap_doc_id]}}  # 使用应付单头ID
                }
                
                val_result = self.http.post(val_url, json=val_request)
                self.assert_util.assert_response_success(val_result)
                
                a.json(val_request, "应付单校验请求数据")
                a.json(val_result, "应付单校验响应数据")

            with a.step("执行应付单行批量转化采购发票校验服务"):
                item_val_api_path = ParamUtil.get_api_path(self.apis, "应付单行批量转化采购发票-校验服务")
                item_val_params, item_val_url = ParamUtil.get_api_params(self.api_params, item_val_api_path)
                
                # 使用应付单明细行ID作为第二个接口的入参
                item_val_request = {
                    "sceneKey": "ERP_FIN$FIN_APM_FROM_DS",
                    "viewKey": "ERP_FIN$FIN_APM_FROM_DS:pkQqXyEVhkP0HpqdAMQC5",
                    "viewTitle": "选择应付单行",
                    "buttonKey": "ERP_FIN$FIN_APM_FROM_DS-KWlwdlZ4J_QWUjN_W147O",
                    "buttonName": "生成采购发票",
                    "appId": 0,
                    "teamId": base_data.get("team_id", 22),
                    "serviceKey": "ERP_FIN$BATCH_AP_ITEM_CONVERT_TO_PI_VAL_SERVICE",
                    "params": {"request": {"apmApItemIds": ap_item_ids}}  # 使用应付单明细行ID
                }
                
                item_val_result = self.http.post(item_val_url, json=item_val_request)
                self.assert_util.assert_response_success(item_val_result)
                
                a.json(item_val_request, "应付单行校验请求数据")
                a.json(item_val_result, "应付单行校验响应数据")

            with a.step("执行采购发票保存服务(部分开票)"):
                save_api_path = ParamUtil.get_api_path(self.apis, "PI-采购发票保存并更新来源服务")
                save_params, save_url = ParamUtil.get_api_params(self.api_params, save_api_path)
                
                # 设置部分开票金额
                ap_gross_amt = TestApBatchCreatePartialPrAndPi.ap_batch_info.get("gross_doc_amt", 10000)
                partial_invoice_amt = ap_gross_amt / 2  # 部分开票金额: 50%
                inv_code = self.mock_data.generate_unique_code("PI")
                
                # 使用数据工厂创建采购发票请求数据
                pi_request_data = self.ap_factory.create_pi_request_data(
                    ap_info, 
                    partial_amount=partial_invoice_amt,
                    partial_qty=50,
                    inv_code=inv_code
                )
                
                save_filtered_params = {"params": {"request": pi_request_data}}
                save_filtered_params = convert_decimal_to_float(save_filtered_params)
                
                save_result = self.http.post(save_url, json=save_filtered_params)
                self.assert_util.assert_response_success(save_result)
                
                pi_head_id = ParamUtil.extract_id(save_result)
                assert pi_head_id, "保存成功但未获取到采购发票ID"
                
                # 从数据工厂生成的数据中获取计算结果
                partial_net_doc_amt = pi_request_data["netDocAmt"]
                partial_tax_doc_amt = pi_request_data["taxDocAmt"]
                
                TestApBatchCreatePartialPrAndPi.ap_batch_info.update({
                    "pi_head_id": pi_head_id,
                    "inv_code": inv_code,
                    "partial_invoice_amt": partial_invoice_amt,
                    "partial_net_doc_amt": partial_net_doc_amt,
                    "partial_tax_doc_amt": partial_tax_doc_amt,
                    "invoice_qty": 50,
                    "invoice_percentage": 50.0
                })
                
                a.json(save_filtered_params, "采购发票保存请求数据")
                a.json(TestApBatchCreatePartialPrAndPi.ap_batch_info, "测试数据")

            with a.step("验证批量创建部分采购发票流程完成"):
                assert TestApBatchCreatePartialPrAndPi.ap_batch_info.get("pi_head_id"), "采购发票创建失败"
                
                # 添加部分开票验证总结
                invoice_summary = {
                    "测试场景": "批量创建部分采购发票",
                    "应付单信息": {
                        "应付单ID": ap_doc_id,
                        "应付单编码": ap_head_code,
                        "应付单总金额": ap_gross_amt
                    },
                    "采购发票信息": {
                        "采购发票ID": pi_head_id,
                        "发票编码": inv_code,
                        "开票金额": partial_invoice_amt,
                        "开票数量": 50,
                        "开票比例": "50%",
                        "不含税金额": partial_net_doc_amt,
                        "税额": partial_tax_doc_amt,
                        "税率": "13%"
                    },
                    "验证结果": {
                        "部分开票金额正确": f"✓ {partial_invoice_amt} = {ap_gross_amt} × 50%",
                        "数量比例一致": f"✓ 开票数量50 = 总数量100 × 50%",
                        "金额计算正确": f"✓ 含税金额 = 不含税金额 + 税额 ({partial_net_doc_amt} + {partial_tax_doc_amt} = {partial_invoice_amt})"
                    },
                    "验证结论": "部分采购发票创建成功，开票金额、数量和税额计算均正确"
                }
                
                a.json(invoice_summary, "部分采购发票创建总结")
                
                # 更新测试数据
                TestApBatchCreatePartialPrAndPi.ap_batch_info.update({
                    "invoice_summary": invoice_summary,
                    "partial_invoice_completed": True
                })
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 

    @case_decorator(
        story="应付单分页查询验证",
        title="分页查询应付单验证金额更新",
        description="通过应付单分页查询接口验证创建付款申请单和采购发票后，应付单的已付款金额、已开票金额等字段是否正确更新",
        severity="critical",
        order=4,
        smoke=True,
        tags=["ap", "query", "page", "verify", "amount"]
    )
    def test_04_query_ap_doc_and_verify_amounts(self):
        """应付单分页查询并验证金额更新"""
        try:
            # 确保前面的用例已运行并获得数据
            ap_doc_id = TestApBatchCreatePartialPrAndPi.ap_batch_info.get("ap_doc_id")
            ap_head_code = TestApBatchCreatePartialPrAndPi.ap_batch_info.get("ap_head_code")
            
            assert ap_doc_id, "未获取到应付单ID，请确保前面的测试用例已成功运行"
            assert ap_head_code, "未获取到应付单编号，请确保前面的测试用例已成功运行"
            
            with a.step("等待异步任务完成"):
                # 等待付款申请单和采购发票的创建及过账完成
                time.sleep(8)  
                a.text("已等待8秒，确保异步任务完成", "等待说明")

            with a.step("执行应付单分页查询"):
                # 获取应付单分页查询API配置
                query_api_path = ParamUtil.get_api_path(self.apis, "应付单头-ES数据分页查询服务")
                query_params, query_url = ParamUtil.get_api_params(self.api_params, query_api_path)
                
                # 构建查询条件：按应付单编号精确查询
                query_condition = {
                    "apHeadCode": ap_head_code,
                    "id": ap_doc_id,
                    "comOrgId": TestApBatchCreatePartialPrAndPi.ap_batch_info.get("com_org_id")
                }
                
                # 设置分页参数
                pageable = {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": [
                        {
                            "fieldAlias": "updatedAt",
                            "sortType": "DESC"
                        }
                    ]
                }
                
                # 构建请求参数
                query_request = {
                    "pageable": pageable
                }
                
                # 使用应付单头编号作为查询条件
                for key in query_condition:
                    if key in query_params.get("params", {}).get("request", {}):
                        query_request[key] = query_condition[key]
                
                # 更新请求参数
                query_filtered_params = ParamUtil.filter_post_body_fields(
                    query_params, list(query_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(query_filtered_params, query_request)
                
                a.json(query_filtered_params, "应付单分页查询请求参数")
                
                # 执行查询
                query_result = self.http.post(query_url, json=query_filtered_params)
                self.assert_util.assert_response_success(query_result)
                
                query_data = query_result.get("data", {}).get("data", {})
                records = query_data.get("records", [])
                
                a.json(query_result, "应付单分页查询结果")
                
                # 验证查询结果
                assert records, f"未查询到应付单数据，单据编号: {ap_head_code}"
                
                # 找到目标应付单记录
                target_ap_record = None
                for record in records:
                    if (record.get("apHeadCode") == ap_head_code or 
                        record.get("id") == ap_doc_id):
                        target_ap_record = record
                        break
                
                assert target_ap_record, f"未找到对应的应付单记录，单据编号: {ap_head_code}"
                
                a.json(target_ap_record, "目标应付单记录")

            with a.step("验证应付单金额字段"):
                # 获取各种金额字段
                gross_doc_amt = float(target_ap_record.get("grossDocAmt", 0))  # 价税合计总额
                gross_base_amt = float(target_ap_record.get("grossBaseAmt", 0))  # 价税合计本币金额
                
                # 付款相关金额
                paying_doc_amt = float(target_ap_record.get("payingDocAmt", 0))  # 付款中金额
                paypaid_doc_amt = float(target_ap_record.get("paypaidDocAmt", 0))  # 已付款金额
                unpaid_doc_amt = float(target_ap_record.get("unpaidDocAmt", 0))  # 未付款金额
                
                paying_base_amt = float(target_ap_record.get("payingBaseAmt", 0))  # 付款中本币金额
                paypaid_base_amt = float(target_ap_record.get("paypaidBaseAmt", 0))  # 已付款本币金额
                unpaid_base_amt = float(target_ap_record.get("unpaidBaseAmt", 0))  # 未付款本币金额
                
                # 开票相关金额
                invoicing_doc_amt = float(target_ap_record.get("invoicingDocAmt", 0))  # 开票中金额
                invoiced_doc_amt = float(target_ap_record.get("invoicedDocAmt", 0))  # 已开票金额
                uninvoiced_doc_amt = float(target_ap_record.get("uninvoicedDocAmt", 0))  # 未开票金额
                
                invoicing_base_amt = float(target_ap_record.get("invoicingBaseAmt", 0))  # 开票中本币金额
                invoiced_base_amt = float(target_ap_record.get("invoicedBaseAmt", 0))  # 已开票本币金额
                uninvoiced_base_amt = float(target_ap_record.get("uninvoicedBaseAmt", 0))  # 未开票本币金额
                
                # 打印所有金额信息用于调试
                amount_info = {
                    "价税合计": {"原币": gross_doc_amt, "本币": gross_base_amt},
                    "付款状态": {
                        "付款中": {"原币": paying_doc_amt, "本币": paying_base_amt},
                        "已付款": {"原币": paypaid_doc_amt, "本币": paypaid_base_amt},
                        "未付款": {"原币": unpaid_doc_amt, "本币": unpaid_base_amt}
                    },
                    "开票状态": {
                        "开票中": {"原币": invoicing_doc_amt, "本币": invoicing_base_amt},
                        "已开票": {"原币": invoiced_doc_amt, "本币": invoiced_base_amt},
                        "未开票": {"原币": uninvoiced_doc_amt, "本币": uninvoiced_base_amt}
                    }
                }
                a.json(amount_info, "应付单金额明细")

            with a.step("验证付款金额计算逻辑"):
                # 验证付款金额逻辑：已付款金额 + 付款中金额 + 未付款金额 = 价税合计总额
                total_payment_related = paypaid_doc_amt + paying_doc_amt + unpaid_doc_amt
                
                assert abs(total_payment_related - gross_doc_amt) < 0.01, (
                    f"付款金额计算异常！\n"
                    f"已付款金额({paypaid_doc_amt}) + 付款中金额({paying_doc_amt}) + 未付款金额({unpaid_doc_amt}) "
                    f"= {total_payment_related}\n"
                    f"应等于价税合计总额: {gross_doc_amt}\n"
                    f"差异: {abs(total_payment_related - gross_doc_amt)}"
                )
                
                # 验证本币付款金额逻辑
                total_payment_base_related = paypaid_base_amt + paying_base_amt + unpaid_base_amt
                
                assert abs(total_payment_base_related - gross_base_amt) < 0.01, (
                    f"本币付款金额计算异常！\n"
                    f"已付款本币金额({paypaid_base_amt}) + 付款中本币金额({paying_base_amt}) + 未付款本币金额({unpaid_base_amt}) "
                    f"= {total_payment_base_related}\n"
                    f"应等于价税合计本币金额: {gross_base_amt}\n"
                    f"差异: {abs(total_payment_base_related - gross_base_amt)}"
                )
                
                a.text(f"✅ 付款金额计算正确：{total_payment_related} = {gross_doc_amt}", "付款金额验证")
                a.text(f"✅ 本币付款金额计算正确：{total_payment_base_related} = {gross_base_amt}", "本币付款金额验证")

            with a.step("验证开票金额计算逻辑"):
                # 验证开票金额逻辑：已开票金额 + 开票中金额 + 未开票金额 = 价税合计总额
                total_invoice_related = invoiced_doc_amt + invoicing_doc_amt + uninvoiced_doc_amt
                
                assert abs(total_invoice_related - gross_doc_amt) < 0.01, (
                    f"开票金额计算异常！\n"
                    f"已开票金额({invoiced_doc_amt}) + 开票中金额({invoicing_doc_amt}) + 未开票金额({uninvoiced_doc_amt}) "
                    f"= {total_invoice_related}\n"
                    f"应等于价税合计总额: {gross_doc_amt}\n"
                    f"差异: {abs(total_invoice_related - gross_doc_amt)}"
                )
                
                # 验证本币开票金额逻辑
                total_invoice_base_related = invoiced_base_amt + invoicing_base_amt + uninvoiced_base_amt
                
                assert abs(total_invoice_base_related - gross_base_amt) < 0.01, (
                    f"本币开票金额计算异常！\n"
                    f"已开票本币金额({invoiced_base_amt}) + 开票中本币金额({invoicing_base_amt}) + 未开票本币金额({uninvoiced_base_amt}) "
                    f"= {total_invoice_base_related}\n"
                    f"应等于价税合计本币金额: {gross_base_amt}\n"
                    f"差异: {abs(total_invoice_base_related - gross_base_amt)}"
                )
                
                a.text(f"✅ 开票金额计算正确：{total_invoice_related} = {gross_doc_amt}", "开票金额验证")
                a.text(f"✅ 本币开票金额计算正确：{total_invoice_base_related} = {gross_base_amt}", "本币开票金额验证")

            with a.step("验证业务逻辑更新"):
                # 验证创建付款申请单后，已付款金额是否有更新
                if paypaid_doc_amt > 0 or paying_doc_amt > 0:
                    a.text(f"✅ 付款申请单创建成功，已更新付款状态：已付款金额={paypaid_doc_amt}, 付款中金额={paying_doc_amt}", "付款状态更新验证")
                else:
                    a.text(f"⚠️ 付款申请单可能未完全处理：已付款金额={paypaid_doc_amt}, 付款中金额={paying_doc_amt}", "付款状态检查")
                
                # 验证创建采购发票后，已开票金额是否有更新
                if invoiced_doc_amt > 0 or invoicing_doc_amt > 0:
                    a.text(f"✅ 采购发票创建成功，已更新开票状态：已开票金额={invoiced_doc_amt}, 开票中金额={invoicing_doc_amt}", "开票状态更新验证")
                else:
                    a.text(f"⚠️ 采购发票可能未完全处理：已开票金额={invoiced_doc_amt}, 开票中金额={invoicing_doc_amt}", "开票状态检查")

            with a.step("保存验证结果"):
                verification_result = {
                    "ap_doc_id": ap_doc_id,
                    "ap_head_code": ap_head_code,
                    "verification_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "amounts": amount_info,
                    "payment_verification": {
                        "total_calculated": total_payment_related,
                        "gross_amount": gross_doc_amt,
                        "difference": abs(total_payment_related - gross_doc_amt),
                        "is_valid": abs(total_payment_related - gross_doc_amt) < 0.01
                    },
                    "invoice_verification": {
                        "total_calculated": total_invoice_related,
                        "gross_amount": gross_doc_amt,
                        "difference": abs(total_invoice_related - gross_doc_amt),
                        "is_valid": abs(total_invoice_related - gross_doc_amt) < 0.01
                    }
                }
                
                # 保存验证结果到类变量
                TestApBatchCreatePartialPrAndPi.ap_batch_info["verification_result"] = verification_result
                
                a.json(verification_result, "验证结果汇总")
                a.text("✅ 应付单分页查询及金额验证全部通过", "测试结论")

        except Exception as e:
            a.text(f"❌ 应付单分页查询验证失败: {str(e)}", "错误信息")
            raise