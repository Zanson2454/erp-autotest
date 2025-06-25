import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("动态表单管理")
class TestDynamic_FormManagement(GenMdBaseTest):
    """动态表单管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.dynamic_form_id = None
        cls.dynamic_form_code = None
        cls.logger.info("动态表单管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的动态表单管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_dynamic_form_md",
                where="dynamic_form_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")







    @case_decorator(
        story="动态表单管理",
        title="测试修改动态表单管理",
        description="验证修改动态表单管理功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["动态表单管理", "修改"]
    )
    def test_update_dynamic_form(self):
        """
        修改动态表单管理用例
        """
        try:
            # 获取动态表单管理信息
            if not self.dynamic_form_id:
                self.test_save_dynamic_form()

            # 调用修改接口
            api_path = self.get_api_path("GEN-创建修改动态表单模板")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "dynamic_form_code", "dynamic_form_name"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.dynamic_form_id,
                "dynamic_form_code": self.dynamic_form_code,
                "dynamic_form_name": f"修改_动态表单管理_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试删除动态表单管理",
        description="验证删除动态表单管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["动态表单管理", "删除"]
    )
    def test_delete_dynamic_form(self):
        """
        删除动态表单管理用例
        """
        try:
            # 获取动态表单管理信息
            if not self.dynamic_form_id:
                self.test_save_dynamic_form()

            # 调用删除接口
            api_path = self.get_api_path("GEN-动态表单-删除动态表单模板服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.dynamic_form_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
