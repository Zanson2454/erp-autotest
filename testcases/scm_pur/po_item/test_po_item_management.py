"""
采购订单行管理测试
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
@allure.feature("采购订单行")
class TestPoItemManagement(ScmPurBaseTest):
    """采购订单行管理测试类"""
    
    TEST_REMARK = "执行自动化测试备注"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.po_id = None
        cls.po_code = None
        cls.po_item_id = None
        cls.po_item_code = None
        cls.pur_remark = None
        
        if cls.md_cache_data:
            mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0]
            org_info = cls.md_cache_data.get("org_info", {})
            partner_info = cls.md_cache_data.get("partner_info", {})
            
            cls.mat_id = mat_info.get("id")
            cls.mat_code = mat_info.get("mat_code")
            cls.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id")
            cls.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id")
            cls.pur_org_id = org_info.get("pur_org_info", [{}])[0].get("id")
            cls.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id")
            cls.vend_id = partner_info.get("vend_info", [{}])[0].get("id")
            cls.pur_employee_id = org_info.get("employee_info", [{}])[0].get("id")
        
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
            cls.po_type_id = pur_config.get("po_type_info", [{}])[0].get("id")
            
            po_item_types = pur_config.get("po_item_type_info", [])
            cls.po_item_type_id = next(
                (item.get("id") for item in po_item_types if item.get("po_item_type") == "STND"),
                None
            )
        
        cls.logger.info("采购订单行管理测试类初始化完成")
    
    
    @case_decorator(
        story="采购订单行",
        title="创建标准采购订单",
        description="创建标准采购订单,用于后续订单行测试",
        severity="critical",
        file_level_order=1,
        tags=["采购", "订单行", "创建"]
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
        story="采购订单行",
        title="查询采购订单行列表",
        description="查询采购订单行列表,获取订单行信息",
        severity="critical",
        file_level_order=2,
        tags=["采购", "订单行", "查询"]
    )
    def test_query_po_item_list(self):
        try:
            api_path = self.get_api_path("分页查询订单行")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"fieldAlias": "updatedAt", "sortType": "DESC"},
                        {"fieldAlias": "createdAt", "sortType": "DESC"}
                    ],
                    "conditionItems": None
                }
            })
            
            response, _ = self.standard_api_call(
                api_key="分页查询订单行",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert records, "未查询到采购订单行数据"
            
            first_record = records[0]
            self.__class__.po_item_id = first_record.get("id")
            self.__class__.po_item_code = first_record.get("poItemCode")
            self.__class__.po_code = first_record.get("poCode")
            document_status = first_record.get("documentStatus")
            
            assert document_status == "EFFECT", \
                f"订单行状态不符合预期: 期望=EFFECT, 实际={document_status}"
            
            a.text(
                f"订单行ID: {self.__class__.po_item_id}\n"
                f"订单行编号: {self.__class__.po_item_code}\n"
                f"订单编号: {self.__class__.po_code}\n"
                f"单据状态: {document_status}",
                "订单行信息"
            )
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购订单行",
        title="导出采购订单行",
        description="导出采购订单行数据",
        severity="normal",
        file_level_order=3,
        tags=["采购", "订单行", "导出"]
    )
    def test_export_po_item(self):
        try:
            if not self.__class__.po_item_id:
                self.test_query_po_item_list()
            
            api_path = self.get_api_path("采购订单-ITEM-导入导出任务管理接口-提交导出任务")
            _, url = self.get_api_params(api_path)
            
            timestamp = self.mock_util.get_timestamp()
            task_name = f"采购订单行-{self.nickname}-{timestamp}-导出"
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_ITEM_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_PUR$pur_po_item_tr",
                            "modelName": "采购订单-ITEM",
                            "sheetNo": 0,
                            "sheetName": "采购订单-ITEM",
                            "headerConfigList": [
                                {"name": "订单行编号", "type": "TEXT", "field": "poItemCode"},
                                {"name": "订单编号", "type": "TEXT", "field": "poCode"},
                                {"name": "物料编码", "type": "TEXT", "field": "matCode"},
                                {"name": "物料名称", "type": "TEXT", "field": "matName"},
                                {"name": "数量", "type": "DECIMAL", "field": "qty", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "单价", "type": "DECIMAL", "field": "price", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "含税总金额", "type": "DECIMAL", "field": "totalAmountGross", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "库存组织", "type": "TEXT", "field": "invOrgId.orgName"},
                                {"name": "库存地点", "type": "TEXT", "field": "invLocId.locName"},
                                {"name": "单据状态", "type": "ENUM", "field": "documentStatus", "multiSelect": False},
                                {"name": "创建人", "type": "TEXT", "field": "createdBy.nickname"},
                                {"name": "创建时间", "type": "DATE", "field": "createdAt"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "PO-ITEM-listView-table",
                        "viewKey": "SCM_PUR$TERP_MIGRATE_PO_ITEM_OPERATE:MNz_nhH3Nti4vkk6a8J-z",
                        "sceneKey": "SCM_PUR$TERP_MIGRATE_PO_ITEM_OPERATE",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.__class__.po_item_id]
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
                                {"field": "poItemCode"},
                                {"field": "poCode"},
                                {"field": "matCode"},
                                {"field": "matName"},
                                {"field": "qty"},
                                {"field": "price"},
                                {"field": "totalAmountGross"},
                                {"field": "documentStatus"},
                                {"field": "createdAt"},
                                {"field": "invOrgId", "selectFields": [{"field": "orgName"}]},
                                {"field": "invLocId", "selectFields": [{"field": "locName"}]},
                                {"field": "createdBy", "selectFields": [{"field": "nickname"}]}
                            ],
                            "modelKey": "SCM_PUR$pur_po_item_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_PUR$pur_po_item_tr",
                        "modelName": "采购订单-ITEM",
                        "containerKey": "PO-ITEM-listView-table",
                        "viewKey": "SCM_PUR$TERP_MIGRATE_PO_ITEM_OPERATE:MNz_nhH3Nti4vkk6a8J-z",
                        "sceneKey": "SCM_PUR$TERP_MIGRATE_PO_ITEM_OPERATE"
                    }
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="采购订单-ITEM-导入导出任务管理接口-提交导出任务",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_success(response)
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

