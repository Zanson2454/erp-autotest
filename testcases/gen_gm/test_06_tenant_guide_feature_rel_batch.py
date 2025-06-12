import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("租户引导配置功能点关联批量操作")
class TestTenantGuideFeatureRelBatch(BaseTest):
    tenant_guide_feature_rel_batch_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联批量管理",
        title="批量新增租户引导配置功能点关联",
        description="验证批量新增租户引导配置功能点关联功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_01_tenant_guide_feature_rel_batch_add(self):
        try:
            with a.step("批量新增租户引导配置功能点关联"):
                # 生成测试数据
                guide_id = ParamUtil.generate_test_id()
                feature_ids = [ParamUtil.generate_test_id() for _ in range(3)]
                rel_orders = [1, 2, 3]
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-批量保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId", "featureIds", "relOrders", "status"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": guide_id,
                    "featureIds": feature_ids,
                    "relOrders": rel_orders,
                    "status": "ACTIVE"
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 保存数据
                TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info.update({
                    "guide_id": guide_id,
                    "feature_ids": feature_ids,
                    "rel_orders": rel_orders
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联批量管理",
        title="批量查询租户引导配置功能点关联",
        description="验证批量查询租户引导配置功能点关联功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_02_tenant_guide_feature_rel_batch_query(self):
        try:
            with a.step("批量查询租户引导配置功能点关联"):
                assert TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info.get("guide_id"), "未找到要查询的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-批量查询")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", [])
                assert len(response_data) == len(TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info["feature_ids"]), "查询结果数量与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联批量管理",
        title="批量禁用租户引导配置功能点关联",
        description="验证批量禁用租户引导配置功能点关联功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_03_tenant_guide_feature_rel_batch_disable(self):
        try:
            with a.step("批量禁用租户引导配置功能点关联"):
                assert TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info.get("guide_id"), "未找到要禁用的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-批量禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info["guide_id"]
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
        story="租户引导配置功能点关联批量管理",
        title="批量删除租户引导配置功能点关联",
        description="验证批量删除租户引导配置功能点关联功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_04_tenant_guide_feature_rel_batch_delete(self):
        try:
            with a.step("批量删除租户引导配置功能点关联"):
                assert TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info.get("guide_id"), "未找到要删除的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-批量删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestTenantGuideFeatureRelBatch.tenant_guide_feature_rel_batch_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 