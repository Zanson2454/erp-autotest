import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("汇率管理")
class TestExchange_RateManagement(GenMdBaseTest):
    """汇率管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.exchange_rate_id = None
        cls.exchange_rate_code = None
        cls.logger.info("汇率管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的汇率管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_exchange_rate_md",
                where="exchange_rate_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="汇率管理",
        title="测试新增汇率管理",
        description="验证新增汇率管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["汇率管理", "新增"]
    )
    def test_save_exchange_rate(self):
        """
        新增汇率管理用例
        """
        try:
            # 准备汇率管理数据
            exchange_rate_code = self.mock_data.generate_unique_code(tag="Exchange_Rate")
            exchange_rate_name = f"汇率管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-汇率-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exchange_rate_code", "exchange_rate_name"],
                ["params", "request"]
            )
            set_dict = {
                "exchange_rate_code": exchange_rate_code,
                "exchange_rate_name": exchange_rate_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            exchange_rate_id = response.get("data", {}).get("data", {})

            # 保存汇率管理信息供后续用例使用
            self.exchange_rate_id = exchange_rate_id
            self.exchange_rate_code = exchange_rate_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试查询汇率管理列表",
        description="验证汇率管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["汇率管理", "查询"]
    )
    def test_query_exchange_rate_list(self):
        """
        查询汇率管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("汇率类型-分页数据服务")
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
                    {"name": "exchange_rate_code", "type": "TEXT"},
                    {"name": "exchange_rate_name", "type": "TEXT"}
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
        story="汇率管理",
        title="测试查询汇率管理详情",
        description="验证汇率管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["汇率管理", "查询"]
    )
    def test_query_exchange_rate_detail(self):
        """
        查询汇率管理详情用例
        """
        try:
            # 获取汇率管理ID
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-汇率-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.exchange_rate_id}
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
        story="汇率管理",
        title="测试删除汇率管理",
        description="验证删除汇率管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["汇率管理", "删除"]
    )
    def test_delete_exchange_rate(self):
        """
        删除汇率管理用例
        """
        try:
            # 获取汇率管理信息
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            # 调用删除接口
            api_path = self.get_api_path("GEN-汇率类型-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.exchange_rate_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
