
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
@allure.feature("订单行项目类型组管理")
class TestSlsItemTypeGroupManagement(SlsBase):
    """销售订单行项目类型组管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.item_type_group_id = None
        cls.logger.info("销售订单行项目类型组管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

    @case_decorator(
        story="订单行项目类型组管理",
        title="测试保存订单行项目类型组",
        description="验证SLS-订单行项目类型组-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["订单行项目类型组", "保存", "sls_item_type_group_save_service"]
    )
    def test_save_item_type_group(self):
        """保存订单行项目类型组用例"""
        try:
            # 1. 准备测试数据
            item_type_group_code = self.mock_util.generate_unique_code(tag="ItemTypeGroup")
            item_type_group_name = f"测试订单行项目类型组_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-订单行项目类型组-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "desc"], ["params", "request"]
            )
            set_dict = {
                "code": item_type_group_code,
                "name": item_type_group_name,
                "desc": f'测试订单行项目类型组_{self.mock_util.get_timestamp()}' 
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单行项目类型组-保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            self.item_type_group_id = response.get("data", {}).get("data", {}).get("id")
            self.item_type_group_code = item_type_group_code
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单行项目类型组管理",
        title="测试查询订单行项目类型组分页列表",
        description="验证SLS-订单行项目类型组-分页服务功能",
        severity="normal",
        order=2,
        tags=["订单行项目类型组", "查询", "sls_item_type_group_paging_service"]
    )
    def test_query_item_type_group_page(self):
        """查询订单行项目类型组分页列表用例"""
        try:
            # 1. 确保有测试数据
            if not self.item_type_group_id:
                self.test_save_item_type_group()
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-订单行项目类型组-分页服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
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
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "desc", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单行项目类型组-分页服务",
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
        story="订单行项目类型组管理",
        title="测试查询订单行项目类型组详情",
        description="验证SLS-订单行项目类型组-详情服务功能",
        severity="normal",
        order=3,
        tags=["订单行项目类型组", "查询", "sls_item_type_group_detail_service"]
    )
    def test_query_item_type_group_detail(self):
        """查询订单行项目类型组详情用例"""
        try:
            # 1. 确保有测试数据
            if not self.item_type_group_id:
                self.test_save_item_type_group()
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-订单行项目类型组-详情服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.item_type_group_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单行项目类型组-详情服务",
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
