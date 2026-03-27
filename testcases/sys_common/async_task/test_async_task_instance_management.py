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
@allure.feature("异步任务实例管理")
class TestAsyncTaskInstanceManagement(SysCommonBaseTest):
    """异步任务实例管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.task_instance_id = None
        cls.logger.info("异步任务实例管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.task_instance_id:
                cls.db.delete(
                    table="async_task_instance",  # 假设任务实例表名为async_task_instance
                    where="id = %s",
                    params=[cls.task_instance_id]
                )
            cls.db.delete(
                table="async_task_instance",
                where="task_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("异步任务实例测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="异步任务实例管理",
        title="测试创建任务实例",
        description="验证PI_ASYNC_TASK_TASK_INSTANCE_CREATE_POST功能 - 创建任务实例",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "async_task", "instance", "create"]
    )
    def test_task_instance_create_post(self):
        """测试创建任务实例 - PI_ASYNC_TASK_TASK_INSTANCE_CREATE_POST"""
        try:
            # 1. 准备测试数据
            task_code = f"AT_TASK_INSTANCE_{self.mock_util.get_timestamp()}"
            task_name = f"AT_TASK_NAME_{self.mock_util.get_timestamp()}"
            task_type = "EXPORT"  # 假设任务类型
            priority = 1
            status = "PENDING"
            remark = self.mock_util.get_mock_remark()
            
            # 2. 调用API
            api_path = self.get_api_path("/api/async-task/task-instance/create")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskCode", "taskName", "taskType", "priority", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "taskCode": task_code,
                "taskName": task_name,
                "taskType": task_type,
                "priority": priority,
                "status": status,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="/api/async-task/task-instance/create",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            instance_data = response.get("data", {}).get("data", {})
            self.task_instance_id = instance_data.get("id") if instance_data else None
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建任务实例ID: {self.task_instance_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务实例管理",
        title="测试任务实例分页查询",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_PAGE_POST功能 - 分页查询任务列表",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["sys_common", "async_task", "instance", "page"]
    )
    def test_task_instance_page_post(self):
        """测试任务实例分页查询 - API_ASYNC_TASK_TASK_INSTANCE_PAGE_POST"""
        try:
            # 确保有测试数据
            if not self.task_instance_id:
                self.test_task_instance_create_post()
            
            # 调用分页查询API
            api_path = self.get_api_path("异步任务-任务实例-分页查询任务列表")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
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
                    {"name": "taskCode", "type": "TEXT"},
                    {"name": "taskName", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="异步任务-任务实例-分页查询任务列表",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证分页结果
            paging_data = response.get("data", {}).get("data", {})
            instance_list = paging_data.get("data", [])
            total_count = paging_data.get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(instance_list), "<=", 20, "每页记录数不超过20")
            
            # 验证测试数据是否存在
            test_instance_found = any(
                ins.get("taskCode", "").startswith("AT_TASK_INSTANCE_") for ins in instance_list
            )
            self.assert_util.assert_by_operator(test_instance_found, "=", True, "测试任务实例未在分页结果中找到")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务实例管理",
        title="测试我的任务实例分页查询",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_MY_PAGE_POST功能 - 分页查询我的任务列表",
        severity="normal",
        order=5,
        tags=["sys_common", "async_task", "instance", "my_page"]
    )
    def test_task_instance_my_page_post(self):
        """测试我的任务实例分页查询 - API_ASYNC_TASK_TASK_INSTANCE_MY_PAGE_POST"""
        try:
            # 确保有测试数据
            if not self.task_instance_id:
                self.test_task_instance_create_post()
            
            api_path = self.get_api_path("异步任务-任务实例-分页查询我的任务列表")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="异步任务-任务实例-分页查询我的任务列表",
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
        story="异步任务实例管理",
        title="测试更新任务实例",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_UPDATE_POST功能 - 更新任务实例",
        severity="normal",
        order=7,
        tags=["sys_common", "async_task", "instance", "update"]
    )
    def test_task_instance_update_post(self):
        """测试更新任务实例 - API_ASYNC_TASK_TASK_INSTANCE_UPDATE_POST"""
        try:
            if not self.task_instance_id:
                self.test_task_instance_create_post()
            
            # 更新数据
            new_status = "RUNNING"
            update_remark = f"更新备注_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("/api/async-task/task-instance/update")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.task_instance_id,
                "status": new_status,
                "remark": update_remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="/api/async-task/task-instance/update",
                set_dict=filtered_params.get("params", {}),
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
        story="异步任务实例管理",
        title="测试标记任务已读",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_USER_MARK_PUT功能 - 标记任务已读时间",
        severity="normal",
        order=8,
        tags=["sys_common", "async_task", "instance", "mark"]
    )
    def test_task_instance_user_mark_put(self):
        """测试标记任务已读 - API_ASYNC_TASK_TASK_INSTANCE_USER_MARK_PUT"""
        try:
            if not self.task_instance_id:
                self.test_task_instance_create_post()
            
            api_path = self.get_api_path("异步任务-任务实例-标记任务已读时间")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.task_instance_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.put(url, json=filtered_params)  # PUT请求
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务实例管理",
        title="测试查询今日任务列表",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_TODAY_LIST_GET功能 - 查询今日任务列表",
        severity="normal",
        order=9,
        tags=["sys_common", "async_task", "instance", "today_list"]
    )
    def test_task_instance_today_list_get(self):
        """测试查询今日任务列表 - API_ASYNC_TASK_TASK_INSTANCE_TODAY_LIST_GET"""
        try:
            api_path = self.get_api_path("异步任务-任务实例-查询今日任务列表")
            url = self.get_api_url(api_path)
            
            # GET请求，可能有query参数
            params = {}  # 假设无特定参数，或添加日期范围
            response = self.http.get(url, params=params)
            self.assert_util.assert_response_data(response)
            
            today_list = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(today_list, "not_empty", "今日任务列表不应为空")
            
            a.json(params, "查询参数")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="异步任务实例管理",
        title="测试查询最新任务状态",
        description="验证API_ASYNC_TASK_TASK_INSTANCE_LATEST_GET功能 - 查询今日任务状态",
        severity="normal",
        order=10,
        tags=["sys_common", "async_task", "instance", "latest"]
    )
    def test_task_instance_latest_get(self):
        """测试查询最新任务状态 - API_ASYNC_TASK_TASK_INSTANCE_LATEST_GET"""
        try:
            api_path = self.get_api_path("异步任务-任务实例-查询今日任务状态")
            url = self.get_api_url(api_path)
            
            response = self.http.get(url)
            self.assert_util.assert_response_data(response)
            
            latest_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(latest_data, "not_empty", "最新任务状态不应为空")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
