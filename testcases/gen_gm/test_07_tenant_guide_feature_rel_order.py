import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("租户引导配置功能点关联排序")
class TestTenantGuideFeatureRelOrder(BaseTest):
    tenant_guide_feature_rel_order_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联排序管理",
        title="新增租户引导配置功能点关联排序",
        description="验证新增租户引导配置功能点关联排序功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_01_tenant_guide_feature_rel_order_add(self):
        try:
            with a.step("新增租户引导配置功能点关联排序"):
                # 生成测试数据
                guide_id = ParamUtil.generate_test_id()
                feature_ids = [ParamUtil.generate_test_id() for _ in range(3)]
                rel_orders = [1, 2, 3]
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-保存")
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
                TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info.update({
                    "guide_id": guide_id,
                    "feature_ids": feature_ids,
                    "rel_orders": rel_orders
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联排序管理",
        title="更新租户引导配置功能点关联排序",
        description="验证更新租户引导配置功能点关联排序功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_02_tenant_guide_feature_rel_order_update(self):
        try:
            with a.step("更新租户引导配置功能点关联排序"):
                assert TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info.get("guide_id"), "未找到要更新的租户引导配置ID，请先执行新增用例"
                
                # 生成新的排序数据
                new_rel_orders = [3, 2, 1]  # 反转排序
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-更新排序")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId", "featureIds", "relOrders"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["guide_id"],
                    "featureIds": TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["feature_ids"],
                    "relOrders": new_rel_orders
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 更新保存的数据
                TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["rel_orders"] = new_rel_orders
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联排序管理",
        title="查询租户引导配置功能点关联排序",
        description="验证查询租户引导配置功能点关联排序功能",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_03_tenant_guide_feature_rel_order_query(self):
        try:
            with a.step("查询租户引导配置功能点关联排序"):
                assert TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info.get("guide_id"), "未找到要查询的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-查询排序")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", [])
                assert len(response_data) == len(TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["feature_ids"]), "查询结果数量与创建数据不一致"
                
                # 验证排序
                for item in response_data:
                    assert item.get("relOrder") in TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["rel_orders"], "查询结果排序与更新数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="租户引导配置功能点关联排序管理",
        title="删除租户引导配置功能点关联排序",
        description="验证删除租户引导配置功能点关联排序功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["租户引导配置功能点关联", "功能测试"]
    )
    def test_04_tenant_guide_feature_rel_order_delete(self):
        try:
            with a.step("删除租户引导配置功能点关联排序"):
                assert TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info.get("guide_id"), "未找到要删除的租户引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "租户引导功能点关联-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["guideId"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "guideId": TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestTenantGuideFeatureRelOrder.tenant_guide_feature_rel_order_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 