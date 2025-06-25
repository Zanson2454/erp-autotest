import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织切换管理")
class TestOrg_SwitchManagement(GenMdBaseTest):
    """组织切换管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.org_switch_id = None
        cls.org_switch_code = None
        cls.logger.info("组织切换管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织切换管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_org_switch_md",
                where="org_switch_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织切换管理",
        title="测试新增组织切换管理",
        description="验证新增组织切换管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织切换管理", "新增"]
    )
    def test_save_org_switch(self):
        """
        新增组织切换管理用例
        """
        try:
            # 准备组织切换管理数据
            org_switch_code = self.mock_data.generate_unique_code(tag="Org_Switch")
            org_switch_name = f"组织切换管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-多组织-保存组织切换模型服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["org_switch_code", "org_switch_name"],
                ["params", "request"]
            )
            set_dict = {
                "org_switch_code": org_switch_code,
                "org_switch_name": org_switch_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            org_switch_id = response.get("data", {}).get("data", {})

            # 保存组织切换管理信息供后续用例使用
            self.org_switch_id = org_switch_id
            self.org_switch_code = org_switch_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise







    @case_decorator(
        story="组织切换管理",
        title="测试删除组织切换管理",
        description="验证删除组织切换管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织切换管理", "删除"]
    )
    def test_delete_org_switch(self):
        """
        删除组织切换管理用例
        """
        try:
            # 获取组织切换管理信息
            if not self.org_switch_id:
                self.test_save_org_switch()

            # 调用删除接口
            api_path = self.get_api_path("ORG-多组织-删除组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.org_switch_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
