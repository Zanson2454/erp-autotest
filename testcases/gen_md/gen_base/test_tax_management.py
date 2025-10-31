import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("税配置管理")
class TestTaxManagement(GenMdBaseTest):
    """税配置管理测试类 - 覆盖所有税配置相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.tax_id = None
        cls.tax_code = None
        cls.logger.info("税配置管理测试类初始化完成")
        
        # 依赖数据
        if cls.init_data:
            cls.coun_id = cls.init_data.get("country_info",[])[0].get("coun_id")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据

            cls.db.delete(
                table='gen_tax_type_cf',
                where="tax_code like %s",
                params=["AT_%"]
            )

            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 税配置基础管理 ================
    @case_decorator(
        story="税配置管理",
        title="测试新增税配置",
        description="验证GEN-税配置-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["税配置", "新增", "GEN_TAX_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_tax(self):
        """新增税配置用例 - GEN_TAX_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            tax_code = self.mock_util.generate_unique_code(tag="TAX")
            tax_name = f"测试税配置_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-税配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "taxRate", "taxType", "description"], ["params", "request"]
            )
            set_dict = {
                "taxCode": tax_code,
                "taxcate": 'J',
                "tax": 0.13,  # 税率13%
                "counId": {
                    "id": self.coun_id
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.tax_id = response.get("data", {}).get("data", {})
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试查询税配置分页列表",
        description="验证GEN-税配置-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["税配置", "查询", "GEN_TAX_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_tax_page(self):
        """查询税配置分页列表用例 - GEN_TAX_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-税配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "taxRate", "type": "NUMBER"},
                    {"name": "taxType", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
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
        story="税配置管理",
        title="测试查询税配置详情",
        description="验证GEN-税配置-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["税配置", "查询", "GEN_TAX_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_tax_detail(self):
        """查询税配置详情用例 - GEN_TAX_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.tax_id:
                self.test_save_tax()

            api_path = self.get_api_path("GEN-税配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)


            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试税配置分页数据",
        description="验证税配置-分页数据服务功能",
        severity="normal",
        file_level_order=4,
        tags=["税配置", "分页数据", "GEN_TAX_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_paging_data(self):
        """税配置分页数据用例 - GEN_TAX_TYPE_CF_PAGING_DATA_SERVICE"""
        try:
            api_path = self.get_api_path("税配置-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageSize", "pageNo", "searchCondition"], ["params", "request"]
            )
            set_dict = {
                "pageSize": 20,
                "pageNo": 1,
                "searchCondition": {}
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
        story="税配置管理",
        title="测试根据ID查找税配置数据",
        description="验证税配置-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=5,
        tags=["税配置", "ID查找", "GEN_TAX_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_find_tax_by_id(self):
        """根据ID查找税配置数据用例 - GEN_TAX_TYPE_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.tax_id:
                self.test_save_tax()

            api_path = self.get_api_path("税配置-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据包含必要字段
            tax_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(tax_data.get("code"), "not_empty")
            self.assert_util.assert_by_operator(tax_data.get("name"), "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="税配置管理",
        title="测试删除税配置",
        description="验证GEN-税配置-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["税配置", "删除", "GEN_TAX_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_tax(self):
        """删除税配置用例 - GEN_TAX_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.tax_id:
                self.test_save_tax()

            api_path = self.get_api_path("GEN-税配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 税配置导入导出管理 ================
    @case_decorator(
        story="税配置导入导出管理",
        title="测试税配置标准导入",
        description="验证税配置标准导入服务功能",
        severity="normal",
        file_level_order=7,
        tags=["税配置", "导入", "GEN_TAX_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_import(self):
        """税配置标准导入用例 - GEN_TAX_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("税配置标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_TAX"),
                    "name": f"导入测试税配置_{self.mock_util.get_timestamp()}",
                    "taxRate": 9.0,
                    "taxType": "VAT",
                    "description": "导入的税配置描述"
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
        story="税配置导入导出管理",
        title="测试税配置标准导出",
        description="验证税配置标准导出服务功能",
        severity="normal",
        file_level_order=8,
        tags=["税配置", "导出", "GEN_TAX_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_export(self):
        """税配置标准导出用例 - GEN_TAX_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("税配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "taxRate", "type": "NUMBER"},
                    {"name": "taxType", "type": "TEXT"},
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
        story="税配置任务管理",
        title="测试税配置OSS导入任务",
        description="验证税配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=9,
        tags=["税配置", "任务管理", "GEN_TAX_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_oss_import_task(self):
        """税配置OSS导入任务用例 - GEN_TAX_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("税配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_tax_import_file.xlsx",
                "taskName": f"税配置导入任务_{self.mock_util.get_timestamp()}",
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
        story="税配置任务管理",
        title="测试税配置导出任务",
        description="验证税配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["税配置", "任务管理", "GEN_TAX_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_tax_export_task(self):
        """税配置导出任务用例 - GEN_TAX_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("税配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['parmas'] =  {
                "taskName": f"税管理-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_tax_type_cf",
                        "modelName": "税配置",
                        "sheetNo": 0,
                        "sheetName": "税配置",
                        "headerConfigList": [
                            {
                                "name": "税码",
                                "type": "TEXT",
                                "field": "taxCode"
                            },
                            {
                                "name": "国家",
                                "type": "TEXT",
                                "field": "counId.counName"
                            },
                            {
                                "name": "类型",
                                "type": "ENUM",
                                "field": "taxcate",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "进项",
                                        "label": "进项",
                                        "value": "J"
                                    },
                                    {
                                        "_row_id_": "销项",
                                        "label": "销项",
                                        "value": "X"
                                    }
                                ]
                            },
                            {
                                "name": "税率(%)",
                                "type": "NUMBER",
                                "field": "tax"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_TAX_TYPE_VIEW-table-container-GEN_MD$gen_tax_type_cf",
                    "viewKey": "GEN_MD$GEN_TAX_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_TAX_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "taxCode"
                            },
                            {
                                "field": "taxcate"
                            },
                            {
                                "field": "tax"
                            },
                            {
                                "field": "counId",
                                "selectFields": [
                                    {
                                        "field": "counName"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "GEN_MD$gen_tax_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_tax_type_cf",
                    "modelName": "税配置",
                    "containerKey": "GEN_MD$GEN_TAX_TYPE_VIEW-table-container-GEN_MD$gen_tax_type_cf",
                    "viewKey": "GEN_MD$GEN_TAX_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_TAX_TYPE_VIEW"
                }
            }


            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
