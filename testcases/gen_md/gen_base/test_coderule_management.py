import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("编码规则管理")
class TestCodeRuleManagement(GenMdBaseTest):
    """编码规则管理测试类 - 覆盖编码规则的编辑、查询详情、分页查询功能"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.code_rule_id = None
        cls.code_rule_code = None
        cls.logger.info("编码规则管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 编码规则通常是系统预设数据，不需要清理测试数据
            cls.logger.info("编码规则测试类结束")
        except Exception as e:
            cls.logger.error(f"测试类结束异常: {str(e)}")

    # ================ 编码规则管理 ================
    @case_decorator(
        story="编码规则管理",
        title="测试分页查询编码规则",
        description="验证GEN-编码规则-分页查询服务功能",
        severity="critical",
        order=1,
        smoke=True,
        tags=["编码规则", "分页查询", "GEN_CODE_RULE_PAGE_ACTION_SERVICE"]
    )
    def test_query_code_rule_page(self):
        """分页查询编码规则用例 - GEN_CODE_RULE_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-编码规则-分页查询服务")
            params, url = self.get_api_params(api_path)

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
                    {"name": "ruleCode", "type": "TEXT"},
                    {"name": "ruleName", "type": "TEXT"},
                    {"name": "ruleType", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 保存第一个编码规则ID用于后续测试
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            if data_list:
                self.code_rule_id = data_list[0].get("id")
                self.code_rule_code = data_list[0].get("ruleCode")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="编码规则管理",
        title="测试查询编码规则详情",
        description="验证GEN-编码规则-查询详情服务功能",
        severity="critical",
        order=2,
        tags=["编码规则", "查询详情", "GEN_CODE_RULE_DETAIL_ACTION_SERVICE"]
    )
    def test_query_code_rule_detail(self):
        """查询编码规则详情用例 - GEN_CODE_RULE_DETAIL_ACTION_SERVICE"""
        try:
            if not self.code_rule_id:
                self.test_query_code_rule_page()

            # 如果分页查询没有返回数据，使用模拟ID
            if not self.code_rule_id:
                self.logger.warning("未获取到编码规则ID，使用模拟ID进行测试")
                self.code_rule_id = 1

            api_path = self.get_api_path("GEN-编码规则-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.code_rule_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="编码规则管理",
        title="测试编辑编码规则",
        description="验证GEN-编码规则-编辑规则服务功能",
        severity="blocker",
        order=3,
        tags=["编码规则", "编辑", "GEN_CODE_RULE_UPDATE_ACTION_SERVICE"]
    )
    def test_update_code_rule(self):
        """编辑编码规则用例 - GEN_CODE_RULE_UPDATE_ACTION_SERVICE"""
        try:
            if not self.code_rule_id:
                self.test_query_code_rule_page()

            # 如果分页查询没有返回数据，使用模拟ID
            if not self.code_rule_id:
                self.logger.warning("未获取到编码规则ID，使用模拟ID进行测试")
                self.code_rule_id = 1

            api_path = self.get_api_path("GEN-编码规则-编辑规则服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "ruleName", "ruleDesc", "rulePattern", "status"], ["params", "request"]
            )
            set_dict = {
                "id": self.code_rule_id,
                "ruleName": f"更新编码规则名称_{self.mock_util.get_timestamp()}",
                "ruleDesc": f"更新编码规则描述_{self.mock_util.get_timestamp()}",
                "rulePattern": "{PREFIX}{YYYYMMDD}{HHMMSS}{###}",  # 示例编码模式
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
