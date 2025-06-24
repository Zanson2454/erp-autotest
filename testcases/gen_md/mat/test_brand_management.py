import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("品牌管理")
class TestBrandManagement(GenMdBaseTest):
    """品牌管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.brandId = None
        cls.brandCode = None
        cls.logger.info("品牌管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的品牌数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_brand_md",
                where="brand_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="品牌管理",
        title="测试新增品牌",
        description="验证新增品牌功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["品牌管理", "新增"]
    )
    def test_save_brand(self):
        """
        新增品牌用例
        """
        try:
            # 准备品牌数据
            brand_code = self.mock_data.generate_unique_code(tag="Brand")
            brand_name = f"品牌_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-品牌-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["brandCode", "brandName", "brandImage"],
                ["params", "request"]
            )
            set_dict = {
                "brandCode": brand_code,
                "brandName": brand_name,
                "brandImage": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            brand_id = response.get("data", {}).get("data", {})

            # 保存品牌信息供后续用例使用
            self.brandId = brand_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌列表",
        description="验证品牌列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["品牌管理", "查询"]
    )
    def test_query_brand_list(self):
        """
        查询品牌列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-品牌-查询分页服务")
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
                    {"name": "brandCode", "type": "TEXT"},
                    {"name": "brandName", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_not_empty(data_list, "品牌列表为空")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌详情",
        description="验证品牌详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["品牌管理", "查询"]
    )
    def test_query_brand_detail(self):
        """
        查询品牌详情用例
        """
        try:
            # 获取品牌ID
            if not self.brandId:
                self.test_save_brand()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-品牌-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.brandId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的品牌信息
            brand_detail = response.get("data", {}).get("data", {})
            self.brandCode = brand_detail.get("brandCode")
            self.assert_util.assert_eq(
                brand_detail.get("id"),
                self.brandId,
                "品牌编码不匹配"
            )

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试修改品牌",
        description="验证修改品牌功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["品牌管理", "修改"]
    )
    def test_update_brand(self):
        """
        修改品牌用例
        """
        try:
            # 获取品牌信息
            if not self.brandId:
                self.test_save_brand()

            # 调用修改接口
            api_path = self.get_api_path("GEN-品牌-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "brandCode", "brandName", "brandImage"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.brandId,
                "brandCode": self.brandCode,
                "brandName": f"品牌_{self.mock_data.get_timestamp()}_修改",
                "brandImage": None
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
        story="品牌管理",
        title="测试删除品牌",
        description="验证删除品牌功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["品牌管理", "删除"]
    )
    def test_delete_brand(self):
        """
        删除品牌用例
        """
        try:
            # 获取品牌ID
            if not self.brandId:
                self.test_save_brand()

            # 调用删除接口
            api_path = self.get_api_path("GEN-品牌-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.brandId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 清除品牌信息
            TestBrandManagement.brand_info = {}

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
