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
@allure.feature("销售审单规则管理")
class TestSoApprovalRuleManagement(SlsBase):
    """销售审单规则管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.approval_rule_id = None
        cls.approval_rule_code = None
        cls.logger.info("销售审单规则管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

        super().teardown_class()
    @case_decorator(
        story="销售审单规则管理",
        title="测试保存销售审单规则",
        description="验证SLS-审单规则-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["销售审单规则", "保存", "sls_order_audit_rule_save"]
    )
    def test_save_approval_rule(self):
        """保存销售审单规则用例"""
        try:
            # 1. 准备测试数据
            approval_rule_code = self.mock_util.generate_unique_code(tag="ApprovalRule")
            approval_rule_name = f"测试审单规则_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-审单规则-保存")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "desc", "calculateType", "status"], ["params", "request"]
            )
            set_dict = {
                "code": approval_rule_code,
                "name": approval_rule_name,
                "desc": self.mock_util.get_mock_remark(),
                "calculateType": "CUSTOM",
                "status":"ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-审单规则-保存",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            self.approval_rule_id = response.get("data", {}).get("data", {}).get("id")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        

    @case_decorator(
        story="销售审单规则管理",
        title="测试启用销售审单规则并清理缓存",
        description="验证SLS-审单规则-启用并清理缓存服务功能",
        severity="critical",
        order=7,
        tags=["销售审单规则", "启用", "清理缓存", "SO_APPROVAL_CF_ENABLE_AND_CLEAR_CACHE_ACTION_SERVICE"]
    )
    def test_enable_approval_rule_and_clear_cache(self):
        """启用销售审单规则并清理缓存用例"""
        try:
            # 1. 确保有测试数据
            if not self.approval_rule_id:
                self.test_save_approval_rule()
            self.logger.info(f"self.approval_rule_id: {self.approval_rule_id}")
            # 2. 调用API
            api_path = self.get_api_path("SLS-审单规则-启用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            self.logger.info(f"url: {url}")
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {
                "id": self.approval_rule_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-审单规则-启用并清理缓存服务",
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
        story="销售审单规则管理",
        title="测试停用销售审单规则并清理缓存",
        description="验证SLS-审单规则-停用并清理缓存服务功能",
        severity="critical",
        order=6,
        tags=["销售审单规则", "停用", "清理缓存", "SO_APPROVAL_CF_DISABLE_AND_CLEAR_CACHE_ACTION_SERVICE"]
    )
    def test_disable_approval_rule_and_clear_cache(self):
        """停用销售审单规则并清理缓存用例"""
        try:
            # 1. 确保有测试数据
            if not self.approval_rule_id:
                self.test_save_approval_rule()
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-审单规则-停用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {
                "id": self.approval_rule_id
            }
            
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-审单规则-停用并清理缓存服务",
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
        story="销售审单规则管理",
        title="测试销售审单规则-导入导出任务管理接口-提交导出任务",
        description="验证销售审单规则-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=2,
        tags=["销售审单规则", "导出任务", "SLS_SO_APPROVAL_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_so_approval_rule_export_task(self):
        """销售审单规则-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售审单规则-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            params['params']={
                "taskName": f"SLS-销售-审单规则-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_SLS$sls_so_approval_rule_cf",
                        "modelName": "销售审单规则",
                        "sheetNo": 0,
                        "sheetName": "销售审单规则",
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
                    "containerKey": "ERP_SCM$SLS_APPROVAL_RULE_MANAGE-list-ERP_SCM$sls_so_approval_rule_cf",
                    "viewKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE:list",
                    "sceneKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "code"
                            },
                            {
                                "field": "name"
                            }
                        ],
                        "modelKey": "SCM_SLS$sls_so_approval_rule_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_SLS$sls_so_approval_rule_cf",
                    "modelName": "销售审单规则",
                    "containerKey": "ERP_SCM$SLS_APPROVAL_RULE_MANAGE-list-ERP_SCM$sls_so_approval_rule_cf",
                    "viewKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE:list",
                    "sceneKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE"
                }
            }   
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售审单规则-导入导出任务管理接口-提交导出任务",
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
        story="销售审单规则管理",
        title="测试销售审单规则标准导入服务",
        description="验证销售审单规则标准导入服务功能",
        severity="normal",
        order=3,
        tags=["销售审单规则", "导入", "SLS_SO_APPROVAL_RULE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_approval_rule_import_service(self):
        """销售审单规则标准导入服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售审单规则标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_APPROVAL_RULE_CF_GEI_IMPORT_SERVICE",
                "params": {
                    "taskName": f"销售审单规则-自动化测试-{self.mock_util.get_timestamp()}-导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_approval_rule_cf",
                            "modelName": "销售审单规则",
                            "sheetNo": 0,
                            "sheetName": "销售审单规则",
                            "headerConfigList": [
                                {
                                    "name": "审单规则编码",
                                    "type": "TEXT",
                                    "field": "approval_rule_code"
                                },
                                {
                                    "name": "审单规则名称",
                                    "type": "TEXT",
                                    "field": "approval_rule_name"
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
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "approval_rule_code"
                                },
                                {
                                    "field": "approval_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_approval_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_approval_rule_cf",
                        "modelName": "销售审单规则",
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售审单规则标准导入服务",
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
        story="销售审单规则管理",
        title="测试销售审单规则标准导出服务",
        description="验证销售审单规则标准导出服务功能",
        severity="normal",
        order=4,
        tags=["销售审单规则", "导出", "SLS_SO_APPROVAL_RULE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_so_approval_rule_export_service(self):
        """销售审单规则标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售审单规则标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_APPROVAL_RULE_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"销售审单规则-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_approval_rule_cf",
                            "modelName": "销售审单规则",
                            "sheetNo": 0,
                            "sheetName": "销售审单规则",
                            "headerConfigList": [
                                {
                                    "name": "审单规则编码",
                                    "type": "TEXT",
                                    "field": "approval_rule_code"
                                },
                                {
                                    "name": "审单规则名称",
                                    "type": "TEXT",
                                    "field": "approval_rule_name"
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
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "approval_rule_code"
                                },
                                {
                                    "field": "approval_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_approval_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_approval_rule_cf",
                        "modelName": "销售审单规则",
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售审单规则标准导出服务",
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
        story="销售审单规则管理",
        title="测试销售审单规则-导入导出任务管理接口-通过OSS提交导入任务",
        description="验证销售审单规则-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=5,
        tags=["销售审单规则", "OSS导入任务", "SLS_SO_APPROVAL_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_so_approval_rule_oss_import_task(self):
        """销售审单规则-导入导出任务管理接口-通过OSS提交导入任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售审单规则-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_SO_APPROVAL_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"销售审单规则-自动化测试-{self.mock_util.get_timestamp()}-OSS导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$so_approval_rule_cf",
                            "modelName": "销售审单规则",
                            "sheetNo": 0,
                            "sheetName": "销售审单规则",
                            "headerConfigList": [
                                {
                                    "name": "审单规则编码",
                                    "type": "TEXT",
                                    "field": "approval_rule_code"
                                },
                                {
                                    "name": "审单规则名称",
                                    "type": "TEXT",
                                    "field": "approval_rule_name"
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
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "approval_rule_code"
                                },
                                {
                                    "field": "approval_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$so_approval_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$so_approval_rule_cf",
                        "modelName": "销售审单规则",
                        "containerKey": "SCM_SLS$so_approval_rule_cf",
                        "viewKey": "SCM_SLS$so_approval_rule_cf:list",
                        "sceneKey": "SCM_SLS$so_approval_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售审单规则-导入导出任务管理接口-通过OSS提交导入任务",
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
