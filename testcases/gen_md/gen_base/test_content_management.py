import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("内容管理")
class TestContentManagement(GenMdBaseTest):
    """内容管理测试类 - 整合附件、文本组、文本类型等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.attachment_id = None
        cls.attachment_code = None
        cls.text_group_id = None
        cls.text_group_code = None
        cls.text_type_id = None
        cls.text_type_code = None
        cls.logger.info("内容管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_attachment_md", "gen_text_group_md", "gen_text_type_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 附件管理 ================
    @case_decorator(
        story="附件管理",
        title="测试新增附件",
        description="验证新增附件功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["附件管理", "新增"]
    )
    def test_save_attachment(self):
        """新增附件用例"""
        try:
            attachment_code = self.mock_data.generate_unique_code(tag="Attachment")
            attachment_name = f"附件_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-附件组-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["attachment_code", "attachment_name"], ["params", "request"]
            )
            set_dict = {"attachment_code": attachment_code, "attachment_name": attachment_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.attachment_id = response.get("data", {}).get("data", {})
            self.attachment_code = attachment_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试查询附件列表",
        description="验证附件列表查询功能",
        severity="normal",
        order=2,
        tags=["附件管理", "查询"]
    )
    def test_query_attachment_list(self):
        """查询附件列表用例"""
        try:
            api_path = self.get_api_path("GEN-附件组-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "attachment_code", "type": "TEXT"},
                    {"name": "attachment_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试删除附件",
        description="验证删除附件功能",
        severity="normal",
        order=3,
        tags=["附件管理", "删除"]
    )
    def test_delete_attachment(self):
        """删除附件用例"""
        try:
            if not self.attachment_id:
                self.test_save_attachment()

            api_path = self.get_api_path("GEN-附件类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.attachment_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 文本组管理 ================
    @case_decorator(
        story="文本组管理",
        title="测试新增文本组",
        description="验证新增文本组功能",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["文本组管理", "新增"]
    )
    def test_save_text_group(self):
        """新增文本组用例"""
        try:
            text_group_code = self.mock_data.generate_unique_code(tag="TextGroup")
            text_group_name = f"文本组_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-文本组-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["text_group_code", "text_group_name"], ["params", "request"]
            )
            set_dict = {"text_group_code": text_group_code, "text_group_name": text_group_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.text_group_id = response.get("data", {}).get("data", {})
            self.text_group_code = text_group_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本组管理",
        title="测试查询文本组列表",
        description="验证文本组列表查询功能",
        severity="normal",
        order=5,
        tags=["文本组管理", "查询"]
    )
    def test_query_text_group_list(self):
        """查询文本组列表用例"""
        try:
            api_path = self.get_api_path("GEN-文本组-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "text_group_code", "type": "TEXT"},
                    {"name": "text_group_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本组管理",
        title="测试删除文本组",
        description="验证删除文本组功能",
        severity="normal",
        order=6,
        tags=["文本组管理", "删除"]
    )
    def test_delete_text_group(self):
        """删除文本组用例"""
        try:
            if not self.text_group_id:
                self.test_save_text_group()

            api_path = self.get_api_path("GEN-文本组-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.text_group_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 文本类型管理 ================
    @case_decorator(
        story="文本类型管理",
        title="测试新增文本类型",
        description="验证新增文本类型功能",
        severity="blocker",
        order=7,
        smoke=True,
        tags=["文本类型管理", "新增"]
    )
    def test_save_text_type(self):
        """新增文本类型用例"""
        try:
            text_type_code = self.mock_data.generate_unique_code(tag="TextType")
            text_type_name = f"文本类型_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-文本类型-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["text_type_code", "text_type_name"], ["params", "request"]
            )
            set_dict = {"text_type_code": text_type_code, "text_type_name": text_type_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.text_type_id = response.get("data", {}).get("data", {})
            self.text_type_code = text_type_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本类型管理",
        title="测试查询文本类型列表",
        description="验证文本类型列表查询功能",
        severity="normal",
        order=8,
        tags=["文本类型管理", "查询"]
    )
    def test_query_text_type_list(self):
        """查询文本类型列表用例"""
        try:
            api_path = self.get_api_path("GEN-文本类型-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "text_type_code", "type": "TEXT"},
                    {"name": "text_type_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本类型管理",
        title="测试删除文本类型",
        description="验证删除文本类型功能",
        severity="normal",
        order=9,
        tags=["文本类型管理", "删除"]
    )
    def test_delete_text_type(self):
        """删除文本类型用例"""
        try:
            if not self.text_type_id:
                self.test_save_text_type()

            api_path = self.get_api_path("GEN-文本类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.text_type_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 