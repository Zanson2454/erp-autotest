import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("取号规则管理")
class TestNumber_RuleManagement(GenMdBaseTest):
    """取号规则管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.number_rule_id = None
        cls.number_rule_code = None
        cls.logger.info("取号规则管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的取号规则管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_number_rule_md",
                where="number_rule_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")





    @case_decorator(
        story="取号规则管理",
        title="测试查询取号规则管理详情",
        description="验证取号规则管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["取号规则管理", "查询"]
    )
    def test_query_number_rule_detail(self):
        """
        查询取号规则管理详情用例
        """
        try:
            # 获取取号规则管理ID
            if not self.number_rule_id:
                self.test_save_number_rule()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-编码规则-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.number_rule_id}
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
        story="取号规则管理",
        title="测试修改取号规则管理",
        description="验证修改取号规则管理功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["取号规则管理", "修改"]
    )
    def test_update_number_rule(self):
        """
        修改取号规则管理用例
        """
        try:
            # 获取取号规则管理信息
            if not self.number_rule_id:
                self.test_save_number_rule()

            # 调用修改接口
            api_path = self.get_api_path("GEN-编码规则-编辑规则服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "number_rule_code", "number_rule_name"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.number_rule_id,
                "number_rule_code": self.number_rule_code,
                "number_rule_name": f"修改_取号规则管理_{self.mock_data.get_timestamp()}"
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


