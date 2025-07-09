import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator



@allure.epic("通用基础数据")
@allure.feature("时区管理")
class TestTimezoneManagement(GenMdBaseTest):
    """时区管理测试类 - 覆盖所有时区配置相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 数据存储
        cls.timezone_id = None
        cls.timezone_code = None

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据

            cls.db.delete(
                table="gen_timezone_type_cf",
                where="timezone_code like %s",
                params=["AT_%"]
            )

            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 时区配置基础管理 ================
    @case_decorator(
        story="时区配置管理",
        title="测试新增时区配置",
        description="验证GEN-时区配置-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["时区管理", "新增", "GEN_TIMEZONE_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_timezone(self):
        """新增时区配置用例 - GEN_TIMEZONE_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            timezone_code = self.mock_data.generate_unique_code(tag="TZ")
            timezone_name = f"测试时区_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-时区配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["timezoneCode", "timezoneDesc", "timezoneFormat", "isSummerTime", "summerTimeEnd", "summerTimeStart"], ["params", "request"]
            )
            set_dict = {
                "timezoneCode": timezone_code,
                "timezoneDesc": timezone_name,
                "timezoneFormat": "UTC",
                "isSummerTime": False,
                "summerTimeEnd": None,
                "summerTimeStart": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.timezone_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试查询时区配置分页列表",
        description="验证GEN-时区配置-查询分页服务功能",
        severity="normal",
        order=2,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_timezone_page(self):
        """查询时区配置分页列表用例 - GEN_TIMEZONE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-时区配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "timezoneCode", "type": "TEXT"},
                    {"name": "timezoneDesc", "type": "TEXT"},
                    {"name": "timezoneFormat", "type": "TEXT"},
                    {"name": "isSummerTime", "type": "TEXT"},
                    {"name": "summerTimeEnd", "type": "TEXT"},
                    {"name": "summerTimeStart", "type": "TEXT"}
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
        story="时区配置管理",
        title="测试查询时区配置详情",
        description="验证GEN-时区配置-查询详情服务功能",
        severity="normal",
        order=3,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_timezone_detail(self):
        """查询时区配置详情用例 - GEN_TIMEZONE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            api_path = self.get_api_path("GEN-时区配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.timezone_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试删除时区配置",
        description="验证GEN-时区配置-删除服务功能",
        severity="normal",
        order=4,
        tags=["时区管理", "删除", "GEN_TIMEZONE_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_timezone(self):
        """删除时区配置用例 - GEN_TIMEZONE_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            api_path = self.get_api_path("GEN-时区配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.timezone_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

            # 重置ID，避免后续测试使用已删除的数据
            self.timezone_id = None

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 时区配置导入导出管理 ================
    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置标准导入",
        description="验证时区配置标准导入服务功能",
        severity="normal",
        order=5,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_import(self):
        """时区配置标准导入用例 - GEN_TIMEZONE_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("时区配置标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_data.generate_unique_code(tag="IMPORT_TZ"),
                    "name": f"导入测试时区_{self.mock_data.get_timestamp()}",
                    "offset": "+09:00",  # 东九区
                    "description": "导入的时区配置"
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
        story="时区配置导入导出管理",
        title="测试时区配置标准导出",
        description="验证时区配置标准导出服务功能",
        severity="normal",
        order=6,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_export(self):
        """时区配置标准导出用例 - GEN_TIMEZONE_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("时区配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "offset", "type": "TEXT"},
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
        story="时区配置导入导出管理",
        title="测试时区配置OSS导入任务",
        description="验证时区配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=7,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_timezone_oss_import_task(self):
        """时区配置OSS导入任务用例 - GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("时区配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_timezone_import_file.xlsx",
                "taskName": f"时区配置导入任务_{self.mock_data.get_timestamp()}",
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
        story="时区配置导入导出管理",
        title="测试时区配置导出任务",
        description="验证时区配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=8,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_timezone_export_task(self):
        """时区配置导出任务用例 - GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("时区配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['params']= {
                "taskName": f"时区管理-{self.nickname}-{self.mock_data.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_timezone_type_cf",
                        "modelName": "时区配置",
                        "sheetNo": 0,
                        "sheetName": "时区配置",
                        "headerConfigList": [
                            {
                                "name": "时区编码",
                                "type": "TEXT",
                                "field": "timezoneCode"
                            },
                            {
                                "name": "时区描述",
                                "type": "TEXT",
                                "field": "timezoneDesc"
                            },
                            {
                                "name": "时区格式",
                                "type": "ENUM",
                                "field": "timezoneFormat",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "UTC",
                                        "label": "UTC",
                                        "value": "UTC"
                                    },
                                    {
                                        "_row_id_": "GMT",
                                        "label": "GMT",
                                        "value": "GMT"
                                    }
                                ]
                            },
                            {
                                "name": "启用夏令时",
                                "type": "BOOL",
                                "field": "isSummerTime"
                            },
                            {
                                "name": "夏令时开始时间",
                                "type": "DATE",
                                "field": "summerTimeStart"
                            },
                            {
                                "name": "夏令时结束时间",
                                "type": "DATE",
                                "field": "summerTimeEnd"
                            },
                            {
                                "name": "状态",
                                "type": "ENUM",
                                "field": "status",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "已启用",
                                        "label": "已启用",
                                        "value": "ENABLED"
                                    },
                                    {
                                        "_row_id_": "已停用",
                                        "label": "已停用",
                                        "value": "DISABLED"
                                    },
                                    {
                                        "_row_id_": "未启用",
                                        "label": "未启用",
                                        "value": "INACTIVE"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_TIMEZONE_VIEW-table-container-GEN_MD$gen_timezone_type_cf",
                    "viewKey": "GEN_MD$GEN_TIMEZONE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_TIMEZONE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "timezoneCode"
                            },
                            {
                                "field": "timezoneDesc"
                            },
                            {
                                "field": "timezoneFormat"
                            },
                            {
                                "field": "isSummerTime"
                            },
                            {
                                "field": "summerTimeStart"
                            },
                            {
                                "field": "summerTimeEnd"
                            },
                            {
                                "field": "status"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_timezone_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_timezone_type_cf",
                    "modelName": "时区配置",
                    "containerKey": "GEN_MD$GEN_TIMEZONE_VIEW-table-container-GEN_MD$gen_timezone_type_cf",
                    "viewKey": "GEN_MD$GEN_TIMEZONE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_TIMEZONE_VIEW"
                }
            }


            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
