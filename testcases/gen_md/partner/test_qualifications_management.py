import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("资质管理")
class TestQualificationsManagement(GenMdBaseTest):
    """资质管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.qualification_type_id = None
        cls.qualification_group_id = None
        cls.logger.info("资质管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_qualifications_type_cf", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_qualifications_procedure_head_cf", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 资质类型管理 =============
    @case_decorator(
        story="资质管理",
        title="测试新增资质类型",
        description="验证新增资质类型功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["资质类型", "新增"]
    )
    def test_save_qualification_type(self):
        """新增资质类型用例"""
        try:
            code = self.mock_util.generate_unique_code(tag="QT")
            name = f"资质类型_{self.mock_util.get_timestamp()}"

            set_dict = {
                "code": code,
                "name": name,
                "description":f"自动化测试资质类型-{self.mock_util.get_timestamp()}"
            }
            fields_to_filter = ["code", "name", "description"]

            response, extracted_id = self.standard_api_call(
                api_key="GEN-资质类型-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            self.qualification_type_id = response.get("data", {}).get("data", {})
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试查询资质类型分页",
        description="验证资质类型分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["资质类型", "查询"]
    )
    def test_query_qualification_type_page(self):
        """查询资质类型分页用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
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
                    }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试查询资质类型详情",
        description="验证资质类型详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["资质类型", "详情"]
    )
    def test_query_qualification_type_detail(self):
        """查询资质类型详情用例"""
        try:
            if not self.qualification_type_id:
                self.test_save_qualification_type()

            set_dict = {"id": self.qualification_type_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试提交资质类型导出任务",
        description="验证提交资质类型导出任务功能",
        severity="normal",
        file_level_order=4,
        tags=["资质类型", "导出任务"]
    )
    def test_submit_qualification_type_export_task(self):
        """提交资质类型导出任务用例"""
        try:
            api_path = self.get_api_path("资质类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] = {
                    
                "taskName": f"资质类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_qualifications_type_cf",
                        "modelName": "资质类型",
                        "sheetNo": 0,
                        "sheetName": "资质类型",
                        "headerConfigList": [
                            {
                                "name": "资质类型编码",
                                "type": "TEXT",
                                "field": "code"
                            },
                            {
                                "name": "资质类型名称",
                                "type": "TEXT",
                                "field": "name"
                            },
                            {
                                "name": "资质类型描述",
                                "type": "TEXT",
                                "field": "description"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW-table-container-GEN_MD$gen_qualifications_type_cf",
                    "viewKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW",
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
                                "field": "description"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_qualifications_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_qualifications_type_cf",
                    "modelName": "资质类型",
                    "containerKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW-table-container-GEN_MD$gen_qualifications_type_cf",
                    "viewKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_QUALIFICATIONS_TYPE_VIEW"
                }
            }
          
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试删除资质类型",
        description="验证删除资质类型功能",
        severity="normal",
        file_level_order=5,
        tags=["资质类型", "删除"]
    )
    def test_delete_qualification_type(self):
        """删除资质类型用例"""
        try:
            if not self.qualification_type_id:
                self.test_save_qualification_type()

            set_dict = {"id": self.qualification_type_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 资质组管理 =============
    @case_decorator(
        story="资质管理",
        title="测试新增资质组",
        description="验证新增资质组功能",
        severity="normal",
        file_level_order=6,
        tags=["资质组", "新增"]
    )
    def test_save_qualification_group(self):
        """新增资质组用例"""
        try:
            if not self.qualification_type_id:
                self.test_save_qualification_type()

            # 使用优化后的generate_unique_code方法，确保编码唯一性
            group_code = self.mock_util.generate_unique_code(tag="QG")
            group_name = f"资质组_{self.mock_util.get_timestamp()}"

            set_dict = {
                "code": group_code,
                "name": group_name,
                "itemList": [
                    {
                        "qualificationsType": {
                            "id": self.qualification_type_id 
                        },
                        "isRequired": True
                    }
                ]
            }
            fields_to_filter = ["code", "name", "itemList"]

            response, extracted_id = self.standard_api_call(
                api_key="GEN-资质组-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            self.qualification_group_id = response.get("data", {}).get("data", {})
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试查询资质组分页",
        description="验证资质组分页查询功能",
        severity="normal",
        file_level_order=7,
        tags=["资质组", "查询"]
    )
    def test_query_qualification_group_page(self):
        """查询资质组分页用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "groupCode", "type": "TEXT"},
                    {"name": "groupName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质组-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试查询资质组详情",
        description="验证资质组详情查询功能",
        severity="normal",
        file_level_order=8,
        tags=["资质组", "详情"]
    )
    def test_query_qualification_group_detail(self):
        """查询资质组详情用例"""
        try:
            if not self.qualification_group_id:
                self.test_save_qualification_group()

            set_dict = {"id": self.qualification_group_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质组-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试提交资质组导出任务",
        description="验证提交资质组导出任务功能",
        severity="normal",
        file_level_order=9,
        tags=["资质组", "导出任务"]
    )
    def test_submit_qualification_group_export_task(self):
        """提交资质组导出任务用例"""
        try:
            api_path = self.get_api_path("资质组-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] =  {
                "taskName": f"资质组-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_qualifications_procedure_head_cf",
                        "modelName": "资质组",
                        "sheetNo": 0,
                        "sheetName": "资质组",
                        "headerConfigList": [
                            {
                                "name": "资质组编码",
                                "type": "TEXT",
                                "field": "name"
                            },
                            {
                                "name": "资质组名称",
                                "type": "TEXT",
                                "field": "code"
                            },
                            {
                                "name": "创建时间",
                                "type": "DATE",
                                "field": "createdAt"
                            },
                            {
                                "name": "更新时间",
                                "type": "DATE",
                                "field": "updatedAt"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW-table-container-GEN_MD$gen_qualifications_procedure_head_cf",
                    "viewKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
        
                            }
                        },
                        "selectFields": [
                            {
                                "field": "name"
                            },
                            {
                                "field": "code"
                            },
                            {
                                "field": "createdAt"
                            },
                            {
                                "field": "updatedAt"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_qualifications_procedure_head_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_qualifications_procedure_head_cf",
                    "modelName": "资质组",
                    "containerKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW-table-container-GEN_MD$gen_qualifications_procedure_head_cf",
                    "viewKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_QUALIFICATIONS_GROUP_VIEW"
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="资质管理",
        title="测试删除资质组",
        description="验证删除资质组功能",
        severity="normal",
        file_level_order=10,
        tags=["资质组", "删除"]
    )
    def test_delete_qualification_group(self):
        """删除资质组用例"""
        try:
            if not self.qualification_group_id:
                self.test_save_qualification_group()

            set_dict = {"id": self.qualification_group_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-资质组-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="资质管理",
        title="测试资质类型标准导出",
        description="验证资质类型标准导出功能",
        severity="normal",
        file_level_order=11,
        tags=["资质类型", "导出"]
    )
    def test_export_qualification_type(self):
        """资质类型标准导出用例"""
        try:
            api_path = self.get_api_path("资质类型标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"资质类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "资质类型"
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
        story="资质管理",
        title="测试资质类型标准导入",
        description="验证资质类型标准导入功能",
        severity="normal",
        file_level_order=12,
        tags=["资质类型", "导入"]
    )
    def test_import_qualification_type(self):
        """资质类型标准导入用例"""
        try:
            api_path = self.get_api_path("资质类型标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"资质类型导入_{self.mock_util.get_timestamp()}",
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
        story="资质管理",
        title="测试通过OSS提交资质类型导入任务",
        description="验证通过OSS提交资质类型导入任务功能",
        severity="normal",
        file_level_order=13,
        tags=["资质类型", "OSS导入"]
    )
    def test_submit_qualification_type_import_task_by_oss(self):
        """通过OSS提交资质类型导入任务用例"""
        try:
            api_path = self.get_api_path("资质类型-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"资质类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"qualification_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "资质类型"
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
        story="资质管理",
        title="测试资质组标准导出",
        description="验证资质组标准导出功能",
        severity="normal",
        file_level_order=14,
        tags=["资质组", "导出"]
    )
    def test_export_qualification_group(self):
        """资质组标准导出用例"""
        try:
            api_path = self.get_api_path("资质组标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"资质组导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "资质组"
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
        story="资质管理",
        title="测试资质组标准导入",
        description="验证资质组标准导入功能",
        severity="normal",
        file_level_order=15,
        tags=["资质组", "导入"]
    )
    def test_import_qualification_group(self):
        """资质组标准导入用例"""
        try:
            api_path = self.get_api_path("资质组标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"资质组导入_{self.mock_util.get_timestamp()}",
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
        story="资质管理",
        title="测试通过OSS提交资质组导入任务",
        description="验证通过OSS提交资质组导入任务功能",
        severity="normal",
        file_level_order=16,
        tags=["资质组", "OSS导入"]
    )
    def test_submit_qualification_group_import_task_by_oss(self):
        """通过OSS提交资质组导入任务用例"""
        try:
            api_path = self.get_api_path("资质组-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"资质组OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"qualification_group_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "资质组"
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