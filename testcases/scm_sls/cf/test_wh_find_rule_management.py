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
@allure.feature("寻仓规则配置管理")
class TestWhFindRuleManagement(SlsBase):
    """销售寻仓规则配置表管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.wh_find_rule_id = None
        cls.wh_find_rule_code = None
        cls.logger.info("销售寻仓规则配置表管理测试类初始化完成")
        
        # 依赖主数据
        cls.sls_org_id = cls.md_cache_data.get("org_info").get("sls_org_info")[0].get("id")
        cls.sls_dc_id = cls.md_cache_data.get("org_info").get("sls_dc_md")[0].get("id")
        cls.inv_loc_id = cls.md_cache_data.get("org_info").get("inv_loc_info")[0].get("id")

    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

        super().teardown_class()
    @case_decorator(
        story="寻仓规则配置管理",
        title="测试寻仓规则配置表-导入导出任务管理接口-提交导出任务",
        description="验证销售寻仓规则配置表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=1,
        tags=["寻仓规则", "导出任务", "SLS_WH_FIND_RULE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_wh_find_rule_export_task(self):
        """寻仓规则配置表-导入导出任务管理接口-提交导出任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售寻仓规则配置表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            params['params'] = {
                    "taskName": f"寻仓规则配置表-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$sls_wh_find_rule_cf",
                            "modelName": "寻仓规则配置表",
                            "sheetNo": 0,
                            "sheetName": "寻仓规则配置表",
                            "headerConfigList": [
                                {
                                    "name": "寻仓规则编码",
                                    "type": "TEXT",
                                    "field": "name"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW:list-SCM_SLS$sls_wh_find_rule_cf",
                        "viewKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW:list",
                        "sceneKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "name"
                                }
                            ],
                            "modelKey": "SCM_SLS$sls_wh_find_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$sls_wh_find_rule_cf",
                        "modelName": "寻仓规则配置表",
                        "containerKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW:list-SCM_SLS$sls_wh_find_rule_cf",
                        "viewKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW:list",
                        "sceneKey": "SCM_SLS$SLS_WH_FIND_RULE_VIEW"
                    }
                }

            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售寻仓规则配置表-导入导出任务管理接口-提交导出任务",
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
        story="寻仓规则配置管理",
        title="测试寻仓规则保存",
        description="验证销售寻仓规则保存功能",
        severity="normal",
        order=2,
        tags=["寻仓规则", "保存", "WH_FIND_RULE_UPDATE_SERVICE"]
    )
    def test_wh_find_rule_save(self):
        """寻仓规则保存用例"""
        try:
            # 1. 准备测试数据
            wh_find_rule_name = f"自动化寻仓规则_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("寻仓规则保存")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["name", "sls_org_id", "sls_dc_id", "inv_loc", "wms_strategy", "status"], ["params","request"]
            )
            set_dict =  {
                        "name": wh_find_rule_name,
                        "sls_org_id": {"id": self.sls_org_id},
                        "sls_dc_id": {"id": self.sls_dc_id},
                        "inv_loc": {"id": self.inv_loc_id},
                        "wms_strategy" : "DEFAULT_PRIORITY",
                        "status": "DRAFT"
                    }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="寻仓规则保存",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 5. 保存数据和报告
            self.wh_find_rule_id = response.get("data", {}).get("data", {})
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="寻仓规则配置管理",
        title="测试寻仓规则详情查询",
        description="验证销售寻仓规则详情查询功能",
        severity="normal",
        order=3,
        tags=["寻仓规则", "详情查询", "WH_FIND_RULE_DETAIL_SERVICE"]
    )
    def test_wh_find_rule_detail(self):
        """寻仓规则详情查询用例"""
        try:
            # 检查依赖数据
            if not self.wh_find_rule_id:
                self.test_wh_find_rule_save()
            
            # 1. 调用API
            api_path = self.get_api_path("寻仓规则详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$WH_FIND_RULE_DETAIL_SERVICE",
                "params": {
                    "request": {
                        "id": self.wh_find_rule_id
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="寻仓规则详情",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 验证返回数据
            response_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(response_data.get("wh_find_rule_code"), "=", self.wh_find_rule_code)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="寻仓规则配置管理",
        title="测试寻仓规则启用",
        description="验证销售寻仓规则启用功能",
        severity="normal",
        order=4,
        tags=["寻仓规则", "启用", "WH_FIND_RULE_ENABLED_SERVICE"]
    )
    def test_wh_find_rule_enable(self):
        """寻仓规则启用用例"""
        try:
            # 检查依赖数据
            if not self.wh_find_rule_id:
                self.test_wh_find_rule_save()
            
            # 1. 调用API
            api_path = self.get_api_path("寻仓规则启用")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$WH_FIND_RULE_ENABLED_SERVICE",
                "params": {
                    "request": {
                        "id": self.wh_find_rule_id
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="寻仓规则启用",
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
        story="寻仓规则配置管理",
        title="测试寻仓规则停用",
        description="验证销售寻仓规则停用功能",
        severity="normal",
        order=5,
        tags=["寻仓规则", "停用", "WH_FIND_RULE_DISABLED_SERVICE"]
    )
    def test_wh_find_rule_disable(self):
        """寻仓规则停用用例"""
        try:
            # 检查依赖数据
            if not self.wh_find_rule_id:
                self.test_wh_find_rule_save()
            
            # 1. 调用API
            api_path = self.get_api_path("寻仓规则停用")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$WH_FIND_RULE_DISABLED_SERVICE",
                "params": {
                    "request": {
                        "id": self.wh_find_rule_id
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="寻仓规则停用",
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
        story="寻仓规则配置管理",
        title="测试寻仓规则删除",
        description="验证销售寻仓规则删除功能",
        severity="normal",
        order=6,
        tags=["寻仓规则", "删除", "WH_FIND_RULE_DELETE_SERVICE"]
    )
    def test_wh_find_rule_delete(self):
        """寻仓规则删除用例"""
        try:
            # 检查依赖数据
            if not self.wh_find_rule_id:
                self.test_wh_find_rule_save()
            
            # 1. 调用API
            api_path = self.get_api_path("寻仓规则删除")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$WH_FIND_RULE_DELETE_SERVICE",
                "params": {
                    "request": {
                        "id": self.wh_find_rule_id
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="寻仓规则删除",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 清理数据
            self.wh_find_rule_id = None
            self.wh_find_rule_code = None
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ==================== 跳过的测试用例 ====================

    @case_decorator(
        story="寻仓规则配置管理",
        title="测试寻仓规则配置表标准导入服务",
        description="验证销售寻仓规则配置表标准导入服务功能",
        severity="normal",
        order=7,
        tags=["寻仓规则", "导入", "SLS_WH_FIND_RULE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_wh_find_rule_import_service(self):
        """寻仓规则配置表标准导入服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售寻仓规则配置表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_WH_FIND_RULE_CF_GEI_IMPORT_SERVICE",
                "params": {
                    "taskName": f"寻仓规则配置表-自动化测试-{self.mock_util.get_timestamp()}-导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$wh_find_rule_cf",
                            "modelName": "寻仓规则配置表",
                            "sheetNo": 0,
                            "sheetName": "寻仓规则配置表",
                            "headerConfigList": [

                                {
                                    "name": "寻仓规则名称",
                                    "type": "TEXT",
                                    "field": "wh_find_rule_name"
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
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "wh_find_rule_code"
                                },
                                {
                                    "field": "wh_find_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$wh_find_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$wh_find_rule_cf",
                        "modelName": "寻仓规则配置表",
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售寻仓规则配置表标准导入服务",
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
        story="寻仓规则配置管理",
        title="测试寻仓规则配置表-导入导出任务管理接口-通过OSS提交导入任务",
        description="验证销售寻仓规则配置表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=8,
        tags=["寻仓规则", "OSS导入任务", "SLS_WH_FIND_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_wh_find_rule_oss_import_task(self):
        """寻仓规则配置表-导入导出任务管理接口-通过OSS提交导入任务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售寻仓规则配置表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_WH_FIND_RULE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"寻仓规则配置表-自动化测试-{self.mock_util.get_timestamp()}-OSS导入",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$wh_find_rule_cf",
                            "modelName": "寻仓规则配置表",
                            "sheetNo": 0,
                            "sheetName": "寻仓规则配置表",
                            "headerConfigList": [
                                {
                                    "name": "寻仓规则编码",
                                    "type": "TEXT",
                                    "field": "wh_find_rule_code"
                                },
                                {
                                    "name": "寻仓规则名称",
                                    "type": "TEXT",
                                    "field": "wh_find_rule_name"
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
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "wh_find_rule_code"
                                },
                                {
                                    "field": "wh_find_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$wh_find_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$wh_find_rule_cf",
                        "modelName": "寻仓规则配置表",
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售寻仓规则配置表-导入导出任务管理接口-通过OSS提交导入任务",
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
        story="寻仓规则配置管理",
        title="测试寻仓规则配置表标准导出服务",
        description="验证销售寻仓规则配置表标准导出服务功能",
        severity="normal",
        order=9,
        tags=["寻仓规则", "导出", "SLS_WH_FIND_RULE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出服务暂时跳过")
    def test_wh_find_rule_export_service(self):
        """寻仓规则配置表标准导出服务用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售寻仓规则配置表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$SLS_WH_FIND_RULE_CF_GEI_EXPORT_SERVICE",
                "params": {
                    "taskName": f"寻仓规则配置表-自动化测试-{self.mock_util.get_timestamp()}-标准导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_SLS$wh_find_rule_cf",
                            "modelName": "寻仓规则配置表",
                            "sheetNo": 0,
                            "sheetName": "寻仓规则配置表",
                            "headerConfigList": [
                                {
                                    "name": "寻仓规则编码",
                                    "type": "TEXT",
                                    "field": "wh_find_rule_code"
                                },
                                {
                                    "name": "寻仓规则名称",
                                    "type": "TEXT",
                                    "field": "wh_find_rule_name"
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
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "wh_find_rule_code"
                                },
                                {
                                    "field": "wh_find_rule_name"
                                },
                                {
                                    "field": "description"
                                }
                            ],
                            "modelKey": "SCM_SLS$wh_find_rule_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_SLS$wh_find_rule_cf",
                        "modelName": "寻仓规则配置表",
                        "containerKey": "SCM_SLS$wh_find_rule_cf",
                        "viewKey": "SCM_SLS$wh_find_rule_cf:list",
                        "sceneKey": "SCM_SLS$wh_find_rule_cf"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售寻仓规则配置表标准导出服务",
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
