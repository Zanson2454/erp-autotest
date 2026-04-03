import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("物料价值管理")
class TestMat_ValueManagement(GenMdBaseTest):
    """物料价值管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mat_value_code = None
        if cls.md_cache_data:
            inv_org_info = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])
            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None
            mat_type_info = cls.md_cache_data.get("mat_info",{}).get("mat_type_cf",{}).get("FINP",[])
            cls.mat_type_id = mat_type_info[0].get("id") if mat_type_info else None
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.logger.info("物料价值管理测试类初始化完成")

    def _create_mat_value(self):
        set_dict = {
            "invOrgId": {"id": self.inv_org_id},
            "matTypeId": {"id": self.mat_type_id},
            "matQtyUpdate": True,
            "matValUpdate": False,
        }
        response, extracted_id = self.standard_api_call(
            api_key="GEN-物料价值数量配置-保存服务",
            set_dict=set_dict,
            fields_to_filter=["invOrgId", "matTypeId", "matQtyUpdate", "matValUpdate"],
            store_id_as="mat_value",
        )
        self.assert_util.assert_response_success(response)
        self.set_runtime_id("mat_value", extracted_id)
        return extracted_id

    def _ensure_save_mat_value(self):
        mat_value_id = self.get_runtime_id("mat_value")
        if mat_value_id:
            return mat_value_id
        mat_value_id = self.query_service.get_inv_org_mat_type_link_id(
            self.mat_type_id,
            self.inv_org_id,
        )
        if mat_value_id:
            self.set_runtime_id("mat_value", mat_value_id)
            return mat_value_id
        return self._create_mat_value()

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行数据初始化
        如果不存在物料价值管理数据则插入默认数据
        """
        try:
            # 检查是否存在数据
            mat_value_id = cls.query_service.get_inv_org_mat_type_link_id(
                cls.mat_type_id,
                cls.inv_org_id,
                deleted=0,
            )
            if not mat_value_id:
                cls.db.insert(
                    table="gen_inv_org_mat_type_link_cf",
                    data={
                        "mat_type_id": cls.mat_type_id,
                        "inv_org_id": cls.inv_org_id,
                        "mat_qty_update": True,
                        "mat_val_update": True,
                        "created_by": cls.user_id,
                        "created_at": cls.mock_util.get_timestamp(),
                        "updated_by": cls.user_id,
                        "updated_at": cls.mock_util.get_timestamp()
                    }
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

        super().teardown_class()
    @case_decorator(
        story="物料价值管理",
        title="测试新增物料价值管理",
        description="验证新增物料价值管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["物料价值管理", "新增"]
    )
    def test_save_mat_value(self):
        """
        新增物料价值管理用例
        """
        try:
            mat_value_id = self._ensure_save_mat_value()
            a.json({"mat_value_id": mat_value_id}, "物料价值ID")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试查询物料价值管理列表",
        description="验证物料价值管理列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["物料价值管理", "查询"]
    )
    def test_query_mat_value_list(self):
        """
        查询物料价值管理列表用例
        """
        try:
            # 1. 准备测试数据（业务逻辑保持不变）
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
                        "name": "invOrgId",
                        "type": "OBJECT"
                    },
                    {
                        "name": "matTypeId",
                        "type": "OBJECT"
                    }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料价值数量配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试查询物料价值管理详情",
        description="验证物料价值管理详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["物料价值管理", "查询"]
    )
    def test_query_mat_value_detail(self):
        """
        查询物料价值管理详情用例
        """
        try:
            mat_value_id = self._ensure_save_mat_value()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": mat_value_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料价值数量配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置标准导出",
        description="验证物料数量价值更新配置标准导出服务功能",
        severity="normal",
        file_level_order=4,
        tags=["物料价值管理", "标准导出", "GEN_INV_ORG_MAT_TYPE_LINK_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出需要复杂配置，暂时跳过")
    def test_export_mat_value(self):
        """
        物料价值数量配置标准导出用例 - GEN_INV_ORG_MAT_TYPE_LINK_CF_GEI_EXPORT_SERVICE
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "matTypeId", "type": "OBJECT"},
                    {"name": "matQtyUpdate", "type": "BOOLEAN"},
                    {"name": "matValUpdate", "type": "BOOLEAN"},
                    {"name": "updatedAt", "type": "DATE"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="物料数量价值更新配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["sliceData"],
                store_id_as=None
            )
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置标准导入",
        description="验证物料数量价值更新配置标准导入服务功能",
        severity="normal",
        file_level_order=5,
        tags=["物料价值管理", "标准导入", "GEN_INV_ORG_MAT_TYPE_LINK_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_import_mat_value(self):
        """
        物料价值数量配置标准导入用例 - GEN_INV_ORG_MAT_TYPE_LINK_CF_GEI_IMPORT_SERVICE
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "invOrgId": {"id": self.inv_org_id},
                    "matTypeId": {"id": self.mat_type_id},
                    "matQtyUpdate": True,
                    "matValUpdate": True
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sliceData"], ["params", "request"]
            )
            set_dict = {"sliceData": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="物料数量价值更新配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["sliceData"],
                store_id_as=None
            )
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置导出任务",
        description="验证物料数量价值更新配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=6,
        tags=["物料价值管理", "导出任务", "GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_export_task(self):
        """
        提交物料价值数量配置导出任务用例
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params={
                "serviceKey": "GEN_MD$GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"物料数量价值配置-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_inv_org_mat_type_link_cf",
                            "modelName": "物料数量价值更新配置",
                            "sheetNo": 0,
                            "sheetName": "物料数量价值更新配置",
                            "headerConfigList": [
                                {
                                    "name": "库存组织",
                                    "type": "TEXT",
                                    "field": "invOrgId.orgName"
                                },
                                {
                                    "name": "物料类型",
                                    "type": "TEXT",
                                    "field": "matTypeId.matTypeName"
                                },
                                {
                                    "name": "是否数量更新",
                                    "type": "BOOL",
                                    "field": "matQtyUpdate"
                                },
                                {
                                    "name": "是否价值更新",
                                    "type": "BOOL",
                                    "field": "matValUpdate"
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
                        "containerKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW-table-container-GEN_MD$gen_inv_org_mat_type_link_cf",
                        "viewKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "matQtyUpdate"
                                },
                                {
                                    "field": "matValUpdate"
                                },
                                {
                                    "field": "updatedAt"
                                },
                                {
                                    "field": "invOrgId",
                                    "selectFields": [
                                        {
                                            "field": "orgName"
                                        }
                                    ]
                                },
                                {
                                    "field": "matTypeId",
                                    "selectFields": [
                                        {
                                            "field": "matTypeName"
                                        }
                                    ]
                                }
                            ],
                            "modelKey": "GEN_MD$gen_inv_org_mat_type_link_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_inv_org_mat_type_link_cf",
                        "modelName": "物料数量价值更新配置",
                        "containerKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW-table-container-GEN_MD$gen_inv_org_mat_type_link_cf",
                        "viewKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW"
                    }
                }
            }
            response, _ = self.standard_api_call(
                api_key="物料数量价值更新配置-导入导出任务管理接口-提交导出任务",
                set_dict=params["params"],
                fields_to_filter=list(params["params"].keys()),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置OSS导入任务",
        description="验证物料数量价值更新配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=7,
        tags=["物料价值管理", "OSS导入任务", "GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_oss_import_task(self):
        """
        物料价值数量配置OSS导入任务用例 - GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 构造OSS导入任务参数
            params = {
                "serviceKey": "GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"物料价值配置_{self.nickname}_{self.mock_util.get_timestamp()}_OSS导入",
                    "fileKey": "test_mat_value_import.xlsx",
                    "fileName": "物料价值配置导入模板.xlsx",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_inv_org_mat_type_link_cf",
                            "modelName": "物料数量价值更新配置",
                            "sheetNo": 0,
                            "sheetName": "物料数量价值更新配置"
                        }
                    ],
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_inv_org_mat_type_link_cf",
                        "modelName": "物料数量价值更新配置"
                    }
                }
            }

            response, _ = self.standard_api_call(
                api_key="物料数量价值更新配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params["params"],
                fields_to_filter=list(params["params"].keys()),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试删除物料价值管理",
        description="验证删除物料价值管理功能",
        severity="normal",
        file_level_order=8,
        smoke=True,
        tags=["物料价值管理", "删除"]
    )
    def test_delete_mat_value(self):
        """
        删除物料价值管理用例
        """
        try:
            mat_value_id = self._ensure_save_mat_value()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": mat_value_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料价值数量配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
