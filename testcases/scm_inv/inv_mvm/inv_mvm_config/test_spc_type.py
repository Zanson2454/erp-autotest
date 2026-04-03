"""
特殊库存类型配置管理测试模块
覆盖特殊库存类型的CRUD操作、分页查询、导出功能
"""
import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("特殊库存类型配置")
class TestSpcTypeManagement(ScmInvBaseTest):
    """特殊库存类型配置管理测试类"""
    
    # 常量配置
    TEST_PREFIX = "AT"
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_TEAM_ID = 22

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.spc_type_id = None
        cls._save_executed = False  # 添加执行标记
        cls.logger.info("特殊库存类型配置管理测试类初始化完成")

    @case_decorator(
        story="特殊库存类型配置",
        title="测试保存特殊库存类型",
        description="验证特殊库存类型的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "特殊库存类型", "配置"]
    )
    def test_save_spc_type(self):
        """测试保存特殊库存类型"""
        try:
            # 防重复执行检查
            if self.__class__._save_executed and self.spc_type_id is not None:
                self.logger.info(f"保存方法已执行过，跳过重复执行，ID: {self.spc_type_id}")
                return
            
            # 1. 准备测试数据
            spc_type_code = self.mock_util.generate_unique_code(tag="AT")
            spc_type_name = f"特殊库存类型_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("INV-特殊库存类型-保存服务")
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
                "code": spc_type_code,
                "name": spc_type_name,
                "isPushInvValue": True,
                "originOrgId": 0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-特殊库存类型-保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            response_data = response.get("data", {}).get("data", {})
            self.__class__.spc_type_id = response_data.get("id")
            self.__class__._save_executed = True  # 标记已执行
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"特殊库存类型保存成功，ID: {self.spc_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特殊库存类型配置",
        title="测试查询特殊库存类型详情",
        description="验证特殊库存类型的详情查询功能",
        severity="normal",
        order=2,
        tags=["库存", "特殊库存类型", "查询"]
    )
    def test_query_spc_type_detail(self):
        """测试查询特殊库存类型详情"""
        try:
            # 确保前置数据存在
            if self.spc_type_id is None:
                self._ensure_save_spc_type()
            
            # 1. 调用API
            api_path = self.get_api_path("INV-特殊库存类型-详情查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.spc_type_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-特殊库存类型-详情查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("id"), "=", self.spc_type_id)
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"特殊库存类型详情查询成功，ID: {self.spc_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特殊库存类型配置",
        title="测试查询特殊库存类型分页",
        description="验证特殊库存类型的分页查询功能",
        severity="normal",
        order=3,
        tags=["库存", "特殊库存类型", "查询"]
    )
    def test_query_spc_type_page(self):
        """测试查询特殊库存类型分页"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("INV-特殊库存类型-查询分页服务")
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
            response, _ = self.standard_api_call(
                api_key="INV-特殊库存类型-查询分页服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
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
            
            self.logger.info("特殊库存类型分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.skip(reason="导出功能需要完整的业务流程支持，暂时跳过")
    @case_decorator(
        story="特殊库存类型配置",
        title="测试导出特殊库存类型",
        description="验证特殊库存类型的导出功能",
        severity="normal",
        order=4,
        tags=["库存", "特殊库存类型", "导出"]
    )
    def test_export_spc_type(self):
        """测试导出特殊库存类型"""
        try:
            # 依赖保存方法创建的数据
            if not self.spc_type_id:
                self._ensure_save_spc_type()
            
            # 1. 调用API
            api_path = self.get_api_path("特殊库存标识定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 构造导出参数
            timestamp = self.mock_util.get_timestamp()
            export_params = {
                "serviceKey": "SCM_INV$INV_SPC_STK_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"特殊库存类型-{self.nickname}-{timestamp}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_INV$inv_spc_stk_type_cf",
                            "modelName": "特殊库存标识定义表",
                            "sheetNo": 0,
                            "sheetName": "特殊库存标识定义表",
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
                                },
                                {
                                    "name": "是否推送存货价值",
                                    "type": "BOOL",
                                    "field": "isPushInvValue"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_INV$INV_SPC_TYPE_VIEW-table-container-SCM_INV$inv_spc_stk_type_cf",
                        "viewKey": "SCM_INV$INV_SPC_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_SPC_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.spc_type_id]
                                            }
                                        }
                                    },
                                    "pageNo": 1,
                                    "pageSize": self.DEFAULT_PAGE_SIZE
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"},
                                {"field": "isPushInvValue"}
                            ],
                            "modelKey": "SCM_INV$inv_spc_stk_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_INV$inv_spc_stk_type_cf",
                        "modelName": "特殊库存标识定义表",
                        "containerKey": "SCM_INV$INV_SPC_TYPE_VIEW-table-container-SCM_INV$inv_spc_stk_type_cf",
                        "viewKey": "SCM_INV$INV_SPC_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_SPC_TYPE_VIEW"
                    }
                }
            }
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="特殊库存标识定义表-导入导出任务管理接口-提交导出任务",
                set_dict=(export_params.get("params", {}) if isinstance(export_params, dict) else export_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("特殊库存类型导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="特殊库存类型删除可能受业务限制，需要确认业务规则后再启用")
    @case_decorator(
        story="特殊库存类型配置",
        title="测试删除特殊库存类型",
        description="验证特殊库存类型的删除功能",
        severity="normal",
        order=5,
        tags=["库存", "特殊库存类型", "删除"]
    )
    def test_delete_spc_type(self):
        """测试删除特殊库存类型"""
        try:
            # 确保前置数据存在
            if self.spc_type_id is None:
                self._ensure_save_spc_type()
            
            # 1. 调用API
            api_path = self.get_api_path("INV-特殊库存类型-删除服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.spc_type_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-特殊库存类型-删除服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"特殊库存类型删除成功，ID: {self.spc_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
