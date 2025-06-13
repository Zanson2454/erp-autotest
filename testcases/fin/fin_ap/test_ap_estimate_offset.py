"""
应付单暂估冲回自动化用例
完全独立的测试用例，不依赖其他测试文件
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
import time
from decimal import Decimal
from data_factory.fin_ap_factory import FinApFactory
from pathlib import Path
from datetime import datetime

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApEstimateOffset(BaseTest):
    ap_estimate_offset_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ap_factory = FinApFactory()
        
        # 初始化财务API配置
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params

    def _create_prerequisite_ap_doc(self, ap_doc_info):
        """创建前置应付单，结果存储到ap_doc_info中"""
        try:
            with a.step("创建前置应付单"):
                now = datetime.now()
                now_ts = int(now.timestamp() * 1000)
                
                # 使用数据工厂生成基础数据
                com_org = self.ap_factory.create_org("COM")
                vend = self.ap_factory.create_vendor()
                pur_org = self.ap_factory.create_org("PUR")
                pay_org = com_org
                curr = self.ap_factory.create_currency()
                tax_code = self.ap_factory.create_tax_code()
                mat = self.ap_factory.create_material()
                mat_list = [mat, mat]
                tax_code_list = [tax_code, tax_code]
                ap_items = self.ap_factory.create_ap_items_full(mat_list, tax_code_list)
                
                # 转换金额类型
                for item in ap_items:
                    for k in ["grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt"]:
                        if k in item:
                            item[k] = float(item[k])
                
                total_amt = float(sum([item["grossDocAmt"] for item in ap_items]))
                net_doc_amt = float(sum([item["netDocAmt"] for item in ap_items]))
                gross_base_amt = float(sum([item["grossBaseAmt"] for item in ap_items]))
                net_base_amt = float(sum([item["netBaseAmt"] for item in ap_items]))
                ap_schl = self.ap_factory.create_ap_schl(amount=total_amt, due_date=now_ts)
                
                if isinstance(ap_schl, dict):
                    for k in ap_schl:
                        if hasattr(ap_schl[k], "__float__"):
                            ap_schl[k] = float(ap_schl[k])
                
                # 创建应付单
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    ["docTypeId", "apDate", "comOrgId", "purOrgId", "payOrgId", "apHeadCode", "remark", 
                     "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId", "exchRate", 
                     "grossDocAmt", "netDocAmt", "grossBaseAmt", "netBaseAmt", "payClearingStatus", 
                     "invClearingStatus", "headOffsetStatus", "apItems", "apSchls"],
                    ["params", "request"]
                )
                
                ap_head_code = ParamUtil.generate_unique_code("AP_EST")
                ParamUtil.set_request_params(filtered_params, {
                    "docTypeId": {"id": 2002002},
                    "apDate": now_ts,
                    "comOrgId": com_org,
                    "purOrgId": pur_org,
                    "payOrgId": pay_org,
                    "apHeadCode": ap_head_code,
                    "remark": f"暂估冲回前置应付单 - {now.strftime('%Y-%m-%d %H:%M:%S')}",
                    "settPartnerType": "SUPPLIER",
                    "settPartnerId": {"id": vend["id"]},
                    "docCurrId": {"id": curr["id"]},
                    "baseCurrId": {"id": curr["id"]},
                    "exchRate": 1,
                    "grossDocAmt": total_amt,
                    "netDocAmt": net_doc_amt,
                    "grossBaseAmt": gross_base_amt,
                    "netBaseAmt": net_base_amt,
                    "payClearingStatus": "UNCLEARED",
                    "invClearingStatus": "UNCLEARED",
                    "headOffsetStatus": "UNOFFSET",
                    "apItems": ap_items,
                    "apSchls": [ap_schl]
                })
                
                filtered_params = self._convert_decimal_to_float_single(filtered_params)
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                ap_doc_id = ParamUtil.extract_id(result)
                assert ap_doc_id, "创建前置应付单失败：未获取到单据ID"
                
                # 保存应付单信息
                ap_doc_info.update({
                    "ap_doc_id": ap_doc_id,
                    "apHeadCode": ap_head_code,
                    "settPartnerId": vend,
                    "payOrgId": pay_org,
                    "comOrgId": com_org,
                    "purOrgId": pur_org,
                    "currency": curr,
                    "total_amt": total_amt,
                    "net_doc_amt": net_doc_amt,
                    "gross_base_amt": gross_base_amt,
                    "net_base_amt": net_base_amt
                })
                
                a.json({"ap_doc_id": ap_doc_id, "apHeadCode": ap_head_code}, "前置应付单创建结果")
                
        except Exception as e:
            a.text(f"创建前置应付单失败: {str(e)}", "错误信息")
            raise

    def _submit_and_post_ap_doc(self, ap_doc_info, processing_result):
        """提交并过账应付单，结果存储到processing_result中"""
        try:
            ap_doc_id = ap_doc_info["ap_doc_id"]
            ap_head_code = ap_doc_info["apHeadCode"]
            
            with a.step("提交暂估应付单"):
                # 提交应付单
                api_path = ParamUtil.get_api_path(self.apis, "AP-应付单-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
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
                    "unpaidBaseAmt": ap_doc_info["net_base_amt"],
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
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(submit_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, submit_request)
                filtered_params = self._convert_decimal_to_float_single(filtered_params)
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
            with a.step("过账暂估应付单"):
                # 过账应付单
                api_path = ParamUtil.get_api_path(self.apis, "应付单-过账-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
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
                    "unpaidBaseAmt": ap_doc_info["net_base_amt"],
                    "uninvoicedBaseAmt": ap_doc_info["net_base_amt"],
                    "unoffsetDocAmt": ap_doc_info["total_amt"],
                    "unoffsetBaseAmt": ap_doc_info["total_amt"],
                    "headOffsetStatus": "UNOFFSET",
                    "asyncExecutionStatus": "CREATED",
                    "id": ap_doc_id
                }
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, list(post_request.keys()), ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, post_request)
                filtered_params = self._convert_decimal_to_float_single(filtered_params)
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                processing_result.update({
                    "submit_success": True,
                    "post_success": True,
                    "message": "暂估应付单提交和过账成功"
                })
                
        except Exception as e:
            processing_result.update({
                "submit_success": False,
                "post_success": False,
                "error": str(e)
            })
            a.text(f"提交或过账暂估应付单失败: {str(e)}", "错误信息")
            raise

    def _wait_for_ap_completion(self, ap_head_code, completion_result, max_wait=30, interval=2):
        """等待应付单异步处理完成，结果存储到completion_result中"""
        waited = 0
        
        while waited < max_wait:
            query_api_path = ParamUtil.get_api_path(self.apis, "应付单头表-分页数据服务_PmHKWs2")
            query_params, query_url = ParamUtil.get_api_params(self.api_params, query_api_path)
            ParamUtil.set_request_params(query_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "needTotal": False,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "apHeadCode": {
                                "operator": "CONTAINS",
                                "value": ap_head_code
                            }
                        },
                        "logicOperator": "AND"
                    }
                }
            })
            query_result = self.http.post(query_url, json=query_params)
            self.assert_util.assert_response_success(query_result)
            data_list = query_result.get("data", {}).get("data", {}).get("data", [])
            
            if data_list:
                current_status = data_list[0].get("apStatus")
                async_status = data_list[0].get("asyncExecutionStatus")
                
                if current_status == "DONE" and async_status == "SUCCEEDED":
                    a.text(f"应付单异步处理完成，状态：{current_status}，异步状态：{async_status}", "状态检查")
                    completion_result["final_status"] = current_status
                    completion_result["async_status"] = async_status
                    completion_result["success"] = True
                    break
            
            time.sleep(interval)
            waited += interval
        else:
            completion_result["final_status"] = None
            completion_result["async_status"] = None
            completion_result["success"] = False
            completion_result["error"] = f"应付单处理超时，等待时间：{waited}s"

    def _convert_decimal_to_float_single(self, obj):
        """单个对象转换 - 工具函数必需返回值"""
        if isinstance(obj, dict):
            return {k: self._convert_decimal_to_float_single(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float_single(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    def _prepare_estimate_offset_data(self, output_dict):
        """准备暂估冲回数据，结果存储到output_dict中"""
        # 使用数据工厂生成标准的明细数据
        mat = self.ap_factory.create_material()
        tax_code = self.ap_factory.create_tax_code()
        original_ap_items = self.ap_factory.create_ap_items_full([mat, mat], [tax_code, tax_code])
        original_ap_items = self._convert_decimal_to_float_single(original_ap_items)
        
        # 计算调整后的金额（第一个明细行减少292.2）
        adj_ap_items = []
        for i, item in enumerate(original_ap_items):
            adj_item = {
                "context": {},
                "matId": item["matId"],
                "matName": "物料",
                "apQty": item["apQty"],
                "grossDocPrice": item["grossDocPrice"],
                "grossDocAmt": float(item["grossDocAmt"]),
                "netDocAmt": float(item["netDocAmt"]),
                "taxCodeId": item["taxCodeId"],
                "taxRate": float(item["taxRate"]),
                "taxAmt": float(item["taxAmt"]),
                "settItemTypeId": item["settItemTypeId"],
                "netDocPrice": 471.69,
                "adjGrossDocPrice": item["grossDocPrice"],
                "adjGrossDocAmt": float(item["grossDocAmt"]),
                "adjNetDocPrice": 471.69,
                "adjNetDocAmt": float(item["netDocAmt"]) - (292.2 if i == 0 else 0),
                "diffGrossDocPrice": 0,
                "diffGrossDocAmt": 0,
                "diffNetDocPrice": 0,
                "diffNetDocAmt": -292.2 if i == 0 else 0,
            }
            adj_ap_items.append(adj_item)
        
        # 计算汇总金额
        total_adj_net_amt = sum([float(item["adjNetDocAmt"]) for item in adj_ap_items])
        total_adj_gross_amt = sum([float(item["adjGrossDocAmt"]) for item in adj_ap_items])
        total_diff_net_amt = sum([float(item["diffNetDocAmt"]) for item in adj_ap_items])
        
        output_dict.update({
            "adj_ap_items": adj_ap_items,
            "total_adj_net_amt": total_adj_net_amt,
            "total_adj_gross_amt": total_adj_gross_amt,
            "total_diff_net_amt": total_diff_net_amt
        })

    def _send_estimate_offset_request(self, ap_doc_info, offset_data, result_dict):
        """发送暂估冲回请求，结果存储到result_dict中"""
        # 获取API配置并设置参数
        api_path = ParamUtil.get_api_path(self.apis, "AP-应付暂估冲回保存事件服务")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        filtered_params = ParamUtil.filter_post_body_fields(
            params, 
            ["settPartnerType", "adjNetDocAmt", "docCurrId", "comOrgId", "netDocAmt", 
             "exchRate", "estOffsetRelId", "diffNetDocAmt", "apDate", "diffGrossDocAmt", 
             "adjApItems", "adjGrossDocAmt", "settPartnerId", "docTypeId", "baseCurrId", 
             "payOrgId", "grossDocAmt"], 
            ["params", "request"]
        )
        
        # 设置请求参数
        ParamUtil.set_request_params(filtered_params, {
            "settPartnerType": "SUPPLIER",
            "adjNetDocAmt": offset_data["total_adj_net_amt"],
            "docCurrId": {"id": ap_doc_info["currency"]["id"]},
            "comOrgId": ap_doc_info["comOrgId"],
            "netDocAmt": ap_doc_info["net_doc_amt"],
            "exchRate": 1,
            "estOffsetRelId": {"id": ap_doc_info["ap_doc_id"]},
            "diffNetDocAmt": offset_data["total_diff_net_amt"],
            "apDate": int(time.time() * 1000),
            "diffGrossDocAmt": 0,
            "adjApItems": offset_data["adj_ap_items"],
            "adjGrossDocAmt": offset_data["total_adj_gross_amt"],
            "settPartnerId": ap_doc_info["settPartnerId"],
            "docTypeId": {"id": 2002001},
            "baseCurrId": {"id": ap_doc_info["currency"]["id"]},
            "payOrgId": ap_doc_info["payOrgId"],
            "grossDocAmt": ap_doc_info["total_amt"]
        })
        
        # 发送请求
        result = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(result)
        
        a.json(filtered_params, "请求数据")
        a.json(result, "响应结果数据")
        
        result_dict.update(result)

    @ParamUtil.case_decorator(
        story="应付单前置数据",
        title="创建暂估应付单前置数据",
        description="创建、提交、过账暂估应付单，为暂估冲回提供前置数据",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ap", "prerequisite", "estimate"]
    )
    def test_create_prerequisite_ap_doc(self):
        """创建前置暂估应付单"""
        try:
            # 创建前置应付单
            ap_doc_info = {}
            self._create_prerequisite_ap_doc(ap_doc_info)
            
            # 提交并过账应付单
            processing_result = {}
            self._submit_and_post_ap_doc(ap_doc_info, processing_result)
            
            # 等待应付单处理完成
            with a.step("等待应付单处理完成"):
                completion_result = {}
                self._wait_for_ap_completion(ap_doc_info["apHeadCode"], completion_result)
                
                if not completion_result.get("success"):
                    error_msg = completion_result.get("error", "应付单处理失败")
                    assert False, error_msg
                
                current_status = completion_result.get("final_status")
                assert current_status == "DONE", f"应付单状态异常：{current_status}"
            
            # 保存前置数据到类变量
            TestApEstimateOffset.ap_estimate_offset_info.update({
                "prerequisite_ap_doc": ap_doc_info,
                "processing_result": processing_result,
                "completion_result": completion_result,
                "验证结果": "前置暂估应付单创建成功"
            })
            
            a.json(TestApEstimateOffset.ap_estimate_offset_info, "前置数据创建结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
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
            # 获取前置应付单数据
            prerequisite_data = TestApEstimateOffset.ap_estimate_offset_info.get("prerequisite_ap_doc")
            assert prerequisite_data, "未找到前置应付单数据，请先执行创建前置数据用例"
            
            ap_doc_info = prerequisite_data
            ap_doc_id = ap_doc_info.get("ap_doc_id")
            ap_head_code = ap_doc_info.get("apHeadCode")
            assert ap_doc_id and ap_head_code, "前置应付单数据不完整"
            
            # 验证前置应付单状态
            with a.step("验证前置应付单状态"):
                completion_result = {}
                self._wait_for_ap_completion(ap_head_code, completion_result, max_wait=5)
                
                if not completion_result.get("success"):
                    assert False, "前置应付单状态异常，无法执行暂估冲回"
                
                current_status = completion_result.get("final_status")
                assert current_status == "DONE", f"前置应付单状态应为DONE，实际为：{current_status}"
            
            # 执行暂估冲回
            with a.step("准备暂估冲回数据并调用接口"):
                offset_data = {}
                self._prepare_estimate_offset_data(offset_data)
                
                result = {}
                self._send_estimate_offset_request(ap_doc_info, offset_data, result)
                
                # 断言暂估冲回执行成功
                success = result.get("success", False)
                if not success:
                    inner_msg = result.get("innerMsg", "未知错误")
                    assert success, f"暂估冲回执行失败，错误信息: {inner_msg}"
                
                # 更新测试数据
                TestApEstimateOffset.ap_estimate_offset_info.update({
                    "ap_doc_id": ap_doc_id,
                    "ap_head_code": ap_head_code,
                    "offset_result": result,
                    "offset_data": offset_data,
                    "验证结果": "暂估冲回执行成功"
                })
                
                a.json(TestApEstimateOffset.ap_estimate_offset_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApEstimateOffset()
    test.setup_class()
    test.test_ap_estimate_offset() 