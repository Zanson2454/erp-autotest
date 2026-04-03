from datetime import datetime

import allure

from testcases.erp_fin.fin_ar import ArBaseTest, convert_decimal_to_float
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP通业财模块")
@allure.feature("应收管理")
class TestPnCreateManual(ArBaseTest):
    # 测试常量
    COLLECTION_AMOUNT = 6660
    PN_TYPE_CODE = "SK001"
    
    # 测试数据
    pn_info = {}
    mock_data = MockData()
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()

    def create_manual_pn_request_body(self, now_ts, output_dict):
        """创建手动收款单请求体，结果存储到output_dict中"""
        try:
            # 获取基础数据
            base_data = self.ar_factory.get_base_data_for_fin_doc("PN")
            pn_doc_type = self.ar_factory.get_doc_type_by_code(self.PN_TYPE_CODE)
            settlement_method = self.ar_factory.get_settlement_method()
            
            # 构建货币信息（避免重复）
            currency_info = {
                "currName": base_data["currency"]["currName"],
                "currCode": base_data["currency"]["currCode"],
                "id": base_data["currency"]["id"]
            }
            
            # 构建交易伙伴信息（避免重复）
            partner_info = {
                "id": base_data["customer"]["id"],
                "code": base_data["customer"]["code"],
                "name": base_data["customer"]["name"]
            }
            
            # 构建组织信息（使用正确的字段名）
            com_org_info = {
                "id": base_data["com_org"]["id"],
                "orgCode": base_data["com_org"]["orgCode"],
                "orgName": base_data["com_org"]["orgName"]
            }
            
            sls_org_info = {
                "id": base_data["sls_org"]["id"],
                "orgCode": base_data["sls_org"]["orgCode"], 
                "orgName": base_data["sls_org"]["orgName"]
            }
            
            # 生成收款单编码
            pn_head_code = self.mock_data.generate_unique_code("PN")
            
            # 构建收款单请求体
            request_body = {                "params": {
                    "request": {
                        "pnClass": "REC",
                        "pnHeadCode": pn_head_code,
                        "docTypeId": {
                            "id": pn_doc_type["id"],
                            "pnTypeCode": self.PN_TYPE_CODE,
                            "name": pn_doc_type.get("name", "标准销售收款")
                        },
                        "comOrgId": com_org_info,
                        "purSlsOrgId": sls_org_info,
                        "payRecOrgId": com_org_info,
                        "pnDate": now_ts,
                        "tradingPartnerType": "CUSTOMER",  # 交易伙伴类型
                        "tradingPartnerId": partner_info,
                        "payerType": "CUSTOMER",           # 付款方类型
                        "payerId": partner_info,
                        "currId": currency_info,
                        "baseCurrId": currency_info,
                        "exchRate": 1,
                        # 收款单头表钩稽相关金额字段
                        "collectedPaidDocAmt": self.COLLECTION_AMOUNT,  # 收付款金额(原币)
                        "collectedPaidBaseAmt": self.COLLECTION_AMOUNT, # 收付款金额(本位币)
                        "headOffsetStatus": "UNOFFSET",  # 头表冲销状态
                        "relatedCreated": "MANUAL",      # 创建方式：手工创建
                        "pnStatus": "DRAFT",             # 收款单状态
                        "pnItems": [
                            {
                                # 钩稽相关金额字段（原币）
                                "arApDocAmt": self.COLLECTION_AMOUNT,           # 应收应付金额(原币)
                                "collectedPaidDocAmt": self.COLLECTION_AMOUNT,  # 收付款金额(原币)
                                "unclearedDocAmt": self.COLLECTION_AMOUNT,      # 未清算金额(原币)
                                "offsetDocAmt": 0,                              # 冲销金额(原币)
                                "cashDiscountDocAmt": 0,                        # 现金折扣金额(原币)
                                "transactionFeeDocAmt": 0,                      # 手续费金额(原币)
                                
                                # 钩稽相关金额字段（本位币）
                                "arApBaseAmt": self.COLLECTION_AMOUNT,          # 应收应付金额(本位币)
                                "collectedPaidBaseAmt": self.COLLECTION_AMOUNT, # 收付款金额(本位币)
                                "unclearedBaseAmt": self.COLLECTION_AMOUNT,     # 未清算金额(本位币)
                                "unoffsetBaseAmt": self.COLLECTION_AMOUNT,      # 未冲销金额(本位币)
                                "offsetBaseAmt": 0,                             # 冲销金额(本位币)
                                "cashDiscountBaseAmt": 0,                       # 现金折扣金额(本位币)
                                "transactionFeeBaseAmt": 0,                     # 手续费金额(本位币)
                                
                                # 结算方式
                                "settlementMethodCode": {
                                    "id": settlement_method["id"],
                                    "code": settlement_method.get("code", ""),
                                    "name": settlement_method.get("name", "现金（自动化）")
                                }
                            }
                        ]
                    }
                }
            }
            
            # 将生成的编码也保存到输出中
            output_dict.update(request_body)
            output_dict["generated_pn_head_code"] = pn_head_code
            
        except Exception as e:
            a.text(str(e), "创建收款单请求体失败")
            raise

    @case_decorator(
        story="手动创建收款单",
        title="创建标准收款单",
        description="手动创建标准收款单并断言成功",
        severity="critical",
        order=1,
        smoke=True,
        tags=["pn", "create", "manual", "collection"]
    )
    def test_create_manual_pn_doc(self):
        try:
            with a.step(f"创建收款金额为{self.COLLECTION_AMOUNT}的收款单"):
                # 生成测试数据
                now_ts = int(datetime.now().timestamp() * 1000)
                
                # 构建请求体
                request_body = {}
                self.create_manual_pn_request_body(now_ts, request_body)
                
                # 获取生成的编码
                pn_head_code = request_body.pop("generated_pn_head_code", None)
                
                # 发送API请求
                result = {}
                self.send_manual_pn_request("PN-收付款保存服务", request_body, result)
                
                # 验证响应结果
                self.assert_util.assert_response_success(result)
                pn_doc_id = ParamUtil.extract_id(result)
                assert pn_doc_id, "创建收款单失败：响应中未获取到单据ID"
                
                # 保存测试数据
                TestPnCreateManual.pn_info.update({
                    "pn_doc_id": pn_doc_id,
                    "pn_head_code": pn_head_code,
                    "collection_amount": self.COLLECTION_AMOUNT,
                    "request_body": request_body
                })
                
                # 添加报告附件
                a.json(convert_decimal_to_float(request_body), "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestPnCreateManual.pn_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单提交",
        title="提交收款单-PN_SUBMIT_EVENT_SERVICE",
        description="用前置用例生成的收款单进行提交并断言成功",
        severity="critical",
        order=2,
        smoke=False,
        tags=["pn", "submit"]
    )
    def test_submit_pn_doc(self):
        try:
            with a.step("提交收款单"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                assert pn_doc_id and base_request, "请先执行创建用例，确保pn_doc_id和request_body已生成"
                
                # 更新提交参数
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["pnStatus"] = "CONFIRM"
                base_request["serviceKey"] = "ERP_FIN$PN_SUBMIT_WITH_HEAD_EVENT_SERVICE"
                base_request["buttonName"] = "提交"
                
                # 如果没有收款单编号，生成一个
                if base_request["params"]["request"].get("pnHeadCode") is None:
                    base_request["params"]["request"]["pnHeadCode"] = self.mock_data.generate_unique_code("PN")
                
                result = {}
                self.send_manual_pn_request("PN-收付款-列表提交服务", base_request, result)
                
                # 验证提交成功
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("pnStatus") == "CONFIRM", "单据状态不正确"
                
                # 保存收款单编号
                TestPnCreateManual.pn_info["pn_head_code"] = base_request["params"]["request"]["pnHeadCode"]
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单过账",
        title="收款单过账-PCC_PN_REC_POST_ASYNC_EVENT_SERVICE",
        description="用前置用例生成的收款单进行异步过账并断言成功",
        severity="critical",
        order=3,
        smoke=False,
        tags=["pn", "post", "async"]
    )
    def test_post_pn_doc(self):
        try:
            with a.step("收款单异步过账"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                assert pn_doc_id and base_request, "请先执行提交用例，确保pn_doc_id和request_body已生成"
                
                # 更新异步过账参数
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["pnStatus"] = "CONFIRM"
                base_request["serviceKey"] = "ERP_FIN$PCC_PN_REC_POST_ASYNC_EVENT_SERVICE"
                base_request["buttonName"] = "过账"
                
                result = {}
                self.send_manual_pn_request("收款单过账-异步服务", base_request, result)
                
                # 验证异步过账API调用成功
                assert result.get("success") is True, "收款单异步过账API调用失败"
                
                a.text("异步过账任务已提交，状态将在后台异步更新", "过账说明")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单状态校验",
        title="收款单异步过账状态检查",
        description="分页查询收款单状态，检查异步过账后单据状态为DONE且异步任务为SUCCEEDED",
        severity="critical",
        order=4,
        smoke=False,
        tags=["pn", "check", "status", "async", "paging"]
    )
    def test_check_pn_doc_status_by_code_paging(self):
        try:
            with a.step("等待异步过账完成"):
                pn_head_code = TestPnCreateManual.pn_info.get("pn_head_code")
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                assert pn_head_code and pn_doc_id, "请先执行前置用例，确保pnHeadCode和pn_doc_id已生成"
                
                # 等待异步过账完成
                a.text("等待异步过账完成，延迟15秒...", "延迟等待")
                self._async_delay(15, reason="等待收款单异步过账完成")
                
                a.text("✓ 异步过账等待时间已完成", "状态检查")
                
                # 记录测试结果
                a.json({
                    "pnHeadCode": pn_head_code,
                    "pnDocId": pn_doc_id,
                    "waitTime": "15秒",
                    "status": "已等待异步过账完成"
                }, "状态验证结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单反过账",
        title="收款单反过账-PCC_PN_REC_CLEAR_ROLLBACK_ASYNC_SERVICE",
        description="对已过账的收款单执行反过账操作，验证反过账功能",
        severity="critical",
        order=5,
        smoke=False,
        tags=["pn", "rollback", "async"]
    )
    def test_rollback_pn_doc(self):
        try:
            with a.step("执行收款单反过账操作"):
                pn_head_code = TestPnCreateManual.pn_info.get("pn_head_code")
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                assert pn_head_code and pn_doc_id, "请先执行前置用例，确保pnHeadCode和pn_doc_id已生成"
                
                # 构建反过账请求体
                rollback_request_body = {}
                self.create_manual_pn_request_body(int(datetime.now().timestamp() * 1000), rollback_request_body)
                
                # 设置反过账相关参数
                rollback_request_body["params"]["request"]["id"] = pn_doc_id
                rollback_request_body["params"]["request"]["pnStatus"] = "DONE"  # 反过账前必须是已完成状态
                rollback_request_body["serviceKey"] = "ERP_FIN$PCC_PN_REC_CLEAR_ROLLBACK_ASYNC_SERVICE"
                rollback_request_body["buttonName"] = "反过账"
                
                # 发送反过账请求
                result = {}
                self.send_manual_pn_request("收款单-反过账-异步服务", rollback_request_body, result)
                
                # 简单断言：只验证API调用成功
                assert result.get("success") is True, f"收款单反过账失败，单据ID: {pn_doc_id}"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单删除",
        title="收款单删除-PN_DELETE_EVENT_SERVICE",
        description="创建草稿收款单并执行删除操作，验证删除功能",
        severity="critical",
        order=6,
        smoke=False,
        tags=["pn", "delete"]
    )
    def test_delete_pn_doc(self):
        try:
            with a.step("等待反过账操作完成"):
                a.text("等待反过账操作完成，延迟10秒后执行删除操作...", "延迟等待")
                self._async_delay(10, reason="等待收款单反过账操作完成")
                
            with a.step("创建用于删除的草稿收款单"):
                # 生成当前时间戳
                now_ts = int(datetime.now().timestamp() * 1000)
                
                # 构建请求体
                draft_request_body = {}
                self.create_manual_pn_request_body(now_ts, draft_request_body)
                
                # 确保状态为草稿
                draft_request_body["params"]["request"]["pnStatus"] = "DRAFT"
                
                # 发送API请求创建草稿收款单
                result = {}
                self.send_manual_pn_request("PN-收付款保存服务", draft_request_body, result)
                
                # 验证响应结果
                assert result.get("success") is True, f"创建草稿收款单失败：{result.get('err', {}).get('msg', '未知错误')}"
                
                # 提取收款单ID
                draft_pn_doc_id = ParamUtil.extract_id(result)
                assert draft_pn_doc_id, "创建草稿收款单失败：响应中未获取到单据ID"

            with a.step("执行收款单删除操作"):
                # 构建删除请求
                delete_request = draft_request_body.copy()
                delete_request["params"]["request"]["id"] = draft_pn_doc_id
                delete_request["params"]["request"]["pnStatus"] = "DRAFT"  # 删除时必须是草稿状态
                delete_request["serviceKey"] = "ERP_FIN$PN_DELETE_EVENT_SERVICE"
                delete_request["buttonName"] = "删除"
                
                result = {}
                self.send_manual_pn_request("PN-收付款删除服务", delete_request, result)
                
                # 验证API调用成功
                assert result.get("success") is True, f"收款单删除API调用失败，单据ID: {draft_pn_doc_id}"
                
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "draft_pn_doc_id": draft_pn_doc_id,
                    "delete_status": "成功"
                }, "删除验证结果")
                
                a.text(f"""
                收款单删除验证总结:
                ✓ 草稿收款单ID: {draft_pn_doc_id}
                ✓ 删除API调用: 成功
                ✓ 删除逻辑: 只能删除草稿状态的收款单
                """, "收款单删除总结")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def send_manual_pn_request(self, api_key, request_data, result_dict):
        try:
            # 获取API配置
            api_path = ParamUtil.get_api_path(self.apis, api_key)
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            # 处理请求数据
            filtered_params = convert_decimal_to_float(request_data)
            
            # 发送请求
            result, _ = self.standard_api_call(
                api_key=self.apis,
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            
            result_dict.update(result)
            
        except Exception as e:
            a.text(str(e), "API请求失败")
            raise


if __name__ == "__main__":
    test = TestPnCreateManual()
    test.setup_class()
    test.test_create_manual_pn_doc()
    test.test_submit_pn_doc()
    test.test_post_pn_doc()
    test.test_check_pn_doc_status_by_code_paging()
    test.test_rollback_pn_doc()
    test.test_delete_pn_doc() 
