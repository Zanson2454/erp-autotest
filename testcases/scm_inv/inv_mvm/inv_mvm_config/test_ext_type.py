"""
移动类型扩展配置管理测试模块
覆盖移动类型扩展的CRUD操作、分页查询、导出功能
"""
import allure
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("移动类型扩展配置")
class TestInvMvmConfigManagement(ScmInvBaseTest):
    """移动类型扩展配置管理测试类"""
    
    # 常量配置
    TEST_PREFIX = "AT"
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_TEAM_ID = 22

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mvm_ext_type_id = None
        cls._save_executed = False  # 防重复执行标记
        cls.logger.info("移动类型扩展配置管理测试类初始化完成")

    @case_decorator(
        story="移动类型扩展配置",
        title="测试保存移动类型扩展",
        description="验证移动类型扩展的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "移动类型扩展", "配置"]
    )
    def test_save_mvm_ext_type(self):
        """测试保存移动类型扩展"""
        try:
            # 防重复执行检查
            if self.__class__._save_executed and self.mvm_ext_type_id is not None:
                self.logger.info(f"保存方法已执行过，跳过重复执行，ID: {self.mvm_ext_type_id}")
                return
            
            # 1. 准备测试数据
            timestamp_suffix = str(int(time.time() * 1000000))[-6:]
            ext_type_code = f"{self.TEST_PREFIX}{timestamp_suffix}"
            ext_type_name = f"移动类型扩展_{timestamp_suffix}"
            
            # 2. 调用API
            api_path = self.get_api_path("INV-移动扩展类型-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            set_dict = {
                "id": None,
                "code": ext_type_code,
                "uniqueCode": ext_type_code,
                "name": ext_type_name,
                "originOrgId": 0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            response_data = response.get("data", {}).get("data", {})
            self.__class__.mvm_ext_type_id = response_data.get("id")  # 保存到类变量，供其他测试方法使用
            self.__class__._save_executed = True  # 标记已执行
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"移动类型扩展保存成功，ID: {self.mvm_ext_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型扩展配置",
        title="测试查询移动类型扩展详情",
        description="验证移动类型扩展的详情查询功能",
        severity="normal",
        order=2,
        tags=["库存", "移动类型扩展", "查询"]
    )
    def test_query_mvm_ext_type_detail(self):
        """测试查询移动类型扩展详情"""
        try:
            # 确保前置数据存在
            if self.mvm_ext_type_id is None:
                self.test_save_mvm_ext_type()
            
            # 1. 调用API
            api_path = self.get_api_path("INV-移动扩展类型-详情服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.mvm_ext_type_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("id"), "=", self.mvm_ext_type_id)
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"移动类型扩展详情查询成功，ID: {self.mvm_ext_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型扩展配置",
        title="测试查询移动类型扩展分页",
        description="验证移动类型扩展的分页查询功能",
        severity="normal",
        order=3,
        tags=["库存", "移动类型扩展", "查询"]
    )
    def test_query_mvm_ext_type_page(self):
        """测试查询移动类型扩展分页"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("INV-移动扩展类型-查询分页服务")
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
                    {"name": "uniqueCode", "type": "TEXT"},
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
            
            self.logger.info("移动类型扩展分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.skip(reason="导出功能需要完整的业务流程支持，暂时跳过")
    @case_decorator(
        story="移动类型扩展配置",
        title="测试导出移动类型扩展",
        description="验证移动类型扩展的导出功能",
        severity="normal",
        order=4,
        tags=["库存", "移动类型扩展", "导出"]
    )
    def test_export_mvm_ext_type(self):
        """测试导出移动类型扩展"""
        try:
            # 依赖保存方法创建的数据
            if not self.mvm_ext_type_id:
                self.test_save_mvm_ext_type()
            
            # 1. 调用API
            api_path = self.get_api_path("移动类型扩展类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 构造导出参数
            timestamp = self.mock_util.get_timestamp()
            export_params = {
                "serviceKey": "SCM_INV$INV_MVM_EXT_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": self.DEFAULT_TEAM_ID,
                "params": {
                    "taskName": f"移动类型扩展-{self.nickname}-{timestamp}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_INV$inv_mvm_ext_type_cf",
                            "modelName": "移动类型扩展类型定义表",
                            "sheetNo": 0,
                            "sheetName": "移动类型扩展类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "简码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "唯一码",
                                    "type": "TEXT",
                                    "field": "uniqueCode"
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
                        "appId": 0,
                        "teamId": self.DEFAULT_TEAM_ID,
                        "containerKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW-table-container-SCM_INV$inv_mvm_ext_type_cf",
                        "viewKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.mvm_ext_type_id]
                                            }
                                        }
                                    },
                                    "pageNo": 1,
                                    "pageSize": self.DEFAULT_PAGE_SIZE
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "uniqueCode"},
                                {"field": "name"}
                            ],
                            "modelKey": "SCM_INV$inv_mvm_ext_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "appId": 0,
                        "teamId": self.DEFAULT_TEAM_ID,
                        "model": "SCM_INV$inv_mvm_ext_type_cf",
                        "modelName": "移动类型扩展类型定义表",
                        "containerKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW-table-container-SCM_INV$inv_mvm_ext_type_cf",
                        "viewKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_MVM_EXT_TYPE_VIEW"
                    }
                }
            }
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=export_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("移动类型扩展导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型扩展配置",
        title="测试删除移动类型扩展",
        description="验证移动类型扩展的删除功能",
        severity="normal",
        order=5,
        tags=["库存", "移动类型扩展", "删除"]
    )
    def test_delete_mvm_ext_type(self):
        """测试删除移动类型扩展"""
        try:
            # 确保前置数据存在
            if self.mvm_ext_type_id is None:
                self.test_save_mvm_ext_type()
            
            # 1. 调用API
            api_path = self.get_api_path("INV-移动扩展类型-删除服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.mvm_ext_type_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"移动类型扩展删除成功，ID: {self.mvm_ext_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

