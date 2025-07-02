import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("客户税分类管理")
class TestCustomerTaxManagement(GenMdBaseTest):
    """客户税分类管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("客户税分类管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.logger.info("客户税分类管理测试类清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="客户税分类管理",
        title="测试客户税分类标准导出",
        description="验证客户税分类标准导出功能",
        severity="normal",
        order=1,
        tags=["客户税分类", "导出"]
    )
    def test_export_customer_tax_type(self):
        """客户税分类标准导出用例"""
        try:
            api_path = self.get_api_path("客户税分类标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"客户税分类导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "客户税分类"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="客户税分类管理",
        title="测试客户税分类标准导入",
        description="验证客户税分类标准导入功能",
        severity="normal",
        order=2,
        tags=["客户税分类", "导入"]
    )
    def test_import_customer_tax_type(self):
        """客户税分类标准导入用例"""
        try:
            api_path = self.get_api_path("客户税分类标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"客户税分类导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="客户税分类管理",
        title="测试提交客户税分类导出任务",
        description="验证提交客户税分类导出任务功能",
        severity="normal",
        order=3,
        tags=["客户税分类", "导出任务"]
    )
    def test_submit_customer_tax_type_export_task(self):
        """提交客户税分类导出任务用例"""
        try:
            api_path = self.get_api_path("客户税分类-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"客户税分类导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"客户税分类_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="客户税分类管理",
        title="测试通过OSS提交客户税分类导入任务",
        description="验证通过OSS提交客户税分类导入任务功能",
        severity="normal",
        order=4,
        tags=["客户税分类", "OSS导入"]
    )
    def test_submit_customer_tax_type_import_task_by_oss(self):
        """通过OSS提交客户税分类导入任务用例"""
        try:
            api_path = self.get_api_path("客户税分类-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"客户税分类OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"customer_tax_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "客户税分类"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 