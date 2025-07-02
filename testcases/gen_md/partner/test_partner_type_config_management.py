import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴类型配置与其他功能")
class TestPartnerTypeConfigManagement(GenMdBaseTest):
    """合作伙伴类型配置与其他功能测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_type_config_id = None
        cls.partner_group_id = None
        cls.logger.info("合作伙伴类型配置与其他功能测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_business_partner_type_cf", 
                where="type_code like %s", 
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_partner_procedure_head_cf", 
                where="group_code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 合作伙伴类型配置管理 =============
    @case_decorator(
        story="合作伙伴类型配置",
        title="测试新增合作伙伴类型",
        description="验证新增合作伙伴类型功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["合作伙伴类型", "新增"]
    )
    def test_save_business_partner_type(self):
        """新增合作伙伴类型用例"""
        try:
            type_code = self.mock_util.generate_unique_code(tag="BPT")
            type_name = f"合作伙伴类型_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-合作伙伴类型-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["typeCode", "typeName", "category", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "typeCode": type_code,
                "typeName": type_name,
                "category": "BUSINESS",
                "status": "ENABLED",
                "remark": f"自动化测试合作伙伴类型-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.partner_type_config_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试查询合作伙伴类型分页",
        description="验证合作伙伴类型分页查询功能",
        severity="normal",
        order=2,
        tags=["合作伙伴类型", "查询"]
    )
    def test_query_business_partner_type_page(self):
        """查询合作伙伴类型分页用例"""
        try:
            api_path = self.get_api_path("GEN-合作伙伴类型-查询分页服务")
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
                    {"name": "typeCode", "type": "TEXT"},
                    {"name": "typeName", "type": "TEXT"}
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
        story="合作伙伴类型配置",
        title="测试查询合作伙伴类型详情",
        description="验证合作伙伴类型详情查询功能",
        severity="normal",
        order=3,
        tags=["合作伙伴类型", "详情"]
    )
    def test_query_business_partner_type_detail(self):
        """查询合作伙伴类型详情用例"""
        try:
            if not self.partner_type_config_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_type_config_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型分页数据服务",
        description="验证合作伙伴类型分页数据服务功能",
        severity="normal",
        order=4,
        tags=["合作伙伴类型", "分页数据"]
    )
    def test_business_partner_type_paging_data(self):
        """合作伙伴类型分页数据服务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "queryCondition"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "queryCondition": {}
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
        story="合作伙伴类型配置",
        title="测试合作伙伴类型分页查询(根据角色过滤)",
        description="验证合作伙伴类型分页查询(根据角色过滤)功能",
        severity="normal",
        order=5,
        tags=["合作伙伴类型", "角色过滤"]
    )
    def test_partner_type_filter_paging(self):
        """合作伙伴类型分页查询(根据角色过滤)用例"""
        try:
            api_path = self.get_api_path("GEN-合作伙伴类型-分页查询(根据角色过滤)")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["roleType", "pageable"],
                ["params", "request"]
            )
            set_dict = {
                "roleType": "CUSTOMER",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
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
        story="合作伙伴类型配置",
        title="测试启用合作伙伴类型",
        description="验证启用合作伙伴类型功能",
        severity="normal",
        order=6,
        tags=["合作伙伴类型", "启用"]
    )
    def test_enable_business_partner_type(self):
        """启用合作伙伴类型用例"""
        try:
            if not self.partner_type_config_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": [self.partner_type_config_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试禁用合作伙伴类型",
        description="验证禁用合作伙伴类型功能",
        severity="normal",
        order=7,
        tags=["合作伙伴类型", "禁用"]
    )
    def test_disable_business_partner_type(self):
        """禁用合作伙伴类型用例"""
        try:
            if not self.partner_type_config_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": [self.partner_type_config_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试提交合作伙伴类型导出任务",
        description="验证提交合作伙伴类型导出任务功能",
        severity="normal",
        order=8,
        tags=["合作伙伴类型", "导出任务"]
    )
    def test_submit_business_partner_type_export_task(self):
        """提交合作伙伴类型导出任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴类型导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"合作伙伴类型_{self.mock_util.get_timestamp()}",
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

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试删除合作伙伴类型",
        description="验证删除合作伙伴类型功能",
        severity="normal",
        order=9,
        tags=["合作伙伴类型", "删除"]
    )
    def test_delete_business_partner_type(self):
        """删除合作伙伴类型用例"""
        try:
            if not self.partner_type_config_id:
                self.test_save_business_partner_type()

            api_path = self.get_api_path("GEN-合作伙伴类型-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": [self.partner_type_config_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 相关方组管理 =============
    @case_decorator(
        story="相关方组管理",
        title="测试新增相关方组",
        description="验证新增相关方组功能",
        severity="normal",
        order=10,
        tags=["相关方组", "新增"]
    )
    def test_save_partner_group(self):
        """新增相关方组用例"""
        try:
            group_code = self.mock_util.generate_unique_code(tag="PG")
            group_name = f"相关方组_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-相关方组-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["groupCode", "groupName", "description", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "groupCode": group_code,
                "groupName": group_name,
                "description": "相关方组描述",
                "remark": f"自动化测试相关方组-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.partner_group_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方组管理",
        title="测试查询相关方组分页",
        description="验证相关方组分页查询功能",
        severity="normal",
        order=11,
        tags=["相关方组", "查询"]
    )
    def test_query_partner_group_page(self):
        """查询相关方组分页用例"""
        try:
            api_path = self.get_api_path("GEN-相关方组-查询分页服务")
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
                    {"name": "groupCode", "type": "TEXT"},
                    {"name": "groupName", "type": "TEXT"}
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
        story="相关方组管理",
        title="测试查询相关方组详情",
        description="验证相关方组详情查询功能",
        severity="normal",
        order=12,
        tags=["相关方组", "详情"]
    )
    def test_query_partner_group_detail(self):
        """查询相关方组详情用例"""
        try:
            if not self.partner_group_id:
                self.test_save_partner_group()

            api_path = self.get_api_path("GEN-相关方组-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_group_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="相关方组管理",
        title="测试提交相关方组导出任务",
        description="验证提交相关方组导出任务功能",
        severity="normal",
        order=13,
        tags=["相关方组", "导出任务"]
    )
    def test_submit_partner_group_export_task(self):
        """提交相关方组导出任务用例"""
        try:
            api_path = self.get_api_path("相关方组-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"相关方组导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"相关方组_{self.mock_util.get_timestamp()}",
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

    @case_decorator(
        story="相关方组管理",
        title="测试删除相关方组",
        description="验证删除相关方组功能",
        severity="normal",
        order=14,
        tags=["相关方组", "删除"]
    )
    def test_delete_partner_group(self):
        """删除相关方组用例"""
        try:
            if not self.partner_group_id:
                self.test_save_partner_group()

            api_path = self.get_api_path("GEN-相关方组-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": [self.partner_group_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 评分模板查询 =============
    @case_decorator(
        story="评分管理",
        title="测试查询评分模板信息",
        description="验证查询评分模板信息功能",
        severity="normal",
        order=15,
        tags=["评分模板", "查询"]
    )
    def test_query_survey_template(self):
        """查询评分模板信息用例"""
        try:
            api_path = self.get_api_path("GEN-评分查询模板信息")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["templateId"],
                ["params", "request"]
            )
            set_dict = {"templateId": 1}  # 示例模板ID
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型标准导出",
        description="验证合作伙伴类型标准导出功能",
        severity="normal",
        order=16,
        tags=["合作伙伴类型", "导出"]
    )
    def test_export_business_partner_type(self):
        """合作伙伴类型标准导出用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"合作伙伴类型导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "合作伙伴类型"
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
        story="合作伙伴类型配置",
        title="测试合作伙伴类型标准导入",
        description="验证合作伙伴类型标准导入功能",
        severity="normal",
        order=17,
        tags=["合作伙伴类型", "导入"]
    )
    def test_import_business_partner_type(self):
        """合作伙伴类型标准导入用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"合作伙伴类型导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL"
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
        story="合作伙伴类型配置",
        title="测试通过OSS提交合作伙伴类型导入任务",
        description="验证通过OSS提交合作伙伴类型导入任务功能",
        severity="normal",
        order=18,
        tags=["合作伙伴类型", "OSS导入"]
    )
    def test_submit_business_partner_type_import_task_by_oss(self):
        """通过OSS提交合作伙伴类型导入任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴类型-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴类型OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_type_config_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "合作伙伴类型"
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

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="相关方组管理",
        title="测试相关方组标准导出",
        description="验证相关方组标准导出功能",
        severity="normal",
        order=19,
        tags=["相关方组", "导出"]
    )
    def test_export_partner_group(self):
        """相关方组标准导出用例"""
        try:
            api_path = self.get_api_path("相关方组标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"相关方组导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "相关方组"
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
        story="相关方组管理",
        title="测试相关方组标准导入",
        description="验证相关方组标准导入功能",
        severity="normal",
        order=20,
        tags=["相关方组", "导入"]
    )
    def test_import_partner_group(self):
        """相关方组标准导入用例"""
        try:
            api_path = self.get_api_path("相关方组标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"相关方组导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL"
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
        story="相关方组管理",
        title="测试通过OSS提交相关方组导入任务",
        description="验证通过OSS提交相关方组导入任务功能",
        severity="normal",
        order=21,
        tags=["相关方组", "OSS导入"]
    )
    def test_submit_partner_group_import_task_by_oss(self):
        """通过OSS提交相关方组导入任务用例"""
        try:
            api_path = self.get_api_path("相关方组-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"相关方组OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_group_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "相关方组"
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