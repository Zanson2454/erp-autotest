import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("行业引导配置功能点")
class TestIndustryGuideFeature(BaseTest):
    industry_guide_feature_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="行业引导配置功能点管理",
        title="新增行业引导配置功能点",
        description="验证新增行业引导配置功能点功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["行业引导配置功能点", "功能测试"]
    )
    def test_01_industry_guide_feature_add(self):
        try:
            with a.step("新增行业引导配置功能点"):
                # 生成测试数据
                menu_name = ParamUtil.generate_test_name("TEST_MENU")
                menu_path = "/test/path"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置功能点-保存")
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
                assert feature_id, "新增行业引导配置功能点失败，未获取到ID"
                
                # 保存数据
                TestIndustryGuideFeature.industry_guide_feature_info.update({
                    "feature_id": feature_id,
                    "menu_name": menu_name,
                    "menu_path": menu_path
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestIndustryGuideFeature.industry_guide_feature_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="行业引导配置功能点管理",
        title="查询行业引导配置功能点详情",
        description="验证查询行业引导配置功能点详情功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["行业引导配置功能点", "功能测试"]
    )
    def test_02_industry_guide_feature_query(self):
        try:
            with a.step("查询行业引导配置功能点详情"):
                assert TestIndustryGuideFeature.industry_guide_feature_info.get("feature_id"), "未找到要查询的行业引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置功能点-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuideFeature.industry_guide_feature_info["feature_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data.get("menuName") == TestIndustryGuideFeature.industry_guide_feature_info["menu_name"], "查询结果与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="行业引导配置功能点管理",
        title="分页查询行业引导配置功能点",
        description="验证分页查询行业引导配置功能点功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["行业引导配置功能点", "功能测试"]
    )
    def test_03_industry_guide_feature_paging(self):
        try:
            with a.step("分页查询行业引导配置功能点"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置功能点-分页")
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
        story="行业引导配置功能点管理",
        title="禁用行业引导配置功能点",
        description="验证禁用行业引导配置功能点功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["行业引导配置功能点", "功能测试"]
    )
    def test_04_industry_guide_feature_disable(self):
        try:
            with a.step("禁用行业引导配置功能点"):
                assert TestIndustryGuideFeature.industry_guide_feature_info.get("feature_id"), "未找到要禁用的行业引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置功能点-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuideFeature.industry_guide_feature_info["feature_id"]
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
        story="行业引导配置功能点管理",
        title="删除行业引导配置功能点",
        description="验证删除行业引导配置功能点功能",
        severity="normal",
        order=5,
        smoke=False,
        tags=["行业引导配置功能点", "功能测试"]
    )
    def test_05_industry_guide_feature_delete(self):
        try:
            with a.step("删除行业引导配置功能点"):
                assert TestIndustryGuideFeature.industry_guide_feature_info.get("feature_id"), "未找到要删除的行业引导配置功能点ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置功能点-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuideFeature.industry_guide_feature_info["feature_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestIndustryGuideFeature.industry_guide_feature_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 