import allure
import pytest
from testcases.scm_pur import ScmPurBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("采购订单行类型配置管理")
class TestPoItemTypeManagement(ScmPurBaseTest):
    """采购订单行类型配置管理测试类"""
    
    # 常量定义（MODULE_NAME 继承自 ScmPurBaseTest）
    MODEL_KEY = "SCM_PUR$pur_po_item_type_cf"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_item_type_id = None
        cls.po_item_type_code = None
        cls.logger.info("采购订单行类型配置管理测试类初始化完成")
    
    @case_decorator(
        story="采购订单行类型配置新建",
        title="测试创建采购订单行类型配置",
        description="验证采购订单行类型配置创建功能",
        severity="critical",
        file_level_order=1,
        tags=["采购订单行类型配置", "创建", "SYS_MasterData_SaveDataService"]
    )
    def test_create_po_item_type(self):
        """创建采购订单行类型配置用例"""
        try:
            # 1. 生成测试数据
            test_code = self.mock_util.generate_unique_code(tag="AUTOTEST_ITEM")
            test_name = f"自动化测试订单行类型_{self.mock_util.get_timestamp()}"
            
            # 2. 准备完整的 params 结构（包含 request 和 modelKey）
            set_dict = {
                "request": {
                    "poItemType": test_code,
                    "poItemTypeName": test_name,
                    "autoComplete": False,
                    "isReverse": False,
                    "requireSupplyInvOrg": False,
                    "requireSupplyInvLoc": False,
                    "outsourcingSupplierRequired": False,
                    "outsourcing": False,
                    "enableShortSpinnerControl": False,
                    "thirdPartyOrder": False,
                    "operationOutsourced": False,
                    "mtoOrder": False,
                    "isAutoCreateDn": False,
                    "isSettRelv": False,
                    "requiredSlsSoItemTrId": False
                },
                "modelKey": self.MODEL_KEY  # modelKey 与 request 同级
            }
            
            # 3. 使用 standard_api_call 发送请求
            #    - param_path=["params"]: set_dict 完整替换 params
            #    - use_param_util=False: 不使用 ParamUtil，直接使用 set_dict
            #    - query_params: URL 参数（?tmodule=SCM_PUR&modelKey=XXX）
            response, extracted_id = self.standard_api_call(
                api_key="(系统)保存主数据服务",
                set_dict=set_dict,
                param_path=["params"],
                use_param_util=False,
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "id" in result_data and "poItemType" in result_data, "创建结果缺少必需字段"
            assert result_data.get("poItemType") == test_code, "订单行类型编码不匹配"
            
            # 6. 保存测试数据
            self.__class__.po_item_type_id = result_data.get("id")
            self.__class__.po_item_type_code = result_data.get("poItemType")
            
            # 7. 记录报告
            self.logger.info(f"✅ 采购订单行类型配置创建成功，ID: {self.__class__.po_item_type_id}, 编码: {self.__class__.po_item_type_code}")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单行类型配置分页查询",
        title="采购订单行类型配置分页数据服务",
        description="验证采购订单行类型配置分页数据服务功能",
        severity="blocker",
        file_level_order=2,
        tags=["采购订单行类型配置", "分页查询", "SYS_PagingDataService"]
    )
    def test_paging_po_item_type(self):
        """采购订单行类型配置分页查询测试"""
        try:
            # 1. 准备完整的 params 结构（包含 request 和 modelKey）
            set_dict = {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "sortOrders": None,
                        "conditionItems": None
                    }
                },
                "modelKey": self.MODEL_KEY  # modelKey 与 request 同级
            }
            
            # 2. 使用 standard_api_call 发送请求
            #    - param_path=["params"]: set_dict 完整替换 params
            #    - use_param_util=False: 不使用 ParamUtil，直接使用 set_dict
            #    - query_params: URL 参数（?tmodule=SCM_PUR&modelKey=XXX）
            response, _ = self.standard_api_call(
                api_key="(系统)查询分页数据服务",
                set_dict=set_dict,
                param_path=["params"],
                use_param_util=False,
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 验证响应数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            assert len(data_list) > 0, "分页查询结果为空"
            
            # 5. 记录报告
            self.logger.info(f"✅ 分页查询成功，共查询到 {len(data_list)} 条数据")
            a.json(response, "响应数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单行类型配置导出任务",
        title="采购订单行类型配置导出任务接口",
        description="验证采购订单行类型配置导出任务接口功能",
        severity="normal",
        file_level_order=3,
        tags=["采购订单行类型配置", "导出任务"]
    )
    def test_export_task_po_item_type(self):
        """采购订单行类型配置导出任务测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("订单项目行类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成任务名称
            timestamp = self.mock_util.get_timestamp()
            task_name = f"订单行类型-{self.nickname}-{timestamp}-导出"
            
            # 3. 获取导出的ID列表
            condition_value = [self.__class__.po_item_type_id] if self.__class__.po_item_type_id else []
            
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
                "modelName": "订单项目行类型",
                "sheetNo": 0,
                "sheetName": "订单项目行类型",
                "headerConfigList": [
                    {"name": "行类型编码", "type": "TEXT", "field": "poItemType"},
                    {"name": "行类型名称", "type": "TEXT", "field": "poItemTypeName"}
                ]
            }]
            filtered_params["params"]["queryData"] = {
                "appId": 0,
                "teamId": 22,
                "containerKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type-list-{self.MODEL_KEY}",
                "viewKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type:9o",
                "sceneKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type",
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
                        {"field": "poItemType"},
                        {"field": "poItemTypeName"}
                    ],
                    "modelKey": self.MODEL_KEY
                }
            }
            filtered_params["params"]["processConfig"] = {
                "processType": "TRANTOR",
                "appId": 0,
                "teamId": 22,
                "model": self.MODEL_KEY,
                "modelName": "订单项目行类型",
                "containerKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type-list-{self.MODEL_KEY}",
                "viewKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type:9o",
                "sceneKey": f"{self.MODULE_NAME}$TERP_MIGRATE_po_item_type"
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
        story="采购订单行类型配置删除",
        title="测试删除采购订单行类型配置",
        description="验证采购订单行类型配置删除功能",
        severity="critical",
        file_level_order=4,
        tags=["采购订单行类型配置", "删除", "SYS_MasterData_DeleteDataService"]
    )
    def test_delete_po_item_type(self):
        """删除采购订单行类型配置用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.po_item_type_id:
                pytest.skip("没有可用的采购订单行类型配置ID，跳过删除测试")
            
            # 2. 准备完整的 params 结构（包含 request 和 modelKey）
            set_dict = {
                "request": {
                    "id": self.__class__.po_item_type_id
                },
                "modelKey": self.MODEL_KEY  # modelKey 与 request 同级
            }
            
            # 3. 使用 standard_api_call 发送请求
            #    - param_path=["params"]: set_dict 完整替换 params
            #    - use_param_util=False: 不使用 ParamUtil，直接使用 set_dict
            #    - query_params: URL 参数（?tmodule=SCM_PUR&modelKey=XXX）
            response, _ = self.standard_api_call(
                api_key="(系统)删除数据服务",
                set_dict=set_dict,
                param_path=["params"],
                use_param_util=False,
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 清空类变量
            self.__class__.po_item_type_id = None
            self.__class__.po_item_type_code = None
            
            # 6. 记录报告
            self.logger.info(f"✅ 采购订单行类型配置删除成功")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

