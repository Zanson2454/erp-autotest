import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from pathlib import Path
from utils.yaml_util import YamlUtil
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("行业引导配置")
class TestIndustryGuide(BaseTest):
    industry_guide_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        init_gen_gm_config(cls)
    
    @case_decorator(
        story="行业引导配置管理",
        title="新增行业引导配置",
        description="验证新增行业引导配置功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["行业引导配置", "功能测试"]
    )
    def test_01_industry_guide_add(self):
        try:
            with a.step("新增行业引导配置"):
                # 生成测试数据
                guide_name = ParamUtil.generate_test_name("TEST_INDUSTRY_GUIDE")
                guide_desc = ParamUtil.generate_remark()
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["cardName", "cardDesc", "status", "cardOrder"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "cardName": guide_name,
                    "cardDesc": guide_desc,
                    "status": "ACTIVE",
                    "cardOrder": 1
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                guide_id = ParamUtil.extract_id(result)
                assert guide_id, "新增行业引导配置失败，未获取到ID"
                
                # 保存数据
                TestIndustryGuide.industry_guide_info.update({
                    "guide_id": guide_id,
                    "guide_name": guide_name,
                    "guide_desc": guide_desc
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestIndustryGuide.industry_guide_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="行业引导配置管理",
        title="查询行业引导配置详情",
        description="验证查询行业引导配置详情功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["行业引导配置", "功能测试"]
    )
    def test_02_industry_guide_query(self):
        try:
            with a.step("查询行业引导配置详情"):
                assert TestIndustryGuide.industry_guide_info.get("guide_id"), "未找到要查询的行业引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuide.industry_guide_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data.get("cardName") == TestIndustryGuide.industry_guide_info["guide_name"], "查询结果与创建数据不一致"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="行业引导配置管理",
        title="分页查询行业引导配置",
        description="验证分页查询行业引导配置功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["行业引导配置", "功能测试"]
    )
    def test_03_industry_guide_paging(self):
        try:
            with a.step("分页查询行业引导配置"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置-分页")
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

    @case_decorator(
        story="行业引导配置管理",
        title="禁用行业引导配置",
        description="验证禁用行业引导配置功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["行业引导配置", "功能测试"]
    )
    def test_04_industry_guide_disable(self):
        try:
            with a.step("禁用行业引导配置"):
                assert TestIndustryGuide.industry_guide_info.get("guide_id"), "未找到要禁用的行业引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuide.industry_guide_info["guide_id"]
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

    @case_decorator(
        story="行业引导配置管理",
        title="删除行业引导配置",
        description="验证删除行业引导配置功能",
        severity="normal",
        order=5,
        smoke=False,
        tags=["行业引导配置", "功能测试"]
    )
    def test_05_industry_guide_delete(self):
        try:
            with a.step("删除行业引导配置"):
                assert TestIndustryGuide.industry_guide_info.get("guide_id"), "未找到要删除的行业引导配置ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业引导配置-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["id"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryGuide.industry_guide_info["guide_id"]
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                # 清理测试数据
                TestIndustryGuide.industry_guide_info.clear()
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 