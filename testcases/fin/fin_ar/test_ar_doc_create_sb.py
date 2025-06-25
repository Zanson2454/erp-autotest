import allure
from testcases.fin.fin_ar import ArBaseTest, convert_decimal_to_float
from utils.param_util import ParamUtil
from utils.mock_util import MockData
from utils.report_util import a, case_decorator
from data_factory.fin_ar_factory import FinArFactory
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import time

class TestArDocCreateSb(ArBaseTest):
    ar_info = {}
    mock_data = MockData()
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ar_factory = FinArFactory()
        cls.mock_data = MockData()
        
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params

    def _create_ar_request_body(self, now_ts, output_dict):
        """创建应收单请求体"""
        # 使用数据工厂获取完整的基础数据
        base_data = self.ar_factory.get_base_data_for_fin_doc("AR")
        
        # 从基础数据中获取必要信息
        com_org_id = base_data["com_org"]["id"]
        sls_org_id = base_data["sls_org"]["id"]
        curr_id = base_data["currency"]["id"]
        customer_info = base_data["customer"]  # 获取完整的客户信息
        
        # 获取其他必要的数据
        mat_id = self.ar_factory.get_material_by_id(14672002)["id"]
        tax_code_id = self.ar_factory.get_tax_code_by_id(2002002)["id"]
        sett_item_type_id = self.ar_factory.get_sett_item_type_by_id(12)["id"]
        
        ar_items = self.ar_factory.create_ar_items_full(mat_id, tax_code_id, sett_item_type_id)
        ar_schls = self.ar_factory.create_ar_schls_full(due_date=now_ts)
        
        gross_doc_amt = sum([item.get("grossDocAmt", 0) for item in ar_items])
        net_doc_amt = sum([item.get("netDocAmt", 0) for item in ar_items])
        gross_base_amt = sum([item.get("grossBaseAmt", 0) for item in ar_items])
        net_base_amt = sum([item.get("netBaseAmt", 0) for item in ar_items])
        tax_amt = sum([item.get("taxAmt", 0) for item in ar_items])
        
        output_dict.update({
            "docTypeId": {"id": 14003001},
            "arDate": now_ts,
            "comOrgId": {"id": com_org_id},
            "slsOrgId": {"id": sls_org_id},
            "payOrgId": {"id": com_org_id},
            "docCurrId": {"id": curr_id},
            "baseCurrId": {"id": curr_id},
            "exchRate": 1,
            "settPartnerType": "CUSTOMER",
            "settPartnerId": customer_info,  # 使用完整的客户信息
            "arStatus": "DRAFT",
            "collectionClearingStatus": "UNCLEARED",
            "billingClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "remark": self.mock_data.get_mock_remark(),
            "arItems": ar_items,
            "arSchls": ar_schls,
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_base_amt,
            "netBaseAmt": net_base_amt,
            "taxAmt": tax_amt,
            "uncollectedDocAmt": gross_doc_amt,
            "uncollectedBaseAmt": gross_base_amt,
            "unbilledDocAmt": gross_doc_amt,
            "unbilledBaseAmt": gross_base_amt,
            "unoffsetDocAmt": gross_doc_amt,
            "unoffsetBaseAmt": gross_base_amt
        })

    def _send_api_request(self, api_key, request_data, result_dict):
        """发送API请求"""
        api_path = ParamUtil.get_api_path(self.apis, api_key)
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        filtered_params = ParamUtil.filter_post_body_fields(
            params, list(request_data.keys()), ["params", "request"]
        )
        ParamUtil.set_request_params(filtered_params, request_data)
        filtered_params = convert_decimal_to_float(filtered_params)
        
        result = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(result)
        
        a.json(filtered_params, "请求数据")
        a.json(result, "响应结果数据")
        
        result_dict.update(result)

    def _wait_for_ar_status(self, ar_head_code, target_status, status_result, max_wait=15, interval=2):
        """等待应收单状态变更"""
        api_path = ParamUtil.get_api_path(self.apis, "应收单头表-分页数据服务_PmHKWs4")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        ParamUtil.set_request_params(params, {
            "pageable": {
                "pageNo": 1,
                "pageSize": 1,
                "needTotal": False,
                "conditionItems": {
                    "type": "ConditionItems",
                    "conditions": {"arHeadCode": {"operator": "CONTAINS", "value": ar_head_code}},
                    "logicOperator": "AND"
                }
            }
        })
        
        waited = 0
        while waited < max_wait:
            result = self.http.post(url, json=params)
            self.assert_util.assert_response_success(result)
            
            data_list = result.get("data", {}).get("data", {}).get("data", [])
            if data_list and data_list[0].get("arStatus") == target_status:
                status_result["status"] = target_status
                status_result["success"] = True
                break
            
            time.sleep(interval)
            waited += interval
        else:
            status_result["status"] = None
            status_result["success"] = False

    def _create_sb_by_ar(self, ar_doc_id, bil_code, sb_result):
        """基于应收单创建销售发票，结果存储到sb_result中"""
        sb_request = {
            "params": {
                "request": {
                    "bilCode": bil_code,
                    "docTypeId": {"id": 20000012},
                    "id": ar_doc_id
                }
            }
        }
        
        api_path = "/api/trantor/service/engine/execute/ERP_FIN$SB_CONVERT_BY_AR_ASYNC_EVENT_SERVICE"
        result = self.http.post(api_path, json=sb_request)
        self.assert_util.assert_response_success(result)
        
        a.json(sb_request, "请求数据")
        a.json(result, "响应结果数据")
        
        sb_result.update(result)

    def _wait_for_sb_task_completion(self, ar_doc_id, task_result, max_wait=15, interval=3):
        """等待销售发票创建异步任务完成，结果存储到task_result中"""
        waited = 0
        ar_detail = {}
        
        while waited < max_wait:
            ar_detail.clear()
            self.query_ar_detail(ar_doc_id, ar_detail)
            
            if not ar_detail:
                time.sleep(interval)
                waited += interval
                continue
                
            async_status = ar_detail.get("asyncExecutionStatus")
            billing_doc_amt = ar_detail.get("billingDocAmt", 0)
            
            if async_status == "SUCCEEDED" and billing_doc_amt > 0:
                task_result.update({
                    "ar_data": ar_detail.copy(),
                    "status": "SUCCESS"
                })
                break
            elif async_status == "FAILED":
                failure_reason = ar_detail.get("asyncExecutionFailureReason", "未知原因")
                task_result.update({
                    "ar_data": ar_detail.copy(),
                    "status": f"FAILED: {failure_reason}"
                })
                break
            
            time.sleep(interval)
            waited += interval
        else:
            final_ar_detail = {}
            self.query_ar_detail(ar_doc_id, final_ar_detail)
            task_result.update({
                "ar_data": final_ar_detail,
                "status": "TIMEOUT"
            })

    def _build_sb_query_params(self, bil_code, query_params):
        """构建销售发票查询参数，结果存储到query_params中"""
        query_params.update({
            "serviceKey": "ERP_FIN$FIN_TM_SB_HEAD_TR_PAGING_DATA_SERVICE_PmHKWs1",
            "params": {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "conditionGroup": {
                            "type": "ConditionGroup",
                            "logicOperator": "AND", 
                            "conditions": [{
                                "type": "ConditionLeaf",
                                "leftValue": {
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "VAR",
                                    "varValue": [{"valueKey": "bilCode"}]
                                },
                                "operator": "EQ",
                                "rightValue": {
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "CONST",
                                    "constValue": bil_code
                                }
                            }]
                        }
                    }
                },
                "modelKey": "ERP_FIN$fin_tm_sb_head_tr"
            }
        })

    def _query_sb_by_paging(self, bil_code, query_result, max_wait=15, interval=2):
        """通过分页服务查询销售发票，结果存储到query_result中"""
        api_path = ParamUtil.get_api_path(self.apis, "销售发票头表-分页数据服务_PmHKWs1")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        query_params = {}
        self._build_sb_query_params(bil_code, query_params)
        
        waited = 0
        while waited < max_wait:
            result = self.http.post(url, json=query_params)
            self.assert_util.assert_response_success(result)
            
            data_list = result.get("data", {}).get("data", {}).get("data", [])
            for record in data_list:
                if isinstance(record, dict) and record.get("bilCode") == bil_code:
                    a.json(query_params, "请求数据")
                    a.json(result, "响应结果数据")
                    query_result.update({
                        "record": record,
                        "result": result,
                        "waited": waited,
                        "found": True
                    })
                    return
            
            time.sleep(interval)
            waited += interval
            a.text(f"等待销售发票生成中...已等待{waited}秒", "轮询状态")
        
        a.json(query_params, "请求数据")
        a.json(result, "响应结果数据")
        query_result.update({
            "record": None,
            "result": result,
            "waited": waited,
            "found": False
        })

    def _verify_ar_billing_amounts(self, ar_data, verification_result):
        """验证应收单收票金额，结果存储到verification_result中"""
        billing_doc_amt = ar_data.get("billingDocAmt", 0)
        gross_doc_amt = ar_data.get("grossDocAmt", 0)
        ar_items = ar_data.get("arItems", [])
        
        assert billing_doc_amt == gross_doc_amt, f"应收单头上的收票中金额应等于价税合计总额，收票中金额：{billing_doc_amt}，价税合计总额：{gross_doc_amt}"
        assert ar_items, "未找到应收明细行数据"
        
        item_verification_results = []
        for i, item in enumerate(ar_items):
            clearing_doc_amt = item.get("clearingDocAmt", 0)
            item_gross_doc_amt = item.get("grossDocAmt", 0)
            
            item_result = {
                "index": i + 1,
                "clearingDocAmt": clearing_doc_amt,
                "grossDocAmt": item_gross_doc_amt,
                "验证结果": "通过" if clearing_doc_amt == item_gross_doc_amt else "失败"
            }
            item_verification_results.append(item_result)
            
            assert clearing_doc_amt == item_gross_doc_amt, f"应收明细行{i+1}的钩稽中金额应等于价税合计金额，钩稽中金额：{clearing_doc_amt}，价税合计金额：{item_gross_doc_amt}"
        
        verification_result.update({
            "应收单头表验证": {
                "billingDocAmt": billing_doc_amt,
                "grossDocAmt": gross_doc_amt,
                "头表验证结果": "通过"
            },
            "应收明细行验证": item_verification_results
        })

    def _verify_sb_record(self, sb_record, bil_code, sb_verification):
        """验证销售发票记录，结果存储到sb_verification中"""
        actual_sb_status = sb_record.get("sbStatus")
        actual_sb_id = sb_record.get("id")
        actual_bil_code = sb_record.get("bilCode")
        actual_sb_head_code = sb_record.get("sbHeadCode")
        
        assert actual_sb_status == "DRAFT", f"销售发票状态应为DRAFT，实际为：{actual_sb_status}"
        assert actual_bil_code == bil_code, f"bil_code不匹配，期望：{bil_code}，实际：{actual_bil_code}"
        assert actual_sb_id, "销售发票ID不能为空"
        assert actual_sb_head_code, "销售发票编码不能为空"
        
        sb_verification.update({
            "actualSbStatus": actual_sb_status,
            "actualSbId": actual_sb_id,
            "actualBilCode": actual_bil_code,
            "actualSbHeadCode": actual_sb_head_code
        })

    def _verify_ar_item_clearing_status(self, ar_items):
        """验证应收单明细行钩稽状态"""
        assert ar_items, "未找到应收明细行数据"
        
        for i, item in enumerate(ar_items):
            clearing_doc_amt = item.get("clearingDocAmt", 0)
            cleared_doc_amt = item.get("clearedDocAmt", 0)
            clearing_qty = item.get("clearingQty", 0)
            cleared_qty = item.get("clearedQty", 0)
            clearing_base_amt = item.get("clearingBaseAmt", 0)
            cleared_base_amt = item.get("clearedBaseAmt", 0)
            item_clearing_status = item.get("clearingStatus")
            item_gross_doc_amt = item.get("grossDocAmt", 0)
            item_qty = item.get("qty", 0)
            item_gross_base_amt = item.get("grossBaseAmt", 0)
            
            assert clearing_doc_amt == 0, f"明细行{i+1}过账后钩稽中金额应为0，实际为：{clearing_doc_amt}"
            assert cleared_doc_amt == item_gross_doc_amt, f"明细行{i+1}过账后已钩稽金额应等于价税合计金额，已钩稽：{cleared_doc_amt}，价税合计：{item_gross_doc_amt}"
            assert clearing_qty == 0, f"明细行{i+1}过账后钩稽中数量应为0，实际为：{clearing_qty}"
            assert cleared_qty == item_qty, f"明细行{i+1}过账后已钩稽数量应等于数量，已钩稽：{cleared_qty}，数量：{item_qty}"
            assert clearing_base_amt == 0, f"明细行{i+1}过账后钩稽中金额-本位币应为0，实际为：{clearing_base_amt}"
            assert cleared_base_amt == item_gross_base_amt, f"明细行{i+1}过账后已钩稽金额-本位币应等于价税合计金额-本位币，已钩稽：{cleared_base_amt}，价税合计：{item_gross_base_amt}"
            assert item_clearing_status == "CLEARED", f"明细行{i+1}过账后行钩稽状态应为CLEARED，实际为：{item_clearing_status}"

    @case_decorator(
        story="应收单创建",
        title="创建并过账标准应收单",
        description="创建标准应收单并过账，为后续创建销售发票做准备",
        severity="critical",
        order=1,
        smoke=True,
        tags=["ar", "save", "post"]
    )
    def test_ar_create_and_post(self):
        try:
            with a.step("创建标准应收单"):
                now_ts = int(datetime.now().timestamp() * 1000)
                request_body = {}
                self.create_ar_request_body(now_ts, request_body)
                
                result = {}
                self.send_api_request("AR-应收单保存服务", request_body, result)
                ar_doc_id = ParamUtil.extract_id(result)
                assert ar_doc_id, "创建应收单失败：未获取到单据ID"
                
                TestArDocCreateSb.ar_info.update({
                    "ar_doc_id": ar_doc_id,
                    "request_body": request_body,
                    "total_amt": request_body.get("grossDocAmt", 0)  # 添加total_amt用于后续验证
                })

            with a.step("提交并过账应收单"):
                ar_head_code = self.mock_data.generate_unique_code("AR")
                base_request = request_body.copy()
                base_request.update({
                    "id": ar_doc_id,
                    "arStatus": "CONFIRM",
                    "arHeadCode": ar_head_code
                })
                
                submit_result = {}
                post_result = {}
                self.send_api_request("AR-应收单-列表提交服务", base_request, submit_result)
                self.send_api_request("应收单-过账-异步服务", base_request, post_result)
                
                TestArDocCreateSb.ar_info["ar_head_code"] = ar_head_code

            with a.step("验证过账状态"):
                status_result = {}
                self.wait_for_ar_status(ar_head_code, "DONE", status_result)
                assert status_result.get("success") and status_result.get("status") == "DONE", \
                    f"过账后单据状态应为DONE，实际为：{status_result.get('status')}"
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
        
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售发票创建",
        title="基于应收单创建销售发票",
        description="使用SB_CONVERT_BY_AR_ASYNC_EVENT_SERVICE基于应收单创建销售发票",
        severity="critical",
        order=2,
        smoke=True,
        tags=["ar", "sb", "create"]
    )
    def test_sb_create_by_ar(self):
        try:
            with a.step("基于应收单创建销售发票"):
                ar_doc_id = TestArDocCreateSb.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行创建应收单用例，确保ar_doc_id已生成"
                
                bil_code = self.mock_data.generate_unique_code("auto")
                result = {}
                self._create_sb_by_ar(ar_doc_id, bil_code, result)
                
                response_data = result.get("data", {})
                assert response_data, "创建销售发票失败：未获取到响应数据"
                
                TestArDocCreateSb.ar_info.update({
                    "bil_code": bil_code,
                    "sb_result": response_data
                })
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单收票金额验证",
        title="验证应收单收票中金额更新",
        description="等待销售发票创建异步任务完成后，验证应收单收票中金额是否正确更新",
        severity="critical",
        order=3,
        smoke=True,
        tags=["ar", "sb", "verify", "billing", "async"]
    )
    def test_ar_billing_amt_verify(self):
        try:
            with a.step("等待销售发票创建异步任务完成"):
                ar_doc_id = TestArDocCreateSb.ar_info.get("ar_doc_id")
                assert ar_doc_id, "请先执行创建应收单用例，确保ar_doc_id已生成"
                
                task_result = {}
                self._wait_for_sb_task_completion(ar_doc_id, task_result)
                
                ar_data = task_result.get("ar_data", {})
                task_status = task_result.get("status", "UNKNOWN")
                
                a.json({
                    "arDocId": ar_doc_id,
                    "asyncExecutionStatus": ar_data.get("asyncExecutionStatus"),
                    "taskStatus": task_status,
                    "billingDocAmt": ar_data.get("billingDocAmt", 0),
                    "grossDocAmt": ar_data.get("grossDocAmt", 0)
                }, "异步任务执行情况")
                
                if task_status == "TIMEOUT":
                    a.text("警告：等待异步任务完成超时，继续进行验证", "超时警告")
                elif task_status.startswith("FAILED"):
                    a.text(f"异步任务执行失败：{task_status}", "任务失败信息")

            with a.step("验证应收单收票中金额"):
                verification_result = {}
                self._verify_ar_billing_amounts(ar_data, verification_result)
                
                TestArDocCreateSb.ar_info.update({
                    "ar_billing_data": ar_data,
                    "billing_verification_result": verification_result
                })
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售发票生成验证",
        title="验证销售发票是否真的生成",
        description="通过分页服务查询销售发票，验证销售发票是否真的生成",
        severity="critical",
        order=4,
        smoke=True,
        tags=["ar", "sb", "verify", "creation"]
    )
    def test_sb_creation_verify(self):
        try:
            with a.step("获取查询参数"):
                ar_doc_id = TestArDocCreateSb.ar_info.get("ar_doc_id")
                bil_code = TestArDocCreateSb.ar_info.get("bil_code")
                
                assert ar_doc_id, "请先执行创建应收单用例，确保ar_doc_id已生成"
                assert bil_code, "未找到bil_code，请先执行创建销售发票用例"

            with a.step("通过分页服务查询销售发票"):
                query_result = {}
                self._query_sb_by_paging(bil_code, query_result)
                
                sb_record = query_result.get("record")
                assert sb_record, f"未查询到bil_code为[{bil_code}]的销售发票记录，可能销售发票创建失败"

            with a.step("验证销售发票状态和信息"):
                sb_verification = {}
                self._verify_sb_record(sb_record, bil_code, sb_verification)
                
                TestArDocCreateSb.ar_info.update({
                    "sb_record_from_api": sb_record,
                    "sb_head_code": sb_verification['actualSbHeadCode'],
                    "sb_id": sb_verification['actualSbId']
                })
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售发票提交",
        title="提交销售发票",
        description="使用SB_SUBMIT_WITH_HEAD_EVENT_SERVICE提交销售发票并验证提交成功",
        severity="critical",
        order=5,
        smoke=True,
        tags=["sb", "submit", "success"]
    )
    def test_sb_submit(self):
        try:
            with a.step("获取销售发票信息"):
                sb_id = TestArDocCreateSb.ar_info.get("sb_id")
                sb_record = TestArDocCreateSb.ar_info.get("sb_record_from_api")
                bil_code = TestArDocCreateSb.ar_info.get("bil_code")
                
                assert sb_id, "请先执行销售发票创建验证用例，确保sb_id已生成"
                assert sb_record, "请先执行销售发票创建验证用例，确保sb_record已获取"
                assert bil_code, "未找到bil_code，请先执行创建销售发票用例"

            with a.step("通过数据工厂查询销售发票完整信息包括税额"):
                # 使用数据工厂查询当前销售发票的完整信息，包括税额
                sb_db_info = self.ar_factory.query_sales_invoice_by_bil_code(bil_code)
                assert sb_db_info, f"数据工厂未查询到bil_code为[{bil_code}]的销售发票信息"
                
                # 提取税额信息
                bil_doc_tax = sb_db_info.get("bil_doc_tax", 0.0)
                bil_base_tax = sb_db_info.get("bil_base_tax", 0.0)
                
                # 更新sb_record以包含税额信息
                sb_record.update({
                    "bilDocTax": bil_doc_tax,
                    "bilBaseTax": bil_base_tax
                })
                
                a.json(sb_db_info, "数据工厂查询的销售发票完整信息")

            with a.step("发送销售发票提交请求"):
                api_path = ParamUtil.get_api_path(self.apis, "SB-销售发票-列表提交服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                sb_params = {}
                self.build_sb_request_params(sb_record, sb_id, bil_code, "CONFIRM", sb_params)
                core_fields = sb_params["core_fields"]
                request_data = sb_params["request_data"]
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, core_fields, ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, request_data)
                filtered_params = convert_decimal_to_float(filtered_params)
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                success = result.get("success")
                assert success is True, f"销售发票提交失败，success字段应为True，实际为：{success}"
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")

            with a.step("验证销售发票状态更新"):
                time.sleep(2)
                
                query_result = {}
                self._query_sb_by_paging(bil_code, query_result, max_wait=15, interval=2)
                
                updated_sb_record = query_result.get("record")
                assert updated_sb_record, f"提交后未能查询到bil_code为[{bil_code}]的销售发票记录"
                
                updated_status = updated_sb_record.get("sbStatus")
                assert updated_status == "CONFIRM", f"提交后销售发票状态应为CONFIRM，实际为：{updated_status}"

            with a.step("保存提交结果"):
                TestArDocCreateSb.ar_info.update({
                    "updated_sb_record": updated_sb_record,
                    "final_sb_status": updated_status,
                    "bil_doc_tax": bil_doc_tax,  # 保存税额信息以供后续用例使用
                    "bil_base_tax": bil_base_tax
                })
                
                a.json({
                    "bilCode": bil_code,
                    "bil_doc_tax": bil_doc_tax,
                    "bil_base_tax": bil_base_tax,
                    "success": success,
                    "final_status": updated_status,
                    "submit_result": "PASSED"
                }, "提交结果汇总")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售发票过账",
        title="销售发票过账校验与自动钩稽",
        description="校验过账金额是否与发票金额合计值一致，如果不一致则执行自动钩稽",
        severity="critical",
        order=6,
        smoke=True,
        tags=["sb", "post_validation", "auto_match"]
    )
    def test_sb_post_validation_and_auto_match(self):
        try:
            with a.step("获取销售发票信息"):
                sb_id = TestArDocCreateSb.ar_info.get("sb_id")
                sb_record = TestArDocCreateSb.ar_info.get("updated_sb_record")
                bil_code = TestArDocCreateSb.ar_info.get("bil_code")
                
                assert sb_id, "请先执行销售发票提交用例，确保sb_id已生成"
                assert sb_record, "请先执行销售发票提交用例，确保sb_record已获取"
                assert bil_code, "未找到bil_code，请先执行创建销售发票用例"
                
                current_status = sb_record.get("sbStatus")
                assert current_status == "CONFIRM", f"销售发票状态应为CONFIRM才能过账，当前状态：{current_status}"

            with a.step("执行销售发票过账校验"):
                # 获取校验接口配置
                val_api_path = ParamUtil.get_api_path(self.apis, "销售发票-校验是否需要强制钩稽服务")
                val_params, val_url = ParamUtil.get_api_params(self.api_params, val_api_path)
                
                # 构建校验请求参数
                val_sb_params = {}
                self.build_sb_request_params(sb_record, sb_id, bil_code, sb_record.get("sbStatus"), val_sb_params)
                val_core_fields = val_sb_params["core_fields"]
                val_request_data = val_sb_params["request_data"]
                
                val_filtered_params = ParamUtil.filter_post_body_fields(
                    val_params, val_core_fields, ["params", "request"]
                )
                ParamUtil.set_request_params(val_filtered_params, val_request_data)
                val_filtered_params = convert_decimal_to_float(val_filtered_params)
                
                # 发送校验请求
                val_result = self.http.post(val_url, json=val_filtered_params)
                self.assert_util.assert_response_success(val_result)
                
                # 获取校验结果
                validation_data = val_result.get("data", {})
                result_flag = validation_data.get("result", True)
                
                a.json(val_filtered_params, "过账校验请求")
                a.json(val_result, "过账校验响应")

            with a.step("根据校验结果处理过账流程"):
                if result_flag is False:
                    # result=false表示过账金额与发票金额一致，执行自动钩稽接口
                    a.text("校验结果：过账金额与发票金额一致，自动执行钩稽接口", "校验结果")
                    
                    # 获取自动钩稽接口配置
                    match_api_path = ParamUtil.get_api_path(self.apis, "销售发票自动钩稽-异步服务")
                    match_params, match_url = ParamUtil.get_api_params(self.api_params, match_api_path)
                    
                    # 构建自动钩稽请求参数（使用相同的请求数据）
                    match_filtered_params = ParamUtil.filter_post_body_fields(
                        match_params, val_core_fields, ["params", "request"]
                    )
                    ParamUtil.set_request_params(match_filtered_params, val_request_data)
                    match_filtered_params = convert_decimal_to_float(match_filtered_params)
                    
                    # 发送自动钩稽请求
                    match_result = self.http.post(match_url, json=match_filtered_params)
                    self.assert_util.assert_response_success(match_result)
                    
                    # 断言自动钩稽接口success字段
                    match_success = match_result.get("success")
                    assert match_success is True, f"销售发票自动钩稽失败，success应为True，实际为: {match_success}"
                    
                    # 保存结果
                    TestArDocCreateSb.ar_info.update({
                        "post_validation_result": "AUTO_MATCH_EXECUTED",
                        "auto_match_success": True,
                        "validation_response": val_result,
                        "auto_match_response": match_result
                    })
                    
                    a.json(match_filtered_params, "自动钩稽请求")
                    a.json(match_result, "自动钩稽响应")
                    a.json({
                        "bil_code": bil_code,
                        "validation_result": result_flag,
                        "auto_match_success": match_success,
                        "process_result": "AUTO_MATCH_COMPLETED"
                    }, "钩稽流程结果")
                    
                else:
                    # result=true表示需要强制钩稽，不包含该场景
                    a.text("校验结果：销售发票需要强制钩稽，该自动化用例不包含该场景", "校验结果")
                    
                    # 保存结果
                    TestArDocCreateSb.ar_info.update({
                        "post_validation_result": "FORCE_MATCH_REQUIRED",
                        "auto_match_required": False,
                        "validation_response": val_result
                    })
                    
                    a.json({
                        "bil_code": bil_code,
                        "validation_result": result_flag,
                        "process_result": "FORCE_MATCH_REQUIRED_SKIPPED",
                        "message": "销售发票需要强制钩稽，该自动化用例不包含该场景"
                    }, "校验流程结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售发票过账状态验证",
        title="验证销售发票自动钩稽后状态",
        description="查询销售发票异步执行状态、发票状态、已钩稽金额是否正确更新",
        severity="critical",
        order=7,
        smoke=True,
        tags=["sb", "post_match_status", "final_verification"]
    )
    def test_verify_sb_status_after_auto_match(self):
        try:
            with a.step("获取销售发票信息并查询状态"):
                bil_code = TestArDocCreateSb.ar_info.get("bil_code")
                expected_amount = TestArDocCreateSb.ar_info.get("total_amt")
                
                assert bil_code, "未找到bil_code，请先执行创建销售发票用例"
                assert expected_amount, "未找到发票金额，请先执行创建销售发票用例"
                
                # 通过分页查询接口获取销售发票最新状态
                query_result = {}
                self._query_sb_by_paging(bil_code, query_result, max_wait=15, interval=3)
                
                sb_record = query_result.get("record")
                assert sb_record, f"未查询到bil_code为[{bil_code}]的销售发票记录"

            with a.step("验证销售发票关键状态"):
                # 获取关键状态字段
                async_status = sb_record.get("asyncExecutionStatus")
                sb_status = sb_record.get("sbStatus") 
                cleared_doc_amt = sb_record.get("clearedDocAmt", 0)
                confirm_status = sb_record.get("confirmStatus")
                
                # 记录当前状态
                current_status = {
                    "bil_code": bil_code,
                    "async_execution_status": async_status,
                    "sb_status": sb_status,
                    "cleared_doc_amt": cleared_doc_amt,
                    "expected_amount": expected_amount,
                    "confirm_status": confirm_status
                }
                
                a.json(current_status, "销售发票当前状态")

            with a.step("执行状态断言"):
                # 断言1：异步执行状态必须为SUCCEEDED
                assert async_status == "SUCCEEDED", f"异步执行状态应为SUCCEEDED，实际为：{async_status}"
                
                # 断言2：发票状态必须为DONE
                assert sb_status == "DONE", f"发票状态应为DONE，实际为：{sb_status}"
                
                # 断言3：已钩稽金额必须等于发票金额合计
                assert cleared_doc_amt == expected_amount, f"已钩稽金额应等于发票金额合计，已钩稽：{cleared_doc_amt}，发票金额：{expected_amount}"

            with a.step("保存验证结果"):
                TestArDocCreateSb.ar_info.update({
                    "final_async_status": async_status,
                    "final_sb_status": sb_status,
                    "final_cleared_amount": cleared_doc_amt,
                    "final_confirm_status": confirm_status,
                    "sb_status_verification": "PASSED"
                })
                
                a.json({
                    "bil_code": bil_code,
                    "verification_result": "SUCCESS",
                    "validation_summary": {
                        "异步执行状态": f"{async_status} ✓",
                        "发票状态": f"{sb_status} ✓", 
                        "已钩稽金额": f"{cleared_doc_amt} = {expected_amount} ✓"
                    }
                }, "销售发票状态验证成功")
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="应收单收票金额验证",
        title="验证销售发票过账后应收单收票金额和钩稽状态更新",
        description="验证销售发票过账后，应收单头表和明细行的收票金额、钩稽状态正确更新",
        severity="critical",
        order=8,
        smoke=True,
        tags=["ar", "sb", "post", "billing", "clearing"]
    )
    def test_ar_billing_clearing_verify(self):
        try:
            with a.step("获取应收单信息"):
                ar_doc_id = TestArDocCreateSb.ar_info.get("ar_doc_id")
                bil_code = TestArDocCreateSb.ar_info.get("bil_code")
                
                assert ar_doc_id, "请先执行创建应收单用例，确保ar_doc_id已生成"
                assert bil_code, "未找到bil_code，请先执行创建销售发票用例"

            with a.step("等待销售发票过账异步任务完成"):
                time.sleep(10)
                a.text("等待销售发票过账异步任务处理完成...", "等待状态")

            with a.step("查询应收单最新状态"):
                ar_detail = {}
                self.query_ar_detail(ar_doc_id, ar_detail)
                
                assert ar_detail, f"未查询到ar_doc_id为[{ar_doc_id}]的应收单记录"
                
                billing_doc_amt = ar_detail.get("billingDocAmt", 0)
                billed_doc_amt = ar_detail.get("billedDocAmt", 0)
                billing_clearing_status = ar_detail.get("billingClearingStatus")
                gross_doc_amt = ar_detail.get("grossDocAmt", 0)
                ar_items = ar_detail.get("arItems", [])
                
                a.json({
                    "arDocId": ar_doc_id,
                    "bilCode": bil_code,
                    "应收单头表状态": {
                        "开票中金额": billing_doc_amt,
                        "已开票金额": billed_doc_amt,
                        "价税合计总额": gross_doc_amt,
                        "开票钩稽状态": billing_clearing_status
                    },
                    "应收明细行数量": len(ar_items)
                }, "应收单状态信息")

            with a.step("验证应收单头表收票金额和钩稽状态"):
                assert billing_doc_amt == 0, f"过账后开票中金额应为0，实际为：{billing_doc_amt}"
                assert billed_doc_amt == gross_doc_amt, f"过账后已开票金额应等于价税合计总额，已开票：{billed_doc_amt}，价税合计：{gross_doc_amt}"
                assert billing_clearing_status == "CLEARED", f"过账后开票钩稽状态应为CLEARED，实际为：{billing_clearing_status}"

            with a.step("验证应收单明细行钩稽金额和状态"):
                self._verify_ar_item_clearing_status(ar_items)

            with a.step("保存验证结果"):
                TestArDocCreateSb.ar_info.update({
                    "ar_billing_clearing_data": ar_detail
                })
                
                a.json(TestArDocCreateSb.ar_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestArDocCreateSb()
    test.setup_class()
    test.test_ar_create_and_post()
    test.test_sb_create_by_ar()
    test.test_ar_billing_amt_verify()
    test.test_sb_creation_verify()
    test.test_sb_submit()
    test.test_sb_post_validation_and_auto_match()
    test.test_verify_sb_status_after_auto_match()
    test.test_ar_billing_clearing_verify() 