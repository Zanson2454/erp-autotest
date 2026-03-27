import allure
import pytest
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("订单行项目类型定义管理")
class TestSoItemTypeManagement(SlsBase):
    """销售订单行项目类型定义表管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.so_item_type_id = None
        cls.so_item_type_code = None
        cls.logger.info("销售订单行项目类型定义表管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

    @case_decorator(
        story="订单行项目类型定义管理",
        title="测试SCM-销售订单行项目类型分页查询",
        description="验证SCM-销售订单行项目类型分页查询服务功能",
        severity="normal",
        order=1,
        tags=["订单行项目类型", "分页查询", "SO_ITEM_TYPE_PAGING_SERVICE"]
    )
    def test_so_item_type_paging_service(self):
        """SCM-销售订单行项目类型分页查询用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SCM-销售订单行项目类型分页查询")
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
                    {"name": "soItemTypeCode", "type": "TEXT"},
                    {"name": "soItemTypeName", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SCM-销售订单行项目类型分页查询",
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
        story="订单行项目类型定义管理",
        title="测试订单行项目类型定义表标准导入服务",
        description="验证订单行项目类型定义表标准导入服务功能",
        severity="normal",
        order=2,
        tags=["订单行项目类型", "导入", "SLS_SO_ITEM_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_item_type_import_service(self):
        """订单行项目类型定义表标准导入服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单行项目类型定义表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_ITEM_TYPE_CF_GEI_IMPORT_SERVICE",
                "params": {
                    "taskName": f"订单行项目类型定义表-自动化测试-{self.mock_util.get_timestamp()}-导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_item_type_cf",
                            "modelName": "订单行项目类型定义表",
                            "sheetNo": 0,
                            "sheetName": "订单行项目类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "订单行项目类型编码",
                                    "type": "TEXT",
                                    "field": "so_item_type_code"
                                },
                                {
                                    "name": "订单行项目类型名称",
                                    "type": "TEXT",
                                    "field": "so_item_type_name"
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
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "so_item_type_code"
                                },
                                {
                                    "field": "so_item_type_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_item_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_item_type_cf",
                        "modelName": "订单行项目类型定义表",
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单行项目类型定义表标准导入服务",
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

    @case_decorator(
        story="订单行项目类型定义管理",
        title="测试订单行项目类型定义表标准导出服务",
        description="验证订单行项目类型定义表标准导出服务功能",
        severity="normal",
        order=3,
        tags=["订单行项目类型", "导出", "SLS_SO_ITEM_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_item_type_export_service(self):
        """订单行项目类型定义表标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单行项目类型定义表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_ITEM_TYPE_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"订单行项目类型定义表-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_item_type_cf",
                            "modelName": "订单行项目类型定义表",
                            "sheetNo": 0,
                            "sheetName": "订单行项目类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "订单行项目类型编码",
                                    "type": "TEXT",
                                    "field": "so_item_type_code"
                                },
                                {
                                    "name": "订单行项目类型名称",
                                    "type": "TEXT",
                                    "field": "so_item_type_name"
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
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "so_item_type_code"
                                },
                                {
                                    "field": "so_item_type_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_item_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_item_type_cf",
                        "modelName": "订单行项目类型定义表",
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单行项目类型定义表标准导出服务",
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

    @case_decorator(
        story="订单行项目类型定义管理",
        title="测试订单行项目类型定义表-导入导出任务管理接口-通过OSS提交导入任务",
        description="验证订单行项目类型定义表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=4,
        tags=["订单行项目类型", "OSS导入任务", "SLS_SO_ITEM_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_so_item_type_oss_import_task(self):
        """订单行项目类型定义表-导入导出任务管理接口-通过OSS提交导入任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单行项目类型定义表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_ITEM_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"订单行项目类型定义表-自动化测试-{self.mock_util.get_timestamp()}-OSS导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_item_type_cf",
                            "modelName": "订单行项目类型定义表",
                            "sheetNo": 0,
                            "sheetName": "订单行项目类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "订单行项目类型编码",
                                    "type": "TEXT",
                                    "field": "so_item_type_code"
                                },
                                {
                                    "name": "订单行项目类型名称",
                                    "type": "TEXT",
                                    "field": "so_item_type_name"
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
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "so_item_type_code"
                                },
                                {
                                    "field": "so_item_type_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_item_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_item_type_cf",
                        "modelName": "订单行项目类型定义表",
                        "containerKey": "SCM_SLS$so_item_type_cf",
                        "viewKey": "SCM_SLS$so_item_type_cf:list",
                        "sceneKey": "SCM_SLS$so_item_type_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单行项目类型定义表-导入导出任务管理接口-通过OSS提交导入任务",
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

    @case_decorator(
        story="订单行项目类型定义管理",
        title="测试订单行项目类型定义表-导入导出任务管理接口-提交导出任务",
        description="验证订单行项目类型定义表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=5,
        tags=["订单行项目类型", "导出任务", "SLS_SO_ITEM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_so_item_type_export_task(self):
        """订单行项目类型定义表-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单行项目类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            params['params'] = {
                "taskName": f"订单行项目类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_SLS$sls_so_item_type_cf",
                        "modelName": "订单行项目类型定义表",
                        "sheetNo": 0,
                        "sheetName": "订单行项目类型定义表",
                        "headerConfigList": [
                            {
                                "name": "类型编码",
                                "type": "TEXT",
                                "field": "soItemTypeCode"
                            },
                            {
                                "name": "类型名称",
                                "type": "TEXT",
                                "field": "soItemTypeName"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "ERP_SCM$so_item_type_cf-list-ERP_SCM$sls_so_item_type_cf",
                    "viewKey": "SCM_SLS$so_item_type_cf:list",
                    "sceneKey": "SCM_SLS$so_item_type_cf",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "soItemTypeCode"
                            },
                            {
                                "field": "soItemTypeName"
                            }
                        ],
                        "modelKey": "SCM_SLS$sls_so_item_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_SLS$sls_so_item_type_cf",
                    "modelName": "订单行项目类型定义表",
                    "containerKey": "ERP_SCM$so_item_type_cf-list-ERP_SCM$sls_so_item_type_cf",
                    "viewKey": "SCM_SLS$so_item_type_cf:list",
                    "sceneKey": "SCM_SLS$so_item_type_cf"
                }
            }

            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单行项目类型定义表-导入导出任务管理接口-提交导出任务",
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
        story="订单项目行分配管理",
        title="测试订单项目行分配表标准导出服务",
        description="验证订单项目行分配表标准导出服务功能",
        severity="normal",
        order=6,
        tags=["订单项目行分配", "导出", "SLS_SO_ITEM_DETM_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_item_detm_export_service(self):
        """订单项目行分配表标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单项目行分配表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_ITEM_DETM_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"订单项目行分配表-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_item_detm_cf",
                            "modelName": "订单项目行分配表",
                            "sheetNo": 0,
                            "sheetName": "订单项目行分配表",
                            "headerConfigList": [
                                {
                                    "name": "订单项目行分配编码",
                                    "type": "TEXT",
                                    "field": "so_item_detm_code"
                                },
                                {
                                    "name": "订单项目行分配名称",
                                    "type": "TEXT",
                                    "field": "so_item_detm_name"
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
                        "containerKey": "SCM_SLS$so_item_detm_cf",
                        "viewKey": "SCM_SLS$so_item_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_item_detm_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "so_item_detm_code"
                                },
                                {
                                    "field": "so_item_detm_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_item_detm_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_item_detm_cf",
                        "modelName": "订单项目行分配表",
                        "containerKey": "SCM_SLS$so_item_detm_cf",
                        "viewKey": "SCM_SLS$so_item_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_item_detm_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单项目行分配表标准导出服务",
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

    @case_decorator(
        story="订单项目行分配管理",
        title="测试订单项目行分配表-导入导出任务管理接口-提交导出任务",
        description="验证订单项目行分配表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=7,
        tags=["订单项目行分配", "导出任务", "SLS_SO_ITEM_DETM_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_so_item_detm_export_task(self):
        """订单项目行分配表-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("订单项目行分配表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            params['params'] = {
                "taskName": f"订单项目行分配-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_SLS$sls_so_item_detm_cf",
                        "modelName": "订单项目行分配表",
                        "sheetNo": 0,
                        "sheetName": "订单项目行分配表",
                        "headerConfigList": [
                            {
                                "name": "销售订单类型",
                                "type": "TEXT",
                                "field": "soTypeId.soTypeName"
                            },
                            {
                                "name": "订单行项目类型组",
                                "type": "TEXT",
                                "field": "soItemTypeGroupId.name"
                            },
                            {
                                "name": "用途",
                                "type": "ENUM",
                                "field": "usageType",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "FREE_GIFT",
                                        "label": "赠品",
                                        "value": "FREE_GIFT"
                                    },
                                    {
                                        "_row_id_": "jNOSfni",
                                        "label": "定制",
                                        "value": "CUSTOMED"
                                    }
                                ]
                            },
                            {
                                "name": "高层级的项目类型",
                                "type": "TEXT",
                                "field": "parentSoItemTypeId.soItemTypeName"
                            },
                            {
                                "name": "默认订单行项目类型",
                                "type": "TEXT",
                                "field": "soItemTypeId.soItemTypeName"
                            },
                            {
                                "name": "可选订单行项目类型1",
                                "type": "TEXT",
                                "field": "soItemTypeId1.soItemTypeName"
                            },
                            {
                                "name": "可选订单行项目类型2",
                                "type": "TEXT",
                                "field": "soItemTypeId2.soItemTypeName"
                            },
                            {
                                "name": "可选订单行项目类型3",
                                "type": "TEXT",
                                "field": "soItemTypeId3.soItemTypeName"
                            },
                            {
                                "name": "备注",
                                "type": "TEXT",
                                "field": "remark"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "ERP_SCM$so_item_detm_scence-table-container-ERP_SCM$sls_so_item_detm_cf",
                    "viewKey": "SCM_SLS$so_item_detm_scence:list",
                    "sceneKey": "SCM_SLS$so_item_detm_scence",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "usageType"
                            },
                            {
                                "field": "remark"
                            },
                            {
                                "field": "soTypeId",
                                "selectFields": [
                                    {
                                        "field": "soTypeName"
                                    }
                                ]
                            },
                            {
                                "field": "soItemTypeGroupId",
                                "selectFields": [
                                    {
                                        "field": "name"
                                    }
                                ]
                            },
                            {
                                "field": "parentSoItemTypeId",
                                "selectFields": [
                                    {
                                        "field": "soItemTypeName"
                                    }
                                ]
                            },
                            {
                                "field": "soItemTypeId",
                                "selectFields": [
                                    {
                                        "field": "soItemTypeName"
                                    }
                                ]
                            },
                            {
                                "field": "soItemTypeId1",
                                "selectFields": [
                                    {
                                        "field": "soItemTypeName"
                                    }
                                ]
                            },
                            {
                                "field": "soItemTypeId2",
                                "selectFields": [
                                    {
                                        "field": "soItemTypeName"
                                    }
                                ]
                            },
                            {
                                "field": "soItemTypeId3",
                                "selectFields": [
                                    {
                                        "field": "soItemTypeName"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "SCM_SLS$sls_so_item_detm_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_SLS$sls_so_item_detm_cf",
                    "modelName": "订单项目行分配表",
                    "containerKey": "ERP_SCM$so_item_detm_scence-table-container-ERP_SCM$sls_so_item_detm_cf",
                    "viewKey": "SCM_SLS$so_item_detm_scence:list",
                    "sceneKey": "SCM_SLS$so_item_detm_scence"
                }
            }

            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单项目行分配表-导入导出任务管理接口-提交导出任务",
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
