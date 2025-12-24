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
        title="测试分页查询站内信",
        description="验证API_NOTICE_STATION_PAGING_POST功能 - 分页查询站内信",
        severity="normal",
        file_level_order=1,
        tags=["sys_common", "notice", "station", "paging"]
    )
    def test_notice_station_paging_post(self):
        """测试分页查询站内信 - API_NOTICE_STATION_PAGING_POST"""
        try:
            # 1. 准备测试数据
            # 根据 curl 请求，参数结构为: {"params":{"readStatus":"UNREAD","pageSize":10,"pageNo":1}}
            set_dict = {
                "readStatus": "UNREAD",
                "pageSize": 10,
                "pageNo": 1
            }
            
            # 2. 使用标准化API调用
            # 根据 curl 请求，参数直接放在 params 层级下，不使用默认的 params.request
            response, _ = self.standard_api_call(
                api_key="站内信APP服务-分页查询站内信(/api/notice/station/paging#POST)",
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
            
            self.logger.info(f"分页查询站内信成功: {data}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise