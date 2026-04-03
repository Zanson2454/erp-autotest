import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("订单类型定义管理")
class TestSoTypeManagement(SlsBase):
    """销售订单类型定义表管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.so_type_id = None
        cls.so_type_code = None
        cls.logger.info("销售订单类型定义表管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

        super().teardown_class()
    @case_decorator(
        story="订单类型定义管理",
        title="测试订单类型定义表-根据ID查找数据服务",
        description="验证订单类型定义表-根据ID查找数据服务功能",
        severity="normal",
        order=1,
        tags=["订单类型", "ID查找", "SLS_SO_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_type_find_by_id_service(self):
        """订单类型定义表-根据ID查找数据服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单类型定义表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": 1}  # 使用默认ID进行测试
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单类型定义表-根据ID查找数据服务",
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
        story="订单类型定义管理",
        title="测试订单类型定义表-分页数据服务",
        description="验证订单类型定义表-分页数据服务功能",
        severity="normal",
        order=6,
        tags=["订单类型", "分页数据", "SLS_SO_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    def test_so_type_paging_data_service(self):
        """订单类型定义表-分页数据服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单类型定义表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "soTypeCode", "type": "TEXT"},
                    {"name": "soTypeName", "type": "TEXT"},
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单类型定义表-分页数据服务",
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
        story="订单类型定义管理",
        title="测试订单类型定义表-导入导出任务管理接口-提交导出任务",
        description="验证订单类型定义表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=3,
        tags=["订单类型", "导出任务", "SLS_SO_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_so_type_export_task(self):
        """订单类型定义表-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            params['params']= {
                    "taskName": f"订单类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$sls_so_type_cf",
                            "modelName": "订单类型定义表",
                            "sheetNo": 0,
                            "sheetName": "订单类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "类型编码",
                                    "type": "TEXT",
                                    "field": "soTypeCode"
                                },
                                {
                                    "name": "类型名称",
                                    "type": "TEXT",
                                    "field": "soTypeName"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_SCM$so_type_cf-list-ERP_SCM$sls_so_type_cf",
                        "viewKey": "SCM_SLS$so_type_cf:list",
                        "sceneKey": "SCM_SLS$so_type_cf",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "soTypeCode"
                                },
                                {
                                    "field": "soTypeName"
                                }
                            ],
                            "modelKey": "SCM_SLS$sls_so_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$sls_so_type_cf",
                        "modelName": "订单类型定义表",
                        "containerKey": "ERP_SCM$so_type_cf-list-ERP_SCM$sls_so_type_cf",
                        "viewKey": "SCM_SLS$so_type_cf:list",
                        "sceneKey": "SCM_SLS$so_type_cf"
                    }
            }
                        
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单类型定义表-导入导出任务管理接口-提交导出任务",
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


    @case_decorator(
        story="订单类型定义管理",
        title="测试订单类型定义表标准导出服务",
        description="验证订单类型定义表标准导出服务功能",
        severity="normal",
        order=5,
        tags=["订单类型", "导出", "SLS_SO_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_type_export_service(self):
        """订单类型定义表标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单类型定义表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_TYPE_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"订单类型定义表-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_type_cf",
                            "modelName": "订单类型定义表",
                            "sheetNo": 0,
                            "sheetName": "订单类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "订单类型编码",
                                    "type": "TEXT",
                                    "field": "so_type_code"
                                },
                                {
                                    "name": "订单类型名称",
                                    "type": "TEXT",
                                    "field": "so_type_name"
                                },
                                {
                                    "name": "描述",
                                    "type": "TEXT",
                                    "field": "description"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_SLS$so_type_cf",
                        "viewKey": "SCM_SLS$so_type_cf:list",
                        "sceneKey": "SCM_SLS$so_type_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "so_type_code"
                                },
                                {
                                    "field": "so_type_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_type_cf",
                        "modelName": "订单类型定义表",
                        "containerKey": "SCM_SLS$so_type_cf",
                        "viewKey": "SCM_SLS$so_type_cf:list",
                        "sceneKey": "SCM_SLS$so_type_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单类型定义表标准导出服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
