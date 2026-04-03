"""
采购交货单行测试
"""
import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del import ScmDelBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("交货管理")
@allure.feature("采购交货单行")
class TestDelPoDnItemManagement(ScmDelBaseTest):
    """采购交货单行测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.dn_item_id = None
        cls.logger.info("采购交货单行测试类初始化完成")
    

    @case_decorator(
        story="采购交货单行",
        title="查询采购交货单行列表",
        description="查询采购交货单行列表，验证分页查询功能",
        severity="critical",
        file_level_order=1,
        tags=["交货单行", "查询", "分页"]
    )
    def test_query_dn_item_list(self):
        """查询采购交货单行列表"""
        try:
            api_path = self.get_api_path("DEL-交货单公共-分页查询交货单行-后端")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["btClass", "pageable"], ["params", "request"]
            )
            
            set_dict = {
                "btClass": "PUR",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [],
                    "conditionGroup": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="DEL-交货单公共-分页查询交货单行-后端",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {})
            assert records.get("total") >= 0, "查询结果异常"
            
            # 保存第一个交货单行ID供后续测试使用
            if records.get("data"):
                self.__class__.dn_item_id = records["data"][0].get("id")
                self.logger.info(f"保存交货单行ID: {self.__class__.dn_item_id}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购交货单行",
        title="查询交货单行子行下拉",
        description="根据交货单行ID查询子行下拉数据",
        severity="critical",
        file_level_order=2,
        tags=["交货单行", "子行", "下拉查询"]
    )
    def test_query_dn_item_dropdown(self):
        """查询交货单行子行下拉"""
        try:
            if not self.__class__.dn_item_id:
                self._ensure_query_dn_item_list()
            
            api_path = self.get_api_path("DEL-查询交货单行批次信息服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            set_dict = {"id": self.__class__.dn_item_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="DEL-查询交货单行批次信息服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", [])
            assert result_data is not None, "未查询到子行下拉数据"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="采购交货单行",
        title="导出采购交货单行",
        description="验证采购交货单行导出功能",
        severity="critical",
        file_level_order=3,
        tags=["交货单行", "导出"]
    )
    def test_export_dn_item(self):
        """导出采购交货单行"""
        try:
            if not self.__class__.dn_item_id:
                self._ensure_query_dn_item_list()
            
            api_path = self.get_api_path("交货单项目行表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            set_dict = {
                "taskName": f"采购交货单行-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_DEL$del_dn_item_tr",
                        "modelName": "交货单项目行表",
                        "sheetNo": 0,
                        "sheetName": "交货单项目行表",
                        "headerConfigList": [
                            {"name": "交货单行编号", "type": "TEXT", "field": "dnItemCode"},
                            {"name": "行项目类型", "type": "TEXT", "field": "dnItemTypeId.dnItemTypeName"},
                            {"name": "物料编码", "type": "TEXT", "field": "matCode"},
                            {"name": "物料名称", "type": "TEXT", "field": "matName"},
                            {"name": "类目", "type": "TEXT", "field": "matId.cateId.matCateName"},
                            {"name": "基本单位数量", "type": "DECIMAL", "field": "docItemQty", "precision": 3},
                            {"name": "计划交货数量", "type": "DECIMAL", "field": "planDelQty", "precision": 3},
                            {"name": "执行数量", "type": "DECIMAL", "field": "invExecutedQty", "precision": 3, "precisionDisplayType": "FILL_ROUND"},
                            {"name": "过账数量", "type": "DECIMAL", "field": "realDelQty", "precision": 6},
                            {"name": "行状态", "type": "ENUM", "field": "status", "multiSelect": False},
                            {"name": "业务状态", "type": "ENUM", "field": "bizStatus", "multiSelect": False},
                            {"name": "计划交货日期", "type": "DATE", "field": "planRecvDate", "dateFormat": "yyyy-MM-dd"},
                            {"name": "库存组织", "type": "TEXT", "field": "invOrgId.orgName"},
                            {"name": "库存地点", "type": "TEXT", "field": "invLocId.orgName"},
                            {"name": "交货单编号", "type": "TEXT", "field": "dnId.dnCode"},
                            {"name": "关联采购订单编号", "type": "TEXT", "field": "docCode"},
                            {"name": "关联采购订单行编号", "type": "TEXT", "field": "docItemCode"},
                            {"name": "关联交货单编号", "type": "TEXT", "field": "dnId.relationDnId.dnCode"},
                            {"name": "关联交货单行编号", "type": "TEXT", "field": "relationItemId.dnItemCode"},
                            {"name": "净重", "type": "DECIMAL", "field": "netWeight", "precision": 3, "precisionDisplayType": "FILL_ROUND"},
                            {"name": "毛重", "type": "DECIMAL", "field": "grossWeight", "precision": 3, "precisionDisplayType": "ORIGIN_ROUND"},
                            {"name": "体积", "type": "NUMBER", "field": "matVolume", "precisionDisplayType": "FILL_ROUND"},
                            {"name": "特殊库存类型", "type": "TEXT", "field": "spcStkTypeId.name"},
                            {"name": "特殊库存取值", "type": "TEXT", "field": "spcStkTypeClassName"}
                        ]
                    }
                ],
                "queryData": {
                    "params": {
                        "request": {
                            "pageable": {
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {
                                        "id": {
                                            "operator": "IN",
                                            "value": [self.__class__.dn_item_id]
                                        }
                                    }
                                },
                                "pageNo": 1,
                                "pageSize": 20,
                                "sortOrders": []
                            }
                        },
                        "selectFields": [
                            {"field": "dnItemCode"},
                            {"field": "matCode"},
                            {"field": "matName"},
                            {"field": "docItemQty"},
                            {"field": "planDelQty"},
                            {"field": "invExecutedQty"},
                            {"field": "realDelQty"},
                            {"field": "status"},
                            {"field": "bizStatus"},
                            {"field": "planRecvDate"},
                            {"field": "docCode"},
                            {"field": "docItemCode"},
                            {"field": "netWeight"},
                            {"field": "grossWeight"},
                            {"field": "matVolume"},
                            {"field": "spcStkTypeClassName"},
                            {"field": "dnItemTypeId", "selectFields": [{"field": "dnItemTypeName"}]},
                            {"field": "matId", "selectFields": [{"field": "cateId", "selectFields": [{"field": "matCateName"}]}]},
                            {"field": "invOrgId", "selectFields": [{"field": "orgName"}]},
                            {"field": "invLocId", "selectFields": [{"field": "orgName"}]},
                            {"field": "dnId", "selectFields": [{"field": "dnCode"}, {"field": "relationDnId", "selectFields": [{"field": "dnCode"}]}]},
                            {"field": "relationItemId", "selectFields": [{"field": "dnItemCode"}]},
                            {"field": "spcStkTypeId", "selectFields": [{"field": "name"}]}
                        ],
                        "modelKey": "SCM_DEL$del_dn_item_tr"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_DEL$del_dn_item_tr",
                    "modelName": "交货单项目行表",
                    "containerKey": "ERP_SCM$DEL_DN_PUR_ITEM_VEW-table-container-ERP_SCM$del_dn_item_tr",
                }
            }
            
            # 直接设置params字段
            params["params"] = set_dict
            
            response, _ = self.standard_api_call(
                api_key="交货单项目行表-导入导出任务管理接口-提交导出任务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
