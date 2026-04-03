import allure
import pytest

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("文本管理")
class TestTextManagement(GenMdBaseTest):
    """文本管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.text_type_id = None
        cls.text_group_id = None
        cls.logger.info("文本管理测试类初始化完成")
        
        cls.call_times=0
        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    @case_decorator(
        story="文本管理",
        title="测试新增文本类型",
        description="验证新增文本类型功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["文本类型", "新增"]
    )
    def test_save_text_type(self):
        """新增文本类型用例"""
        try:
            # 每次都生成新的唯一标识，避免重复键错误
            text_code = self.mock_util.generate_unique_code(tag="TXT")
            text_name = f"文本类型_{self.mock_util.get_timestamp()}"

            set_dict = {
                "textCode": text_code,
                "textName": text_name,
                "btClass": 'SLS',
                "desc": f"自动化文本-{self.mock_util.get_timestamp()}"
            }
            fields_to_filter = ["textCode", "textName", "btClass", "desc"]

            response, extracted_id = self.standard_api_call(
                api_key="GEN-文本类型-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 赋值
            self.text_type_id  = response.get("data", {}).get("data", {})
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本类型分页",
        description="验证文本类型分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["文本类型", "查询"]
    )
    def test_query_text_type_page(self):
        """查询文本类型分页用例"""
        try:
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
            fields_to_filter = ["pageable", "fields", "systemParams"]

            response, _ = self.standard_api_call(
                api_key="GEN-文本类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本类型详情",
        description="验证文本类型详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["文本类型", "详情"]
    )
    def test_query_text_type_detail(self):
        """查询文本类型详情用例"""
        try:
            if not self.text_type_id:
                self._ensure_save_text_type()

            set_dict = {"id": self.text_type_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-文本类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试提交文本类型导出任务",
        description="验证提交文本类型导出任务功能",
        severity="normal",
        file_level_order=4,
        tags=["文本类型", "导出任务"]
    )
    def test_submit_text_type_export_task(self):
        """提交文本类型导出任务用例"""
        try:
            export_params = {
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

            response, _ = self.standard_api_call(
                api_key="文本类型-导入导出任务管理接口-提交导出任务",
                set_dict=export_params.get("params", {}),
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            self.export_task_id = response.get("data", {}).get("data", {}).get("mainTaskId")
            self.assert_util.assert_by_operator(self.export_task_id, "!=", None)

            a.json(export_params.get("params", {}), "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试删除文本类型",
        description="验证删除文本类型功能",
        severity="normal",
        file_level_order=5,
        tags=["文本类型", "删除"]
    )
    def test_delete_text_type(self):
        """删除文本类型用例"""
        try:
            if not self.text_type_id:
                self._ensure_save_text_type()

            set_dict = {"id": self.text_type_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-文本类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
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
        file_level_order=6,
        tags=["文本组", "新增"]
    )
    def test_save_text_group(self):
        """新增文本组用例"""
        try:
            if not self.text_type_id:
                self._ensure_save_text_type()

            code = self.mock_util.generate_unique_code(tag="TXTGROUP")
            name = f"文本组_{self.mock_util.get_timestamp()}"

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
            fields_to_filter = ["code", "name", "itemList"]

            response, extracted_id = self.standard_api_call(
                api_key="GEN-文本组-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            self.text_group_id = response.get("data", {}).get("data", {})
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本组分页",
        description="验证文本组分页查询功能",
        severity="normal",
        file_level_order=7,
        tags=["文本组", "查询"]
    )
    def test_query_text_group_page(self):
        """查询文本组分页用例"""
        try:
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
            fields_to_filter = ["pageable", "fields", "systemParams"]
   
            response, _ = self.standard_api_call(
                api_key="GEN-文本组-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试查询文本组详情",
        description="验证文本组详情查询功能",
        severity="normal",
        file_level_order=8,
        tags=["文本组", "详情"]
    )
    def test_query_text_group_detail(self):
        """查询文本组详情用例"""
        try:
            
            if not self.text_group_id:
                self._ensure_save_text_group()

            set_dict = {"id": self.text_group_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-文本组-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试提交文本组导出任务",
        description="验证提交文本组导出任务功能",
        severity="normal",
        file_level_order=9,
        tags=["文本组", "导出任务"]
    )
    def test_submit_text_group_export_task(self):
        """提交文本组导出任务用例"""
        try:
            export_params = {
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

            response, _ = self.standard_api_call(
                api_key="文本组-导入导出任务管理接口-提交导出任务",
                set_dict=export_params.get("params", {}),
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(export_params.get("params", {}), "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="文本管理",
        title="测试删除文本组",
        description="验证删除文本组功能",
        severity="normal",
        file_level_order=10,
        tags=["文本组", "删除"]
    )
    def test_delete_text_group(self):
        """删除文本组用例"""
        try:
            if not self.text_group_id:
                self._ensure_save_text_group()

            set_dict = {"id": self.text_group_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-文本组-删除服务",
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
        story="文本管理",
        title="测试文本类型标准导出",
        description="验证文本类型标准导出功能",
        severity="normal",
        file_level_order=11,
        tags=["文本类型", "导出"]
    )
    def test_export_text_type(self):
        """文本类型标准导出用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fileName": f"文本类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "文本类型"
                }
            }
            response, _ = self.standard_api_call(
                api_key="文本类型标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
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
        file_level_order=14,
        tags=["文本组", "导出"]
    )
    def test_export_text_group(self):
        """文本组标准导出用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fileName": f"文本组导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "文本组"
                }
            }
            response, _ = self.standard_api_call(
                api_key="文本组标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


