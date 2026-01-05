"""
标准采购订单无审批流程测试
"""
import allure
import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.report_util import a, case_decorator
from data_factory.pur_po_factory import PurPoFactory
from utils.param_util import ParamUtil


@allure.epic("采购管理")
@allure.feature("标准采购订单")
class TestPoManagement(ScmPurBaseTest):
    """标准采购订单测试类"""
    
    TEST_REMARK = "执行自动化测试备注"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_id = None
        cls.po_code = None
        cls.pur_remark = None
        
        if cls.md_cache_data:
            finp_list = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP") or []
            mat_info = finp_list[0] if finp_list else {}
            org_info = cls.md_cache_data.get("org_info", {})
            partner_info = cls.md_cache_data.get("partner_info", {})
            
            cls.mat_id = mat_info.get("id")
            cls.mat_code = mat_info.get("mat_code")
            
            inv_org_info = org_info.get("inv_org_info") or []
            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None
            
            inv_loc_info = org_info.get("inv_loc_info") or []
            cls.inv_loc_id = inv_loc_info[0].get("id") if inv_loc_info else None
            
            pur_org_info = org_info.get("pur_org_info") or []
            cls.pur_org_id = pur_org_info[0].get("id") if pur_org_info else None
            
            gr_come_org_info = org_info.get("gr_come_org_info") or []
            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            
            vend_info = partner_info.get("vend_info") or []
            cls.vend_id = vend_info[0].get("id") if vend_info else None
            
            employee_info = org_info.get("employee_info") or []
            cls.pur_employee_id = employee_info[0].get("id") if employee_info else None
        
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.pur_curr_id = currency_info[0].get("curr_id")
            else:
                cls.pur_curr_id = None
            
            uom_info = cls.init_data.get("uom_info", {})
            qty_uom_info = uom_info.get("qty_uom_info") or []
            if qty_uom_info:
                cls.uom_pur_id = qty_uom_info[0].get("uom_id")
            else:
                cls.uom_pur_id = None
            
            tax_info = cls.init_data.get("tax_info") or []
            if tax_info:
                cls.tax_rate_id = tax_info[0].get("id")
            else:
                cls.tax_rate_id = None
        
        if cls.pur_cache_data:
            pur_config = cls.pur_cache_data.get("pur_config", {})
            po_type_info = pur_config.get("po_type_info") or []
            if po_type_info:
                cls.po_type_id = po_type_info[0].get("id")
            else:
                cls.po_type_id = None
            
            po_item_types = pur_config.get("po_item_type_info", [])
            cls.po_item_type_id = next(
                (item.get("id") for item in po_item_types if item.get("po_item_type") == "STND"),
                None
            )
        
        cls.logger.info("标准采购订单测试类初始化完成")
    
    
    def _get_po_detail_by_id(self, po_id):
        """获取订单详情"""
        api_path = self.get_api_path("(系统)查询数据详情服务")
        _, url = self.get_api_params(api_path)
        
        params = {
            "serviceKey": "SCM_PUR$SYS_FindDataByIdService",
            "params": {
                "request": {"id": po_id},
                "modelKey": "SCM_PUR$pur_po_head_tr"
            }
        }
        
        response = self.http.post(
            url,
            json=params,
            params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_po_head_tr"}
        )
        self.assert_util.assert_response_data(response)
        
        po_detail = response.get("data", {}).get("data", {})
        if not po_detail:
            raise ValueError(f"未获取到订单详情数据: po_id={po_id}")
        
        return po_detail
    
    def _verify_po_status(self, expected_status, status_desc):
        """验证订单状态"""
        query_sql = "SELECT id, document_status, deleted FROM pur_po_head_tr WHERE id = %s"
        result = self.db.query(query_sql, [self.__class__.po_id])
        
        assert result, "数据库未查询到订单数据"
        
        document_status = result[0].get("document_status")
        assert document_status == expected_status, \
            f"订单状态不符合预期: 期望={expected_status}, 实际={document_status}"
        
        self.logger.info(f"订单{status_desc}成功: po_id={self.__class__.po_id}, status={document_status}")
        return result
    
    @case_decorator(
        story="标准采购订单",
        title="创建标准采购订单",
        description="创建标准采购订单,验证创建成功",
        severity="critical",
        file_level_order=1,
        tags=["采购", "标准订单", "创建"]
    )
    def test_create_standard_po(self):
        try:
            current_ts = int(datetime.now().timestamp() * 1000)
            
            mat_items = [{
                "mat_id": str(self.mat_id),
                "mat_code": self.mat_code,
                "inv_org_id": str(self.inv_org_id),
                "inv_loc_id": str(self.inv_loc_id),
                "uom_pur_id": str(self.uom_pur_id),
                "qty": 12,
                "price": 11,
                "po_item_type_id": str(self.po_item_type_id),
                "tax_rate_id": str(self.tax_rate_id),
                "delivery_date": current_ts,
                "note": self.TEST_REMARK
            }]
            
            po_factory = PurPoFactory(
                http_client=self.http,
                apis=self.apis,
                api_params=self.api_params,
                mock_util=self.mock_util,
                logger=self.logger,
                init_data=self.init_data,
                md_cache_data=self.md_cache_data,
                pur_cache_data=self.pur_cache_data
            )
            
            result = po_factory.create_standard_po(
                mat_items=mat_items,
                business_date=current_ts,
                pur_remark=self.TEST_REMARK
            )
            
            self.__class__.pur_remark = self.TEST_REMARK
            a.json(result.get("response", {}), "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="查询采购订单列表",
        description="查询采购订单列表,获取第一条数据的ID和编码",
        severity="critical",
        file_level_order=2,
        tags=["采购", "标准订单", "查询"]
    )
    def test_query_po_list(self):
        try:
            api_path = self.get_api_path("采购订单分页查询ACTION服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"fieldAlias": "createdAt", "sortType": "DESC"}
                    ],
                    "conditionItems": None
                },
                "fields": [
                    {"name": "poCode", "type": "TEXT"},
                    {"name": "poType", "type": "OBJECT"},
                    {"name": "vendId", "type": "OBJECT"},
                    {"name": "documentStatus", "type": "SELECT"},
                    {"name": "businessStatus", "type": "SELECT"},
                    {"name": "comOrgId", "type": "OBJECT"},
                    {"name": "purOrgId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "poStatusDel", "type": "SELECT"},
                    {"name": "createdBy", "type": "OBJECT"},
                    {"name": "updatedBy", "type": "OBJECT"}
                ],
                "systemParams": None
            })
            
            response = self.http.post(
                url,
                json=filtered_params,
                params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert records, "未查询到采购订单数据"
            
            first_record = records[0]
            self.__class__.po_id = first_record.get("id")
            self.__class__.po_code = first_record.get("poCode")
            pur_remark = first_record.get("purRemark")
            document_status = first_record.get("documentStatus")
            
            assert document_status == "EFFECT", \
                f"单据状态不符合预期: 期望=EFFECT, 实际={document_status}"
            
            # 只有当 pur_remark 存在且 TEST_REMARK 已设置时才断言
            if self.__class__.pur_remark and pur_remark:
                assert pur_remark == self.__class__.pur_remark, \
                    f"采购备注不匹配: 期望={self.__class__.pur_remark}, 实际={pur_remark}"
            
            a.text(
                f"订单ID: {self.__class__.po_id}\n"
                f"订单编码: {self.__class__.po_code}\n"
                f"备注: {pur_remark}\n"
                f"单据状态: {document_status}",
                "订单信息"
            )
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="查询采购订单详情",
        description="根据订单ID查询采购订单详情",
        severity="critical",
        file_level_order=3,
        tags=["采购", "标准订单", "查询"]
    )
    def test_query_po_detail(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            api_path = self.get_api_path("(系统)查询数据详情服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$SYS_FindDataByIdService",
                "params": {
                    "request": {"id": self.__class__.po_id},
                    "modelKey": "SCM_PUR$pur_po_head_tr"
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_po_head_tr"}
            )
            
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", {})
            assert result_data, "详情数据为空"
            
            document_status = result_data.get("documentStatus")
            assert document_status == "EFFECT", \
                f"单据状态不符合预期: 期望=EFFECT, 实际={document_status}"
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="交货冻结",
        description="对采购订单进行交货冻结",
        severity="critical",
        file_level_order=4,
        tags=["采购", "标准订单", "冻结"]
    )
    def test_freeze_po_delivery(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-订单头-冻结服务")
            params_template, url = self.get_api_params(api_path)
            
            # 使用参数模板，确保结构正确
            if params_template:
                request_params = params_template.copy()
                request_params["params"]["request"] = po_detail
            else:
                # 如果模板不存在，使用手动构造（向后兼容）
                request_params = {
                    "serviceKey": "SCM_PUR$PUR_PO_FREEZE_SERVICE",
                    "params": {
                        "request": po_detail
                    }
                }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            query_sql = "SELECT id, delivery_frozen FROM pur_po_head_tr WHERE id = %s"
            result = self.db.query(query_sql, [self.__class__.po_id])
            
            assert result, "数据库未查询到订单数据"
            
            delivery_frozen = result[0].get("delivery_frozen")
            assert delivery_frozen == 1, \
                f"交货冻结状态不符合预期: 期望=1, 实际={delivery_frozen}"
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="标准采购订单",
        title="交货解冻",
        description="对采购订单进行交货解冻",
        severity="critical",
        file_level_order=5,
        tags=["采购", "标准订单", "解冻"]
    )
    def test_unfreeze_po_delivery(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-订单头-取消冻结服务")
            params_template, url = self.get_api_params(api_path)
            
            # 使用参数模板，确保结构正确
            if params_template:
                request_params = params_template.copy()
                request_params["params"]["request"] = po_detail
            else:
                # 如果模板不存在，使用手动构造（向后兼容）
                request_params = {
                    "serviceKey": "SCM_PUR$PUR_PO_HEAD_CANCEL_FREEZE_SERVICE",
                    "params": {
                        "request": po_detail
                    }
                }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            query_sql = "SELECT id, delivery_frozen FROM pur_po_head_tr WHERE id = %s"
            result = self.db.query(query_sql, [self.__class__.po_id])
            
            assert result, "数据库未查询到订单数据"
            
            delivery_frozen = result[0].get("delivery_frozen")
            assert delivery_frozen == 0, \
                f"交货解冻状态不符合预期: 期望=0, 实际={delivery_frozen}"
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="标准采购订单",
        title="未交货完成订单失败",
        description="验证未交货状态下完成采购订单失败",
        severity="normal",
        file_level_order=6,
        tags=["采购", "标准订单", "完成", "失败校验"]
    )
    def test_finish_po_without_delivery(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("采购订单完成")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_FINISHED_SERVICE",
                "params": {
                    "request": po_detail
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            success = response.get("success", True)
            assert success is False, "预期完成操作应该失败，但实际返回成功"
            
            err_info = response.get("err", {})
            err_code = err_info.get("code", "")
            err_msg = err_info.get("msg", "")
            
            assert err_code == "po.item.delivery.not.completed", \
                f"错误码不符合预期: 期望=po.item.delivery.not.completed, 实际={err_code}"
            assert "交货未完成" in err_msg or "不允许完成" in err_msg, \
                f"错误信息不符合预期: {err_msg}"
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"错误码: {err_code}\n错误信息: {err_msg}", "业务校验")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="作废采购订单",
        description="作废采购订单并验证状态",
        severity="critical",
        file_level_order=7,
        tags=["采购", "标准订单", "作废"]
    )
    def test_abolish_po(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            api_path = self.get_api_path("PO-订单-作废服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_ABOLISHED_SERVICE",
                "params": {
                    "request": {"id": self.__class__.po_id}
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            result = self._verify_po_status("ABOLISH", "作废")
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="取消提交采购订单",
        description="创建新订单后取消提交并验证状态为草稿",
        severity="critical",
        file_level_order=8,
        tags=["采购", "标准订单", "取消提交"]
    )
    def test_cancel_submit_po(self):
        try:
            self.test_create_standard_po()
            self.test_query_po_list()
            
            if not self.__class__.po_id:
                raise ValueError("创建订单后未获取到po_id")
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-取消提交服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_CANCEL_SUBMIT_EVENT_SERVICE",
                "params": {
                    "request": po_detail
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            result = self._verify_po_status("DRAFT", "取消提交")
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="导出采购订单",
        description="导出采购订单数据",
        severity="normal",
        file_level_order=9,
        tags=["采购", "标准订单", "导出"]
    )
    def test_export_po(self):
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            api_path = self.get_api_path("采购订单-H-导入导出任务管理接口-提交导出任务")
            _, url = self.get_api_params(api_path)
            
            timestamp = self.mock_util.get_timestamp()
            task_name = f"采购订单-{self.nickname}-{timestamp}-导出"
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_HEAD_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_PUR$pur_po_head_tr",
                            "modelName": "采购订单-H",
                            "sheetNo": 0,
                            "sheetName": "采购订单-H",
                            "headerConfigList": [
                                {"name": "单据编号", "type": "TEXT", "field": "poCode"},
                                {"name": "单据类型", "type": "TEXT", "field": "poType"},
                                {"name": "供应商,伙伴名称", "type": "TEXT", "field": "vendId.name"},
                                {"name": "含税总金额", "type": "DECIMAL", "field": "totalAmountGross", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "不含税金额", "type": "DECIMAL", "field": "amountNet", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "税额", "type": "DECIMAL", "field": "taxAmount", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "采购组织", "type": "TEXT", "field": "purOrgId.orgName"},
                                {"name": "单据状态", "type": "ENUM", "field": "documentStatus", "multiSelect": False},
                                {"name": "业务状态", "type": "ENUM", "field": "businessStatus", "multiSelect": False},
                                {"name": "交货状态", "type": "ENUM", "field": "poStatusDel", "multiSelect": False},
                                {"name": "采购员", "type": "TEXT", "field": "purEmployee.name"},
                                {"name": "创建人", "type": "TEXT", "field": "createdBy.nickname"},
                                {"name": "创建时间", "type": "DATE", "field": "createdAt"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "PO-listView-table",
                        "viewKey": "SCM_PUR$TERP_MIGRATE_PO:5FK5Ssd3Ov6z1uVTvum6n",
                        "sceneKey": "SCM_PUR$TERP_MIGRATE_PO",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.__class__.po_id]
                                            }
                                        }
                                    },
                                    "sortOrders": [
                                        {"fieldAlias": "updatedAt", "sortType": "DESC"},
                                        {"fieldAlias": "createdAt", "sortType": "DESC"}
                                    ],
                                    "pageNo": 1,
                                    "pageSize": 20
                                }
                            },
                            "selectFields": [
                                {"field": "poCode"},
                                {"field": "poType"},
                                {"field": "totalAmountGross"},
                                {"field": "amountNet"},
                                {"field": "taxAmount"},
                                {"field": "documentStatus"},
                                {"field": "businessStatus"},
                                {"field": "poStatusDel"},
                                {"field": "createdAt"},
                                {"field": "vendId", "selectFields": [{"field": "name"}]},
                                {"field": "purOrgId", "selectFields": [{"field": "orgName"}]},
                                {"field": "purEmployee", "selectFields": [{"field": "name"}]},
                                {"field": "createdBy", "selectFields": [{"field": "nickname"}]}
                            ],
                            "modelKey": "SCM_PUR$pur_po_head_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_PUR$pur_po_head_tr",
                        "modelName": "采购订单-H",
                        "containerKey": "PO-listView-table",
                        "viewKey": "SCM_PUR$TERP_MIGRATE_PO:5FK5Ssd3Ov6z1uVTvum6n",
                        "sceneKey": "SCM_PUR$TERP_MIGRATE_PO"
                    }
                }
            }
            
            response = self.http.post(url, json=request_params, params={"tmodule": "SCM_PUR"})
            self.assert_util.assert_response_success(response)
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="删除采购订单",
        description="删除草稿状态的采购订单并验证deleted字段",
        severity="critical",
        file_level_order=10,
        tags=["采购", "标准订单", "删除"]
    )
    def test_delete_po(self):
        try:
            if not self.__class__.po_id:
                raise ValueError("未找到可删除的订单ID")
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-删除订单服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PO_DELETE_DRAFT_PO_BY_ID_EVENT_SERVICE",
                "params": {
                    "request": po_detail
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            query_sql = "SELECT id, document_status, deleted FROM pur_po_head_tr WHERE id = %s"
            result = self.db.query(query_sql, [self.__class__.po_id])
            
            assert result, "数据库未查询到订单数据"
            
            deleted_value = result[0].get("deleted")
            assert deleted_value != 0, \
                f"订单删除标记不符合预期: 期望 deleted != 0, 实际 deleted={deleted_value}"
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


 