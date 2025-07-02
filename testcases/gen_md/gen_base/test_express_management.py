import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("快递公司管理")
class TestExpressManagement(GenMdBaseTest):
    """快递公司管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.express_id = None
        cls.express_code = None
        cls.logger.info("快递公司管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的快递公司管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_express_md",
                where="express_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="快递公司管理",
        title="测试新增快递公司管理",
        description="验证新增快递公司管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["快递公司管理", "新增"]
    )
    def test_save_express(self):
        """
        新增快递公司管理用例
        """
        try:
            # 准备快递公司管理数据
            express_code = self.mock_data.generate_unique_code(tag="Express")
            express_name = f"快递公司管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-快递公司-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["express_code", "express_name"],
                ["params", "request"]
            )
            set_dict = {
                "express_code": express_code,
                "express_name": express_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            express_id = response.get("data", {}).get("data", {})

            # 保存快递公司管理信息供后续用例使用
            self.express_id = express_id
            self.express_code = express_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试查询快递公司管理列表",
        description="验证快递公司管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["快递公司管理", "查询"]
    )
    def test_query_express_list(self):
        """
        查询快递公司管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-快递公司-查询分页服务")
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
                    {"name": "express_code", "type": "TEXT"},
                    {"name": "express_name", "type": "TEXT"}
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
        story="快递公司管理",
        title="测试查询快递公司管理详情",
        description="验证快递公司管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["快递公司管理", "查询"]
    )
    def test_query_express_detail(self):
        """
        查询快递公司管理详情用例
        """
        try:
            # 获取快递公司管理ID
            if not self.express_id:
                self.test_save_express()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-快递公司-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.express_id}
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
        story="快递公司管理",
        title="测试删除快递公司管理",
        description="验证删除快递公司管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["快递公司管理", "删除"]
    )
    def test_delete_express(self):
        """
        删除快递公司管理用例
        """
        try:
            # 获取快递公司管理信息
            if not self.express_id:
                self.test_save_express()

            # 调用删除接口
            api_path = self.get_api_path("GEN-快递公司-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.express_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
