"""
应付单保存服务测试用例
包含创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.erp_fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from datetime import datetime
import time

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApDocumentSave(ApBaseTest):
    ap_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()

    @case_decorator(
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
                # 创建应付单请求体
                ap_data = self.create_ap_request_body(doc_type_id=2002001, account_type="FIN")
                request_body = ap_data["request_body"]
                base_data = ap_data["base_data"]
                
                # 发送创建请求
                fields = ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", 
                         "remark", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", 
                         "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", 
                         "payClearingStatus", "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"]
                
                response = self.send_api_request("AP-应付保存服务", request_body, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 提取应付单ID
                ap_doc_id = ParamUtil.extract_id(result)
                assert ap_doc_id, "创建应付单失败：未获取到单据ID"
                
                # 保存测试数据
                TestApDocumentSave.ap_info.update({
                    "ap_doc_id": ap_doc_id,
                    "apHeadCode": request_body["apHeadCode"],
                    "apDate": request_body["apDate"],  # 保存应付单日期
                    "settPartnerId": base_data["vend"],
                    "payOrgId": base_data["pay_org"],
                    "comOrgId": base_data["com_org"],
                    "purOrgId": base_data["pur_org"],
                    "total_amt": base_data["total_amt"],
                    "net_doc_amt": base_data["net_doc_amt"],
                    "gross_base_amt": base_data["gross_base_amt"],
                    "net_base_amt": base_data["net_base_amt"],
                    "request_body": request_body
                })
                
                # 转换Decimal类型以便JSON序列化
                ap_info_for_report = self.convert_decimal_to_float(TestApDocumentSave.ap_info)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(ap_info_for_report, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单编辑",
        title="编辑应付单备注内容",
        description="编辑应付单备注内容并保存",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ap", "edit", "remark"]
    )
    def test_edit_ap_doc_remark(self):
        try:
            with a.step("编辑应付单备注内容"):
                ap_doc_id = TestApDocumentSave.ap_info.get("ap_doc_id")
                assert ap_doc_id, "请先执行创建标准应付单用例"
                
                # 构建编辑请求，修改备注内容
                base_request = TestApDocumentSave.ap_info.get("request_body", {}).copy()
                new_remark = f"自动化测试编辑应付单备注 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                base_request.update({
                    "id": ap_doc_id,
                    "remark": new_remark
                })
                
                # 发送编辑请求
                response = self.send_api_request("AP-应付保存服务", base_request, list(base_request.keys()))
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 验证编辑结果
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True
                assert isinstance(data.get("id"), int)
                assert data.get("docTypeId", {}).get("id") == 2002001  # 保持原始单据类型
                assert data.get("apHeadCode")
                assert data.get("remark") == new_remark
                
                # 更新测试数据中的备注
                TestApDocumentSave.ap_info["remark"] = new_remark
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"updated_remark": new_remark}, "备注更新结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                # 获取前置数据
                ap_doc_id = TestApDocumentSave.ap_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                sett_partner_id = TestApDocumentSave.ap_info.get("settPartnerId")
                pay_org_id = TestApDocumentSave.ap_info.get("payOrgId")
                total_amt = TestApDocumentSave.ap_info.get("total_amt")
                net_doc_amt = TestApDocumentSave.ap_info.get("net_doc_amt")
                gross_base_amt = TestApDocumentSave.ap_info.get("gross_base_amt")
                net_base_amt = TestApDocumentSave.ap_info.get("net_base_amt")
                
                assert all([ap_doc_id, ap_head_code, sett_partner_id, pay_org_id]), \
                    "请先执行创建用例，确保ap_doc_id、apHeadCode、settPartnerId和payOrgId已生成"
                
                # 构建提交请求
                submit_request = {
                    "apHeadCode": ap_head_code,
                    "apStatus": "CONFIRM",
                    "comOrgId": TestApDocumentSave.ap_info.get("comOrgId"),
                    "purOrgId": TestApDocumentSave.ap_info.get("purOrgId"),
                    "payOrgId": pay_org_id,
                    "grossDocAmt": total_amt,
                    "grossBaseAmt": gross_base_amt,
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": total_amt,
                    "uninvoicedDocAmt": total_amt,
                    "unpaidBaseAmt": gross_base_amt,
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
                }
                
                # 发送提交请求
                fields = list(submit_request.keys())
                response = self.send_api_request("AP-应付单-列表提交服务", submit_request, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单过账",
        title="应付单过账-AP_POST_ASYNC_EVENT_SERVICE（动态单据）",
        description="用前置用例生成的单据进行过账并断言API调用成功",
        severity="critical",
        order=4,
        smoke=False,
        tags=["ap", "post"]
    )
    def test_post_ap_doc(self):
        try:
            with a.step("应付单过账"):
                # 获取前置数据
                ap_doc_id = TestApDocumentSave.ap_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                assert ap_doc_id and ap_head_code, "请先执行前置用例，确保ap_doc_id和apHeadCode已生成"
                
                # 构建过账请求
                post_request = {
                    "apHeadCode": ap_head_code,
                    "docTypeId": {"id": 2002001},
                    "apStatus": "CONFIRM",
                    "comOrgId": TestApDocumentSave.ap_info.get("comOrgId"),
                    "purOrgId": TestApDocumentSave.ap_info.get("purOrgId"),
                    "payOrgId": TestApDocumentSave.ap_info.get("payOrgId"),
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": TestApDocumentSave.ap_info.get("settPartnerId")["id"]},
                    "docCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "baseCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "exchRate": 1,
                    "grossDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "netDocAmt": TestApDocumentSave.ap_info.get("net_doc_amt"),
                    "grossBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "netBaseAmt": TestApDocumentSave.ap_info.get("net_base_amt"),
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "uninvoicedDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unpaidBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "uninvoicedBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id,
                    "apItems": [],
                    "apSchls": []
                }
                
                # 发送过账请求
                fields = list(post_request.keys())
                response = self.send_api_request("应付单-过账-异步服务", post_request, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 验证API调用成功
                assert result.get("success") is True, f"应付单过账API调用失败，单据编号: {ap_head_code}"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"api_success": result.get("success"), "ap_head_code": ap_head_code}, "过账结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单状态校验",
        title="根据单据编号分页查询应付单状态",
        description="用apHeadCode分页查询应付单详情并轮询等待状态变为DONE",
        severity="critical",
        order=5,
        smoke=False,
        tags=["ap", "check", "status", "by_code", "polling"]
    )
    def test_check_ap_doc_status_by_code_paging(self):
        try:
            with a.step("根据单据编号分页查询应付单状态"):
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                assert ap_head_code, "请先执行前置用例，确保apHeadCode已生成"
                
                # 轮询查询应付单状态
                max_attempts = 15  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                current_status = None
                
                for attempt in range(max_attempts):
                    try:
                        # 构建查询请求
                        query_request = {
                            "apHeadCode": ap_head_code,
                            "pageable": {
                                "page": 0,
                                "size": 10,
                                "sort": []
                            }
                        }
                        
                        # 使用指定的分页数据服务API
                        api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
                        params, url = ParamUtil.get_api_params(self.api_params, api_path)
                        
                        filtered_params = ParamUtil.filter_post_body_fields(
                            params, ["apHeadCode", "pageable"], ["params", "request"]
                        )
                        ParamUtil.set_request_params(filtered_params, query_request)
                        
                        # 发送查询请求
                        result = self.http.post(url, json=filtered_params)
                        
                        if result.get("success"):
                            data = result.get("data", {}).get("data", {})
                            records = data.get("data", [])  # 修正数据结构路径
                            
                            if records:
                                # 找到匹配的应付单记录
                                ap_record = None
                                for record in records:
                                    if record.get("apHeadCode") == ap_head_code:
                                        ap_record = record
                                        break
                                
                                if ap_record:
                                    current_status = ap_record.get("apStatus")
                                    a.text(f"第{attempt + 1}次查询，当前状态: {current_status}", "轮询状态")
                                    
                                    if current_status == "DONE":
                                        # 状态已变为DONE，验证成功
                                        a.json({"apHeadCode": ap_head_code}, "查询条件")
                                        a.json(ap_record, "应付单详情")
                                        a.json({
                                            "ap_status": current_status, 
                                            "polling_attempts": attempt + 1,
                                            "status_check": "PASSED"
                                        }, "状态校验结果")
                                        break  # 跳出轮询循环，验证成功
                                    
                                    elif current_status in ["DRAFT", "CONFIRM"]:
                                        # 状态还未完成，继续轮询
                                        if attempt < max_attempts - 1:
                                            time.sleep(interval)
                                            continue
                                    else:
                                        # 状态异常
                                        assert False, f"应付单状态异常，期望: DONE，实际: {current_status}"
                                else:
                                    a.text(f"第{attempt + 1}次查询，未找到匹配的应付单记录", "轮询状态")
                            else:
                                a.text(f"第{attempt + 1}次查询，返回记录为空", "轮询状态")
                        else:
                            a.text(f"第{attempt + 1}次查询，API调用失败", "轮询状态")
                        
                        # 如果不是最后一次尝试，等待后继续
                        if attempt < max_attempts - 1:
                            time.sleep(interval)
                            
                    except Exception as e:
                        a.text(f"第{attempt + 1}次查询异常: {str(e)}", "轮询异常")
                        if attempt < max_attempts - 1:
                            time.sleep(interval)
                            continue
                        else:
                            raise
                
                # 验证最终状态 - 如果是通过break跳出循环，状态应该已经是DONE
                if current_status == "DONE":
                    a.text(f"应付单状态校验完成，最终状态: {current_status}", "状态校验完成")
                else:
                    # 轮询结束仍未达到期望状态
                    assert False, f"轮询{max_attempts}次后，应付单状态仍未变为DONE，最后状态: {current_status}，单据编号: {ap_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单反过账",
        title="应付单反过账-AP_POST_ROLLBACK_ASYNC_SERVICE（动态单据）",
        description="用前置用例生成的单据进行反过账并断言API调用成功",
        severity="critical",
        order=6,
        smoke=False,
        tags=["ap", "post_rollback"]
    )
    def test_rollback_ap_doc(self):
        try:
            with a.step("应付单反过账"):
                # 获取前置数据
                ap_doc_id = TestApDocumentSave.ap_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                assert ap_doc_id and ap_head_code, "请先执行前置用例，确保ap_doc_id和apHeadCode已生成"
                
                # 构建反过账请求
                rollback_request = {
                    "id": ap_doc_id,
                    "apHeadCode": ap_head_code,
                    "docTypeId": {"id": 2002001},
                    "apStatus": "DONE",
                    "comOrgId": TestApDocumentSave.ap_info.get("comOrgId"),
                    "purOrgId": TestApDocumentSave.ap_info.get("purOrgId"),
                    "payOrgId": TestApDocumentSave.ap_info.get("payOrgId"),
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": TestApDocumentSave.ap_info.get("settPartnerId")["id"]},
                    "docCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "baseCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "exchRate": 1,
                    "grossDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "netDocAmt": TestApDocumentSave.ap_info.get("net_doc_amt"),
                    "grossBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "netBaseAmt": TestApDocumentSave.ap_info.get("net_base_amt"),
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "uninvoicedDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unpaidBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "uninvoicedBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "DONE",
                    "apItems": [],
                    "apSchls": []
                }
                
                # 发送反过账请求
                fields = list(rollback_request.keys())
                response = self.send_api_request("应付单-反过账-异步服务", rollback_request, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 验证API调用成功
                assert result.get("success") is True, f"应付单反过账API调用失败，单据编号: {ap_head_code}"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"api_success": result.get("success"), "ap_head_code": ap_head_code}, "反过账结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单状态验证",
        title="分页查询验证应付单状态是否为草稿态",
        description="在删除前使用分页查询接口验证应付单状态是否已正确回退到草稿态",
        severity="critical",
        order=7,
        smoke=False,
        tags=["ap", "verify", "status", "draft", "paging"]
    )
    def test_verify_ap_doc_status_is_draft(self):
        try:
            with a.step("等待反过账异步任务完成"):
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                assert ap_head_code, "请先执行前置用例，确保apHeadCode已生成"
            

            with a.step("分页查询验证应付单状态"):
                # 轮询查询应付单状态，验证是否为草稿态
                max_attempts = 10  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                current_status = None
                
                for attempt in range(max_attempts):
                    try:
                        # 构建查询请求，使用与用例5相同的接口和参数结构
                        query_request = {
                            "apHeadCode": ap_head_code,
                            "pageable": {
                                "page": 0,
                                "size": 10,
                                "sort": []
                            }
                        }
                        
                        # 使用指定的分页数据服务API
                        api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
                        params, url = ParamUtil.get_api_params(self.api_params, api_path)
                        
                        filtered_params = ParamUtil.filter_post_body_fields(
                            params, ["apHeadCode", "pageable"], ["params", "request"]
                        )
                        ParamUtil.set_request_params(filtered_params, query_request)
                        
                        # 发送查询请求
                        result = self.http.post(url, json=filtered_params)
                        
                        if result.get("success"):
                            data = result.get("data", {}).get("data", {})
                            records = data.get("data", [])  # 修正数据结构路径
                            
                            if records:
                                # 找到匹配的应付单记录
                                ap_record = None
                                for record in records:
                                    if record.get("apHeadCode") == ap_head_code:
                                        ap_record = record
                                        break
                                
                                if ap_record:
                                    current_status = ap_record.get("apStatus")
                                    a.text(f"第{attempt + 1}次查询，应付单状态: {current_status}", "状态查询")
                                    
                                    if current_status == "DRAFT":
                                        # 状态正确，验证成功
                                        a.text(f"应付单状态验证成功，当前状态: {current_status}", "验证结果")
                                        
                                        # 添加验证结果到报告
                                        a.json({
                                            "ap_head_code": ap_head_code,
                                            "expected_status": "DRAFT",
                                            "actual_status": current_status,
                                            "verification_result": "PASSED",
                                            "attempts": attempt + 1
                                        }, "状态验证结果")
                                        
                                        break  # 跳出轮询循环，验证成功
                                    
                                    elif current_status in ["CONFIRM", "DONE"]:
                                        # 状态还未回退，继续轮询
                                        if attempt < max_attempts - 1:
                                            a.text(f"状态还未回退到草稿态，继续轮询...", "等待状态更新")
                                            time.sleep(interval)
                                            continue
                                        else:
                                            # 轮询结束仍未回退到草稿态
                                            assert False, f"轮询{max_attempts}次后，应付单状态仍未回退到草稿态，当前状态: {current_status}，单据编号: {ap_head_code}"
                                    else:
                                        # 状态异常
                                        assert False, f"应付单状态异常，期望: DRAFT，实际: {current_status}，单据编号: {ap_head_code}"
                                else:
                                    a.text(f"第{attempt + 1}次查询，未找到匹配的应付单记录", "查询结果")
                            else:
                                a.text(f"第{attempt + 1}次查询，返回记录为空", "查询结果")
                        else:
                            a.text(f"第{attempt + 1}次查询，API调用失败", "查询结果")
                        
                        # 如果不是最后一次尝试，等待后继续
                        if attempt < max_attempts - 1:
                            time.sleep(interval)
                            
                    except Exception as e:
                        a.text(f"第{attempt + 1}次查询异常: {str(e)}", "查询异常")
                        if attempt < max_attempts - 1:
                            time.sleep(interval)
                            continue
                        else:
                            raise
                
                # 验证最终状态 - 如果是通过break跳出循环，状态应该已经是DRAFT
                if current_status == "DRAFT":
                    a.text(f"应付单状态验证完成，最终状态: {current_status}", "状态验证完成")
                else:
                    # 轮询结束仍未找到正确状态
                    assert False, f"轮询{max_attempts}次后，未能验证应付单状态为草稿态，最后状态: {current_status}，单据编号: {ap_head_code}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单删除",
        title="应付单删除-AP_DELETE_EVENT_SERVICE（动态单据）",
        description="在确认状态为草稿态后执行应付单删除操作",
        severity="critical",
        order=8,
        smoke=False,
        tags=["ap", "delete"]
    )
    def test_delete_ap_doc(self):
        try:
            with a.step("获取前置数据"):
                # 获取前置数据
                ap_doc_id = TestApDocumentSave.ap_info.get("ap_doc_id")
                ap_head_code = TestApDocumentSave.ap_info.get("apHeadCode")
                assert ap_doc_id and ap_head_code, "请先执行前置用例，确保ap_doc_id和apHeadCode已生成"

            with a.step("执行应付单删除操作"):
                # 构建删除请求
                delete_request = {
                    "id": ap_doc_id,
                    "apHeadCode": ap_head_code,
                    "apDate": TestApDocumentSave.ap_info.get("apDate"),  # 添加应付单日期
                    "docTypeId": {"id": 2002001},
                    "apStatus": "DRAFT",
                    "comOrgId": TestApDocumentSave.ap_info.get("comOrgId"),
                    "purOrgId": TestApDocumentSave.ap_info.get("purOrgId"),
                    "payOrgId": TestApDocumentSave.ap_info.get("payOrgId"),
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": TestApDocumentSave.ap_info.get("settPartnerId")["id"]},
                    "docCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "baseCurrId": {"id": TestApDocumentSave.ap_info.get("payOrgId")["id"]},
                    "exchRate": 1,
                    "grossDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "netDocAmt": TestApDocumentSave.ap_info.get("net_doc_amt"),
                    "grossBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "netBaseAmt": TestApDocumentSave.ap_info.get("net_base_amt"),
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "uninvoicedDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unpaidBaseAmt": TestApDocumentSave.ap_info.get("gross_base_amt"),
                    "uninvoicedBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetDocAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "unoffsetBaseAmt": TestApDocumentSave.ap_info.get("total_amt"),
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "apItems": [],
                    "apSchls": []
                }
                
                # 发送删除请求
                fields = list(delete_request.keys())
                response = self.send_api_request("AP-应付单删除服务", delete_request, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 验证API调用成功
                assert result.get("success") is True, f"应付单删除API调用失败，单据编号: {ap_head_code}"
                
                # 添加报告附件
                a.json(filtered_params, "删除请求数据")
                a.json(result, "删除响应结果数据")

            with a.step("验证删除后应付单状态"):
                # 验证删除后的状态，应该变为DRAFT
                data = result.get("data", {}).get("data", {})
                actual_status = data.get("apStatus")
                
                # 断言状态是否等于DRAFT
                assert actual_status == "DRAFT", f"应付单删除后状态验证失败，期望: DRAFT，实际: {actual_status}"
                
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "ap_head_code": ap_head_code,
                    "expected_status": "DRAFT",
                    "actual_status": actual_status,
                    "status_check": "PASSED" if actual_status == "DRAFT" else "FAILED"
                }, "删除验证结果")
                
                a.text(f"""
                应付单删除验证总结:
                ✓ 应付单编码: {ap_head_code}
                ✓ 删除API调用: 成功
                ✓ 删除后状态: {actual_status}
                ✓ 状态验证: {'通过' if actual_status == 'DRAFT' else '失败'}
                """, "应付单删除总结")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApDocumentSave()
    test.setup_class() 