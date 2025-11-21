import allure
import pytest
from pathlib import Path
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织身份管理")
class TestIdentityManagement(GenMdBaseTest):
    """组织身份管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.identity_id = None
        cls.user_id = cls.md_cache_data.get("user_info",{}).get("id",None)
        cls.created_at = cls.mock_util.get_mock_date(include_time=True)
        
        
    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织身份管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_identity_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

   
    @pytest.mark.dependency(name="test_enable_identity")
    @case_decorator(
        story="组织身份管理",
        title="测试启用组织身份",
        description="验证启用组织身份功能",
        severity="normal",
        file_level_order=1,
        smoke=True,
        tags=["组织身份", "启用"]
    )
    def test_enable_identity(self):
        """
        启用组织身份用例
        """
        try:
            # 创建组织身份数据
            identity_code = self.mock_util.generate_unique_code(tag="Org_Identity")
            identity_name = f"测试组织身份(自动化)_{self.mock_util.get_timestamp()}"
            
            # 使用正确的insert方法
            data = {
                "code": identity_code,
                "name": identity_name,
                "status": None,
                "created_by": None,
                "updated_by": self.user_id,
                "created_at": self.created_at,
                "updated_at": self.created_at,
                "version": 0,
                "deleted": 0,
                "origin_org_id": 0
            }
            org_identity_id = self.db.insert("org_identity_cf", data)
            self.logger.info(f"创建组织身份成功，ID: {org_identity_id}")

            # 调用启用接口
            api_path = self.get_api_path("ORG-组织身份-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": org_identity_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            TestIdentityManagement.identity_id = org_identity_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.dependency(depends=["test_enable_identity"])
    @case_decorator(
        story="组织身份管理",
        title="测试禁用组织身份",
        description="验证禁用组织身份功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["组织身份", "禁用"]
    )
    def test_disable_identity(self):
        """
        禁用组织身份用例
        """
        try:
            # 确保先执行启用测试
            if not TestIdentityManagement.identity_id:
                self.test_enable_identity()
            
            # 调用禁用接口
            api_path = self.get_api_path("ORG-组织身份-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": TestIdentityManagement.identity_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

