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
        title="测试保存组织切换",
        description="验证保存组织切换功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织切换管理", "保存切换"]
    )
    def test_save_org_switch_instance(self):
        """
        保存组织切换用例
        """
        try:
            # 获取组织切换模型信息
            if not self.org_switch_id:
                self.test_save_org_switch()

            # 调用保存组织切换接口
            api_path = self.get_api_path("ORG-多组织-保存组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["org_switch_model_id", "org_switch_name"],
                ["params", "request"]
            )
            set_dict = {
                "org_switch_model_id": self.org_switch_id,
                "org_switch_name": f"组织切换实例_{self.mock_data.get_timestamp()}"
            }
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
        story="组织切换管理",
        title="测试启用组织切换",
        description="验证启用组织切换功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织切换管理", "启用"]
    )
    def test_enable_org_switch(self):
        """
        启用组织切换用例
        """
        try:
            # 先查询获取一个禁用状态的组织切换ID
            sql = """
                SELECT id, org_switch_code, org_switch_name 
                FROM org_switch_cf 
                WHERE deleted = 0 AND status = 'DISABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到禁用状态的组织切换数据，跳过启用测试")
                return
            
            switch_id = result[0]["id"]

            # 调用启用接口
            api_path = self.get_api_path("ORG-多组织-启用组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [switch_id]}
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
        story="组织切换管理",
        title="测试停用组织切换",
        description="验证停用组织切换功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织切换管理", "停用"]
    )
    def test_disable_org_switch(self):
        """
        停用组织切换用例
        """
        try:
            # 先查询获取一个启用状态的组织切换ID
            sql = """
                SELECT id, org_switch_code, org_switch_name 
                FROM org_switch_cf 
                WHERE deleted = 0 AND status = 'ENABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到启用状态的组织切换数据，跳过停用测试")
                return
            
            switch_id = result[0]["id"]

            # 调用停用接口
            api_path = self.get_api_path("ORG-多组织-停用组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [switch_id]}
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
        story="组织切换管理",
        title="测试分页查询组织切换",
        description="验证分页查询组织切换功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["组织切换管理", "分页查询"]
    )
    def test_query_org_switch_page(self):
        """
        分页查询组织切换用例
        """
        try:
            # 调用分页查询接口
            api_path = self.get_api_path("ORG-多组织-分页查询组织切换服务")
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
                    {"name": "org_switch_code", "type": "TEXT"},
                    {"name": "org_switch_name", "type": "TEXT"}
                ]
            }
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
        story="组织切换管理",
        title="测试查询组织切换详情",
        description="验证查询组织切换详情功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["组织切换管理", "详情查询"]
    )
    def test_query_org_switch_detail(self):
        """
        查询组织切换详情用例
        """
        try:
            # 先查询获取一个组织切换ID
            sql = """
                SELECT id, org_switch_code, org_switch_name 
                FROM org_switch_cf 
                WHERE deleted = 0
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到组织切换数据，跳过详情查询测试")
                return
            
            switch_id = result[0]["id"]

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-多组织-查询组织切换详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": switch_id}
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
        story="组织切换管理",
        title="测试查询用户所在的公司",
        description="验证查询用户所在的公司功能",
        severity="normal",
        order=8,
        smoke=True,
        tags=["组织切换管理", "用户公司查询"]
    )
    def test_query_user_company(self):
        """
        查询用户所在的公司用例
        """
        try:
            # 调用查询用户所在公司接口
            api_path = self.get_api_path("ORG-多组织-查询用户所在的公司服务")
            params, url = self.get_api_params(api_path)

            # 这个接口可能不需要参数或参数很少
            self.logger.info(f"请求参数: {params}")

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试删除组织切换管理",
        description="验证删除组织切换管理功能",
        severity="normal",
        order=9,
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
