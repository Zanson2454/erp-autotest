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
        cls.mat_tax_id = None
        cls.mat_tax_code = None
        cls.logger.info("物料税分类管理测试类初始化完成")
        country_info = cls.init_data.get("country_info")
        cls.counId = country_info[0].get("coun_id") if country_info else None

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料税分类数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_mat_tax_type_cf",
                where="tax_class_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="物料税分类管理",
        title="测试新增物料税分类",
        description="验证新增物料税分类功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["物料税分类管理", "新增"]
    )
    def test_save_mat_tax(self):
        """
        新增物料税分类用例
        """
        try:
            # 准备物料税分类数据
            mat_tax_code = self.mock_util.generate_unique_code(tag="MatTax")

            api_path = self.get_api_path("GEN-物料税分类-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taxClassCode", "taxClassDesc", "counId"],
                ["params", "request"]
            )
            set_dict = {
                "taxClassCode": mat_tax_code,
                "taxClassDesc": f"自动化测试物料税分类-{self.mock_util.get_timestamp()}",
                "counId": {"id": self.counId}
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.mat_tax_id = response.get("data", {}).get("data", {})
            self.mat_tax_code = mat_tax_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料税分类管理",
        title="测试查询物料税分类分页",
        description="验证物料税分类分页查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["物料税分类管理", "查询"]
    )
    def test_query_mat_tax_page(self):
        """
        查询物料税分类分页用例
        """
        try:
            api_path = self.get_api_path("GEN-物料税分类-查询分页服务")
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
                    {"name": "matTaxCode", "type": "TEXT"},
                    {"name": "matTaxName", "type": "TEXT"}
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
        story="物料税分类管理",
        title="测试查询物料税分类详情",
        description="验证物料税分类详情查询功能",
        severity="normal",
        order=3,
        tags=["物料税分类管理", "详情"]
    )
    def test_query_mat_tax_detail(self):
        """
        查询物料税分类详情用例
        """
        try:
            if not self.mat_tax_id:
                self.test_save_mat_tax()

            api_path = self.get_api_path("GEN-物料税分类-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mat_tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="实际业务未调用")
    @case_decorator(
        story="物料税分类管理",
        title="测试物料税分类标准导出",
        description="验证物料税分类标准导出功能",
        severity="normal",
        order=4,
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

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="物料税分类管理",
        title="测试物料税分类标准导入",
        description="验证物料税分类标准导入功能",
        severity="normal",
        order=6,
        tags=["物料税分类管理", "导入"]
    )
    def test_import_mat_tax(self):
        """
        物料税分类标准导入用例（需要文件上传）
        """
        try:
            # 调用标准导入接口
            api_path = self.get_api_path("物料税分类标准导入服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["file", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "file": f"物料税分类导入模板_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "sheetName": "物料税分类",
                    "startRow": 2,
                    "validateOnly": False
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
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
        order=7,
        tags=["物料税分类管理", "导出任务"]
    )
    def test_submit_export_task(self):
        """
        提交物料税分类导出任务用例
        """
        try:
            api_path = self.get_api_path("物料税分类-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params = {
                "serviceKey": "GEN_MD$GEN_MAT_TAX_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
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
                        "appId": 0,
                        "teamId": 22,
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
                        "appId": 0,
                        "teamId": 22,
                        "model": "GEN_MD$gen_mat_tax_type_cf",
                        "modelName": "物料税分类",
                        "containerKey": "GEN_MD$GEN_MAT_TAX_VIEW-table-container-GEN_MD$gen_mat_tax_type_cf",
                        "viewKey": "GEN_MD$GEN_MAT_TAX_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_TAX_VIEW"
                    }
                }
            }
            self.logger.info(f"请求参数: {self.admin_headers}")
            response = self.http.post(url, headers=self.admin_headers, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料税分类管理",
        title="测试通过OSS提交物料税分类导入任务",
        description="验证通过OSS提交物料税分类导入任务功能",
        severity="normal",
        order=8,
        tags=["物料税分类管理", "OSS导入"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交物料税分类导入任务用例（需要OSS配置）
        """
        try:
            # 调用OSS导入任务接口
            api_path = self.get_api_path("物料税分类-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ossPath", "fileName", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "ossPath": f"mat_tax_import_{self.mock_util.get_timestamp()}.xlsx",
                "fileName": f"物料税分类导入_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "sheetName": "物料税分类数据",
                    "startRow": 2,
                    "mapping": {
                        "taxClassCode": "A",
                        "taxClassDesc": "B",
                        "counId": "C"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料税分类管理",
        title="测试删除物料税分类",
        description="验证删除物料税分类功能",
        severity="normal",
        order=9,
        tags=["物料税分类管理", "删除"]
    )
    def test_delete_mat_tax(self):
        """
        删除物料税分类用例
        """
        try:
            if not self.mat_tax_id:
                self.test_save_mat_tax()

            api_path = self.get_api_path("GEN-物料税分类-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mat_tax_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 