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
@allure.feature("通知任务管理")
class TestNoticeTaskManagement(SysCommonBaseTest):
    """通知任务管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.notice_task_id = None
        cls.logger.info("通知任务管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.notice_task_id:
                cls.db.delete(
                    table="notice_task",  # 假设通知任务表名为notice_task
                    where="id = %s",
                    params=[cls.notice_task_id]
                )
            cls.db.delete(
                table="notice_task",
                where="task_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("通知任务测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="通知任务管理",
        title="测试根据业务编码发送通知",
        description="验证API_NOTICE_CREATE_TASK_BY_SCENE_POST功能 - 根据通知业务编码发送通知",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "notice", "task", "create"]
    )
    def test_notice_create_task_by_scene_post(self):
        """测试根据业务编码发送通知 - API_NOTICE_CREATE_TASK_BY_SCENE_POST"""
        try:
            # 1. 准备测试数据
            scene_code = f"AT_NOTICE_SCENE_{self.mock_util.get_timestamp()}"
            business_code = f"AT_BUSINESS_CODE_{self.mock_util.get_timestamp()}"
            task_name = f"AT_NOTICE_TASK_{self.mock_util.get_timestamp()}"
            recipient_type = "USER"  # 假设接收者类型：USER/ROLE/DEPT等
            recipient_ids = [self.admin_user_info.get("id")] if self.admin_user_info else ["test_user_id"]  # 使用已登录用户ID或模拟
            title = f"测试通知标题_{self.mock_util.get_timestamp()}"
            content = f"测试通知内容_{self.mock_util.get_timestamp()}"
            priority = 1
            send_type = "IMMEDIATE"  # 立即发送或定时
            remark = self.mock_util.get_mock_remark()
            
            # 2. 调用API
            api_path = self.get_api_path("通知发送服务-根据通知业务编码发送通知")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sceneCode", "businessCode", "taskName", "recipientType", "recipientIds", 
                        "title", "content", "priority", "sendType", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "sceneCode": scene_code,
                "businessCode": business_code,
                "taskName": task_name,
                "recipientType": recipient_type,
                "recipientIds": recipient_ids,
                "title": title,
                "content": content,
                "priority": priority,
                "sendType": send_type,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            task_data = response.get("data", {}).get("data", {})
            self.notice_task_id = task_data.get("taskId") or task_data.get("id") if task_data else None
            self.assert_util.assert_by_operator(self.notice_task_id, "not_empty", "通知任务ID不应为空")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建通知任务ID: {self.notice_task_id}, 场景编码: {scene_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
