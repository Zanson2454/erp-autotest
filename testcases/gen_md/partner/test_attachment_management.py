import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("附件管理")
class TestAttachmentManagement(GenMdBaseTest):
    """附件管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("附件管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_attachment_type(self):
        attachment_code = self.mock_util.generate_unique_code(tag="ATT")
        attachment_name = f"附件类型_{self.mock_util.get_timestamp()}"
        set_dict = {
            "attachmentCode": attachment_code,
            "attachmentName": attachment_name,
            "btClass": "SLS",
            "desc": f"自动化测试附件类型-{self.mock_util.get_timestamp()}",
            "url": "https://www.baidu.com",
        }
        response, extracted_id = self.standard_api_call(
            api_key="GEN-附件类型-保存服务",
            set_dict=set_dict,
            fields_to_filter=["attachmentCode", "attachmentName", "btClass", "desc", "url"],
            store_id_as="attachment_type",
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("attachment_type", extracted_id)
        return extracted_id

    def _ensure_save_attachment_type(self):
        attachment_type_id = self.get_runtime_id("attachment_type")
        if attachment_type_id:
            return attachment_type_id
        return self._create_attachment_type()

    def _create_attachment_group(self):
        attachment_type_id = self._ensure_save_attachment_type()
        code = self.mock_util.generate_unique_code(tag="ATTG")
        name = f"附件组_{self.mock_util.get_timestamp()}"
        set_dict = {
            "code": code,
            "name": name,
            "itemList": [{"attachmentType": {"id": attachment_type_id}, "isRequired": False}],
        }
        response, extracted_id = self.standard_api_call(
            api_key="GEN-附件组-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "itemList"],
            store_id_as="attachment_group",
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("attachment_group", extracted_id)
        return extracted_id

    def _ensure_save_attachment_group(self):
        attachment_group_id = self.get_runtime_id("attachment_group")
        if attachment_group_id:
            return attachment_group_id
        return self._create_attachment_group()

    @case_decorator(
        story="附件管理",
        title="测试新增附件类型",
        description="验证新增附件类型功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["附件类型", "新增"]
    )
    def test_save_attachment_type(self):
        """新增附件类型用例"""
        try:
            attachment_type_id = self._create_attachment_type()
            a.json({"attachment_type_id": attachment_type_id}, "新增附件类型结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试查询附件类型分页",
        description="验证附件类型分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["附件类型", "查询"]
    )
    def test_query_attachment_type_page(self):
        """查询附件类型分页用例"""
        try:
            # 调用查询接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "attachmentCode", "type": "TEXT"},
                    {"name": "attachmentName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields","systemParams"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试查询附件类型详情",
        description="验证附件类型详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["附件类型", "详情"]
    )
    def test_query_attachment_type_detail(self):
        """查询附件类型详情用例"""
        try:
            attachment_type_id = self._ensure_save_attachment_type()

            # 调用详情查询接口
            set_dict = {"id": attachment_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试删除附件类型",
        description="验证删除附件类型功能",
        severity="normal",
        file_level_order=4,
        tags=["附件类型", "删除"]
    )
    def test_delete_attachment_type(self):
        """删除附件类型用例"""
        try:
            attachment_type_id = self._ensure_save_attachment_type()

            # 调用删除接口
            set_dict = {"id": attachment_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试提交附件类型导出任务",
        description="验证提交附件类型导出任务功能",
        severity="normal",
        file_level_order=5,
        tags=["附件类型", "导出任务"]
    )
    def test_submit_attachment_type_export_task(self):
        """提交附件类型导出任务用例"""
        try:
            export_params = {
                "taskName": f"附件类型-章昂-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_attachment_type_cf",
                        "modelName": "附件类型",
                        "sheetNo": 0,
                        "sheetName": "附件类型",
                        "headerConfigList": [
                            {
                                "name": "附件编码",
                                "type": "TEXT",
                                "field": "attachmentCode"
                            },
                            {
                                "name": "附件名称",
                                "type": "TEXT",
                                "field": "attachmentName"
                            },
                            {
                                "name": "业务类别",
                                "type": "ENUM",
                                "field": "btClass",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "label": "销售",
                                        "value": "SLS"
                                    },
                                    {
                                        "label": "采购",
                                        "value": "PUR"
                                    }
                                ]
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
                    "containerKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW-table-container-GEN_MD$gen_attachment_type_cf",
                    "viewKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
        
                            }
                        },
                        "selectFields": [
                            {
                                "field": "attachmentCode"
                            },
                            {
                                "field": "attachmentName"
                            },
                            {
                                "field": "btClass"
                            },
                            {
                                "field": "desc"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_attachment_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_attachment_type_cf",
                    "modelName": "附件类型",
                    "containerKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW-table-container-GEN_MD$gen_attachment_type_cf",
                    "viewKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_ATTACHMENT_TYPE_VIEW"
                }
            }

            response, _ = self.standard_api_call(
                api_key="附件类型-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 附件组管理 =============
    @case_decorator(
        story="附件管理",
        title="测试新增附件组",
        description="验证新增附件组功能",
        severity="normal",
        file_level_order=6,
        tags=["附件组", "新增"]
    )
    def test_save_attachment_group(self):
        """新增附件组用例"""
        try:
            attachment_group_id = self._create_attachment_group()
            a.json({"attachment_group_id": attachment_group_id}, "新增附件组结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试查询附件组分页",
        description="验证附件组分页查询功能",
        severity="normal",
        file_level_order=7,
        tags=["附件组", "查询"]
    )
    def test_query_attachment_group_page(self):
        """查询附件组分页用例"""
        try:
            # 调用查询接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "groupCode", "type": "TEXT"},
                    {"name": "groupName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields","systemParams"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件组-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试查询附件组详情",
        description="验证附件组详情查询功能",
        severity="normal",
        file_level_order=8,
        tags=["附件组", "详情"]
    )
    def test_query_attachment_group_detail(self):
        """查询附件组详情用例"""
        try:
            attachment_group_id = self._ensure_save_attachment_group()

            # 调用详情查询接口
            set_dict = {"id": attachment_group_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件组-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试删除附件组",
        description="验证删除附件组功能",
        severity="normal",
        file_level_order=9,
        tags=["附件组", "删除"]
    )
    def test_delete_attachment_group(self):
        """删除附件组用例"""
        try:
            attachment_group_id = self._ensure_save_attachment_group()

            # 调用删除接口
            set_dict = {"id": attachment_group_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-附件组-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="附件管理",
        title="测试提交附件组导出任务",
        description="验证提交附件组导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["附件组", "导出任务"]
    )
    def test_submit_attachment_group_export_task(self):
        """提交附件组导出任务用例"""
        try:
            export_params = {
                "taskName": f"附件组-章昂-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_attachment_procedure_head_cf",
                        "modelName": "附件组",
                        "sheetNo": 0,
                        "sheetName": "附件组",
                        "headerConfigList": [
                            {
                                "name": "附件组编码",
                                "type": "TEXT",
                                "field": "code"
                            },
                            {
                                "name": "附件组名称",
                                "type": "TEXT",
                                "field": "name"
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
                    "containerKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW-table-container-GEN_MD$gen_attachment_procedure_head_cf",
                    "viewKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW",
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
                                "field": "updatedAt"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_attachment_procedure_head_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_attachment_procedure_head_cf",
                    "modelName": "附件组",
                    "containerKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW-table-container-GEN_MD$gen_attachment_procedure_head_cf",
                    "viewKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_ATTACHMENT_GROUP_VIEW"
                }
            }

            response, _ = self.standard_api_call(
                api_key="附件组-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="附件管理",
        title="测试附件类型标准导出",
        description="验证附件类型标准导出功能",
        severity="normal",
        file_level_order=11,
        tags=["附件类型", "导出"]
    )
    def test_export_attachment_type(self):
        """附件类型标准导出用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fileName": f"附件类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "附件类型",
                    "format": "EXCEL"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件类型标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="附件管理",
        title="测试附件类型标准导入",
        description="验证附件类型标准导入功能",
        severity="normal",
        file_level_order=12,
        tags=["附件类型", "导入"]
    )
    def test_import_attachment_type(self):
        """附件类型标准导入用例"""
        try:
            set_dict = {
                "importConfig": {
                    "fileName": f"附件类型导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL",
                    "sheetName": "附件类型"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件类型标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="附件管理",
        title="测试通过OSS提交附件类型导入任务",
        description="验证通过OSS提交附件类型导入任务功能",
        severity="normal",
        file_level_order=13,
        tags=["附件类型", "OSS导入"]
    )
    def test_submit_attachment_type_import_task_by_oss(self):
        """通过OSS提交附件类型导入任务用例"""
        try:
            set_dict = {
                "taskName": f"附件类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"attachment_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "附件类型"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件类型-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "ossConfig", "importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="附件管理",
        title="测试附件组标准导出",
        description="验证附件组标准导出功能",
        severity="normal",
        file_level_order=14,
        tags=["附件组", "导出"]
    )
    def test_export_attachment_group(self):
        """附件组标准导出用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fileName": f"附件组导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "附件组",
                    "format": "EXCEL"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件组标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="附件管理",
        title="测试附件组标准导入",
        description="验证附件组标准导入功能",
        severity="normal",
        file_level_order=15,
        tags=["附件组", "导入"]
    )
    def test_import_attachment_group(self):
        """附件组标准导入用例"""
        try:
            set_dict = {
                "importConfig": {
                    "fileName": f"附件组导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL",
                    "sheetName": "附件组"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件组标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="附件管理",
        title="测试通过OSS提交附件组导入任务",
        description="验证通过OSS提交附件组导入任务功能",
        severity="normal",
        file_level_order=16,
        tags=["附件组", "OSS导入"]
    )
    def test_submit_attachment_group_import_task_by_oss(self):
        """通过OSS提交附件组导入任务用例"""
        try:
            set_dict = {
                "taskName": f"附件组OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"attachment_group_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "附件组"
                }
            }
            response, _ = self.standard_api_call(
                api_key="附件组-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "ossConfig", "importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 
