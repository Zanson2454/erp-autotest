import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("主数据管理")
@allure.feature("合作伙伴类型配置")
class TestPartnerTypeConfigCheck(GenMdBaseTest):
    """合作伙伴类型配置检查测试类"""

    def setup_class(self):
        super().setup_class()
        self.partnerType_info = {}

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型新增接口",
        description="验证合作伙伴类型新增（保存）接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["合作伙伴类型", "新增"]
    )
    def test_partner_type_save_customer(self):
        """
        新增客户类型用例
        """
        try:
            # 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-合作伙伴类型-保存服务")
            params, url = self.get_api_params(api_path)


            partner_type_code = self.mock_util.generate_unique_code(tag="CUST")
            partner_type_name = self.mock_util.get_mock_company()
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                [
                    "code", "name", "classType", "role", "desc", "isInternal", "isAddrRequired", "isBankRequired", "annexGroupId", "textGroupId", "partnerProcedureHeadId", "isOverseasPartner", "isNeedMaintainService"
                ],
                ["params", "request"]
            )
            set_dict = {
                "code": partner_type_code,
                "name": partner_type_name,
                "classType": "COMPANY",
                "role": "CUSTOMER",
                "desc": "测试客户类型",
                "isInternal": False,
                "isAddrRequired": False,
                "isBankRequired": False,
                "annexGroupId": None,
                "textGroupId": None,
                "partnerProcedureHeadId": None,
                "isOverseasPartner": False,
                "isNeedMaintainService": False
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            customer_type_id = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(customer_type_id is not None, "=", True)
            self.partnerType_info["customer_type_id"] = customer_type_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型新增供应商接口",
        description="验证合作伙伴类型新增供应商接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["合作伙伴类型", "新增", "供应商"]
    )
    def test_partner_type_save_supplier(self):
        """
        合作伙伴类型新增供应商用例
        """
        try:
            # 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-合作伙伴类型-保存服务")
            params, url = self.get_api_params(api_path)
            
            #  mock 供应商 code 和 name
            partner_type_code = self.mock_util.generate_unique_code(tag="SUPPLIER")
            partner_type_name = self.mock_util.get_mock_company()
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                [
                    "code", "name", "classType", "role", "desc", "isInternal", "isAddrRequired", "isBankRequired", "annexGroupId", "textGroupId", "partnerProcedureHeadId", "isOverseasPartner", "isNeedMaintainService"
                ],
                ["params", "request"]
            )
            set_dict = {
                "code": partner_type_code,
                "name": partner_type_name,
                "classType": "COMPANY",
                "role": "SUPPLIER",
                "desc": "测试供应商类型",
                "isInternal": False,
                "isAddrRequired": False,
                "isBankRequired": False,
                "annexGroupId": None,
                "textGroupId": None,
                "partnerProcedureHeadId": None,
                "isOverseasPartner": False,
                "isNeedMaintainService": False
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_by_operator(response.get("success"), "=", True)
            supplier_type_id = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(supplier_type_id is not None, "=", True)
            self.partnerType_info["supplier_type_id"] = supplier_type_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型新增服务供应商接口",
        description="验证合作伙伴类型新增服务供应商接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["合作伙伴类型", "新增", "服务供应商"]
    )
    def test_partner_type_save_service_supplier(self):
        """
        合作伙伴类型新增服务供应商用例
        """
        try:
            # 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-合作伙伴类型-保存服务")
            params, url = self.get_api_params(api_path)


            partner_type_code = self.mock_util.generate_unique_code(tag="SERVICE_SUPPLIER")
            partner_type_name = self.mock_util.get_mock_company()
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                [
                    "code", "name", "classType", "role", "desc", "isInternal", "isAddrRequired", "isBankRequired", "annexGroupId", "textGroupId", "partnerProcedureHeadId", "isOverseasPartner", "isNeedMaintainService"
                ],
                ["params", "request"]
            )
            set_dict = {
                "code": partner_type_code,
                "name": partner_type_name,
                "classType": "COMPANY",
                "role": "SUPPLIER",
                "desc": "测试服务供应商",
                "isInternal": False,
                "isAddrRequired": True,
                "isBankRequired": False,
                "annexGroupId": None,
                "textGroupId": None,
                "partnerProcedureHeadId": None,
                "isOverseasPartner": False,
                "isNeedMaintainService": True   
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的主键ID或成功标志
            service_supplier_type_id = response.get("data", {}).get("data", {})
            self.partnerType_info['service_supplier_type_id']=service_supplier_type_id
            self.assert_util.assert_by_operator(service_supplier_type_id, "not_empty")
            self.logger.info(f"服务供应商类型ID: {service_supplier_type_id}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型分页查询接口",
        description="验证合作伙伴类型分页查询接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["合作伙伴类型", "分页查询"]
    )
    def test_partner_type_query_page(self):
        """
        合作伙伴类型分页查询用例
        """
        try:
            # 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-合作伙伴类型-查询分页服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "isInternal", "type": "BOOL"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            total = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_response_success(response)
            self.assert_util.assert_by_operator(total, ">", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

   
    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型详情查询接口",
        description="验证合作伙伴类型详情查询接口的功能性",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["合作伙伴类型", "详情查询"]
    )
    def test_partner_type_detail(self):
        """
        合作伙伴类型详情查询用例，依赖 test_partner_type_save 先执行
        """
        try:
            # 查询详情
            api_path = self.get_api_path("GEN-合作伙伴类型-查询详情服务")
            params, url = self.get_api_params(api_path)
            
            partner_type_id= self.partnerType_info.get("customer_type_id")
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": partner_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"详情请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_by_operator(response.get("success"), "=", True)

            # 验证返回的详情信息
            partner_type_id = response.get("data", {}).get("data", {}).get("id")
            status = response.get("data", {}).get("data", {}).get("status")
            self.assert_util.assert_by_operator(partner_type_id, "not_empty")
            self.assert_util.assert_by_operator(status, "=", 'INACTIVE')
            
            a.json(filtered_params, "详情请求数据")
            a.json(response, "详情响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型启用接口",
        description="验证合作伙伴类型启用接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["合作伙伴类型", "启用"]
    )
    def test_partner_type_enable(self):
        """
        合作伙伴类型启用用例，依赖保存接口先执行
        """
        try:
            # 先创建一条数据，获取ID
            api_path_save = self.get_api_path("GEN-合作伙伴类型-启用服务")
            params_save, url_save = self.get_api_params(api_path_save)
            partner_type_id = self.partnerType_info.get("customer_type_id")
            filtered_params = ParamUtil.filter_post_body_fields(
                params_save,
                ["id"],
                ["params", "request"]
            )
            set_dict_save = {
                "id": partner_type_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict_save)
            self.logger.info(f"启用请求参数: {filtered_params}")

            response = self.http.post(url_save, json=filtered_params)
            self.assert_util.assert_by_operator(response.get("success"), "=", True)

            a.json(filtered_params, "启用请求数据")
            a.json(response, "启用响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型禁用接口",
        description="验证合作伙伴类型禁用接口的功能性",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["合作伙伴类型", "禁用"]
    )
    def test_partner_type_disable(self):
        """
        合作伙伴类型禁用用例，依赖保存接口先执行
        """
        try:
            # 先创建一条数据，获取ID
            api_path_save = self.get_api_path("GEN-合作伙伴类型-禁用服务")
            params, url = self.get_api_params(api_path_save)
            
            # 参数设置
            partner_type_id = self.partnerType_info.get("customer_type_id")
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                [
                    "id"
                ],
                ["params", "request"]
            )
            set_dict_save = {
                "id": partner_type_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict_save)
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

           

            a.json(filtered_params, "禁用请求数据")
            a.json(response, "禁用响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="合作伙伴类型配置",
        title="测试合作伙伴类型删除接口",
        description="验证合作伙伴类型删除接口的功能性（未启用可删除）",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["合作伙伴类型", "删除"]
    )
    def test_partner_type_delete(self):
        """
        合作伙伴类型删除用例，需先创建一条未启用的数据
        """
        try:
            # 删除接口
            if not self.partnerType_info.get("service_supplier_type_id"):
                self.test_partner_type_save_service_supplier()
            partner_type_id = self.partnerType_info.get("service_supplier_type_id")
            api_path = self.get_api_path("GEN-合作伙伴类型-删除服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": partner_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"删除请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_by_operator(response.get("success"), "=", True)

            a.json(filtered_params, "删除请求数据")
            a.json(response, "删除响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
