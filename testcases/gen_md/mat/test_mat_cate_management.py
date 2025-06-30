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

    @case_decorator(
        story="物料类目管理",
        title="测试查询类目分页",
        description="验证类目分页查询功能",
        severity="normal",
        order=6,
        tags=["物料类目管理", "分页查询"]
    )
    def test_query_cate_page(self):
        """
        查询类目分页用例
        """
        try:
            api_path = self.get_api_path("GEN-类目配置-查询分页服务")
            params, url = self.get_api_params(api_path)

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
                    {"name": "matCateCode", "type": "TEXT"},
                    {"name": "matCateName", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类目管理",
        title="测试根据父类目查询下级类目",
        description="验证根据父类目查询下级类目服务",
        severity="normal",
        order=7,
        tags=["物料类目管理", "下级类目"]
    )
    def test_query_child_cate(self):
        """
        根据父类目查询下级类目用例
        """
        try:
            if not self.cateId:
                self.test_save_root_cate()

            api_path = self.get_api_path("GEN-类目配置-根据父类目查询下级类目服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["parentId"],
                ["params", "request"]
            )
            set_dict = {"parentId": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类目管理",
        title="测试查找类目树子数据",
        description="验证查找类目树子数据服务",
        severity="normal",
        order=8,
        tags=["物料类目管理", "树结构"]
    )
    def test_find_tree_child_cate(self):
        """
        查找类目树子数据用例
        """
        try:
            if not self.cateId:
                self.test_save_root_cate()

            api_path = self.get_api_path("类目配置-查找树子数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["parentId"],
                ["params", "request"]
            )
            set_dict = {"parentId": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料类目管理",
        title="测试根据ID查找类目数据",
        description="验证根据ID查找类目数据服务",
        severity="normal",
        order=9,
        tags=["物料类目管理", "ID查找"]
    )
    def test_find_cate_by_id(self):
        """
        根据ID查找类目数据用例
        """
        try:
            if not self.cateId:
                self.test_save_root_cate()

            api_path = self.get_api_path("类目配置-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="实际业务未调用")
    @case_decorator(
        story="物料类目管理",
        title="测试类目分页数据服务",
        description="验证类目分页数据服务",
        severity="normal",
        order=10,
        tags=["物料类目管理", "分页数据"]
    )
    def test_cate_paging_data(self):
        """
        类目分页数据服务用例
        """
        try:
            api_path = self.get_api_path("类目配置-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields","systemParams"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "matCateCode", "type": "TEXT"},
                    {"name": "matCateName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="物料类目管理",
        title="测试类目标准导入",
        description="验证类目标准导入功能",
        severity="normal",
        order=11,
        tags=["物料类目管理", "导入"]
    )
    def test_import_cate(self):
        """
        类目标准导入用例（需要文件上传）
        """
        # 这里应该调用: 类目配置标准导入服务
        pass

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类目管理",
        title="测试通过OSS提交类目导入任务",
        description="验证通过OSS提交类目导入任务功能",
        severity="normal",
        order=12,
        tags=["物料类目管理", "OSS导入"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交类目导入任务用例（需要OSS配置）
        """
        try:
            # 调用OSS导入任务接口
            api_path = self.get_api_path("类目配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ossPath", "fileName", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "ossPath": f"mat_cate_import_{self.mock_util.get_timestamp()}.xlsx",
                "fileName": f"类目导入_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "sheetName": "类目数据",
                    "startRow": 2,
                    "mapping": {
                        "matCateCode": "A",
                        "matCateName": "B",
                        "isLeaf": "C"
                    }
                }
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

    @case_decorator(
        story="物料类目管理",
        title="测试删除类目",
        description="验证删除类目功能",
        severity="normal",
        order=13,
        tags=["物料类目管理", "删除"]
    )
    def test_delete_cate(self):
        """
        删除类目用例
        """
        try:
            if not self.cateId:
                self.test_save_root_cate()

            api_path = self.get_api_path("GEN-类目配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.cateId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
