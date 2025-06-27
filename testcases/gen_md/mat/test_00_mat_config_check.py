import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("物料类型配置检查")
class TestMatConfigCheck(GenMdBaseTest):
    """物料类型配置检查测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.required_mat_types = ["FINP", "SERV"]  # 必需的物料类型编码

    @case_decorator(
        story="物料类型配置检查",
        title="测试物料类型配置是否完整",
        description="验证系统中是否包含所需的基础物料类型配置",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["物料类型", "配置检查"]
    )
    def test_mat_type_config(self):
        """
        检查物料类型配置用例
        验证系统中是否包含必需的物料类型编码：
        - FINP：成品
        - SERV：服务
        - RAWM：原材料
        """
        try:
            api_path = self.get_api_path("GEN-物料类型-查询分页服务")
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
                    "pageSize": 100,  # 设置较大的页面大小以获取所有记录
                    "needTotal": True
                },
                "fields": [
                    {"name": "matTypeCode", "type": "TEXT"},
                    {"name": "matTypeName", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            mat_type_list = response.get("data", {}).get("data", {}).get("data", [])
            mat_type_codes = [item.get("matTypeCode") for item in mat_type_list]
            self.logger.info(f"mat_type_codes: {mat_type_codes}")
            
            # 检查所有必需的物料类型是否都存在
            self.assert_util.assert_all_in(
                self.required_mat_types, 
                mat_type_codes,
                "物料类型配置不完整"
            )

            # 记录到Allure报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"所有必需的物料类型均已配置: {', '.join(self.required_mat_types)}", "检查结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
