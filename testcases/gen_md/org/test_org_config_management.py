import allure
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator

@allure.epic("组织管理")
@allure.feature("组织类型查询")
class TestOrgTypeQuery(GenMdBaseTest):
    path_params = {"tmodule":"GEN_MD"}
    def setup_class(self):
        super().setup_class()
    
    @case_decorator(
        story="查询组织类型",
        title="测试组织类型查询接口",
        description="验证组织类型查询接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织", "类型查询"]
    )
    def test_query_org_type(self):
        # 1. 构造请求参数
        api_path = self.get_api_path("ORG-组织架构-查询组织类型列表服务")
        params, url = self.get_api_params(api_path)
        # 只保留必要参数
        params["params"] = {
            "request": {
                "orgDimensionCode": "SCM_ORG_GRP"
            }
        }
        self.logger.info(f"请求参数: {params}")

        # 2. 发送请求
        response = self.http.post(url, json=params)
        self.logger.info(f"响应: {response}")

        # 3. 断言
        self.assert_util.assert_response_data(response,"组织类型列表为空")

        # 4. Allure 附件
        a.json(params, "请求数据")
        a.json(response, "响应数据")

    @case_decorator(
        story="查询组织业务类型",
        title="测试组织业务类型查询接口",
        description="验证组织业务类型查询接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["组织", "业务类型查询"]
    )
    def test_query_org_business_type(self):
        # 1. 构造请求参数
        api_path = self.get_api_path("GEN-组织类型-查询分页服务")
        params,url = self.get_api_params(api_path)
        params["params"]["request"] = {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None
                    },
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "status", "type": "SELECT"}
                    ],
                    "systemParams": None
                }

        self.logger.info(f"请求参数: {params}")

        # 2. 发送请求
        response = self.http.post(url, params = self.path_params,json=params)
        self.logger.info(f"响应: {response}")

        # 3. 断言
        self.assert_util.assert_response_data(response, "组织业务类型列表不为空")

        # 4. Allure 附件
        a.json(params, "请求数据")
        a.json(response, "响应数据")
