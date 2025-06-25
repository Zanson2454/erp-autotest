import allure
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator



@allure.epic("属性管理" )
@allure.feature("属性管理")
class GenAttrManagement(GenMdBaseTest):
    
    def setup_class(self):
        super().setup_class()
        self.logger.info(f"init_data: {self.init_data}")
        self.logger.info(f"md_cache_data: {self.md_cache_data}")
        
        
    @case_decorator(
        story="查询通用属性配置",
        title="测试通用属性配置查询接口",
        description="验证通用属性配置查询接口的功能性",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["通用", "属性配置查询"]
    )
    def test_query_gen_attr_cf(self):
        # 1. 构造请求参数
        api_path = self.get_api_path("GEN-通用属性配置-查询分页服务")
        params, url = self.get_api_params(api_path)
        params["params"]["request"] = {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "conditionGroup": None,
                "sortOrders": None,
                "keyword": None
            },
            "keyword": None,
            "filterData": {}
        }
        self.logger.info(f"请求参数: {params}")

        # 2. 发送请求
        response = self.http.post(url, params=self.path_params, json=params)
        self.logger.info(f"响应: {response}")

        # 3. 断言
        self.assert_util.assert_response_data(response, "通用属性配置列表不为空")

        # 4. Allure 附件
        a.json(params, "请求数据")
        a.json(response, "响应数据")