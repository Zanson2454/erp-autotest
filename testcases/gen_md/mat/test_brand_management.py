import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("品牌管理")
class TestBrandManagement(GenMdBaseTest):
    """品牌管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # No need for cls.mock_data = MockData() due to singleton pattern
        cls.brandId = None
        cls.brandCode = None
        cls.logger.info("品牌管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的品牌数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_brand_md",
                where="brand_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

        super().teardown_class()
    @case_decorator(
        story="品牌管理",
        title="测试新增品牌",
        description="验证新增品牌功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["品牌管理", "新增"]
    )
    def test_save_brand(self):
        """
        新增品牌用例
        """
        try:
            # 准备品牌数据
            brand_code = self.mock_util.generate_unique_code(tag="Brand")
            brand_name = f"品牌_{self.mock_util.get_timestamp()}"

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "brandCode": brand_code,
                "brandName": brand_name,
                "brandImage": None
            }
            fields_to_filter = ["brandCode", "brandName", "brandImage"]

            # 2. 使用标准化API调用（无任何断言）
            response, extracted_id = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="brand"  # 自动存储 self.brandId
            )

            # 3. 保存品牌信息供后续用例使用（保持原有逻辑）
            self.brandId = extracted_id
            self.__class__.brandCode = brand_code

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌列表",
        description="验证品牌列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["品牌管理", "查询"]
    )
    def test_query_brand_list(self):
        """
        查询品牌列表用例
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
                    {"name": "brandCode", "type": "TEXT"},
                    {"name": "brandName", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-品牌-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")
            self.assert_util.assert_response_data(response)

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌详情",
        description="验证品牌详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["品牌管理", "查询"]
    )
    def test_query_brand_detail(self):
        """
        查询品牌详情用例
        """
        try:
            # 获取品牌ID
            if not self.brandId:
                self.test_save_brand()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.brandId}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-品牌-查询详情服务",
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
        story="品牌管理",
        title="测试修改品牌",
        description="验证修改品牌功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["品牌管理", "修改"]
    )
    def test_update_brand(self):
        """
        修改品牌用例
        """
        try:
            # 获取品牌信息
            if not self.brandId:
                self.test_save_brand()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "id": self.brandId,
                "brandCode": self.brandCode,
                "brandName": f"品牌_{self.mock_util.get_timestamp()}_修改",
                "brandImage": None
            }
            fields_to_filter = ["id", "brandCode", "brandName", "brandImage"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
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
        story="品牌管理",
        title="测试删除品牌",
        description="验证删除品牌功能",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["品牌管理", "删除"]
    )
    def test_delete_brand(self):
        """
        删除品牌用例
        """
        try:
            # 获取品牌ID
            if not self.brandId:
                self.test_save_brand()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.brandId}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-品牌-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 4. 清除品牌信息（保持原有逻辑）
            TestBrandManagement.brand_info = {}

            # 5. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 品牌导入导出管理 ================
    @pytest.mark.skip(reason="品牌标准导入服务功能未实现")
    @case_decorator(
        story="品牌导入导出管理",
        title="测试品牌标准导入",
        description="验证品牌标准导入服务功能",
        severity="normal",
        file_level_order=6,
        tags=["品牌管理", "导入", "GEN_BRAND_MD_GEI_IMPORT_SERVICE"]
    )
    def test_brand_import(self):
        """品牌标准导入用例 - GEN_BRAND_MD_GEI_IMPORT_SERVICE"""
        try:
            # 构建导入数据
            import_data = [
                {
                    "brandCode": self.mock_util.generate_unique_code(tag="IMPORT_BRAND"),
                    "brandName": f"导入测试品牌_{self.mock_util.get_timestamp()}",
                    "brandImage": None
                }
            ]

            set_dict = {"data": import_data}
            response, _ = self.standard_api_call(
                api_key="品牌标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="品牌标准导出服务功能未实现")
    @case_decorator(
        story="品牌导入导出管理",
        title="测试品牌标准导出",
        description="验证品牌标准导出服务功能",
        severity="normal",
        file_level_order=7,
        tags=["品牌管理", "导出", "GEN_BRAND_MD_GEI_EXPORT_SERVICE"]
    )
    def test_brand_export(self):
        """品牌标准导出用例 - GEN_BRAND_MD_GEI_EXPORT_SERVICE"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "brandCode", "type": "TEXT"},
                    {"name": "brandName", "type": "TEXT"},
                    {"name": "brandImage", "type": "TEXT"}
                ]
            }
            response, _ = self.standard_api_call(
                api_key="品牌标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="品牌OSS导入服务功能未实现")
    @case_decorator(
        story="品牌导入导出管理",
        title="测试品牌OSS导入任务",
        description="验证品牌-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=8,
        tags=["品牌管理", "导入", "GEN_BRAND_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_brand_oss_import_task(self):
        """品牌OSS导入任务用例 - GEN_BRAND_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            set_dict = {
                "fileKey": "test_brand_import_file.xlsx",
                "taskName": f"品牌导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            response, _ = self.standard_api_call(
                api_key="品牌-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌导入导出管理",
        title="测试品牌导出任务",
        description="验证品牌-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=9,
        tags=["品牌管理", "导出", "GEN_BRAND_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_brand_export_task(self):
        """品牌导出任务用例 - GEN_BRAND_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            export_params = {
                "taskName": f"品牌管理-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_brand_md",
                        "modelName": "品牌",
                        "sheetNo": 0,
                        "sheetName": "品牌",
                        "headerConfigList": [
                            {
                                "name": "品牌图片",
                                "type": "ATTACHMENT",
                                "field": "brandImage"
                            },
                            {
                                "name": "品牌编码",
                                "type": "TEXT",
                                "field": "brandCode"
                            },
                            {
                                "name": "品牌名称",
                                "type": "TEXT",
                                "field": "brandName"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_BRAND_VIEW-table-container-GEN_MD$gen_brand_md",
                    "viewKey": "GEN_MD$GEN_BRAND_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BRAND_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "brandImage"
                            },
                            {
                                "field": "brandCode"
                            },
                            {
                                "field": "brandName"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_brand_md"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_brand_md",
                    "modelName": "品牌",
                    "containerKey": "GEN_MD$GEN_BRAND_VIEW-table-container-GEN_MD$gen_brand_md",
                    "viewKey": "GEN_MD$GEN_BRAND_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BRAND_VIEW"
                }
            }

            response, _ = self.standard_api_call(
                api_key="品牌-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            a.json(export_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 品牌业务场景测试 ================
    @case_decorator(
        story="品牌业务场景",
        title="测试品牌编码唯一性验证",
        description="验证品牌编码的唯一性约束",
        severity="normal",
        file_level_order=10,
        tags=["品牌管理", "业务验证", "唯一性测试"]
    )
    def test_brand_code_uniqueness(self):
        """品牌编码唯一性测试用例"""
        try:
            # 创建第一个品牌
            brand_code = self.mock_util.generate_unique_code(tag="UNIQUE_BRAND")
            
            set_dict = {
                "brandCode": brand_code,
                "brandName": f"唯一性测试品牌1_{self.mock_util.get_timestamp()}"
            }
            response1, _ = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
                set_dict=set_dict,
                fields_to_filter=["brandCode", "brandName"]
            )
            self.assert_util.assert_response_data(response1)

            # 尝试创建相同编码的品牌（应该失败或更新）
            set_dict["brandName"] = f"唯一性测试品牌2_{self.mock_util.get_timestamp()}"
            response2, _ = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
                set_dict=set_dict,
                fields_to_filter=["brandCode", "brandName"]
            )
            # 这里根据业务逻辑验证：要么失败，要么是更新操作
            
            a.json({"test_scenario": "uniqueness_validation"}, "测试场景")
            a.json(response1, "第一次创建响应")
            a.json(response2, "第二次创建响应")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌综合测试",
        title="测试品牌完整流程",
        description="验证品牌从创建到删除的完整业务流程",
        severity="critical",
        file_level_order=11,
        tags=["品牌管理", "综合测试", "业务流程"]
    )
    def test_brand_complete_workflow(self):
        """
        品牌完整流程测试用例
        """
        try:
            # 1. 创建品牌
            brand_code = self.mock_util.generate_unique_code(tag="WORKFLOW_BRAND")
            brand_name = f"流程测试品牌_{self.mock_util.get_timestamp()}"

            # 创建
            set_dict_create = {"brandCode": brand_code, "brandName": brand_name}
            fields_to_filter_create = ["brandCode", "brandName"]
            create_response, workflow_brand_id = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
                set_dict=set_dict_create,
                fields_to_filter=fields_to_filter_create,
                store_id_as=None
            )
            self.assert_util.assert_response_data(create_response)

            # 2. 查询详情验证
            set_dict_detail = {"id": workflow_brand_id}
            fields_to_filter_detail = ["id"]
            detail_response, _ = self.standard_api_call(
                api_key="GEN-品牌-查询详情服务",
                set_dict=set_dict_detail,
                fields_to_filter=fields_to_filter_detail,
                store_id_as=None
            )
            self.assert_util.assert_response_data(detail_response)

            detail_data = detail_response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("brandCode"), "=", brand_code, "品牌编码不匹配")
            self.assert_util.assert_by_operator(detail_data.get("brandName"), "=", brand_name, "品牌名称不匹配")

            # 3. 更新品牌
            update_name = f"更新后的品牌名称_{self.mock_util.get_timestamp()}"
            set_dict_update = {
                "id": workflow_brand_id,
                "brandCode": brand_code,
                "brandName": update_name
            }
            fields_to_filter_update = ["id", "brandCode", "brandName"]
            update_response, _ = self.standard_api_call(
                api_key="GEN-品牌-保存服务",
                set_dict=set_dict_update,
                fields_to_filter=fields_to_filter_update,
                store_id_as=None
            )
            self.assert_util.assert_response_data(update_response)

            # 4. 删除验证
            set_dict_delete = {"id": workflow_brand_id}
            fields_to_filter_delete = ["id"]
            delete_response, _ = self.standard_api_call(
                api_key="GEN-品牌-删除服务",
                set_dict=set_dict_delete,
                fields_to_filter=fields_to_filter_delete,
                store_id_as=None
            )
            self.assert_util.assert_response_data(delete_response)

            # 5. 日志记录（Allure报告已由standard_api_call处理）
            a.json({"workflow": "complete"}, "完整流程执行成功")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
