"""
组织通用查询服务测试用例
覆盖员工、组织单元、身份等通用查询功能
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("组织通用查询服务")
class TestOrgQueryService(SysCommonBaseTest):
    """组织通用查询服务测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("组织通用查询服务测试类初始化完成")
    
    # ==================== 员工查询相关 ====================
    
    @case_decorator(
        story="组织通用查询",
        title="通过员工ID查询员工详情",
        description="验证get_employee_details_by_id功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_get_employee_details_by_id(self):
        """通过员工ID查询员工详情"""
        try:
            # 使用已有的用户ID作为测试
            test_employee_id = self.user_id
            
            # 1. 调用API
            api_path = self.get_api_path("通过员工 ID 查询员工详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["employeeId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"employeeId": test_employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过员工 ID 查询员工详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"通过员工ID查询详情成功: ID={test_employee_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过员工编码查询员工详情",
        description="验证get_employee_details_by_emp_code功能",
        severity="critical",
        order=2,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_get_employee_details_by_emp_code(self):
        """通过员工编码查询员工详情"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过员工编码查询员工详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"empCode": "TEST_EMP_CODE"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过员工编码查询员工详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过员工编码查询详情成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过用户ID查询员工详情",
        description="验证query_employee_detail_by_user_id功能",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_query_employee_detail_by_user_id(self):
        """通过用户ID查询员工详情"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过用户 ID 查询员工详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["userId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"userId": self.user_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过用户 ID 查询员工详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"通过用户ID查询员工详情成功: UserID={self.user_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过员工ID列表查询员工列表",
        description="验证get_employee_list_by_id_list功能",
        severity="critical",
        order=4,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_get_employee_list_by_id_list(self):
        """通过员工ID列表查询员工列表"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过员工ID列表查询员工列表")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["employeeIdList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"employeeIdList": [self.user_id]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过员工ID列表查询员工列表",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过员工ID列表查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过员工编码列表查询员工列表",
        description="验证get_employee_list_by_code_list功能",
        severity="critical",
        order=5,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_get_employee_list_by_code_list(self):
        """通过员工编码列表查询员工列表"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过员工编码列表查询员工列表")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCodeList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"empCodeList": ["TEST_CODE"]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过员工编码列表查询员工列表",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过员工编码列表查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="员工分页查询服务",
        description="验证ORG_EMPLOYEE_PAGE_SERVICE功能",
        severity="critical",
        order=6,
        tags=["sys_common", "org_query", "员工查询"]
    )
    def test_employee_page_service(self):
        """员工分页查询服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("员工分页查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工分页查询服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("员工分页查询服务成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 组织查询相关 ====================
    
    @case_decorator(
        story="组织通用查询",
        title="通过组织单元ID查询详情",
        description="验证get_ou_details_by_id功能",
        severity="critical",
        order=7,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_get_ou_details_by_id(self):
        """通过组织单元ID查询组织单元详情"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过组织单元 ID 查询组织单元详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ouId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ouId": "TEST_OU_ID"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过组织单元 ID 查询组织单元详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过组织单元ID查询详情成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过身份ID查询身份详情",
        description="验证get_identity_details_by_id功能",
        severity="critical",
        order=8,
        tags=["sys_common", "org_query", "身份查询"]
    )
    def test_get_identity_details_by_id(self):
        """通过身份ID查询身份详情"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过身份 ID 查询身份详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["identityId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"identityId": "TEST_IDENTITY_ID"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过身份 ID 查询身份详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过身份ID查询详情成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过组织编码查询员工信息",
        description="验证query_employee_info_by_organization_code功能",
        severity="normal",
        order=9,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_query_employee_info_by_organization_code(self):
        """通过组织编码查询员工信息"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过组织编码查询员工信息")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"orgCode": "TEST_ORG_CODE"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过组织编码查询员工信息",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过组织编码查询员工信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过组织编码及角色编码查询员工信息",
        description="验证query_employee_info_by_organization_and_role_code功能",
        severity="normal",
        order=10,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_query_employee_info_by_org_and_role_code(self):
        """通过组织编码及角色编码查询员工信息"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过组织编码及角色编码查询员工信息")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "roleCode"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": "TEST_ORG_CODE",
                "roleCode": "TEST_ROLE_CODE"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过组织编码及角色编码查询员工信息",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("通过组织及角色编码查询员工信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="通过员工编码与角色编码查询上级组织信息",
        description="验证query_superior_organization_info_by_employee_code_功能",
        severity="normal",
        order=11,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_query_superior_organization_info(self):
        """通过员工编码与角色编码查询上级组织信息"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("通过员工编码与角色编码查询上级组织信息")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode", "roleCode"],
                ["params", "request"]
            )
            set_dict = {
                "empCode": "TEST_EMP_CODE",
                "roleCode": "TEST_ROLE_CODE"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="通过员工编码与角色编码查询上级组织信息",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查询上级组织信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="根据pid查询组织单元服务",
        description="验证ORG_ORG_UNIT_QUERY_PID_SERVICE功能",
        severity="normal",
        order=12,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_org_unit_query_by_pid(self):
        """根据pid查询组织单元服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("根据pid查询组织单元服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pid"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pid": "TEST_PID"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="根据pid查询组织单元服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据pid查询组织单元成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="根据条件查询组织数据服务",
        description="验证ORG_ORG_UNIT_FIND_ALL_SERVICE功能",
        severity="critical",
        order=13,
        tags=["sys_common", "org_query", "组织查询"]
    )
    def test_org_unit_find_all(self):
        """根据条件查询组织数据服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("根据条件查询组织数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="根据条件查询组织数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据条件查询组织数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="组织身份职级管理列表查询服务",
        description="验证ORG_RANK_CF_FIND_ALL_SERVICE功能",
        severity="normal",
        order=14,
        tags=["sys_common", "org_query", "身份查询"]
    )
    def test_org_rank_find_all(self):
        """组织身份职级管理列表查询服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织身份职级管理列表查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="组织身份职级管理列表查询服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("组织身份职级管理列表查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="组织业务类型列表查询服务",
        description="验证ORG_BIZ_TYPE_FIND_ALL_SERVICE功能",
        severity="normal",
        order=15,
        tags=["sys_common", "org_query", "业务类型查询"]
    )
    def test_org_biz_type_find_all(self):
        """组织业务类型列表查询服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织业务类型列表查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="组织业务类型列表查询服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("组织业务类型列表查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织通用查询",
        title="查找树子数据服务(支持条件过滤)",
        description="验证STRUCT_FIND_TREE_CHILDREN_DATA_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "org_query", "树查询"]
    )
    def test_struct_find_tree_children_data(self):
        """查找树子数据服务(支持条件过滤)"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-查找树子数据服务(支持条件过滤)")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["parentId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"parentId": "ROOT"})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="组织架构表-查找树子数据服务(支持条件过滤)",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找树子数据服务(支持条件过滤)成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
