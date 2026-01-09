"""
库存类型配置管理测试模块
覆盖库存类型的CRUD操作、分页查询、导出功能
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("库存类型配置")
class TestInvTypeManagement(ScmInvBaseTest):
    """库存类型配置管理测试类"""
    
    # 常量配置
    TEST_PREFIX = "AT"
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_TEAM_ID = 22

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.inv_type_id = None
        cls._save_executed = False  # 防重复执行标记
        cls.logger.info("库存类型配置管理测试类初始化完成")

    @case_decorator(
        story="库存类型配置",
        title="测试保存库存类型",
        description="验证库存类型的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "库存类型", "配置"]
    )
    def test_save_inv_type(self):
        """测试保存库存类型"""
        try:
            # 防重复执行检查
            if self.__class__._save_executed and self.inv_type_id is not None:
                self.logger.info(f"保存方法已执行过，跳过重复执行，ID: {self.inv_type_id}")
                return
            
            # 1. 准备测试数据
            inv_type_code = self.mock_util.generate_unique_code(tag="AT")
            inv_type_name = f"库存类型_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("INV-库存类型-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            set_dict = {
                "id": None,
                "createdBy": None,
                "updatedBy": None,
                "createdAt": None,
                "updatedAt": None,
                "version": 0,
                "deleted": 0,
                "code": inv_type_code,
                "name": inv_type_name,
                "originOrgId": 0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            response_data = response.get("data", {}).get("data", {})
            self.__class__.inv_type_id = response_data.get("id")
            self.__class__._save_executed = True  # 标记已执行
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"库存类型保存成功，ID: {self.inv_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="库存类型配置",
        title="测试查询库存类型分页",
        description="验证库存类型的分页查询功能",
        severity="normal",
        order=3,
        tags=["库存", "库存类型", "查询"]
    )
    def test_query_inv_type_page(self):
        """测试查询库存类型分页"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("INV-库存类型--查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            # 3. 设置分页查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": self.DEFAULT_PAGE_SIZE,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "code": {
                                "operator": "CONTAINS",
                                "value": self.TEST_PREFIX
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 验证返回数据结构
            data = response.get("data", {}).get("data", {})
            total = data.get("total", 0)
            data_list = data.get("data", [])
            
            # 基础断言：验证分页查询结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("库存类型分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存类型配置",
        title="测试导出库存类型",
        description="验证库存类型的导出功能",
        severity="normal",
        order=4,
        tags=["库存", "库存类型", "导出"]
    )
    def test_export_inv_type(self):
        """测试导出库存类型"""
        try:
            # 确保前置数据存在
            if self.inv_type_id is None:
                self.test_save_inv_type()
            
            # 1. 构建导出URL
            url = "https://t-erp-huoshan-portal-test.app.duandian.com/api/trantor/service/engine/execute/SCM_INV$INV_INV_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"
            
            # 2. 构造导出参数（基于curl命令的完整参数结构）
            timestamp = self.mock_util.get_timestamp()
            export_params = {
                "serviceKey": "SCM_INV$INV_INV_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"库存类型-{self.nickname}-{timestamp}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_INV$inv_inv_type_cf",
                            "modelName": "库存类型定义表",
                            "sheetNo": 0,
                            "sheetName": "库存类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "名称",
                                    "type": "TEXT",
                                    "field": "name"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_INV$INV_TYPE_VIEW-table-container-SCM_INV$inv_inv_type_cf",
                        "viewKey": "SCM_INV$INV_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.inv_type_id]
                                            }
                                        }
                                    },
                                    "pageNo": 1,
                                    "pageSize": self.DEFAULT_PAGE_SIZE
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"}
                            ],
                            "modelKey": "SCM_INV$inv_inv_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_INV$inv_inv_type_cf",
                        "modelName": "库存类型定义表",
                        "containerKey": "SCM_INV$INV_TYPE_VIEW-table-container-SCM_INV$inv_inv_type_cf",
                        "viewKey": "SCM_INV$INV_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_TYPE_VIEW"
                    }
                }
            }
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=export_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("库存类型导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存类型配置",
        title="测试删除库存类型",
        description="验证库存类型的删除功能",
        severity="normal",
        order=5,
        tags=["库存", "库存类型", "删除"]
    )
    def test_delete_inv_type(self):
        """测试删除库存类型"""
        try:
            # 确保前置数据存在
            if self.inv_type_id is None:
                self.test_save_inv_type()
            
            # 1. 调用API
            api_path = self.get_api_path("INV-库存类型-删除服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.inv_type_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"库存类型删除成功，ID: {self.inv_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
