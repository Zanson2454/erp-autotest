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
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
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
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    @case_decorator(
        story="员工管理",
        title="测试新增员工管理",
        description="验证新增员工管理功能",
        severity="blocker",
        file_level_order=1,
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

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "code": employee_code,
                "name": employee_name,
                "type": "FORMAL",  # 正式员工
                "orgStructId": self.com_org_id,
                "mobile": mobile,
                "email": email,
                "userName": user_name,
                "entryAt": entry_date,
                "resignationAt": None,
                "idCard": id_card,
                "addressId": None,
                "addressDetail": None,  
            }
            fields_to_filter = ["code", "name", "type", "orgStructId", "mobile", "email", 
                                "userName", "entryAt", "resignationAt", "idCard", "addressId", 
                                "addressDetail"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-员工-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)
            TestEmployeeManagement.employee_id = response.get("data", {}).get("data", {}).get("id")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试查询员工详情",
        description="验证查询员工详情功能",
        severity="normal",
        file_level_order=2,
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

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": TestEmployeeManagement.employee_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-员工-详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 验证返回的员工信息
            employee_status = response.get("data", {}).get("data", {}).get("status")
            self.assert_util.assert_by_operator(employee_status, "=", "ENABLED")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工分页查询",
        description="验证员工分页查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["员工管理", "分页查询"]
    )
    def test_employee_paging_query(self):
        """
        员工分页查询用例
        """
        try:
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True, "sortOrders": None, "conditionItems": None}}
            fields_to_filter = ["pageable"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-员工-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)
            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, ">", 0)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工条件查询-按手机号",
        description="验证员工按手机号条件查询功能",
        severity="normal",
        file_level_order=4,
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
            
             # 准备测试数据（业务逻辑保持不变）
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
            fields_to_filter = ["pageable"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-员工-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, "=", 1)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试员工条件查询-按姓名",
        description="验证员工按姓名条件查询功能",
        severity="normal",
        file_level_order=5,
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
            
            # 准备测试数据（业务逻辑保持不变）
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
            fields_to_filter = ["pageable"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-员工-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, ">", 0)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试保存员工组织关联关系",
        description="验证保存员工组织关联关系功能",
        severity="normal",
        file_level_order=6,
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
            
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "employeeId":  {"id":TestEmployeeManagement.employee_id},
                "identityId": {"id":self.identityId },
                "orgUnitId":  self.pur_org_id,
                "isMainOrg": True
            }
            fields_to_filter = ["employeeId", "identityId","orgUnitId","isMainOrg"]

            # 判断是否已存在员工关联数据（保持原有SQL逻辑）
            sql = f"select id from org_employee_org_link_cf where employee_id={TestEmployeeManagement.employee_id} and identity_id={self.identityId} and org_unit_id={self.pur_org_id}"
            result = self.db.query(sql)
            if result:
                # 幂等处理：若关系已存在，直接复用，避免因禁用物理删除导致重复创建失败
                self.logger.info(f"员工组织关联已存在，复用关系ID: {result[0].get('id')}")
                return

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织-保存员工组织关联关系服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            if response.get("success") is True:
                self.assert_util.assert_response_success(response)
            else:
                # 并发/脏数据场景兜底：接口返回“已存在”时视为幂等成功
                err_code = response.get("err", {}).get("code")
                if err_code == "Org.struct.member.is.exist":
                    existed = self.db.query(sql)
                    if existed:
                        self.logger.warning(
                            f"员工组织关联返回已存在，按幂等成功处理，关系ID: {existed[0].get('id')}"
                        )
                        return
                self.assert_util.assert_response_success(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

   

    @case_decorator(
        story="员工管理",
        title="测试查询指定组织和下级组织的员工信息",
        description="验证查询指定组织和下级组织的员工信息功能",
        severity="normal",
        file_level_order=7,
        smoke=True,
        tags=["员工管理", "组织查询", "下级组织"]
    )
    def test_query_org_and_child_org_employee(self):
        """
        查询指定组织和下级组织的员工信息用例
        """
        try:
            self.test_save_employee_org_relation()
            # 准备测试数据（业务逻辑保持不变）
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
            fields_to_filter = ["orgId", "pageable"]

            # 使用标准化API调用（无任何断言，preserve headers if needed but standard_api_call uses self.http）
            response, _ = self.standard_api_call(
                api_key="ORG-组织-查询指定组织和下级组织的员工信息",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 验证返回的员工信息列表
            employee_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(len(employee_list), ">", 0)
    
            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="员工管理",
        title="测试删除员工组织关联关系",
        description="验证删除员工组织关联关系功能",
        severity="normal",
        file_level_order=8,
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

            # SQL query to get relation ID (keep original)
            sql = f"select id  from org_employee_org_link_cf where employee_id={TestEmployeeManagement.employee_id}  and  identity_id={self.identityId} and org_unit_id={self.pur_org_id}"
            result = self.db.query(sql)
            if not result:
                self.test_save_employee_org_relation()
                result = self.db.query(sql)
            
            employee_org_relationId = result[0].get("id")
            
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": employee_org_relationId}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织-删除员工组织关联关系服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
