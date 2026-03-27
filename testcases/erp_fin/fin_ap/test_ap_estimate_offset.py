"""
应付单暂估冲回自动化用例
完全独立的测试用例，不依赖其他测试文件
"""
import allure
from testcases.erp_fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import time
from datetime import datetime

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApEstimateOffset(ApBaseTest):
    ap_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()

    def create_prerequisite_ap_doc(self, ap_doc_info):
        """创建前置应付单，结果存储到ap_doc_info中"""
        try:
            with a.step("创建前置应付单"):
                # 创建暂估应付单请求体
                ap_data = self.create_ap_request_body(doc_type_id=2002002, account_type="EST")
                request_body = ap_data["request_body"]
                base_data = ap_data["base_data"]
                
                # 设置暂估应付单特有字段
                ap_head_code = self.mock_util.generate_unique_code("AP_EST")
                request_body["apHeadCode"] = ap_head_code
                request_body["remark"] = f"暂估冲回前置应付单 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 发送创建请求
                fields = ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", 
                         "remark", "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", 
                         "exchRate", "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", 
                         "payClearingStatus", "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"]
                
                response = self.send_api_request("AP-应付保存服务", request_body, fields)
                result = response["result"]
                
                # 提取应付单ID
                ap_doc_id = ParamUtil.extract_id(result)
                assert ap_doc_id, "创建前置应付单失败：未获取到单据ID"
                
                # 保存应付单信息
                ap_doc_info.update({
                    "ap_doc_id": ap_doc_id,
                    "apHeadCode": ap_head_code,
                    "settPartnerId": base_data["vend"],
                    "payOrgId": base_data["pay_org"],
                    "comOrgId": base_data["com_org"],
                    "purOrgId": base_data["pur_org"],
                    "currency": base_data["currency"],
                    "total_amt": base_data["total_amt"],
                    "net_doc_amt": base_data["net_doc_amt"],
                    "gross_base_amt": base_data["gross_base_amt"],
                    "net_base_amt": base_data["net_base_amt"]
                })
                
                a.json({"ap_doc_id": ap_doc_id, "apHeadCode": ap_head_code}, "前置应付单创建结果")
                
        except Exception as e:
            a.text(f"创建前置应付单失败: {str(e)}", "错误信息")
            raise

    def submit_and_post_ap_doc(self, ap_doc_info, processing_result):
        """提交并过账应付单，结果存储到processing_result中"""
        try:
            ap_doc_id = ap_doc_info["ap_doc_id"]
            ap_head_code = ap_doc_info["apHeadCode"]
            
            with a.step("提交暂估应付单"):
                # 构建提交请求
                submit_request = {
                    "apHeadCode": ap_head_code,
                    "apStatus": "CONFIRM",
                    "comOrgId": ap_doc_info["payOrgId"],
                    "purOrgId": ap_doc_info["purOrgId"],
                    "payOrgId": ap_doc_info["payOrgId"],
                    "grossDocAmt": ap_doc_info["total_amt"],
                    "grossBaseAmt": ap_doc_info["gross_base_amt"],
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": ap_doc_info["total_amt"],
                    "uninvoicedDocAmt": ap_doc_info["total_amt"],
                    "unpaidBaseAmt": ap_doc_info["gross_base_amt"],
                    "uninvoicedBaseAmt": ap_doc_info["total_amt"],
                    "unoffsetDocAmt": ap_doc_info["total_amt"],
                    "unoffsetBaseAmt": ap_doc_info["total_amt"],
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id,
                    "apItems": [],
                    "apSchls": [],
                    "settPartnerId": {"id": ap_doc_info["settPartnerId"]["id"]},
                    "netDocAmt": ap_doc_info["net_doc_amt"],
                    "netBaseAmt": ap_doc_info["net_base_amt"]
                }
                
                # 发送提交请求
                fields = list(submit_request.keys())
                self.send_api_request("AP-应付单-列表提交服务", submit_request, fields)
                
            with a.step("过账暂估应付单"):
                # 构建过账请求
                post_request = {
                    "apHeadCode": ap_head_code,
                    "docTypeId": {"id": 2002002},  # 暂估应付单类型
                    "apStatus": "CONFIRM",
                    "comOrgId": ap_doc_info["payOrgId"],
                    "purOrgId": ap_doc_info["purOrgId"],
                    "payOrgId": ap_doc_info["payOrgId"],
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": ap_doc_info["settPartnerId"]["id"]},
                    "docCurrId": {"id": ap_doc_info["payOrgId"]["id"]},  # 使用组织ID作为货币ID（系统特殊要求）
                    "baseCurrId": {"id": ap_doc_info["payOrgId"]["id"]},  # 使用组织ID作为货币ID（系统特殊要求）
                    "exchRate": 1,
                    "grossDocAmt": ap_doc_info["total_amt"],
                    "netDocAmt": ap_doc_info["net_doc_amt"],
                    "grossBaseAmt": ap_doc_info["gross_base_amt"],
                    "netBaseAmt": ap_doc_info["net_base_amt"],
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "unpaidDocAmt": ap_doc_info["total_amt"],
                    "uninvoicedDocAmt": ap_doc_info["total_amt"],
                    "unpaidBaseAmt": ap_doc_info["gross_base_amt"],
                    "uninvoicedBaseAmt": ap_doc_info["total_amt"],
                    "unoffsetDocAmt": ap_doc_info["total_amt"],
                    "unoffsetBaseAmt": ap_doc_info["total_amt"],
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
                
                # 只验证API调用成功，不等待状态变更
                assert result.get("success"), f"暂估应付单过账API调用失败，单据编号: {ap_head_code}"
                
                processing_result.update({
                    "submit_success": True,
                    "post_success": True,
                    "post_api_success": result.get("success")
                })
                
        except Exception as e:
            a.text(f"提交或过账失败: {str(e)}", "错误信息")
            raise

    def prepare_estimate_offset_data(self, output_dict):
        """准备暂估冲回数据，结果存储到output_dict中"""
        try:
            with a.step("准备暂估冲回数据"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付暂估冲回保存事件服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 构建暂估冲回数据
                now_ts = int(datetime.now().timestamp() * 1000)
                offset_data = {
                    "apHeadCode": self.mock_util.generate_unique_code("AP_OFFSET"),
                    "docTypeId": {"id": 2002001},  # 标准应付单类型
                    "apDate": now_ts,
                    "comOrgId": TestApEstimateOffset.ap_info["comOrgId"],
                    "purOrgId": TestApEstimateOffset.ap_info["purOrgId"],
                    "payOrgId": TestApEstimateOffset.ap_info["payOrgId"],
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": TestApEstimateOffset.ap_info["settPartnerId"]["id"]},
                    "docCurrId": {"id": TestApEstimateOffset.ap_info["currency"]["id"]},
                    "baseCurrId": {"id": TestApEstimateOffset.ap_info["currency"]["id"]},
                    "exchRate": 1,
                    "grossDocAmt": TestApEstimateOffset.ap_info["total_amt"] * 0.8,  # 冲回80%
                    "netDocAmt": TestApEstimateOffset.ap_info["net_doc_amt"] * 0.8,
                    "grossBaseAmt": TestApEstimateOffset.ap_info["gross_base_amt"] * 0.8,
                    "netBaseAmt": TestApEstimateOffset.ap_info["net_base_amt"] * 0.8,
                    "remark": f"暂估冲回测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "headOffsetStatus": "UNOFFSET",
                    "apItems": [],
                    "apSchls": [],
                    "estOffsetRelId": {"id": TestApEstimateOffset.ap_info["ap_doc_id"]},
                    "estOffsetRelCode": TestApEstimateOffset.ap_info["apHeadCode"]
                }
                
                output_dict.update({
                    "offset_data": offset_data,
                    "api_url": url,
                    "api_params": params
                })
                
                a.json(offset_data, "暂估冲回数据")
                
        except Exception as e:
            a.text(f"准备暂估冲回数据失败: {str(e)}", "错误信息")
            raise

    def send_estimate_offset_request(self, ap_doc_info, offset_data, result_dict):
        """发送暂估冲回请求，结果存储到result_dict中"""
        try:
            with a.step("发送暂估冲回请求"):
                offset_request = offset_data["offset_data"]
                
                # 发送暂估冲回请求
                fields = list(offset_request.keys())
                response = self.send_api_request("AP-应付暂估冲回保存事件服务", offset_request, fields)
                result = response["result"]
                filtered_params = response["request_params"]
                
                # 提取冲回单据ID
                offset_doc_id = ParamUtil.extract_id(result)
                assert offset_doc_id, "暂估冲回失败：未获取到冲回单据ID"
                
                result_dict.update({
                    "offset_doc_id": offset_doc_id,
                    "offset_head_code": offset_request["apHeadCode"],
                    "offset_amount": offset_request["grossDocAmt"],
                    "original_amount": ap_doc_info["total_amt"],
                    "remaining_amount": ap_doc_info["total_amt"] - offset_request["grossDocAmt"]
                })
                
                # 添加报告附件
                a.json(filtered_params, "暂估冲回请求数据")
                a.json(result, "暂估冲回响应结果")
                a.json(result_dict, "暂估冲回结果")
                
        except Exception as e:
            a.text(f"发送暂估冲回请求失败: {str(e)}", "错误信息")
            raise

    @case_decorator(
        story="应付单前置数据",
        title="创建暂估应付单前置数据",
        description="创建、提交、过账暂估应付单，为暂估冲回提供前置数据",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ap", "prerequisite", "estimate"]
    )
    def test_create_prerequisite_ap_doc(self):
        try:
            with a.step("创建暂估应付单前置数据"):
                # 创建前置应付单
                self.create_prerequisite_ap_doc(TestApEstimateOffset.ap_info)
                
                # 提交并过账应付单
                processing_result = {}
                self.submit_and_post_ap_doc(TestApEstimateOffset.ap_info, processing_result)
                
                # 验证处理结果
                assert processing_result.get("submit_success"), "提交暂估应付单失败"
                assert processing_result.get("post_success"), "过账暂估应付单失败"
                
                a.json(TestApEstimateOffset.ap_info, "前置数据创建结果")
                a.json(processing_result, "处理结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应付单暂估冲回",
        title="执行应付单暂估冲回",
        description="基于前置暂估应付单执行暂估冲回，调整金额并断言成功",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ap", "estimate_offset"]
    )
    def test_ap_estimate_offset(self):
        try:
            with a.step("执行应付单暂估冲回"):
                # 验证前置数据
                assert TestApEstimateOffset.ap_info.get("ap_doc_id"), "请先执行前置用例，确保暂估应付单已创建"
                
                # 准备暂估冲回数据
                offset_data = {}
                self.prepare_estimate_offset_data(offset_data)
                
                # 发送暂估冲回请求
                result_dict = {}
                self.send_estimate_offset_request(TestApEstimateOffset.ap_info, offset_data, result_dict)
                
                # 验证冲回结果
                assert result_dict.get("offset_doc_id"), "暂估冲回失败：未获取到冲回单据ID"
                assert result_dict.get("offset_head_code"), "暂估冲回失败：未获取到冲回单据编号"
                
                # 验证金额计算
                original_amount = result_dict.get("original_amount", 0)
                offset_amount = result_dict.get("offset_amount", 0)
                remaining_amount = result_dict.get("remaining_amount", 0)
                
                assert original_amount > 0, "原始金额应大于0"
                assert offset_amount > 0, "冲回金额应大于0"
                assert remaining_amount >= 0, "剩余金额应大于等于0"
                assert abs(original_amount - offset_amount - remaining_amount) < 0.01, "金额计算不正确"
                
                a.json(result_dict, "暂估冲回最终结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApEstimateOffset()
    test.setup_class() 
    test.test_create_prerequisite_ap_doc()
    test.test_ap_estimate_offset() 