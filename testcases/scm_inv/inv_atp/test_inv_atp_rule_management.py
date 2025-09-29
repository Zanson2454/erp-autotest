import allure
import pytest
import sys
from pathlib import Path
import importlib

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("ATP检查规则管理")
class TestInvAtpRuleManagement(ScmInvBaseTest):
    """ATP检查规则管理测试类 - 覆盖CRUD全流程"""
    
    # 常量定义
    MODEL_KEY = "SCM_INV$inv_atp_rule_cf"
    URL_PARAMS = {"tmodule": "SCM_INV", "modelKey": MODEL_KEY}
    DEFAULT_SELECT_FIELDS = [
        {"field": "id"}, {"field": "atpGroupId"}, {"field": "docClass"}, 
        {"field": "ctrlType"}, {"field": "planStrategy"}, {"field": "invRule"}
    ]

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.atp_rule_id = None
        cls.atp_group_id = None
        cls.atp_group_code = None
        cls.logger.info("ATP检查规则创建测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理ATP检查组测试数据
            cls.db.delete(
                table="inv_atp_group_md",
                where="code like %s",
                params=["AUTOTEST_ATP_%"]
            )
            cls.logger.info("ATP检查规则测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    def _create_prerequisite_atp_group(self):
        """创建前置ATP检查组"""
        if self.__class__.atp_group_id:
            return
            
        # 动态导入ATP检查组管理类，避免pytest发现额外的测试类
        module = importlib.import_module('testcases.scm_inv.inv_atp.test_inv_atp_group_management')
        TestInvAtpGroupManagement = module.TestInvAtpGroupManagement
        
        # 创建ATP检查组实例并调用创建方法
        atp_group_test = TestInvAtpGroupManagement()
        atp_group_test.setup_class()
        atp_group_test.test_create_atp_group()
        
        # 获取创建的ATP检查组信息
        self.__class__.atp_group_id = atp_group_test.__class__.atp_group_id
        self.__class__.atp_group_code = atp_group_test.__class__.atp_group_code
        
        assert self.__class__.atp_group_id, "前置ATP检查组创建失败"

    def _setup_model_config(self, filtered_params):
        """统一设置模型配置"""
        filtered_params["params"]["modelKey"] = self.MODEL_KEY
        return filtered_params
    
    def _setup_select_fields(self, filtered_params, fields=None):
        """统一处理selectFields配置"""
        if "selectFields" in filtered_params["params"]:
            filtered_params["selectFields"] = filtered_params["params"]["selectFields"]
            del filtered_params["params"]["selectFields"]
        
        if "selectFields" not in filtered_params or not filtered_params["selectFields"]:
            filtered_params["selectFields"] = fields or self.DEFAULT_SELECT_FIELDS
        return filtered_params
    
    def _execute_request(self, url, filtered_params):
        """统一执行请求"""
        return self.http.post(url, json=filtered_params, params=self.URL_PARAMS)
    
    def _prepare_request_params(self, filtered_params, fields=None):
        """统一准备请求参数"""
        filtered_params = self._setup_model_config(filtered_params)
        filtered_params = self._setup_select_fields(filtered_params, fields)
        return filtered_params
    
    def _validate_response_data(self, response, required_fields=None):
        """统一验证响应数据"""
        self.assert_util.assert_response_data(response)
        result_data = response.get("data", {}).get("data", {})
        
        if required_fields:
            for field in required_fields:
                assert field in result_data, f"响应结果缺少{field}字段"
        
        return result_data

    @pytest.mark.run(order=1)
    @case_decorator(
        story="ATP检查规则管理",
        title="测试创建ATP检查规则",
        description="验证ATP检查规则创建功能",
        severity="critical",
        order=1,
        tags=["ATP检查规则", "创建"]
    )
    def test_create_atp_rule(self):
        """创建ATP检查规则用例"""
        try:
            # 创建前置ATP检查组
            self._create_prerequisite_atp_group()
            
            api_path = self.get_api_path("(系统)保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "atpGroupId", "docClass", "ctrlType", "planStrategy", 
                    "invRule", "invPriority", "isShortageCheck", "isInvOrg", 
                    "isInvLoc", "isInvSpec", "isAllowReconfirm", "isAllowPart", 
                    "isSoContain", "isPoContain", "isPdContain", "isDnContain"
                ], ["params", "request"]
            )
            
            # 设置ATP检查规则参数
            ParamUtil.set_request_params(filtered_params, {
                "atpGroupId": {
                    "id": self.__class__.atp_group_id,
                    "code": self.__class__.atp_group_code
                },
                "docClass": "PO",
                "ctrlType": "NONE", 
                "planStrategy": "AUTO_SUGGEST",
                "invRule": "SPOT_PRIORITY",
                "invPriority": "FUT",
                "isShortageCheck": True,
                "isInvOrg": True,
                "isInvLoc": True,
                "isInvSpec": True,
                "isAllowReconfirm": True,
                "isAllowPart": True,
                "isSoContain": True,
                "isPoContain": True,
                "isPdContain": True,
                "isDnContain": True
            })
            
            # 统一配置请求参数
            filtered_params = self._prepare_request_params(filtered_params)
            
            # 执行请求
            response = self._execute_request(url, filtered_params)
            
            # 验证结果
            result_data = self._validate_response_data(response, ["id", "docClass"])
            assert result_data.get("docClass") == "PO", "单据类型不匹配"
            
            # 保存ATP检查规则ID
            self.__class__.atp_rule_id = result_data.get("id")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @case_decorator(
        story="ATP检查规则管理",
        title="测试查询ATP检查规则导出",
        description="验证ATP检查规则导出查询功能",
        severity="normal",
        order=2,
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
                ["serviceKey", "teamId", "taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            
            # 设置导出配置
            export_config = {
                "serviceKey": "SCM_INV$INV_ATP_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
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
                    "appId": 0, "teamId": 22,
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
                    "processType": "TRANTOR", "appId": 0, "teamId": 22,
                    "model": "SCM_INV$inv_atp_rule_cf", "modelName": "ATP检查规则",
                    "containerKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW-table-container-SCM_INV$inv_atp_rule_cf",
                    "viewKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW:list",
                    "sceneKey": "SCM_INV$INV_ATP_RULE_NEW_VIEW"
                }
            }
            
            # 应用配置
            filtered_params["serviceKey"] = export_config["serviceKey"]
            filtered_params["teamId"] = export_config["teamId"]
            for key in ["taskName", "multiSheetConfig", "queryData", "processConfig"]:
                filtered_params["params"][key] = export_config[key]

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @case_decorator(
        story="ATP检查规则管理",
        title="测试查询ATP检查规则详情",
        description="验证ATP检查规则详情查询功能",
        severity="normal",
        order=3,
        tags=["ATP检查规则", "详情查询"]
    )
    def test_query_atp_rule_detail(self):
        """查询ATP检查规则详情用例"""
        try:
            if not self.__class__.atp_rule_id:
                pytest.skip("没有可用的ATP检查规则ID，跳过详情查询测试")
            
            api_path = self.get_api_path("(系统)查询数据详情服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            # 设置请求参数
            ParamUtil.set_request_params(filtered_params, {
                "id": self.__class__.atp_rule_id
            })
            
            # 统一配置请求参数
            filtered_params = self._prepare_request_params(filtered_params)
            
            # 执行请求
            response = self._execute_request(url, filtered_params)
            
            # 验证结果
            result_data = self._validate_response_data(response, ["id", "docClass"])
            assert result_data.get("id") == self.__class__.atp_rule_id, "ATP检查规则ID不匹配"
            
            # 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @case_decorator(
        story="ATP检查规则管理",
        title="测试分页查询ATP检查规则列表",
        description="验证根据ATP检查组ID分页查询ATP检查规则功能",
        severity="normal",
        order=4,
        tags=["ATP检查规则", "分页查询"]
    )
    def test_query_atp_rule_paging(self):
        """分页查询ATP检查规则列表用例"""
        try:
            if not self.__class__.atp_group_id:
                pytest.skip("没有可用的ATP检查组ID，跳过分页查询测试")
            
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            
            # 设置请求参数 - 根据ATP检查组ID查询
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "atpGroupId": {
                                "operator": "EQ",
                                "value": {
                                    "code": self.__class__.atp_group_code,
                                    "id": self.__class__.atp_group_id
                                }
                            }
                        },
                        "logicOperator": "AND"
                    }
                }
            })
            
            # 统一配置请求参数
            filtered_params = self._prepare_request_params(filtered_params)
            
            # 执行请求
            response = self._execute_request(url, filtered_params)
            
            # 验证结果
            result_data = self._validate_response_data(response, ["data", "total"])
            
            content = result_data.get("data", [])
            total_elements = result_data.get("total", 0)
            
            # 验证查询结果
            if content:
                first_item = content[0]
                assert "id" in first_item, "查询结果项缺少ID字段"
                assert "atpGroupId" in first_item, "查询结果项缺少ATP检查组ID字段"
                
                # 验证ATP检查组ID匹配
                atp_group_info = first_item.get("atpGroupId", {})
                if isinstance(atp_group_info, dict) and "id" in atp_group_info:
                    assert atp_group_info["id"] == self.__class__.atp_group_id, "ATP检查组ID不匹配"
            
            self.logger.info(f"ATP检查规则分页查询成功，总数: {total_elements}, 当前页数据: {len(content)}")
            
            # 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @case_decorator(
        story="ATP检查规则管理",
        title="测试删除ATP检查规则",
        description="验证ATP检查规则删除功能",
        severity="critical",
        order=5,
        tags=["ATP检查规则", "删除"]
    )
    def test_delete_atp_rule(self):
        """删除ATP检查规则用例"""
        try:
            if not self.__class__.atp_rule_id:
                pytest.skip("没有可用的ATP检查规则ID，跳过删除测试")
            
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            # 设置请求参数
            ParamUtil.set_request_params(filtered_params, {
                "id": self.__class__.atp_rule_id
            })
            
            # 统一配置请求参数（删除操作不需要selectFields）
            filtered_params = self._setup_model_config(filtered_params)
            
            # 执行请求
            response = self._execute_request(url, filtered_params)
            
            # 验证删除结果
            assert response.get("success") is True, "删除ATP检查规则失败"
            
            # 清空类变量
            self.__class__.atp_rule_id = None
            
            # 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
