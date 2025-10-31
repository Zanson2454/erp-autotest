import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴类型管理")
class TestBusinessPartnerTypeManagement(GenMdBaseTest):
    """合作伙伴类型管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_type_id = None
        cls.logger.info("合作伙伴类型管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_business_partner_type_cf", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="合作伙伴类型管理",
        title="测试新增合作伙伴类型",
        description="验证新增合作伙伴类型功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["合作伙伴类型", "新增"]
    )
    def test_save_business_partner_type(self):
        """新增合作伙伴类型用例"""
        try:
            # 使用优化后的唯一编码生成方法
            code = self.mock_util.generate_unique_code(tag="BPT")
            name = f"合作伙伴类型_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-合作伙伴类型-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["typeCode", "typeName", "category", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "code": code,
                "name": name,
                "category": "BUSINESS",
                "status": "ENABLED",
                "remark": f"自动化测试合作伙伴类型-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.partner_type_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型管理",
        title="测试查询合作伙伴类型分页",
        description="验证合作伙伴类型分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["合作伙伴类型", "查询"]
    )
    def test_query_business_partner_type_page(self):
        """查询合作伙伴类型分页用例"""
        try:
            api_path = self.get_api_path("GEN-合作伙伴类型-查询分页服务")
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
        story="合作伙伴类型管理",
        title="测试查询合作伙伴类型详情",
        description="验证合作伙伴类型详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["合作伙伴类型", "详情"]
    )
    def test_query_business_partner_type_detail(self):
        """查询合作伙伴类型详情用例"""
        try:
            if not self.partner_type_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-查询详情服务")
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
        story="合作伙伴类型管理",
        title="测试合作伙伴类型分页数据服务",
        description="验证合作伙伴类型分页数据服务功能",
        severity="normal",
        file_level_order=4,
        tags=["合作伙伴类型", "分页数据"]
    )
    def test_business_partner_type_paging_data(self):
        """合作伙伴类型分页数据服务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "queryCondition"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "queryCondition": {}
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
        story="合作伙伴类型管理",
        title="测试启用合作伙伴类型",
        description="验证启用合作伙伴类型功能",
        severity="normal",
        file_level_order=5,
        tags=["合作伙伴类型", "启用"]
    )
    def test_enable_business_partner_type(self):
        """启用合作伙伴类型用例"""
        try:
            if not self.partner_type_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_id }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型管理",
        title="测试禁用合作伙伴类型",
        description="验证禁用合作伙伴类型功能",
        severity="normal",
        file_level_order=6,
        tags=["合作伙伴类型", "禁用"]
    )
    def test_disable_business_partner_type(self):
        """禁用合作伙伴类型用例"""
        try:
            if not self.partner_type_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型管理",
        title="测试删除合作伙伴类型",
        description="验证删除合作伙伴类型功能",
        severity="normal",
        file_level_order=7,
        tags=["合作伙伴类型", "删除"]
    )
    def test_delete_business_partner_type(self):
        """删除合作伙伴类型用例"""
        try:
            if not self.partner_type_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_id}
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
        story="合作伙伴类型管理",
        title="测试合作伙伴类型标准导出",
        description="验证合作伙伴类型标准导出功能",
        severity="normal",
        file_level_order=8,
        tags=["合作伙伴类型", "导出"]
    )
    def test_export_business_partner_type(self):
        """合作伙伴类型标准导出用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"合作伙伴类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "合作伙伴类型",
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

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="合作伙伴类型管理",
        title="测试合作伙伴类型标准导入",
        description="验证合作伙伴类型标准导入功能",
        severity="normal",
        file_level_order=9,
        tags=["合作伙伴类型", "导入"]
    )
    def test_import_business_partner_type(self):
        """合作伙伴类型标准导入用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"合作伙伴类型导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL",
                    "sheetName": "合作伙伴类型"
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
        story="合作伙伴类型管理",
        title="测试提交合作伙伴类型导出任务",
        description="验证提交合作伙伴类型导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["合作伙伴类型", "导出任务"]
    )
    def test_submit_business_partner_type_export_task(self):
        """提交合作伙伴类型导出任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] =  {
                "taskName": f"合作伙伴类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_business_partner_type_cf",
                        "modelName": "合作伙伴类型",
                        "sheetNo": 0,
                        "sheetName": "合作伙伴类型",
                        "headerConfigList": [
                            {
                                "name": "编码",
                                "type": "TEXT",
                                "field": "code"
                            },
                            {
                                "name": "名称",
                                "type": "TEXT",
                                "field": "name"
                            },
                            {
                                "name": "类别",
                                "type": "ENUM",
                                "field": "classType",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "个人",
                                        "label": "个人",
                                        "value": "PERSON"
                                    },
                                    {
                                        "_row_id_": "公司",
                                        "label": "公司",
                                        "value": "COMPANY"
                                    }
                                ]
                            },
                            {
                                "name": "角色",
                                "type": "ENUM",
                                "field": "role",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "供应商",
                                        "label": "供应商",
                                        "value": "SUPPLIER"
                                    },
                                    {
                                        "_row_id_": "客户",
                                        "label": "客户",
                                        "value": "CUSTOMER"
                                    }
                                ]
                            },
                            {
                                "name": "是否内部公司",
                                "type": "BOOL",
                                "field": "isInternal"
                            },
                            {
                                "name": "说明",
                                "type": "TEXT",
                                "field": "desc"
                            },
                            {
                                "name": "状态",
                                "type": "ENUM",
                                "field": "status",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "未启用",
                                        "label": "未启用",
                                        "value": "INACTIVE"
                                    },
                                    {
                                        "_row_id_": "已启用",
                                        "label": "已启用",
                                        "value": "ENABLED"
                                    },
                                    {
                                        "_row_id_": "已停用",
                                        "label": "已停用",
                                        "value": "DISABLED"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW-table-container-GEN_MD$gen_business_partner_type_cf",
                    "viewKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "code"
                            },
                            {
                                "field": "name"
                            },
                            {
                                "field": "classType"
                            },
                            {
                                "field": "role"
                            },
                            {
                                "field": "isInternal"
                            },
                            {
                                "field": "desc"
                            },
                            {
                                "field": "status"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_business_partner_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_business_partner_type_cf",
                    "modelName": "合作伙伴类型",
                    "containerKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW-table-container-GEN_MD$gen_business_partner_type_cf",
                    "viewKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BUSINESS_PARTNER_TYPE_VIEW"
                }
            }   

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="oss 导入依赖文件，暂时跳过")
    @case_decorator(
        story="合作伙伴类型管理",
        title="测试通过OSS提交合作伙伴类型导入任务",
        description="验证通过OSS提交合作伙伴类型导入任务功能",
        severity="normal",
        file_level_order=11,
        tags=["合作伙伴类型", "OSS导入"]
    )
    def test_submit_business_partner_type_import_task_by_oss(self):
        """通过OSS提交合作伙伴类型导入任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "合作伙伴类型"
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