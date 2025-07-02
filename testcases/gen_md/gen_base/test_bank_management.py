import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("银行管理")
class TestBankManagement(GenMdBaseTest):
    """银行管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.bank_id = None
        cls.bank_code = None
        cls.logger.info("银行管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的银行管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_bank_md",
                where="bank_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="银行管理",
        title="测试新增银行管理",
        description="验证新增银行管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["银行管理", "新增"]
    )
    def test_save_bank(self):
        """
        新增银行管理用例
        """
        try:
            # 准备银行管理数据
            bank_code = self.mock_data.generate_unique_code(tag="Bank")
            bank_name = f"银行管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-银行配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bank_code", "bank_name"],
                ["params", "request"]
            )
            set_dict = {
                "bank_code": bank_code,
                "bank_name": bank_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            bank_id = response.get("data", {}).get("data", {})

            # 保存银行管理信息供后续用例使用
            self.bank_id = bank_id
            self.bank_code = bank_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试查询银行管理列表",
        description="验证银行管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_list(self):
        """
        查询银行管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("银行支行-分页数据服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "bank_code", "type": "TEXT"},
                    {"name": "bank_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试查询银行管理详情",
        description="验证银行管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_detail(self):
        """
        查询银行管理详情用例
        """
        try:
            # 获取银行管理ID
            if not self.bank_id:
                self.test_save_bank()

            # 调用详情查询接口
            api_path = self.get_api_path("银行配置-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bank_id}
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
        story="银行管理",
        title="测试删除银行管理",
        description="验证删除银行管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["银行管理", "删除"]
    )
    def test_delete_bank(self):
        """
        删除银行管理用例
        """
        try:
            # 获取银行管理信息
            if not self.bank_id:
                self.test_save_bank()

            # 调用删除接口
            api_path = self.get_api_path("GEN-银行配置-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bank_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
