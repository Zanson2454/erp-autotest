"""
采购计划行管理测试
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
@allure.feature("采购计划行")
class TestPoSchlManagement(ScmPurBaseTest):
    """采购计划行管理测试类"""
    
    TEST_REMARK = "执行自动化测试备注"
    TEST_QTY = 12  # 测试数量
    TEST_PRICE = 11  # 测试单价
    SPLIT_QTY = 3  # 拆分后的数量
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.po_schl_id = None
        cls.po_schl_code = None
        cls.po_code = None
        
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
        
        cls.logger.info("采购计划行管理测试类初始化完成")
    
    
    @case_decorator(
        story="采购计划行",
        title="创建标准采购订单（含计划行拆分）",
        description="创建标准采购订单,1个订单行拆成2个计划行",
        severity="critical",
        file_level_order=1,
        tags=["采购", "计划行", "创建", "拆分"]
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
                "qty": self.TEST_QTY,
                "price": self.TEST_PRICE,
                "po_item_type_id": str(self.po_item_type_id),
                "tax_rate_id": str(self.tax_rate_id),
                "delivery_date": current_ts,
                "note": self.TEST_REMARK,
                "po_schl_list": [
                    {"qty": 10, "delivery_date": current_ts},
                    {"qty": 2, "delivery_date": current_ts}
                ]
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
            
            a.text(
                f"订单行数量: {self.TEST_QTY}\n"
                f"计划行拆分: 10 + 2",
                "创建信息"
            )
            a.json(result.get("response", {}), "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购计划行",
        title="查询采购计划行列表",
        description="查询采购计划行列表,获取2条计划行信息",
        severity="critical",
        file_level_order=2,
        tags=["采购", "计划行", "查询"]
    )
    def test_query_po_schl_list(self):
        try:
            api_path = self.get_api_path("(系统)查询分页数据服务")
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
                    "sortOrders": None,
                    "systemParams": {
                        "viewCondition": {
                            "conditionKey": "iDlL48ASuNfmtmXQCJtc-",
                            "rightValues": {}
                        }
                    },
                    "conditionGroup": None
                }
            })
            
            if "params" in filtered_params:
                filtered_params["params"].pop("selectFields", None)
                filtered_params["params"]["modelKey"] = "SCM_PUR$pur_po_schl_tr"
            
            response, _ = self.standard_api_call(
                api_key="(系统)查询分页数据服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_po_schl_tr"}
            )
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert len(records) >= 2, f"计划行数量不足，期望>=2，实际={len(records)}"
            
            # 获取第1条和第2条计划行数据
            schl_1 = records[0]
            schl_2 = records[1]
            
            # 保存第1条计划行信息
            self.__class__.po_schl_id = schl_1.get("id")
            self.__class__.po_schl_code = schl_1.get("poSchlCode")
            self.__class__.po_code = schl_1.get("poCode")
            
            # 保存第2条计划行信息
            self.__class__.po_schl_id2 = schl_2.get("id")
            self.__class__.po_schl_code2 = schl_2.get("poSchlCode")
            self.__class__.po_code2 = schl_2.get("poCode")
            
            # 验证第1条计划行数量字段
            schl_1_qty_del = schl_1.get("poSchlQtyDel")
            schl_1_qty_ful = schl_1.get("poSchlQtyFul")
            schl_1_un_close = schl_1.get("unCloseQty")
            
            assert schl_1_qty_ful == 0.0, f"计划行1累计收货数量应为0，实际={schl_1_qty_ful}"
            assert schl_1_qty_del == schl_1_un_close, f"计划行1未清数量应等于计划数量"
            
            # 验证第2条计划行数量字段
            schl_2_qty_del = schl_2.get("poSchlQtyDel")
            schl_2_qty_ful = schl_2.get("poSchlQtyFul")
            schl_2_un_close = schl_2.get("unCloseQty")
            
            assert schl_2_qty_ful == 0.0, f"计划行2累计收货数量应为0，实际={schl_2_qty_ful}"
            assert schl_2_qty_del == schl_2_un_close, f"计划行2未清数量应等于计划数量"
            
            a.text(
                f"计划行1 - ID: {schl_1.get('id')}, 编号: {schl_1.get('poSchlCode')}, "
                f"计划数量: {schl_1_qty_del}, 累计收货: {schl_1_qty_ful}, 未清数量: {schl_1_un_close}\n"
                f"计划行2 - ID: {schl_2.get('id')}, 编号: {schl_2.get('poSchlCode')}, "
                f"计划数量: {schl_2_qty_del}, 累计收货: {schl_2_qty_ful}, 未清数量: {schl_2_un_close}\n"
                f"订单编号: {self.__class__.po_code}",
                "计划行信息"
            )
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购计划行",
        title="导出采购计划行",
        description="导出采购计划行数据",
        severity="normal",
        file_level_order=3,
        tags=["采购", "计划行", "导出"]
    )
    def test_export_po_schl(self):
        try:
            if not self.__class__.po_schl_id:
                try:
                    self.test_query_po_schl_list()
                except Exception as e:
                    pytest.skip(f"依赖测试失败，跳过导出测试: {str(e)}")
            
            api_path = self.get_api_path("采购订单-SCHL-导入导出任务管理接口-提交导出任务")
            _, url = self.get_api_params(api_path)
            
            timestamp = self.mock_util.get_timestamp()
            task_name = f"采购计划行-{self.nickname}-{timestamp}-导出"
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_SCHL_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_PUR$pur_po_schl_tr",
                            "modelName": "采购订单-SCHL",
                            "sheetNo": 0,
                            "sheetName": "采购订单-SCHL",
                            "headerConfigList": [
                                {"name": "计划行编号", "type": "TEXT", "field": "schl_code"},
                                {"name": "订单编号", "type": "TEXT", "field": "poCode"},
                                {"name": "物料编码", "type": "TEXT", "field": "matCode"},
                                {"name": "物料名称", "type": "TEXT", "field": "matName"},
                                {"name": "计划数量", "type": "DECIMAL", "field": "qty", "precision": 2, "precisionDisplayType": "FILL_ROUND"},
                                {"name": "交货日期", "type": "DATE", "field": "deliveryDate"},
                                {"name": "库存组织", "type": "TEXT", "field": "invOrgId.orgName"},
                                {"name": "库存地点", "type": "TEXT", "field": "invLocId.locName"},
                                {"name": "单据状态", "type": "ENUM", "field": "documentStatus", "multiSelect": False},
                                {"name": "创建人", "type": "TEXT", "field": "createdBy.nickname"},
                                {"name": "创建时间", "type": "DATE", "field": "createdAt"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_SCM$SCHL_VIEW-table-container-ERP_SCM$pur_po_schl_tr",
                        "viewKey": "SCM_PUR$SCHL_VIEW:list",
                        "sceneKey": "SCM_PUR$SCHL_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.__class__.po_schl_id]
                                            }
                                        }
                                    },
                                    "sortOrders": None,
                                    "pageNo": 1,
                                    "pageSize": 20
                                }
                            },
                            "selectFields": [
                                {"field": "schl_code"},
                                {"field": "poCode"},
                                {"field": "matCode"},
                                {"field": "matName"},
                                {"field": "qty"},
                                {"field": "deliveryDate"},
                                {"field": "documentStatus"},
                                {"field": "createdAt"},
                                {"field": "invOrgId", "selectFields": [{"field": "orgName"}]},
                                {"field": "invLocId", "selectFields": [{"field": "locName"}]},
                                {"field": "createdBy", "selectFields": [{"field": "nickname"}]}
                            ],
                            "modelKey": "SCM_PUR$pur_po_schl_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_PUR$pur_po_schl_tr",
                        "modelName": "采购订单-SCHL",
                        "containerKey": "ERP_SCM$SCHL_VIEW-table-container-ERP_SCM$pur_po_schl_tr",
                        "viewKey": "SCM_PUR$SCHL_VIEW:list",
                        "sceneKey": "SCM_PUR$SCHL_VIEW"
                    }
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="采购订单-SCHL-导入导出任务管理接口-提交导出任务",
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
    
    @case_decorator(
        story="采购计划行",
        title="合并采购计划行",
        description="合并2个采购计划行",
        severity="normal",
        file_level_order=4,
        tags=["采购", "计划行", "合并"]
    )
    def test_merge_po_schl(self):
        try:
            if not hasattr(self.__class__, 'po_schl_id') or not self.__class__.po_schl_id:
                try:
                    self.test_query_po_schl_list()
                except Exception as e:
                    pytest.skip(f"依赖测试失败，跳过合并测试: {str(e)}")
            if not hasattr(self.__class__, 'po_schl_id2') or not self.__class__.po_schl_id2:
                try:
                    self.test_query_po_schl_list()
                except Exception as e:
                    pytest.skip(f"依赖测试失败，跳过合并测试: {str(e)}")
            
            api_path = self.get_api_path("采购计划行-合并")
            _, url = self.get_api_params(api_path)
            '''
            ParamUtil.filter_post_body_fields 会把数据放到 params.request.records，
            但接口需要的是 params.records，所以需要手动设置,直接构造参数
            '''
            request_params = {
                "serviceKey": "SCM_PUR$PO_SCHEDULE_MERGE_SERVICE",
                "params": {
                    "records": [
                        {"id": self.__class__.po_schl_id},   
                        {"id": self.__class__.po_schl_id2}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="采购计划行-合并",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_data(response)
            
            merged_list = response.get("data", {}).get("data", {}).get("list", [])
            if not merged_list:
                raise ValueError("合并接口未返回数据")
            
            merged_record = merged_list[0]
            self.__class__.merged_schl_data = [merged_record]
            
            a.text(
                f"合并计划行1: {self.__class__.po_schl_id}\n"
                f"合并计划行2: {self.__class__.po_schl_id2}\n"
                f"合并后编号: {merged_record.get('poSchlCode')}\n"
                f"合并后数量: {merged_record.get('poSchlQtyDel')}",
                "合并信息"
            )
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购计划行",
        title="合并后保存采购计划行",
        description="保存合并后的采购计划行",
        severity="normal",
        file_level_order=5,
        tags=["采购", "计划行", "保存"]
    )
    def test_merge_save_po_schl(self):
        try:
            if not hasattr(self.__class__, 'merged_schl_data') or not self.__class__.merged_schl_data:
                try:
                    self.test_merge_po_schl()
                except Exception as e:
                    pytest.skip(f"依赖测试失败，跳过保存测试: {str(e)}")
            
            api_path = self.get_api_path("采购计划行-合并后保存")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PO_SCHEDULE_MERGE_SAVE_SERVICE",
                "params": {
                    "records": self.__class__.merged_schl_data
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="采购计划行-合并后保存",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"}
            )
            
            # 从合并后的数据中获取订单号和计划行信息
            merged_record = self.__class__.merged_schl_data[0]
            merged_po_code = merged_record.get('poCode')
            
            # 数据库验证并保存ID供后续拆分使用
            db_result = self.db.query(
                sql="SELECT id, po_schl_code, un_close_qty FROM pur_po_schl_tr WHERE po_code=%s AND deleted=0",
                params=[merged_po_code]
            )
            
            assert db_result, f"数据库未查询到订单 {merged_po_code} 的计划行"
            
            # 保存合并后的计划行ID、编号和订单号，供拆分使用
            self.__class__.merged_po_schl_id = db_result[0].get("id")
            self.__class__.merged_po_schl_code = db_result[0].get("po_schl_code")
            self.__class__.merged_po_code = merged_po_code
            self.__class__.merged_po_schl_qty = merged_record.get('poSchlQtyDel')
            
            un_close_qty = db_result[0].get("un_close_qty")
            expected_qty = float(self.__class__.merged_po_schl_qty)
            assert un_close_qty == expected_qty, \
                f"未清数量不符合预期: 期望={expected_qty}, 实际={un_close_qty}"
            
            a.text(
                f"订单编号: {merged_po_code}\n"
                f"合并后编号: {merged_record.get('poSchlCode')}\n"
                f"合并后ID: {self.__class__.merged_po_schl_id}\n"
                f"合并后数量: {self.__class__.merged_po_schl_qty}\n"
                f"数据库未清数量: {un_close_qty} ✅",
                "保存结果"
            )
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购计划行",
        title="编辑采购计划行数量（拆分）",
        description="通过在位编辑修改计划行的计划收货数量，实现拆分效果",
        severity="normal",
        file_level_order=6,
        tags=["采购", "计划行", "编辑", "拆分"]
    )
    def test_edit_po_schl_qty(self):
        try:
            # 检查并获取合并后保存的ID
            if not hasattr(self.__class__, 'merged_po_schl_id') or not self.__class__.merged_po_schl_id:
                self.test_merge_save_po_schl()
            
            # 从数据库查询完整的计划行数据
            db_result = self.db.query(
                sql="SELECT id, po_schl_code, po_code, mat_id, mat_name, po_schl_qty_del, "
                    "po_schl_qty_ful, po_schl_date_del, inv_loc_id, po_item_code, uom_pur_id, "
                    "vend_id, vend_contact_person, vend_contact_info, pur_employee_contact_info, "
                    "pur_employee, un_close_qty, version "
                    "FROM pur_po_schl_tr WHERE id=%s AND deleted=0",
                params=[self.__class__.merged_po_schl_id]
            )
            
            if not db_result:
                raise ValueError(f"数据库未查询到ID为 {self.__class__.merged_po_schl_id} 的计划行")
            
            schl_record = db_result[0]
            original_qty = schl_record.get("po_schl_qty_del")
            
            # 修改计划收货数量（从12改为3，实现拆分效果）
            new_qty = 3
            
            api_path = self.get_api_path("采购计划行-编辑")
            params, url = self.get_api_params(api_path)
            
            # 构造请求参数（处理Decimal和datetime类型）
            po_schl_date_del = schl_record.get("po_schl_date_del")
            if hasattr(po_schl_date_del, 'timestamp'):
                po_schl_date_del = int(po_schl_date_del.timestamp() * 1000)
            
            params["params"]["record"] = {
                "poSchlCode": schl_record.get("po_schl_code"),
                "poCode": schl_record.get("po_code"),
                "matId": {"id": schl_record.get("mat_id")},
                "matName": schl_record.get("mat_name"),
                "poSchlQtyDel": new_qty,
                "poSchlQtyFul": float(schl_record.get("po_schl_qty_ful", 0)),
                "poSchlDateDel": po_schl_date_del,
                "invLocId": {"id": schl_record.get("inv_loc_id")},
                "poItemCode": schl_record.get("po_item_code"),
                "uomPurId": {"id": schl_record.get("uom_pur_id")},
                "vendId": {"id": schl_record.get("vend_id")},
                "vendContactPerson": schl_record.get("vend_contact_person"),
                "vendContactInfo": schl_record.get("vend_contact_info"),
                "purEmployeeContactInfo": schl_record.get("pur_employee_contact_info"),
                "purEmployee": {"id": schl_record.get("pur_employee")},
                "unCloseQty": float(schl_record.get("un_close_qty")),
                "id": schl_record.get("id"),
                "version": schl_record.get("version")
            }
            
            response, _ = self.standard_api_call(
                api_key="采购计划行-编辑",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_success(response)
            
            # 验证拆分结果：应该有2行数据，总和等于原数量
            verify_result = self.db.query(
                sql="SELECT id, po_schl_qty_del, un_close_qty FROM pur_po_schl_tr WHERE po_code=%s AND deleted=0",
                params=[self.__class__.merged_po_code]
            )
            
            assert len(verify_result) == 2, \
                f"拆分后应该有2行数据，实际={len(verify_result)}行"
            
            total_qty = sum(row.get("un_close_qty", 0) for row in verify_result)
            expected_total = float(self.__class__.merged_po_schl_qty)
            assert total_qty == expected_total, \
                f"拆分后总未清数量不符合预期: 期望={expected_total}, 实际={total_qty}"
            
            a.text(
                f"订单编号: {self.__class__.merged_po_code}\n"
                f"原计划行ID: {self.__class__.merged_po_schl_id}\n"
                f"合并后总数量: {self.__class__.merged_po_schl_qty}\n"
                f"编辑后数量: {self.SPLIT_QTY}\n"
                f"拆分后行数: {len(verify_result)}\n"
                f"拆分后总数量: {total_qty} ✅\n"
                f"第1行未清数量: {verify_result[0].get('un_close_qty')}\n"
                f"第2行未清数量: {verify_result[1].get('un_close_qty')}",
                "拆分结果"
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
