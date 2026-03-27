import allure
import pytest
from testcases.sys_common import SysCommonBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("系统通用模块")
@allure.feature("用户管理")
class TestUserManagement(SysCommonBaseTest):
    """用户管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mock_data = MockData()


    
    @case_decorator(
        story="用户管理",
        title="测试根据ID查询用户数据",
        description="验证USER_FIND_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["sys_common", "user", "查询"]
    )
    def test_query_user_by_id(self):
        """
        根据ID查询用户数据用例 - USER_FIND_DATA_BY_ID_SERVICE
        """
        try:
            # 准备测试用户ID（模拟已有用户或通过创建获取）
            # 这里假设有一个测试用户ID，或者通过创建用户获取
            test_user_id = self.user_id  # 模拟测试用户ID
            
            # 调用查询接口
            api_path = self.get_api_path("用户-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": test_user_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            
            response, _ = self.standard_api_call(
                api_key="用户-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 保存用户ID供后续用例使用
            response_data = response.get("data", {}).get("data", {})
            if isinstance(response_data, dict):
                self.user_id = response_data.get("id", test_user_id)
                self.user_code = response_data.get("userCode")
            else:
                self.user_id = test_user_id
                self.user_code = f"AT_USER_{self.mock_data.get_timestamp()}"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="用户管理",
        title="测试根据ID查询单表用户数据",
        description="验证USER_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        file_level_order=2,
        smoke=True,
        tags=["sys_common", "user", "查询"]
    )
    def test_query_single_user_by_id(self):
        """
        根据ID查询单表用户数据用例 - USER_FIND_SINGLE_DATA_BY_ID_SERVICE
        """
        try:
            # 获取用户ID
            if not self.user_id:
                self.test_query_user_by_id()
            
            # 调用单表查询接口
            api_path = self.get_api_path("用户-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.user_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            
            response, _ = self.standard_api_call(
                api_key="用户-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证返回的基本用户信息
            user_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(user_data.get("id"), "=", self.user_id)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="用户管理",
        title="测试用户关联关系折叠",
        description="验证USER_FOLDING_ASSOCIATED_SERVICE功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["sys_common", "user", "关联关系"]
    )
    def test_folding_user_associated(self):
        """
        用户关联关系折叠用例 - USER_FOLDING_ASSOCIATED_SERVICE
        """
        try:
            # 获取用户ID
            if not self.user_id:
                self.test_query_user_by_id()
            
            # 调用关联关系折叠接口
            api_path = self.get_api_path("用户-折叠关联关系服务")
            params, url = self.get_api_params(api_path)
            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "request"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.user_id,
                "request": {
                    "updatedBy": self.user_id,
                    "createdBy": self.user_id,
                    "tenantId": self.env_config.get("tenant_id", 22)
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            
            response, _ = self.standard_api_call(
                api_key="用户-折叠关联关系服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证折叠后的关联数据结构
            associated_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(associated_data, "not_empty", "关联数据不能为空")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="用户管理",
        title="测试用户分页查询",
        description="验证USER_PAGING_DATA_SERVICE功能",
        severity="blocker",
        file_level_order=4,
        smoke=True,
        tags=["sys_common", "user", "分页查询"]
    )
    def test_query_user_paging(self):
        """
        用户分页查询用例 - USER_PAGING_DATA_SERVICE
        """
        try:
            # 调用分页查询接口
            api_path = self.get_api_path("用户-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "userCode", "type": "TEXT"},
                    {"name": "userName", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            
            response, _ = self.standard_api_call(
                api_key="用户-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证分页结果
            paging_data = response.get("data", {}).get("data", {})
            user_list = paging_data.get("data", [])
            total_count = paging_data.get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(user_list), "<=", 20, "每页记录数不应超过20")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="用户管理",
        title="测试用户完整查询流程",
        description="验证用户从分页查询到详情查询的完整流程",
        severity="critical",
        file_level_order=5,
        tags=["sys_common", "user", "综合测试"]
    )
    def test_user_complete_query_workflow(self):
        """
        用户完整查询流程测试用例
        """
        try:
            # 1. 执行分页查询获取用户列表
            api_path_paging = self.get_api_path("用户-分页数据服务")
            params_paging, url_paging = self.get_api_params(api_path_paging)
            
            filtered_params_paging = ParamUtil.filter_post_body_fields(
                params_paging,
                ["pageable"],
                ["params", "request"]
            )
            paging_set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                }
            }
            ParamUtil.set_request_params(filtered_params_paging, paging_set_dict)
            
            paging_response, _ = self.standard_api_call(
                api_key="用户-分页数据服务",
                set_dict=filtered_params_paging.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(paging_response)
            
            # 2. 从分页结果中获取第一个用户ID
            paging_data = paging_response.get("data", {}).get("data", {})
            user_list = paging_data.get("data", [])
            
            if user_list:
                first_user_id = user_list[0].get("id")
                self.logger.info(f"从分页获取到用户ID: {first_user_id}")
                
                # 3. 使用获取的用户ID查询详情
                api_path_detail = self.get_api_path("用户-根据ID查找数据服务")
                params_detail, url_detail = self.get_api_params(api_path_detail)
                
                filtered_params_detail = ParamUtil.filter_post_body_fields(
                    params_detail,
                    ["id"],
                    ["params", "request"]
                )
                detail_set_dict = {"id": first_user_id}
                ParamUtil.set_request_params(filtered_params_detail, detail_set_dict)
                
                detail_response, _ = self.standard_api_call(
                    api_key="用户-根据ID查找数据服务",
                    set_dict=filtered_params_detail.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_data(detail_response)
                
                # 4. 验证详情查询结果
                detail_data = detail_response.get("data", {}).get("data", {})
                self.assert_util.assert_by_operator(detail_data.get("id"), "=", first_user_id, "用户ID不匹配")
                
                a.json({"workflow": "user_query_complete"}, "完整查询流程执行成功")
                a.json(paging_response, "分页查询响应")
                a.json(detail_response, "详情查询响应")
            else:
                a.text("分页查询未返回用户数据", "流程验证信息")
                self.logger.warning("分页查询未返回用户数据，跳过详情验证")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
