"""
通知场景管理测试用例
覆盖通知场景查询等功能
"""
import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("通知场景管理")
class TestNoticeSceneManagement(SysCommonBaseTest):
    """通知场景管理测试类"""
    
    # API配置
    API_KEY = "通知场景列表查询(/api/trantor/portal/meta/list/NoticeScene#GET)"
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("通知场景管理测试类初始化完成")
    
    def _build_base_params(self):
        """
        构建基础请求参数
        
        :return: 完整的请求参数字典
        """
        pageable = {
            "pageNo": 1,
            "pageSize": 20,
            "sortOrders": None
        }
        
        return {
            "params": {
                "request": {
                    "pageable": pageable,
                    "fields": [],
                    "systemParams": None
                }
            },
            "sceneKey": "sys_common$notify_scene",
            "viewKey": "sys_common$notify_scene:list",
            "serviceKey": "sys_common$API_TRANTOR_PORTAL_META_LIST_NOTICE_SCENE_GET",
        }
    
    def _validate_response(self, response, validate_func=None):
        """
        验证响应数据的通用方法
        
        :param response: API响应
        :param validate_func: 可选的额外验证函数，接收data_list作为参数
        :return: 数据列表
        """
        # 业务断言
        self.assert_util.assert_response_data(response)
        
        # 验证返回数据
        data = response.get("data", {}).get("data", {})
        self.assert_util.assert_by_operator(
            data is not None,
            "=",
            True,
            "返回数据不应为空"
        )
        
        # 验证返回的数据列表
        data_list = data.get("data", [])
        self.assert_util.assert_by_operator(
            isinstance(data_list, list),
            "=",
            True,
            "返回数据应为列表类型"
        )
        
        # 执行额外的验证逻辑
        if validate_func:
            validate_func(data_list)
        
        return data_list
    
    @case_decorator(
        story="通知场景管理",
        title="测试通知场景列表查询",
        description="验证通知场景列表查询功能 - API_TRANTOR_PORTAL_META_LIST_NOTICE_SCENE_GET",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "notice", "scene", "query_list"]
    )
    def test_notice_scene_query_list(self):
        """测试通知场景列表查询"""
        try:
            # 1. 准备测试数据
            set_dict = self._build_base_params()
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key=self.API_KEY,
                set_dict=set_dict,
                param_path=[] # 空路径，让 set_dict 直接作为顶层参数
            )
            
            # 3. 验证响应数据
            data_list = self._validate_response(response)
            
            self.logger.info(f"通知场景列表查询成功，共查询到 {len(data_list)} 条记录")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
