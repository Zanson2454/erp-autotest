import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("租户信息管理")
class TestTenantInfo(BaseTest):
    """租户信息管理测试用例"""
    
    tenant_info = {}
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="创建租户信息",
        description="测试创建租户信息的功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_add(self):
        """测试创建租户信息"""
        try:
            with a.step("创建租户信息"):
                # 生成测试数据
                tenant_name = ParamUtil.generate_test_name("TEST_TENANT")
                tenant_code = ParamUtil.generate_unique_code("TEN")
                admin_name = ParamUtil.generate_test_name("ADMIN")
                admin_phone = f"1{ParamUtil.generate_random_number(10)}"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["tenantName", "tenantCode", "adminName", "adminPhone", "status"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "tenantName": tenant_name,
                    "tenantCode": tenant_code,
                    "adminName": admin_name,
                    "adminPhone": admin_phone,
                    "status": "ENABLE"
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                tenant_id = ParamUtil.extract_id(result)
                assert tenant_id, "创建租户信息失败，未返回ID"
                
                # 保存数据
                TestTenantInfo.tenant_info.update({
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_name,
                    "tenant_code": tenant_code,
                    "admin_name": admin_name,
                    "admin_phone": admin_phone
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantInfo.tenant_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="查询租户信息详情",
        description="测试查询租户信息详情的功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_query(self):
        """测试查询租户信息详情"""
        try:
            with a.step("查询租户信息详情"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要查询的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantInfo.tenant_info["tenant_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                data = result.json()["data"]
                assert data["tenantName"] == TestTenantInfo.tenant_info["tenant_name"], "租户名称不匹配"
                assert data["tenantCode"] == TestTenantInfo.tenant_info["tenant_code"], "租户编码不匹配"
                assert data["adminName"] == TestTenantInfo.tenant_info["admin_name"], "管理员名称不匹配"
                assert data["adminPhone"] == TestTenantInfo.tenant_info["admin_phone"], "管理员电话不匹配"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="分页查询租户信息",
        description="测试分页查询租户信息的功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_paging(self):
        """测试分页查询租户信息"""
        try:
            with a.step("分页查询租户信息"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-分页")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20
                    }
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="禁用租户信息",
        description="测试禁用租户信息的功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_disable(self):
        """测试禁用租户信息"""
        try:
            with a.step("禁用租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要禁用的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantInfo.tenant_info["tenant_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="启用租户信息",
        description="测试启用租户信息的功能",
        severity="normal",
        order=5,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_enable(self):
        """测试启用租户信息"""
        try:
            with a.step("启用租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要启用的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-启用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantInfo.tenant_info["tenant_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="批量启用租户信息",
        description="测试批量启用租户信息的功能",
        severity="normal",
        order=6,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_enable_batch(self):
        """测试批量启用租户信息"""
        try:
            with a.step("批量启用租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要启用的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-批量启用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestTenantInfo.tenant_info["tenant_id"]]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="批量禁用租户信息",
        description="测试批量禁用租户信息的功能",
        severity="normal",
        order=7,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_disable_batch(self):
        """测试批量禁用租户信息"""
        try:
            with a.step("批量禁用租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要禁用的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-批量禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestTenantInfo.tenant_info["tenant_id"]]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="删除租户信息",
        description="测试删除租户信息的功能",
        severity="normal",
        order=8,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_delete(self):
        """测试删除租户信息"""
        try:
            with a.step("删除租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要删除的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantInfo.tenant_info["tenant_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="批量删除租户信息",
        description="测试批量删除租户信息的功能",
        severity="normal",
        order=9,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_delete_batch(self):
        """测试批量删除租户信息"""
        try:
            with a.step("批量删除租户信息"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要删除的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-批量删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestTenantInfo.tenant_info["tenant_id"]]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="更换企业管理员",
        description="测试更换企业管理员的功能",
        severity="normal",
        order=10,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_change_admin(self):
        """测试更换企业管理员"""
        try:
            with a.step("更换企业管理员"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要操作的租户信息ID，请先执行新增用例"
                
                # 生成新管理员信息
                new_admin_name = ParamUtil.generate_test_name("NEW_ADMIN")
                new_admin_phone = f"1{ParamUtil.generate_random_number(10)}"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户信息-更换企业管理员")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id", "adminEmpNew"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantInfo.tenant_info["tenant_id"],
                    "adminEmpNew": {
                        "name": new_admin_name,
                        "phone": new_admin_phone
                    }
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 更新测试数据
                TestTenantInfo.tenant_info.update({
                    "admin_name": new_admin_name,
                    "admin_phone": new_admin_phone
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantInfo.tenant_info, "更新后的租户信息")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="租户信息管理",
        title="查询租户下员工",
        description="测试查询租户下员工的功能",
        severity="normal",
        order=11,
        smoke=False,
        tags=["租户信息", "功能测试"]
    )
    def test_tenant_query_employees(self):
        """测试查询租户下员工"""
        try:
            with a.step("查询租户下员工"):
                assert TestTenantInfo.tenant_info.get("tenant_id"), "未找到要查询的租户信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "查询租户下员工")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["tenantId", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "tenantId": TestTenantInfo.tenant_info["tenant_id"],
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20
                    }
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 