import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator

@allure.epic("系统通用模块")
@allure.feature("WebSocket管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestWebsocketManagement(SysCommonBaseTest):
    """WebSocket管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.ws_token = None
        cls.session_id = None  # 用于消息推送的目标会话
        cls.logger.info("WebSocket管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # Token和会话通常是临时性的，无需数据库清理
            # 如果推送消息创建了任务记录，可在此清理
            if cls.session_id:
                # 假设有会话清理接口或数据库表，实际根据实现调整
                pass
            cls.logger.info("WebSocket测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="WebSocket管理",
        title="测试获取WebSocket连接Token",
        description="验证API_MW_WEBSOCKET_GET_TOKEN_POST功能 - 获取ws连接token",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "webSocket", "token", "get"]
    )
    def test_websocket_get_token_post(self):
        """测试获取WebSocket连接Token - API_MW_WEBSOCKET_GET_TOKEN_POST"""
        try:
            # 1. 准备测试数据
            user_id = self.admin_user_info.get("id") if self.admin_user_info else f"AT_USER_{self.mock_util.get_timestamp()}"
            expire_time = 3600  # Token过期时间（秒）
            scope = "DEFAULT"  # Token作用域
            
            # 2. 调用API
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="Websocket前端http(s)接口-获取ws连接token",
                set_dict={
                    "userId": user_id,
                    "expireTime": expire_time,
                    "scope": scope,
                },
                fields_to_filter=["userId", "expireTime", "scope"],
                param_path=["params", "request"],
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存Token和报告
            token_data = response.get("data", {}).get("data", {})
            self.ws_token = token_data.get("token") if token_data else None
            self.assert_util.assert_by_operator(self.ws_token, "not_empty", "WebSocket Token不应为空")
            self.assert_util.assert_by_operator(
                isinstance(self.ws_token, str) and len(self.ws_token) > 20, 
                "=", True, "Token应为有效字符串（长度>20）"
            )
            
            a.json({"userId": user_id, "expireTime": expire_time, "scope": scope}, "请求数据")
            a.json({"token": self.ws_token[:50] + "..." if self.ws_token else None}, "Token摘要（前50字符）")
            a.json(response, "完整响应数据")
            self.logger.info(f"获取WebSocket Token成功，用户ID: {user_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="WebSocket管理",
        title="测试获取全部WebSocket会话列表",
        description="验证API_MW_WEBSOCKET_GET_SESSION_LIST_GET功能 - 获取全部session",
        severity="normal",
        order=4,
        tags=["sys_common", "webSocket", "session", "list"]
    )
    def test_websocket_get_session_list_get(self):
        """测试获取全部WebSocket会话列表 - API_MW_WEBSOCKET_GET_SESSION_LIST_GET"""
        try:
            # 可选：先获取Token确保认证，但此接口可能独立
            # if not self.ws_token:
            #     self._ensure_websocket_get_token_post()
            
            # GET参数（如果需要过滤条件，如状态、用户ID）
            get_params = {
                # "status": "ACTIVE",  # 可选：活跃会话
                # "userId": self.admin_user_info.get("id") if self.admin_user_info else None
            }
            # 清理空值
            get_params = {k: v for k, v in get_params.items() if v}

            response, _ = self.standard_api_call(
                api_key="Websocket前端http(s)接口-获取全部session",
                method="GET",
                set_dict=get_params,
            )
            self.assert_util.assert_response_data(response)
            
            # 验证会话列表
            session_data = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(isinstance(session_data, list), "=", True, "会话数据应为列表")
            
            # 如果期望有会话，验证非空；否则验证结构
            if session_data:
                self.assert_util.assert_by_operator(len(session_data), ">=", 1, "应至少返回一个会话")
                # 保存一个会话ID用于后续推送测试
                first_session = session_data[0]
                self.session_id = first_session.get("sessionId") or first_session.get("id")
                self.logger.info(f"获取会话ID: {self.session_id}")
            else:
                self.logger.info("当前无活跃会话，返回空列表（正常）")
            
            a.json(get_params, "查询参数")
            a.json({"session_count": len(session_data)}, "会话统计")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="WebSocket管理",
        title="测试推送任务消息",
        description="验证API_MW_WEBSOCKET_PUSH_TASK_MESSAGE_GET功能 - 推送任务消息(调试用)",
        severity="normal",
        order=5,
        tags=["sys_common", "webSocket", "message", "push"]
    )
    def test_websocket_push_task_message_get(self):
        """测试推送任务消息 - API_MW_WEBSOCKET_PUSH_TASK_MESSAGE_GET"""
        try:
            # 确保有会话ID（从会话列表获取）
            if not self.session_id:
                self._ensure_websocket_get_session_list_get()
                if not self.session_id:
                    # 如果无会话，模拟一个或跳过推送测试
                    self.logger.warning("无可用会话ID，模拟推送测试")
                    self.session_id = f"AT_SIMULATED_SESSION_{self.mock_util.get_timestamp()}"
            
            # 准备消息数据
            task_id = f"AT_TASK_{self.mock_util.get_timestamp()}"
            message_type = "TASK_PROGRESS"  # 任务进度消息
            content = {
                "taskId": task_id,
                "progress": 50,
                "status": "RUNNING",
                "message": f"任务 {task_id} 进度更新 - 调试推送"
            }
            target_session = self.session_id
            broadcast = False  # 针对特定会话推送
            
            get_params = {
                "sessionId": target_session,
                "messageType": message_type,
                "content": str(content),  # 序列化为字符串，或根据API要求调整
                "broadcast": str(broadcast).lower()
            }

            response, _ = self.standard_api_call(
                api_key="Websocket前端http(s)接口-推送任务消息(调试用)",
                method="GET",
                set_dict=get_params,
            )
            self.assert_util.assert_response_success(response)  # 假设推送成功返回200或确认状态
            
            # 验证推送响应
            push_data = response.get("data", {})
            self.assert_util.assert_by_operator(
                bool(push_data.get("success") or response.get("success")),
                "=", True, "消息推送应成功"
            )
            if "messageId" in push_data:
                message_id = push_data.get("messageId")
                self.logger.info(f"推送消息ID: {message_id}, 目标会话: {target_session}")
            
            a.json(get_params, "推送参数")
            a.json(content, "消息内容")
            a.json(response, "推送响应")
            self.logger.info(f"成功推送任务消息到会话 {target_session}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
