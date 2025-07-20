import allure
import pytest
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("其他查询服务")
class TestOtherQuery(SlsBase):
    """销售管理其他查询服务测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.sls_org_id = None
        cls.com_org_id = None
        cls.partner_class_id = None
        cls.logger.info("销售管理其他查询服务测试类初始化完成")
        
        # 获取依赖数据
        cls.sls_org_id = cls.md_cache_data.get("org_info", {}).get("sls_org_info", [])[0].get("id")
        cls.com_org_id = cls.md_cache_data.get("org_info", {}).get("com_org_info", [])[0].get("id")
        cls.partner_class_id = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id")

    @case_decorator(
        story="销售管理查询",
        title="测试根据销售组织查询关联组织信息",
        description="验证根据销售组织ID查询关联组织信息功能",
        severity="normal",
        order=1,
        tags=["销售管理", "组织查询"]
    )
    def test_query_relate_org_by_sls_org(self):
        """测试根据销售组织查询关联组织信息"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("根据销售组织查询关联组织信息")
            params, url = self.get_api_params(api_path)
            # 3. 发送请求和断言
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售管理查询",
        title="测试根据相关方类别查询相关方",
        description="验证根据相关方类别查询相关方功能",
        severity="normal",
        order=2,
        tags=["销售管理", "相关方查询"]
    )
    def test_query_cust_partner(self):
        """测试根据相关方类别查询相关方"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SO-根据相关方类别查询合作伙伴信息")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["prtnClassRef"], ["params"]
            )
            set_dict = {"prtnClassRef": self.partner_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售管理查询",
        title="测试根据相关方类别查询相关方详情",
        description="验证根据相关方类别查询相关方详情功能",
        severity="normal",
        order=3,
        tags=["销售管理", "相关方查询"]
    )
    def test_query_cust_partner_detail(self):
        """测试根据相关方类别查询相关方详情"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SO-根据相关方类别查询合作伙伴信息")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["prtnClassRef"], ["params"]
            )
            set_dict = {"prtnClassRef": self.partner_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售管理查询",
        title="测试根据公司组织查询币种",
        description="验证根据公司组织ID查询币种功能",
        severity="normal",
        order=4,
        tags=["销售管理", "币种查询"]
    )
    def test_query_currency_by_com_org(self):
        """测试根据公司组织查询币种"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("根据公司组织查询币种")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["currency_id"], ["params"]
            )
            set_dict = {"currency_id": self.com_org_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售管理查询",
        title="测试销售组织分页查询",
        description="验证销售组织分页查询功能",
        severity="normal",
        order=5,
        tags=["销售管理", "组织查询"]
    )
    def test_sls_sales_organization_paging(self):
        """测试销售组织分页查询"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售组织-分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
