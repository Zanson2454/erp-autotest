import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("币种管理")
class TestCurrencyManagement(GenMdBaseTest):
    """币种管理测试类 - 覆盖币种、汇率和汇率类型相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.curr_id = None
        cls.exchange_rate_id = None
        cls.exchange_rate_type_id = None
        cls.logger.info("币种管理测试类初始化完成")
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_curr_type_cf",
                where="curr_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_curr_formula_type_cf",
                where="exchange_rate_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_curr_exchange_rate_type_cf",
                where="exchange_rate_type_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 币种配置管理 ================
    @case_decorator(
        story="币种配置管理",
        title="测试新增币种配置",
        description="验证GEN-币种配置-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["币种管理", "新增", "GEN_CURR_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_currency(self):
        """新增币种配置用例"""
        try:
            curr_code = self.mock_util.generate_unique_code(tag="CURR")
            curr_name = f"测试币种_{self.mock_util.get_timestamp()}"

            set_dict = {
                "currCode": curr_code,
                "currName": curr_name,
                "currNameEn": f"Test Currency_{self.mock_util.get_timestamp()}",
                "currSymbol": "TC",
                "currDecimal": 2,
                "currIsBase": False
            }
            
            response, curr_id = self.standard_api_call(
                api_key="GEN-币种配置-保存服务",
                set_dict=set_dict,
                fields_to_filter=["currCode", "currName", "currNameEn", "currSymbol", "currDecimal", "currIsBase"],
                store_id_as="curr"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种配置管理",
        title="测试查询币种配置分页列表",
        description="验证GEN-币种配置-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["币种管理", "查询", "GEN_CURR_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_currency_page(self):
        """查询币种配置分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "symbol", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种配置管理",
        title="测试查询币种配置详情",
        description="验证GEN-币种配置-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["币种管理", "查询", "GEN_CURR_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_currency_detail(self):
        """查询币种配置详情用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()

            set_dict = {"id": self.curr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 汇率管理 ================
    @case_decorator(
        story="汇率管理",
        title="测试新增汇率",
        description="验证GEN-汇率-保存服务功能",
        severity="blocker",
        file_level_order=4,
        smoke=True,
        tags=["汇率管理", "新增", "GEN_CURR_FORMULA_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_exchange_rate(self):
        """新增汇率用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()
                
            exchange_rate_code = self.mock_util.generate_unique_code(tag="EXCHANGE_RATE")
            exchange_rate_name = f"测试汇率_{self.mock_util.get_timestamp()}"

            set_dict = {
                "exchangeRateCode": exchange_rate_code,
                "exchangeRateName": exchange_rate_name,
                "baseCurrId": {"id": self.curr_id},
                "targetCurrId": {"id": self.curr_id},
                "exchangeRate": 1.0,
                "effectiveDate": self.mock_util.get_timestamp(),
                "remark": f"汇率描述_{self.mock_util.get_timestamp()}"
            }
            
            response, exchange_rate_id = self.standard_api_call(
                api_key="GEN-汇率-保存服务",
                set_dict=set_dict,
                fields_to_filter=["exchangeRateCode", "exchangeRateName", "baseCurrId", "targetCurrId", "exchangeRate", "effectiveDate", "remark"],
                store_id_as="exchange_rate"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试查询汇率分页列表",
        description="验证GEN-汇率-查询分页服务功能",
        severity="normal",
        file_level_order=5,
        tags=["汇率管理", "查询", "GEN_CURR_FORMULA_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_exchange_rate_page(self):
        """查询汇率分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "exchangeRateCode", "type": "TEXT"},
                    {"name": "exchangeRateName", "type": "TEXT"},
                    {"name": "exchangeRate", "type": "NUMBER"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试根据币种获取汇率",
        description="验证GEN-汇率-根据基本币种与目标币种获取汇率功能",
        severity="normal",
        file_level_order=6,
        tags=["汇率管理", "查询", "GEN_GET_RATE_FROM_CURR_SERVICE"]
    )
    def test_get_rate_from_currency(self):
        """根据币种获取汇率用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()

            set_dict = {
                "baseCurrId": {"id": self.curr_id},
                "targetCurrId": {"id": self.curr_id}
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-根据基本币种与目标币种获取汇率",
                set_dict=set_dict,
                fields_to_filter=["baseCurrId", "targetCurrId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 汇率类型管理 ================
    @case_decorator(
        story="汇率类型管理",
        title="测试新增汇率类型",
        description="验证GEN-汇率类型-保存服务功能",
        severity="blocker",
        file_level_order=7,
        smoke=True,
        tags=["汇率类型管理", "新增", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_exchange_rate_type(self):
        """新增汇率类型用例"""
        try:
            exchange_rate_type_code = self.mock_util.generate_unique_code(tag="EXCHANGE_RATE_TYPE")
            exchange_rate_type_name = f"测试汇率类型_{self.mock_util.get_timestamp()}"

            set_dict = {
                "exchangeRateTypeCode": exchange_rate_type_code,
                "exchangeRateTypeName": exchange_rate_type_name,
                "remark": f"汇率类型描述_{self.mock_util.get_timestamp()}"
            }
            
            response, exchange_rate_type_id = self.standard_api_call(
                api_key="GEN-汇率类型-保存服务",
                set_dict=set_dict,
                fields_to_filter=["exchangeRateTypeCode", "exchangeRateTypeName", "remark"],
                store_id_as="exchange_rate_type"
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型管理",
        title="测试查询汇率类型分页列表",
        description="验证GEN-汇率类型-查询分页服务功能",
        severity="normal",
        file_level_order=8,
        tags=["汇率类型管理", "查询", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_exchange_rate_type_page(self):
        """查询汇率类型分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "exchangeRateTypeCode", "type": "TEXT"},
                    {"name": "exchangeRateTypeName", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型管理",
        title="测试查询汇率类型详情",
        description="验证GEN-汇率类型-查询详情服务功能",
        severity="normal",
        file_level_order=9,
        tags=["汇率类型管理", "查询", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_exchange_rate_type_detail(self):
        """查询汇率类型详情用例"""
        try:
            if not self.exchange_rate_type_id:
                self.test_save_exchange_rate_type()

            set_dict = {"id": self.exchange_rate_type_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 汇率管理详情 ================
    @case_decorator(
        story="汇率管理",
        title="测试查询汇率详情",
        description="验证GEN-汇率-查询详情服务功能",
        severity="normal",
        file_level_order=10,
        tags=["汇率管理", "查询", "GEN_CURR_FORMULA_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_exchange_rate_detail(self):
        """查询汇率详情用例"""
        try:
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            set_dict = {"id": self.exchange_rate_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试查询汇率(前端)",
        description="验证GEN-汇率-查询汇率(前端)服务功能",
        severity="normal",
        file_level_order=11,
        tags=["汇率管理", "查询", "GEN_CURR_FORMULA_TYPE_CF_QUERY_ACTION_SERVICE"]
    )
    def test_query_exchange_rate_frontend(self):
        """查询汇率(前端)用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()

            set_dict = {
                "baseCurrId": {"id": self.curr_id},
                "targetCurrId": {"id": self.curr_id}
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询汇率(前端)服务",
                set_dict=set_dict,
                fields_to_filter=["baseCurrId", "targetCurrId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 币种配置管理详情 ================
    @case_decorator(
        story="币种配置管理",
        title="测试币种配置根据ID查找数据",
        description="验证币种配置-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=12,
        tags=["币种管理", "查询", "GEN_CURR_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_currency_data_by_id(self):
        """币种配置根据ID查找数据用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()

            set_dict = {"id": self.curr_id}
            
            response, _ = self.standard_api_call(
                api_key="币种配置-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型管理",
        title="测试汇率类型根据ID查找数据",
        description="验证汇率类型-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=13,
        tags=["汇率类型管理", "查询", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_exchange_rate_type_data_by_id(self):
        """汇率类型根据ID查找数据用例"""
        try:
            if not self.exchange_rate_type_id:
                self.test_save_exchange_rate_type()

            set_dict = {"id": self.exchange_rate_type_id}
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 分页数据服务 ================
    @case_decorator(
        story="币种配置管理",
        title="测试币种配置分页数据服务",
        description="验证币种配置-分页数据服务功能",
        severity="normal",
        file_level_order=14,
        tags=["币种管理", "查询", "GEN_CURR_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    def test_currency_paging_data(self):
        """币种配置分页数据服务用例"""
        try:
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
                    {"name": "symbol", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="币种配置-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型管理",
        title="测试汇率类型分页数据服务",
        description="验证汇率类型-分页数据服务功能",
        severity="normal",
        file_level_order=15,
        tags=["汇率类型管理", "查询", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_PAGING_DATA_SERVICE"]
    )
    def test_exchange_rate_type_paging_data(self):
        """汇率类型分页数据服务用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "exchangeRateTypeCode", "type": "TEXT"},
                    {"name": "exchangeRateTypeName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 导入导出管理 ================
    @case_decorator(
        story="汇率管理",
        title="测试汇率标准导入",
        description="验证汇率标准导入服务功能",
        severity="normal",
        file_level_order=16,
        tags=["汇率管理", "导入", "GEN_CURR_FORMULA_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="汇率标准导入服务功能未实现")
    def test_exchange_rate_import(self):
        """汇率标准导入用例"""
        try:
            import_data = [
                {
                    "exchangeRateCode": self.mock_util.generate_unique_code(tag="IMPORT_EXCHANGE"),
                    "exchangeRateName": "导入测试汇率",
                    "baseCurrId": {"id": self.curr_id},
                    "targetCurrId": {"id": self.curr_id},
                    "exchangeRate": 1.0
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="汇率标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试汇率标准导出",
        description="验证汇率标准导出服务功能",
        severity="normal",
        file_level_order=17,
        tags=["汇率管理", "导出", "GEN_CURR_FORMULA_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="汇率标准导出服务功能未实现")
    def test_exchange_rate_export(self):
        """汇率标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "exchangeRateCode", "type": "TEXT"},
                    {"name": "exchangeRateName", "type": "TEXT"},
                    {"name": "exchangeRate", "type": "NUMBER"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型导入导出管理",
        title="测试汇率类型标准导入",
        description="验证汇率类型标准导入服务功能",
        severity="normal",
        file_level_order=18,
        tags=["汇率类型管理", "导入", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="汇率类型标准导入服务功能未实现")
    def test_exchange_rate_type_import(self):
        """汇率类型标准导入用例"""
        try:
            import_data = [
                {
                    "exchangeRateTypeCode": self.mock_util.generate_unique_code(tag="IMPORT_EXCHANGE_TYPE"),
                    "exchangeRateTypeName": "导入测试汇率类型"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="汇率类型标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型导入导出管理",
        title="测试汇率类型标准导出",
        description="验证汇率类型标准导出服务功能",
        severity="normal",
        file_level_order=19,
        tags=["汇率类型管理", "导出", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="汇率类型标准导出服务功能未实现")
    def test_exchange_rate_type_export(self):
        """汇率类型标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "exchangeRateTypeCode", "type": "TEXT"},
                    {"name": "exchangeRateTypeName", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率类型标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 任务管理 ================
    @case_decorator(
        story="币种配置任务管理",
        title="测试币种配置OSS导入任务",
        description="验证币种配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=20,
        tags=["币种管理", "任务管理", "GEN_CURR_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务功能未实现")
    def test_currency_oss_import_task(self):
        """币种配置OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_currency_import.xlsx",
                "taskName": f"币种配置导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="币种配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种配置任务管理",
        title="测试币种配置导出任务",
        description="验证币种配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=21,
        tags=["币种管理", "任务管理", "GEN_CURR_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="导出任务功能未实现")
    def test_currency_export_task(self):
        """币种配置导出任务用例"""
        try:
            set_dict = {
                "taskName": f"币种配置导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "symbol", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="币种配置-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率任务管理",
        title="测试汇率OSS导入任务",
        description="验证汇率-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=22,
        tags=["汇率管理", "任务管理", "GEN_CURR_FORMULA_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务功能未实现")
    def test_exchange_rate_oss_import_task(self):
        """汇率OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_exchange_rate_import.xlsx",
                "taskName": f"汇率导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率任务管理",
        title="测试汇率导出任务",
        description="验证汇率-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=23,
        tags=["汇率管理", "任务管理", "GEN_CURR_FORMULA_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="导出任务功能未实现")
    def test_exchange_rate_export_task(self):
        """汇率导出任务用例"""
        try:
            set_dict = {
                "taskName": f"汇率导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "exchangeRateCode", "type": "TEXT"},
                        {"name": "exchangeRateName", "type": "TEXT"},
                        {"name": "exchangeRate", "type": "NUMBER"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型任务管理",
        title="测试汇率类型OSS导入任务",
        description="验证汇率类型-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=24,
        tags=["汇率类型管理", "任务管理", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务功能未实现")
    def test_exchange_rate_type_oss_import_task(self):
        """汇率类型OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_exchange_rate_type_import.xlsx",
                "taskName": f"汇率类型导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型任务管理",
        title="测试汇率类型导出任务",
        description="验证汇率类型-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=25,
        tags=["汇率类型管理", "任务管理", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="导出任务功能未实现")
    def test_exchange_rate_type_export_task(self):
        """汇率类型导出任务用例"""
        try:
            set_dict = {
                "taskName": f"汇率类型导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "exchangeRateTypeCode", "type": "TEXT"},
                        {"name": "exchangeRateTypeName", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 删除操作 ================
    @case_decorator(
        story="币种配置管理",
        title="测试删除币种配置",
        description="验证GEN-币种配置-删除服务功能",
        severity="critical",
        file_level_order=26,
        tags=["币种管理", "删除", "GEN_CURR_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_currency(self):
        """删除币种配置用例"""
        try:
            if not self.curr_id:
                self.test_save_currency()

            set_dict = {"id": self.curr_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率管理",
        title="测试删除汇率",
        description="验证GEN-汇率-删除服务功能",
        severity="critical",
        file_level_order=27,
        tags=["汇率管理", "删除", "GEN_CURR_FORMULA_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_exchange_rate(self):
        """删除汇率用例"""
        try:
            if not self.exchange_rate_id:
                self.test_save_exchange_rate()

            set_dict = {"id": self.exchange_rate_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="汇率类型管理",
        title="测试删除汇率类型",
        description="验证GEN-汇率类型-删除服务功能",
        severity="critical",
        file_level_order=28,
        tags=["汇率类型管理", "删除", "GEN_CURR_EXCHANGE_RATE_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_exchange_rate_type(self):
        """删除汇率类型用例"""
        try:
            if not self.exchange_rate_type_id:
                self.test_save_exchange_rate_type()

            set_dict = {"id": self.exchange_rate_type_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 币种导入导出管理 ================
    @case_decorator(
        story="币种导入导出管理",
        title="测试币种配置标准导入",
        description="验证币种配置标准导入服务功能",
        severity="normal",
        file_level_order=29,
        tags=["币种管理", "导入", "GEN_CURR_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="币种配置标准导入服务功能未实现")
    def test_currency_import(self):
        """币种配置标准导入用例"""
        try:
            import_data = [
                {
                    "currCode": self.mock_util.generate_unique_code(tag="IMPORT_CURR"),
                    "currName": "导入测试币种",
                    "currNameEn": "Import Test Currency",
                    "currSymbol": "ITC"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="币种配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="币种导入导出管理",
        title="测试币种配置标准导出",
        description="验证币种配置标准导出服务功能",
        severity="normal",
        file_level_order=30,
        tags=["币种管理", "导出", "GEN_CURR_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="币种配置标准导出服务功能未实现")
    def test_currency_export(self):
        """币种配置标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "currCode", "type": "TEXT"},
                    {"name": "currName", "type": "TEXT"},
                    {"name": "currSymbol", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="币种配置标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 币种综合测试 ================
    @case_decorator(
        story="币种综合测试",
        title="测试币种汇率完整业务流程",
        description="验证币种、汇率、汇率类型的完整业务流程",
        severity="critical",
        file_level_order=31,
        tags=["币种管理", "综合测试", "业务流程"]
    )
    def test_currency_complete_workflow(self):
        """币种汇率完整业务流程用例"""
        try:
            # 1. 创建币种
            self.test_save_currency()
            
            # 2. 创建汇率
            self.test_save_exchange_rate()
            
            # 3. 创建汇率类型
            self.test_save_exchange_rate_type()
            
            # 4. 验证完整流程
            self.logger.info("币种汇率完整业务流程测试通过")
            self.assert_util.assert_by_operator(self.curr_id, "not_none")
            self.assert_util.assert_by_operator(self.exchange_rate_id, "not_none")
            self.assert_util.assert_by_operator(self.exchange_rate_type_id, "not_none")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 