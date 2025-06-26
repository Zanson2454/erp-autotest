import allure
import pytest
from pathlib import Path
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("员工管理")
class TestEmployeeManagement(GenMdBaseTest):
    """员工管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.employee_id = None
        cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("com_org_info",[])[0].get("id",None)
        cls.mobile = cls.mock_data.get_mock_phone_number()
        cls.email = cls.mock_data.get_mock_email()
        cls.user_name = cls.mock_data.generate_unique_code(tag="user")
        cls.id_card = cls.mock_data.get_mock_ssn()
        cls.entry_date = cls.mock_data.get_timestamp(timestamp =True)
        cls.employee_name = cls.mock_data.get_mock_name()
        
    # @classmethod
    # def teardown_class(cls):
    #     """
    #     测试类结束后执行清理
    #     清理所有测试过程中创建的员工管理数据
    #     """
    #     try:
    #         # 使用SQL删除测试数据
    #         cls.db.delete(
    #             table="org_employee_md",
    #             where="code like %s",
    #             params=["AT_%"]
    #         )
    #         cls.logger.info("测试数据清理完成")
    #     except Exception as e:
    #         cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="员工管理",
        title="测试新增员工管理",
        description="验证新增员工管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["员工管理", "新增"]
    )
    def test_save_employee(self):
        """
        新增员工管理用例
        """
        try:
            # 准备员工管理数据
            employee_code = self.mock_data.generate_unique_code(tag="Employee")
            


            # 调用保存接口
            api_path = self.get_api_path("ORG-员工-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["code", "name", "type", "orgStructId", "mobile", "email", 
                 "userName", "entryAt", "resignationAt", "idCard", "addressId", 
                 "addressDetail"],
                ["params", "request"]
            )
            set_dict = {
                "code": employee_code,
                "name": self.employee_name,
                "type": "FORMAL",  # 正式员工
                "orgStructId": self.com_org_id,
                "mobile": self.mobile,
                "email": self.email,
                "userName": self.user_name,
                "entryAt": self.entry_date,
                "resignationAt": None,
                "idCard": self.id_card,
                "addressId": None,
                "addressDetail": None,  
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            self.employee_id = response.get("data", {}).get("data", {}).get("id")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试查询员工详情",
        description="验证查询员工详情功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["员工管理", "查询详情"]
    )
    def test_query_employee_detail(self):
        """
        查询员工详情用例
        """
        try:
            # 确保已经创建了员工
            if not self.employee_id:
                self.test_save_employee()

            # 调用查询详情接口
            api_path = self.get_api_path("ORG-员工-详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.employee_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的员工信息
            employee_status = response.get("data", {}).get("data", {}).get("status")
            self.assert_util.assert_by_operator(employee_status, "=", "ENABLED")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工分页查询",
        description="验证员工分页查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["员工管理", "分页查询"]
    )
    def test_employee_paging_query(self):
        """
        员工分页查询用例
        """
        try:
            # 调用分页查询接口
            api_path = self.get_api_path("员工信息表-分页数据服务")
            params, url = self.get_api_path(api_path)


            # 构建请求参数
            filtered_params = {
                "sceneKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW",
                "viewKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW:list",
                "serviceKey": "sys_common$ORG_EMPLOYEE_MD_PAGING_DATA_SERVICE",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionItems": None
                        }
                    }
                }
            }
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            # 验证分页数据
            page_data = response.get("data", {})
            assert "content" in page_data, "分页数据中缺少content字段"
            assert "totalElements" in page_data, "分页数据中缺少totalElements字段"
            self.logger.info(f"员工分页查询成功，总记录数: {page_data.get('totalElements', 0)}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工条件查询-按手机号",
        description="验证员工按手机号条件查询功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["员工管理", "条件查询", "手机号查询"]
    )
    def test_employee_query_by_mobile(self):
        """
        员工按手机号条件查询用例
        """
        try:
            # 调用分页查询接口
            api_path = self.get_sys_common_api_path("员工信息表-分页数据服务")
            params, url = self.get_sys_common_api_params(api_path)
            # 添加查询参数
            url = f"{api_path}?tmodule=GEN_MD"

            # 构建请求参数 - 按手机号查询
            filtered_params = {
                "sceneKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW",
                "viewKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW:list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "sys_common$ORG_EMPLOYEE_MD_PAGING_DATA_SERVICE",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionItems": {
                                "type": "ConditionItems",
                                "conditions": {
                                    "mobile": {
                                        "operator": "CONTAINS",
                                        "value": self.mobile
                                    }
                                },
                                "logicOperator": "AND"
                            }
                        }
                    }
                }
            }
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            # 验证查询结果
            page_data = response.get("data", {})
            assert "content" in page_data, "分页数据中缺少content字段"
            self.logger.info(f"按手机号查询员工成功，匹配记录数: {len(page_data.get('content', []))}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工条件查询-按姓名",
        description="验证员工按姓名条件查询功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["员工管理", "条件查询", "姓名查询"]
    )
    def test_employee_query_by_name(self):
        """
        员工按姓名条件查询用例
        """
        try:
            # 调用分页查询接口
            api_path = self.get_sys_common_api_path("员工信息表-分页数据服务")
            params, url = self.get_sys_common_api_params(api_path)
            # 添加查询参数
            url = f"{api_path}?tmodule=GEN_MD"

            # 构建请求参数 - 按姓名查询
            filtered_params = {
                "sceneKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW",
                "viewKey": "GEN_MD$ORG_EMPLOYEE_NEW_VIEW:list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "sys_common$ORG_EMPLOYEE_MD_PAGING_DATA_SERVICE",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionItems": {
                                "type": "ConditionItems",
                                "conditions": {
                                    "name": {
                                        "operator": "CONTAINS",
                                        "value": self.employee_name
                                    }
                                },
                                "logicOperator": "AND"
                            }
                        }
                    }
                }
            }
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            # 验证查询结果
            page_data = response.get("data", {})
            assert "content" in page_data, "分页数据中缺少content字段"
            self.logger.info(f"按姓名查询员工成功，匹配记录数: {len(page_data.get('content', []))}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试删除员工组织关联关系",
        description="验证删除员工组织关联关系功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["员工管理", "删除关联"]
    )
    def test_delete_employee_org_relation(self):
        """
        删除员工组织关联关系用例
        """
        try:
            # 获取员工管理信息
            if not TestEmployeeManagement.employee_id:
                self.test_save_employee()

            # 调用删除员工组织关联关系接口
            api_path = self.get_api_path("ORG-组织-删除员工组织关联关系服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.employee_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
