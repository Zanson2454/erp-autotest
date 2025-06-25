import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("员工管理")
class TestEmployeeManagement(GenMdBaseTest):
    """员工管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.employee_id = None
        cls.employee_code = None
        cls.logger.info("员工管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的员工管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_employee_md",
                where="employee_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="员工管理",
        title="测试新增员工管理",
        description="验证新增员工管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["员工管理", "新增"]
    )
    def test_save_employee(self):
        """
        新增员工管理用例
        """
        try:
            # 准备员工管理数据
            employee_code = self.mock_data.generate_unique_code(tag="Employee")
            employee_name = f"员工管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-员工-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["employee_code", "employee_name"],
                ["params", "request"]
            )
            set_dict = {
                "employee_code": employee_code,
                "employee_name": employee_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            employee_id = response.get("data", {}).get("data", {})

            # 保存员工管理信息供后续用例使用
            self.employee_id = employee_id
            self.employee_code = employee_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise







    @case_decorator(
        story="员工管理",
        title="测试删除员工管理",
        description="验证删除员工管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["员工管理", "删除"]
    )
    def test_delete_employee(self):
        """
        删除员工管理用例
        """
        try:
            # 获取员工管理信息
            if not self.employee_id:
                self.test_save_employee()

            # 调用删除接口
            api_path = self.get_api_path("ORG-组织-删除员工组织关联关系服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.employee_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
