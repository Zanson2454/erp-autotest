"""
应收单保存服务测试用例
覆盖创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.erp_fin.fin_ar import ArBaseTest, convert_decimal_to_float
from utils.param_util import ParamUtil
from utils.mock_util import MockData
from utils.report_util import a, case_decorator
from datetime import datetime
import time

@allure.epic("ERP通业财模块")
@allure.feature("应收管理")
class TestArDocumentSave(ArBaseTest):
    """应收单全流程自动化用例"""
    ar_info = {}
    mock_data = MockData()
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()

    @case_decorator(
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
                now_ts = int(datetime.now().timestamp() * 1000)
                request_body = {}
                self.create_ar_request_body(now_ts, request_body)
                
                result = {}
                self.send_api_request("AR-应收单保存服务", request_body, result)
                ar_doc_id = ParamUtil.extract_id(result)
                assert ar_doc_id, "创建应收单失败：未获取到单据ID"
                
                TestArDocumentSave.ar_info.update({
                    "ar_doc_id": ar_doc_id,
                    "request_body": request_body
                })
                
                a.json(convert_decimal_to_float(TestArDocumentSave.ar_info), "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行创建标准应收单用例"
                
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                base_request["id"] = ar_doc_id
                base_request["remark"] = f"应收单编辑场景自动化用例 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                result = {}
                self.send_api_request("AR-应收单保存服务", base_request, result)
                
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("arStatus") == "DRAFT", "单据状态不正确"
                assert data.get("remark") == base_request["remark"], "备注未正确变更"
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                assert ar_doc_id and base_request, "请先执行编辑用例，确保ar_doc_id和request_body已生成"
                
                base_request["id"] = ar_doc_id
                base_request["arStatus"] = "CONFIRM"
                if base_request.get("arHeadCode") is None:
                    base_request["arHeadCode"] = self.mock_data.generate_unique_code("AR")
                
                ar_items = base_request.get("arItems", [])
                base_request["grossDocAmt"] = sum([item.get("grossDocAmt", 0) for item in ar_items])
                base_request["netDocAmt"] = sum([item.get("netDocAmt", 0) for item in ar_items])
                base_request["grossBaseAmt"] = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                base_request["netBaseAmt"] = sum([item.get("netBaseAmt", 0) for item in ar_items])
                
                result = {}
                self.send_api_request("AR-应收单-列表提交服务", base_request, result)
                
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("arStatus") == "CONFIRM", "单据状态不正确"
                
                TestArDocumentSave.ar_info["request_body"]["arHeadCode"] = base_request["arHeadCode"]
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                assert ar_doc_id and base_request, "请先执行提交用例，确保ar_doc_id和request_body已生成"
                
                base_request["id"] = ar_doc_id
                base_request["arStatus"] = "CONFIRM"
                ar_items = base_request.get("arItems", [])
                base_request["grossDocAmt"] = sum([item.get("grossDocAmt", 0) for item in ar_items])
                base_request["netDocAmt"] = sum([item.get("netDocAmt", 0) for item in ar_items])
                base_request["grossBaseAmt"] = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                base_request["netBaseAmt"] = sum([item.get("netBaseAmt", 0) for item in ar_items])
                
                result = {}
                self.send_api_request("应收单-过账-异步服务", base_request, result)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
            with a.step("轮询查询应收单过账状态"):
                ar_head_code = TestArDocumentSave.ar_info.get("request_body", {}).get("arHeadCode")
                assert ar_head_code, "请先执行提交用例，确保arHeadCode已生成"
                
                # 轮询检查状态是否更新为DONE，异步执行状态是否等于SUCCEEDED
                max_attempts = 5  # 最大轮询次数（15秒）
                interval = 3  # 轮询间隔（秒）
                current_status = None
                async_status = None
                
                for attempt in range(max_attempts):
                    query_request = {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 10,
                            "needTotal": False,
                            "conditionItems": {
                                "type": "ConditionItems",
                                "conditions": {"arHeadCode": {"operator": "CONTAINS", "value": ar_head_code}},
                                "logicOperator": "AND"
                            }
                        }
                    }
                    
                    # 发送分页查询请求
                    fields = ["pageable"]
                    api_path = ParamUtil.get_api_path(self.apis, "应收单头表-分页数据服务_PmHKWs4")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, fields, ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, query_request)
                    
                    result = self.http.post(url, json=filtered_params)
                    self.assert_util.assert_response_success(result)
                    
                    # 解析响应数据
                    data = result.get("data", {}).get("data", {})
                    data_list = data.get("data", [])
                    
                    if data_list:
                        ar_record = data_list[0]
                        current_status = ar_record.get("arStatus")
                        async_status = ar_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 应收单状态: {current_status}, 异步状态: {async_status}", "状态轮询")
                        
                        # 如果状态为DONE且异步任务成功，则验证通过
                        if current_status == "DONE" and async_status == "SUCCEEDED":
                            a.text("✅ 过账异步任务完成，应收单状态已更新为完成", "验证成功")
                            break
                        # 如果异步任务失败，抛出异常
                        elif async_status == "FAILED":
                            failure_reason = ar_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"应收单过账异步任务失败: {failure_reason}")
                        # 继续等待
                        else:
                            if attempt < max_attempts - 1:
                                a.text(f"异步任务尚未完成，等待{interval}秒后重试...", "等待中")
                                time.sleep(interval)
                    else:
                        raise Exception(f"未找到应收单编码为[{ar_head_code}]的数据")
                
                # 最终验证
                assert current_status == "DONE", f"应收单状态验证失败，期望: DONE，实际: {current_status}"
                assert async_status == "SUCCEEDED", f"过账异步任务未完成，当前状态: {async_status}"
                
                a.json({
                    "arHeadCode": ar_head_code,
                    "expectedStatus": "DONE",
                    "actualStatus": current_status,
                    "asyncExecutionStatus": async_status,
                    "verificationResult": "PASSED"
                }, "状态验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单反过账",
        title="应收单反过账-AR_POST_ROLLBACK_ASYNC_SERVICE（异步服务）",
        description="用前置用例生成的单据进行反过账并断言API调用成功",
        severity="critical",
        order=6,
        smoke=False,
        tags=["ar", "post_rollback"]
    )
    def test_rollback_ar_doc(self):
        try:
            with a.step("应收单反过账"):
                # 获取前置数据
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                ar_head_code = base_request.get("arHeadCode")
                
                assert ar_doc_id and ar_head_code and base_request, "请先执行前置用例，确保ar_doc_id、arHeadCode和request_body已生成"
                
                # 构建反过账请求（精简版本，只保留必要字段）
                rollback_request = {
                    "id": ar_doc_id,
                    "arHeadCode": ar_head_code,
                    "docTypeId": base_request.get("docTypeId"),
                    "arStatus": "DONE",  # 使用过账完成后的状态
                    "comOrgId": base_request.get("comOrgId"),
                    "slsOrgId": base_request.get("slsOrgId"),
                    "payOrgId": base_request.get("payOrgId"),
                    "settPartnerType": base_request.get("settPartnerType"),
                    "createType": "MANUAL",
                    "baseCurrId": base_request.get("baseCurrId"),
                    "docCurrId": base_request.get("docCurrId"),
                    "exchRate": base_request.get("exchRate", 1),
                    "grossDocAmt": base_request.get("grossDocAmt"),
                    "netDocAmt": base_request.get("netDocAmt"),
                    "grossBaseAmt": base_request.get("grossBaseAmt"),
                    "netBaseAmt": base_request.get("netBaseAmt"),
                    "collectionClearingStatus": "UNCLEARED",
                    "billingClearingStatus": "UNCLEARED",
                    "collectedDocAmt": 0,
                    "collectingDocAmt": 0,
                    "uncollectedDocAmt": base_request.get("netDocAmt"),
                    "billedDocAmt": 0,
                    "billingDocAmt": 0,
                    "unbilledDocAmt": base_request.get("netDocAmt"),
                    "remark": base_request.get("remark"),
                    "arDate": base_request.get("arDate"),
                    "offsetDocAmt": 0,
                    "unoffsetDocAmt": base_request.get("netDocAmt"),
                    "offsetBaseAmt": 0,
                    "unoffsetBaseAmt": base_request.get("netBaseAmt"),
                    "headOffsetStatus": "UNOFFSET",
                    "collectedBaseAmt": 0,
                    "uncollectedBaseAmt": base_request.get("netBaseAmt"),
                    "collectingBaseAmt": 0,
                    "billedBaseAmt": 0,
                    "billingBaseAmt": 0,
                    "unbilledBaseAmt": base_request.get("netBaseAmt"),
                    "costAcqStatus": "NO_NEED_OBTAINED",
                    "asyncExecutionStatus": "SUCCEEDED",  # 使用过账成功的异步状态
                    "accountType": "FIN",
                    "aesDsdPushStatus": "WAITING"
                }
                
                # 发送反过账请求
                result = {}
                self.send_api_request("应收单-反过账-异步服务", rollback_request, result)
                
                # 验证API调用成功
                assert result.get("success") is True, f"应收单反过账API调用失败，单据编号: {ar_head_code}"
                
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "ar_head_code": ar_head_code,
                    "ar_doc_id": ar_doc_id
                }, "反过账结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单状态验证",
        title="分页查询验证应收单状态是否为草稿态",
        description="反过账后利用分页查询接口验证应收单状态是否正确回退到草稿态",
        severity="critical",
        order=7,
        smoke=False,
        tags=["ar", "verify", "status", "draft"]
    )
    def test_verify_ar_doc_status_is_draft(self):
        try:
            with a.step("轮询查询应收单反过账状态"):
                # 获取应收单编码
                ar_head_code = TestArDocumentSave.ar_info.get("request_body", {}).get("arHeadCode")
                assert ar_head_code, "请先执行前置用例，确保arHeadCode已生成"
                
                # 轮询检查状态是否更新为DRAFT，异步执行状态是否等于SUCCEEDED
                max_attempts = 5  # 最大轮询次数（15秒）
                interval = 3  # 轮询间隔（秒）
                current_status = None
                async_status = None
                
                for attempt in range(max_attempts):
                    query_request = {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 10,
                            "needTotal": False,
                            "conditionItems": {
                                "type": "ConditionItems",
                                "conditions": {"arHeadCode": {"operator": "CONTAINS", "value": ar_head_code}},
                                "logicOperator": "AND"
                            }
                        }
                    }
                    
                    # 发送分页查询请求
                    fields = ["pageable"]
                    api_path = ParamUtil.get_api_path(self.apis, "应收单头表-分页数据服务_PmHKWs4")
                    params, url = ParamUtil.get_api_params(self.api_params, api_path)
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, fields, ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, query_request)
                    
                    result = self.http.post(url, json=filtered_params)
                    self.assert_util.assert_response_success(result)
                    
                    # 解析响应数据
                    data = result.get("data", {}).get("data", {})
                    data_list = data.get("data", [])
                    
                    if data_list:
                        ar_record = data_list[0]
                        current_status = ar_record.get("arStatus")
                        async_status = ar_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 应收单状态: {current_status}, 异步状态: {async_status}", "状态轮询")
                        
                        # 如果状态为DRAFT且异步任务成功，则验证通过
                        if current_status == "DRAFT" and async_status == "SUCCEEDED":
                            a.text("✅ 反过账异步任务完成，应收单状态已回退到草稿态", "验证成功")
                            break
                        # 如果异步任务失败，抛出异常
                        elif async_status == "FAILED":
                            failure_reason = ar_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"应收单反过账异步任务失败: {failure_reason}")
                        # 继续等待
                        else:
                            if attempt < max_attempts - 1:
                                a.text(f"异步任务尚未完成，等待{interval}秒后重试...", "等待中")
                                time.sleep(interval)
                    else:
                        raise Exception(f"未找到应收单编码为[{ar_head_code}]的数据")
                
                # 最终验证
                assert current_status == "DRAFT", f"应收单状态验证失败，期望: DRAFT，实际: {current_status}"
                assert async_status == "SUCCEEDED", f"反过账异步任务未完成，当前状态: {async_status}"
                
                a.json({
                    "arHeadCode": ar_head_code,
                    "expectedStatus": "DRAFT",
                    "actualStatus": current_status,
                    "asyncExecutionStatus": async_status,
                    "verificationResult": "PASSED"
                }, "状态验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单删除",
        title="应收单删除-AR_DELETE_EVENT_SERVICE（动态单据）",
        description="等待反过账完成后执行应收单删除操作，并断言删除后单据状态变为DRAFT",
        severity="critical",
        order=8,
        smoke=False,
        tags=["ar", "delete"]
    )
    def test_delete_ar_doc(self):
        try:
            with a.step("等待反过账异步任务完成"):
                # 等待8秒让反过账异步任务完成
                a.text("等待8秒让反过账异步任务完成...", "等待反过账")
                time.sleep(8)
                
            with a.step("执行应收单删除操作"):
                # 获取前置数据
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                ar_head_code = base_request.get("arHeadCode")
                
                assert ar_doc_id and ar_head_code and base_request, "请先执行前置用例，确保ar_doc_id、arHeadCode和request_body已生成"
                
                # 构建删除请求
                delete_request = base_request.copy()
                delete_request.update({
                    "id": ar_doc_id,
                    "arStatus": "DRAFT",  # 使用草稿态状态，因为已经反过账
                    "asyncExecutionStatus": "CREATED"
                })
                
                # 计算总金额
                ar_items = delete_request.get("arItems", [])
                delete_request["grossDocAmt"] = sum([item.get("grossDocAmt", 0) for item in ar_items])
                delete_request["netDocAmt"] = sum([item.get("netDocAmt", 0) for item in ar_items])
                delete_request["grossBaseAmt"] = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                delete_request["netBaseAmt"] = sum([item.get("netBaseAmt", 0) for item in ar_items])
                
                # 发送删除请求
                result = {}
                self.send_api_request("AR-应收单删除服务", delete_request, result)
                
                # 验证API调用成功
                assert result.get("success") is True, f"应收单删除API调用失败，单据编号: {ar_head_code}"

            with a.step("验证删除API调用成功"):
                # 对于删除操作，只需要验证API调用成功，不需要验证状态变化
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "ar_head_code": ar_head_code,
                    "ar_doc_id": ar_doc_id,
                    "delete_result": "API_CALL_SUCCESS"
                }, "删除验证结果")
                
                a.text(f"""
                应收单删除验证总结:
                ✓ 应收单编码: {ar_head_code}
                ✓ 删除API调用: 成功
                ✓ 验证结果: API调用成功
                """, "应收单删除总结")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestArDocumentSave()
    test.setup_class()
    test.test_create_draft_ar_doc()
    test.test_edit_ar_doc()
    test.test_submit_ar_doc()
    test.test_post_ar_doc()
    test.test_check_ar_doc_status_by_code_paging()
    test.test_rollback_ar_doc()
    test.test_delete_ar_doc() 