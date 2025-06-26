import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织架构管理")
class TestOrgStructManagement(GenMdBaseTest):
    """组织架构管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.logger.info("组织架构管理测试类初始化完成")

    @case_decorator(
        story="组织架构管理",
        title="测试查询组织架构分页",
        description="验证组织架构分页查询功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织架构", "分页查询"]
    )
    def test_query_org_struct_page(self):
        """
        查询组织架构分页用例
        """
        try:
            # 调用分页查询接口
            api_path = self.get_api_path("ORG-组织架构-分页查询服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "orgDimensionCode"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "orgCode", "type": "TEXT"},
                    {"name": "orgName", "type": "TEXT"},
                    {"name": "orgStatus", "type": "SELECT"}
                ],
                "orgDimensionCode": "SCM_ORG_GRP"
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
        story="组织架构管理",
        title="测试查询组织架构详情",
        description="验证组织架构详情查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织架构", "详情查询"]
    )
    def test_query_org_struct_detail(self):
        """
        查询组织架构详情用例
        """
        try:
            # 先查询获取一个组织ID
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE org_status = 'ENABLED' 
                    AND org_dimension_code = 'SCM_ORG_GRP'
                    AND deleted = 0 
                ORDER BY org_sort DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            self.assert_util.assert_by_operator(result, "not_empty")
            org_id = result[0]["id"]

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-组织架构-查询组织单元详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": org_id}
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
        story="组织架构管理",
        title="测试构建组织架构树",
        description="验证组织架构树构建功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织架构", "树构建"]
    )
    def test_build_org_struct_tree(self):
        """
        构建组织架构树用例
        """
        try:
            # 调用构建组织树接口
            api_path = self.get_api_path("ORG-组织架构-根据维度构建一个组织树服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgDimensionCode"],
                ["params", "request"]
            )
            set_dict = {
                "orgDimensionCode": "SCM_ORG_GRP"
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
        story="组织架构管理",
        title="测试搜索组织架构",
        description="验证组织架构搜索功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织架构", "搜索"]
    )
    def test_search_org_struct(self):
        """
        搜索组织架构用例
        """
        try:
            # 调用搜索接口
            api_path = self.get_api_path("ORG-组织架构-新组织搜索服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgDimensionCode", "orgStatus", "searchText"],
                ["params", "request"]
            )
            set_dict = {
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT"],
                "searchText": ""
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
        story="组织架构管理",
        title="测试查询组织历史版本",
        description="验证组织历史版本查看功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织架构", "历史版本"]
    )
    def test_query_org_struct_history(self):
        """
        查询组织历史版本用例
        """
        try:
            # 先查询获取一个组织ID
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE org_status = 'ENABLED' 
                    AND org_dimension_code = 'SCM_ORG_GRP'
                    AND deleted = 0 
                ORDER BY org_sort DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            self.assert_util.assert_by_operator(result, "not_empty")
            org_id = result[0]["id"]

            # 调用历史版本查询接口
            api_path = self.get_api_path("ORG-组织架构-组织历史版本查看服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": org_id}
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
        story="组织架构管理",
        title="测试查询员工组织信息",
        description="验证查询指定组织和下级组织的员工信息功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["组织架构", "员工查询"]
    )
    def test_query_org_employee_info(self):
        """
        查询组织员工信息用例
        """
        try:
            # 先查询获取一个组织ID
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE org_status = 'ENABLED' 
                    AND org_dimension_code = 'SCM_ORG_GRP'
                    AND deleted = 0 
                ORDER BY org_sort DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            self.assert_util.assert_by_operator(result, "not_empty")
            org_id = result[0]["id"]

            # 调用查询员工信息接口
            api_path = self.get_api_path("ORG-组织-查询指定组织和下级组织的员工信息")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgId"],
                ["params", "request"]
            )
            set_dict = {"orgId": org_id}
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
        story="组织架构管理",
        title="测试启用组织单元",
        description="验证组织单元启用功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["组织架构", "启用"]
    )
    def test_enable_org_struct(self):
        """
        启用组织单元用例
        """
        try:
            # 先查询获取一个禁用状态的组织ID
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE deleted = 0 AND org_status = 'DISABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到禁用状态的组织数据，跳过启用测试")
                return
            
            org_id = result[0]["id"]

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织架构-启用组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": org_id}
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
        story="组织架构管理",
        title="测试停用组织单元",
        description="验证组织单元停用功能",
        severity="normal",
        order=8,
        smoke=True,
        tags=["组织架构", "停用"]
    )
    def test_disable_org_struct(self):
        """
        停用组织单元用例
        """
        try:
            # 先查询获取一个启用状态的组织ID（避免停用重要组织）
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE deleted = 0 AND org_status = 'ENABLED' 
                    AND org_code LIKE 'AT_%'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到测试组织数据，跳过停用测试")
                return
            
            org_id = result[0]["id"]

            # 调用停用接口
            api_path = self.get_api_path("ORG-组织架构-停用组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": org_id}
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
        story="组织架构管理",
        title="测试删除组织单元",
        description="验证组织单元删除功能",
        severity="normal",
        order=9,
        smoke=True,
        tags=["组织架构", "删除"]
    )
    def test_delete_org_struct(self):
        """
        删除组织单元用例
        """
        try:
            # 先查询获取一个测试组织ID（避免删除重要数据）
            sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE deleted = 0 AND org_code LIKE 'AT_%'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到测试组织数据，跳过删除测试")
                return
            
            org_id = result[0]["id"]

            # 调用删除接口
            api_path = self.get_api_path("ORG-组织架构-删除组织单元服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_id]}
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
        story="组织架构管理",
        title="测试获取组织导入模板",
        description="验证获取组织导入模板功能",
        severity="normal",
        order=10,
        smoke=False,
        tags=["组织架构", "导入模板"]
    )
    def test_get_org_import_template(self):
        """
        获取组织导入模板用例
        """
        try:
            # 调用获取导入模板接口
            api_path = self.get_api_path("ORG-组织架构-获取组织导入的模版服务")
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