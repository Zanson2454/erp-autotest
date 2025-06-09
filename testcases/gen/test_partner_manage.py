import allure
from testcases.gen import GenBaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a

@allure.epic("通用基础")
@allure.feature("合作伙伴管理")
class TestPartnerSimplified(GenBaseTest):
    partner_info = {}
    @classmethod
    def setup_class(cls):
        super().setup_class()
    @ParamUtil.case_decorator(
        story="新增合作伙伴",
        title="新增合作伙伴流程",
        description="验证新增合作伙伴功能全流程正确性（覆盖基础信息生成、请求构造、接口发送、响应校验及数据保存）",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["合作伙伴管理", "功能测试"]
    )
    def test_partner_add(self):
        try:
            with a.step("新增合作伙伴流程"):
                partner_code = ParamUtil.generate_unique_code("PAR")
                partner_name = ParamUtil.generate_test_name("TEST_PARTNER")
                remark = ParamUtil.generate_remark()
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-合作伙伴保存服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["code", "name", "classType", "status", "partnerTypeId", "partnerIdentity"], 
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "code": partner_code,
                    "name": partner_name,
                    "classType": "COMPANY",
                    "status": "INACTIVE",
                    "partnerTypeId": {"id": 2011001},
                    "partnerIdentity": ["SUPPLIER"]
                })
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                partner_id = ParamUtil.extract_id(result)
                assert partner_id, "新增合作伙伴失败：返回的ID为空"
                
                TestPartnerSimplified.partner_info.update({
                    "partner_id": partner_id,
                    "partner_code": partner_code,
                    "partner_name": partner_name
                })
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestPartnerSimplified.partner_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="查询合作伙伴",
        title="查询合作伙伴流程",
        description="验证合作伙伴查询功能正确性（覆盖查询条件构造、分页查询接口、结果校验及数据匹配验证）",
        severity="normal",
        order=2,
        tags=["合作伙伴管理", "功能测试"]
    )
    def test_partner_search(self):
        try:
            with a.step("查询合作伙伴流程"):
                assert TestPartnerSimplified.partner_info.get("partner_code"), "未找到要查询的合作伙伴编码，请先执行新增用例"
                api_path = ParamUtil.get_api_path(self.apis, "合作伙伴-分页数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["conditionItems", "pageable"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "pageable": {
                        "conditionItems": {
                            "conditions": {
                                "code": {
                                    "operator": "CONTAINS",
                                    "value": TestPartnerSimplified.partner_info["partner_code"]
                                }
                            }
                        },
                        "sortOrders": None
                    }
                })
            
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                total = response_data.get("total", 0)
                assert total > 0, "查询结果总数为0"
                
                data_list = response_data.get("data", [])
                assert data_list, "查询结果为空"
                
                found = any(item.get("code") == TestPartnerSimplified.partner_info["partner_code"] for item in data_list)
                assert found, f"未找到合作伙伴编码: {TestPartnerSimplified.partner_info['partner_code']}"
                
                a.text(f"预置数据: {TestPartnerSimplified.partner_info['partner_code']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"total": total, "found": found, "data_count": len(data_list)}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="启用合作伙伴",
        title="启用合作伙伴流程",
        description="验证合作伙伴启用功能正确性（覆盖ID传参、启用接口调用、状态变更及操作结果确认）",
        severity="blocker",
        order=3,
        tags=["合作伙伴管理", "功能测试"]
    )
    def test_partner_enable(self):
        try:
            with a.step("启用合作伙伴流程"):
                assert TestPartnerSimplified.partner_info.get("partner_id"), "未找到要启用的合作伙伴ID，请先执行新增用例"
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-合作伙伴启动服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_param(filtered_params, "id", TestPartnerSimplified.partner_info["partner_id"])
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                a.text(f"预置数据: {TestPartnerSimplified.partner_info['partner_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "enable", "success": True}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="停用合作伙伴",
        title="停用合作伙伴流程",
        description="验证合作伙伴停用功能正确性（覆盖ID传参、停用接口调用、状态变更及操作结果确认）",
        severity="normal",
        order=4,
        tags=["合作伙伴管理", "功能测试"]
    )
    def test_partner_disable(self):
        try:
            with a.step("停用合作伙伴流程"):
                assert TestPartnerSimplified.partner_info.get("partner_id"), "未找到要停用的合作伙伴ID，请先执行新增用例"
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-合作伙伴停用服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_param(filtered_params, "id", TestPartnerSimplified.partner_info["partner_id"])
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                a.text(f"预置数据: {TestPartnerSimplified.partner_info['partner_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "disable", "success": True}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="删除合作伙伴",
        title="删除合作伙伴流程",
        description="验证合作伙伴删除功能正确性（覆盖ID传参、删除接口调用、数据清理及测试环境重置）",
        severity="blocker",
        order=5,
        tags=["合作伙伴管理", "删除操作", "数据清理"]
    )
    def test_partner_delete(self):
        try:
            with a.step("删除合作伙伴流程"):
                assert TestPartnerSimplified.partner_info.get("partner_id"), "未找到要删除的合作伙伴ID，请先执行新增用例"
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-删除服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_param(filtered_params, "id", TestPartnerSimplified.partner_info["partner_id"])
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                old_data = TestPartnerSimplified.partner_info.copy()
                TestPartnerSimplified.partner_info = {}
                
                a.text(f"预置数据: {old_data['partner_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "delete", "success": True, "data_cleared": True}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

# if __name__ == "__main__":
#     """直接运行测试用例的入口点"""
#     test = TestPartnerSimplified()
#     test.setup_class()
#     test.test_partner_add()    # 新增合作伙伴
#     test.test_partner_search() # 查询合作伙伴
#     test.test_partner_enable() # 启用合作伙伴
#     test.test_partner_disable() # 停用合作伙伴
#     test.test_partner_delete() # 删除合作伙伴 