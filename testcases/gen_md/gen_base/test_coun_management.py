import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("国家管理")
class TestCountryManagement(GenMdBaseTest):
    """国家管理测试类 - 覆盖所有国家配置相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.country_id = None
        cls.country_code = None
        cls.logger.info("国家管理测试类初始化完成")
        
        if  cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
            cls.timezone_id = cls.init_data.get("timezone_info",[])[0].get("id")
            
        

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据

            cls.db.delete(
                table="gen_coun_type_cf",
                where="coun_code like %s",
                params=["AT_%"]
            )

            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 国家配置基础管理 ================
    @case_decorator(
        story="国家配置管理",
        title="测试新增国家配置",
        description="验证GEN-国家配置表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["国家管理", "新增", "GEN_COUN_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_country(self):
        """新增国家配置用例 - GEN_COUN_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            coun_code = self.mock_util.generate_unique_code(tag="COUN")
            coun_name = f"测试国家_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-国家配置表-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["counCode", "counName", "currId", "timezoneId", "defaultRelv"], ["params", "request"]
            )
            set_dict = {
                "counCode": coun_code,
                "counName": coun_name,
                "currId":{"id":self.curr_id},
                "timezoneId":{"id":self.timezone_id},
                "defaultRelv": False
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.country_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试查询国家配置分页列表",
        description="验证GEN-国家配置表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_country_page(self):
        """查询国家配置分页列表用例 - GEN_COUN_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-国家配置表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "engName", "type": "TEXT"},
                    {"name": "isoCode", "type": "TEXT"}
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
        story="国家配置管理",
        title="测试查询国家配置详情",
        description="验证GEN-国家配置表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_country_detail(self):
        """查询国家配置详情用例 - GEN_COUN_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.country_id:
                self.test_save_country()

            api_path = self.get_api_path("GEN-国家配置表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.country_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试删除国家配置",
        description="验证GEN-国家配置表-删除服务功能",
        severity="normal",
        file_level_order=4,
        tags=["国家管理", "删除", "GEN_COUN_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_country(self):
        """删除国家配置用例 - GEN_COUN_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.country_id:
                self.test_save_country()

            api_path = self.get_api_path("GEN-国家配置表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.country_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

            # 重置ID，避免后续测试使用已删除的数据
            self.country_id = None

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 国家配置导入导出管理 ================
    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置标准导入",
        description="验证国家配置标准导入服务功能",
        severity="normal",
        file_level_order=5,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_import(self):
        """国家配置标准导入用例 - GEN_COUN_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("国家配置标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_COUN"),
                    "name": f"导入测试国家_{self.mock_util.get_timestamp()}",
                    "engName": f"Import Test Country {self.mock_util.get_timestamp()}",
                    "isoCode": "TC"
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
        story="国家配置导入导出管理",
        title="测试国家配置标准导出",
        description="验证国家配置标准导出服务功能",
        severity="normal",
        file_level_order=6,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_export(self):
        """国家配置标准导出用例 - GEN_COUN_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("国家配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "engName", "type": "TEXT"},
                    {"name": "isoCode", "type": "TEXT"}
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
        story="国家配置导入导出管理",
        title="测试国家配置OSS导入任务",
        description="验证国家配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=7,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_country_oss_import_task(self):
        """国家配置OSS导入任务用例 - GEN_COUN_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("国家配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_country_import_file.xlsx",
                "taskName": f"国家配置导入任务_{self.mock_util.get_timestamp()}",
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
        story="国家配置导入导出管理",
        title="测试国家配置导出任务",
        description="验证国家配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_country_export_task(self):
        """国家配置导出任务用例 - GEN_COUN_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("国家配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] =  {
                "taskName": f"国家管理-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_coun_type_cf",
                        "modelName": "国家配置",
                        "sheetNo": 0,
                        "sheetName": "国家配置",
                        "headerConfigList": [
                            {
                                "name": "国家代码",
                                "type": "TEXT",
                                "field": "counCode"
                            },
                            {
                                "name": "国家名称",
                                "type": "TEXT",
                                "field": "counName"
                            },
                            {
                                "name": "币种",
                                "type": "TEXT",
                                "field": "currId.currName"
                            },
                            {
                                "name": "时区",
                                "type": "TEXT",
                                "field": "timezoneId.timezoneCode"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_COUN_VIEW-table-container-GEN_MD$gen_coun_type_cf",
                    "viewKey": "GEN_MD$GEN_COUN_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_COUN_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "counCode"
                            },
                            {
                                "field": "counName"
                            },
                            {
                                "field": "currId",
                                "selectFields": [
                                    {
                                        "field": "currName"
                                    }
                                ]
                            },
                            {
                                "field": "timezoneId",
                                "selectFields": [
                                    {
                                        "field": "timezoneCode"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "GEN_MD$gen_coun_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_coun_type_cf",
                    "modelName": "国家配置",
                    "containerKey": "GEN_MD$GEN_COUN_VIEW-table-container-GEN_MD$gen_coun_type_cf",
                    "viewKey": "GEN_MD$GEN_COUN_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_COUN_VIEW"
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
