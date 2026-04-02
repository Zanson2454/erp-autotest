import allure
import pytest
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售渠道管理")
class TestSlsDcManagement(SlsBase):
    """销售渠道管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.sls_dc_id = None
        cls.sls_dc_code = None
        cls.sls_org_id = None
        cls.logger.info("销售渠道管理测试类初始化完成")
        
        # 获取依赖数据
        cls.sls_org_id = cls.md_cache_data.get("org_info", {}).get("sls_org_info", [])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

        super().teardown_class()
    @case_decorator(
        story="销售渠道管理",
        title="测试创建销售渠道",
        description="验证创建销售渠道功能",
        severity="critical",
        order=1,
        smoke=True,
        tags=["销售管理", "销售渠道"]
    )
    def test_save_sls_dc(self):
        """测试创建销售渠道"""
        try:
            # 1. 准备测试数据
            sls_dc_code = self.mock_util.generate_unique_code(tag="DC")
            sls_dc_name = f"自动化销售渠道_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-销售渠道-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "isOnline"], ["params", "request"]
            )
            set_dict = {
                "code": sls_dc_code,
                "name": sls_dc_name,
                "isOnline": True
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            self.sls_dc_id = response.get("data", {}).get("data", {}).get("id")
          
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试查询销售渠道详情",
        description="验证根据ID查询销售渠道详情功能",
        severity="critical",
        order=2,
        tags=["销售管理", "销售渠道"]
    )
    def test_query_sls_dc_detail(self):
        """测试查询销售渠道详情"""
        try:
            # 检查依赖数据
            if not self.sls_dc_id:
                self._ensure_save_sls_dc()
            
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售渠道-查询详情")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.sls_dc_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-查询详情",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试分页查询销售渠道",
        description="验证分页查询销售渠道列表功能",
        severity="normal",
        order=3,
        tags=["销售管理", "销售渠道"]
    )
    def test_query_sls_dc_paging(self):
        """测试分页查询销售渠道"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售渠道-分页服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-分页服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试根据销售组织查询销售渠道",
        description="验证根据销售组织ID查询销售渠道功能",
        severity="normal",
        order=4,
        tags=["销售管理", "销售渠道"]
    )
    def test_query_sls_dc_by_org(self):
        """测试根据销售组织查询销售渠道"""
        try:
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-销售渠道-根据销售组织查询销售渠道")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["slsOrgId", "pageable"], ["params", "request"]
            )
            set_dict = {
                "slsOrgId": self.sls_org_id,
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-根据销售组织查询销售渠道",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试停用销售渠道",
        description="验证停用销售渠道功能",
        severity="critical",
        order=5,
        tags=["销售管理", "销售渠道"]
    )
    def test_disable_sls_dc(self):
        """测试停用销售渠道"""
        try:
            # 检查依赖数据
            if not self.sls_dc_id:
                self._ensure_save_sls_dc()
            
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售渠道-停用")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.sls_dc_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-停用",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            sql = f"select `status` from sls_dc_md where id = {self.sls_dc_id}"
            status = self.query_service.query(sql)[0].get("status")
            self.assert_util.assert_by_operator(status, "=", "DISABLED")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试启用销售渠道",
        description="验证启用销售渠道功能",
        severity="critical",
        order=6,
        tags=["销售管理", "销售渠道"]
    )
    def test_enable_sls_dc(self):
        """测试启用销售渠道"""
        try:
            # 检查依赖数据
            if not self.sls_dc_id:
                self._ensure_save_sls_dc()
            
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售渠道-启用")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.sls_dc_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售渠道-启用",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            sql = f"select `status` from sls_dc_md where id = {self.sls_dc_id}"
            status = self.query_service.query(sql)[0].get("status")
            self.assert_util.assert_by_operator(status, "=", "ENABLED")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试导出销售渠道",
        description="验证导出销售渠道功能",
        severity="normal",
        order=7,
        tags=["销售管理", "销售渠道"]
    )
    @pytest.mark.skip(reason="标准导出服务暂时跳过")
    def test_export_sls_dc(self):
        """测试导出销售渠道"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售渠道标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售渠道标准导出服务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试导入销售渠道",
        description="验证导入销售渠道功能",
        severity="normal",
        order=8,
        tags=["销售管理", "销售渠道"]
    )
    @pytest.mark.skip(reason="标准导入服务暂时跳过")
    def test_import_sls_dc(self):
        """测试导入销售渠道"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售渠道标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售渠道标准导入服务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试销售渠道导出任务管理",
        description="验证销售渠道导出任务管理接口功能",
        severity="normal",
        order=9,
        tags=["销售管理", "销售渠道"]
    )
    @pytest.mark.skip(reason="OSS导出任务管理接口暂时跳过")
    def test_export_task_sls_dc(self):
        """测试销售渠道导出任务管理"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售渠道-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售渠道-导入导出任务管理接口-提交导出任务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售渠道管理",
        title="测试销售渠道导入任务管理",
        description="验证销售渠道导入任务管理接口功能",
        severity="normal",
        order=10,
        tags=["销售管理", "销售渠道"]
    )
    @pytest.mark.skip(reason="OSS导入任务管理接口暂时跳过")
    def test_import_task_sls_dc(self):
        """测试销售渠道导入任务管理"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("销售渠道-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售渠道-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
