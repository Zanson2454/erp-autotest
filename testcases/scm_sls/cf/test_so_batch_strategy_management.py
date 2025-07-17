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
@allure.feature("订单批次策略分配管理")
class TestSoBatchStrategyManagement(SlsBase):
    """销售订单批次策略分配表管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.batch_strategy_id = None
        cls.batch_strategy_code = None
        cls.logger.info("销售订单批次策略分配表管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_sls_so_batch_strategy_detm_cf",
                where="batch_strategy_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="订单批次策略分配管理",
        title="测试销售订单批次策略分配表标准导出服务",
        description="验证销售订单批次策略分配表标准导出服务功能",
        severity="normal",
        order=1,
        tags=["订单批次策略", "导出", "SLS_SO_BATCH_STRATEGY_DETM_CF_GEI_EXPORT_SERVICE"]
    )
    def test_so_batch_strategy_export_service(self):
        """销售订单批次策略分配表标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售订单批次策略分配表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_BATCH_STRATEGY_DETM_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"销售订单批次策略分配表-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf",
                            "modelName": "销售订单批次策略分配表",
                            "sheetNo": 0,
                            "sheetName": "销售订单批次策略分配表",
                            "headerConfigList": [
                                {
                                    "name": "批次策略分配编码",
                                    "type": "TEXT",
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "name": "批次策略分配名称",
                                    "type": "TEXT",
                                    "field": "batch_strategy_name"
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
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "field": "batch_strategy_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_batch_strategy_detm_cf",
                        "modelName": "销售订单批次策略分配表",
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单批次策略分配管理",
        title="测试销售订单批次策略分配表-导入导出任务管理接口-通过OSS提交导入任务",
        description="验证销售订单批次策略分配表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=2,
        tags=["订单批次策略", "OSS导入任务", "SLS_SO_BATCH_STRATEGY_DETM_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_so_batch_strategy_oss_import_task(self):
        """销售订单批次策略分配表-导入导出任务管理接口-通过OSS提交导入任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售订单批次策略分配表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_BATCH_STRATEGY_DETM_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"销售订单批次策略分配表-自动化测试-{self.mock_util.get_timestamp()}-OSS导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf",
                            "modelName": "销售订单批次策略分配表",
                            "sheetNo": 0,
                            "sheetName": "销售订单批次策略分配表",
                            "headerConfigList": [
                                {
                                    "name": "批次策略分配编码",
                                    "type": "TEXT",
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "name": "批次策略分配名称",
                                    "type": "TEXT",
                                    "field": "batch_strategy_name"
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
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "field": "batch_strategy_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_batch_strategy_detm_cf",
                        "modelName": "销售订单批次策略分配表",
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单批次策略分配管理",
        title="测试销售订单批次策略分配表标准导入服务",
        description="验证销售订单批次策略分配表标准导入服务功能",
        severity="normal",
        order=3,
        tags=["订单批次策略", "导入", "SLS_SO_BATCH_STRATEGY_DETM_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_so_batch_strategy_import_service(self):
        """销售订单批次策略分配表标准导入服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售订单批次策略分配表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_BATCH_STRATEGY_DETM_CF_GEI_IMPORT_SERVICE",
                "params": {
                    "taskName": f"销售订单批次策略分配表-自动化测试-{self.mock_util.get_timestamp()}-导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf",
                            "modelName": "销售订单批次策略分配表",
                            "sheetNo": 0,
                            "sheetName": "销售订单批次策略分配表",
                            "headerConfigList": [
                                {
                                    "name": "批次策略分配编码",
                                    "type": "TEXT",
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "name": "批次策略分配名称",
                                    "type": "TEXT",
                                    "field": "batch_strategy_name"
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
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "field": "batch_strategy_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_batch_strategy_detm_cf",
                        "modelName": "销售订单批次策略分配表",
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单批次策略分配管理",
        title="测试销售订单批次策略分配表-导入导出任务管理接口-提交导出任务",
        description="验证销售订单批次策略分配表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=4,
        tags=["订单批次策略", "导出任务", "SLS_SO_BATCH_STRATEGY_DETM_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_so_batch_strategy_export_task(self):
        """销售订单批次策略分配表-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售订单批次策略分配表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_BATCH_STRATEGY_DETM_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"销售订单批次策略分配表-自动化测试-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf",
                            "modelName": "销售订单批次策略分配表",
                            "sheetNo": 0,
                            "sheetName": "销售订单批次策略分配表",
                            "headerConfigList": [
                                {
                                    "name": "批次策略分配编码",
                                    "type": "TEXT",
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "name": "批次策略分配名称",
                                    "type": "TEXT",
                                    "field": "batch_strategy_name"
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
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "batch_strategy_code"
                                },
                                {
                                    "field": "batch_strategy_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_batch_strategy_detm_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_batch_strategy_detm_cf",
                        "modelName": "销售订单批次策略分配表",
                        "containerKey": "SCM_SLS$so_batch_strategy_detm_cf",
                        "viewKey": "SCM_SLS$so_batch_strategy_detm_cf:list",
                        "sceneKey": "SCM_SLS$so_batch_strategy_detm_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
