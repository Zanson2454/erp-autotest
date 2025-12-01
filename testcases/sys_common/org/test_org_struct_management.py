"""
组织架构管理测试用例
覆盖组织架构表的增删改查、启用禁用、导入导出等功能
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
@allure.feature("组织架构管理")
class TestOrgStructManagement(SysCommonBaseTest):
    """组织架构管理测试类"""
    
    org_struct_id = None
    org_struct_code = None
    org_struct_name = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.org_struct_id = None
        cls.org_struct_code = None
        cls.org_struct_name = None
        cls.logger.info("组织架构管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="org_struct_md",
                where="org_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("组织架构测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"组织架构测试数据清理失败: {str(e)}")
    
    # ==================== 创建相关测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试创建组织架构",
        description="验证ORG_STRUCT_MD_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "org_struct", "创建"]
    )
    def test_create_org_struct(self):
        """创建组织架构数据"""
        try:
            # 1. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="AT_ORG")
            org_name = f"自动化测试组织_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("组织架构表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["orgCode", "orgName", "orgType", "status"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgType": "COMPANY",  # 公司类型
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据
            self.__class__.org_struct_id = response.get("data", {}).get("data", {})
            self.__class__.org_struct_code = org_code
            self.__class__.org_struct_name = org_name
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建组织架构成功: ID={self.org_struct_id}, Code={org_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试保存组织架构",
        description="验证ORG_STRUCT_MD_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=2,
        tags=["sys_common", "org_struct", "创建"]
    )
    def test_save_org_struct(self):
        """保存组织架构数据（新增或更新）"""
        try:
            # 1. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="AT_ORG_SAVE")
            org_name = f"保存测试组织_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("组织架构表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgType", "status"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgType": "DEPARTMENT",  # 部门类型
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存组织架构成功: Code={org_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试批量创建组织架构",
        description="验证ORG_STRUCT_MD_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=3,
        tags=["sys_common", "org_struct", "创建"]
    )
    def test_batch_create_org_struct(self):
        """批量创建组织架构数据"""
        try:
            # 1. 准备批量测试数据
            org_list = []
            for i in range(3):
                org_code = self.mock_util.generate_unique_code(tag=f"AT_ORG_BATCH_{i}")
                org_name = f"批量测试组织{i}_{self.mock_util.get_timestamp()}"
                org_list.append({
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgType": "DEPARTMENT",
                    "status": "ENABLED"
                })
            
            # 2. 调用API
            api_path = self.get_api_path("组织架构表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": org_list})
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"批量创建组织架构成功: 共{len(org_list)}条")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 查询相关测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试查找树数据",
        description="验证ORG_STRUCT_MD_FIND_TREE_DATA_SERVICE功能",
        severity="critical",
        order=4,
        smoke=True,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_tree_data(self):
        """查找组织架构树数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-查找树数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)
            
            # 3. 记录报告
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织架构树数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试分页查询",
        description="验证ORG_STRUCT_MD_PAGING_DATA_SERVICE功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_paging_query(self):
        """分页查询组织架构"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-分页查询服务")
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
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("分页查询组织架构成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试查找列表数据",
        description="验证ORG_STRUCT_MD_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=6,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_list_data(self):
        """查找组织架构列表数据"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)
            
            # 3. 记录报告
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织架构列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试查找单条数据",
        description="验证ORG_STRUCT_MD_FIND_ONE_DATA_SERVICE功能",
        severity="critical",
        order=7,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_one_data(self):
        """查找单条组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_code:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"orgCode": self.org_struct_code})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"查找单条组织架构数据成功: Code={self.org_struct_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试根据ID查找单表数据",
        description="验证ORG_STRUCT_MD_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=8,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_single_data_by_id(self):
        """根据ID查找单表组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表数据成功: ID={self.org_struct_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试根据ID查找数据",
        description="验证ORG_STRUCT_MD_FIND_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=9,
        smoke=True,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_data_by_id(self):
        """根据ID查找组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找数据成功: ID={self.org_struct_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试根据ID列表查找数据",
        description="验证ORG_STRUCT_MD_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=10,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_data_by_ids(self):
        """根据ID列表查找组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.org_struct_id]})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试查找树子数据",
        description="验证ORG_STRUCT_MD_FIND_TREE_CHILDREN_DATA_SERVICE功能",
        severity="normal",
        order=11,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_find_tree_children_data(self):
        """查找组织架构树子数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-查找树子数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["parentId"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"parentId": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找树子数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试反向构建树",
        description="验证ORG_STRUCT_MD_REVERSE_CONSTRUCT_TREE_SERVICE功能",
        severity="normal",
        order=12,
        tags=["sys_common", "org_struct", "查询"]
    )
    def test_reverse_construct_tree(self):
        """反向构建组织架构树"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-反向构建树服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("反向构建树成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 更新相关测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试根据ID更新数据",
        description="验证ORG_STRUCT_MD_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=13,
        smoke=True,
        tags=["sys_common", "org_struct", "更新"]
    )
    def test_update_data_by_id(self):
        """根据ID更新组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 准备更新数据
            new_name = f"更新后组织_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("组织架构表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "orgName"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.org_struct_id,
                "orgName": new_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新组织架构成功: ID={self.org_struct_id}, 新名称={new_name}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 启用禁用相关测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试启用主数据",
        description="验证ORG_STRUCT_MD_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="critical",
        order=14,
        tags=["sys_common", "org_struct", "启用禁用"]
    )
    def test_enable_data(self):
        """启用组织架构主数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"启用组织架构成功: ID={self.org_struct_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试禁用主数据",
        description="验证ORG_STRUCT_MD_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="critical",
        order=15,
        tags=["sys_common", "org_struct", "启用禁用"]
    )
    def test_disable_data(self):
        """禁用组织架构主数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"禁用组织架构成功: ID={self.org_struct_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试批量启用主数据",
        description="验证ORG_STRUCT_MD_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "org_struct", "启用禁用"]
    )
    def test_multi_enable_data(self):
        """批量启用组织架构主数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-批量启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.org_struct_id]})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量启用组织架构成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试批量禁用主数据",
        description="验证ORG_STRUCT_MD_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=17,
        tags=["sys_common", "org_struct", "启用禁用"]
    )
    def test_multi_disable_data(self):
        """批量禁用组织架构主数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-批量禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.org_struct_id]})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量禁用组织架构成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 其他功能测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试折叠关联关系",
        description="验证ORG_STRUCT_MD_FOLDING_ASSOCIATED_SERVICE功能",
        severity="normal",
        order=18,
        tags=["sys_common", "org_struct", "其他"]
    )
    def test_folding_associated(self):
        """折叠组织架构关联关系"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-折叠关联关系服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("折叠关联关系成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 导入导出测试 ====================
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="组织架构管理",
        title="测试标准导入",
        description="验证ORG_STRUCT_MD_GEI_IMPORT_SERVICE功能",
        severity="normal",
        order=19,
        tags=["sys_common", "org_struct", "导入"]
    )
    def test_gei_import(self):
        """标准导入组织架构数据"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织架构表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 准备导入数据（实际使用时需要准备文件）
            # 此处仅作接口测试
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("标准导入成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="组织架构管理",
        title="测试通过OSS提交导入任务",
        description="验证ORG_STRUCT_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        order=20,
        tags=["sys_common", "org_struct", "导入"]
    )
    def test_import_by_oss(self):
        """通过OSS提交导入任务"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 准备OSS导入参数（实际使用时需要上传文件到OSS）
            # 此处仅作接口测试
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("OSS导入任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 删除相关测试 ====================
    
    @case_decorator(
        story="组织架构管理",
        title="测试根据ID删除数据",
        description="验证ORG_STRUCT_MD_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=21,
        tags=["sys_common", "org_struct", "删除"]
    )
    def test_delete_data_by_id(self):
        """根据ID删除组织架构数据"""
        try:
            # 确保有测试数据
            if not self.org_struct_id:
                self.test_create_org_struct()
            
            # 1. 调用API
            api_path = self.get_api_path("组织架构表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.org_struct_id})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除组织架构成功: ID={self.org_struct_id}")
            
            # 5. 清空ID（已删除）
            self.__class__.org_struct_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织架构管理",
        title="测试批量删除数据",
        description="验证ORG_STRUCT_MD_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=22,
        tags=["sys_common", "org_struct", "删除"]
    )
    def test_batch_delete_data(self):
        """批量删除组织架构数据"""
        try:
            # 创建测试数据用于删除
            test_id = None
            org_code = self.mock_util.generate_unique_code(tag="AT_ORG_DEL")
            org_name = f"待删除组织_{self.mock_util.get_timestamp()}"
            
            # 创建数据
            api_path = self.get_api_path("组织架构表-创建数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgType", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "orgCode": org_code,
                "orgName": org_name,
                "orgType": "DEPARTMENT",
                "status": "ENABLED"
            })
            response = self.http.post(url, json=filtered_params)
            test_id = response.get("data", {}).get("data", {})
            
            # 1. 调用批量删除API
            api_path = self.get_api_path("组织架构表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [test_id]})
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除组织架构成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

