import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("物料类目管理")
class TestMatCateManagement(GenMdBaseTest):
    """物料类目管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.logger.info("物料类目管理测试类初始化完成")
        cls.cateId = None

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的类目数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_mat_cate_md",
                where="mat_cate_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
            
    @case_decorator(
        story="物料类目管理",
        title="测试新增根类目",
        description="验证新增根类目功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["物料类目管理", "新增"]
    )
    def test_save_root_cate(self):
        """
        新增根类目用例
        """
        try:
            # 准备类目数据
            cate_code = self.mock_data.generate_unique_code(tag="Cate")
            cate_name = f"类目_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-类目配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["matCateCode", "matCateName", "isLeaf", "qualificationsGroupId", 
                 "isLimitPoQualifications", "isLimitSoQualifications", "path", "matCateParent"],
                ["params", "request"]
            )
            set_dict = {
                "matCateCode": cate_code,
                "matCateName": cate_name,
                "isLeaf": False,
                "qualificationsGroupId": None,
                "isLimitPoQualifications": False,
                "isLimitSoQualifications": False,
                "path": None,
                "matCateParent": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            cate_id = response.get("data", {}).get("data", {})

            # 保存类目信息供后续用例使用
            self.cateId = cate_id

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="物料类目管理",
        title="测试查询类目详情",
        description="验证类目详情查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["物料类目管理", "查询"]
    )
    def test_query_cate_detail(self):
        """
        查询类目详情用例
        """
        try:
            if not self.cateId:
                self.test_save_root_cate()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-类目配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的类目信息
            status = response.get("data", {}).get("data", {}).get("status")
            
            self.assert_util.assert_by_operator(status,"=","ENABLED")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="物料类目管理",
        title="测试新增子类目",
        description="验证新增子类目功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["物料类目管理", "新增"]
    )
    def test_save_sub_cate(self):
        """
        新增子类目用例
        """
        try:
            # 获取父类目ID
            if not self.cateId:
                self.test_save_root_cate()

            # 准备子类目数据
            sub_cate_code = self.mock_data.generate_unique_code(tag="CateSub")
            sub_cate_name = f"子类目_{self.mock_data.get_timestamp()}"

            # 调用保存接口
            api_path = self.get_api_path("GEN-类目配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["matCateCode", "matCateName", "isLeaf", "qualificationsGroupId", 
                 "isLimitPoQualifications", "isLimitSoQualifications", "path", "matCateParent"],
                ["params", "request"]
            )
            set_dict = {
                "matCateCode": sub_cate_code,
                "matCateName": sub_cate_name,
                "isLeaf": False,
                "qualificationsGroupId": None,
                "isLimitPoQualifications": False,
                "isLimitSoQualifications": False,
                "path": None,
                "matCateParent": {"id": self.cateId}
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
        story="物料类目管理",
        title="测试启用类目",
        description="验证类目启用功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["物料类目管理", "启用"]
    )
    def test_enable_cate(self):
        """
        启用类目用例
        """
        try:
            # 获取类目ID
            if not self.cateId:
                self.test_save_root_cate()

            # 调用启用接口
            api_path = self.get_api_path("GEN-类目配置-启用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="物料类目管理",
        title="测试禁用类目",
        description="验证类目禁用功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["物料类目管理", "禁用"]
    )
    def test_disable_cate(self):
        """
        禁用类目用例
        """
        try:
            # 获取类目ID
            if not self.cateId:
                self.test_save_root_cate()

            # 调用禁用接口
            api_path = self.get_api_path("GEN-类目配置-禁用服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
