"""
手动创建收款单自动化测试用例
覆盖收款单创建、提交、过账等场景
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
class TestPnCreateManual(ArBaseTest):
    """手动创建收款单自动化用例"""
    pn_info = {}
    mock_data = MockData()
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()

    def create_manual_pn_request_body(self, now_ts, output_dict):
        """创建手动收款单请求体，结果存储到output_dict中"""
        try:
            # 获取基础数据
            base_data = self.ar_factory.get_base_data_for_fin_doc("PN")
            
            # 获取收款单类型
            pn_doc_type = self.ar_factory.get_doc_type_by_code("SK001")
            
            # 获取结算方式
            settlement_method = self.ar_factory.get_settlement_method()
            
            # 收款金额
            collection_amount = 6660
            
            # 构建收款单请求体
            request_body = {
                "sceneKey": "ERP_FIN$FIN_CM_PN_REC",
                "viewKey": "ERP_FIN$FIN_CM_PN_REC:edit",
                "viewTitle": "edit",
                "buttonKey": "TERP_MIGRATE$FIN_CM_PN_REC-editView-footer-save",
                "buttonName": "提交",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "ERP_FIN$PN_SAVE_EVENT_SERVICE",
                "params": {
                    "request": {
                        "pnClass": "REC",
                        "docTypeId": {
                            "pnTypeCode": "SK001",
                            "pnClass": "COLLECTION",
                            "name": "标准销售收款",
                            "isAccDocRelv": "YES",
                            "businessType": "PUR_SLS",
                            "isAdvanceRelv": False,
                            "exchangeRateType": {
                                "id": base_data["currency"]["id"]
                            },
                            "pushAes": True,
                            "autoPushAes": False,
                            "id": pn_doc_type["id"],
                            "createdBy": {
                                "id": 496988507945925
                            },
                            "updatedBy": {
                                "id": 477517877510789
                            },
                            "createdAt": 1703645544000,
                            "updatedAt": 1739954834000,
                            "version": 3,
                            "deleted": 0,
                            "originOrgId": 0
                        },
                        "comOrgId": {
                            "orgCode": "AUTOTEST_COM_ORG",
                            "orgName": "公司组织(自动化)",
                            "id": base_data["com_org"]["id"]
                        },
                        "purSlsOrgId": {
                            "orgCode": "AUTOTEST_SLS_ORG", 
                            "orgName": "销售组织(自动化)",
                            "id": base_data["sls_org"]["id"]
                        },
                        "payRecOrgId": {
                            "orgCode": "AUTOTEST_COM_ORG",
                            "orgName": "公司组织(自动化)",
                            "id": base_data["com_org"]["id"]
                        },
                        "pnDate": now_ts,
                        "tradingPartnerId": {
                            "id": base_data["customer"]["id"],
                            "code": "AUTOTEST_VEND",
                            "status": "ENABLED",
                            "name": "供应商(自动化)",
                            "partnerIdentity": ["SUPPLIER"],
                            "classType": "COMPANY",
                            "isInternal": True
                        },
                        "payerId": {
                            "id": base_data["customer"]["id"],
                            "code": "AUTOTEST_VEND", 
                            "status": "ENABLED",
                            "name": "供应商(自动化)",
                            "partnerIdentity": ["SUPPLIER"],
                            "classType": "COMPANY",
                            "isInternal": True
                        },
                        "pnStatus": None,
                        "clearingStatus": None,
                        "currId": {
                            "currName": base_data["currency"]["currName"],
                            "currCode": base_data["currency"]["currCode"],
                            "id": base_data["currency"]["id"]
                        },
                        "baseCurrId": {
                            "currName": base_data["currency"]["currName"],
                            "currCode": base_data["currency"]["currCode"],
                            "id": base_data["currency"]["id"]
                        },
                        "exchRate": 1,
                        "pnItems": [
                            {
                                "arApDocAmt": collection_amount,
                                "cashDiscountDocAmt": 0,
                                "transactionFeeDocAmt": 0,
                                "collectedPaidDocAmt": collection_amount,
                                "arApBaseAmt": collection_amount,
                                "cashDiscountBaseAmt": 0,
                                "transactionFeeBaseAmt": 0,
                                "collectedPaidBaseAmt": collection_amount,
                                "offsetDocAmt": 0,
                                "offsetBaseAmt": 0,
                                "unclearedDocAmt": collection_amount,
                                "unoffsetBaseAmt": collection_amount,
                                "settlementMethodCode": {
                                    "code": "auto_test_06201434",
                                    "name": "现金（自动化）",
                                    "type": "CASH",
                                    "status": "ENABLED",
                                    "id": settlement_method["id"]
                                },
                                "tradingAccountCode": None,
                                "recBillUseWay": None,
                                "nmArId": None,
                                "clearedDocAmt": None,
                                "clearedBaseAmt": None,
                                "unclearedBaseAmt": None,
                                "relDocTypeHeadCode": None,
                                "unoffsetDocAmt": None
                            }
                        ]
                    }
                }
            }
            
            output_dict.update(request_body)
            
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
            with a.step("手动创建收款单"):
                now_ts = int(datetime.now().timestamp() * 1000)
                request_body = {}
                self.create_manual_pn_request_body(now_ts, request_body)
                
                result = {}
                self.send_manual_pn_request("PN-收付款保存服务", request_body, result)
                
                # 提取收款单ID
                pn_doc_id = ParamUtil.extract_id(result)
                assert pn_doc_id, "创建收款单失败：未获取到单据ID"
                
                # 保存收款单信息
                TestPnCreateManual.pn_info.update({
                    "pn_doc_id": pn_doc_id,
                    "request_body": request_body,
                    "collection_amount": 6660
                })
                
                a.json(convert_decimal_to_float(TestPnCreateManual.pn_info), "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单编辑",
        title="编辑收款单备注",
        description="编辑收款单备注信息并保存",
        severity="critical", 
        order=2,
        smoke=False,
        tags=["pn", "edit", "remark"]
    )
    def test_edit_pn_doc_remark(self):
        try:
            with a.step("编辑收款单备注"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                assert pn_doc_id, "请先执行创建收款单用例"
                
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                
                # 修改备注
                new_remark = f"收款单编辑场景自动化用例 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["remark"] = new_remark
                
                result = {}
                self.send_manual_pn_request("PN-收付款保存服务", base_request, result)
                
                # 验证编辑成功
                data = result.get("data", {}).get("data", {})
                assert result.get("success") is True, "接口未成功"
                assert isinstance(data.get("id"), int), "未返回单据ID"
                assert data.get("remark") == new_remark, "备注未正确变更"
                
                # 更新备注信息
                TestPnCreateManual.pn_info["remark"] = new_remark
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单提交",
        title="提交收款单-PN_SUBMIT_EVENT_SERVICE",
        description="用前置用例生成的收款单进行提交并断言成功",
        severity="critical",
        order=3,
        smoke=False,
        tags=["pn", "submit"]
    )
    def test_submit_pn_doc(self):
        try:
            with a.step("提交收款单"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                assert pn_doc_id and base_request, "请先执行编辑用例，确保pn_doc_id和request_body已生成"
                
                # 更新提交参数
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["pnStatus"] = "CONFIRM"
                base_request["serviceKey"] = "ERP_FIN$PN_SUBMIT_EVENT_SERVICE"
                base_request["buttonName"] = "提交"
                
                # 如果没有收款单编号，生成一个
                if base_request["params"]["request"].get("pnHeadCode") is None:
                    base_request["params"]["request"]["pnHeadCode"] = self.mock_data.generate_unique_code("PN")
                
                result = {}
                self.send_manual_pn_request("PN-收付款提交服务", base_request, result)
                
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
        title="收款单过账-PN_PAY_POST_EVENT_SERVICE",
        description="用前置用例生成的收款单进行过账并断言成功",
        severity="critical",
        order=4,
        smoke=False,
        tags=["pn", "post"]
    )
    def test_post_pn_doc(self):
        try:
            with a.step("收款单过账"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                assert pn_doc_id and base_request, "请先执行提交用例，确保pn_doc_id和request_body已生成"
                
                # 更新过账参数
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["pnStatus"] = "CONFIRM"
                base_request["serviceKey"] = "ERP_FIN$PN_PAY_POST_EVENT_SERVICE"
                base_request["buttonName"] = "过账"
                
                result = {}
                self.send_manual_pn_request("PN-付款单过账服务", base_request, result)
                
                # 验证过账成功 - 通常过账是异步的，这里主要验证API调用成功
                assert result.get("success") is True, "收款单过账API调用失败"
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单状态校验",
        title="轮询分页查询收款单状态",
        description="根据pnHeadCode分页查询收款单状态，轮询直至状态为DONE",
        severity="critical",
        order=5,
        smoke=False,
        tags=["pn", "check", "status", "by_code", "paging"]
    )
    def test_check_pn_doc_status_by_code_paging(self):
        try:
            with a.step("轮询查询收款单状态"):
                pn_head_code = TestPnCreateManual.pn_info.get("pn_head_code")
                assert pn_head_code, "请先执行提交用例，确保pnHeadCode已生成"
                
                status_result = {}
                self.wait_for_pn_status(pn_head_code, "DONE", status_result, max_wait=120, interval=3)
                
                assert status_result.get("success"), f"等待收款单状态变更失败，最终状态：{status_result.get('status')}"
                assert status_result.get("status") == "DONE", f"收款单状态应为DONE，实际为：{status_result.get('status')}"
                
                a.json({
                    "pnHeadCode": pn_head_code,
                    "finalStatus": status_result.get("status"),
                    "waitedTime": status_result.get("waited_time", 0)
                }, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="收款单删除",
        title="收款单删除-PN_DELETE_EVENT_SERVICE",
        description="过账完成后执行收款单删除操作，并断言删除成功",
        severity="critical",
        order=6,
        smoke=False,
        tags=["pn", "delete"]
    )
    def test_delete_pn_doc(self):
        try:
            with a.step("等待过账完成"):
                # 等待5秒让过账任务完成
                a.text("等待5秒让过账任务完成...", "等待过账")
                time.sleep(5)

            with a.step("执行收款单删除操作"):
                pn_doc_id = TestPnCreateManual.pn_info.get("pn_doc_id")
                base_request = TestPnCreateManual.pn_info.get("request_body", {}).copy()
                pn_head_code = TestPnCreateManual.pn_info.get("pn_head_code")
                
                assert pn_doc_id and pn_head_code and base_request, "请先执行前置用例，确保pn_doc_id、pnHeadCode和request_body已生成"
                
                # 构建删除请求
                base_request["params"]["request"]["id"] = pn_doc_id
                base_request["params"]["request"]["pnStatus"] = "DONE"  # 删除时应该是已过账状态
                base_request["serviceKey"] = "ERP_FIN$PN_DELETE_EVENT_SERVICE"
                base_request["buttonName"] = "删除"
                
                result = {}
                self.send_manual_pn_request("PN-收付款删除服务", base_request, result)
                
                # 验证API调用成功
                assert result.get("success") is True, f"收款单删除API调用失败，单据编号: {pn_head_code}"
                
                # 添加验证结果到报告
                a.json({
                    "api_success": result.get("success"),
                    "pn_head_code": pn_head_code,
                    "pn_doc_id": pn_doc_id
                }, "删除验证结果")
                
                a.text(f"""
                收款单删除验证总结:
                ✓ 收款单编码: {pn_head_code}
                ✓ 删除API调用: 成功
                """, "收款单删除总结")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def send_manual_pn_request(self, api_key, request_data, result_dict):
        """发送手动收款单API请求，结果存储到result_dict中"""
        try:
            api_path = ParamUtil.get_api_path(self.apis, api_key)
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            # 直接使用完整的请求体
            filtered_params = convert_decimal_to_float(request_data)
            
            result = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(result)
            
            a.json(filtered_params, "请求数据")
            a.json(result, "响应结果数据")
            
            result_dict.update(result)
            
        except Exception as e:
            a.text(str(e), "API请求失败")
            raise

    def wait_for_pn_status(self, pn_head_code, target_status, status_result, max_wait=60, interval=2):
        """等待收款单状态变更，结果存储到status_result中"""
        try:
            # 使用应付单分页接口查询收款单状态
            api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            query_request = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": False,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {"pnHeadCode": {"operator": "CONTAINS", "value": pn_head_code}},
                        "logicOperator": "AND"
                    }
                }
            }
            
            ParamUtil.set_request_params(params, query_request)
            
            waited = 0
            while waited < max_wait:
                result = self.http.post(url, json=params)
                self.assert_util.assert_response_success(result)
                
                data_list = result.get("data", {}).get("data", {}).get("data", [])
                if data_list and data_list[0].get("pnStatus") == target_status:
                    status_result.update({
                        "status": target_status,
                        "success": True,
                        "waited_time": waited
                    })
                    break
                
                time.sleep(interval)
                waited += interval
            else:
                current_status = data_list[0].get("pnStatus") if data_list else None
                status_result.update({
                    "status": current_status,
                    "success": False,
                    "waited_time": waited
                })
                
        except Exception as e:
            a.text(str(e), "状态查询失败")
            status_result.update({
                "status": None,
                "success": False,
                "waited_time": max_wait,
                "error": str(e)
            })

if __name__ == "__main__":
    test = TestPnCreateManual()
    test.setup_class()
    test.test_create_manual_pn_doc()
    test.test_edit_pn_doc_remark()
    test.test_submit_pn_doc()
    test.test_post_pn_doc()
    test.test_check_pn_doc_status_by_code_paging()
    test.test_delete_pn_doc() 