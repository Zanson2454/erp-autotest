import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("导入导出管理")
class TestImport_ExportManagement(GenMdBaseTest):
    """导入导出管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.import_export_id = None
        cls.import_export_code = None
        cls.logger.info("导入导出管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的导入导出管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_import_export_md",
                where="import_export_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="导入导出管理",
        title="测试新增导入导出管理",
        description="验证新增导入导出管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["导入导出管理", "新增"]
    )
    def test_save_import_export(self):
        """
        新增导入导出管理用例
        """
        try:
            # 准备导入导出管理数据
            import_export_code = self.mock_data.generate_unique_code(tag="Import_Export")
            import_export_name = f"导入导出管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-组织架构-组织新增导入服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["import_export_code", "import_export_name"],
                ["params", "request"]
            )
            set_dict = {
                "import_export_code": import_export_code,
                "import_export_name": import_export_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            import_export_id = response.get("data", {}).get("data", {})

            # 保存导入导出管理信息供后续用例使用
            self.import_export_id = import_export_id
            self.import_export_code = import_export_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise








