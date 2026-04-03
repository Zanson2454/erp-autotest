"""
组织关联关系管理测试用例
覆盖员工组织关联、组织业务类型关联、组织维度业务类型关联等功能
"""
import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("组织关联关系管理")
class TestOrgLinkManagement(SysCommonBaseTest):
    """组织关联关系管理测试类"""
    
    emp_org_link_id = None
    struct_biz_link_id = None
    dim_biz_link_id = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.emp_org_link_id = None
        cls.struct_biz_link_id = None
        cls.dim_biz_link_id = None
        cls.org_struct_id = None
        cls.biz_type_id = None
        cls.dimension_id = None
        cls.logger.info("组织关联关系管理测试类初始化完成")

    def _ensure_seed_ids(self):
        """优先用缓存，其次回查数据库，避免用字符串占位导致 Long 反序列化失败。"""
        if self.org_struct_id and self.biz_type_id and self.dimension_id:
            return

        if self.md_cache_data:
            org_info = self.md_cache_data.get("org_info", {})
            for key in ("gr_come_org_info", "sls_org_info", "inv_org_info", "com_org_info"):
                rows = org_info.get(key, [])
                if rows and rows[0].get("id") and not self.org_struct_id:
                    self.__class__.org_struct_id = rows[0].get("id")
                    break

            biz_type_ids = org_info.get("org_biz_type_cf", [])
            if biz_type_ids and not self.biz_type_id:
                first = biz_type_ids[0]
                self.__class__.biz_type_id = first.get("id") if isinstance(first, dict) else first

            dim_rows = org_info.get("org_dimension_info", []) or org_info.get("dimension_info", [])
            if dim_rows and dim_rows[0].get("id") and not self.dimension_id:
                self.__class__.dimension_id = dim_rows[0].get("id")

        if not self.org_struct_id:
            row = self.db.query_one(sql="SELECT id FROM org_struct_md ORDER BY id DESC LIMIT 1")
            if row:
                self.__class__.org_struct_id = row.get("id")
        if not self.biz_type_id:
            row = self.db.query_one(sql="SELECT id FROM org_business_type_cf ORDER BY id DESC LIMIT 1")
            if row:
                self.__class__.biz_type_id = row.get("id")
        if not self.dimension_id:
            row = self.db.query_one(sql="SELECT id FROM org_dimension_cf ORDER BY id DESC LIMIT 1")
            if row:
                self.__class__.dimension_id = row.get("id")

        if not self.org_struct_id or not self.biz_type_id or not self.dimension_id:
            pytest.fail("缺少组织关联所需基础ID(org_struct/biz_type/dimension)，无法执行当前用例")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理员工组织关联数据
            cls.db.delete(
                table="org_employee_org_link_cf",
                where="created_by = %s",
                params=[cls.user_id]
            )
            # 清理组织业务类型关联数据
            cls.db.delete(
                table="org_struct_business_type_link",
                where="created_by = %s",
                params=[cls.user_id]
            )
            # 清理组织维度业务类型关联数据
            cls.db.delete(
                table="org_dimension_business_link",
                where="created_by = %s",
                params=[cls.user_id]
            )
            cls.logger.info("组织关联关系测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"组织关联关系测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    # ==================== 员工组织关联表测试 ====================
    
    @allure.story("员工组织关联")
    @case_decorator(
        story="员工组织关联",
        title="测试创建员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "org_link", "员工组织关联", "创建"]
    )
    def test_create_emp_org_link(self):
        """创建员工组织关联数据"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("员工组织关联表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["empId", "orgId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "empId": self.user_id,
                "orgId": self.org_struct_id,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            self.__class__.emp_org_link_id = response.get("data", {}).get("data", {})
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建员工组织关联成功: ID={self.emp_org_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试员工组织关联分页查询",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_PAGING_DATA_SERVICE功能",
        severity="critical",
        order=2,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_emp_org_link_paging_query(self):
        """员工组织关联分页查询"""
        try:
            api_path = self.get_api_path("员工组织关联表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            })
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("员工组织关联分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试根据ID查找员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=3,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_find_emp_org_link_by_id(self):
        """根据ID查找员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.emp_org_link_id})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找员工组织关联成功: ID={self.emp_org_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试更新员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=4,
        tags=["sys_common", "org_link", "员工组织关联", "更新"]
    )
    def test_update_emp_org_link(self):
        """更新员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": self.emp_org_link_id,
                "status": "DISABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新员工组织关联成功: ID={self.emp_org_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试保存员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=5,
        tags=["sys_common", "org_link", "员工组织关联", "创建"]
    )
    def test_save_emp_org_link(self):
        """保存员工组织关联"""
        try:
            api_path = self.get_api_path("员工组织关联表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empId", "orgId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "empId": self.user_id,
                "orgId": "TEST_ORG_ID_2",
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("保存员工组织关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试批量创建员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=6,
        tags=["sys_common", "org_link", "员工组织关联", "创建"]
    )
    def test_batch_create_emp_org_link(self):
        """批量创建员工组织关联"""
        try:
            api_path = self.get_api_path("员工组织关联表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            link_list = [
                {"empId": self.user_id, "orgId": "BATCH_ORG_1", "status": "ENABLED"},
                {"empId": self.user_id, "orgId": "BATCH_ORG_2", "status": "ENABLED"}
            ]
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": link_list})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量创建员工组织关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试查找单条员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_FIND_ONE_DATA_SERVICE功能",
        severity="normal",
        order=7,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_find_one_emp_org_link(self):
        """查找单条员工组织关联"""
        try:
            api_path = self.get_api_path("员工组织关联表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-查找单条数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找单条员工组织关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试查找员工组织关联列表",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_FIND_LIST_DATA_SERVICE功能",
        severity="normal",
        order=8,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_find_list_emp_org_link(self):
        """查找员工组织关联列表"""
        try:
            api_path = self.get_api_path("员工组织关联表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找员工组织关联列表成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试根据ID查找单表员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="normal",
        order=9,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_find_single_emp_org_link_by_id(self):
        """根据ID查找单表员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.emp_org_link_id})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表员工组织关联成功: ID={self.emp_org_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试根据ID列表查找员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=10,
        tags=["sys_common", "org_link", "员工组织关联", "查询"]
    )
    def test_find_emp_org_link_by_ids(self):
        """根据ID列表查找员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.emp_org_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找员工组织关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试批量删除员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=11,
        tags=["sys_common", "org_link", "员工组织关联", "删除"]
    )
    def test_batch_delete_emp_org_link(self):
        """批量删除员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.emp_org_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除员工组织关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工组织关联",
        title="测试删除员工组织关联",
        description="验证ORG_EMPLOYEE_ORG_LINK_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=12,
        tags=["sys_common", "org_link", "员工组织关联", "删除"]
    )
    def test_delete_emp_org_link(self):
        """删除员工组织关联"""
        try:
            if not self.emp_org_link_id:
                self._ensure_create_emp_org_link()
            
            api_path = self.get_api_path("员工组织关联表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.emp_org_link_id})
            
            response, _ = self.standard_api_call(
                api_key="员工组织关联表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除员工组织关联成功: ID={self.emp_org_link_id}")
            
            self.__class__.emp_org_link_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 组织业务类型关联表测试 ====================
    
    @allure.story("组织业务类型关联")
    @case_decorator(
        story="组织业务类型关联",
        title="测试创建组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=6,
        smoke=True,
        tags=["sys_common", "org_link", "组织业务类型关联", "创建"]
    )
    def test_create_struct_biz_link(self):
        """创建组织业务类型关联数据"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织业务类型关联表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["orgStructId", "bizTypeId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "orgStructId": self.org_struct_id,
                "bizTypeId": self.biz_type_id,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            self.__class__.struct_biz_link_id = response.get("data", {}).get("data", {})
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建组织业务类型关联成功: ID={self.struct_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试组织业务类型关联分页查询",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_PAGING_DATA_SERVICE功能",
        severity="critical",
        order=7,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_struct_biz_link_paging_query(self):
        """组织业务类型关联分页查询"""
        try:
            api_path = self.get_api_path("组织业务类型关联表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            })
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("组织业务类型关联分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试查找列表数据",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=8,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_struct_biz_link_find_list(self):
        """查找组织业务类型关联列表数据"""
        try:
            api_path = self.get_api_path("组织业务类型关联表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织业务类型关联列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试根据ID查找组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=9,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_find_struct_biz_link_by_id(self):
        """根据ID查找组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.struct_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找组织业务类型关联成功: ID={self.struct_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试更新组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=10,
        tags=["sys_common", "org_link", "组织业务类型关联", "更新"]
    )
    def test_update_struct_biz_link(self):
        """更新组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": self.struct_biz_link_id,
                "status": "DISABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新组织业务类型关联成功: ID={self.struct_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试保存组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_SAVE_DATA_SERVICE功能",
        severity="normal",
        order=11,
        tags=["sys_common", "org_link", "组织业务类型关联", "创建"]
    )
    def test_save_struct_biz_link(self):
        """保存组织业务类型关联"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织业务类型关联表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgStructId", "bizTypeId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "orgStructId": self.org_struct_id,
                "bizTypeId": self.biz_type_id,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("保存组织业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试批量创建组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=12,
        tags=["sys_common", "org_link", "组织业务类型关联", "创建"]
    )
    def test_batch_create_struct_biz_link(self):
        """批量创建组织业务类型关联"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织业务类型关联表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            link_list = [
                {"orgStructId": self.org_struct_id, "bizTypeId": self.biz_type_id, "status": "ENABLED"}
            ]
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": link_list})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量创建组织业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试查找单条组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_FIND_ONE_DATA_SERVICE功能",
        severity="normal",
        order=13,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_find_one_struct_biz_link(self):
        """查找单条组织业务类型关联"""
        try:
            api_path = self.get_api_path("组织业务类型关联表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-查找单条数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找单条组织业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试根据ID查找单表组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="normal",
        order=14,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_find_single_struct_biz_link_by_id(self):
        """根据ID查找单表组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.struct_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表组织业务类型关联成功: ID={self.struct_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试根据ID列表查找组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=15,
        tags=["sys_common", "org_link", "组织业务类型关联", "查询"]
    )
    def test_find_struct_biz_link_by_ids(self):
        """根据ID列表查找组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.struct_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找组织业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试批量删除组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "org_link", "组织业务类型关联", "删除"]
    )
    def test_batch_delete_struct_biz_link(self):
        """批量删除组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.struct_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除组织业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型关联",
        title="测试删除组织业务类型关联",
        description="验证ORG_STRUCT_BUSINESS_TYPE_LINK_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=17,
        tags=["sys_common", "org_link", "组织业务类型关联", "删除"]
    )
    def test_delete_struct_biz_link(self):
        """删除组织业务类型关联"""
        try:
            if not self.struct_biz_link_id:
                self._ensure_create_struct_biz_link()
            
            api_path = self.get_api_path("组织业务类型关联表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.struct_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型关联表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除组织业务类型关联成功: ID={self.struct_biz_link_id}")
            
            self.__class__.struct_biz_link_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 组织维度业务类型关联表测试 ====================
    
    @allure.story("组织维度业务类型关联")
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试创建组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=12,
        smoke=True,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "创建"]
    )
    def test_create_dim_biz_link(self):
        """创建组织维度业务类型关联数据"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织维度业务类型关联表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["dimensionId", "bizTypeId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "dimensionId": self.dimension_id,
                "bizTypeId": self.biz_type_id,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            self.__class__.dim_biz_link_id = response.get("data", {}).get("data", {})
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试组织维度业务类型关联分页查询",
        description="验证ORG_DIMENSION_BUSINESS_LINK_PAGING_DATA_SERVICE功能",
        severity="critical",
        order=13,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_dim_biz_link_paging_query(self):
        """组织维度业务类型关联分页查询"""
        try:
            api_path = self.get_api_path("组织维度业务类型关联表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("组织维度业务类型关联分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试查找列表数据",
        description="验证ORG_DIMENSION_BUSINESS_LINK_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=14,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_dim_biz_link_find_list(self):
        """查找组织维度业务类型关联列表数据"""
        try:
            api_path = self.get_api_path("组织维度业务类型关联表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织维度业务类型关联列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试根据ID查找组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=15,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_find_dim_biz_link_by_id(self):
        """根据ID查找组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dim_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试启用组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "启用禁用"]
    )
    def test_enable_dim_biz_link(self):
        """启用组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dim_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"启用组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试禁用组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=17,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "启用禁用"]
    )
    def test_disable_dim_biz_link(self):
        """禁用组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dim_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"禁用组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试批量启用组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=18,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "启用禁用"]
    )
    def test_multi_enable_dim_biz_link(self):
        """批量启用组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-批量启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dim_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-批量启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量启用组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试批量禁用组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=19,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "启用禁用"]
    )
    def test_multi_disable_dim_biz_link(self):
        """批量禁用组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-批量禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dim_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-批量禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量禁用组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试更新组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=20,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "更新"]
    )
    def test_update_dim_biz_link(self):
        """更新组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": self.dim_biz_link_id,
                "status": "DISABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试保存组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_SAVE_DATA_SERVICE功能",
        severity="normal",
        order=21,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "创建"]
    )
    def test_save_dim_biz_link(self):
        """保存组织维度业务类型关联"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织维度业务类型关联表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dimensionId", "bizTypeId", "status"],
                ["params", "request"]
            )
            set_dict = {
                "dimensionId": self.dimension_id,
                "bizTypeId": self.biz_type_id,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("保存组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试批量创建组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=22,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "创建"]
    )
    def test_batch_create_dim_biz_link(self):
        """批量创建组织维度业务类型关联"""
        try:
            self._ensure_seed_ids()
            api_path = self.get_api_path("组织维度业务类型关联表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            link_list = [
                {"dimensionId": self.dimension_id, "bizTypeId": self.biz_type_id, "status": "ENABLED"}
            ]
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": link_list})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量创建组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试查找单条组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_FIND_ONE_DATA_SERVICE功能",
        severity="normal",
        order=23,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_find_one_dim_biz_link(self):
        """查找单条组织维度业务类型关联"""
        try:
            api_path = self.get_api_path("组织维度业务类型关联表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-查找单条数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找单条组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试根据ID查找单表组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="normal",
        order=24,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_find_single_dim_biz_link_by_id(self):
        """根据ID查找单表组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dim_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试根据ID列表查找组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=25,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "查询"]
    )
    def test_find_dim_biz_link_by_ids(self):
        """根据ID列表查找组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dim_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试批量删除组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=26,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "删除"]
    )
    def test_batch_delete_dim_biz_link(self):
        """批量删除组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dim_biz_link_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除组织维度业务类型关联成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度业务类型关联",
        title="测试删除组织维度业务类型关联",
        description="验证ORG_DIMENSION_BUSINESS_LINK_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=27,
        tags=["sys_common", "org_link", "组织维度业务类型关联", "删除"]
    )
    def test_delete_dim_biz_link(self):
        """删除组织维度业务类型关联"""
        try:
            if not self.dim_biz_link_id:
                self._ensure_create_dim_biz_link()
            
            api_path = self.get_api_path("组织维度业务类型关联表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dim_biz_link_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度业务类型关联表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除组织维度业务类型关联成功: ID={self.dim_biz_link_id}")
            
            self.__class__.dim_biz_link_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
