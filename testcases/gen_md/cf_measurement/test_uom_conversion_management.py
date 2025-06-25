import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("计量单位换算管理")
class TestUom_ConversionManagement(GenMdBaseTest):
    """计量单位换算管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.uom_conversion_id = None
        cls.uom_conversion_code = None
        cls.logger.info("计量单位换算管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的计量单位换算管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_uom_conversion_md",
                where="uom_conversion_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="计量单位换算管理",
        title="测试新增计量单位换算管理",
        description="验证新增计量单位换算管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["计量单位换算管理", "新增"]
    )
    def test_save_uom_conversion(self):
        """
        新增计量单位换算管理用例
        """
        try:
            # 准备计量单位换算管理数据
            uom_conversion_code = self.mock_data.generate_unique_code(tag="Uom_Conversion")
            uom_conversion_name = f"计量单位换算管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-计量单位转换-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["uom_conversion_code", "uom_conversion_name"],
                ["params", "request"]
            )
            set_dict = {
                "uom_conversion_code": uom_conversion_code,
                "uom_conversion_name": uom_conversion_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            uom_conversion_id = response.get("data", {}).get("data", {})

            # 保存计量单位换算管理信息供后续用例使用
            self.uom_conversion_id = uom_conversion_id
            self.uom_conversion_code = uom_conversion_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位换算管理",
        title="测试查询计量单位换算管理列表",
        description="验证计量单位换算管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["计量单位换算管理", "查询"]
    )
    def test_query_uom_conversion_list(self):
        """
        查询计量单位换算管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-计量单位转换-查询分页服务")
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
                    {"name": "uom_conversion_code", "type": "TEXT"},
                    {"name": "uom_conversion_name", "type": "TEXT"}
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
        story="计量单位换算管理",
        title="测试查询计量单位换算管理详情",
        description="验证计量单位换算管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["计量单位换算管理", "查询"]
    )
    def test_query_uom_conversion_detail(self):
        """
        查询计量单位换算管理详情用例
        """
        try:
            # 获取计量单位换算管理ID
            if not self.uom_conversion_id:
                self.test_save_uom_conversion()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-计量单位转换-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.uom_conversion_id}
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
        story="计量单位换算管理",
        title="测试删除计量单位换算管理",
        description="验证删除计量单位换算管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["计量单位换算管理", "删除"]
    )
    def test_delete_uom_conversion(self):
        """
        删除计量单位换算管理用例
        """
        try:
            # 获取计量单位换算管理信息
            if not self.uom_conversion_id:
                self.test_save_uom_conversion()

            # 调用删除接口
            api_path = self.get_api_path("GEN-计量单位转换-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.uom_conversion_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
