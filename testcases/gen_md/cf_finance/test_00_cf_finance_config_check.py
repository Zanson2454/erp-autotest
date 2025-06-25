import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("币种管理配置检查")
class TestCurrConfigCheck(GenMdBaseTest):
    """币种管理配置检查测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.required_curr_types = ["TYPE1", "TYPE2"]  # 必需的币种管理类型编码

    @case_decorator(
        story="币种管理配置检查",
        title="测试币种管理配置是否完整",
        description="验证系统中是否包含所需的基础币种管理配置",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["币种管理", "配置检查"]
    )
    def test_curr_type_config(self):
        """
        检查币种管理配置用例
        验证系统中是否包含必需的币种管理类型编码
        """
        try:
            # 这里需要根据实际API进行调整
            api_path = self.get_api_path("待补充具体API名称")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )

            # 设置分页和查询字段参数
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 100,
                    "needTotal": True
                },
                "fields": [
                    {"name": "curr_type_code", "type": "TEXT"},
                    {"name": "curr_type_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            curr_type_list = response.get("data", {}).get("data", {}).get("data", [])
            curr_type_codes = [item.get("curr_type_code") for item in curr_type_list]
            self.logger.info(f"curr_type_codes: {curr_type_codes}")
            
            # 检查所有必需的币种管理类型是否都存在
            self.assert_util.assert_all_in(
                self.required_curr_types, 
                curr_type_codes,
                "币种管理配置不完整"
            )

            # 记录到Allure报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"所有必需的币种管理类型均已配置: {', '.join(self.required_curr_types)}", "检查结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
