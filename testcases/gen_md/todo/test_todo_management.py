from typing import Any

import allure

from testcases.gen_md import GenMdBaseTest


@allure.epic("通用基础数据")
@allure.feature("待办管理")
class TestTodoManagement(GenMdBaseTest):
    """待办管理测试类 - 覆盖日常待办和业务待办相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 数据存储
        cls.daily_todo_id = None
        cls.biz_todo_id = None
        cls.todo_code = None
        cls.logger.info("待办管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    # ================ 日常待办管理 ================




    # ================ 业务待办管理 ================


