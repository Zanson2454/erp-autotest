import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("物料价格管理")
class TestMatPriceManagement(GenMdBaseTest):
    """物料价格管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.mat_price_id = None
        cls.mat_price_code = None
        cls.logger.info("物料价格管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料价格管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_mat_price_md",
                where="mat_price_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="物料价格管理",
        title="测试新增物料价格",
        description="验证新增物料价格功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["物料价格管理", "新增"]
    )
    def test_save_mat_price(self):
        """
        新增物料价格用例
        """
        try:
            # 准备物料价格数据
            mat_price_code = self.mock_util.generate_unique_code(tag="MatPrice")
            mat_price_name = f"物料价格_{self.mock_util.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-物料价格-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["matPriceCode", "matPriceName", "price", "currencyId", "matId"],
                ["params", "request"]
            )
            set_dict = {
                "matPriceCode": mat_price_code,
                "matPriceName": mat_price_name,
                "price": 100.00,
                "currencyId": None,  # 需要关联币种ID
                "matId": None  # 需要关联物料ID
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            mat_price_id = response.get("data", {}).get("data", {})

            # 保存物料价格信息供后续用例使用
            self.mat_price_id = mat_price_id
            self.mat_price_code = mat_price_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价格管理",
        title="测试查询物料价格列表",
        description="验证物料价格列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["物料价格管理", "查询"]
    )
    def test_query_mat_price_list(self):
        """
        查询物料价格列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-物料价格-查询分页服务")
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
                    {"name": "matPriceCode", "type": "TEXT"},
                    {"name": "matPriceName", "type": "TEXT"}
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
        story="物料价格管理",
        title="测试查询物料价格详情",
        description="验证物料价格详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["物料价格管理", "查询"]
    )
    def test_query_mat_price_detail(self):
        """
        查询物料价格详情用例
        """
        try:
            # 获取物料价格ID
            if not self.mat_price_id:
                self.test_save_mat_price()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-物料价格-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mat_price_id}
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
        story="物料价格管理",
        title="测试删除物料价格",
        description="验证删除物料价格功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["物料价格管理", "删除"]
    )
    def test_delete_mat_price(self):
        """
        删除物料价格用例
        """
        try:
            # 获取物料价格信息
            if not self.mat_price_id:
                self.test_save_mat_price()

            # 调用删除接口
            api_path = self.get_api_path("GEN-物料价格-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.mat_price_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise










