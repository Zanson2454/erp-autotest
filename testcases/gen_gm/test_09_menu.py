import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.report_util import a
from testcases.gen_gm import init_gen_gm_config

@allure.epic("通用基础")
@allure.feature("菜单管理")
class TestMenu(BaseTest):
    """菜单管理测试用例"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        init_gen_gm_config(cls)
    
    @ParamUtil.case_decorator(
        story="菜单管理",
        title="查询菜单树",
        description="测试查询菜单树的功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["菜单", "功能测试"]
    )
    def test_menu_tree_query(self):
        """测试查询菜单树"""
        try:
            with a.step("查询菜单树"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "菜单-查询")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["request"], ["params"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "request": {}
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
        story="菜单管理",
        title="查询菜单树（权限过滤）",
        description="测试查询菜单树（权限过滤）的功能",
        severity="normal",
        order=2,
        smoke=False,
        tags=["菜单", "功能测试"]
    )
    def test_menu_tree_query_with_auth(self):
        """测试查询菜单树（权限过滤）"""
        try:
            with a.step("查询菜单树（权限过滤）"):
                # 获取API配置
                api_path = ParamUtil.get_api_path(self.apis, "菜单-查询（权限过滤）")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["request"], ["params"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "request": {}
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