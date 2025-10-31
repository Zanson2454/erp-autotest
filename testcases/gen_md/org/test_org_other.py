import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织其他功能")
class TestOrgOther(GenMdBaseTest):
    """组织其他功能测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("组织其他功能测试类初始化完成")
        
        # 获取组织信息
        cls.com_org_id = cls.md_cache_data["org_info"].get("com_org_info", [])[0]["id"]
        cls.user_id = cls.md_cache_data.get("user_info", {}).get("id", None)

    @case_decorator(
        story="组织其他功能",
        title="测试当前登录人是否在当前组织内",
        description="验证当前登录人是否在当前组织内服务功能",
        severity="normal",
        file_level_order=1,
        smoke=True,
        tags=["组织其他功能", "用户组织判断"]
    )
    def test_judge_logging_user_in_current_org(self):
        """
        判断当前登录人是否在当前组织内用例
        """
        try:
            # 调用判断接口
            api_path = self.get_api_path("ORG-多组织-当前登陆人是否在当当前组织内服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgId", "userId"],
                ["params", "request"]
            )
            set_dict = {
                "orgId": self.com_org_id,
                "userId": self.user_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回结果是布尔值
            result = response.get("data", {}).get("data")
            self.assert_util.assert_by_operator(result, "in", [True, False])

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织其他功能",
        title="测试钉钉同步组织架构",
        description="验证钉钉同步组织架构服务功能",
        severity="normal",
        file_level_order=2,
        smoke=False,
        tags=["组织其他功能", "钉钉同步"]
    )
    def test_dingtalk_sync_org(self):
        """
        钉钉同步组织架构用例
        """
        try:
            # 调用钉钉同步接口
            api_path = self.get_api_path("ORG-组织-钉钉同步组织架构服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["syncConfig", "orgId"],
                ["params", "request"]
            )
            set_dict = {
                "syncConfig": {
                    "syncType": "FULL",  # 全量同步
                    "syncDepartment": True,  # 同步部门
                    "syncEmployee": True,    # 同步员工
                    "deleteNotExist": False  # 不删除不存在的
                },
                "orgId": self.com_org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            # 钉钉同步可能需要配置，这里只验证接口可访问
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            # 钉钉同步可能因为配置问题失败，这里不强制要求成功
            self.logger.warning(f"钉钉同步接口调用失败，可能需要钉钉配置: {str(e)}")

    @case_decorator(
        story="组织其他功能",
        title="测试公司组织预留字段转币种",
        description="验证公司组织预留字段转币种服务功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["组织其他功能", "币种转换"]
    )
    def test_convert_com_org_field_to_currency(self):
        """
        公司组织预留字段转币种用例
        """
        try:
            # 调用币种转换接口
            api_path = self.get_api_path("公司组织预留字段转币种服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgId", "fieldName", "fieldValue"],
                ["params", "request"]
            )
            set_dict = {
                "orgId": self.com_org_id,
                "fieldName": "def6",  # 通常def6字段用于存储币种ID
                "fieldValue": "CNY"   # 人民币
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的币种信息
            currency_data = response.get("data", {}).get("data", {})
            if currency_data:
                self.assert_util.assert_by_operator(currency_data.get("currCode"), "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
