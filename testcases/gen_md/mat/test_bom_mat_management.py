import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("BOM管理")
class TestBomManagement(GenMdBaseTest):
    """BOM管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bom_head_id = None
        cls.bom_item_type_id = None
        cls.bom_status_id = None
        cls.bom_use_id = None
        cls.bom_supp_ind_id = None
        cls.logger.info("BOM管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的BOM数据
        """
        try:
            # 清理BOM相关测试数据
            cls.db.delete(table="gen_bom_head_md", where="bom_code like %s", params=["AT_%"])
            cls.db.delete(table="gen_bom_item_type_cf", where="item_type_code like %s", params=["AT_%"])
            cls.db.delete(table="gen_bom_status_cf", where="status_code like %s", params=["AT_%"])
            cls.db.delete(table="gen_bom_use_cf", where="use_code like %s", params=["AT_%"])
            cls.db.delete(table="gen_bom_item_supp_ind_cf", where="supp_ind_code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= BOM头管理 =============
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM头",
        description="验证新增BOM头功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["BOM管理", "BOM头", "新增"]
    )
    def test_save_bom_head(self):
        """
        新增BOM头用例
        """
        try:
            bom_code = self.mock_util.generate_unique_code(tag="BOM")
            bom_name = f"BOM_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-物料BOM头-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bomCode", "bomName", "matId", "version", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "bomCode": bom_code,
                "bomName": bom_name,
                "matId": None,  # 需要关联物料ID
                "version": "1.0",
                "remark": f"自动化测试BOM-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_head_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM头分页",
        description="验证BOM头分页查询功能",
        severity="normal",
        order=2,
        tags=["BOM管理", "BOM头", "查询"]
    )
    def test_query_bom_head_page(self):
        """
        查询BOM头分页用例
        """
        try:
            api_path = self.get_api_path("GEN-物料BOM头-查询分页服务")
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
                    {"name": "bomCode", "type": "TEXT"},
                    {"name": "bomName", "type": "TEXT"}
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
        story="BOM管理",
        title="测试查询BOM头详情",
        description="验证BOM头详情查询功能",
        severity="normal",
        order=3,
        tags=["BOM管理", "BOM头", "详情"]
    )
    def test_query_bom_head_detail(self):
        """
        查询BOM头详情用例
        """
        try:
            if not self.bom_head_id:
                self.test_save_bom_head()

            api_path = self.get_api_path("GEN-物料BOM头-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bom_head_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试BOM头标准导出",
        description="验证BOM头标准导出功能",
        severity="normal",
        order=4,
        tags=["BOM管理", "BOM头", "导出"]
    )
    def test_export_bom_head(self):
        """
        BOM头标准导出用例
        """
        try:
            api_path = self.get_api_path("物料BOM头标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"BOM头导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "BOM头"
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
        story="BOM管理",
        title="测试BOM头标准导入",
        description="验证BOM头标准导入功能",
        severity="normal",
        order=5,
        tags=["BOM管理", "BOM头", "导入"]
    )
    def test_import_bom_head(self):
        """
        BOM头标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试删除BOM头",
        description="验证删除BOM头功能",
        severity="normal",
        order=6,
        tags=["BOM管理", "BOM头", "删除"]
    )
    def test_delete_bom_head(self):
        """
        删除BOM头用例
        """
        try:
            if not self.bom_head_id:
                self.test_save_bom_head()

            api_path = self.get_api_path("GEN-物料BOM头-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bom_head_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= BOM行项目类别管理 =============
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM行项目类别",
        description="验证新增BOM行项目类别功能",
        severity="normal",
        order=7,
        tags=["BOM管理", "行项目类别", "新增"]
    )
    def test_save_bom_item_type(self):
        """
        新增BOM行项目类别用例
        """
        try:
            item_type_code = self.mock_util.generate_unique_code(tag="ItemType")
            item_type_name = f"行项目类别_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-BOM行项目类别配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["itemTypeCode", "itemTypeName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "itemTypeCode": item_type_code,
                "itemTypeName": item_type_name,
                "remark": f"自动化测试行项目类别-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_item_type_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM行项目类别分页",
        description="验证BOM行项目类别分页查询功能",
        severity="normal",
        order=8,
        tags=["BOM管理", "行项目类别", "查询"]
    )
    def test_query_bom_item_type_page(self):
        """
        查询BOM行项目类别分页用例
        """
        try:
            api_path = self.get_api_path("GEN-BOM行项目类别配置-查询分页服务")
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
                    {"name": "itemTypeCode", "type": "TEXT"},
                    {"name": "itemTypeName", "type": "TEXT"}
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
        story="BOM管理",
        title="测试查询BOM行项目类别详情",
        description="验证BOM行项目类别详情查询功能",
        severity="normal",
        order=9,
        tags=["BOM管理", "行项目类别", "详情"]
    )
    def test_query_bom_item_type_detail(self):
        """
        查询BOM行项目类别详情用例
        """
        try:
            if not self.bom_item_type_id:
                self.test_save_bom_item_type()

            api_path = self.get_api_path("GEN-BOM行项目类别配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bom_item_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试删除BOM行项目类别",
        description="验证删除BOM行项目类别功能",
        severity="normal",
        order=10,
        tags=["BOM管理", "行项目类别", "删除"]
    )
    def test_delete_bom_item_type(self):
        """
        删除BOM行项目类别用例
        """
        try:
            if not self.bom_item_type_id:
                self.test_save_bom_item_type()

            api_path = self.get_api_path("GEN-BOM行项目类别配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bom_item_type_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= BOM状态管理 =============
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM状态",
        description="验证新增BOM状态功能",
        severity="normal",
        order=11,
        tags=["BOM管理", "BOM状态", "新增"]
    )
    def test_save_bom_status(self):
        """
        新增BOM状态用例
        """
        try:
            status_code = self.mock_util.generate_unique_code(tag="BomStatus")
            status_name = f"BOM状态_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-BOM状态配置表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["statusCode", "statusName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "statusCode": status_code,
                "statusName": status_name,
                "remark": f"自动化测试BOM状态-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_status_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM状态分页",
        description="验证BOM状态分页查询功能",
        severity="normal",
        order=12,
        tags=["BOM管理", "BOM状态", "查询"]
    )
    def test_query_bom_status_page(self):
        """
        查询BOM状态分页用例
        """
        try:
            api_path = self.get_api_path("GEN-BOM状态配置表-查询分页服务")
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
                    {"name": "statusCode", "type": "TEXT"},
                    {"name": "statusName", "type": "TEXT"}
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
        story="BOM管理",
        title="测试查询BOM状态详情",
        description="验证BOM状态详情查询功能",
        severity="normal",
        order=13,
        tags=["BOM管理", "BOM状态", "详情"]
    )
    def test_query_bom_status_detail(self):
        """
        查询BOM状态详情用例
        """
        try:
            if not self.bom_status_id:
                self.test_save_bom_status()

            api_path = self.get_api_path("GEN-BOM状态配置表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bom_status_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试删除BOM状态",
        description="验证删除BOM状态功能",
        severity="normal",
        order=14,
        tags=["BOM管理", "BOM状态", "删除"]
    )
    def test_delete_bom_status(self):
        """
        删除BOM状态用例
        """
        try:
            if not self.bom_status_id:
                self.test_save_bom_status()

            api_path = self.get_api_path("GEN-BOM状态配置表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bom_status_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= BOM用途管理 =============
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM用途",
        description="验证新增BOM用途功能",
        severity="normal",
        order=15,
        tags=["BOM管理", "BOM用途", "新增"]
    )
    def test_save_bom_use(self):
        """
        新增BOM用途用例
        """
        try:
            use_code = self.mock_util.generate_unique_code(tag="BomUse")
            use_name = f"BOM用途_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-BOM用途配置-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["useCode", "useName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "useCode": use_code,
                "useName": use_name,
                "remark": f"自动化测试BOM用途-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_use_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM用途分页",
        description="验证BOM用途分页查询功能",
        severity="normal",
        order=16,
        tags=["BOM管理", "BOM用途", "查询"]
    )
    def test_query_bom_use_page(self):
        """
        查询BOM用途分页用例
        """
        try:
            api_path = self.get_api_path("GEN-BOM用途配置-查询分页服务")
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
                    {"name": "useCode", "type": "TEXT"},
                    {"name": "useName", "type": "TEXT"}
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
        story="BOM管理",
        title="测试查询BOM用途详情",
        description="验证BOM用途详情查询功能",
        severity="normal",
        order=17,
        tags=["BOM管理", "BOM用途", "详情"]
    )
    def test_query_bom_use_detail(self):
        """
        查询BOM用途详情用例
        """
        try:
            if not self.bom_use_id:
                self.test_save_bom_use()

            api_path = self.get_api_path("GEN-BOM用途配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bom_use_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试BOM用途标准导出",
        description="验证BOM用途标准导出功能",
        severity="normal",
        order=18,
        tags=["BOM管理", "BOM用途", "导出"]
    )
    def test_export_bom_use(self):
        """
        BOM用途标准导出用例
        """
        try:
            api_path = self.get_api_path("BOM用途配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"BOM用途导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "BOM用途"
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
        story="BOM管理",
        title="测试BOM用途标准导入",
        description="验证BOM用途标准导入功能",
        severity="normal",
        order=19,
        tags=["BOM管理", "BOM用途", "导入"]
    )
    def test_import_bom_use(self):
        """
        BOM用途标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试提交BOM用途导出任务",
        description="验证提交BOM用途导出任务功能",
        severity="normal",
        order=20,
        tags=["BOM管理", "BOM用途", "导出任务"]
    )
    def test_submit_bom_use_export_task(self):
        """
        提交BOM用途导出任务用例
        """
        try:
            api_path = self.get_api_path("BOM用途配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"BOM用途导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"BOM用途_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
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
        story="BOM管理",
        title="测试通过OSS提交BOM用途导入任务",
        description="验证通过OSS提交BOM用途导入任务功能",
        severity="normal",
        order=21,
        tags=["BOM管理", "BOM用途", "OSS导入"]
    )
    def test_submit_bom_use_import_task_by_oss(self):
        """
        通过OSS提交BOM用途导入任务用例（需要OSS配置）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试删除BOM用途",
        description="验证删除BOM用途功能",
        severity="normal",
        order=22,
        tags=["BOM管理", "BOM用途", "删除"]
    )
    def test_delete_bom_use(self):
        """
        删除BOM用途用例
        """
        try:
            if not self.bom_use_id:
                self.test_save_bom_use()

            api_path = self.get_api_path("GEN-BOM用途配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bom_use_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= BOM状态管理导入导出 =============
    @case_decorator(
        story="BOM管理",
        title="测试BOM状态标准导出",
        description="验证BOM状态标准导出功能",
        severity="normal",
        order=23,
        tags=["BOM管理", "BOM状态", "导出"]
    )
    def test_export_bom_status(self):
        """
        BOM状态标准导出用例
        """
        try:
            api_path = self.get_api_path("BOM状态配置表标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"BOM状态导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "BOM状态"
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
        story="BOM管理",
        title="测试BOM状态标准导入",
        description="验证BOM状态标准导入功能",
        severity="normal",
        order=24,
        tags=["BOM管理", "BOM状态", "导入"]
    )
    def test_import_bom_status(self):
        """
        BOM状态标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试提交BOM状态导出任务",
        description="验证提交BOM状态导出任务功能",
        severity="normal",
        order=25,
        tags=["BOM管理", "BOM状态", "导出任务"]
    )
    def test_submit_bom_status_export_task(self):
        """
        提交BOM状态导出任务用例
        """
        try:
            api_path = self.get_api_path("BOM状态配置表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"BOM状态导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"BOM状态_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
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
        story="BOM管理",
        title="测试通过OSS提交BOM状态导入任务",
        description="验证通过OSS提交BOM状态导入任务功能",
        severity="normal",
        order=26,
        tags=["BOM管理", "BOM状态", "OSS导入"]
    )
    def test_submit_bom_status_import_task_by_oss(self):
        """
        通过OSS提交BOM状态导入任务用例（需要OSS配置）
        """
        pass

    # ============= BOM行项目类别导入导出 =============
    @case_decorator(
        story="BOM管理",
        title="测试BOM行项目类别标准导出",
        description="验证BOM行项目类别标准导出功能",
        severity="normal",
        order=27,
        tags=["BOM管理", "行项目类别", "导出"]
    )
    def test_export_bom_item_type(self):
        """
        BOM行项目类别标准导出用例
        """
        try:
            api_path = self.get_api_path("BOM行项目类别配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"BOM行项目类别导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "BOM行项目类别"
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
        story="BOM管理",
        title="测试BOM行项目类别标准导入",
        description="验证BOM行项目类别标准导入功能",
        severity="normal",
        order=28,
        tags=["BOM管理", "行项目类别", "导入"]
    )
    def test_import_bom_item_type(self):
        """
        BOM行项目类别标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试提交BOM行项目类别导出任务",
        description="验证提交BOM行项目类别导出任务功能",
        severity="normal",
        order=29,
        tags=["BOM管理", "行项目类别", "导出任务"]
    )
    def test_submit_bom_item_type_export_task(self):
        """
        提交BOM行项目类别导出任务用例
        """
        try:
            api_path = self.get_api_path("BOM行项目类别配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"BOM行项目类别导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"BOM行项目类别_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
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
        story="BOM管理",
        title="测试通过OSS提交BOM行项目类别导入任务",
        description="验证通过OSS提交BOM行项目类别导入任务功能",
        severity="normal",
        order=30,
        tags=["BOM管理", "行项目类别", "OSS导入"]
    )
    def test_submit_bom_item_type_import_task_by_oss(self):
        """
        通过OSS提交BOM行项目类别导入任务用例（需要OSS配置）
        """
        pass

    # ============= BOM供应标识管理 =============
    @case_decorator(
        story="BOM管理",
        title="测试新增BOM供应标识",
        description="验证新增BOM供应标识功能",
        severity="normal",
        order=38,
        tags=["BOM管理", "供应标识", "新增"]
    )
    def test_save_bom_supp_ind(self):
        """
        新增BOM供应标识用例
        """
        try:
            supp_ind_code = self.mock_util.generate_unique_code(tag="SuppInd")
            supp_ind_name = f"供应标识_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-BOM 行项目供应标识配置表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["suppIndCode", "suppIndName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "suppIndCode": supp_ind_code,
                "suppIndName": supp_ind_name,
                "remark": f"自动化测试供应标识-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.bom_supp_ind_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试查询BOM供应标识分页",
        description="验证BOM供应标识分页查询功能",
        severity="normal",
        order=39,
        tags=["BOM管理", "供应标识", "查询"]
    )
    def test_query_bom_supp_ind_page(self):
        """
        查询BOM供应标识分页用例
        """
        try:
            api_path = self.get_api_path("GEN-BOM 行项目供应标识配置表-查询分页服务")
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
                    {"name": "suppIndCode", "type": "TEXT"},
                    {"name": "suppIndName", "type": "TEXT"}
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
        story="BOM管理",
        title="测试查询BOM供应标识详情",
        description="验证BOM供应标识详情查询功能",
        severity="normal",
        order=40,
        tags=["BOM管理", "供应标识", "详情"]
    )
    def test_query_bom_supp_ind_detail(self):
        """
        查询BOM供应标识详情用例
        """
        try:
            if not self.bom_supp_ind_id:
                self.test_save_bom_supp_ind()

            api_path = self.get_api_path("GEN-BOM 行项目供应标识配置表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.bom_supp_ind_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="BOM管理",
        title="测试删除BOM供应标识",
        description="验证删除BOM供应标识功能",
        severity="normal",
        order=41,
        tags=["BOM管理", "供应标识", "删除"]
    )
    def test_delete_bom_supp_ind(self):
        """
        删除BOM供应标识用例
        """
        try:
            if not self.bom_supp_ind_id:
                self.test_save_bom_supp_ind()

            api_path = self.get_api_path("GEN-BOM 行项目供应标识配置表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.bom_supp_ind_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= BOM头导入导出任务 =============
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="BOM管理",
        title="测试BOM头标准导入",
        description="验证BOM头标准导入功能",
        severity="normal",
        order=35,
        tags=["BOM管理", "BOM头", "导入"]
    )
    def test_import_bom_head_standard(self):
        """
        BOM头标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试提交BOM头导出任务",
        description="验证提交BOM头导出任务功能",
        severity="normal",
        order=36,
        tags=["BOM管理", "BOM头", "导出任务"]
    )
    def test_submit_bom_head_export_task(self):
        """
        提交BOM头导出任务用例
        """
        try:
            api_path = self.get_api_path("物料BOM头-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"BOM头导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"BOM头_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
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
        story="BOM管理",
        title="测试通过OSS提交BOM头导入任务",
        description="验证通过OSS提交BOM头导入任务功能",
        severity="normal",
        order=37,
        tags=["BOM管理", "BOM头", "OSS导入"]
    )
    def test_submit_bom_head_import_task_by_oss(self):
        """
        通过OSS提交BOM头导入任务用例（需要OSS配置）
        """
        pass

    # ============= BOM供应标识管理导入导出 =============
    @case_decorator(
        story="BOM管理",
        title="测试BOM供应标识标准导出",
        description="验证BOM供应标识标准导出功能",
        severity="normal",
        order=31,
        tags=["BOM管理", "供应标识", "导出"]
    )
    def test_export_bom_supp_ind(self):
        """
        BOM供应标识标准导出用例
        """
        try:
            api_path = self.get_api_path("BOM 行项目供应标识配置表标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"BOM供应标识导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "BOM供应标识"
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
        story="BOM管理",
        title="测试BOM供应标识标准导入",
        description="验证BOM供应标识标准导入功能",
        severity="normal",
        order=32,
        tags=["BOM管理", "供应标识", "导入"]
    )
    def test_import_bom_supp_ind(self):
        """
        BOM供应标识标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="BOM管理",
        title="测试提交BOM供应标识导出任务",
        description="验证提交BOM供应标识导出任务功能",
        severity="normal",
        order=33,
        tags=["BOM管理", "供应标识", "导出任务"]
    )
    def test_submit_bom_supp_ind_export_task(self):
        """
        提交BOM供应标识导出任务用例
        """
        try:
            api_path = self.get_api_path("BOM 行项目供应标识配置表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"BOM供应标识导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"BOM供应标识_{self.mock_util.get_timestamp()}",
                    "format": "EXCEL"
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
        story="BOM管理",
        title="测试通过OSS提交BOM供应标识导入任务",
        description="验证通过OSS提交BOM供应标识导入任务功能",
        severity="normal",
        order=34,
        tags=["BOM管理", "供应标识", "OSS导入"]
    )
    def test_submit_bom_supp_ind_import_task_by_oss(self):
        """
        通过OSS提交BOM供应标识导入任务用例（需要OSS配置）
        """
        pass
