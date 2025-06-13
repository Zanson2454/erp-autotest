"""
应付单暂估冲回自动化用例
依赖test_ap_doc_save.py生成的应付单数据，符合testcaserole规范
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
import time
from decimal import Decimal
from testcases.fin.fin_ap.test_ap_doc_save import TestApDocumentSave
from data_factory.fin_ap_factory import FinApFactory
from pathlib import Path

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

    def _wait_for_ap_completion(self, ap_head_code):
        """等待应付单异步处理完成"""
        max_wait = 60
        interval = 2
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
                    return current_status
            
            time.sleep(interval)
            waited += interval
        
        raise AssertionError(f"应付单处理超时，等待时间：{waited}s")

    def _convert_decimal_to_float(self, obj):
        """递归转换Decimal类型为float"""
        if isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    @ParamUtil.case_decorator(
        story="应付单暂估冲回",
        title="执行应付单暂估冲回",
        description="基于前置应付单执行暂估冲回，调整金额并断言成功",
        severity="critical",
        order=6,
        smoke=False,
        tags=["ap", "estimate_offset"]
    )
    def test_ap_estimate_offset(self):
        try:
            with a.step("等待前置应付单处理完成"):
                ap_save_info = TestApDocumentSave.ap_save_info
                ap_doc_id = ap_save_info.get("ap_doc_id")
                ap_head_code = ap_save_info.get("apHeadCode")
                assert ap_doc_id and ap_head_code, "未找到应付单ID或编码，请先执行应付单保存用例"
                
                current_status = self._wait_for_ap_completion(ap_head_code)
                assert current_status == "DONE", f"应付单状态异常：{current_status}"
            
            with a.step("准备暂估冲回数据并调用接口"):
                # 使用数据工厂生成标准的明细数据
                mat = self.ap_factory.create_material()
                tax_code = self.ap_factory.create_tax_code()
                original_ap_items = self.ap_factory.create_ap_items_full([mat, mat], [tax_code, tax_code])
                original_ap_items = self._convert_decimal_to_float(original_ap_items)
                
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
                    "adjNetDocAmt": total_adj_net_amt,
                    "docCurrId": ap_save_info.get("currency", {"id": 2000001}),
                    "comOrgId": ap_save_info.get("comOrgId", {"id": 14373001}),
                    "netDocAmt": ap_save_info.get("net_doc_amt", 6929.37),
                    "exchRate": 1,
                    "estOffsetRelId": {"id": ap_doc_id},
                    "diffNetDocAmt": total_diff_net_amt,
                    "apDate": int(time.time() * 1000),
                    "diffGrossDocAmt": 0,
                    "adjApItems": adj_ap_items,
                    "adjGrossDocAmt": total_adj_gross_amt,
                    "settPartnerId": ap_save_info.get("settPartnerId", {"id": 2058001}),
                    "docTypeId": {"id": 2002001},
                    "baseCurrId": {"id": 2000001},
                    "payOrgId": ap_save_info.get("payOrgId", {"id": 14373001}),
                    "grossDocAmt": ap_save_info.get("total_amt", 7500)
                })
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 断言暂估冲回执行成功
                success = result.get("success", False)
                if not success:
                    inner_msg = result.get("innerMsg", "未知错误")
                    assert success, f"暂估冲回执行失败，错误信息: {inner_msg}"
                else:
                    assert success, "暂估冲回执行成功"
                
                # 保存测试数据
                TestApEstimateOffset.ap_estimate_offset_info.update({
                    "ap_doc_id": ap_doc_id,
                    "adj_net_doc_amt": total_adj_net_amt,
                    "diff_net_doc_amt": total_diff_net_amt,
                    "success": success
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApEstimateOffset.ap_estimate_offset_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApEstimateOffset()
    test.setup_class() 