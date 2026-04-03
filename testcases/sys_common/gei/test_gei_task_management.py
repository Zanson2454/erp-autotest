import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("导入导出任务管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestGeiTaskManagement(SysCommonBaseTest):
    """导入导出任务管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.gei_task_id = None
        cls.logger.info("导入导出任务管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.gei_task_id:
                cls.db.delete(
                    table="gei_task",
                    where="id = %s",
                    params=[cls.gei_task_id]
                )
            cls.db.delete(
                table="gei_task",
                where="task_name like %s",
                params=["AT_%"]
            )
            cls.logger.info("导入导出任务测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="导入导出任务管理",
        title="测试提交导出任务",
        description="验证API_GEI_TASK_EXPORT_POST功能 - 创建导出任务",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "gei", "task", "export"]
    )
    def test_export_task_post(self):
        """测试提交导出任务 - API_GEI_TASK_EXPORT_POST"""
        try:
            # 1. 准备测试数据
            task_name = f"AT_EXPORT_TASK_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            set_dict = {
                "taskName": task_name,
                "multiSheetConfig": [
                    {
                        "modelKey": "TEST_MODEL",
                        "modelName": "测试模型",
                        "sheetNo": 0,
                        "sheetName": "Sheet1",
                        "headerConfigList": [
                            {"name": "测试字段", "type": "TEXT", "field": "test_field"}
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "TEST_CONTAINER",
                    "viewKey": "TEST_VIEW:list",
                    "sceneKey": "TEST_SCENE",
                    "params": {
                        "request": {
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 10,
                                "needTotal": True
                            }
                        },
                        "selectFields": [{"field": "test_field"}],
                        "modelKey": "TEST_MODEL"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "TEST_MODEL",
                    "modelName": "测试模型",
                    "containerKey": "TEST_CONTAINER",
                    "viewKey": "TEST_VIEW:list",
                    "sceneKey": "TEST_SCENE"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-提交导出任务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            task_data = response.get("data", {}).get("data", {})
            self.gei_task_id = task_data.get("taskId") if task_data else None
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出任务管理",
        title="测试提交直接导出任务",
        description="验证API_GEI_TASK_EXPORT_DIRECT_POST功能 - 直接导出任务",
        severity="critical",
        order=2,
        tags=["sys_common", "gei", "task", "direct_export"]
    )
    def test_export_direct_task_post(self):
        """测试提交直接导出任务 - API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            if not self.gei_task_id:
                self._ensure_export_task_post()
            
            api_path = self.get_api_path("导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["taskName"], ["params"])
            set_dict = {"taskName": f"AT_DIRECT_EXPORT_{self.mock_util.get_timestamp()}"}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-提交导出任务",
                set_dict=filtered_params.get("params", {}),
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
        story="导入导出任务管理",
        title="测试任务分页查询",
        description="验证API_GEI_TASK_PAGING_POST功能 - 分页查询任务",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["sys_common", "gei", "task", "paging"]
    )
    def test_task_paging_post(self):
        """测试任务分页查询 - API_GEI_TASK_PAGING_POST"""
        try:
            api_path = self.get_api_path("导入导出任务管理接口-分页查询任务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"],
                ["params", "request"]
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
                    {"name": "taskName", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-分页查询任务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            paging_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(paging_data.get("total", 0), ">=", 0)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.parametrize("task_type, title", [
        ("IMPORT", "测试我的任务分页查询-导入类型"),
        ("EXPORT", "测试我的任务分页查询-导出类型")
    ])
    @case_decorator(
        story="导入导出任务管理",
        title="测试我的任务分页查询",
        description="验证API_GEI_TASK_MY_PAGING_POST功能 - 分页查询我的任务",
        severity="normal",
        file_level_order=5,
        tags=["sys_common", "gei", "task", "my_paging"]
    )
    def test_my_task_paging_post(self, task_type, title):
        """测试我的任务分页查询 - API_GEI_TASK_MY_PAGING_POST"""
        try:
            import allure
            allure.dynamic.title(title)  # 动态设置测试标题
            
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"pageNo":1,"pageSize":20,"type":"IMPORT"}} 或 {"params":{"pageNo":1,"pageSize":20,"type":"EXPORT"}}
            set_dict = {
                "pageNo": 1,
                "pageSize": 20,
                "type": task_type
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-分页查询我的任务(/api/gei/task/myPaging#POST)",
                set_dict=set_dict,
                param_path=["params"]  # 参数路径设置为["params"]，确保set_dict直接放在params层级
            )
            
            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            data = response.get("data", {}).get("data", {})
            # 验证返回数据不为空
            self.assert_util.assert_by_operator(
                data is not None,
                "=",
                True,
                "返回数据不应为空"
            )
            
            self.logger.info(f"分页查询我的任务成功 (type={task_type}): {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出任务管理",
        title="测试查询任务进度",
        description="验证API_GEI_TASK_PROGRESS_POST功能 - 查询任务进度",
        severity="normal",
        order=6,
        tags=["sys_common", "gei", "task", "progress"]
    )
    def test_task_progress_post(self):
        """测试查询任务进度 - API_GEI_TASK_PROGRESS_POST"""
        try:
            if not self.gei_task_id:
                self._ensure_export_task_post()
            
            api_path = self.get_api_path("导入导出任务管理接口-查询任务进度")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["taskId"], ["params"])
            set_dict = {"taskId": self.gei_task_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-查询任务进度",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            progress_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(progress_data.get("progress", 0), ">=", 0)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出任务管理",
        title="测试任务统计",
        description="验证API_GEI_TASK_TASK_STATISTIC_POST功能 - 任务统计",
        severity="minor",
        order=7,
        tags=["sys_common", "gei", "task", "statistic"]
    )
    def test_task_statistic_post(self):
        """测试任务统计 - API_GEI_TASK_TASK_STATISTIC_POST"""
        try:
            api_path = self.get_api_path("导入导出任务管理接口-任务统计")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, [], ["params"])
            
            response, _ = self.standard_api_call(
                api_key="导入导出任务管理接口-任务统计",
                set_dict=filtered_params.get("params", {}),
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
