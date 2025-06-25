import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织关联管理")
class TestOrg_RelationManagement(GenMdBaseTest):
    """组织关联管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.org_relation_id = None
        cls.org_relation_code = None
        cls.logger.info("组织关联管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织关联管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_org_relation_md",
                where="org_relation_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织关联管理",
        title="测试新增组织关联管理",
        description="验证新增组织关联管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织关联管理", "新增"]
    )
    def test_save_org_relation(self):
        """
        新增组织关联管理用例
        """
        try:
            # 准备组织关联管理数据
            org_relation_code = self.mock_data.generate_unique_code(tag="Org_Relation")
            org_relation_name = f"组织关联管理_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-组织关联-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["org_relation_code", "org_relation_name"],
                ["params", "request"]
            )
            set_dict = {
                "org_relation_code": org_relation_code,
                "org_relation_name": org_relation_name
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            org_relation_id = response.get("data", {}).get("data", {})

            # 保存组织关联管理信息供后续用例使用
            self.org_relation_id = org_relation_id
            self.org_relation_code = org_relation_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试查询组织关联管理列表",
        description="验证组织关联管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织关联管理", "查询"]
    )
    def test_query_org_relation_list(self):
        """
        查询组织关联管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-组织关联-查询分页服务")
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
                    "needTotal": True
                },
                "fields": [
                    {"name": "org_relation_code", "type": "TEXT"},
                    {"name": "org_relation_name", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试查询组织关联管理详情",
        description="验证组织关联管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织关联管理", "查询"]
    )
    def test_query_org_relation_detail(self):
        """
        查询组织关联管理详情用例
        """
        try:
            # 获取组织关联管理ID
            if not self.org_relation_id:
                self.test_save_org_relation()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-组织关联-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_relation_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise



    @case_decorator(
        story="组织关联管理",
        title="测试删除组织关联管理",
        description="验证删除组织关联管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织关联管理", "删除"]
    )
    def test_delete_org_relation(self):
        """
        删除组织关联管理用例
        """
        try:
            # 获取组织关联管理信息
            if not self.org_relation_id:
                self.test_save_org_relation()

            # 调用删除接口
            api_path = self.get_api_path("ORG-组织-删除员工组织关联关系服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [self.org_relation_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
