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
@allure.feature("导入导出配置管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestGeiConfigManagement(SysCommonBaseTest):
    """导入导出配置管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("导入导出配置管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 配置通常不需特定数据清理
            cls.logger.info("导入导出配置测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="导入导出配置管理",
        title="测试表头预测",
        description="验证API_GEI_TASK_CONFIG_PREDICT_POST功能 - 表头预测",
        severity="normal",
        order=1,
        tags=["sys_common", "gei", "config", "predict"]
    )
    def test_config_predict_post(self):
        """测试表头预测 - API_GEI_TASK_CONFIG_PREDICT_POST"""
        try:
            api_path = self.get_api_path("导入导出配置管理接口-表头预测")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["headerInfo"], ["params"])
            set_dict = {"headerInfo": ["Column1", "Column2"]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出配置管理接口-表头预测",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            predict_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(predict_data, "not_empty", "预测结果不能为空")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出配置管理",
        title="测试判断是否自定义导入",
        description="验证API_GEI_TASK_CONFIG_JUDGE_IF_CUSTOM_IMPORT_POST功能 - 判断自定义导入",
        severity="minor",
        order=2,
        tags=["sys_common", "gei", "config", "judge"]
    )
    def test_config_judge_custom_post(self):
        """测试判断是否自定义导入 - API_GEI_TASK_CONFIG_JUDGE_IF_CUSTOM_IMPORT_POST"""
        try:
            api_path = self.get_api_path("导入导出配置管理接口-判断是否自定义导入")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["modelKey"], ["params"])
            set_dict = {"modelKey": "TEST_MODEL"}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出配置管理接口-判断是否自定义导入",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            judge_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(judge_data.get("isCustom"), "in", [True, False])
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出配置管理",
        title="测试保存表头选择记录",
        description="验证API_GEI_TASK_CONFIG_SAVE_HEADER_SELECTIVE_RECORD_POST功能 - 保存表头选择",
        severity="normal",
        order=3,
        tags=["sys_common", "gei", "config", "save_header"]
    )
    def test_config_save_header_post(self):
        """测试保存表头选择记录 - API_GEI_TASK_CONFIG_SAVE_HEADER_SELECTIVE_RECORD_POST"""
        try:
            api_path = self.get_api_path("导入导出配置管理接口-保存表头选择记录")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["selectedHeaders"], ["params"])
            set_dict = {"selectedHeaders": ["field1", "field2"]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出配置管理接口-保存表头选择记录",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出配置管理",
        title="测试查询表头选择记录",
        description="验证API_GEI_TASK_CONFIG_QUERY_HEADER_SELECTIVE_RECORD_POST功能 - 查询表头选择",
        severity="normal",
        order=4,
        tags=["sys_common", "gei", "config", "query_header"]
    )
    def test_config_query_header_post(self):
        """测试查询表头选择记录 - API_GEI_TASK_CONFIG_QUERY_HEADER_SELECTIVE_RECORD_POST"""
        try:
            self._ensure_config_save_header_post()
            
            api_path = self.get_api_path("导入导出配置管理接口-查询表头选择记录")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="导入导出配置管理接口-查询表头选择记录",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            query_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(query_data, "not_empty", "查询结果不能为空")
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出配置管理",
        title="测试自定义导入Demo",
        description="验证API_GEI_TASK_CONFIG_CUSTOM_IMPORT_DEMO_POST功能 - 自定义导入Demo",
        severity="minor",
        order=5,
        tags=["sys_common", "gei", "config", "demo"]
    )
    def test_config_custom_demo_post(self):
        """测试自定义导入Demo - API_GEI_TASK_CONFIG_CUSTOM_IMPORT_DEMO_POST"""
        try:
            api_path = self.get_api_path("导入导出配置管理接口-自定义导入Demo")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["modelKey"], ["params"])
            set_dict = {"modelKey": "TEST_MODEL"}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="导入导出配置管理接口-自定义导入Demo",
                set_dict=filtered_params.get("params", {}),
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
