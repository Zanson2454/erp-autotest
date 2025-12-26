"""
通知记录管理测试用例
覆盖通知记录查询等功能
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("通知记录管理")
class TestNoticeRecordManagement(SysCommonBaseTest):
    """通知记录管理测试类"""
    
    # API配置
    API_KEY = "通知记录APP服务-分页查询记录(Trantor入参)(/api/notice/record/pagingByTrantor#POST)"
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("通知记录管理测试类初始化完成")
    
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
                        {"name": "receiverIdentity", "type": "TEXT"},
                        {"name": "sendTime", "type": "DATE"},
                        {"name": "recordStatus", "type": "SELECT"},
                        {"name": "templateId", "type": "OBJECT"},
                        {"name": "channelId", "type": "OBJECT"}
                    ],
                    "systemParams": None
                }
            },
            "sceneKey": "sys_common$notify_record",
            "viewKey": "sys_common$notify_record:list",
            "appId": 0,
            "teamId": 22,
            "serviceKey": "sys_common$API_NOTICE_RECORD_PAGING_BY_TRANTOR_POST",
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
        story="通知记录管理",
        title="测试通知记录分页查询",
        description="验证通知记录分页查询功能 - API_NOTICE_RECORD_PAGING_BY_TRANTOR_POST",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "notice", "record", "query_list"]
    )
    def test_notice_record_query_list(self):
        """测试通知记录分页查询"""
        try:
            # 1. 准备测试数据
            set_dict = self._build_base_params(condition_items=None)
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key=self.API_KEY,
                set_dict=set_dict,
                param_path=[] # 空路径，让 set_dict 直接作为顶层参数
            )
            
            # 3. 验证响应数据
            data_list = self._validate_response(response)
            
            self.logger.info(f"通知记录分页查询成功，共查询到 {len(data_list)} 条记录")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

