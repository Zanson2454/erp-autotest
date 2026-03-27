import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("物料单位转换管理")
class TestMat_Unit_ConversionManagement(GenMdBaseTest):
    """物料单位转换管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mat_unit_conversion_id = None

        # 安全获取计量单位ID，避免IndexError
        cls.uomId = None
        if cls.init_data:
            uom_info = cls.init_data.get("uom_info", {})
            if uom_info:
                qty_uom_info = uom_info.get("qty_uom_info", [])
                if qty_uom_info and len(qty_uom_info) > 0:
                    cls.uomId = qty_uom_info[0].get("uom_id")

        # 安全获取用户信息
        if cls.init_data and cls.init_data.get("user_info"):
            user_info = cls.init_data["user_info"].get("user_info", {})
            cls.nickname = user_info.get("nickname")
            cls.user_id = user_info.get("id")
        else:
            cls.nickname = None
            cls.user_id = None
            cls.logger.warning("init_data 中未找到 user_info，nickname 和 user_id 设置为 None")
        cls.logger.info("物料单位转换管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料单位转换管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_uom_formula_type_cf",
                where="created_by = %s",
                params= [cls.user_id]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="物料单位转换管理",
        title="测试新增物料单位转换管理",
        description="验证新增物料单位转换管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["物料单位转换管理", "新增"]
    )
    def test_save_mat_unit_conversion(self):
        """
        新增物料单位转换管理用例
        """
        try:
            # 准备物料单位转换管理数据
            mat_unit_conversion_code = self.mock_util.generate_unique_code(tag="Mat_Unit_Conversion")
            mat_unit_conversion_name = f"物料单位转换管理_{self.mock_util.get_timestamp()}"

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "targetUnitFactor": 1,
                "baseUnitFactor": 1,
                "targetUnitId": {"id": self.uomId},
                "unitId": {"id": self.uomId},
                "genMatMdId": None
            }
            fields_to_filter = ["targetUnitFactor", "targetUnitId","baseUnitFactor","unitId","genMatMdId"]

            # 2. 使用标准化API调用（无任何断言）
            response, extracted_id = self.standard_api_call(
                api_key="GEN-计量单位转换-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="mat_unit_conversion"  # 自动存储 self.mat_unit_conversion_id
            )

            # 3. 保存业务数据（保持原有逻辑）
            self.mat_unit_conversion_id = extracted_id

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料单位转换管理",
        title="测试查询物料单位转换管理列表",
        description="验证物料单位转换管理列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["物料单位转换管理", "查询"]
    )
    def test_query_mat_unit_conversion_list(self):
        """
        查询物料单位转换管理列表用例
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
                    {"name": "mat_unit_conversion_code", "type": "TEXT"},
                    {"name": "mat_unit_conversion_name", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-计量单位转换-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 3. 业务验证（保持原有逻辑）
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            # 4. 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料单位转换管理",
        title="测试查询物料单位转换管理详情",
        description="验证物料单位转换管理详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["物料单位转换管理", "查询"]
    )
    def test_query_mat_unit_conversion_detail(self):
        """
        查询物料单位转换管理详情用例
        """
        try:
            # 获取物料单位转换管理ID
            if not self.mat_unit_conversion_id:
                self.test_save_mat_unit_conversion()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.mat_unit_conversion_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-计量单位转换-查询详情服务",
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
        story="物料单位转换管理",
        title="测试删除物料单位转换管理",
        description="验证删除物料单位转换管理功能",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["物料单位转换管理", "删除"]
    )
    def test_delete_mat_unit_conversion(self):
        """
        删除物料单位转换管理用例
        """
        try:
            # 获取物料单位转换管理信息
            if not self.mat_unit_conversion_id:
                self.test_save_mat_unit_conversion()

            # 1. 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.mat_unit_conversion_id}
            fields_to_filter = ["id"]

            # 2. 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-计量单位转换-删除服务",
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

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="物料单位转换管理",
        title="测试物料单位转换标准导出",
        description="验证物料单位转换标准导出功能",
        severity="normal",
        file_level_order=6,
        tags=["物料单位转换管理", "导出"]
    )
    def test_export_mat_unit_conversion(self):
        """
        物料单位转换标准导出用例
        """
        try:
            api_path = self.get_api_path("物料单位转换标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料单位转换导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料单位转换"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="物料单位转换标准导出服务",
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

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="物料单位转换管理",
        title="测试物料单位转换标准导入",
        description="验证物料单位转换标准导入功能",
        severity="normal",
        file_level_order=7,
        tags=["物料单位转换管理", "导入"]
    )
    def test_import_mat_unit_conversion(self):
        """
        物料单位转换标准导入用例（需要文件上传）
        """
        pass


    @case_decorator(
        story="物料单位转换管理",
        title="测试提交物料单位转换导出任务",
        description="验证提交物料单位转换导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["物料单位转换管理", "导出任务"]
    )
    def test_submit_export_task(self):
        """
        提交物料单位转换导出任务用例
        """
        try:
            api_path = self.get_api_path("物料单位转换-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['params']={
                "taskName": f"单位转换-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_uom_formula_type_cf",
                        "modelName": "物料单位转换",
                        "sheetNo": 0,
                        "sheetName": "物料单位转换",
                        "headerConfigList": [
                            {
                                "name": "物料",
                                "type": "TEXT",
                                "field": "genMatMdId.matName"
                            },
                            {
                                "name": "目标单位系数",
                                "type": "NUMBER",
                                "field": "targetUnitFactor",
                                "precisionDisplayType": "FILL_ROUND"
                            },
                            {
                                "name": "目标单位",
                                "type": "TEXT",
                                "field": "targetUnitId.uomDesc"
                            },
                            {
                                "name": "基本单位系数",
                                "type": "NUMBER",
                                "field": "baseUnitFactor"
                            },
                            {
                                "name": "基础单位",
                                "type": "TEXT",
                                "field": "unitId.uomDesc"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_UOM_FORMULA_VIEW-table-container-GEN_MD$gen_uom_formula_type_cf",
                    "viewKey": "GEN_MD$GEN_UOM_FORMULA_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_UOM_FORMULA_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "targetUnitFactor"
                            },
                            {
                                "field": "baseUnitFactor"
                            },
                            {
                                "field": "genMatMdId",
                                "selectFields": [
                                    {
                                        "field": "matName"
                                    }
                                ]
                            },
                            {
                                "field": "targetUnitId",
                                "selectFields": [
                                    {
                                        "field": "uomDesc"
                                    }
                                ]
                            },
                            {
                                "field": "unitId",
                                "selectFields": [
                                    {
                                        "field": "uomDesc"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "GEN_MD$gen_uom_formula_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_uom_formula_type_cf",
                    "modelName": "物料单位转换",
                    "containerKey": "GEN_MD$GEN_UOM_FORMULA_VIEW-table-container-GEN_MD$gen_uom_formula_type_cf",
                    "viewKey": "GEN_MD$GEN_UOM_FORMULA_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_UOM_FORMULA_VIEW"
                }
            }

            response, _ = self.standard_api_call(
                api_key="物料单位转换-导入导出任务管理接口-提交导出任务",
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

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料单位转换管理",
        title="测试通过OSS提交物料单位转换导入任务",
        description="验证通过OSS提交物料单位转换导入任务功能",
        severity="normal",
        file_level_order=9,
        tags=["物料单位转换管理", "OSS导入"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交物料单位转换导入任务用例（需要OSS配置）
        """
        pass
