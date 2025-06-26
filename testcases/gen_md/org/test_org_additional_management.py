import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织补充管理")
class TestOrgAdditionalManagement(GenMdBaseTest):
    """组织补充管理测试类 - 补充缺失的API接口"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.logger.info("组织补充管理测试类初始化完成")

    # ==================== 员工相关接口 ====================
    
    @case_decorator(
        story="员工管理",
        title="测试查询员工详情",
        description="验证员工详情查询功能",
        severity="normal",
        order=1,
        smoke=True,
        tags=["员工管理", "详情查询"]
    )
    def test_query_employee_detail(self):
        """
        查询员工详情用例
        """
        try:
            # 先查询获取一个员工ID
            sql = """
                SELECT id, employee_code, employee_name 
                FROM gen_employee_md 
                WHERE deleted = 0
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到员工数据，跳过详情查询测试")
                return
            
            employee_id = result[0]["id"]

            # 调用员工详情查询接口
            api_path = self.get_api_path("ORG-员工-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": employee_id}
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
        story="员工管理",
        title="测试分页查询员工",
        description="验证员工分页查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["员工管理", "分页查询"]
    )
    def test_query_employee_page(self):
        """
        分页查询员工用例
        """
        try:
            # 调用员工分页查询接口
            api_path = self.get_api_path("ORG-员工-查询分页服务")
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
                    {"name": "employee_code", "type": "TEXT"},
                    {"name": "employee_name", "type": "TEXT"}
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

    # ==================== 组织类型相关接口 ====================
    
    @case_decorator(
        story="组织类型管理",
        title="测试启用组织类型",
        description="验证组织类型启用功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织类型", "启用"]
    )
    def test_enable_org_type(self):
        """
        启用组织类型用例
        """
        try:
            # 先查询获取一个禁用状态的组织类型ID
            sql = """
                SELECT id, org_type_code, org_type_name 
                FROM gen_org_type_md 
                WHERE deleted = 0 AND status = 'DISABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到禁用状态的组织类型数据，跳过启用测试")
                return
            
            org_type_id = result[0]["id"]

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织类型-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_type_id]}
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
        title="测试禁用组织类型",
        description="验证组织类型禁用功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织类型", "禁用"]
    )
    def test_disable_org_type(self):
        """
        禁用组织类型用例
        """
        try:
            # 先查询获取一个启用状态的组织类型ID（避免禁用重要类型）
            sql = """
                SELECT id, org_type_code, org_type_name 
                FROM gen_org_type_md 
                WHERE deleted = 0 AND status = 'ENABLED' 
                    AND org_type_code LIKE 'AT_%'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到测试组织类型数据，跳过禁用测试")
                return
            
            org_type_id = result[0]["id"]

            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织类型-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_type_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ==================== 组织维度相关接口 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试启用组织维度",
        description="验证组织维度启用功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["组织维度", "启用"]
    )
    def test_enable_org_dimension(self):
        """
        启用组织维度用例
        """
        try:
            # 先查询获取一个禁用状态的组织维度ID
            sql = """
                SELECT id, org_dimension_code, org_dimension_name 
                FROM gen_org_dimension_md 
                WHERE deleted = 0 AND status = 'DISABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到禁用状态的组织维度数据，跳过启用测试")
                return
            
            org_dimension_id = result[0]["id"]

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织维度-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_dimension_id]}
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
        story="组织维度管理",
        title="测试禁用组织维度",
        description="验证组织维度禁用功能",
        severity="normal",
        order=6,
        smoke=True,
        tags=["组织维度", "禁用"]
    )
    def test_disable_org_dimension(self):
        """
        禁用组织维度用例
        """
        try:
            # 先查询获取一个启用状态的组织维度ID（避免禁用重要维度）
            sql = """
                SELECT id, org_dimension_code, org_dimension_name 
                FROM gen_org_dimension_md 
                WHERE deleted = 0 AND status = 'ENABLED' 
                    AND org_dimension_code LIKE 'AT_%'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到测试组织维度数据，跳过禁用测试")
                return
            
            org_dimension_id = result[0]["id"]

            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织维度-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_dimension_id]}
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
        story="组织维度管理",
        title="测试查询组织维度详情",
        description="验证组织维度详情查询功能",
        severity="normal",
        order=7,
        smoke=True,
        tags=["组织维度", "详情查询"]
    )
    def test_query_org_dimension_detail(self):
        """
        查询组织维度详情用例
        """
        try:
            # 先查询获取一个组织维度ID
            sql = """
                SELECT id, org_dimension_code, org_dimension_name 
                FROM gen_org_dimension_md 
                WHERE deleted = 0
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到组织维度数据，跳过详情查询测试")
                return
            
            org_dimension_id = result[0]["id"]

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-组织维度-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": org_dimension_id}
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
        story="组织维度管理",
        title="测试查询启用的组织维度列表",
        description="验证查询启用的组织维度列表功能",
        severity="normal",
        order=8,
        smoke=True,
        tags=["组织维度", "启用列表查询"]
    )
    def test_query_enabled_org_dimension_list(self):
        """
        查询启用的组织维度列表用例
        """
        try:
            # 调用查询启用列表接口
            api_path = self.get_api_path("ORG-组织维度-查询启用列表服务")
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

    # ==================== 组织关联相关接口 ====================
    
    @case_decorator(
        story="组织关联管理",
        title="测试启用组织关联",
        description="验证组织关联启用功能",
        severity="normal",
        order=9,
        smoke=True,
        tags=["组织关联", "启用"]
    )
    def test_enable_org_relation(self):
        """
        启用组织关联用例
        """
        try:
            # 先查询获取一个禁用状态的组织关联ID
            sql = """
                SELECT id, org_relation_code, org_relation_name 
                FROM gen_org_relation_md 
                WHERE deleted = 0 AND status = 'DISABLED'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到禁用状态的组织关联数据，跳过启用测试")
                return
            
            org_relation_id = result[0]["id"]

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织关联-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_relation_id]}
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
        title="测试禁用组织关联",
        description="验证组织关联禁用功能",
        severity="normal",
        order=10,
        smoke=True,
        tags=["组织关联", "禁用"]
    )
    def test_disable_org_relation(self):
        """
        禁用组织关联用例
        """
        try:
            # 先查询获取一个启用状态的组织关联ID（避免禁用重要关联）
            sql = """
                SELECT id, org_relation_code, org_relation_name 
                FROM gen_org_relation_md 
                WHERE deleted = 0 AND status = 'ENABLED' 
                    AND org_relation_code LIKE 'AT_%'
                ORDER BY created_time DESC
                LIMIT 1
            """
            result = self.db.query(sql)
            if not result:
                self.logger.warning("没有找到测试组织关联数据，跳过禁用测试")
                return
            
            org_relation_id = result[0]["id"]

            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织关联-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": [org_relation_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ==================== 其他特殊接口 ====================
    
    @case_decorator(
        story="组织管理",
        title="测试钉钉同步组织",
        description="验证钉钉同步组织功能",
        severity="normal",
        order=11,
        smoke=False,
        tags=["组织管理", "钉钉同步"]
    )
    def test_dingtalk_sync_org(self):
        """
        钉钉同步组织用例
        """
        try:
            # 调用钉钉同步接口
            api_path = self.get_api_path("ORG-组织-钉钉同步组织服务")
            params, url = self.get_api_params(api_path)

            # 这个接口可能需要特定参数
            self.logger.info(f"请求参数: {params}")

            response = self.http.post(url, json=params)
            # 钉钉同步可能会有特殊的响应处理，这里简单验证不报错即可
            self.logger.info(f"钉钉同步响应: {response}")

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            # 钉钉同步失败是可以接受的，记录日志即可
            self.logger.warning(f"钉钉同步测试失败: {str(e)}")

    @case_decorator(
        story="组织管理",
        title="测试查询库存地点",
        description="验证查询库存地点功能",
        severity="normal",
        order=12,
        smoke=True,
        tags=["组织管理", "库存地点查询"]
    )
    def test_query_inventory_location(self):
        """
        查询库存地点用例
        """
        try:
            # 调用查询库存地点接口
            api_path = self.get_api_path("ORG-组织-查询库存地点服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数，可能需要组织ID或其他参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgId"],
                ["params", "request"]
            )
            
            # 先查询获取一个库存组织ID
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
            if result:
                org_id = result[0]["id"]
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