import allure
from testcases.gen import GenBaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a

@allure.epic("通用基础")
@allure.feature("租户引导配置功能点关联")
class TestTenantGuideFeatureRel(GenBaseTest):
    tenant_guide_feature_rel_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
    
    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联管理",
        title="新增租户引导配置功能点关联",
        description="验证新增租户引导配置功能点关联功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_01_tenant_guide_feature_rel_add(self):
        try:
            with a.step("新增租户引导配置功能点关联"):
                # 生成测试数据
                guide_id = ParamUtil.generate_test_id()
                feature_id = ParamUtil.generate_test_id()
                rel_order = 1
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId", "featureId", "relOrder", "status"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": guide_id,
                    "featureId": feature_id,
                    "relOrder": rel_order,
                    "status": "ACTIVE"
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                rel_id = ParamUtil.extract_id(result)
                assert rel_id, "新增租户引导配置功能点关联失败，未获取到ID"
                
                # 保存数据
                TestTenantGuideFeatureRel.tenant_guide_feature_rel_info.update({
                    "rel_id": rel_id,
                    "guide_id": guide_id,
                    "feature_id": feature_id,
                    "rel_order": rel_order
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuideFeatureRel.tenant_guide_feature_rel_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联管理",
        title="查询租户引导配置功能点关联详情",
        description="验证查询租户引导配置功能点关联详情功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_02_tenant_guide_feature_rel_query(self):
        try:
            with a.step("查询租户引导配置功能点关联详情"):
                assert TestTenantGuideFeatureRel.tenant_guide_feature_rel_info.get("rel_id"), "未找到要查询的租户引导配置功能点关联ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeatureRel.tenant_guide_feature_rel_info["rel_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data.get("guideId") == TestTenantGuideFeatureRel.tenant_guide_feature_rel_info["guide_id"], "查询结果与创建数据不一致"
                assert response_data.get("featureId") == TestTenantGuideFeatureRel.tenant_guide_feature_rel_info["feature_id"], "查询结果与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联管理",
        title="禁用租户引导配置功能点关联",
        description="验证禁用租户引导配置功能点关联功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_03_tenant_guide_feature_rel_disable(self):
        try:
            with a.step("禁用租户引导配置功能点关联"):
                assert TestTenantGuideFeatureRel.tenant_guide_feature_rel_info.get("rel_id"), "未找到要禁用的租户引导配置功能点关联ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeatureRel.tenant_guide_feature_rel_info["rel_id"]
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
        story="租户引导配置功能点关联管理",
        title="删除租户引导配置功能点关联",
        description="验证删除租户引导配置功能点关联功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_04_tenant_guide_feature_rel_delete(self):
        try:
            with a.step("删除租户引导配置功能点关联"):
                assert TestTenantGuideFeatureRel.tenant_guide_feature_rel_info.get("rel_id"), "未找到要删除的租户引导配置功能点关联ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestTenantGuideFeatureRel.tenant_guide_feature_rel_info["rel_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestTenantGuideFeatureRel.tenant_guide_feature_rel_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 