import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("相关方类型配置")
class TestPartnerTypeManagement(GenMdBaseTest):
    """相关方类型配置管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_type_id = None
        cls.partner_type_code = None
        cls.logger.info("相关方类型配置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_partner_type_cf", 
                where="type_code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 核心功能测试 =============
    @case_decorator(
        story="相关方类型配置",
        title="测试新增相关方类型",
        description="验证新增相关方类型功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["相关方类型", "新增"]
    )
    def test_save_partner_type(self):
        """新增相关方类型用例"""
        try:
            type_code = self.mock_util.generate_unique_code(tag="PT")
            type_name = f"相关方类型_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-相关方类型-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["typeCode", "typeName", "category", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "typeCode": type_code,
                "typeName": type_name,
                "category": "BUSINESS",
                "status": "ENABLED",
                "remark": f"自动化测试相关方类型-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.partner_type_id = response.get("data", {}).get("data", {})
            self.partner_type_code = type_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方类型配置",
        title="测试查询相关方类型分页",
        description="验证相关方类型分页查询功能",
        severity="normal",
        order=2,
        tags=["相关方类型", "查询"]
    )
    def test_query_partner_type_page(self):
        """查询相关方类型分页用例"""
        try:
            api_path = self.get_api_path("GEN-相关方类型-查询分页服务")
            params, url = self.get_api_params(api_path)

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
                    {"name": "typeCode", "type": "TEXT"},
                    {"name": "typeName", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方类型配置",
        title="测试查询相关方类型详情",
        description="验证相关方类型详情查询功能",
        severity="normal",
        order=3,
        tags=["相关方类型", "详情"]
    )
    def test_query_partner_type_detail(self):
        """查询相关方类型详情用例"""
        try:
            if not self.partner_type_id:
                self.test_save_partner_type()

            api_path = self.get_api_path("GEN-相关方类型-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方类型配置",
        title="测试根据ID查找相关方类型数据",
        description="验证根据ID查找相关方类型数据功能",
        severity="normal",
        order=4,
        tags=["相关方类型", "查找"]
    )
    def test_find_partner_type_by_id(self):
        """根据ID查找相关方类型数据用例"""
        try:
            if not self.partner_type_id:
                self.test_save_partner_type()

            api_path = self.get_api_path("GEN-相关方类型定义配置表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方类型配置",
        title="测试根据类型查询相关方分页",
        description="验证根据类型查询相关方分页功能",
        severity="normal",
        order=5,
        tags=["相关方类型", "相关方查询"]
    )
    def test_query_partner_by_type_page(self):
        """根据类型查询相关方分页用例"""
        try:
            api_path = self.get_api_path("GEN-相关方类型-根据类型查询相关方分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["typeId", "pageable"],
                ["params", "request"]
            )
            set_dict = {
                "typeId": 1,  # 示例类型ID
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方类型配置",
        title="测试提交相关方类型导出任务",
        description="验证提交相关方类型导出任务功能",
        severity="normal",
        order=6,
        tags=["相关方类型", "导出任务"]
    )
    def test_submit_partner_type_export_task(self):
        """提交相关方类型导出任务用例"""
        try:
            api_path = self.get_api_path("相关方类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"相关方类型导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"相关方类型_{self.mock_util.get_timestamp()}",
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

    @case_decorator(
        story="相关方类型配置",
        title="测试删除相关方类型",
        description="验证删除相关方类型功能",
        severity="normal",
        order=7,
        tags=["相关方类型", "删除"]
    )
    def test_delete_partner_type(self):
        """删除相关方类型用例"""
        try:
            if not self.partner_type_id:
                self.test_save_partner_type()

            api_path = self.get_api_path("GEN-相关方类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": [self.partner_type_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="相关方类型配置",
        title="测试相关方类型标准导出",
        description="验证相关方类型标准导出功能",
        severity="normal",
        order=8,
        tags=["相关方类型", "导出"]
    )
    def test_export_partner_type(self):
        """相关方类型标准导出用例"""
        try:
            api_path = self.get_api_path("相关方类型标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"相关方类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "相关方类型"
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
        story="相关方类型配置",
        title="测试相关方类型标准导入",
        description="验证相关方类型标准导入功能",
        severity="normal",
        order=9,
        tags=["相关方类型", "导入"]
    )
    def test_import_partner_type(self):
        """相关方类型标准导入用例"""
        try:
            api_path = self.get_api_path("相关方类型标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"相关方类型导入_{self.mock_util.get_timestamp()}",
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

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="相关方类型配置",
        title="测试通过OSS提交相关方类型导入任务",
        description="验证通过OSS提交相关方类型导入任务功能",
        severity="normal",
        order=10,
        tags=["相关方类型", "OSS导入"]
    )
    def test_submit_partner_type_import_task_by_oss(self):
        """通过OSS提交相关方类型导入任务用例"""
        try:
            api_path = self.get_api_path("相关方类型-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"相关方类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "相关方类型"
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