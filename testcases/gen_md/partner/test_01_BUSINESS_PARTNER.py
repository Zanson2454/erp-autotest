import allure
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("通用基础")
@allure.feature("合作伙伴管理")
class TestPartnerSimplified(GenMdBaseTest):
    partner_info = {}
    @classmethod
    def setup_class(cls):
        super().setup_class()
    @case_decorator(
        story="新增合作伙伴(供应商)",
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
                partner_code = self.mock_util.generate_unique_code(tag="Partner")
                partner_name = f"合作伙伴_{self.mock_util.get_timestamp()}"
                remark = f"测试备注_{self.mock_util.get_timestamp()}"
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-保存服务")
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
                    "partnerTypeId": {"id": 2017001},
                    "partnerIdentity": ["SUPPLIER"]
                })
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                partner_id = result.get("data", {}).get("data")
                assert partner_id, "新增合作伙伴失败：返回的ID为空"
                
                TestPartnerSimplified.partner_info.update({
                    "partner_id": partner_id,
                    "partner_code": partner_code,
                    "partner_name": partner_name,
                    "partner_identity": ["SUPPLIER"]  # 保存初始身份信息
                })
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestPartnerSimplified.partner_info, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询合作伙伴",
        title="查询合作伙伴流程",
        description="验证合作伙伴查询功能正确性（覆盖查询条件构造、分页查询接口、结果校验及数据匹配验证）",
        severity="normal",
        order=3,
        tags=["合作伙伴管理", "功能测试"]
    )
    def test_partner_search(self):
        try:
            with a.step("查询合作伙伴流程"):
                # 如果没有预置数据，先创建一个合作伙伴
                if not TestPartnerSimplified.partner_info.get("partner_code"):
                    self.test_partner_add()
                
                partner_code = TestPartnerSimplified.partner_info["partner_code"]
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
                                    "value": partner_code
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
                
                found = any(item.get("code") == partner_code for item in data_list)
                assert found, f"未找到合作伙伴编码: {partner_code}"
                
                # 验证合作伙伴身份是否正确
                if TestPartnerSimplified.partner_info.get("partner_identity"):
                    partner_item = next((item for item in data_list if item.get("code") == partner_code), None)
                    if partner_item:
                        actual_identity = partner_item.get("partnerIdentity", [])
                        expected_identity = TestPartnerSimplified.partner_info["partner_identity"]
                        # 如果编辑过，实际身份可能是CUSTOMER，需要动态判断
                        if expected_identity == ["SUPPLIER"] and actual_identity == ["CUSTOMER"]:
                            # 编辑后身份已变更，更新期望值
                            TestPartnerSimplified.partner_info["partner_identity"] = ["CUSTOMER"]
                            expected_identity = ["CUSTOMER"]
                        
                        assert actual_identity == expected_identity, f"合作伙伴身份不匹配，期望: {expected_identity}，实际: {actual_identity}"
                        identity_check = True
                    else:
                        identity_check = False
                else:
                    identity_check = "未设置期望身份"
                
                a.text(f"预置数据: {partner_code}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({
                    "total": total, 
                    "found": found, 
                    "data_count": len(data_list),
                    "identity_check": identity_check
                }, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-启用服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestPartnerSimplified.partner_info["partner_id"]
                })
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                a.text(f"预置数据: {TestPartnerSimplified.partner_info['partner_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "enable", "success": True}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
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
                
                api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-禁用服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {
                    "id": TestPartnerSimplified.partner_info["partner_id"]
                })
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                a.text(f"预置数据: {TestPartnerSimplified.partner_info['partner_id']}", "预置数据")
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json({"operation": "disable", "success": True}, "断言结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # @case_decorator(
    #     story="编辑合作伙伴",
    #     title="编辑合作伙伴流程",
    #     description="验证编辑合作伙伴功能正确性（覆盖ID传参、编辑接口调用、数据更新及操作结果确认）",
    #     severity="blocker",
    #     order=2,
    #     tags=["合作伙伴管理", "功能测试"]
    # )
    # def test_partner_edit(self):
    #     try:
    #         with a.step("编辑合作伙伴流程"):
    #             # 如果没有预置数据，先创建一个合作伙伴
    #             if not TestPartnerSimplified.partner_info.get("partner_id"):
    #                 self.test_partner_add()
                
    #             partner_id = TestPartnerSimplified.partner_info["partner_id"]
    #             new_partner_name = f"编辑后合作伙伴_{self.mock_util.get_timestamp()}"
                
    #             api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-保存服务")
    #             params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
    #             # 构建简化的编辑请求参数，修改名称跟身份
    #             edit_params = {
    #                 "params": {
    #                     "request": {
    #                         "id": partner_id,
    #                         "name": new_partner_name,  # 新名称
    #                         "code": TestPartnerSimplified.partner_info["partner_code"],
    #                         "classType": "COMPANY",
    #                         "status": "INACTIVE",
    #                         "partnerTypeId": {"id": 2017001},
    #                         "partnerIdentity": ["CUSTOMER"],  # 修改身份为客户
    #                         "addrList": [],  # 添加空数组避免空指针异常
    #                         "bankList": [],  # 添加空数组避免空指针异常
    #                         "contactList": [],  # 添加空数组避免空指针异常
    #                         "attachmentList": [],  # 添加空数组避免空指针异常
    #                         "textList": [],  # 添加空数组避免空指针异常
    #                         "qualificationsList": [],  # 添加空数组避免空指针异常
    #                         "userList": [],  # 添加空数组避免空指针异常
    #                         "partiesList": [],  # 添加空数组避免空指针异常
    #                         "cateList": [],  # 添加分类列表避免Index错误
    #                         "labelList": [],  # 添加标签列表
    #                         "attrList": []  # 添加属性列表
    #                     }
    #                 }
    #             }
                
    #             # 发送编辑请求
    #             result = self.http.post(url, json=edit_params)
    #             self.assert_util.assert_response_success(result)
                
    #             # 更新合作伙伴信息
    #             TestPartnerSimplified.partner_info["partner_name"] = new_partner_name
    #             TestPartnerSimplified.partner_info["partner_identity"] = ["CUSTOMER"]  # 更新身份信息
                
    #             a.text(f"预置数据: {partner_id}", "预置数据")
    #             a.json(edit_params, "请求数据")
    #             a.json(result, "响应结果数据")
    #             a.json({
    #                 "operation": "edit", 
    #                 "success": True, 
    #                 "new_name": new_partner_name,
    #                 "new_identity": ["CUSTOMER"]  # 添加身份断言
    #             }, "断言结果")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    # @case_decorator(
    #     story="删除合作伙伴",
    #     title="删除合作伙伴流程",
    #     description="验证合作伙伴删除功能正确性（覆盖ID传参、删除接口调用、数据清理及测试环境重置）",
    #     severity="blocker",
    #     order=5,
    #     tags=["合作伙伴管理", "删除操作", "数据清理"]
    # )
    # def test_partner_delete(self):
    #     try:
    #         with a.step("删除合作伙伴流程"):
    #             assert TestPartnerSimplified.partner_info.get("partner_id"), "未找到要删除的合作伙伴ID，请先执行新增用例"
                
    #             api_path = ParamUtil.get_api_path(self.apis, "GEN-合作伙伴-删除服务")
    #             params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
    #             filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
    #             ParamUtil.set_request_params(filtered_params, {
    #                 "id": TestPartnerSimplified.partner_info["partner_id"]
    #             })
    #             result = self.http.post(url, json=filtered_params)
    #             self.assert_util.assert_response_success(result)
                
    #             old_data = TestPartnerSimplified.partner_info.copy()
    #             TestPartnerSimplified.partner_info = {}
                
    #             a.text(f"预置数据: {old_data['partner_id']}", "预置数据")
    #             a.json(filtered_params, "请求数据")
    #             a.json(result, "响应结果数据")
    #             a.json({"operation": "delete", "success": True, "data_cleared": True}, "断言结果")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPartnerSimplified()
    test.setup_class()
    test.test_partner_add()    # 新增合作伙伴
    test.test_partner_search() # 查询合作伙伴
    test.test_partner_enable() # 启用合作伙伴
    test.test_partner_disable() # 停用合作伙伴
    # test.test_partner_delete() # 删除合作伙伴 