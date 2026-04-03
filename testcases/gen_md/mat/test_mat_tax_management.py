import allure
import pytest

from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("物料税分类管理")
class TestMatTaxManagement(GenMdBaseTest):
    """物料税分类管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("物料税分类管理测试类初始化完成")
        country_info = cls.init_data.get("country_info")
        cls.counId = country_info[0].get("coun_id") if country_info else None

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="物料税分类管理",
        title="测试新增物料税分类",
        description="验证新增物料税分类功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["物料税分类管理", "新增"]
    )
    def test_save_mat_tax(self):
        """
        新增物料税分类用例
        """
        try:
            self._create_mat_tax()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def _create_mat_tax(self):
        mat_tax_code = self.mock_util.generate_unique_code(tag="MatTax")
        set_dict = {
            "taxClassCode": mat_tax_code,
            "taxClassDesc": f"自动化测试物料税分类-{self.mock_util.get_timestamp()}",
            "counId": {"id": self.counId}
        }
        fields_to_filter = ["taxClassCode", "taxClassDesc", "counId"]
        response, extracted_id = self.standard_api_call(
            api_key="GEN-物料税分类-保存服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as="mat_tax"
        )
        self.set_runtime_id("mat_tax", extracted_id)
        self.test_data["mat_tax_code"] = mat_tax_code
        self.assert_util.assert_response_data(response)
        return extracted_id

    def _ensure_save_mat_tax(self):
        mat_tax_id = self.get_runtime_id("mat_tax")
        if mat_tax_id:
            return mat_tax_id
        return self._create_mat_tax()

    @case_decorator(
        story="物料税分类管理",
        title="测试查询物料税分类分页",
        description="验证物料税分类分页查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["物料税分类管理", "查询"]
    )
    def test_query_mat_tax_page(self):
        """
        查询物料税分类分页用例
        """
        try:
            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "matTaxCode", "type": "TEXT"},
                    {"name": "matTaxName", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料税分类-查询分页服务",
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
        story="物料税分类管理",
        title="测试查询物料税分类详情",
        description="验证物料税分类详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["物料税分类管理", "详情"]
    )
    def test_query_mat_tax_detail(self):
        """
        查询物料税分类详情用例
        """
        try:
            mat_tax_id = self._ensure_save_mat_tax()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": mat_tax_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料税分类-查询详情服务",
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

    @pytest.mark.skip(reason="实际业务未调用")
    @case_decorator(
        story="物料税分类管理",
        title="测试物料税分类标准导出",
        description="验证物料税分类标准导出功能",
        severity="normal",
        file_level_order=4,
        tags=["物料税分类管理", "导出"]
    )
    def test_export_mat_tax(self):
        """
        物料税分类标准导出用例
        """
        try:
            api_path = self.get_api_path("物料税分类标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料税分类导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料税分类"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="物料税分类标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"],
                store_id_as=None
            )
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="物料税分类管理",
        title="测试提交物料税分类导出任务",
        description="验证提交物料税分类导出任务功能",
        severity="normal",
        file_level_order=7,
        tags=["物料税分类管理", "导出任务"]
    )
    @pytest.mark.skip(reason="业务不存在该场景，暂时跳过")
    def test_submit_export_task(self):
        """
        提交物料税分类导出任务用例
        """
        try:
            api_path = self.get_api_path("物料税分类-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params = {
                "serviceKey": "GEN_MD$GEN_MAT_TAX_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"物料税分类-自动化测试-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_mat_tax_type_cf",
                            "modelName": "物料税分类",
                            "sheetNo": 0,
                            "sheetName": "物料税分类",
                            "headerConfigList": [
                                {
                                    "name": "物料税分类编码",
                                    "type": "TEXT",
                                    "field": "taxClassCode"
                                },
                                {
                                    "name": "国家",
                                    "type": "TEXT",
                                    "field": "counId.counName"
                                },
                                {
                                    "name": "物料分类描述",
                                    "type": "TEXT",
                                    "field": "taxClassDesc"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$GEN_MAT_TAX_VIEW-table-container-GEN_MD$gen_mat_tax_type_cf",
                        "viewKey": "GEN_MD$GEN_MAT_TAX_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_TAX_VIEW",
                        "params": {
                            "request": {
                                "pageable": {}
                            },
                            "selectFields": [
                                {"field": "taxClassCode"},
                                {"field": "taxClassDesc"},
                                {
                                    "field": "counId",
                                    "selectFields": [
                                        {"field": "counName"}
                                    ]
                                }
                            ],
                            "modelKey": "GEN_MD$gen_mat_tax_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_mat_tax_type_cf",
                        "modelName": "物料税分类",
                        "containerKey": "GEN_MD$GEN_MAT_TAX_VIEW-table-container-GEN_MD$gen_mat_tax_type_cf",
                        "viewKey": "GEN_MD$GEN_MAT_TAX_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_TAX_VIEW"
                    }
                }
            }
            self.logger.info(f"请求参数: {self.admin_headers}")
            response, _ = self.standard_api_call(
                api_key="物料税分类-导入导出任务管理接口-提交导出任务",
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
        story="物料税分类管理",
        title="测试删除物料税分类",
        description="验证删除物料税分类功能",
        severity="normal",
        file_level_order=9,
        tags=["物料税分类管理", "删除"]
    )
    def test_delete_mat_tax(self):
        """
        删除物料税分类用例
        """
        try:
            mat_tax_id = self._ensure_save_mat_tax()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": mat_tax_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料税分类-删除服务",
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
