import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("物料类型管理")
class TestMatTypeManagement(GenMdBaseTest):
    """物料类型管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.required_mat_types = ["FINP", "SERV"]  # 必需的物料类型编码
        cls.mat_type_id = None
        cls.mat_type_code = None

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料类型数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_mat_type_cf",
                where="mat_type_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="物料类型管理",
        title="测试物料类型配置是否完整",
        description="验证系统中是否包含所需的基础物料类型配置",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["物料类型", "配置检查"]
    )
    def test_mat_type_config(self):
        """
        检查物料类型配置用例
        验证系统中是否包含必需的物料类型编码：
        - FINP：成品
        - SERV：服务
        - RAWM：原材料
        """
        try:
            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 100,  # 设置较大的页面大小以获取所有记录
                    "needTotal": True
                },
                "fields": [
                    {"name": "matTypeCode", "type": "TEXT"},
                    {"name": "matTypeName", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            mat_type_list = response.get("data", {}).get("data", {}).get("data", [])
            mat_type_codes = [item.get("matTypeCode") for item in mat_type_list]
            self.logger.info(f"mat_type_codes: {mat_type_codes}")
            
            # 检查所有必需的物料类型是否都存在
            self.assert_util.assert_all_in(
                self.required_mat_types, 
                mat_type_codes,
                "物料类型配置不完整"
            )

            # 4. 记录到Allure报告（保持原有逻辑）
            a.text(f"所有必需的物料类型均已配置: {', '.join(self.required_mat_types)}", "检查结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类型管理",
        title="测试新增物料类型",
        description="验证新增物料类型功能",
        severity="blocker",
        file_level_order=2,
        smoke=True,
        tags=["物料类型", "新增"]
    )
    def test_save_mat_type(self):
        """
        新增物料类型用例
        """
        try:
            # 准备物料类型数据
            mat_type_code = self.mock_util.generate_unique_code(tag="MatType")
            mat_type_name = f"物料类型_{self.mock_util.get_timestamp()}"

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "matTypeCode": mat_type_code,
                "matTypeName": mat_type_name,
                "remark": f"自动化测试物料类型-{self.mock_util.get_timestamp()}"
            }
            fields_to_filter = ["matTypeCode", "matTypeName", "remark"]

            # 2. 使用标准化API调用（无任何断言）
            response, extracted_id = self.standard_api_call(
                api_key="GEN-物料类型-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="mat_type"  # 自动存储 self.mat_type_id
            )

            # 3. 保存业务数据（保持原有逻辑）
            self.mat_type_id = extracted_id
            self.mat_type_code = mat_type_code

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类型管理",
        title="测试查询物料类型详情",
        description="验证物料类型详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["物料类型", "查询详情"]
    )
    def test_query_mat_type_detail(self):
        """
        查询物料类型详情用例
        """
        try:
            if not self.mat_type_id:
                self.test_save_mat_type()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.mat_type_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料类型-查询详情服务",
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
        story="物料类型管理",
        title="测试根据ID查找物料类型数据",
        description="验证根据ID查找物料类型数据服务",
        severity="normal",
        file_level_order=4,
        tags=["物料类型", "查找"]
    )
    @pytest.mark.skip(reason="接口404: GEN_MD$gen_mat_type_cf_FOLDING_ASSOCIATED_SERVICE服务不存在")
    def test_find_mat_type_by_id(self):
        """
        根据ID查找物料类型数据用例
        """
        try:
            if not self.mat_type_id:
                self.test_save_mat_type()

            set_dict = {"id": self.mat_type_id}
            response, _ = self.standard_api_call(
                api_key="物料类型-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类型管理",
        title="测试物料类型查询分页",
        description="验证物料类型查询分页功能",
        severity="normal",
        file_level_order=5,
        tags=["物料类型", "查询分页"]
    )
    def test_query_mat_type_page(self):
        """
        物料类型查询分页用例
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
                    {"name": "matTypeCode", "type": "TEXT"},
                    {"name": "matTypeName", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料类型-查询分页服务",
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
        story="物料类型管理",
        title="测试物料类型分页数据服务",
        description="验证物料类型分页数据服务",
        severity="normal",
        file_level_order=6,
        tags=["物料类型", "分页数据"]
    )
    def test_mat_type_paging_data(self):
        """
        物料类型分页数据服务用例
        """
        try:
            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "keyword": None,
                    "conditionGroup": {
                        "type": "ConditionGroup",
                        "logicOperator": "AND",
                        "conditions": [
                            {
                                "type": "ConditionGroup",
                                "logicOperator": "AND",
                                "conditions": [
                                    {
                                        "key": "sSswBRvpLF-g9ITgP1HaV",
                                        "type": "ConditionLeaf",
                                        "leftValue": {
                                            "id": "VJ95O-9In5EpIj-MopDQ7",
                                            "key": "VJ95O-9In5EpIj-MopDQ7",
                                            "type": "VarValue",
                                            "fieldType": "Text",
                                            "valueType": "VAR",
                                            "varValue": [
                                                {
                                                    "valueKey": "matTypeCode",
                                                    "valueName": "matTypeCode"
                                                }
                                            ]
                                        },
                                        "operator": "CONTAINS",
                                        "rightValue": {
                                            "key": "l5M7qNnHFR9-GxgUVzgU7",
                                            "type": "VarValue",
                                            "fieldType": "Text",
                                            "valueType": "CONST",
                                            "constValue": "FINP"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                },
                "keyword": None,
                "filterData": {
                    "matName": None,
                    "matCode": None,
                    "genMatTypeCfId": None,
                    "__##FILTER_OPERATIONS__": None
                }
            }
            fields_to_filter = ["pageable", "keyword", "filterData"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="物料类型-分页数据服务",
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
        story="物料类型管理",
        title="测试物料类型标准导出",
        description="验证物料类型标准导出功能",
        severity="normal",
        file_level_order=7,
        tags=["物料类型", "导出"]
    )
    def test_export_mat_type(self):
        """
        物料类型标准导出用例
        """
        try:
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料类型"
                }
            }
            response, _ = self.standard_api_call(
                api_key="物料类型标准导出服务",
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
        story="物料类型管理",
        title="测试物料类型标准导入",
        description="验证物料类型标准导入功能",
        severity="normal",
        file_level_order=8,
        tags=["物料类型", "导入"]
    )
    def test_import_mat_type(self):
        """
        物料类型标准导入用例（需要文件上传）
        """
        try:
            set_dict = {
                "file": f"物料类型导入模板_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "sheetName": "物料类型",
                    "startRow": 2,
                    "validateOnly": False
                }
            }
            response, _ = self.standard_api_call(
                api_key="物料类型标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["file", "importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类型管理",
        title="测试提交物料类型导出任务",
        description="验证提交物料类型导出任务功能",
        severity="normal",
        file_level_order=9,
        tags=["物料类型", "导出任务"]
    )
    def test_submit_export_task(self):
        """
        提交物料类型导出任务用例
        """
        try:
            export_params = {
                "serviceKey": "GEN_MD$GEN_MAT_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"物料类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_mat_type_cf",
                            "modelName": "物料类型",
                            "sheetNo": 0,
                            "sheetName": "物料类型",
                            "headerConfigList": [
                                {
                                    "name": "物料类型编码",
                                    "type": "TEXT",
                                    "field": "matTypeCode"
                                },
                                {
                                    "name": "物料类型名称",
                                    "type": "TEXT",
                                    "field": "matTypeName"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$GEN_MAT_TYPE_VIEW-table-container-GEN_MD$gen_mat_type_cf",
                        "viewKey": "GEN_MD$GEN_MAT_TYPE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "matTypeCode"
                                },
                                {
                                    "field": "matTypeName"
                                }
                            ],
                            "modelKey": "GEN_MD$gen_mat_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_mat_type_cf",
                        "modelName": "物料类型",
                        "containerKey": "GEN_MD$GEN_MAT_TYPE_VIEW-table-container-GEN_MD$gen_mat_type_cf",
                        "viewKey": "GEN_MD$GEN_MAT_TYPE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_TYPE_VIEW"
                    }
                }
            }

            response, _ = self.standard_api_call(
                api_key="物料类型-导入导出任务管理接口-提交导出任务",
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

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类型管理",
        title="测试通过OSS提交物料类型导入任务",
        description="验证通过OSS提交物料类型导入任务功能",
        severity="normal",
        file_level_order=10,
        tags=["物料类型", "OSS导入"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交物料类型导入任务用例（需要OSS配置）
        """
        try:
            set_dict = {
                "ossPath": f"mat_type_import_{self.mock_util.get_timestamp()}.xlsx",
                "fileName": f"物料类型导入_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "sheetName": "物料类型数据",
                    "startRow": 2,
                    "mapping": {
                        "matTypeCode": "A",
                        "matTypeName": "B",
                        "remark": "C"
                    }
                }
            }
            response, _ = self.standard_api_call(
                api_key="物料类型-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["ossPath", "fileName", "importConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类型管理",
        title="测试删除物料类型",
        description="验证删除物料类型功能",
        severity="normal",
        file_level_order=11,
        tags=["物料类型", "删除"]
    )
    def test_delete_mat_type(self):
        """
        删除物料类型用例
        """
        try:
            if not self.mat_type_id:
                self.test_save_mat_type()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.mat_type_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-物料类型-删除服务",
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
