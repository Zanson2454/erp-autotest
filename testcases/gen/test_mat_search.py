import os
import sys
import allure
from pathlib import Path
from testcases.gen import GenBaseTest
from utils.allure_simple import a
from utils.param_util import ParamUtil

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("物料管理_物料列表查询")
class TestMatSearch(GenBaseTest):
    @classmethod
    def setup_class(cls):
        # 调用父类的初始化方法，会自动加载API配置
        super().setup_class()
        cls.logger.info("物料查询测试类初始化完成")
        
    @allure.story("物料列表查询")
    @allure.description("""
    ## 测试步骤
    1. 获取接口路径和参数
    2. 发送查询请求
    3. 验证响应结果
    4. 验证数据内容
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("物料列表查询")
    @allure.tag("物料管理", "功能测试")
    def test_mat_search(self):
        try:
            with a.step("1. 获取接口路径和参数"):
                # 获取API路径
                api_path = self.get_api_path("物料主数据定义表-分页数据服务")
                self.logger.debug(f"物料查询API路径: {api_path}")
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                # 使用ParamUtil.filter_post_body_fields过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                ["slsOrgId","cateId","slsDcId","pageable"],["params", "request"])
                
                # 使用基类方法批量设置参数
                self.set_request_params(filtered_params, {
                    "slsOrgId": 0,
                    "cateId": 0,
                    "slsDcId": 0,
                    "pageable": {
                        "sortOrders": []
                    }
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求参数到报告
                a.json(filtered_params, "请求参数")
            with a.step("2. 发送查询请求"):
                # 发送POST请求并获取响应
                result = self.http.post(url, json=filtered_params, description="查询物料列表")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
                # 解析响应数据
                response_data = result.get("data", {}).get("data", {})
            
            with a.step("3. 验证响应结果"):
                # 验证响应结果
                self.assert_util.assert_response_success(result)
                # 验证返回的total字段
                total = response_data.get("total")  
                assert total is not None and total > 0, f"物料总数异常: {total}"
                # 记录验证结果
                a.text(f"物料总数: {total}", "验证结果 - 总数")
            with a.step("4. 验证数据内容"):
                # 验证返回的数据列表
                data_list = response_data.get("data", [])
                assert len(data_list) > 0, "返回的物料列表为空"
                # 记录验证结果
                a.text(f"当前页物料数量: {len(data_list)}", "验证结果 - 列表数量")
                # 添加物料列表的第一条记录到报告中
                if len(data_list) > 0:
                    a.json(data_list[0], "物料记录示例")
                self.logger.info(f"物料列表查询完成，总记录数: {total}")
        except Exception as e:
            self.logger.error(f"物料列表查询失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise
if __name__ == "__main__":
    # 直接运行测试用例
    test = TestMatSearch()
    test.setup_class()
    test.test_mat_search()