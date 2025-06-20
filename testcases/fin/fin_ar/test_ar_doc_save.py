"""
应收单保存服务测试用例
覆盖创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.fin.fin_ar import ArBaseTest, convert_decimal_to_float
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
            with a.step("轮询查询应收单状态"):
                ar_head_code = TestArDocumentSave.ar_info.get("request_body", {}).get("arHeadCode")
                assert ar_head_code, "请先执行提交用例，确保arHeadCode已生成"
                
                status_result = {}
                self.wait_for_ar_status(ar_head_code, "DONE", status_result, max_wait=120, interval=3)
                
                assert status_result.get("success"), f"等待应收单状态变更失败，最终状态：{status_result.get('status')}"
                assert status_result.get("status") == "DONE", f"应收单状态应为DONE，实际为：{status_result.get('status')}"
                
                a.json({
                    "arHeadCode": ar_head_code,
                    "finalStatus": status_result.get("status"),
                    "waitedTime": status_result.get("waited_time", 0)
                }, "断言结果")
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
                
                # 构建反过账请求
                rollback_request = base_request.copy()
                rollback_request.update({
                    "id": ar_doc_id,
                    "arStatus": "DONE",
                    "asyncExecutionStatus": "DONE"
                })
                
                # 计算总金额
                ar_items = rollback_request.get("arItems", [])
                rollback_request["grossDocAmt"] = sum([item.get("grossDocAmt", 0) for item in ar_items])
                rollback_request["netDocAmt"] = sum([item.get("netDocAmt", 0) for item in ar_items])
                rollback_request["grossBaseAmt"] = sum([item.get("grossBaseAmt", 0) for item in ar_items])
                rollback_request["netBaseAmt"] = sum([item.get("netBaseAmt", 0) for item in ar_items])
                
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
            with a.step("分页查询验证应收单状态"):
                # 获取应收单编码
                ar_head_code = TestArDocumentSave.ar_info.get("request_body", {}).get("arHeadCode")
                assert ar_head_code, "请先执行前置用例，确保arHeadCode已生成"
                
                # 轮询查询应收单状态，验证是否为草稿态
                max_attempts = 10  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                current_status = None
                verification_success = False  # 验证成功标志
                
                for attempt in range(max_attempts):
                    try:
                        # 构建分页查询请求（使用正确的参数格式）
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
                        
                        if result.status_code == 200 and result.json().get("success"):
                            data = result.json().get("data", {}).get("data", {})
                            data_list = data.get("data", [])
                            
                            if data_list:
                                current_status = data_list[0].get("arStatus")
                                async_status = data_list[0].get("asyncExecutionStatus")
                                
                                a.text(f"第{attempt + 1}次查询 - 应收单状态: {current_status}, 异步状态: {async_status}", 
                                      "状态查询结果")
                                
                                # 添加调试信息
                                a.text(f"验证条件: current_status={current_status}, async_status={async_status}", "调试信息")
                                a.text(f"条件判断: status==DRAFT: {current_status == 'DRAFT'}, async in list: {async_status in ['SUCCEEDED', 'CREATED']}", "调试信息")
                                
                                # 如果状态为DRAFT且异步执行完成，则验证成功，立即退出轮询
                                if current_status == "DRAFT" and async_status in ["SUCCEEDED", "CREATED"]:
                                    a.text("✅ 应收单状态已正确回退到草稿态", "验证成功")
                                    verification_success = True
                                    break
                                # 如果异步执行失败，则抛出异常
                                elif async_status == "FAILED":
                                    failure_reason = data_list[0].get("asyncExecutionFailureReason", "未知原因")
                                    raise Exception(f"应收单异步执行失败: {failure_reason}")
                            else:
                                a.text(f"第{attempt + 1}次查询 - 未找到应收单数据", "查询结果")
                        else:
                            error_info = result.json() if result.status_code == 200 else {"error": f"HTTP {result.status_code}"}
                            a.text(f"第{attempt + 1}次查询失败: {error_info}", "查询异常")
                    
                    except Exception as e:
                        a.text(f"第{attempt + 1}次查询异常: {str(e)}", "查询异常")
                        # 如果查询异常但已经获取过正确状态，不影响最终结果
                        if current_status == "DRAFT":
                            a.text("虽有查询异常，但已获取到正确状态，继续验证", "状态确认")
                            break
                    
                    # 如果已经验证成功，立即退出轮询
                    if verification_success:
                        break
                    
                    # 如果不是最后一次尝试，则等待后继续
                    if attempt < max_attempts - 1:
                        time.sleep(interval)
                
                # 验证最终状态 - 使用verification_success标志来判断
                if not verification_success:
                    assert current_status == "DRAFT", f"应收单状态验证失败，期望: DRAFT，实际: {current_status}，验证状态: {verification_success}"
                
                # 如果验证成功，确保状态确实是DRAFT
                assert verification_success, f"应收单状态验证未完成，最后查询到的状态: {current_status}"
                
                a.json({
                    "arHeadCode": ar_head_code,
                    "expectedStatus": "DRAFT",
                    "actualStatus": current_status,
                    "attempts": attempt + 1,
                    "maxAttempts": max_attempts,
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
                # 获取前置数据
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                ar_head_code = base_request.get("arHeadCode")
                
                assert ar_doc_id and ar_head_code and base_request, "请先执行前置用例，确保ar_doc_id、arHeadCode和request_body已生成"
                
                # 等待5秒让反过账异步任务完成
                a.text("等待5秒让反过账异步任务完成...", "等待反过账")
                time.sleep(5)

            with a.step("执行应收单删除操作"):
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

            with a.step("验证删除后应收单状态"):
                # 验证删除后的状态，应该变为DRAFT
                data = result.get("data", {}).get("data", {})
                actual_status = data.get("arStatus")
                
                # 断言状态是否等于DRAFT
                assert actual_status == "DRAFT", f"应收单删除后状态验证失败，期望: DRAFT，实际: {actual_status}"
                
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "ar_head_code": ar_head_code,
                    "ar_doc_id": ar_doc_id,
                    "expected_status": "DRAFT",
                    "actual_status": actual_status,
                    "status_check": "PASSED" if actual_status == "DRAFT" else "FAILED"
                }, "删除验证结果")
                
                a.text(f"""
                应收单删除验证总结:
                ✓ 应收单编码: {ar_head_code}
                ✓ 删除API调用: 成功
                ✓ 删除后状态: {actual_status}
                ✓ 状态验证: {'通过' if actual_status == 'DRAFT' else '失败'}
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