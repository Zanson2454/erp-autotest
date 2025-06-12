import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from pathlib import Path
from utils.yaml_util import YamlUtil


@allure.epic("通用基础")
@allure.feature("行业信息管理")
class TestIndustryInfo(BaseTest):
    """行业信息管理测试用例"""
    
    industry_info = {}
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        
        # 初始化 API 配置
        project_root = Path(__file__).resolve().parent.parent.parent
        api_path_yaml = project_root / "testdata" / "gen_gm" / "gm_api_path.yaml"
        api_params_yaml = project_root / "testdata" / "gen_gm" / "gm_api_params.yaml"
        
        # 读取 API 配置
        cls.apis = YamlUtil.read_yaml(str(api_path_yaml))["apis"]
        cls.api_params = YamlUtil.read_yaml(str(api_params_yaml))["api_params"]
        

    
    @ParamUtil.case_decorator(
        story="行业信息管理",
        title="创建行业信息",
        description="测试创建行业信息的功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_add(self):
        """测试创建行业信息"""
        try:
            with a.step("创建行业信息"):
                # 生成测试数据
                industry_name = ParamUtil.generate_test_name("TEST_INDUSTRY")
                industry_desc = ParamUtil.generate_remark()
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-保存")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["industryName", "industryDesc", "status"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "industryName": industry_name,
                    "industryDesc": industry_desc,
                    "status": "ENABLE"
                })
                
                # 发送请求并验证
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                industry_id = ParamUtil.extract_id(result)
                assert industry_id, "创建行业信息失败，未返回ID"
                
                # 保存数据
                TestIndustryInfo.industry_info.update({
                    "industry_id": industry_id,
                    "industry_name": industry_name,
                    "industry_desc": industry_desc
                })
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestIndustryInfo.industry_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="行业信息管理",
        title="查询行业信息详情",
        description="测试查询行业信息详情的功能",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_query(self):
        """测试查询行业信息详情"""
        try:
            with a.step("查询行业信息详情"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要查询的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-详情")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": self.industry_info["industry_id"]
                })

                result = self.http.post(url, json=filtered_params)
                self.logger.debug(f"result: {result}")
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                data = result['data']['data']
                self.logger.info(f"TestIndustryInfo.industry_info: {TestIndustryInfo.industry_info}")
                assert data["industryName"] == TestIndustryInfo.industry_info["industry_name"], "行业名称不匹配"
                assert data["industryDesc"] == TestIndustryInfo.industry_info["industry_desc"], "行业描述不匹配"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @ParamUtil.case_decorator(
        story="行业信息管理",
        title="分页查询行业信息",
        description="测试分页查询行业信息的功能",
        severity="normal",
        order=3,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_paging(self):
        """测试分页查询行业信息"""
        try:
            with a.step("分页查询行业信息"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-分页")
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
        story="行业信息管理",
        title="禁用行业信息",
        description="测试禁用行业信息的功能",
        severity="normal",
        order=4,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_disable(self):
        """测试禁用行业信息"""
        try:
            with a.step("禁用行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要禁用的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryInfo.industry_info["industry_id"]
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
        story="行业信息管理",
        title="启用行业信息",
        description="测试启用行业信息的功能",
        severity="normal",
        order=5,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_enable(self):
        """测试启用行业信息"""
        try:
            with a.step("启用行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要启用的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-启用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryInfo.industry_info["industry_id"]
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
        story="行业信息管理",
        title="批量启用行业信息",
        description="测试批量启用行业信息的功能",
        severity="normal",
        order=6,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_enable_batch(self):
        """测试批量启用行业信息"""
        try:
            with a.step("批量启用行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要启用的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-批量启用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestIndustryInfo.industry_info["industry_id"]]
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
        story="行业信息管理",
        title="批量禁用行业信息",
        description="测试批量禁用行业信息的功能",
        severity="normal",
        order=7,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_disable_batch(self):
        """测试批量禁用行业信息"""
        try:
            with a.step("批量禁用行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要禁用的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-批量禁用")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestIndustryInfo.industry_info["industry_id"]]
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
        story="行业信息管理",
        title="删除行业信息",
        description="测试删除行业信息的功能",
        severity="normal",
        order=8,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_delete(self):
        """测试删除行业信息"""
        try:
            with a.step("删除行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要删除的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestIndustryInfo.industry_info["industry_id"]
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
        story="行业信息管理",
        title="批量删除行业信息",
        description="测试批量删除行业信息的功能",
        severity="normal",
        order=9,
        smoke=False,
        tags=["行业信息", "功能测试"]
    )
    def test_industry_delete_batch(self):
        """测试批量删除行业信息"""
        try:
            with a.step("批量删除行业信息"):
                assert TestIndustryInfo.industry_info.get("industry_id"), "未找到要删除的行业信息ID，请先执行新增用例"
                
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "行业信息-批量删除")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "ids": [TestIndustryInfo.industry_info["industry_id"]]
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