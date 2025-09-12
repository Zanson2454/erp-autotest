import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织类型管理")
class TestOrg_TypeManagement(GenMdBaseTest):
    """组织类型管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.org_type_id = None
        cls.org_type_code = None
     
        cls.logger.info("组织类型管理测试类初始化完成")
        if cls.md_cache_data:
            org_attr_list = cls.md_cache_data["org_info"]["org_attr_cf"]
            cls.org_attr_id = cls.mock_util.get_mock_choice(org_attr_list)["id"]
            cls.logger.info(f"org_attr_id: {cls.org_attr_id}")

        
    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织类型管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_business_type_cf",
                where="code like %s",
                params=["AT_OrgType%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织类型管理",
        title="测试新增组织类型管理",
        description="验证新增组织类型管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织类型管理", "新增"]
    )
    def test_save_org_type(self):
        """
        新增组织类型管理用例
        """
        try:
            # 准备组织类型管理数据
            org_type_code = self.mock_util.generate_unique_code(tag="OrgType")
            org_type_name = f"组织类型管理_{self.mock_util.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-组织类型-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["org_type_code", "org_type_name","attrList"],
                ["params", "request"]
            )
            set_dict = {
                "code": org_type_code,
                "name": org_type_name,
                "attrList": [
                    {
                        "attrId": {
                            "id": self.org_attr_id
                        },
                        "attrIsMulti": True,
                        "attrIsRequired": False,
                        "attrSort": 1,
                        "attrValue": "测试组织类型"
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            self.org_type_id = response.get("data", {}).get("data", {}).get("id", None)


            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试查询组织类型管理列表",
        description="验证组织类型管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织类型管理", "查询"]
    )
    def test_query_org_type_list(self):
        """
        查询组织类型管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-组织类型-查询分页服务")
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
                    {"name": "org_type_code", "type": "TEXT"},
                    {"name": "org_type_name", "type": "TEXT"}
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
        story="组织类型管理",
        title="测试查询组织类型管理详情",
        description="验证组织类型管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织类型管理", "查询"]
    )
    def test_query_org_type_detail(self):
        """
        查询组织类型管理详情用例
        """
        try:
            # 获取组织类型管理ID
            if not self.org_type_id:
                self.test_save_org_type()

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-组织类型-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_type_id}
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
        story="组织类型管理",
        title="测试启用组织类型管理",
        description="验证启用组织类型管理功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织类型管理", "启用"]
    )
    def test_enabled_org_type(self):
        """
        启用组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self.test_save_org_type()

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织类型-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            sql = f"select status from org_business_type_cf where id ={self.org_type_id}"
            if self.db.query(sql):
                status = self.db.query(sql)[0]["status"]
                self.assert_util.assert_by_operator(status, "=", "ENABLED")
            else:
                self.logger.info("组织类型管理信息不存在")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试禁用组织类型管理",
        description="验证禁用组织类型管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织类型管理", "禁用"]
    )
    def test_disabled_org_type(self):
        """
        禁用组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self.test_enabled_org_type()

            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织类型-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            sql = f"select status from org_business_type_cf where id ={self.org_type_id}"
            self.logger.info(f"data: {self.db.query(sql)}")
            if self.db.query(sql):
                status = self.db.query(sql)[0]["status"]
                self.assert_util.assert_by_operator(status, "=", "DISABLED")
            else:
                self.logger.info("组织类型管理信息不存在")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试查询组织架构类型列表",
        description="验证组织架构类型列表查询功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["组织类型管理", "架构查询"]
    )
    def test_query_org_structure_type_list(self):
        """
        查询组织架构类型列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("ORG-组织架构-查询组织类型列表服务")
            params, url = self.get_api_params(api_path)

            # 设置参数
            params["params"] = {
                "request": {
                    "orgDimensionCode": "SCM_ORG_GRP"
                }
            }
            self.logger.info(f"请求参数: {params}")

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response, "组织类型列表为空")

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理", 
        title="测试查询组织业务类型分页",
        description="验证组织业务类型分页查询功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["组织类型管理", "业务类型查询"]
    )
    def test_query_org_business_type_paging(self):
        """
        查询组织业务类型分页用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-组织类型-查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 设置参数
            params["params"]["request"] = {
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
                    {"name": "status", "type": "SELECT"}
                ],
                "systemParams": None
            }
            self.logger.info(f"请求参数: {params}")

            # 发送请求，添加查询参数
            response = self.http.post(url, params={"tmodule": "GEN_MD"}, json=params)
            self.assert_util.assert_response_data(response, "组织业务类型列表不为空")

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试删除组织类型管理",
        description="验证删除组织类型管理功能",
        severity="normal",
        order=8,
        smoke=True,
        tags=["组织类型管理", "删除"]
    )
    def test_delete_org_type(self):
        """
        删除组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self.test_save_org_type()

            # 调用删除接口
            api_path = self.get_api_path("ORG-组织类型-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_type_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            sql = f"select deleted from org_business_type_cf where id ={self.org_type_id}"
            deleted = self.db.query(sql)[0]["deleted"]
            self.assert_util.assert_by_operator(deleted, "!=", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
