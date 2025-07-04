import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("文本管理")
class TestTextManagement(GenMdBaseTest):
    """文本管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.text_type_id = None
        cls.text_group_id = None
        cls.logger.info("文本管理测试类初始化完成")
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        
        cls.call_times=0
        

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
        
            cls.db.delete(
                table="gen_text_type_cf", 
                where="text_code like %s", 
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_text_procedure_head_cf", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 文本类型管理 =============
    @case_decorator(
        story="文本管理",
        title="测试新增文本类型",
        description="验证新增文本类型功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["文本类型", "新增"]
    )
    def test_save_text_type(self):
        """新增文本类型用例"""
        try:
            # 每次都生成新的唯一标识，避免重复键错误
            text_code = self.mock_util.generate_unique_code(tag="TXT")
            text_name = f"文本类型_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-文本类型-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["textCode", "textName", "btClass", "desc"],
                ["params", "request"]
            )
            set_dict = {
                "textCode": text_code,
                "textName": text_name,
                "btClass": 'SLS',
                "desc": f"自动化文本-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 赋值
            self.text_type_id  = response.get("data", {}).get("data", {})
            

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本类型分页",
        description="验证文本类型分页查询功能",
        severity="normal",
        order=2,
        tags=["文本类型", "查询"]
    )
    def test_query_text_type_page(self):
        """查询文本类型分页用例"""
        try:
            api_path = self.get_api_path("GEN-文本类型-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            set_dict =  {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {
                        "name": "btClass",
                        "type": "SELECT"
                    },
                    {
                        "name": "textCode",
                        "type": "TEXT"
                    },
                    {
                        "name": "textName",
                        "type": "TEXT"
                    }
                ],
                "systemParams": None
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
        story="文本管理",
        title="测试查询文本类型详情",
        description="验证文本类型详情查询功能",
        severity="normal",
        order=3,
        tags=["文本类型", "详情"]
    )
    def test_query_text_type_detail(self):
        """查询文本类型详情用例"""
        try:
            if not self.text_type_id:
                self.test_save_text_type()

            api_path = self.get_api_path("GEN-文本类型-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.text_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试提交文本类型导出任务",
        description="验证提交文本类型导出任务功能",
        severity="normal",
        order=4,
        tags=["文本类型", "导出任务"]
    )
    def test_submit_text_type_export_task(self):
        """提交文本类型导出任务用例"""
        try:
            api_path = self.get_api_path("文本类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params = {
                "serviceKey": "GEN_MD$GEN_TEXT_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"文本类型导出-{self.nickname}-{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_text_type_cf",
                            "modelName": "文本类型",
                            "sheetNo": 0,
                            "sheetName": "文本类型",
                            "headerConfigList": [
                                {
                                    "name": "文本编码",
                                    "type": "TEXT",
                                    "field": "textCode"
                                },
                                {
                                    "name": "业务类别",
                                    "type": "ENUM",
                                    "field": "btClass",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "销售",
                                            "label": "销售",
                                            "value": "SLS"
                                        },
                                        {
                                            "_row_id_": "采购",
                                            "label": "采购",
                                            "value": "PUR"
                                        }
                                    ]
                                },
                                {
                                    "name": "文本名称",
                                    "type": "TEXT",
                                    "field": "textName"
                                },
                                {
                                    "name": "说明",
                                    "type": "TEXT",
                                    "field": "desc"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$GEN_TEXT_TYPE_VIEW-table-container-GEN_MD$gen_text_type_cf",
                        "viewKey": "GEN_MD$GEN_TEXT_TYPE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_TEXT_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "textCode"
                                },
                                {
                                    "field": "btClass"
                                },
                                {
                                    "field": "textName"
                                },
                                {
                                    "field": "desc"
                                }
                            ],
                            "modelKey": "GEN_MD$gen_text_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_text_type_cf",
                        "modelName": "文本类型",
                        "containerKey": "GEN_MD$GEN_TEXT_TYPE_VIEW-table-container-GEN_MD$gen_text_type_cf",
                        "viewKey": "GEN_MD$GEN_TEXT_TYPE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_TEXT_TYPE_VIEW"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)
            self.export_task_id = response.get("data", {}).get("data", {}).get("mainTaskId")
            self.assert_util.assert_by_operator(self.export_task_id, "!=", None)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试删除文本类型",
        description="验证删除文本类型功能",
        severity="normal",
        order=5,
        tags=["文本类型", "删除"]
    )
    def test_delete_text_type(self):
        """删除文本类型用例"""
        try:
            if not self.text_type_id:
                self.test_save_text_type()

            api_path = self.get_api_path("GEN-文本类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.text_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # # ============= 文本组管理 =============
    @case_decorator(
        story="文本管理",
        title="测试新增文本组",
        description="验证新增文本组功能",
        severity="normal",
        order=6,
        tags=["文本组", "新增"]
    )
    def test_save_text_group(self):
        """新增文本组用例"""
        try:
            if not self.text_type_id:
                self.test_save_text_type()

            code = self.mock_util.generate_unique_code(tag="TXTGROUP")
            name = f"文本组_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-文本组-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["code", "name", "itemList"],
                ["params", "request"]
            )
            set_dict = {
                "code": code,
                "name": name,
                "itemList": [
                    {
                        "id": self.text_type_id,
                        "isRequired": False
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.text_group_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本组分页",
        description="验证文本组分页查询功能",
        severity="normal",
        order=7,
        tags=["文本组", "查询"]
    )
    def test_query_text_group_page(self):
        """查询文本组分页用例"""
        try:
            api_path = self.get_api_path("GEN-文本组-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            set_dict =  {
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
   
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本组详情",
        description="验证文本组详情查询功能",
        severity="normal",
        order=8,
        tags=["文本组", "详情"]
    )
    def test_query_text_group_detail(self):
        """查询文本组详情用例"""
        try:
            
            if not self.text_group_id:
                self.test_save_text_group()

            api_path = self.get_api_path("GEN-文本组-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.text_group_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试提交文本组导出任务",
        description="验证提交文本组导出任务功能",
        severity="normal",
        order=9,
        tags=["文本组", "导出任务"]
    )
    def test_submit_text_group_export_task(self):
        """提交文本组导出任务用例"""
        try:
            api_path = self.get_api_path("文本组-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params = {
                "serviceKey": "GEN_MD$GEN_TEXT_PROCEDURE_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"文本组导出-{self.nickname}-{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_text_procedure_head_cf",
                            "modelName": "文本组",
                            "sheetNo": 0,
                            "sheetName": "文本组",
                            "headerConfigList": [
                                {
                                    "name": "文本组编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "文本组名称",
                                    "type": "TEXT",
                                    "field": "name"
                                },
                                {
                                    "name": "创建时间",
                                    "type": "DATE",
                                    "field": "createdAt"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$GEN_TEXT_GROUP_VIEW-table-container-GEN_MD$gen_text_procedure_head_cf",
                        "viewKey": "GEN_MD$GEN_TEXT_GROUP_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_TEXT_GROUP_VIEW",
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
                                    "field": "createdAt"
                                }
                            ],
                            "modelKey": "GEN_MD$gen_text_procedure_head_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_text_procedure_head_cf",
                        "modelName": "文本组",
                        "containerKey": "GEN_MD$GEN_TEXT_GROUP_VIEW-table-container-GEN_MD$gen_text_procedure_head_cf",
                        "viewKey": "GEN_MD$GEN_TEXT_GROUP_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_TEXT_GROUP_VIEW"
                    }
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
        story="文本管理",
        title="测试删除文本组",
        description="验证删除文本组功能",
        severity="normal",
        order=10,
        tags=["文本组", "删除"]
    )
    def test_delete_text_group(self):
        """删除文本组用例"""
        try:
            if not self.text_group_id:
                self.test_save_text_group()

            api_path = self.get_api_path("GEN-文本组-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.text_group_id}
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
        story="文本管理",
        title="测试文本类型标准导出",
        description="验证文本类型标准导出功能",
        severity="normal",
        order=11,
        tags=["文本类型", "导出"]
    )
    def test_export_text_type(self):
        """文本类型标准导出用例"""
        try:
            api_path = self.get_api_path("文本类型标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"文本类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "文本类型"
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
        story="文本管理",
        title="测试文本类型标准导入",
        description="验证文本类型标准导入功能",
        severity="normal",
        order=12,
        tags=["文本类型", "导入"]
    )
    def test_import_text_type(self):
        """文本类型标准导入用例"""
        try:
            api_path = self.get_api_path("文本类型标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"文本类型导入_{self.mock_util.get_timestamp()}",
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
        story="文本管理",
        title="测试通过OSS提交文本类型导入任务",
        description="验证通过OSS提交文本类型导入任务功能",
        severity="normal",
        order=13,
        tags=["文本类型", "OSS导入"]
    )
    def test_submit_text_type_import_task_by_oss(self):
        """通过OSS提交文本类型导入任务用例"""
        try:
            api_path = self.get_api_path("文本类型-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"文本类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"text_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "文本类型"
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
        story="文本管理",
        title="测试文本组标准导出",
        description="验证文本组标准导出功能",
        severity="normal",
        order=14,
        tags=["文本组", "导出"]
    )
    def test_export_text_group(self):
        """文本组标准导出用例"""
        try:
            api_path = self.get_api_path("文本组标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"文本组导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "文本组"
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
        story="文本管理",
        title="测试文本组标准导入",
        description="验证文本组标准导入功能",
        severity="normal",
        order=15,
        tags=["文本组", "导入"]
    )
    def test_import_text_group(self):
        """文本组标准导入用例"""
        try:
            api_path = self.get_api_path("文本组标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"文本组导入_{self.mock_util.get_timestamp()}",
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
        story="文本管理",
        title="测试通过OSS提交文本组导入任务",
        description="验证通过OSS提交文本组导入任务功能",
        severity="normal",
        order=16,
        tags=["文本组", "OSS导入"]
    )
    def test_submit_text_group_import_task_by_oss(self):
        """通过OSS提交文本组导入任务用例"""
        try:
            api_path = self.get_api_path("文本组-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"文本组OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"text_group_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "文本组"
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