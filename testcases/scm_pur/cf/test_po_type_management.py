import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("采购订单类型配置管理")
class TestPoTypeManagement(ScmPurBaseTest):
    """采购订单类型配置管理测试类"""
    
    # 常量定义
    MODEL_KEY = "SCM_PUR$pur_po_type_cf"
    MODULE_NAME = "SCM_PUR"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_type_id = None
        cls.po_type_code = None
        cls.logger.info("采购订单类型配置管理测试类初始化完成")
    @case_decorator(
        story="采购订单类型配置新建",
        title="测试创建采购订单类型配置",
        description="验证采购订单类型配置创建功能",
        severity="critical",
        file_level_order=1,
        tags=["采购订单类型配置", "创建", "SYS_MasterData_SaveDataService"]
    )
    def test_create_po_type(self):
        """创建采购订单类型配置用例"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("(系统)保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成测试数据
            timestamp = self.mock_util.get_timestamp()
            test_code = f"AUTOTEST_PO_{timestamp}"
            test_name = f"自动化测试订单类型_{timestamp}"
            
            # 3. 过滤参数 - 只保留业务字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["poType", "poTypeName", "remark", "isTransferOrder", "isInnerPur", 
                 "isReverse", "supplyInvOrgRequire", "supplyInvLocRequire", 
                 "thirdPartyOrder", "thirdPartyPriceConfirmed", "operationOutsourced", 
                 "stoOrder", "matControl", "supplierCollaborationEnabled", 
                 "autoSendToSupplier", "submitApproval", "alterApproval"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
            ParamUtil.set_request_params(filtered_params, {
                "poType": test_code,
                "poTypeName": test_name,
                "isTransferOrder": False,
                "isInnerPur": False,
                "isReverse": False,
                "supplyInvOrgRequire": False,
                "supplyInvLocRequire": False,
                "thirdPartyOrder": False,
                "thirdPartyPriceConfirmed": False,
                "operationOutsourced": False,
                "stoOrder": False,
                "matControl": False,
                "supplierCollaborationEnabled": False,
                "autoSendToSupplier": False,
                "submitApproval": False,
                "alterApproval": False
            })
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 5. 执行请求
            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "id" in result_data and "poType" in result_data, "创建结果缺少必需字段"
            assert result_data.get("poType") == test_code, "订单类型编码不匹配"
            
            # 7. 保存测试数据
            self.__class__.po_type_id = result_data.get("id")
            self.__class__.po_type_code = result_data.get("poType")
            
            self.logger.info(f"✅ 采购订单类型配置创建成功，ID: {self.__class__.po_type_id}, 编码: {self.__class__.po_type_code}")
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单类型配置分页查询",
        title="采购订单类型配置分页数据服务",
        description="验证采购订单类型配置分页数据服务功能",
        severity="blocker",
        file_level_order=2,
        tags=["采购订单类型配置", "分页查询", "SYS_PagingDataService"]
    )
    def test_paging_po_type(self):
        """采购订单类型配置分页查询测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("(系统)查询分页数据服务")
            _, url = self.get_api_params(api_path)
            
            # 2. 构建完整请求参数（按照curl结构）
            request_params = {
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "sortOrders": None,
                            "conditionItems": None
                        }
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 3. 执行请求（带上查询参数）
            response = self.http.post(
                url, 
                json=request_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
            # 5. 验证响应数据
            data_list = response["data"]["data"]["data"]
            assert len(data_list) > 0, "分页查询结果为空"
            
            self.logger.info(f"✅ 分页查询成功，共查询到 {len(data_list)} 条数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单类型配置导出任务",
        title="采购订单类型配置导出任务接口",
        description="验证采购订单类型配置导出任务接口功能",
        severity="normal",
        file_level_order=3,
        tags=["采购订单类型配置", "导出任务"]
    )
    def test_export_task_po_type(self):
        """采购订单类型配置导出任务测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("订单类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成任务名称
            timestamp = self.mock_util.get_timestamp()
            task_name = f"订单类型-{self.nickname}-{timestamp}-导出"
            
            # 3. 获取导出的ID列表
            condition_value = [self.__class__.po_type_id] if self.__class__.po_type_id else []
            
            # 4. 过滤参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            
            # 5. 设置请求参数
            filtered_params["params"]["taskName"] = task_name
            filtered_params["params"]["multiSheetConfig"] = [{
                "modelKey": self.MODEL_KEY,
                "modelName": "订单类型",
                "sheetNo": 0,
                "sheetName": "订单类型",
                "headerConfigList": [
                    {"name": "类型编码", "type": "TEXT", "field": "poType"},
                    {"name": "类型名称", "type": "TEXT", "field": "poTypeName"}
                ]
            }]
            filtered_params["params"]["queryData"] = {
                "appId": 0,
                "teamId": 22,
                "containerKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW-list-{self.MODEL_KEY}",
                "viewKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW:list",
                "sceneKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW",
                "params": {
                    "request": {
                        "pageable": {
                            "conditionItems": {
                                "type": "ConditionItems",
                                "logicOperator": "AND",
                                "conditions": {
                                    "id": {
                                        "operator": "IN",
                                        "value": condition_value
                                    }
                                } if condition_value else {}
                            },
                            "pageNo": 1,
                            "pageSize": 20
                        }
                    },
                    "selectFields": [
                        {"field": "poType"},
                        {"field": "poTypeName"}
                    ],
                    "modelKey": self.MODEL_KEY
                }
            }
            filtered_params["params"]["processConfig"] = {
                "processType": "TRANTOR",
                "appId": 0,
                "teamId": 22,
                "model": self.MODEL_KEY,
                "modelName": "订单类型",
                "containerKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW-list-{self.MODEL_KEY}",
                "viewKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW:list",
                "sceneKey": f"{self.MODULE_NAME}$PUR_PO_TYPE_VIEW"
            }
            
            # 6. 执行请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.logger.info(f"✅ 导出任务创建成功，任务名称: {task_name}")
            
            # 7. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单类型配置删除",
        title="测试删除采购订单类型配置",
        description="验证采购订单类型配置删除功能",
        severity="critical",
        file_level_order=4,
        tags=["采购订单类型配置", "删除", "SYS_DeleteDataByIdService"]
    )
    def test_delete_po_type(self):
        """删除采购订单类型配置用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.po_type_id:
                pytest.skip("没有可用的采购订单类型配置ID，跳过删除测试")
            
            # 2. 获取API配置
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 过滤参数 - 只保留id字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.po_type_id})
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 5. 执行请求
            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 6. 验证删除结果
            assert response.get("success") is True, "删除请求失败"
            
            self.logger.info(f"✅ 采购订单类型配置删除成功，ID: {self.__class__.po_type_id}")
            
            # 7. 清空类变量
            self.__class__.po_type_id = None
            self.__class__.po_type_code = None
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

