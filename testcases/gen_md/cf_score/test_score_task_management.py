import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("评分任务管理")
class TestScore_TaskManagement(GenMdBaseTest):
    """评分任务管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.score_task_id = None
        cls.score_task_code = None
        cls.logger.info("评分任务管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的评分任务管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_score_task_md",
                where="score_task_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")










