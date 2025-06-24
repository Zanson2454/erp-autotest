import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import pytest


@allure.epic("组织管理")
@allure.feature("行政组织管理")
class TestAdmOrgManagement(GenMdBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.org_info = {}
        cls.mock_data = MockData()
        cls.logger.info(f"init_data: {cls.init_data}")
        cls.logger.info(f"md_cache_data: {cls.md_cache_data}")
        
        # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.genWcHeadId = cls.init_data["gen_wc_head_info"][0]["gen_wc_head_id"] if cls.init_data.get("gen_wc_head_info") else None
        cls.calenderId = cls.init_data["calender_info"][0]["id"] if cls.init_data.get("calender_info") else None
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
        
        # 获取md_cache_data中的第一个数据
        cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
        cls.logger.info(f"orgBusinessTypeIds: {cls.orgBusinessTypeIds}")
        for org_biz_type in cls.orgBusinessTypeIds:
            if org_biz_type["code"] == "ADM_ORG":  # 行政组织类型
                cls.admOrgTypeId = org_biz_type["id"]

    @case_decorator(
        story="保存行政组织",
        title="测试保存行政组织",
        description="验证保存行政组织接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["行政组织", "保存组织"]
    )
    def test_save_adm_org(self):
        """
        保存行政组织用例
        """
        try:
            org_code = self.mock_data.generate_unique_code(tag="AdmOrg")
            org_name = self.mock_data.get_mock_company()
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 9999,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.admOrgTypeId],
                "orgDimensionCode": "ADM_ORG_GRP"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestAdmOrgManagement.org_info.update({
                "adm_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="启用行政组织",
        title="测试启用行政组织",
        description="验证启用行政组织接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["行政组织", "启用组织"]
    )
    def test_enable_adm_org(self):
        """
        启用行政组织用例
        """
        try:
            # 获取行政组织信息
            adm_org_info = TestAdmOrgManagement.org_info.get("adm_org_info", {})
            org_id = adm_org_info.get("id")
            assert org_id, "请先执行test_save_adm_org并成功保存行政组织"

            api_path = self.get_api_path("ORG-组织管理-启动EHR组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="停用行政组织",
        title="测试停用行政组织",
        description="验证停用行政组织接口的功能性",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["行政组织", "停用组织"]
    )
    def test_disable_adm_org(self):
        """
        停用行政组织用例
        """
        try:
            # 获取行政组织信息
            adm_org_info = TestAdmOrgManagement.org_info.get("adm_org_info", {})
            org_id = adm_org_info.get("id")
            assert org_id, "请先执行test_save_adm_org并成功保存行政组织"

            api_path = self.get_api_path("ORG-组织管理-停用组织EHR组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="删除行政组织",
        title="测试删除行政组织",
        description="验证删除行政组织接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["行政组织", "删除组织"]
    )
    def test_delete_adm_org(self):
        """
        删除行政组织用例
        """
        try:
            # 获取行政组织信息
            adm_org_info = TestAdmOrgManagement.org_info.get("adm_org_info", {})
            org_id = adm_org_info.get("id")
            assert org_id, "请先执行test_save_adm_org并成功保存行政组织"

            api_path = self.get_api_path("ORG-组织管理-删除EHR组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 清除组织信息
            TestAdmOrgManagement.org_info = {}

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询行政组织",
        title="测试查询行政组织",
        description="验证查询行政组织接口的功能性",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["行政组织", "查询组织"]
    )
    def test_query_adm_org(self):
        """
        查询行政组织用例
        """
        try:
            api_path = self.get_api_path("ORG-新版组织-搜索服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgDimensionCode", "orgStatus"],
                ["params", "request"]
            )
            set_dict = {
                "orgDimensionCode": "ADM_ORG_GRP",
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT", "DISABLED"]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    