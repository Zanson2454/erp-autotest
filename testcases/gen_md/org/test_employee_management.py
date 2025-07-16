import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("员工管理")
class TestEmployeeManagement(GenMdBaseTest):
    """员工管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        
    
        # 用于存储创建员工时的实际数据，供查询测试用例使用
        cls.mobile = None
        cls.email = None
        cls.user_name = None
        cls.id_card = None
        cls.entry_date = None
        cls.employee_name = None
        cls.employee_id = None
        
        # 依赖组织
        if cls.md_cache_data:
            cls.pur_org_id = cls.md_cache_data.get("org_info",{}).get("pur_org_info",[])[0].get("id",None)
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("com_org_info",[])[0].get("id",None)
            cls.identityId = cls.md_cache_data.get("org_info",{}).get("org_identity_cf",[])[0].get("id",None)
    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的员工管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="pen_adjust_type_md",
                where="id in (select org_employee_id from org_employee_md where code like %s)",
                params=["AT_%"]
            )
            cls.db.delete(
                table="pen_adjust_md",
                where="id in (select org_employee_id from org_employee_md where code like %s)",
                params=["AT_%"]
            )
            cls.db.delete(
                table="org_employee_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.iam_db.delete(
                table="iam_user",
                where="username like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

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
            # 每次新增都生成新的员工数据
            employee_code = self.mock_util.generate_unique_code(tag="Employee")
            mobile = self.mock_util.get_mock_phone_number()
            email = self.mock_util.get_mock_email()
            user_name = self.mock_util.generate_unique_code(tag="user")
            id_card = self.mock_util.get_mock_ssn()
            entry_date = self.mock_util.get_timestamp(timestamp=True)
            employee_name = self.mock_util.get_mock_name()
            
            # 保存创建的数据供其他测试用例使用
            TestEmployeeManagement.mobile = mobile
            TestEmployeeManagement.email = email
            TestEmployeeManagement.user_name = user_name
            TestEmployeeManagement.id_card = id_card
            TestEmployeeManagement.entry_date = entry_date
            TestEmployeeManagement.employee_name = employee_name

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
                "name": employee_name,
                "type": "FORMAL",  # 正式员工
                "orgStructId": self.com_org_id,
                "mobile": mobile,
                "email": f"{self.mock_util.get_timestamp()}@terminus.io",
                "userName": user_name,
                "entryAt": entry_date,
                "resignationAt": None,
                "idCard": id_card,
                "addressId": None,
                "addressDetail": None,  
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            TestEmployeeManagement.employee_id = response.get("data", {}).get("data", {}).get("id")

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
            if not TestEmployeeManagement.employee_id:
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
            set_dict = {"id": TestEmployeeManagement.employee_id}
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
            api_path = self.get_api_path("ORG-员工-分页查询服务")
            self.logger.info(f"api_path: {api_path}")
            params, url = self.get_api_params(api_path)


            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            set_dict = {"pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True, "sortOrders": None, "conditionItems": None}}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, ">", 0)

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
            # 确保已经创建了员工，并使用相同的手机号进行查询
            if not TestEmployeeManagement.employee_id:
                self.test_save_employee()
            
             # 调用分页查询接口
            api_path = self.get_api_path("ORG-员工-分页查询服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            # 构建请求参数 - 按手机号查询
            set_dict = {
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
                                        "value": TestEmployeeManagement.mobile
                                    }
                                },
                                "logicOperator": "AND"
                            }
                        }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, "=", 1)

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
            # 确保已经创建了员工，并使用相同的姓名进行查询
            if not TestEmployeeManagement.employee_id:
                self.test_save_employee()
            
            # 调用分页查询接口
            api_path = self.get_api_path("ORG-员工-分页查询服务")
            params, url = self.get_api_params(api_path) 
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            # 构建请求参数 - 按姓名查询
            set_dict = {
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
                                        "value": TestEmployeeManagement.employee_name
                                    }
                                },
                                "logicOperator": "AND"
                            }
                        }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, ">", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试保存员工组织关联关系",
        description="验证保存员工组织关联关系功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["员工管理", "保存关联"]
    )
    def test_save_employee_org_relation(self):
        """
        保存员工组织关联关系用例
        """
        try:
            # 确保已经创建了员工
            if not TestEmployeeManagement.employee_id:
                self.test_save_employee()
            
            
            # 调用保存员工组织关联关系接口
            api_path = self.get_api_path("ORG-组织-保存员工组织关联关系服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["employeeId", "identityId","orgUnitId","isMainOrg"],
                ["params", "request"]
            )
            set_dict = {
                "employeeId":  {"id":TestEmployeeManagement.employee_id},
                "identityId": {"id":self.identityId },
                "orgUnitId":  self.pur_org_id,
                "isMainOrg": True
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            # 判断是否已存在员工关联数据
            sql = f"select id from org_employee_org_link_cf where employee_id={TestEmployeeManagement.employee_id} and identity_id={self.identityId} and org_unit_id={self.pur_org_id}"
            result = self.db.query(sql)
            if  result:
               self.db.delete(
                table="org_employee_org_link_cf",
                where=f"employee_id={TestEmployeeManagement.employee_id} and identity_id={self.identityId} and org_unit_id={self.pur_org_id}"
               )


            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

   

    @case_decorator(
        story="员工管理",
        title="测试查询指定组织和下级组织的员工信息",
        description="验证查询指定组织和下级组织的员工信息功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["员工管理", "组织查询", "下级组织"]
    )
    def test_query_org_and_child_org_employee(self):
        """
        查询指定组织和下级组织的员工信息用例
        """
        try:
            self.test_save_employee_org_relation()
            # 调用查询指定组织和下级组织的员工信息接口
            api_path = self.get_api_path("ORG-组织-查询指定组织和下级组织的员工信息")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgId", "pageable"],
                ["params", "request"]
            )
            set_dict = {
                "orgId": self.pur_org_id,
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "conditionGroup": None,
                    "sortOrders": None,
                    "keyword": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, headers=self.admin_headers, json=filtered_params)
            self.assert_util.assert_response_success(response)

            # 验证返回的员工信息列表
            employee_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(len(employee_list), ">", 0)
    
           
            

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
        order=8,
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

            sql = f"select id  from org_employee_org_link_cf where employee_id={TestEmployeeManagement.employee_id}  and  identity_id={self.identityId} and org_unit_id={self.pur_org_id}"
            result = self.db.query(sql)
            if not result:
                self.test_save_employee_org_relation()
                result = self.db.query(sql)
            
            employee_org_relationId = result[0].get("id")
            # 调用删除员工组织关联关系接口
            api_path = self.get_api_path("ORG-组织-删除员工组织关联关系服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": employee_org_relationId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        