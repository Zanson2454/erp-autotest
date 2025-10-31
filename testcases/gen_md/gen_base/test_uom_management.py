import allure
import pytest
from testcases.gen_md import GenMdBaseTest

from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("计量单位综合管理")
class TestUomComprehensiveManagement(GenMdBaseTest):
    """计量单位综合管理测试类 - 覆盖所有计量单位相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()

        # 数据存储
        cls.uom_id = None
        cls.uom_code = None
        cls.uom_formula_id = None
        cls.uom_formula_code = None
        cls.logger.info("计量单位综合管理测试类初始化完成")
        
        
        # 依赖数据
        if cls.md_cache_data:
            mat_info = cls.md_cache_data.get("mat_info", {})
            mat_md = mat_info.get("mat_md", {})
            mat_md_finp = mat_md.get("FINP", [])
            cls.mat_id = mat_md_finp[0].get("id") if mat_md_finp else None

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 这里 where 里没有 %s，不要传 params
            cls.db.delete(
                table="gen_uom_formula_type_cf",
                where="unit_id in(select id from gen_uom_type_cf where uom_code like %s)",
                params=["AT_%"]
            )
            # 这里有 %s，要传 params
            cls.db.delete(
                table="gen_uom_type_cf",
                where="uom_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 计量单位基础管理 ================
    @case_decorator(
        story="计量单位基础管理",
        title="测试新增计量单位",
        description="验证GEN-计量单位-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["计量单位管理", "新增", "GEN_UOM_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_uom_type(self):
        """新增计量单位用例 - GEN_UOM_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            uom_code = self.mock_util.generate_unique_code(tag="UOM")
            uom_name = f"测试计量单位_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-计量单位-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["uomCode", "uomDigit", "uomDesc", "uomType"], ["params", "request"]
            )
            set_dict = {
                "uomCode": uom_code,
                "uomDigit": 2,
                "uomDesc": uom_name,
                "uomType": "L"  # 长度维度
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_id = response.get("data", {}).get("data", {})
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
        file_level_order=2,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_uom_type_page(self):
        """查询计量单位分页列表用例 - GEN_UOM_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-计量单位-查询分页服务")
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
                {
                    "name": "uomType",
                    "type": "SELECT"
                },
                {
                    "name": "uomDesc",
                    "type": "TEXT"
                },
                {
                    "name": "uomCode",
                    "type": "TEXT"
                }
            ],
            "systemParams": None
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
        file_level_order=3,
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
        file_level_order=4,
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
        file_level_order=5,
        tags=["计量单位管理", "查询", "GEN_UOM_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="废弃")
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
        file_level_order=6,
        tags=["计量单位管理", "转换", "GEN_UOM_TYPE_CONVERSION_ACTION_SERVICE"]
    )
    def test_uom_type_conversion(self):
        """计量单位转换功能用例 - GEN_UOM_TYPE_CONVERSION_ACTION_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("GEN-计量单位-单位转换(前端)服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["matId", "unitId", "targetUnitId", "orgAmount"], ["params", "request"]
            )
            set_dict = {
                "matId": self.mat_id,
                "unitId": self.uom_id,
                "targetUnitId": self.uom_id,
                "orgAmount": 1
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
        file_level_order=7,
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
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

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
        file_level_order=8,
        smoke=True,
        tags=["计量单位转换管理", "新增", "GEN_UOM_FORMULA_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_uom_formula(self):
        """新增计量单位转换用例 - GEN_UOM_FORMULA_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("GEN-计量单位转换-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["baseUnitFactor", "targetUnitFactor", "targetUnitId", "unitId", "genMatMdId"], ["params", "request"]
            )
            set_dict = {
                "baseUnitFactor": 1,
                "targetUnitFactor": 1,
                "targetUnitId":{
                    "id": self.uom_id
                },
                "unitId":{
                    "id": self.uom_id
                },
                "genMatMdId": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.uom_formula_id = response.get("data", {}).get("data", {})

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
        file_level_order=9,
        tags=["计量单位转换管理", "查询", "GEN_UOM_FORMULA_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_uom_formula_page(self):
        """查询计量单位转换分页列表用例 - GEN_UOM_FORMULA_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-计量单位转换-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "fromUom", "type": "TEXT"},
                    {"name": "toUom", "type": "TEXT"},
                    {"name": "rate", "type": "NUMERIC"}
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
        story="计量单位转换管理",
        title="测试查询计量单位转换详情",
        description="验证GEN-计量单位转换-查询详情服务功能",
        severity="normal",
        file_level_order=10,
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
        file_level_order=11,
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
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.uom_formula_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

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
        file_level_order=12,
        tags=["计量单位管理", "导入", "GEN_UOM_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_uom_type_import(self):
        """计量单位标准导入用例 - GEN_UOM_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("计量单位标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_UOM"),
                    "name": f"导入计量单位_{self.mock_util.get_timestamp()}",
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
        file_level_order=13,
        tags=["计量单位管理", "导出", "GEN_UOM_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
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
        file_level_order=14,
        tags=["计量单位管理", "导入", "GEN_UOM_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
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
                "taskName": f"计量单位导入任务_{self.mock_util.get_timestamp()}",
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
        file_level_order=15,
        tags=["计量单位管理", "导出", "GEN_UOM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_uom_type_export_task(self):
        """计量单位导出任务用例 - GEN_UOM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("计量单位-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['params']={
                "taskName": f"计量单位-{self.nickname}{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_uom_type_cf",
                        "modelName": "计量单位",
                        "sheetNo": 0,
                        "sheetName": "计量单位",
                        "headerConfigList": [
                            {
                                "name": "计量单位编码",
                                "type": "TEXT",
                                "field": "uomCode"
                            },
                            {
                                "name": "计量单位名称",
                                "type": "TEXT",
                                "field": "uomDesc"
                            },
                            {
                                "name": "计量单位类型编码",
                                "type": "ENUM",
                                "field": "uomType",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "长度",
                                        "label": "长度",
                                        "value": "L"
                                    },
                                    {
                                        "_row_id_": "数量",
                                        "label": "数量",
                                        "value": "QTY"
                                    },
                                    {
                                        "_row_id_": "面积",
                                        "label": "面积",
                                        "value": "AREA"
                                    },
                                    {
                                        "_row_id_": "体积",
                                        "label": "体积",
                                        "value": "VOL"
                                    },
                                    {
                                        "_row_id_": "时间",
                                        "label": "时间",
                                        "value": "TIME"
                                    },
                                    {
                                        "_row_id_": "质量",
                                        "label": "质量",
                                        "value": "MASS"
                                    },
                                    {
                                        "_row_id_": "其他",
                                        "label": "其他",
                                        "value": "OTHER"
                                    }
                                ]
                            },
                            {
                                "name": "小数位数",
                                "type": "NUMBER",
                                "field": "uomDigit"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_UOM_TYPE_VIEW-table-container-GEN_MD$gen_uom_type_cf",
                    "viewKey": "GEN_MD$GEN_UOM_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_UOM_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "uomCode"
                            },
                            {
                                "field": "uomDesc"
                            },
                            {
                                "field": "uomType"
                            },
                            {
                                "field": "uomDigit"
                            }
                        ],
                        "modelKey": "GEN_MD$gen_uom_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_uom_type_cf",
                    "modelName": "计量单位",
                    "containerKey": "GEN_MD$GEN_UOM_TYPE_VIEW-table-container-GEN_MD$gen_uom_type_cf",
                    "viewKey": "GEN_MD$GEN_UOM_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_UOM_TYPE_VIEW"
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
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
        file_level_order=16,
        tags=["计量单位管理", "转换系数", "GAIN_WEIGHT_COEFFICIENT_EVENT_SERVICE"]
    )
    def test_gain_weight_coefficient(self):
        """获取基本单位转换系数用例 - GAIN_WEIGHT_COEFFICIENT_EVENT_SERVICE"""
        try:
            if not self.uom_id:
                self.test_save_uom_type()

            api_path = self.get_api_path("GEN-UNIT-获取基本单位转换系数服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fromUnit", "toUnit"], ["params", "request"]
            )
            set_dict = {
                "unitId": {
                    "id": self.uom_id
                },
                "orgAmount": 2,
                "targetUnitId": {
                    "id": self.uom_id
                },
                "matId": {
                    "id": self.mat_id
                }
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