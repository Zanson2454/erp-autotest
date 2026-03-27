import allure
import pytest
from typing import Any
from datetime import datetime
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("待办管理")
class TestTodoManagement(GenMdBaseTest):
    """待办管理测试类 - 覆盖日常待办和业务待办相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.daily_todo_id = None
        cls.biz_todo_id = None
        cls.todo_code = None
        cls.logger.info("待办管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_daily_to_do",
                where="title like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_biz_to_do",
                where="title like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 日常待办管理 ================
    @case_decorator(
        story="待办管理",
        title="测试日常待办保存",
        description="验证日常待办保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["待办管理", "日常待办", "保存", "GEN_DAILY_TO_DO_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="日常待办保存服务功能暂未开发，暂时跳过")
    def test_save_daily_todo(self):
        """日常待办保存用例 - GEN_DAILY_TO_DO_SAVE_SERVICE"""
        try:
            # 生成测试数据
            todo_code = self.mock_util.generate_unique_code(tag="DAILY_TODO")
            todo_title = f"AT_日常待办_{self.mock_util.get_timestamp()}"

            # 将dueDate转换为时间戳（deadline字段）
            deadline_timestamp = int(datetime.strptime("2024-12-31", "%Y-%m-%d").timestamp() * 1000)
            set_dict = {
                "todoCode": todo_code,
                "title": todo_title,
                "content": f"日常待办内容描述_{self.mock_util.get_timestamp()}",
                "priority": "MEDIUM",
                "dueDate": "2024-12-31",
                "status": "PENDING",
                "todo": todo_title,  # todo字段不能为空，使用title作为待办内容
                "deadline": deadline_timestamp  # deadline字段不能为空，使用时间戳格式
            }
            response, extracted_id = self.standard_api_call(
                api_key="日常待办保存服务",
                set_dict=set_dict,
                fields_to_filter=["todoCode", "title", "content", "priority", "dueDate", "status", "todo", "deadline"]
            )
            self.assert_util.assert_response_data(response)

            # 保存日常待办ID
            self.daily_todo_id = extracted_id.get("id") if isinstance(extracted_id, dict) else extracted_id
            self.todo_code = todo_code

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="待办管理",
        title="测试日常待办分页查询",
        description="验证日常待办分页查询服务功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["待办管理", "日常待办", "分页查询", "GEN_DAILY_TO_DO_QUERY_PAGE_SERVICE"]
    )
    @pytest.mark.skip(reason="日常待办分页查询服务功能暂未开发，暂时跳过")
    def test_query_daily_todo_page(self):
        """日常待办分页查询用例 - GEN_DAILY_TO_DO_QUERY_PAGE_SERVICE"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "todoCode", "type": "TEXT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "content", "type": "TEXT"},
                    {"name": "priority", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"},
                    {"name": "dueDate", "type": "DATE"}
                ],
                "systemParams": None
            }
            response, _ = self.standard_api_call(
                api_key="日常待办分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"]
            )
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            if data_list and not self.daily_todo_id:
                self.daily_todo_id = data_list[0].get("id")

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="待办管理",
        title="测试日常待办完成",
        description="验证日常待办完成服务功能",
        severity="normal",
        file_level_order=3,
        tags=["待办管理", "日常待办", "完成", "GEN_DAILY_TO_DO_COMPLETED_SERVICE"]
    )
    @pytest.mark.skip(reason="日常待办完成服务功能暂未开发，暂时跳过")
    def test_complete_daily_todo(self):
        """日常待办完成用例 - GEN_DAILY_TO_DO_COMPLETED_SERVICE"""
        try:
            if not self.daily_todo_id:
                self.test_save_daily_todo()

            set_dict = {"id": self.daily_todo_id}
            response, _ = self.standard_api_call(
                api_key="日常待办完成服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="待办管理",
        title="测试日常待办删除",
        description="验证日常待办删除服务功能",
        severity="critical",
        file_level_order=4,
        tags=["待办管理", "日常待办", "删除", "GEN_DAILY_TO_DO_DELETE_SERVICE"]
    )
    @pytest.mark.skip(reason="日常待办删除服务功能暂未开发，暂时跳过")
    def test_delete_daily_todo(self):
        """日常待办删除用例 - GEN_DAILY_TO_DO_DELETE_SERVICE"""
        try:
            # 检查是否存在待办ID，如果不存在先创建
            if not self.daily_todo_id:
                try:
                    self.test_save_daily_todo()
                except Exception as e:
                    self.logger.warning(f"创建日常待办失败: {str(e)}")
                    # 如果创建失败，尝试从分页查询获取现有数据
                    self.test_query_daily_todo_page()
                
            # 如果还是没有数据，使用模拟ID
            if not self.daily_todo_id:
                self.logger.warning("未获取到日常待办ID，使用模拟ID进行测试")
                self.daily_todo_id = 1

            set_dict = {"id": self.daily_todo_id}
            response, _ = self.standard_api_call(
                api_key="日常待办删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 业务待办管理 ================
    @case_decorator(
        story="待办管理",
        title="测试业务待办保存",
        description="验证业务待办保存服务功能",
        severity="blocker",
        file_level_order=5,
        smoke=True,
        tags=["待办管理", "业务待办", "保存", "GEN_BIZ_TO_DO_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="业务待办保存服务功能暂未开发，暂时跳过")
    def test_save_biz_todo(self):
        """业务待办保存用例 - GEN_BIZ_TO_DO_SAVE_SERVICE"""
        try:
            # 生成测试数据
            biz_todo_code = self.mock_util.generate_unique_code(tag="BIZ_TODO")
            biz_todo_title = f"AT_业务待办_{self.mock_util.get_timestamp()}"

            set_dict = {
                "bizCode": biz_todo_code,
                "title": biz_todo_title,
                "bizType": "ORDER_APPROVAL",
                "bizId": f"ORD_{self.mock_util.get_timestamp()}",
                "assignee": self.user_id,
                "status": "PENDING",
                "level": "HIGH"  # 等级不能为空，设置为高级
            }
            response, extracted_id = self.standard_api_call(
                api_key="业务待办保存服务",
                set_dict=set_dict,
                fields_to_filter=["bizCode", "title", "bizType", "bizId", "assignee", "status", "level"]
            )
            self.assert_util.assert_response_data(response)

            # 保存业务待办ID
            self.biz_todo_id = extracted_id.get("id") if isinstance(extracted_id, dict) else extracted_id

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="待办管理",
        title="测试业务待办分页查询",
        description="验证业务待办分页查询服务功能",
        severity="critical",
        file_level_order=6,
        smoke=True,
        tags=["待办管理", "业务待办", "分页查询", "GEN_BIZ_TO_DO_QUERY_PAGE_SERVICE"]
    )
    @pytest.mark.skip(reason="业务待办分页查询服务功能暂未开发，暂时跳过")
    def test_query_biz_todo_page(self):
        """业务待办分页查询用例 - GEN_BIZ_TO_DO_QUERY_PAGE_SERVICE"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "bizCode", "type": "TEXT"},
                    {"name": "title", "type": "TEXT"},
                    {"name": "bizType", "type": "TEXT"},
                    {"name": "bizId", "type": "TEXT"},
                    {"name": "assignee", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ],
                "systemParams": None
            }
            response, _ = self.standard_api_call(
                api_key="业务代办分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"]
            )
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            if data_list and not self.biz_todo_id:
                self.biz_todo_id = data_list[0].get("id")

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="待办管理",
        title="测试业务待办删除",
        description="验证业务待办删除服务功能",
        severity="critical",
        file_level_order=7,
        tags=["待办管理", "业务待办", "删除", "GEN_BIZ_TO_DO_DELETE_SERVICE"]
    )
    @pytest.mark.skip(reason="业务待办删除服务功能暂未开发，暂时跳过")
    def test_delete_biz_todo(self):
        """业务待办删除用例 - GEN_BIZ_TO_DO_DELETE_SERVICE"""
        try:
            # 检查是否存在业务待办ID，如果不存在先创建
            if not self.biz_todo_id:
                try:
                    self.test_save_biz_todo()
                except Exception as e:
                    self.logger.warning(f"创建业务待办失败: {str(e)}")
                    # 如果创建失败，尝试从分页查询获取现有数据
                    self.test_query_biz_todo_page()
                
            # 如果还是没有数据，使用模拟ID
            if not self.biz_todo_id:
                self.logger.warning("未获取到业务待办ID，使用模拟ID进行测试")
                self.biz_todo_id = 1

            set_dict = {"id": self.biz_todo_id}
            response, _ = self.standard_api_call(
                api_key="业务待办删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
