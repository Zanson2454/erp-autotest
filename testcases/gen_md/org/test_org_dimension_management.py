import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织维度管理")
class TestOrg_DimensionManagement(GenMdBaseTest):
    """组织维度管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        
         # 准备组织维度管理数据
        cls.org_dimension_id = None
        cls.org_dimension_code = None
        cls.org_dimension_name = None
        
         # 获取md_cache_data中的第一个数据
        cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
   
        # 初始化组织类型数据
        for org_biz_type in  cls.orgBusinessTypeIds:
            if org_biz_type["code"] == "COM_ORG":
                cls.comOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "PUR_ORG":
                cls.purOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_ORG":
                cls.slsOrgTypeId  = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_DC":
                cls.slsDcTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_ORG":
                cls.invOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_LOC":
                cls.invLocTypeId = org_biz_type["id"]

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织维度管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_dimension_cf",
                where="org_dimension_code like %s",
                params=["AT_Org_Dimension%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织维度管理",
        title="测试新增组织维度管理",
        description="验证新增组织维度管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织维度管理", "新增"]
    )
    def test_save_org_dimension(self):
        """
        新增组织维度管理用例
        """
        try:
            

            # 调用保存接口
            api_path = self.get_api_path("ORG-组织维度-保存服务")
            params, url = self.get_api_params(api_path)

            self.org_dimension_code = self.mock_util.generate_unique_code(tag="Org_Dimension")
            self.org_dimension_name = f"组织维度(自动化)_{self.mock_util.get_timestamp()}"


            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgDimensionCode","orgDimensionName","orgDimensionDescribe","isSupMultiRoot","orgBusinessTypeList"],
                ["params", "request"]
            )
            set_dict = {
                "orgDimensionCode": self.org_dimension_code,
                "orgDimensionName": self.org_dimension_name,
                "orgDimensionDescribe": f"测试组织维度-{self.mock_util.get_timestamp()}",
                "isSupMultiRoot": True,
                "orgBusinessTypeList": [
                    {"orgBusinessTypeId": {"id": self.slsOrgTypeId}},
                    {"orgBusinessTypeId": {"id": self.purOrgTypeId}},
                    {"orgBusinessTypeId": {"id": self.invOrgTypeId}},
                    {"orgBusinessTypeId": {"id": self.invLocTypeId}}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            self.org_dimension_id = response.get("data", {}).get("data", {})
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试查询组织维度管理详情",
        description="验证组织维度管理详情查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织维度管理", "查询详情"]
    )
    def test_query_org_dimension_detail(self):
        """
        查询组织维度管理详情用例
        """
        try:
            # 获取组织维度管理信息
            if not self.org_dimension_id:
                self.test_save_org_dimension()

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-组织维度-详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_dimension_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            status = response.get("data", {}).get("data", {}).get("status", None)
            self.assert_util.assert_by_operator(status, "=", "INACTIVE")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise



    @case_decorator(
        story="组织维度管理",
        title="测试查询组织维度管理列表",
        description="验证组织维度管理列表查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织维度管理", "查询"]
    )
    def test_query_org_dimension_list(self):
        """
        查询组织维度管理列表用例
        """
        try:
            if not self.org_dimension_code:
                self.test_save_org_dimension()
                
            # 调用查询接口
            api_path = self.get_api_path("ORG-组织维度-查询分页服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            set_dict =  {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": {
                    "type": "ConditionItems",
                    "conditions": {
                        "orgDimensionCode": {
                            "operator": "CONTAINS",
                            "value": self.org_dimension_code
                        }
                    },
                    "logicOperator": "AND"
                }
            },
            "fields": [
                {
                    "name": "orgDimensionCode",
                    "type": "TEXT"
                },
                {
                    "name": "orgDimensionName",
                    "type": "TEXT"
                }
            ],
            "systemParams": None
        }

            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            total = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total, "=", 1)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
    @case_decorator(
        story="组织维度管理",
        title="测试启用组织维度管理",
        description="验证启用组织维度管理功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织维度管理", "启用"]
    )
    def test_enabled_org_dimension(self):
        """
        启用组织维度管理用例
        """
        try:
            # 获取组织维度管理信息
            if not self.org_dimension_id:
                self.test_save_org_dimension()

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织维度-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_dimension_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            sql = f"select status from org_dimension_cf where id ={self.org_dimension_id}"
            status = self.db.query(sql)[0]["status"]
            self.assert_util.assert_by_operator(status, "=", "ENABLED")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试禁用组织维度管理",
        description="验证禁用组织维度管理功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织维度管理", "禁用"]
    )
    def test_disabled_org_dimension(self):
        """
        禁用组织维度管理用例
        """
        try:
            # 获取组织维度管理信息
            if not self.org_dimension_id:
                self.test_enabled_org_dimension()

            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织维度-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_dimension_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            sql = f"select status from org_dimension_cf where id ={self.org_dimension_id}"
            status = self.db.query(sql)[0]["status"]
            self.assert_util.assert_by_operator(status, "=", "DISABLED")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试查询启用的组织维度列表",
        description="验证查询启用的组织维度列表功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["组织维度管理", "查询启用列表"]
    )
    def test_query_enabled_org_dimension_list(self):
        """
        查询启用的组织维度列表用例
        """
        try:
            # 确保有启用的组织维度数据
            if not self.org_dimension_id:
                self.test_save_org_dimension()
                self.test_enabled_org_dimension()

            # 调用查询启用列表接口
            api_path = self.get_api_path("ORG-组织维度-查询启用的组织维度列表服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                [],
                ["params", "request"]
            )
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试删除组织维度管理",
        description="验证删除组织维度管理功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["组织维度管理", "删除"]
    )
    def test_delete_org_dimension(self):
        """
        删除组织维度管理用例
        """
        try:
            # 获取组织维度管理信息
            if not self.org_dimension_id:
                self.test_save_org_dimension()

            # 调用删除接口
            api_path = self.get_api_path("ORG-组织维度-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_dimension_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            sql = f"select deleted from org_dimension_cf where id ={self.org_dimension_id}"
            deleted = self.db.query(sql)[0]["deleted"]
            self.assert_util.assert_by_operator(deleted, "!=", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
