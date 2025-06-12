import allure
from testcases.gen import GenBaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a

@allure.epic("通用基础")
@allure.feature("租户引导配置功能点")
class TestTenantGuideFeature(GenBaseTest):
    tenant_guide_feature_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
    
    @ParamUtil.case_decorator(
        story="租户引导配置功能点管理",
        title="新增租户引导配置功能点",
        description="验证新增租户引导配置功能点功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户引导配置功能点", "功能测试"]
    )
    def test_01_tenant_guide_feature_add(self):
        try:
            with a.step("新增租户引导配置功能点"):
                # 生成测试数据
                menu_name = ParamUtil.generate_test_name("TEST_MENU")
                menu_path = "/test/path"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["menuName", "menuPath", "featureOrder", "status"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "menuName": menu_name,
                    "menuPath": menu_path,
                    "featureOrder": 1,
                    "status": "ACTIVE"
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                feature_id = ParamUtil.extract_id(result)
                assert feature_id, "新增租户引导配置功能点失败，未获取到ID"
                
                # 保存数据
                TestTenantGuideFeature.tenant_guide_feature_info.update({
                    "feature_id": feature_id,
                    "menu_name": menu_name,
                    "menu_path": menu_path
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuideFeature.tenant_guide_feature_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点管理",
        title="查询租户引导配置功能点详情",
        description="验证查询租户引导配置功能点详情功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户引导配置功能点", "功能测试"]
    )
    def test_02_tenant_guide_feature_query(self):
        try:
            with a.step("查询租户引导配置功能点详情"):
                assert TestTenantGuideFeature.tenant_guide_feature_info.get("feature_id"), "未找到要查询的租户引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeature.tenant_guide_feature_info["feature_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data.get("menuName") == TestTenantGuideFeature.tenant_guide_feature_info["menu_name"], "查询结果与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点管理",
        title="禁用租户引导配置功能点",
        description="验证禁用租户引导配置功能点功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["租户引导配置功能点", "功能测试"]
    )
    def test_03_tenant_guide_feature_disable(self):
        try:
            with a.step("禁用租户引导配置功能点"):
                assert TestTenantGuideFeature.tenant_guide_feature_info.get("feature_id"), "未找到要禁用的租户引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeature.tenant_guide_feature_info["feature_id"]
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
        story="租户引导配置功能点管理",
        title="删除租户引导配置功能点",
        description="验证删除租户引导配置功能点功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户引导配置功能点", "功能测试"]
    )
    def test_04_tenant_guide_feature_delete(self):
        try:
            with a.step("删除租户引导配置功能点"):
                assert TestTenantGuideFeature.tenant_guide_feature_info.get("feature_id"), "未找到要删除的租户引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeature.tenant_guide_feature_info["feature_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestTenantGuideFeature.tenant_guide_feature_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 