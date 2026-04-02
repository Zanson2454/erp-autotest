import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("系统通用模块")
@allure.feature("异步任务定义管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestAsyncTaskDefinitionManagement(SysCommonBaseTest):
    """异步任务定义管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.task_definition_id = None
        cls.logger.info("异步任务定义管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.task_definition_id:
                cls.db.delete(
                    table="async_task_definition",  # 假设任务定义表名为async_task_definition
                    where="id = %s",
                    params=[cls.task_definition_id]
                )
            cls.db.delete(
                table="async_task_definition",
                where="definition_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("异步任务定义测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="异步任务定义管理",
        title="测试保存任务定义",
        description="验证API_ASYNC_TASK_TASK_DEFINITION_SAVE_POST功能 - 保存任务定义",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "async_task", "definition", "save"]
    )
    def test_task_definition_save_post(self):
        """测试保存任务定义 - API_ASYNC_TASK_TASK_DEFINITION_SAVE_POST"""
        try:
            # 1. 准备测试数据
            definition_code = f"AT_TASK_DEFINITION_{self.mock_util.get_timestamp()}"
            definition_name = f"AT_DEFINITION_NAME_{self.mock_util.get_timestamp()}"
            task_type = "EXPORT"
            handler_class = "com.example.AsyncTaskHandler"
            description = self.mock_util.get_mock_remark()
            enabled = True
            
            # 2. 调用API
            api_path = self.get_api_path("异步任务-任务定义-保存任务定义")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["definitionCode", "definitionName", "taskType", "handlerClass", "description", "enabled"],
                ["params", "request"]
            )
            set_dict = {
                "definitionCode": definition_code,
                "definitionName": definition_name,
                "taskType": task_type,
                "handlerClass": handler_class,
                "description": description,
                "enabled": enabled
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="异步任务-任务定义-保存任务定义",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            definition_data = response.get("data", {}).get("data", {})
            self.task_definition_id = definition_data.get("id") if definition_data else None
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建任务定义ID: {self.task_definition_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务定义管理",
        title="测试任务定义分页查询",
        description="验证API_ASYNC_TASK_TASK_DEFINITION_PAGE_POST功能 - 分页查询任务定义",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["sys_common", "async_task", "definition", "page"]
    )
    def test_task_definition_page_post(self):
        """测试任务定义分页查询 - API_ASYNC_TASK_TASK_DEFINITION_PAGE_POST"""
        try:
            # 确保有测试数据
            if not self.task_definition_id:
                self._ensure_task_definition_save_post()
            
            api_path = self.get_api_path("异步任务-任务定义-分页查询任务定义")
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
                    {"name": "definitionCode", "type": "TEXT"},
                    {"name": "definitionName", "type": "TEXT"},
                    {"name": "taskType", "type": "TEXT"},
                    {"name": "enabled", "type": "BOOLEAN"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="异步任务-任务定义-分页查询任务定义",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证分页结果
            paging_data = response.get("data", {}).get("data", {})
            definition_list = paging_data.get("data", [])
            total_count = paging_data.get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(definition_list), "<=", 20, "每页记录数不超过20")
            
            # 验证测试数据是否存在
            test_definition_found = any(
                defn.get("definitionCode", "").startswith("AT_TASK_DEFINITION_") for defn in definition_list
            )
            self.assert_util.assert_by_operator(test_definition_found, "=", True, "测试任务定义未在分页结果中找到")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务定义管理",
        title="测试删除任务定义",
        description="验证API_ASYNC_TASK_TASK_DEFINITION_DELETE_POST功能 - 删除任务定义",
        severity="normal",
        order=16,
        tags=["sys_common", "async_task", "definition", "delete"]
    )
    def test_task_definition_delete_post(self):
        """测试删除任务定义 - API_ASYNC_TASK_TASK_DEFINITION_DELETE_POST"""
        try:
            # 确保定义存在
            if not self.task_definition_id:
                self._ensure_task_definition_save_post()
            
            api_path = self.get_api_path("异步任务-任务定义-删除任务定义")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.task_definition_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="异步任务-任务定义-删除任务定义",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            self.task_definition_id = None  # 标记已删除
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除任务定义ID: {self.task_definition_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
