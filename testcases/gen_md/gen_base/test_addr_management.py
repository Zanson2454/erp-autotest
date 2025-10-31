import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("地址库管理")
class TestAddrManagement(GenMdBaseTest):
    """地址库管理测试类 - 覆盖所有地址库相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.addr_id = None
        cls.addr_code = None
        cls.parent_addr_id = None
        cls.logger.info("地址库管理测试类初始化完成")
        if cls.init_data:
            cls.coun_id = cls.init_data.get("country_info",[])[0].get("coun_id")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_addr_type_cf",
                where="addr_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 地址库基础管理 ================
    @case_decorator(
        story="地址库管理",
        title="测试新增地址库",
        description="验证GEN-地址库-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["地址库", "新增", "GEN_ADDR_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_addr(self):
        """新增地址库用例 - GEN_ADDR_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            addr_code = self.mock_util.generate_unique_code(tag="ADDR")
            addr_name = f"测试地址_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-地址库-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["addrCode", "addrName", "addrNameEn", "addrType", "addrParentId", "postCode", "lat", "lng", "counId"], ["params", "request"]
            )
            set_dict = {
                "addrCode": addr_code,
                "addrName": addr_name,
                "addrParentId": None,
                "counId":{"id":self.coun_id},
                "postCode": self.mock_util.get_mock_postcode(),  # 顶级地址无父级
                "lat": self.mock_util.get_mock_coordinates()["latitude"],
                "lng": self.mock_util.get_mock_coordinates()["longitude"]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.addr_id = response.get("data", {}).get("data", {})
            self.addr_code = addr_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址库管理",
        title="测试新增下级地址库",
        description="验证GEN-地址库-保存服务功能(创建下级地址)",
        severity="normal",
        file_level_order=2,
        tags=["地址库", "新增", "下级地址", "GEN_ADDR_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_child_addr(self):
        """新增下级地址库用例 - GEN_ADDR_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            if not self.addr_id:
                self.test_save_addr()

            child_addr_code = self.mock_util.generate_unique_code(tag="CITY")
            child_addr_name = f"测试城市_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-地址库-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["addrCode", "addrName", "addrNameEn", "addrType", "addrParentId", "postCode", "lat", "lng"], ["params", "request"]
            )
            set_dict = {
                "addrCode": child_addr_code,
                "addrName": child_addr_name,
                "addrParentId": self.addr_id,
                "counId":{"id":self.coun_id},
                "postCode": self.mock_util.get_mock_postcode(),  # 顶级地址无父级
                "lat": self.mock_util.get_mock_coordinates()["latitude"],
                "lng": self.mock_util.get_mock_coordinates()["longitude"]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.parent_addr_id = self.addr_id  # 保存父级ID用于后续测试

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址库管理",
        title="测试查询地址库分页列表",
        description="验证GEN-地址库-查询分页服务功能",
        severity="normal",
        file_level_order=4,
        tags=["地址库", "查询", "GEN_ADDR_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_addr_page(self):
        """查询地址库分页列表用例 - GEN_ADDR_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-地址库-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "nameEn", "type": "TEXT"},
                    {"name": "addressType", "type": "TEXT"},
                    {"name": "level", "type": "NUMBER"}
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
        story="地址库管理",
        title="测试地址库分页数据服务",
        description="验证地址库-分页数据服务功能",
        severity="normal",
        file_level_order=5,
        tags=["地址库", "分页数据", "GEN_ADDR_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    @pytest.mark.skip(reason="地址库分页数据服务接口未开发")
    def test_addr_paging_data(self):
        """地址库分页数据服务用例 - GEN_ADDR_TYPE_CF_PAGING_DATA_SERVICE"""
        try:
            api_path = self.get_api_path("地址库-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
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
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "nameEn", "type": "TEXT"},
                    {"name": "addressType", "type": "TEXT"},
                    {"name": "level", "type": "NUMBER"}
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

    @case_decorator(
        story="地址库管理",
        title="测试根据父级ID查询下级地址列表",
        description="验证GEN-地址库-根据父级ID查询下级列表服务功能",
        severity="normal",
        file_level_order=6,
        tags=["地址库", "层级查询", "GEN_ADDR_TYPE_CF_QUERY_BY_PARENT_ACTION_SERVICE"]
    )
    def test_query_addr_by_parent(self):
        """根据父级ID查询下级地址列表用例 - GEN_ADDR_TYPE_CF_QUERY_BY_PARENT_ACTION_SERVICE"""
        try:
            if not self.parent_addr_id:
                self.test_save_child_addr()

            api_path = self.get_api_path("GEN-地址库-根据父级ID查询下级列表服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["parentId"], ["params", "request"]
            )
            set_dict = {"parentId": self.parent_addr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的下级列表数据
            child_list = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(len(child_list), ">=", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址库管理",
        title="测试查询地址库详情",
        description="验证GEN-地址库-查询详情服务功能",
        severity="normal",
        file_level_order=7,
        tags=["地址库", "查询", "GEN_ADDR_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_addr_detail(self):
        """查询地址库详情用例 - GEN_ADDR_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.addr_id:
                self.test_save_addr()

            api_path = self.get_api_path("GEN-地址库-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.addr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址库管理",
        title="测试删除地址库",
        description="验证GEN-地址库-删除服务功能",
        severity="critical",
        file_level_order=8,
        tags=["地址库", "删除", "GEN_ADDR_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_addr(self):
        """删除地址库用例 - GEN_ADDR_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.addr_id:
                self.test_save_addr()

            api_path = self.get_api_path("GEN-地址库-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.addr_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 地址库导入导出管理 ================
    @case_decorator(
        story="地址库导入导出管理",
        title="测试地址库标准导入",
        description="验证地址库标准导入服务功能",
        severity="normal",
        file_level_order=9,
        tags=["地址库", "导入", "GEN_ADDR_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_addr_import(self):
        """地址库标准导入用例 - GEN_ADDR_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("地址库标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_ADDR"),
                    "name": f"导入测试地址_{self.mock_util.get_timestamp()}",
                    "nameEn": f"Import_Test_Address_{self.mock_util.get_timestamp()}",
                    "addressType": "PROVINCE",
                    "level": 1,
                    "parentId": None
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="地址库导入导出管理",
        title="测试地址库标准导出",
        description="验证地址库标准导出服务功能",
        severity="normal",
        file_level_order=10,
        tags=["地址库", "导出", "GEN_ADDR_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_addr_export(self):
        """地址库标准导出用例 - GEN_ADDR_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("地址库标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "nameEn", "type": "TEXT"},
                    {"name": "addressType", "type": "TEXT"},
                    {"name": "level", "type": "NUMBER"},
                    {"name": "parentId", "type": "TEXT"}
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
        story="地址库任务管理",
        title="测试地址库OSS导入任务",
        description="验证地址库-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=11,
        tags=["地址库", "任务管理", "GEN_ADDR_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_addr_oss_import_task(self):
        """地址库OSS导入任务用例 - GEN_ADDR_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("地址库-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_addr_import_file.xlsx",
                "taskName": f"地址库导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
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
        story="地址库任务管理",
        title="测试地址库导出任务",
        description="验证地址库-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=12,
        tags=["地址库", "任务管理", "GEN_ADDR_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_addr_export_task(self):
        """地址库导出任务用例 - GEN_ADDR_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("地址库-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"地址库导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "nameEn", "type": "TEXT"},
                        {"name": "addressType", "type": "TEXT"},
                        {"name": "level", "type": "NUMBER"},
                        {"name": "parentId", "type": "TEXT"}
                    ]
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
