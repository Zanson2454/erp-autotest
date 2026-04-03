"""
通知渠道管理测试用例
覆盖通知渠道查询等功能
"""
import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("通知渠道管理")
class TestNoticeChannelManagement(SysCommonBaseTest):
    """通知渠道管理测试类"""
    
    # API配置
    API_KEY = "通知渠道-查询渠道列表(Trantor入参)(/api/notice/channel/queryListByTrantor#POST)"
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("通知渠道管理测试类初始化完成")
    
    def _build_base_params(self, condition_items=None):
        """
        构建基础请求参数
        
        :param condition_items: 查询条件，如果为None则不设置条件
        :return: 完整的请求参数字典
        """
        pageable = {
            "pageNo": 1,
            "pageSize": 20,
            "needTotal": True,
            "sortOrders": None,
            "conditionItems": condition_items
        }
        
        return {
            "params": {
                "request": {
                    "pageable": pageable,
                    "fields": [
                        {"name": "channelName", "type": "TEXT"},
                        {"name": "channelType", "type": "SELECT"}
                    ],
                    "systemParams": None
                }
            },
            "sceneKey": "sys_common$notify_channel",
            "viewKey": "sys_common$notify_channel:list",
            "serviceKey": "sys_common$API_NOTICE_CHANNEL_QUERY_LIST_BY_TRANTOR_POST",
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
    
    @pytest.mark.parametrize("test_scenario", [
        {
            "title": "测试通知渠道列表查询",
            "description": "验证通知渠道列表查询功能 - API_NOTICE_CHANNEL_QUERY_LIST_BY_TRANTOR_POST",
            "file_level_order": 1,
            "tags": ["sys_common", "notice", "channel", "query_list"],
            "condition_items": None,
            "validate_func": None
        },
        {
            "title": "测试通知渠道列表查询-按渠道类型查询",
            "description": "验证通知渠道列表查询功能 - 按渠道类型查询（STATION_NOTICE、SMS）",
            "file_level_order": 2,
            "tags": ["sys_common", "notice", "channel", "query_list", "type"],
            "condition_items": {
                "type": "ConditionItems",
                "conditions": {
                    "channelType": {
                        "operator": "IN",
                        "value": ["STATION_NOTICE", "SMS"]
                    }
                },
                "logicOperator": "AND"
            },
            "validate_func": "validate_types"
        },
        {
            "title": "测试通知渠道列表查询-按渠道名称查询",
            "description": "验证通知渠道列表查询功能 - 按渠道名称搜索（包含关键词）",
            "file_level_order": 3,
            "tags": ["sys_common", "notice", "channel", "query_list", "name"],
            "condition_items": {
                "type": "ConditionItems",
                "conditions": {
                    "channelName": {
                        "operator": "CONTAINS",
                        "value": "站内信"
                    }
                },
                "logicOperator": "AND"
            },
            "validate_func": "validate_names"
        }
    ])
    @case_decorator(
        story="通知渠道管理",
        title="测试通知渠道列表查询",
        description="验证通知渠道列表查询功能",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "notice", "channel", "query_list"]
    )
    def test_notice_channel_query_list(self, test_scenario):
        """测试通知渠道列表查询 - 参数化测试"""
        try:
            # 动态设置测试标题
            allure.dynamic.title(test_scenario["title"])
            allure.dynamic.description(test_scenario["description"])
            
            # 1. 准备测试数据
            set_dict = self._build_base_params(condition_items=test_scenario["condition_items"])
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key=self.API_KEY,
                set_dict=set_dict,
                param_path=[] # 空路径，让 set_dict 直接作为顶层参数
            )
            
            # 3. 定义验证函数
            validate_func = None
            if test_scenario["validate_func"] == "validate_types":
                allowed_types = ["STATION_NOTICE", "SMS"]
                def validate_types(data_list):
                    """验证搜索结果：所有返回的渠道类型应在指定的类型列表中"""
                    if data_list:
                        for item in data_list:
                            channel_type = item.get("channelType", "")
                            self.assert_util.assert_by_operator(
                                channel_type in allowed_types,
                                "=",
                                True,
                                f"搜索结果渠道类型应为 {allowed_types} 之一，实际渠道类型: {channel_type}"
                            )
                validate_func = validate_types
            elif test_scenario["validate_func"] == "validate_names":
                search_keyword = "站内信"
                def validate_names(data_list):
                    """验证搜索结果：所有返回的渠道名称应包含搜索关键词"""
                    if data_list:
                        for item in data_list:
                            channel_name = item.get("channelName", "")
                            self.assert_util.assert_by_operator(
                                search_keyword in channel_name,
                                "=",
                                True,
                                f"搜索结果应包含关键词 '{search_keyword}'，实际渠道名称: {channel_name}"
                            )
                validate_func = validate_names
            
            # 4. 验证响应数据
            data_list = self._validate_response(response, validate_func=validate_func)
            
            # 5. 记录日志
            if test_scenario["validate_func"] == "validate_types":
                self.logger.info(f"按渠道类型查询通知渠道成功，类型: {['STATION_NOTICE', 'SMS']}，共查询到 {len(data_list)} 条记录")
            elif test_scenario["validate_func"] == "validate_names":
                self.logger.info(f"按渠道名称查询通知渠道成功，关键词: '站内信'，共查询到 {len(data_list)} 条记录")
            else:
                self.logger.info(f"通知渠道列表查询成功，共查询到 {len(data_list)} 条记录")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
