"""
付款申请单和付款单创建测试用例
"""
from datetime import datetime
from decimal import Decimal

import allure

from erp_data_factory.compat.fin_ap_factory import FinApFactory
from testcases.erp_fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("财务管理")
@allure.feature("付款申请单管理")
class TestPrCreateAndPayment(ApBaseTest):
    pr_info = {}
    fin_ap_factory = None
    pn_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.fin_ap_factory = FinApFactory()

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
        story="付款申请单创建",
        title="创建付款申请单流程",
        description="验证付款申请单创建功能正确性（覆盖数据构造、接口调用、响应校验及数据保存）",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["付款申请单", "创建功能", "核心流程"]
    )
    def test_payment_request_create(self):
        try:
            with a.step("创建付款申请单流程"):
                # 1. 使用数据工厂创建完整的请求数据
                payment_amount = 4600.0
                request_data = self.fin_ap_factory.create_payment_request_data(
                    payment_amount=payment_amount,
                    remark="自动化测试付款申请单"
                )
                
                # 2. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PR-付款申请保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 3. 转换数据类型以支持JSON序列化
                filtered_params = self.convert_data_for_json(request_data)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应
                self.assert_util.assert_response_success(result)
                pr_id = ParamUtil.extract_id(result)
                assert pr_id, "创建付款申请单失败：返回的ID为空"
                
                # 6. 保存测试数据（从请求数据中提取）
                request_params = request_data["params"]["request"]
                TestPrCreateAndPayment.pr_info.update({
                    "pr_id": pr_id,
                    "payment_amount": payment_amount,
                    "vendor_id": request_params["vendorCode"]["id"],
                    "com_org_id": request_params["comOrgId"]["id"],
                    "pur_org_id": request_params["purOrgId"]["id"],
                    "pay_org_id": request_params["payOrgId"]["id"],
                    "currency_id": request_params["docCurrId"]["id"],
                    "doc_type_id": request_params["docTypeId"]["id"],
                    "settlement_method_id": request_params["prItems"][0]["settlementMethodCode"]["id"],
                    "payment_purpose_id": request_params["prItems"][0]["paymentPurposeCode"]["id"]
                })
                
                # 7. 添加 allure 附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestPrCreateAndPayment.pr_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单查询",
        title="查询付款申请单流程",
        description="验证付款申请单查询功能正确性（覆盖查询条件构造、分页查询接口、结果校验及数据匹配验证）",
        severity="normal",
        order=2,
        tags=["付款申请单", "查询功能"]
    )
    def test_payment_request_query(self):
        try:
            with a.step("查询付款申请单流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要查询的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造查询条件
                query_conditions = {
                    "conditionItems": {
                        "conditions": {
                            "id": {
                                "operator": "EQ",
                                "value": TestPrCreateAndPayment.pr_info["pr_id"]
                            }
                        }
                    },
                    "sortOrders": None,
                    "pageSize": 20,
                    "pageIndex": 1
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["conditionItems", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "pageable": query_conditions
                })
                
                # 3. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 4. 验证响应
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                total = response_data.get("total", 0)
                assert total > 0, "查询结果总数为0"
                
                data_list = response_data.get("data", [])
                assert data_list, "查询结果为空"
                
                # 5. 验证数据匹配
                found_record = None
                for item in data_list:
                    if item.get("id") == TestPrCreateAndPayment.pr_info["pr_id"]:
                        found_record = item
                        break
                
                assert found_record, f"未找到付款申请单ID: {TestPrCreateAndPayment.pr_info['pr_id']}"
                
                # 6. 验证关键字段
                assert found_record.get("paymentRequestDocAmt") == TestPrCreateAndPayment.pr_info["payment_amount"], \
                    "付款申请金额不匹配"
                
                # 7. 更新测试数据，保存查询到的完整信息
                TestPrCreateAndPayment.pr_info.update({
                    "pr_head_code": found_record.get("prHeadCode"),
                    "pr_status": found_record.get("prStatus"),
                    "query_verified": True
                })
                
                # 8. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({
                    "total": total, 
                    "found": True, 
                    "data_count": len(data_list),
                    "pr_head_code": found_record.get("prHeadCode"),
                    "amount_verified": True
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单提交",
        title="付款申请单提交流程",
        description="验证付款申请单提交功能正确性（覆盖提交接口调用、状态变更及操作结果确认）",
        severity="blocker",
        order=3,
        tags=["付款申请单", "提交功能"]
    )
    def test_payment_request_submit(self):
        try:
            with a.step("付款申请单提交流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要提交的付款申请单ID，请先执行创建用例"
                assert TestPrCreateAndPayment.pr_info.get("pr_head_code"), "未获取到付款申请单编码，请先执行查询用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单提交和审批服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造提交数据
                submit_data = {
                    "id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "prHeadCode": TestPrCreateAndPayment.pr_info["pr_head_code"],
                    "prStatus": "SUBMITTED",
                    "comOrgId": {"id": TestPrCreateAndPayment.pr_info["com_org_id"]},
                    "purOrgId": {"id": TestPrCreateAndPayment.pr_info["pur_org_id"]},
                    "payOrgId": {"id": TestPrCreateAndPayment.pr_info["pay_org_id"]},
                    "paymentRequestDocAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "paymentRequestBaseAmt": TestPrCreateAndPayment.pr_info["payment_amount"]
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(submit_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, submit_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款申请单提交失败，单据编号: {TestPrCreateAndPayment.pr_info['pr_head_code']}"
                
                # 6. 更新状态
                TestPrCreateAndPayment.pr_info["pr_status"] = "SUBMITTED"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "submit", "success": success, "new_status": "SUBMITTED"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单过账",
        title="付款申请单过账流程",
        description="验证付款申请单过账功能正确性（使用PR_POST_ASYNC_EVENT_SERVICE接口）",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["付款申请单", "过账功能"]
    )
    def test_payment_request_post(self):
        try:
            with a.step("付款申请单过账流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要过账的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单-过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造过账数据
                post_data = {
                    "id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "prStatus": "DONE",
                    "paymentRequestDocAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "paymentRequestBaseAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "comOrgId": {"id": TestPrCreateAndPayment.pr_info["com_org_id"]},
                    "purOrgId": {"id": TestPrCreateAndPayment.pr_info["pur_org_id"]},
                    "payOrgId": {"id": TestPrCreateAndPayment.pr_info["pay_org_id"]},
                    "vendorCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "payerCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "docCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]},
                    "baseCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]}
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(post_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, post_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款申请单过账失败，单据ID: {TestPrCreateAndPayment.pr_info['pr_id']}"
                
                # 6. 更新状态
                TestPrCreateAndPayment.pr_info["pr_status"] = "DONE"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "post", "success": success, "new_status": "DONE"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单状态验证",
        title="付款申请单过账后状态轮询验证",
        description="通过分页查询轮询验证付款申请单状态为完成且异步执行状态为已成功",
        severity="critical",
        order=5,
        tags=["付款申请单", "状态验证", "轮询查询"]
    )
    def test_payment_request_status_verification_after_post(self):
        try:
            with a.step("付款申请单过账后状态轮询验证"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要验证的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 轮询查询付款申请单状态
                max_attempts = 15  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                
                for attempt in range(max_attempts):
                    # 构造查询条件
                    query_conditions = {
                        "conditionItems": {
                            "conditions": {
                                "id": {
                                    "operator": "EQ", 
                                    "value": TestPrCreateAndPayment.pr_info["pr_id"]
                                }
                            }
                        },
                        "sortOrders": None,
                        "pageSize": 20,
                        "pageIndex": 1
                    }
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["conditionItems", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, {
                        "pageable": query_conditions
                    })
                    
                    # 发送查询请求
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    response_data = result.get("data", {}).get("data", {})
                    data_list = response_data.get("data", [])
                    
                    if data_list:
                        found_record = data_list[0]  # 按ID查询应该只有一条记录
                        current_status = found_record.get("prStatus")
                        async_status = found_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 付款申请状态: {current_status}, 异步执行状态: {async_status}", "状态检查")
                        
                        # 验证状态是否符合预期
                        if current_status == "DONE" and async_status == "SUCCEEDED":
                            TestPrCreateAndPayment.pr_info.update({
                                "pr_status": current_status,
                                "async_status": async_status,
                                "status_verified": True
                            })
                            
                            a.json(filtered_params, "最终查询请求")
                            a.json(result, "最终查询响应")
                            a.json({
                                "expected_status": "DONE",
                                "actual_status": current_status,
                                "expected_async_status": "SUCCEEDED", 
                                "actual_async_status": async_status,
                                "verification_passed": True,
                                "attempts": attempt + 1
                            }, "状态验证结果")
                            
                            return  # 验证成功，退出
                        
                        elif async_status == "FAILED":
                            failure_reason = found_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"付款申请单异步执行失败: {failure_reason}")
                    
                    # 等待下次轮询
                    if attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款申请单状态更新")
                
                # 轮询超时
                raise Exception(f"轮询超时：付款申请单状态未变更为DONE且异步执行状态未变更为SUCCEEDED，最大等待{max_attempts * interval}秒")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单反过账",
        title="付款申请单反过账流程",
        description="验证付款申请单反过账功能正确性（使用PR_POST_ROLLBACK_EVENT_SERVICE接口）",
        severity="blocker",
        order=6,
        smoke=True,
        tags=["付款申请单", "反过账功能"]
    )
    def test_payment_request_post_rollback(self):
        try:
            with a.step("付款申请单反过账流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要反过账的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PR-付款申请反过账服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造反过账数据
                rollback_data = {
                    "id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "prStatus": "SUBMITTED",
                    "paymentRequestDocAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "paymentRequestBaseAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "comOrgId": {"id": TestPrCreateAndPayment.pr_info["com_org_id"]},
                    "purOrgId": {"id": TestPrCreateAndPayment.pr_info["pur_org_id"]},
                    "payOrgId": {"id": TestPrCreateAndPayment.pr_info["pay_org_id"]},
                    "vendorCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "payerCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "docCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]},
                    "baseCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]}
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(rollback_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, rollback_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款申请单反过账失败，单据ID: {TestPrCreateAndPayment.pr_info['pr_id']}"
                
                # 6. 更新状态
                TestPrCreateAndPayment.pr_info["pr_status"] = "SUBMITTED"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "post_rollback", "success": success, "new_status": "SUBMITTED"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单状态验证",
        title="付款申请单反过账后状态轮询验证",
        description="通过分页查询轮询验证付款申请单状态为草稿且异步执行状态为已成功",
        severity="critical",
        order=7,
        tags=["付款申请单", "状态验证", "轮询查询"]
    )
    def test_payment_request_status_verification_after_rollback(self):
        try:
            with a.step("付款申请单反过账后状态轮询验证"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要验证的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单头表-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 轮询查询付款申请单状态
                max_attempts = 15  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                
                for attempt in range(max_attempts):
                    # 构造查询条件
                    query_conditions = {
                        "conditionItems": {
                            "conditions": {
                                "id": {
                                    "operator": "EQ",
                                    "value": TestPrCreateAndPayment.pr_info["pr_id"]
                                }
                            }
                        },
                        "sortOrders": None,
                        "pageSize": 20,
                        "pageIndex": 1
                    }
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["conditionItems", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, {
                        "pageable": query_conditions
                    })
                    
                    # 发送查询请求
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    response_data = result.get("data", {}).get("data", {})
                    data_list = response_data.get("data", [])
                    
                    if data_list:
                        found_record = data_list[0]  # 按ID查询应该只有一条记录
                        current_status = found_record.get("prStatus")
                        async_status = found_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 付款申请状态: {current_status}, 异步执行状态: {async_status}", "状态检查")
                        
                        # 验证状态是否符合预期（反过账后状态为CONFIRM）
                        if current_status == "CONFIRM" and async_status == "SUCCEEDED":
                            TestPrCreateAndPayment.pr_info.update({
                                "pr_status": current_status,
                                "async_status": async_status,
                                "rollback_verified": True
                            })
                            
                            a.json(filtered_params, "最终查询请求")
                            a.json(result, "最终查询响应")
                            a.json({
                                "expected_status": "CONFIRM",
                                "actual_status": current_status,
                                "expected_async_status": "SUCCEEDED",
                                "actual_async_status": async_status,
                                "verification_passed": True,
                                "attempts": attempt + 1
                            }, "状态验证结果")
                            
                            return  # 验证成功，退出
                        
                        elif async_status == "FAILED":
                            failure_reason = found_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"付款申请单异步执行失败: {failure_reason}")
                    
                    # 等待下次轮询
                    if attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款申请单状态更新")
                
                # 轮询超时
                raise Exception(f"轮询超时：付款申请单状态未变更为CONFIRM且异步执行状态未变更为SUCCEEDED，最大等待{max_attempts * interval}秒")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单撤回",
        title="付款申请单撤回流程",
        description="验证付款申请单撤回功能正确性（使用PR_SUBMIT_ROLLBACK_EVENT_SERVICE接口）",
        severity="blocker",
        order=8,
        smoke=True,
        tags=["付款申请单", "撤回功能"]
    )
    def test_payment_request_submit_rollback(self):
        try:
            with a.step("付款申请单撤回流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要撤回的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PR-付款申请撤回服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造撤回数据
                rollback_data = {
                    "id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "prStatus": "CONFIRM",
                    "paymentRequestDocAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "paymentRequestBaseAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "comOrgId": {"id": TestPrCreateAndPayment.pr_info["com_org_id"]},
                    "purOrgId": {"id": TestPrCreateAndPayment.pr_info["pur_org_id"]},
                    "payOrgId": {"id": TestPrCreateAndPayment.pr_info["pay_org_id"]},
                    "vendorCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "payerCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "docCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]},
                    "baseCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]}
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(rollback_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, rollback_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款申请单撤回失败，单据ID: {TestPrCreateAndPayment.pr_info['pr_id']}"
                
                # 6. 验证状态已变更为草稿
                response_data = result.get("data", {}).get("data", {})
                if response_data:
                    actual_status = response_data.get("prStatus")
                    assert actual_status == "CONFIRM", f"撤回后状态错误，期望: CONFIRM, 实际: {actual_status}"
                
                # 7. 更新状态
                TestPrCreateAndPayment.pr_info["pr_status"] = "CONFIRM"
                
                # 8. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({
                    "operation": "submit_rollback", 
                    "success": success, 
                    "new_status": "CONFIRM",
                    "status_verified": actual_status == "CONFIRM" if response_data else False
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款申请单删除",
        title="付款申请单删除流程",
        description="验证付款申请单删除功能正确性（使用PR_DELETE_SERVICE接口）",
        severity="blocker",
        order=9,
        smoke=True,
        tags=["付款申请单", "删除功能"]
    )
    def test_payment_request_delete(self):
        try:
            with a.step("付款申请单删除流程"):
                assert TestPrCreateAndPayment.pr_info.get("pr_id"), "未找到要删除的付款申请单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款申请单-删除服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造删除数据
                delete_data = {
                    "id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "prStatus": "CONFIRM",
                    "paymentRequestDocAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "paymentRequestBaseAmt": TestPrCreateAndPayment.pr_info["payment_amount"],
                    "comOrgId": {"id": TestPrCreateAndPayment.pr_info["com_org_id"]},
                    "purOrgId": {"id": TestPrCreateAndPayment.pr_info["pur_org_id"]},
                    "payOrgId": {"id": TestPrCreateAndPayment.pr_info["pay_org_id"]},
                    "vendorCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "payerCode": {"id": TestPrCreateAndPayment.pr_info["vendor_id"]},
                    "docCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]},
                    "baseCurrId": {"id": TestPrCreateAndPayment.pr_info["currency_id"]}
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(delete_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, delete_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款申请单删除失败，单据ID: {TestPrCreateAndPayment.pr_info['pr_id']}"
                
                # 6. 标记为已删除
                TestPrCreateAndPayment.pr_info["deleted"] = True
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pr_info['pr_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({
                    "operation": "delete", 
                    "success": success,
                    "pr_id": TestPrCreateAndPayment.pr_info["pr_id"],
                    "deleted": True
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单管理",
        title="手动创建付款单",
        description="使用PN_SAVE_EVENT_SERVICE接口手动创建付款单，验证创建成功",
        severity="critical",
        order=10,
        tags=["付款单", "创建", "手动创建"]
    )
    def test_payment_note_create(self):
        try:
            with a.step("手动创建付款单"):
                # 1. 获取基础数据
                base_data = self.ap_factory.get_base_data_for_fin_doc("AP")
                
                # 2. 构建付款单数据（基于真实入参优化）
                pn_date = int(datetime.now().timestamp() * 1000)
                pn_amount = 8240  # 付款金额
                
                pn_request_data = {
                    "pnClass": "PAY",
                    "docTypeId": {
                        "id": 2003002,
                        "pnTypeCode": "FK002",
                        "pnClass": "PAYMENT",
                        "name": "标准采购预付",
                        "isAccDocRelv": "YES",
                        "businessType": "PUR_SLS",
                        "isAdvanceRelv": False,
                        "exchangeRateType": {"id": 2000001},
                        "pushAes": True,
                        "autoPushAes": False
                    },
                    "comOrgId": {"id": base_data["com_org"]["id"]},
                    "purSlsOrgId": {"id": base_data["pur_org"]["id"]},
                    "payRecOrgId": {"id": base_data["com_org"]["id"]},
                    "tradingPartnerId": {"id": base_data["vend"]["id"]},
                    "payerId": {"id": base_data["vend"]["id"]},
                    "pnDate": pn_date,
                    "currId": {"id": base_data["currency"]["id"]},
                    "baseCurrId": {"id": base_data["currency"]["id"]},
                    "exchRate": 1,
                    "pnStatus": None,
                    "clearingStatus": None,
                    "pnItems": [{
                        "arApDocAmt": pn_amount,
                        "cashDiscountDocAmt": 0,
                        "transactionFeeDocAmt": 0,
                        "collectedPaidDocAmt": pn_amount,
                        "arApBaseAmt": pn_amount,
                        "cashDiscountBaseAmt": 0,
                        "transactionFeeBaseAmt": 0,
                        "collectedPaidBaseAmt": pn_amount,
                        "unclearedDocAmt": pn_amount,
                        "settlementMethodCode": {"id": base_data["settlement_method"]["id"]}
                    }],
                    "pnLinks": None,
                    "arApDocAmt": None,
                    "collectedPaidDocAmt": None,
                    "arApBaseAmt": None,
                    "collectedPaidBaseAmt": None
                }
                
                # 3. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PN-收付款保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 4. 构造请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(pn_request_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, pn_request_data)
                
                # 5. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 6. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 7. 验证响应
                self.assert_util.assert_response_success(result)
                
                # 从正确的路径获取付款单ID: result["data"]["data"]["id"]
                response_data = result.get("data", {}).get("data", {})
                pn_id = response_data.get("id")
                assert pn_id, "付款单创建失败，未返回ID"
                
                # 8. 保存付款单信息供后续用例使用
                TestPrCreateAndPayment.pn_info = {
                    "pn_id": pn_id,
                    "pn_amount": pn_amount,
                    "com_org_id": base_data["com_org"]["id"],
                    "pur_org_id": base_data["pur_org"]["id"],
                    "pay_org_id": base_data["com_org"]["id"],
                    "vendor_id": base_data["vend"]["id"],
                    "currency_id": base_data["currency"]["id"],
                    "settlement_method_id": base_data["settlement_method"]["id"],
                    "doc_type_id": pn_request_data["docTypeId"]["id"],  # 保存单据类型ID用于删除
                    "pn_status": "DRAFT"
                }
                
                # 9. 添加 allure 附件
                a.text(f"付款单ID: {pn_id}", "创建结果")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestPrCreateAndPayment.pn_info, "保存的付款单信息")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单管理",
        title="付款单提交",
        description="使用PN_SUBMIT_WITH_HEAD_EVENT_SERVICE接口提交付款单，验证提交成功",
        severity="critical",
        order=11,
        tags=["付款单", "提交"]
    )
    def test_payment_note_submit(self):
        try:
            with a.step("付款单提交"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要提交的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PN-收付款-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造提交数据
                submit_data = {
                    "id": TestPrCreateAndPayment.pn_info["pn_id"]
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(submit_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, submit_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款单提交失败，单据ID: {TestPrCreateAndPayment.pn_info['pn_id']}"
                
                # 6. 更新状态
                TestPrCreateAndPayment.pn_info["pn_status"] = "CONFIRM"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pn_info['pn_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "submit", "success": success, "new_status": "CONFIRM"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单管理",
        title="付款单过账",
        description="使用PCC_PN_PAY_POST_ASYNC_EVENT_SERVICE接口过账付款单，验证过账成功",
        severity="critical",
        order=12,
        tags=["付款单", "过账"]
    )
    def test_payment_note_post(self):
        try:
            with a.step("付款单过账"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要过账的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款单过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造过账数据
                post_data = {
                    "id": TestPrCreateAndPayment.pn_info["pn_id"]
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(post_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, post_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款单过账失败，单据ID: {TestPrCreateAndPayment.pn_info['pn_id']}"
                
                # 6. 更新状态
                TestPrCreateAndPayment.pn_info["pn_status"] = "DONE"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pn_info['pn_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "post", "success": success, "new_status": "DONE"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单状态验证",
        title="付款单过账后状态轮询验证",
        description="通过分页查询轮询验证付款单状态为完成且异步执行状态为已成功",
        severity="critical",
        order=13,
        tags=["付款单", "状态验证", "轮询查询"]
    )
    def test_payment_note_status_verification_after_post(self):
        try:
            with a.step("付款单过账后状态轮询验证"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要验证的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 轮询查询付款单状态
                max_attempts = 15  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                
                for attempt in range(max_attempts):
                    # 构造查询条件
                    query_conditions = {
                        "conditionItems": {
                            "conditions": {
                                "id": {
                                    "operator": "EQ",
                                    "value": TestPrCreateAndPayment.pn_info["pn_id"]
                                }
                            }
                        },
                        "sortOrders": None,
                        "pageSize": 20,
                        "pageIndex": 1
                    }
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["conditionItems", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, {
                        "pageable": query_conditions
                    })
                    
                    # 发送查询请求
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    response_data = result.get("data", {}).get("data", {})
                    data_list = response_data.get("data", [])
                    
                    if data_list:
                        found_record = data_list[0]  # 按ID查询应该只有一条记录
                        current_status = found_record.get("pnStatus")
                        async_status = found_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 付款单状态: {current_status}, 异步执行状态: {async_status}", "状态检查")
                        
                        # 验证状态是否符合预期
                        if current_status == "DONE" and async_status == "SUCCEEDED":
                            TestPrCreateAndPayment.pn_info.update({
                                "pn_status": current_status,
                                "async_status": async_status,
                                "status_verified": True
                            })
                            
                            a.json(filtered_params, "最终查询请求")
                            a.json(result, "最终查询响应")
                            a.json({
                                "expected_status": "DONE",
                                "actual_status": current_status,
                                "expected_async_status": "SUCCEEDED",
                                "actual_async_status": async_status,
                                "verification_passed": True,
                                "attempts": attempt + 1
                            }, "状态验证结果")
                            
                            return  # 验证成功，退出
                        
                        elif async_status == "FAILED":
                            failure_reason = found_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"付款单异步执行失败: {failure_reason}")
                    
                    # 等待下次轮询
                    if attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款单状态更新")
                
                # 轮询超时
                raise Exception(f"轮询超时：付款单状态未变更为DONE且异步执行状态未变更为SUCCEEDED，最大等待{max_attempts * interval}秒")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单管理",
        title="付款单反过账",
        description="使用PCC_PN_PAY_CLEAR_ROLLBACK_ASYNC_SERVICE接口反过账付款单，验证反过账成功",
        severity="critical",
        order=14,
        tags=["付款单", "反过账"]
    )
    def test_payment_note_post_rollback(self):
        try:
            with a.step("付款单反过账"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要反过账的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "付款单-反过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造反过账数据
                rollback_data = {
                    "id": TestPrCreateAndPayment.pn_info["pn_id"]
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(rollback_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, rollback_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款单反过账失败，单据ID: {TestPrCreateAndPayment.pn_info['pn_id']}"
                
                # 6. 更新状态（反过账后状态应该变为草稿）
                TestPrCreateAndPayment.pn_info["pn_status"] = "DRAFT"
                
                # 7. 添加 allure 附件
                a.text(f"预置数据: {TestPrCreateAndPayment.pn_info['pn_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "post_rollback", "success": success, "new_status": "DRAFT"}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单状态验证",
        title="付款单反过账后状态轮询验证",
        description="通过分页查询轮询验证付款单状态为草稿且异步执行状态为已成功",
        severity="critical",
        order=15,
        tags=["付款单", "状态验证", "轮询查询"]
    )
    def test_payment_note_status_verification_after_rollback(self):
        try:
            with a.step("付款单反过账后状态轮询验证"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要验证的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 轮询查询付款单状态
                max_attempts = 15  # 最大轮询次数
                interval = 2  # 轮询间隔（秒）
                
                for attempt in range(max_attempts):
                    # 构造查询条件
                    query_conditions = {
                        "conditionItems": {
                            "conditions": {
                                "id": {
                                    "operator": "EQ",
                                    "value": TestPrCreateAndPayment.pn_info["pn_id"]
                                }
                            }
                        },
                        "sortOrders": None,
                        "pageSize": 20,
                        "pageIndex": 1
                    }
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["conditionItems", "pageable"], ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, {
                        "pageable": query_conditions
                    })
                    
                    # 发送查询请求
                    result, _ = self.standard_api_call(
                        api_key=self.apis,
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_success(result)
                    
                    response_data = result.get("data", {}).get("data", {})
                    data_list = response_data.get("data", [])
                    
                    if data_list:
                        found_record = data_list[0]  # 按ID查询应该只有一条记录
                        current_status = found_record.get("pnStatus")
                        async_status = found_record.get("asyncExecutionStatus")
                        
                        a.text(f"第{attempt + 1}次查询 - 付款单状态: {current_status}, 异步执行状态: {async_status}", "状态检查")
                        
                        # 验证状态是否符合预期（反过账后应为草稿态）
                        if current_status == "DRAFT" and async_status == "SUCCEEDED":
                            TestPrCreateAndPayment.pn_info.update({
                                "pn_status": current_status,
                                "async_status": async_status,
                                "status_verified_after_rollback": True
                            })
                            
                            a.json(filtered_params, "最终查询请求")
                            a.json(result, "最终查询响应")
                            a.json({
                                "expected_status": "DRAFT",
                                "actual_status": current_status,
                                "expected_async_status": "SUCCEEDED",
                                "actual_async_status": async_status,
                                "verification_passed": True,
                                "attempts": attempt + 1
                            }, "状态验证结果")
                            
                            return  # 验证成功，退出
                        
                        elif async_status == "FAILED":
                            failure_reason = found_record.get("asyncExecutionFailureReason", "未知原因")
                            raise Exception(f"付款单异步执行失败: {failure_reason}")
                    
                    # 等待下次轮询
                    if attempt < max_attempts - 1:
                        self._async_delay(interval, reason="等待付款单状态更新")
                
                # 轮询超时
                raise Exception(f"轮询超时：付款单状态未变更为DRAFT且异步执行状态未变更为SUCCEEDED，最大等待{max_attempts * interval}秒")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="付款单管理",
        title="付款单删除",
        description="使用PN_DELETE_EVENT_SERVICE接口删除付款单，验证删除成功",
        severity="critical",
        order=16,
        tags=["付款单", "删除"]
    )
    def test_payment_note_delete(self):
        try:
            with a.step("付款单删除"):
                assert TestPrCreateAndPayment.pn_info.get("pn_id"), "未找到要删除的付款单ID，请先执行创建用例"
                
                # 1. 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "PN-收付款删除服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 2. 构造删除数据（根据页面真实入参格式）
                # 首先查询当前付款单的完整信息
                query_api_path = ParamUtil.get_api_path(self.apis, "收付款单头表-分页数据服务")
                query_params, query_url = ParamUtil.get_api_params(self.api_params, query_api_path)
                
                query_conditions = {
                    "conditionItems": {
                        "conditions": {
                            "id": {
                                "operator": "EQ",
                                "value": TestPrCreateAndPayment.pn_info["pn_id"]
                            }
                        }
                    },
                    "sortOrders": None,
                    "pageSize": 20,
                    "pageIndex": 1
                }
                
                query_filtered_params = ParamUtil.filter_post_body_fields(
                    query_params, ["conditionItems", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(query_filtered_params, {
                    "pageable": query_conditions
                })
                
                query_result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=query_filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(query_result)
                
                query_response_data = query_result.get("data", {}).get("data", {})
                data_list = query_response_data.get("data", [])
                assert data_list, "查询付款单信息失败，无法获取删除所需的完整数据"
                
                current_pn = data_list[0]  # 获取当前付款单完整信息
                
                # 根据页面真实入参构造删除数据
                delete_data = {
                    "pnHeadCode": current_pn.get("pnHeadCode"),
                    "pnClass": "PAY",
                    "docTypeId": {
                        "pnTypeCode": "FK002",
                        "name": "标准采购预付",
                        "pushAes": True,
                        "id": TestPrCreateAndPayment.pn_info["doc_type_id"]
                    },
                    "pnStatus": current_pn.get("pnStatus"),
                    "pnDate": current_pn.get("pnDate"),
                    "tradingPartnerName": current_pn.get("tradingPartnerName"),
                    "createType": "MANUAL",
                    "comOrgId": {
                        "orgName": "公司组织(自动化)",
                        "id": TestPrCreateAndPayment.pn_info["com_org_id"]
                    },
                    "purSlsOrgName": current_pn.get("purSlsOrgName"),
                    "currId": {
                        "currName": "人民币",
                        "id": TestPrCreateAndPayment.pn_info["currency_id"]
                    },
                    "baseCurrId": {
                        "currName": "人民币",
                        "id": TestPrCreateAndPayment.pn_info["currency_id"]
                    },
                    "arApDocAmt": current_pn.get("arApDocAmt"),
                    "collectedPaidDocAmt": current_pn.get("collectedPaidDocAmt"),
                    "arApBaseAmt": current_pn.get("arApBaseAmt"),
                    "collectedPaidBaseAmt": current_pn.get("collectedPaidBaseAmt"),
                    "exchRate": current_pn.get("exchRate"),
                    "clearedDocAmt": current_pn.get("clearedDocAmt", 0),
                    "unclearedDocAmt": current_pn.get("unclearedDocAmt"),
                    "clearedBaseAmt": current_pn.get("clearedBaseAmt", 0),
                    "unclearedBaseAmt": current_pn.get("unclearedBaseAmt"),
                    "offsetDocAmt": current_pn.get("offsetDocAmt", 0),
                    "unoffsetDocAmt": current_pn.get("unoffsetDocAmt", 0),
                    "offsetBaseAmt": current_pn.get("offsetBaseAmt", 0),
                    "unoffsetBaseAmt": current_pn.get("unoffsetBaseAmt", 0),
                    "headOffsetStatus": current_pn.get("headOffsetStatus"),
                    "clearingStatus": current_pn.get("clearingStatus"),
                    "relatedCreated": current_pn.get("relatedCreated"),
                    "clearingDocAmt": current_pn.get("clearingDocAmt", 0),
                    "clearingBaseAmt": current_pn.get("clearingBaseAmt", 0),
                    "confirmStatus": current_pn.get("confirmStatus"),
                    "asyncExecutionStatus": current_pn.get("asyncExecutionStatus"),
                    "asyncExecutionFailureReason": current_pn.get("asyncExecutionFailureReason", ""),
                    "id": TestPrCreateAndPayment.pn_info["pn_id"]
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(delete_data.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, delete_data)
                
                # 3. 转换数据类型
                filtered_params = self.convert_data_for_json(filtered_params)
                
                # 4. 发送请求
                result, _ = self.standard_api_call(
                    api_key=self.apis,
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 5. 验证响应（只判断success字段）
                self.assert_util.assert_response_success(result)
                
                success = result.get("success", False)
                assert success, f"付款单删除失败，单据ID: {TestPrCreateAndPayment.pn_info['pn_id']}"
                
                # 6. 清空付款单信息
                TestPrCreateAndPayment.pn_info = {}
                
                # 7. 添加 allure 附件
                a.text(f"已删除付款单ID: {delete_data['id']}", "删除结果")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "delete", "success": success, "pn_info_cleared": True}, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrCreateAndPayment()
    test.setup_class()
    test.test_payment_request_create()                              # 1. 创建付款申请单
    test.test_payment_request_query()                               # 2. 查询付款申请单
    test.test_payment_request_submit()                              # 3. 提交付款申请单
    test.test_payment_request_post()                                # 4. 过账付款申请单  
    test.test_payment_request_status_verification_after_post()      # 5. 验证过账后状态
    test.test_payment_request_post_rollback()                       # 6. 反过账付款申请单
    test.test_payment_request_status_verification_after_rollback()  # 7. 验证反过账后状态
    test.test_payment_request_submit_rollback()                     # 8. 撤回付款申请单
    test.test_payment_request_delete()                              # 9. 删除付款申请单
    test.test_payment_note_create()                                     # 10. 创建付款单
    test.test_payment_note_submit()                                     # 11. 提交付款单
    test.test_payment_note_post()                                       # 12. 过账付款单
    test.test_payment_note_status_verification_after_post()             # 13. 验证过账后状态
    test.test_payment_note_post_rollback()                              # 14. 反过账付款单
    test.test_payment_note_status_verification_after_rollback()         # 15. 验证反过账后状态
    test.test_payment_note_delete()                                     # 16. 删除付款单 
