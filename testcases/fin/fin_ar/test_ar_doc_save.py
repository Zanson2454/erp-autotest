"""
应收单保存服务测试用例
覆盖创建、编辑、提交、过账、状态校验等场景
"""
import allure
from testcases.fin.fin_ar import ArBaseTest, convert_decimal_to_float
from utils.param_util import ParamUtil
from utils.report_util import a
from datetime import datetime
import time

class TestArDocumentSave(ArBaseTest):
    """应收单全流程自动化用例"""
    ar_info = {}

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
                ar_doc_id = TestArDocumentSave.ar_info.get("ar_doc_id")
                base_request = TestArDocumentSave.ar_info.get("request_body", {}).copy()
                assert ar_doc_id and base_request, "请先执行编辑用例，确保ar_doc_id和request_body已生成"
                
                base_request["id"] = ar_doc_id
                base_request["arStatus"] = "CONFIRM"
                if base_request.get("arHeadCode") is None:
                    base_request["arHeadCode"] = ParamUtil.generate_unique_code("AR")
                
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

if __name__ == "__main__":
    test = TestArDocumentSave()
    test.setup_class()
    test.test_create_draft_ar_doc()
    test.test_edit_ar_doc()
    test.test_submit_ar_doc()
    test.test_post_ar_doc()
    test.test_check_ar_doc_status_by_code_paging() 