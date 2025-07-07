import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴主数据")
class TestBusinessPartnerManagement(GenMdBaseTest):
    """合作伙伴主数据管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.partner_code = None
        cls.logger.info("合作伙伴主数据管理测试类初始化完成")
        
        cls.business_partner_type_cf = cls.md_init_cache.get("partner_info", {}).get("business_partner_type_cf", {})
        cls.out_cust_type_id = cls.business_partner_type_cf.get("out_cust", {}).get("id", None)
        cls.inter_cust_type_id = cls.business_partner_type_cf.get("inter_cust", {}).get("id", None)
        cls.person_cust_type_id = cls.business_partner_type_cf.get("person_cust", {}).get("id", None)
        cls.out_supplier_type_id = cls.business_partner_type_cf.get("out_supplier", {}).get("id", None)
        cls.outsea_supplier_type_id = cls.business_partner_type_cf.get("outsea_supplier", {}).get("id", None)
        cls.inter_supplier_type_id = cls.business_partner_type_cf.get("inter_supplier", {}).get("id", None)
        cls.serv_supplier_type_id = cls.business_partner_type_cf.get("serv_supplier", {}).get("id", None)
        

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_business_partner_md", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 核心功能测试 =============
    @case_decorator(
        story="合作伙伴主数据",
        title="测试新增合作伙伴",
        description="验证新增合作伙伴功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["合作伙伴", "新增"]
    )
    def test_save_business_partner(self):
        """新增合作伙伴用例"""
        try:
            partner_code = self.mock_util.generate_unique_code(tag="BP")
            partner_name = f"合作伙伴_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-合作伙伴-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["partnerCode", "partnerName", "partnerType", "status", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "partnerCode": partner_code,
                "partnerName": partner_name,
                "partnerType": "CUSTOMER",
                "status": "ENABLED",
                "remark": f"自动化测试合作伙伴-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.partner_id = response.get("data", {}).get("data", {})
            self.partner_code = partner_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试查询合作伙伴分页",
        description="验证合作伙伴分页查询功能",
        severity="normal",
        order=2,
        tags=["合作伙伴", "查询"]
    )
    def test_query_business_partner_page(self):
        """查询合作伙伴分页用例"""
        try:
            api_path = self.get_api_path("GEN-合作伙伴-查询分页服务")
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
                    {"name": "partnerCode", "type": "TEXT"},
                    {"name": "partnerName", "type": "TEXT"}
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
        story="合作伙伴主数据",
        title="测试查询合作伙伴详情",
        description="验证合作伙伴详情查询功能",
        severity="normal",
        order=3,
        tags=["合作伙伴", "详情"]
    )
    def test_query_business_partner_detail(self):
        """查询合作伙伴详情用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            api_path = self.get_api_path("GEN-合作伙伴-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试根据ID查找合作伙伴数据",
        description="验证根据ID查找合作伙伴数据功能",
        severity="normal",
        order=4,
        tags=["合作伙伴", "查找"]
    )
    def test_find_business_partner_by_id(self):
        """根据ID查找合作伙伴数据用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            api_path = self.get_api_path("合作伙伴-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.partner_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试合作伙伴分页数据服务",
        description="验证合作伙伴分页数据服务功能",
        severity="normal",
        order=5,
        tags=["合作伙伴", "分页数据"]
    )
    def test_business_partner_paging_data(self):
        """合作伙伴分页数据服务用例"""
        try:
            api_path = self.get_api_path("合作伙伴-分页数据服务")
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
        story="合作伙伴主数据",
        title="测试启用合作伙伴",
        description="验证启用合作伙伴功能",
        severity="normal",
        order=6,
        tags=["合作伙伴", "启用"]
    )
    def test_enable_business_partner(self):
        """启用合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            api_path = self.get_api_path("GEN-合作伙伴-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            # 注意：启用接口ID传单个值，不是列表
            set_dict = {"id": self.partner_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试禁用合作伙伴",
        description="验证禁用合作伙伴功能",
        severity="normal",
        order=7,
        tags=["合作伙伴", "禁用"]
    )
    def test_disable_business_partner(self):
        """禁用合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            api_path = self.get_api_path("GEN-合作伙伴-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            # 注意：禁用接口ID传单个值，不是列表
            set_dict = {"id": self.partner_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试提交合作伙伴导出任务",
        description="验证提交合作伙伴导出任务功能",
        severity="normal",
        order=8,
        tags=["合作伙伴", "导出任务"]
    )
    def test_submit_business_partner_export_task(self):
        """提交合作伙伴导出任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴导出任务_{self.mock_util.get_timestamp()}",
                "exportConfig": {
                    "fileName": f"合作伙伴_{self.mock_util.get_timestamp()}",
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
        story="合作伙伴主数据",
        title="测试删除合作伙伴",
        description="验证删除合作伙伴功能",
        severity="normal",
        order=9,
        tags=["合作伙伴", "删除"]
    )
    def test_delete_business_partner(self):
        """删除合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            api_path = self.get_api_path("GEN-合作伙伴-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            # 注意：删除接口ID传单个值，不是列表
            set_dict = {"id": self.partner_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="合作伙伴主数据",
        title="测试合作伙伴标准导出",
        description="验证合作伙伴标准导出功能",
        severity="normal",
        order=10,
        tags=["合作伙伴", "导出"]
    )
    def test_export_business_partner(self):
        """合作伙伴标准导出用例"""
        try:
            api_path = self.get_api_path("合作伙伴标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"合作伙伴导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "合作伙伴"
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
        story="合作伙伴主数据",
        title="测试合作伙伴标准导入",
        description="验证合作伙伴标准导入功能",
        severity="normal",
        order=11,
        tags=["合作伙伴", "导入"]
    )
    def test_import_business_partner(self):
        """合作伙伴标准导入用例"""
        try:
            api_path = self.get_api_path("合作伙伴标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"合作伙伴导入_{self.mock_util.get_timestamp()}",
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
        story="合作伙伴主数据",
        title="测试通过OSS提交合作伙伴导入任务",
        description="验证通过OSS提交合作伙伴导入任务功能",
        severity="normal",
        order=12,
        tags=["合作伙伴", "OSS导入"]
    )
    def test_submit_business_partner_import_task_by_oss(self):
        """通过OSS提交合作伙伴导入任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "合作伙伴"
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