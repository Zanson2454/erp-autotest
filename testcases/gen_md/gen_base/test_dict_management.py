import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("数据字典管理")
class TestDictManagement(GenMdBaseTest):
    """数据字典管理测试类 - 覆盖所有数据字典类别相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.dict_id = None
        cls.dict_code = None
        cls.logger.info("数据字典管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
        
            cls.db.delete(
                table="gen_dict_head_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_dict_detail_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 数据字典基础管理 ================
    @case_decorator(
        story="数据字典管理",
        title="测试新增数据字典类别",
        description="验证GEN-数据字典类别-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["数据字典", "新增", "GEN_DICT_HEAD_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_dict(self):
        """新增数据字典类别用例 - GEN_DICT_HEAD_CF_SAVE_ACTION_SERVICE"""
        try:
            dict_code = self.mock_util.generate_unique_code(tag="DICT")
            dict_name = f"测试数据字典类别_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-数据字典类别-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "isSystem", "itemList"], ["params", "request"]
            )
            set_dict = {
                "code": dict_code,
                "name": dict_name,
                "isSystem": True,
                "itemList": [
                    {
                        "code": f"P_CODE1_{self.mock_util.get_timestamp()}",
                        "name": f"字典项1_{self.mock_util.get_timestamp()}",
                        "isSystem": True,
                        "sort": 1,
                        "status": "ENABLED"
                    },
                    {
                        "code": f"P_CODE2_{self.mock_util.get_timestamp()}",
                        "name": f"字典项2_{self.mock_util.get_timestamp()}",
                        "isSystem": True,
                        "sort": 2,
                        "status": "ENABLED"
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.dict_id = response.get("data", {}).get("data", {})
            self.dict_code = dict_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试查询数据字典类别分页列表",
        description="验证GEN-数据字典类别-查询分页服务功能",
        severity="normal",
        order=2,
        tags=["数据字典", "查询", "GEN_DICT_HEAD_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_dict_page(self):
        """查询数据字典类别分页列表用例 - GEN_DICT_HEAD_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-数据字典类别-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict =  {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {
                        "name": "code",
                        "type": "TEXT"
                    },
                    {
                        "name": "name",
                        "type": "TEXT"
                    },
                    {
                        "name": "status",
                        "type": "SELECT"
                    }
                ],
                "systemParams": None
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
        story="数据字典管理",
        title="测试查询数据字典类别详情",
        description="验证GEN-数据字典类别-查询详情服务功能",
        severity="normal",
        order=3,
        tags=["数据字典", "查询", "GEN_DICT_HEAD_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_dict_detail(self):
        """查询数据字典类别详情用例 - GEN_DICT_HEAD_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            api_path = self.get_api_path("GEN-数据字典类别-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.dict_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试启用数据字典类别",
        description="验证GEN-数据字典类别-启用服务功能",
        severity="normal",
        order=4,
        tags=["数据字典", "启用", "GEN_DICT_HEAD_CF_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_dict(self):
        """启用数据字典类别用例 - GEN_DICT_HEAD_CF_ENABLED_ACTION_SERVICE"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            api_path = self.get_api_path("GEN-数据字典类别-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.dict_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试禁用数据字典类别",
        description="验证GEN-数据字典类别-禁用服务功能",
        severity="normal",
        order=5,
        tags=["数据字典", "禁用", "GEN_DICT_HEAD_CF_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_dict(self):
        """禁用数据字典类别用例 - GEN_DICT_HEAD_CF_DISABLED_ACTION_SERVICE"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            api_path = self.get_api_path("GEN-数据字典类别-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.dict_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典管理",
        title="测试删除数据字典类别",
        description="验证GEN-数据字典类别-删除服务功能",
        severity="critical",
        order=6,
        tags=["数据字典", "删除", "GEN_DICT_HEAD_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_dict(self):
        """删除数据字典类别用例 - GEN_DICT_HEAD_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.dict_id:
                self.test_save_dict()

            api_path = self.get_api_path("GEN-数据字典类别-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.dict_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 数据字典导入导出管理 ================
    @case_decorator(
        story="数据字典导入导出管理",
        title="测试数据字典类别标准导入",
        description="验证数据字典类别标准导入服务功能",
        severity="normal",
        order=7,
        tags=["数据字典", "导入", "GEN_DICT_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_import(self):
        """数据字典类别标准导入用例 - GEN_DICT_HEAD_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("数据字典类别标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_DICT"),
                    "name": f"导入测试数据字典类别_{self.mock_util.get_timestamp()}",
                    "dictType": "CUSTOM",
                    "description": "导入的数据字典类别描述"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="数据字典导入导出管理",
        title="测试数据字典类别标准导出",
        description="验证数据字典类别标准导出服务功能",
        severity="normal",
        order=8,
        tags=["数据字典", "导出", "GEN_DICT_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_export(self):
        """数据字典类别标准导出用例 - GEN_DICT_HEAD_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("数据字典类别标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "dictType", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
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
        story="数据字典任务管理",
        title="测试数据字典类别OSS导入任务",
        description="验证数据字典类别-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=9,
        tags=["数据字典", "任务管理", "GEN_DICT_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_oss_import_task(self):
        """数据字典类别OSS导入任务用例 - GEN_DICT_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("数据字典类别-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_dict_import_file.xlsx",
                "taskName": f"数据字典类别导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
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
        story="数据字典任务管理",
        title="测试数据字典类别导出任务",
        description="验证数据字典类别-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=10,
        tags=["数据字典", "任务管理", "GEN_DICT_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_dict_export_task(self):
        """数据字典类别导出任务用例 - GEN_DICT_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("数据字典类别-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"数据字典类别导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "dictType", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
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
