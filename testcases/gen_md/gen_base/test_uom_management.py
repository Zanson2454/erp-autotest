import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("计量单位综合管理")
class TestUomComprehensiveManagement(GenMdBaseTest):
    """计量单位综合管理测试类 - 覆盖所有计量单位相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 数据存储
        cls.uom_id = None
        cls.uom_code = None
        cls.uom_formula_id = None
        cls.uom_formula_code = None
        cls.logger.info("计量单位综合管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_uom_md", "gen_uom_formula_md"]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="code like %s",
                        params=["AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 计量单位基础管理 ================
    @case_decorator(
        story="计量单位基础管理",
        title="测试新增计量单位",
        description="验证GEN-计量单位-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["计量单位管理", "新增", "GEN_UOM_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_uom_type(self):
        """新增计量单位用例 - GEN_UOM_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            uom_code = self.mock_data.generate_unique_code(tag="UOM")
            uom_name = f"测试计量单位_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "symbol", "dimension"], ["params", "request"]
            )
            set_dict = {
                "code": uom_code,
                "name": uom_name,
                "symbol": uom_code,
                "dimension": "LENGTH"  # 长度维度
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_id = response.get("data", {}).get("data", {})
            self.uom_code = uom_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位基础管理",
        title="测试查询计量单位分页列表",
        description="验证GEN-计量单位-查询分页服务功能",
        severity="normal",
        order=2,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_uom_type_page(self):
        """查询计量单位分页列表用例 - GEN_UOM_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-计量单位-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "symbol", "type": "TEXT"},
                    {"name": "dimension", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位基础管理",
        title="测试计量单位分页数据服务",
        description="验证计量单位-分页数据服务功能",
        severity="normal",
        order=3,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    def test_query_uom_type_paging_data(self):
        """计量单位分页数据服务用例 - GEN_UOM_TYPE_CF_PAGING_DATA_SERVICE"""
        try:
            api_path = self.get_api_path("计量单位-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 10, "needTotal": True}
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
        story="计量单位基础管理",
        title="测试查询计量单位详情",
        description="验证GEN-计量单位-查询详情服务功能",
        severity="normal",
        order=4,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_uom_type_detail(self):
        """查询计量单位详情用例 - GEN_UOM_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("GEN-计量单位-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位基础管理",
        title="测试根据ID查找计量单位数据",
        description="验证计量单位-根据ID查找数据服务功能",
        severity="normal",
        order=5,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_uom_type_by_id(self):
        """根据ID查找计量单位数据用例 - GEN_UOM_TYPE_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("计量单位-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位基础管理",
        title="测试计量单位转换功能",
        description="验证GEN-计量单位-单位转换(前端)服务功能",
        severity="normal",
        order=6,
        tags=["计量单位管理", "转换", "GEN_UOM_TYPE_CONVERSION_ACTION_SERVICE"]
    )
    def test_uom_type_conversion(self):
        """计量单位转换功能用例 - GEN_UOM_TYPE_CONVERSION_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-计量单位-单位转换(前端)服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fromUom", "toUom", "value"], ["params", "request"]
            )
            set_dict = {
                "fromUom": "M",   # 米
                "toUom": "CM",    # 厘米
                "value": 1.0
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
        story="计量单位基础管理",
        title="测试删除计量单位",
        description="验证GEN-计量单位-删除服务功能",
        severity="normal",
        order=7,
        tags=["计量单位管理", "删除", "GEN_UOM_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_uom_type(self):
        """删除计量单位用例 - GEN_UOM_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("GEN-计量单位-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.uom_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 计量单位转换管理 ================
    @case_decorator(
        story="计量单位转换管理",
        title="测试新增计量单位转换",
        description="验证GEN-计量单位转换-保存服务功能",
        severity="blocker",
        order=8,
        smoke=True,
        tags=["计量单位转换管理", "新增", "GEN_UOM_FORMULA_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_uom_formula(self):
        """新增计量单位转换用例 - GEN_UOM_FORMULA_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            formula_code = self.mock_data.generate_unique_code(tag="UOMF")
            formula_name = f"测试计量单位转换_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位转换-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "fromUom", "toUom", "rate"], ["params", "request"]
            )
            set_dict = {
                "code": formula_code,
                "name": formula_name,
                "fromUom": "M",     # 源单位：米
                "toUom": "CM",      # 目标单位：厘米
                "rate": 100.0       # 转换率：1米=100厘米
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_formula_id = response.get("data", {}).get("data", {})
            self.uom_formula_code = formula_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位转换管理",
        title="测试查询计量单位转换分页列表",
        description="验证GEN-计量单位转换-查询分页服务功能",
        severity="normal",
        order=9,
        tags=["计量单位转换管理", "查询", "GEN_UOM_FORMULA_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_uom_formula_page(self):
        """查询计量单位转换分页列表用例 - GEN_UOM_FORMULA_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-计量单位转换-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "fromUom", "type": "TEXT"},
                    {"name": "toUom", "type": "TEXT"},
                    {"name": "rate", "type": "NUMERIC"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位转换管理",
        title="测试查询计量单位转换详情",
        description="验证GEN-计量单位转换-查询详情服务功能",
        severity="normal",
        order=10,
        tags=["计量单位转换管理", "查询", "GEN_UOM_FORMULA_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_uom_formula_detail(self):
        """查询计量单位转换详情用例 - GEN_UOM_FORMULA_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.uom_formula_id:
                self.test_save_uom_formula()

            api_path = self.get_api_path("GEN-计量单位转换-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_formula_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="计量单位转换管理",
        title="测试删除计量单位转换",
        description="验证GEN-计量单位转换-删除服务功能",
        severity="normal",
        order=11,
        tags=["计量单位转换管理", "删除", "GEN_UOM_FORMULA_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_uom_formula(self):
        """删除计量单位转换用例 - GEN_UOM_FORMULA_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.uom_formula_id:
                self.test_save_uom_formula()

            api_path = self.get_api_path("GEN-计量单位转换-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.uom_formula_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 导入导出管理 ================
    @case_decorator(
        story="计量单位导入导出管理",
        title="测试计量单位标准导入",
        description="验证计量单位标准导入服务功能",
        severity="normal",
        order=12,
        tags=["计量单位管理", "导入", "GEN_UOM_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    def test_uom_type_import(self):
        """计量单位标准导入用例 - GEN_UOM_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("计量单位标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_data.generate_unique_code(tag="IMPORT_UOM"),
                    "name": f"导入计量单位_{self.mock_data.get_timestamp()}",
                    "symbol": "IMPORT_UOM",
                    "dimension": "MASS"
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
        story="计量单位导入导出管理",
        title="测试计量单位标准导出",
        description="验证计量单位标准导出服务功能",
        severity="normal",
        order=13,
        tags=["计量单位管理", "导出", "GEN_UOM_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    def test_uom_type_export(self):
        """计量单位标准导出用例 - GEN_UOM_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("计量单位标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "symbol", "type": "TEXT"},
                    {"name": "dimension", "type": "TEXT"}
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
        story="计量单位导入导出管理",
        title="测试计量单位OSS导入任务",
        description="验证计量单位-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=14,
        tags=["计量单位管理", "导入", "GEN_UOM_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_uom_type_oss_import_task(self):
        """计量单位OSS导入任务用例 - GEN_UOM_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("计量单位-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_uom_import_file.xlsx",
                "taskName": f"计量单位导入任务_{self.mock_data.get_timestamp()}",
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
        story="计量单位导入导出管理",
        title="测试计量单位导出任务",
        description="验证计量单位-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=15,
        tags=["计量单位管理", "导出", "GEN_UOM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_uom_type_export_task(self):
        """计量单位导出任务用例 - GEN_UOM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("计量单位-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"计量单位导出任务_{self.mock_data.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"}
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

    # ================ 单位转换系数服务 ================
    @case_decorator(
        story="单位转换系数管理",
        title="测试获取基本单位转换系数",
        description="验证GEN-UNIT-获取基本单位转换系数服务功能",
        severity="normal",
        order=16,
        tags=["计量单位管理", "转换系数", "GAIN_WEIGHT_COEFFICIENT_EVENT_SERVICE"]
    )
    def test_gain_weight_coefficient(self):
        """获取基本单位转换系数用例 - GAIN_WEIGHT_COEFFICIENT_EVENT_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-UNIT-获取基本单位转换系数服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fromUnit", "toUnit"], ["params", "request"]
            )
            set_dict = {
                "fromUnit": "KG",    # 千克
                "toUnit": "G"        # 克
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的转换系数
            coefficient_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(coefficient_data, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 