import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("模型系统管理")
class TestModelSystemManagement(GenMdBaseTest):
    """模型系统管理测试类 - 覆盖模型系统分页查询和根据ID集合查询详情功能"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.model_system_id = None
        cls.model_system_ids = []
        cls.logger.info("模型系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 模型系统通常是系统预设数据，不需要清理测试数据
            cls.logger.info("模型系统测试类结束")
        except Exception as e:
            cls.logger.error(f"测试类结束异常: {str(e)}")

    # ================ 模型系统管理 ================
    @case_decorator(
        story="模型系统管理",
        title="测试模型系统分页查询",
        description="验证模型系统分页查询服务功能",
        severity="critical",
        order=1,
        smoke=True,
        tags=["模型系统", "分页查询", "GEN_MODEL_SYSTEM_PAGING_ACTION_SERVICE"]
    )
    def test_query_model_system_page(self):
        """模型系统分页查询用例 - GEN_MODEL_SYSTEM_PAGING_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("模型系统分页查询服务")
            params, url = self.get_api_params(api_path)

            params['params']={
                "request": {
                    "modelKey": "GEN_MD$gen_coun_type_cf",
                    "pageable": {
                        "pageNo": "1",
                        "pageSize": "10"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            # 保存模型系统ID用于后续测试
            data_list = response.get("data", {}).get("data", {}).get("data", []).get("data", [])
            if data_list:
                self.model_system_id = data_list[0].get("id")
                # 收集多个ID用于根据ID集合查询测试
                self.model_system_ids = [item.get("id") for item in data_list[:3] if item.get("id")]

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="模型系统管理",
        title="测试模型根据ID集合查询详情",
        description="验证模型根据ID集合查询详情服务功能",
        severity="critical",
        order=2,
        tags=["模型系统", "查询详情", "GEN_MODEL_SYSTEM_QUERY_BY_IDS_ACTION_SERVICE"]
    )
    def test_query_model_system_by_ids(self):
        """模型根据ID集合查询详情用例 - GEN_MODEL_SYSTEM_QUERY_BY_IDS_ACTION_SERVICE"""
        try:
            if not self.model_system_id:
                self.test_query_model_system_page()

    
            api_path = self.get_api_path("模型根据ID集合查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids","modelKey"], ["params", "request"]
            )
            set_dict = {
                "ids": [self.model_system_id],
                "modelKey":"GEN_MD$gen_coun_type_cf"
                }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
