import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("租户引导配置")
class TestTenantGuide(BaseTest):
    tenant_guide_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="租户引导配置管理",
        title="新增租户引导配置",
        description="验证新增租户引导配置功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户引导配置", "功能测试"]
    )
    def test_01_tenant_guide_add(self):
        try:
            with a.step("新增租户引导配置"):
                # 生成测试数据
                card_name = ParamUtil.generate_test_name("TEST_TENANT_GUIDE")
                card_desc = ParamUtil.generate_remark()
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导配置-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["cardName", "cardDescription", "status", "cardOrder"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "cardName": card_name,
                    "cardDescription": card_desc,
                    "status": "ACTIVE",
                    "cardOrder": 1
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                guide_id = ParamUtil.extract_id(result)
                assert guide_id, "新增租户引导配置失败，未获取到ID"
                
                # 保存数据
                TestTenantGuide.tenant_guide_info.update({
                    "guide_id": guide_id,
                    "card_name": card_name,
                    "card_desc": card_desc
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuide.tenant_guide_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置管理",
        title="查询租户引导配置详情",
        description="验证查询租户引导配置详情功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户引导配置", "功能测试"]
    )
    def test_02_tenant_guide_query(self):
        try:
            with a.step("查询租户引导配置详情"):
                assert TestTenantGuide.tenant_guide_info.get("guide_id"), "未找到要查询的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导配置-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuide.tenant_guide_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data.get("cardName") == TestTenantGuide.tenant_guide_info["card_name"], "查询结果与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置管理",
        title="分页查询租户引导配置",
        description="验证分页查询租户引导配置功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["租户引导配置", "功能测试"]
    )
    def test_03_tenant_guide_paging(self):
        try:
            with a.step("分页查询租户引导配置"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导配置-分页")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["pageable"], 
                    ["params", "request"]
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
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert "content" in response_data, "分页查询结果格式不正确"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置管理",
        title="禁用租户引导配置",
        description="验证禁用租户引导配置功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户引导配置", "功能测试"]
    )
    def test_04_tenant_guide_disable(self):
        try:
            with a.step("禁用租户引导配置"):
                assert TestTenantGuide.tenant_guide_info.get("guide_id"), "未找到要禁用的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导配置-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuide.tenant_guide_info["guide_id"]
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
        story="租户引导配置管理",
        title="删除租户引导配置",
        description="验证删除租户引导配置功能",
        severity="normal",
        order=5,
        smoke=False,
        tags=["租户引导配置", "功能测试"]
    )
    def test_05_tenant_guide_delete(self):
        try:
            with a.step("删除租户引导配置"):
                assert TestTenantGuide.tenant_guide_info.get("guide_id"), "未找到要删除的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导配置-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuide.tenant_guide_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestTenantGuide.tenant_guide_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 