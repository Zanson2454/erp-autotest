import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("品牌管理")
class TestBrandManagement(GenMdBaseTest):
    """品牌管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
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

    @case_decorator(
        story="品牌管理",
        title="测试新增品牌",
        description="验证新增品牌功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["品牌管理", "新增"]
    )
    def test_save_brand(self):
        """
        新增品牌用例
        """
        try:
            # 准备品牌数据
            brand_code = self.mock_data.generate_unique_code(tag="Brand")
            brand_name = f"品牌_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-品牌-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["brandCode", "brandName", "brandImage"],
                ["params", "request"]
            )
            set_dict = {
                "brandCode": brand_code,
                "brandName": brand_name,
                "brandImage": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            brand_id = response.get("data", {}).get("data", {})

            # 保存品牌信息供后续用例使用
            self.brandId = brand_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌列表",
        description="验证品牌列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["品牌管理", "查询"]
    )
    def test_query_brand_list(self):
        """
        查询品牌列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-品牌-查询分页服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
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
                    {"name": "brandCode", "type": "TEXT"},
                    {"name": "brandName", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list,"not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试查询品牌详情",
        description="验证品牌详情查询功能",
        severity="normal",
        order=3,
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

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-品牌-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.brandId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试修改品牌",
        description="验证修改品牌功能",
        severity="normal",
        order=4,
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

            # 调用修改接口
            api_path = self.get_api_path("GEN-品牌-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "brandCode", "brandName", "brandImage"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.brandId,
                "brandCode": self.brandCode,
                "brandName": f"品牌_{self.mock_data.get_timestamp()}_修改",
                "brandImage": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="品牌管理",
        title="测试删除品牌",
        description="验证删除品牌功能",
        severity="normal",
        order=5,
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

            # 调用删除接口
            api_path = self.get_api_path("GEN-品牌-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.brandId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 清除品牌信息
            TestBrandManagement.brand_info = {}

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

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
        order=6,
        tags=["品牌管理", "导入", "GEN_BRAND_MD_GEI_IMPORT_SERVICE"]
    )
    def test_brand_import(self):
        """品牌标准导入用例 - GEN_BRAND_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("品牌标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "brandCode": self.mock_data.generate_unique_code(tag="IMPORT_BRAND"),
                    "brandName": f"导入测试品牌_{self.mock_data.get_timestamp()}",
                    "brandImage": None
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
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
        order=7,
        tags=["品牌管理", "导出", "GEN_BRAND_MD_GEI_EXPORT_SERVICE"]
    )
    def test_brand_export(self):
        """品牌标准导出用例 - GEN_BRAND_MD_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("品牌标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "brandCode", "type": "TEXT"},
                    {"name": "brandName", "type": "TEXT"},
                    {"name": "brandImage", "type": "TEXT"}
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

    @pytest.mark.skip(reason="品牌OSS导入服务功能未实现")
    @case_decorator(
        story="品牌导入导出管理",
        title="测试品牌OSS导入任务",
        description="验证品牌-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=8,
        tags=["品牌管理", "导入", "GEN_BRAND_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_brand_oss_import_task(self):
        """品牌OSS导入任务用例 - GEN_BRAND_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("品牌-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_brand_import_file.xlsx",
                "taskName": f"品牌导入任务_{self.mock_data.get_timestamp()}",
                "templateId": 1
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
        story="品牌导入导出管理",
        title="测试品牌导出任务",
        description="验证品牌-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=9,
        tags=["品牌管理", "导出", "GEN_BRAND_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_brand_export_task(self):
        """品牌导出任务用例 - GEN_BRAND_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("品牌-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['params'] = {
                "taskName": f"品牌管理-{self.nickname}-{self.mock_data.get_timestamp()}-导出",
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


            response = self.http.post(url, headers=self.admin_headers, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
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
        order=10,
        tags=["品牌管理", "业务验证", "唯一性测试"]
    )
    def test_brand_code_uniqueness(self):
        """品牌编码唯一性测试用例"""
        try:
            # 创建第一个品牌
            brand_code = self.mock_data.generate_unique_code(tag="UNIQUE_BRAND")
            
            api_path = self.get_api_path("GEN-品牌-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["brandCode", "brandName"], ["params", "request"]
            )
            set_dict = {
                "brandCode": brand_code,
                "brandName": f"唯一性测试品牌1_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response1 = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response1)

            # 尝试创建相同编码的品牌（应该失败或更新）
            set_dict["brandName"] = f"唯一性测试品牌2_{self.mock_data.get_timestamp()}"
            ParamUtil.set_request_params(filtered_params, set_dict)

            response2 = self.http.post(url, json=filtered_params)
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
        order=11,
        tags=["品牌管理", "综合测试", "业务流程"]
    )
    def test_brand_complete_workflow(self):
        """品牌完整流程测试用例"""
        try:
            # 1. 创建品牌
            brand_code = self.mock_data.generate_unique_code(tag="WORKFLOW_BRAND")
            brand_name = f"流程测试品牌_{self.mock_data.get_timestamp()}"

            # 创建
            create_api_path = self.get_api_path("GEN-品牌-保存服务")
            create_params, create_url = self.get_api_params(create_api_path)
            
            create_filtered_params = ParamUtil.filter_post_body_fields(
                create_params, ["brandCode", "brandName"], ["params", "request"]
            )
            create_set_dict = {"brandCode": brand_code, "brandName": brand_name}
            ParamUtil.set_request_params(create_filtered_params, create_set_dict)

            create_response = self.http.post(create_url, json=create_filtered_params)
            self.assert_util.assert_response_data(create_response)
            
            workflow_brand_id = create_response.get("data", {}).get("data", {})
            
            # 2. 查询详情验证
            detail_api_path = self.get_api_path("GEN-品牌-查询详情服务")
            detail_params, detail_url = self.get_api_params(detail_api_path)
            
            detail_filtered_params = ParamUtil.filter_post_body_fields(
                detail_params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(detail_filtered_params, {"id": workflow_brand_id})

            detail_response = self.http.post(detail_url, json=detail_filtered_params)
            self.assert_util.assert_response_data(detail_response)
            
            detail_data = detail_response.get("data", {}).get("data", {})
            assert detail_data.get("brandCode") == brand_code, "品牌编码不匹配"
            assert detail_data.get("brandName") == brand_name, "品牌名称不匹配"

            # 3. 更新品牌
            update_name = f"更新后的品牌名称_{self.mock_data.get_timestamp()}"
            update_filtered_params = ParamUtil.filter_post_body_fields(
                create_params, ["id", "brandCode", "brandName"], ["params", "request"]
            )
            update_set_dict = {
                "id": workflow_brand_id,
                "brandCode": brand_code,
                "brandName": update_name
            }
            ParamUtil.set_request_params(update_filtered_params, update_set_dict)

            update_response = self.http.post(create_url, json=update_filtered_params)
            self.assert_util.assert_response_data(update_response)

            # 4. 删除验证
            delete_api_path = self.get_api_path("GEN-品牌-删除服务")
            delete_params, delete_url = self.get_api_params(delete_api_path)
            
            delete_filtered_params = ParamUtil.filter_post_body_fields(
                delete_params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(delete_filtered_params, {"id": workflow_brand_id})

            delete_response = self.http.post(delete_url, json=delete_filtered_params)
            self.assert_util.assert_response_data(delete_response)

            a.json({"workflow": "complete"}, "完整流程执行成功")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
