import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("ATP检查规则管理")
class TestInvAtpRuleManagement(ScmInvBaseTest):
    """ATP检查规则管理 - 完整CRUD流程测试
    
    测试流程：
    1. 创建共享ATP检查组（conftest辅助函数）
    2. 创建ATP检查规则
    3. 导出查询
    4. 详情查询
    5. 分页查询
    6. 删除规则
    
    优势：不依赖order，可单独运行文件或整个目录
    """
    
    MODEL_KEY = "SCM_INV$inv_atp_rule_cf"
    URL_PARAMS = {"tmodule": "SCM_INV", "modelKey": MODEL_KEY}
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.atp_rule_id = None
        cls.atp_group_id = None
        cls.atp_group_code = None

    def _ensure_atp_group(self):
        """确保ATP检查组存在（只创建一次）"""
        if self.__class__.atp_group_id:
            return
        
        api_path = self.get_api_path("(系统)保存数据服务")
        params, url = self.get_api_params(api_path)
        
        timestamp = self.mock_util.get_timestamp()
        filtered_params = ParamUtil.filter_post_body_fields(params, ["code", "name"], ["params", "request"])
        ParamUtil.set_request_params(filtered_params, {
            "code": f"AUTOTEST_ATP_{timestamp}",
            "name": f"自动化测试ATP组_{timestamp}"
        })
        filtered_params["params"]["modelKey"] = "SCM_INV$inv_atp_group_md"

        response, _ = self.standard_api_call(
            api_key="(系统)保存数据服务",
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            query_params={"tmodule": "SCM_INV", "modelKey": "SCM_INV$inv_atp_group_md"}
        )
        self.assert_util.assert_response_data(response)
        
        result_data = response.get("data", {}).get("data", {})
        self.__class__.atp_group_id = result_data.get("id")
        self.__class__.atp_group_code = result_data.get("code")
        
        self.logger.info(f"✅ 创建ATP检查组: ID={self.__class__.atp_group_id}")
        assert self.__class__.atp_group_id, "ATP检查组创建失败"

    def _prepare_request_params(self, filtered_params):
        """准备请求参数：设置 modelKey。"""
        # 系统服务模板里的 selectFields 结构在部分环境下会被渲染为非法占位对象，
        # 导致后端 NPE（relationAlias is null），这里统一移除。
        filtered_params.get("params", {}).pop("selectFields", None)
        filtered_params["params"]["modelKey"] = self.MODEL_KEY
        return filtered_params
    
    def _validate_response(self, response, required_fields=None):
        """验证响应并返回数据"""
        self.assert_util.assert_response_data(response)
        result_data = response.get("data", {}).get("data", {})
        
        if required_fields:
            for field in required_fields:
                assert field in result_data, f"响应结果缺少{field}字段"
        
        return result_data

    @case_decorator(
        story="ATP检查规则管理",
        title="测试创建ATP检查规则",
        description="验证ATP检查规则创建功能",
        severity="critical",
        #order=1,
        tags=["ATP检查规则", "创建"]
    )
    def test_create_atp_rule(self):
        """创建ATP检查规则"""
        try:
            # 确保ATP检查组存在
            self._ensure_atp_group()
            
            api_path = self.get_api_path("(系统)保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, [
                "atpGroupId", "docClass", "ctrlType", "planStrategy", "invRule", "invPriority", 
                "isShortageCheck", "isInvOrg", "isInvLoc", "isInvSpec", "isAllowReconfirm", 
                "isAllowPart", "isSoContain", "isPoContain", "isPdContain", "isDnContain"
            ], ["params", "request"])
            
            ParamUtil.set_request_params(filtered_params, {
                "atpGroupId": {"id": self.__class__.atp_group_id, "code": self.__class__.atp_group_code},
                "docClass": "PO", "ctrlType": "NONE", "planStrategy": "AUTO_SUGGEST",
                "invRule": "SPOT_PRIORITY", "invPriority": "FUT",
                "isShortageCheck": True, "isInvOrg": True, "isInvLoc": True, "isInvSpec": True,
                "isAllowReconfirm": True, "isAllowPart": True, "isSoContain": True,
                "isPoContain": True, "isPdContain": True, "isDnContain": True
            })
            
            filtered_params = self._prepare_request_params(filtered_params)
            response, _ = self.standard_api_call(
                api_key="(系统)保存数据服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params=self.URL_PARAMS,
            )
            result_data = self._validate_response(response, ["id", "docClass"])
            
            assert result_data.get("docClass") == "PO", "单据类型不匹配"
            self.__class__.atp_rule_id = result_data.get("id")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="ATP检查规则管理",
        title="测试查询ATP检查规则导出",
        description="验证ATP检查规则导出查询功能",
        severity="normal",
        #order=2,
        tags=["ATP检查规则", "导出查询"]
    )
    def test_query_atp_rule_export(self):
        """查询ATP检查规则导出用例"""
        try:
            api_path = self.get_api_path("ATP检查规则-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            timestamp = self.mock_util.get_timestamp()
            task_name = f"ATP检查规则-自动化测试-{timestamp}-导出"
            condition_value = [self.__class__.atp_rule_id] if self.__class__.atp_rule_id else []

            # 构建导出参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["serviceKey", "taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            
            # 设置导出配置
            export_config = {
                "serviceKey": "SCM_INV$INV_ATP_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "taskName": task_name,
                "multiSheetConfig": [{
                    "modelKey": "SCM_INV$inv_atp_rule_cf",
                    "modelName": "ATP检查规则",
                    "sheetNo": 0,
                    "sheetName": "ATP检查规则",
                    "headerConfigList": [
                        {"name": "ATP检查组", "type": "TEXT", "field": "atpGroupId.name"},
                        {"name": "单据类型", "type": "ENUM", "field": "docClass", "multiSelect": False,
                         "dictValues": [
                             {"_row_id_": "PO", "label": "采购单", "value": "PO"},
                             {"_row_id_": "SO", "label": "销售单", "value": "SO"},
                             {"_row_id_": "DN", "label": "交货单", "value": "DN"},
                             {"_row_id_": "zXGEHYM", "label": "生产单", "value": "PD"}
                         ]},
                        {"name": "控制类型", "type": "ENUM", "field": "ctrlType", "multiSelect": False,
                         "dictValues": [
                             {"label": "不控制", "value": "NONE"},
                             {"label": "弱控制", "value": "WEAK"},
                             {"label": "强控制", "value": "STRICT"}
                         ]},
                        {"name": "计划策略", "type": "ENUM", "field": "planStrategy", "multiSelect": False,
                         "dictValues": [
                             {"_row_id_": "zdLEwF6", "label": "自动建议", "value": "AUTO_SUGGEST"},
                             {"_row_id_": "ufv3jVn", "label": "不自动建议", "value": "NOT_SUGGEST"}
                         ]},
                        {"name": "库存占用原则", "type": "ENUM", "field": "invRule", "multiSelect": False,
                         "dictValues": [
                             {"label": "现货就近", "value": "SPOT_PRIORITY"},
                             {"label": "交货就近", "value": "FUTURES_PRIORITY"}
                         ]},
                        {"name": "占用优先策略", "type": "ENUM", "field": "invPriority", "multiSelect": False,
                         "dictValues": [
                             {"_row_id_": "STK", "label": "现货", "value": "STK"},
                             {"_row_id_": "FUT", "label": "在途", "value": "FUT"}
                         ]},
                        {"name": "是否短缺检查", "type": "BOOL", "field": "isShortageCheck"},
                        {"name": "是否允许自动确认", "type": "BOOL", "field": "isAllowReconfirm"},
                        {"name": "是否允许部分占用", "type": "BOOL", "field": "isAllowPart"},
                        {"name": "是否考虑库存组织", "type": "BOOL", "field": "isInvOrg"},
                        {"name": "是否考虑库存地点", "type": "BOOL", "field": "isInvLoc"},
                        {"name": "是否包含未清采购单", "type": "BOOL", "field": "isPoContain"},
                        {"name": "是否包含未清销售单", "type": "BOOL", "field": "isSoContain"},
                        {"name": "是否包含未清生产单", "type": "BOOL", "field": "isPdContain"},
                        {"name": "是否包含未清交货单", "type": "BOOL", "field": "isDnContain"}
                    ]
                }],
                "queryData": {
                    "containerKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW-table-container-SCM_INV$inv_atp_rule_cf",
                    "viewKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW:list",
                    "sceneKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {"id": {"operator": "IN", "value": condition_value}} if condition_value else {}
                                },
                                "pageNo": 1, "pageSize": 20
                            }
                        },
                        "selectFields": [
                            {"field": "docClass"}, {"field": "ctrlType"}, {"field": "planStrategy"},
                            {"field": "invRule"}, {"field": "invPriority"}, {"field": "isShortageCheck"},
                            {"field": "isAllowReconfirm"}, {"field": "isAllowPart"}, {"field": "isInvOrg"},
                            {"field": "isInvLoc"}, {"field": "isPoContain"}, {"field": "isSoContain"},
                            {"field": "isPdContain"}, {"field": "isDnContain"},
                            {"field": "atpGroupId", "selectFields": [{"field": "name"}]}
                        ],
                        "modelKey": "SCM_INV$inv_atp_rule_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR", 
                    "model": "SCM_INV$inv_atp_rule_cf", "modelName": "ATP检查规则",
                    "containerKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW-table-container-SCM_INV$inv_atp_rule_cf",
                    "viewKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW:list",
                    "sceneKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW"
                }
            }
            
            # 应用配置
            filtered_params["serviceKey"] = export_config["serviceKey"]
            for key in ["taskName", "multiSheetConfig", "queryData", "processConfig"]:
                filtered_params["params"][key] = export_config[key]

            response, _ = self.standard_api_call(
                api_key="ATP检查规则-导入导出任务管理接口-提交导出任务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="ATP检查规则管理",
        title="测试查询ATP检查规则详情",
        description="验证ATP检查规则详情查询功能",
        severity="normal",
        #order=8,
        tags=["ATP检查规则", "详情查询"]
    )
    def test_query_atp_rule_detail(self):
        """查询ATP检查规则详情"""
        try:
            if not self.__class__.atp_rule_id:
                pytest.fail("没有可用的ATP检查规则ID")
            
            api_path = self.get_api_path("(系统)查询数据详情服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.atp_rule_id})
            filtered_params = self._prepare_request_params(filtered_params)
            
            response, _ = self.standard_api_call(
                api_key="(系统)查询数据详情服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params=self.URL_PARAMS,
            )
            result_data = self._validate_response(response, ["id", "docClass"])
            assert result_data.get("id") == self.__class__.atp_rule_id, "ATP检查规则ID不匹配"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="ATP检查规则管理",
        title="测试分页查询ATP检查规则列表",
        description="验证根据ATP检查组ID分页查询ATP检查规则功能",
        severity="normal",
        #order=9,
        tags=["ATP检查规则", "分页查询"]
    )
    def test_query_atp_rule_paging(self):
        """分页查询ATP检查规则列表"""
        try:
            if not self.__class__.atp_group_id:
                pytest.fail("没有可用的ATP检查组ID")
            
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["pageable"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1, "pageSize": 20, "needTotal": True,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "atpGroupId": {
                                "operator": "EQ",
                                "value": {"code": self.__class__.atp_group_code, "id": self.__class__.atp_group_id}
                            }
                        },
                        "logicOperator": "AND"
                    }
                }
            })
            
            filtered_params = self._prepare_request_params(filtered_params)
            response, _ = self.standard_api_call(
                api_key="(系统)查询分页数据服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params=self.URL_PARAMS,
            )
            result_data = self._validate_response(response, ["data", "total"])
            
            content = result_data.get("data", [])
            if content:
                first_item = content[0]
                assert "id" in first_item and "atpGroupId" in first_item, "查询结果缺少必需字段"
                atp_group_info = first_item.get("atpGroupId", {})
                if isinstance(atp_group_info, dict) and "id" in atp_group_info:
                    assert atp_group_info["id"] == self.__class__.atp_group_id, "ATP检查组ID不匹配"
            
            self.logger.info(f"分页查询成功: 总数={result_data.get('total', 0)}, 当前页={len(content)}条")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="ATP检查规则管理",
        title="测试删除ATP检查规则",
        description="验证ATP检查规则删除功能",
        severity="critical",
        #order=10,
        tags=["ATP检查规则", "删除"]
    )
    def test_delete_atp_rule(self):
        """删除ATP检查规则"""
        try:
            if not self.__class__.atp_rule_id:
                pytest.fail("没有可用的ATP检查规则ID")
            
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.atp_rule_id})
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            response, _ = self.standard_api_call(
                api_key="(系统)删除数据服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params=self.URL_PARAMS,
            )
            assert response.get("success") is True, "删除ATP检查规则失败"
            
            self.__class__.atp_rule_id = None
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
