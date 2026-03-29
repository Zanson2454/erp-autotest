"""
员工信息管理测试用例
覆盖员工信息表的增删改查、启用禁用、导入导出等功能
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
@allure.feature("员工信息管理")
class TestEmployeeManagement(SysCommonBaseTest):
    """员工信息管理测试类"""
    
    employee_id = None
    employee_code = None
    employee_name = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.employee_id = None
        cls.employee_code = None
        cls.employee_name = None
        cls.logger.info("员工信息管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="org_employee_md",
                where="emp_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("员工测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"员工测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    # ==================== 创建相关测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试创建员工",
        description="验证ORG_EMPLOYEE_MD_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "employee", "创建"]
    )
    def test_create_employee(self):
        """创建员工数据"""
        try:
            # 1. 准备测试数据
            emp_code = self.mock_util.generate_unique_code(tag="AT_EMP")
            emp_name = f"自动化测试员工_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("员工信息表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["empCode", "empName", "status"],
                ["params", "request"]
            )
            set_dict = {
                "empCode": emp_code,
                "empName": emp_name,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据
            self.__class__.employee_id = response.get("data", {}).get("data", {})
            self.__class__.employee_code = emp_code
            self.__class__.employee_name = emp_name
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建员工成功: ID={self.employee_id}, Code={emp_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试保存员工",
        description="验证ORG_EMPLOYEE_MD_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=2,
        tags=["sys_common", "employee", "创建"]
    )
    def test_save_employee(self):
        """保存员工数据（新增或更新）"""
        try:
            # 1. 准备测试数据
            emp_code = self.mock_util.generate_unique_code(tag="AT_EMP_SAVE")
            emp_name = f"保存测试员工_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("员工信息表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode", "empName", "status"],
                ["params", "request"]
            )
            set_dict = {
                "empCode": emp_code,
                "empName": emp_name,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存员工成功: Code={emp_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试批量创建员工",
        description="验证ORG_EMPLOYEE_MD_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=3,
        tags=["sys_common", "employee", "创建"]
    )
    def test_batch_create_employee(self):
        """批量创建员工数据"""
        try:
            # 1. 准备批量测试数据
            emp_list = []
            for i in range(3):
                emp_code = self.mock_util.generate_unique_code(tag=f"AT_EMP_BATCH_{i}")
                emp_name = f"批量测试员工{i}_{self.mock_util.get_timestamp()}"
                emp_list.append({
                    "empCode": emp_code,
                    "empName": emp_name,
                    "status": "ENABLED"
                })
            
            # 2. 调用API
            api_path = self.get_api_path("员工信息表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": emp_list})
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"批量创建员工成功: 共{len(emp_list)}条")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试保存主数据",
        description="验证ORG_EMPLOYEE_MD_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=4,
        tags=["sys_common", "employee", "创建"]
    )
    def test_master_data_save(self):
        """保存员工主数据"""
        try:
            # 1. 准备测试数据
            emp_code = self.mock_util.generate_unique_code(tag="AT_EMP_MD")
            emp_name = f"主数据员工_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("员工信息表-保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode", "empName", "status"],
                ["params", "request"]
            )
            set_dict = {
                "empCode": emp_code,
                "empName": emp_name,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-保存主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存员工主数据成功: Code={emp_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 查询相关测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试分页查询",
        description="验证ORG_EMPLOYEE_MD_PAGING_DATA_SERVICE功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["sys_common", "employee", "查询"]
    )
    def test_paging_query(self):
        """分页查询员工"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-分页数据服务")
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
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("分页查询员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试员工分页查询服务",
        description="验证ORG_EMPLOYEE_PAGING_SERVICE功能",
        severity="critical",
        order=6,
        tags=["sys_common", "employee", "查询"]
    )
    def test_employee_paging_service(self):
        """员工分页查询服务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-员工分页查询服务")
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
                api_key="员工信息表-员工分页查询服务",
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
    
    @case_decorator(
        story="员工信息管理",
        title="测试查找单条数据",
        description="验证ORG_EMPLOYEE_MD_FIND_ONE_DATA_SERVICE功能",
        severity="critical",
        order=7,
        tags=["sys_common", "employee", "查询"]
    )
    def test_find_one_data(self):
        """查找单条员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_code:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"empCode": self.employee_code})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-查找单条数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"查找单条员工数据成功: Code={self.employee_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试查找列表数据",
        description="验证ORG_EMPLOYEE_MD_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=8,
        tags=["sys_common", "employee", "查询"]
    )
    def test_find_list_data(self):
        """查找员工列表数据"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找员工列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试根据ID查找数据",
        description="验证ORG_EMPLOYEE_MD_FIND_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=9,
        smoke=True,
        tags=["sys_common", "employee", "查询"]
    )
    def test_find_data_by_id(self):
        """根据ID查找员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找员工数据成功: ID={self.employee_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试根据ID查找单表数据",
        description="验证ORG_EMPLOYEE_MD_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=10,
        tags=["sys_common", "employee", "查询"]
    )
    def test_find_single_data_by_id(self):
        """根据ID查找单表员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表数据成功: ID={self.employee_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试根据ID列表查找数据",
        description="验证ORG_EMPLOYEE_MD_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=11,
        tags=["sys_common", "employee", "查询"]
    )
    def test_find_data_by_ids(self):
        """根据ID列表查找员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.employee_id]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找员工数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 更新相关测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试根据ID更新数据",
        description="验证ORG_EMPLOYEE_MD_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=12,
        smoke=True,
        tags=["sys_common", "employee", "更新"]
    )
    def test_update_data_by_id(self):
        """根据ID更新员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 准备更新数据
            new_name = f"更新后员工_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("员工信息表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "empName"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.employee_id,
                "empName": new_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新员工成功: ID={self.employee_id}, 新名称={new_name}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 启用禁用相关测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试启用主数据",
        description="验证ORG_EMPLOYEE_MD_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="critical",
        order=13,
        tags=["sys_common", "employee", "启用禁用"]
    )
    def test_enable_data(self):
        """启用员工主数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"启用员工成功: ID={self.employee_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试禁用主数据",
        description="验证ORG_EMPLOYEE_MD_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="critical",
        order=14,
        tags=["sys_common", "employee", "启用禁用"]
    )
    def test_disable_data(self):
        """禁用员工主数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"禁用员工成功: ID={self.employee_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试批量启用主数据",
        description="验证ORG_EMPLOYEE_MD_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=15,
        tags=["sys_common", "employee", "启用禁用"]
    )
    def test_multi_enable_data(self):
        """批量启用员工主数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-批量启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.employee_id]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-批量启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量启用员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试批量禁用主数据",
        description="验证ORG_EMPLOYEE_MD_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "employee", "启用禁用"]
    )
    def test_multi_disable_data(self):
        """批量禁用员工主数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-批量禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.employee_id]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-批量禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量禁用员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 其他功能测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试折叠关联关系",
        description="验证ORG_EMPLOYEE_MD_FOLDING_ASSOCIATED_SERVICE功能",
        severity="normal",
        order=17,
        tags=["sys_common", "employee", "其他"]
    )
    def test_folding_associated(self):
        """折叠员工关联关系"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-折叠关联关系服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-折叠关联关系服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("折叠员工关联关系成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 导入导出测试 ====================
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="员工信息管理",
        title="测试标准导入",
        description="验证ORG_EMPLOYEE_MD_GEI_IMPORT_SERVICE功能",
        severity="normal",
        order=18,
        tags=["sys_common", "employee", "导入"]
    )
    def test_gei_import(self):
        """标准导入员工数据"""
        try:
            api_path = self.get_api_path("员工信息表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工信息表标准导入服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("标准导入员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="员工信息管理",
        title="测试标准导出",
        description="验证ORG_EMPLOYEE_MD_GEI_EXPORT_SERVICE功能",
        severity="normal",
        order=19,
        tags=["sys_common", "employee", "导出"]
    )
    def test_gei_export(self):
        """标准导出员工数据"""
        try:
            api_path = self.get_api_path("员工信息表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工信息表标准导出服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("标准导出员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="员工信息管理",
        title="测试通过OSS提交导入任务",
        description="验证ORG_EMPLOYEE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        order=20,
        tags=["sys_common", "employee", "导入"]
    )
    def test_import_by_oss(self):
        """通过OSS提交导入任务"""
        try:
            api_path = self.get_api_path("员工信息表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工信息表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("OSS导入任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导出任务需要具体配置，复杂度较高")
    @case_decorator(
        story="员工信息管理",
        title="测试提交导出任务",
        description="验证ORG_EMPLOYEE_MD_API_GEI_TASK_EXPORT_DIRECT_POST功能",
        severity="normal",
        order=21,
        tags=["sys_common", "employee", "导出"]
    )
    def test_export_task(self):
        """提交导出任务"""
        try:
            api_path = self.get_api_path("员工信息表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="员工信息表-导入导出任务管理接口-提交导出任务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 删除相关测试 ====================
    
    @case_decorator(
        story="员工信息管理",
        title="测试根据ID删除数据",
        description="验证ORG_EMPLOYEE_MD_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=22,
        tags=["sys_common", "employee", "删除"]
    )
    def test_delete_data_by_id(self):
        """根据ID删除员工数据"""
        try:
            # 确保有测试数据
            if not self.employee_id:
                self.test_create_employee()
            
            # 1. 调用API
            api_path = self.get_api_path("员工信息表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.employee_id})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除员工成功: ID={self.employee_id}")
            
            # 4. 清空ID（已删除）
            self.__class__.employee_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="员工信息管理",
        title="测试批量删除数据",
        description="验证ORG_EMPLOYEE_MD_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=23,
        tags=["sys_common", "employee", "删除"]
    )
    def test_batch_delete_data(self):
        """批量删除员工数据"""
        try:
            # 创建测试数据用于删除
            test_id = None
            emp_code = self.mock_util.generate_unique_code(tag="AT_EMP_DEL")
            emp_name = f"待删除员工_{self.mock_util.get_timestamp()}"
            
            # 创建数据
            api_path = self.get_api_path("员工信息表-创建数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["empCode", "empName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "empCode": emp_code,
                "empName": emp_name,
                "status": "ENABLED"
            })
            response, _ = self.standard_api_call(
                api_key="员工信息表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            test_id = response.get("data", {}).get("data", {})
            
            # 1. 调用批量删除API
            api_path = self.get_api_path("员工信息表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [test_id]})
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="员工信息表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除员工成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
