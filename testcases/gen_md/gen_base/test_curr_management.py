import allure

from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("币种管理")
class TestCurrencyManagement(GenMdBaseTest):
    """币种管理测试类 - 覆盖币种、汇率和汇率类型相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mock_data = MockData()
        cls.logger.info("币种管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_currency(self):
        currency_code = self.mock_data.generate_unique_code(tag="CURR")
        currency_name = f"测试币种_{self.mock_data.get_timestamp()}"

        set_dict = {
            "currCode": currency_code,
            "currName": currency_name,
            "symbol": currency_code,
            "decimalPlace": 2
        }
        fields_to_filter = ["currCode", "currName", "symbol", "decimalPlace"]

        response, currency_id = self.standard_api_call(
            api_key="GEN-币种配置-保存服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as="currency"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("currency", currency_id)
        self.test_data["currency_code"] = currency_code
        return currency_id

    def _ensure_save_currency(self):
        currency_id = self.get_runtime_id("currency")
        if currency_id:
            return currency_id
        return self._create_currency()

    def _create_exchange_rate(self):
        rate_code = self.mock_data.generate_unique_code(tag="RATE")
        rate_name = f"测试汇率_{self.mock_data.get_timestamp()}"

        curr_id = None
        if self.init_data:
            currency_info = self.init_data.get("currency_info", [])
            if currency_info:
                curr_id = currency_info[0].get("curr_id")
        if not curr_id:
            curr_id = 2000001

        rate_type_id = None
        if self.init_data:
            rate_type_info = self.init_data.get("exchange_rate_type_info", [])
            if rate_type_info:
                rate_type_id = rate_type_info[0].get("exchange_rate_type_id")

        set_dict = {
            "code": rate_code,
            "name": rate_name,
            "exchRate": 7.2,
            "baseCurrId": {"id": curr_id},
            "tarCurrId": {"id": curr_id},
            "genCurrExchangeRateTypeCf": {"id": rate_type_id}
        }
        fields_to_filter = ["code", "name", "exchRate", "baseCurrId", "tarCurrId", "genCurrExchangeRateTypeCf"]

        response, exchange_rate_id = self.standard_api_call(
            api_key="GEN-汇率-保存服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as="exchange_rate"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("exchange_rate", exchange_rate_id)
        return exchange_rate_id

    def _ensure_save_exchange_rate(self):
        exchange_rate_id = self.get_runtime_id("exchange_rate")
        if exchange_rate_id:
            return exchange_rate_id
        return self._create_exchange_rate()

    def _create_exchange_rate_type(self):
        rate_type_code = self.mock_data.generate_unique_code(tag="RATETYPE")
        rate_type_name = f"测试汇率类型_{self.mock_data.get_timestamp()}"

        set_dict = {
            "typeCode": rate_type_code,
            "typeName": rate_type_name,
            "typeDefault":False,
        }
        fields_to_filter = ["code", "name", "description"]

        response, exchange_rate_type_id = self.standard_api_call(
            api_key="GEN-汇率类型-保存服务",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as="exchange_rate_type"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("exchange_rate_type", exchange_rate_type_id)
        return exchange_rate_type_id

    def _ensure_save_exchange_rate_type(self):
        exchange_rate_type_id = self.get_runtime_id("exchange_rate_type")
        if exchange_rate_type_id:
            return exchange_rate_type_id
        return self._create_exchange_rate_type()

    # ================ 币种配置基础管理 ================
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
        """新增币种配置用例 - GEN_CURR_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            self._create_currency()
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "currCode", "type": "TEXT"},
                    {"name": "currName", "type": "TEXT"},
                    {"name": "symbol", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 确保币种存在（原有依赖逻辑完全保留）
            currency_id = self._ensure_save_currency()

            # 2. 使用标准化API调用
            set_dict = {"id": currency_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            self._create_exchange_rate()
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "rate", "type": "NUMERIC"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "fromCurr": "USD",
                "toCurr": "CNY"
            }
            fields_to_filter = ["fromCurr", "toCurr"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-根据基本币种与目标币种获取汇率",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            self._create_exchange_rate_type()
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 确保汇率类型存在（原有依赖逻辑完全保留）
            exchange_rate_type_id = self._ensure_save_exchange_rate_type()

            # 2. 使用标准化API调用
            set_dict = {"id": exchange_rate_type_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

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
            # 1. 确保汇率存在（原有依赖逻辑完全保留）
            exchange_rate_id = self._ensure_save_exchange_rate()

            # 2. 使用标准化API调用
            set_dict = {"id": exchange_rate_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "code": "",
                "name": ""
            }
            fields_to_filter = ["code", "name"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-查询汇率(前端)服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 根据ID查找数据服务 ================
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
            # 1. 确保币种存在（原有依赖逻辑完全保留）
            currency_id = self._ensure_save_currency()

            # 2. 使用标准化API调用
            set_dict = {"id": currency_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="币种配置-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 确保汇率类型存在（原有依赖逻辑完全保留）
            exchange_rate_type_id = self._ensure_save_exchange_rate_type()

            # 2. 使用标准化API调用
            set_dict = {"id": exchange_rate_type_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 使用标准化API调用
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
                        "name": "currName",
                        "type": "TEXT"
                    },
                    {
                        "name": "currCode",
                        "type": "TEXT"
                    }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]
            
            response, _ = self.standard_api_call(
                api_key="币种配置-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "conditionGroup": None,
                    "sortOrders": None,
                    "keyword": None
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="汇率类型-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 汇率导入导出管理 ================


    # ================ 汇率类型导入导出管理 ================


    # ================ 导入导出任务管理接口 ================






    # ================ 删除服务 ================
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
            # 1. 准备测试数据（原有业务逻辑完全保留）
            currency_code = self.mock_data.generate_unique_code(tag="DEL_CURR")
            currency_name = f"待删除币种_{self.mock_data.get_timestamp()}"

            save_set_dict = {
                "currCode": currency_code,
                "currName": currency_name,
                "symbol": currency_code,
                "decimalPlace": 2
            }
            save_response, delete_currency_id = self.standard_api_call(
                api_key="GEN-币种配置-保存服务",
                set_dict=save_set_dict,
                fields_to_filter=["currCode", "currName", "symbol", "decimalPlace"]
            )
            self.assert_util.assert_response_data(save_response)

            # 2. 使用标准化API调用删除
            set_dict = {"id": delete_currency_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-币种配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 准备测试数据（原有业务逻辑完全保留）
            rate_code = self.mock_data.generate_unique_code(tag="DEL_RATE")
            rate_name = f"待删除汇率_{self.mock_data.get_timestamp()}"

            # 获取币种ID和汇率类型ID（原有逻辑，安全访问）
            curr_id = None
            if self.init_data:
                currency_info = self.init_data.get("currency_info", [])
                if currency_info:
                    curr_id = currency_info[0].get("curr_id", 2000001)
            if not curr_id:
                curr_id = 2000001  # 默认值
            
            rate_type_id = None
            if self.init_data:
                rate_type_info = self.init_data.get("exchange_rate_type_info", [])
                if rate_type_info:
                    rate_type_id = rate_type_info[0].get("exchange_rate_type_id")
            
            save_set_dict = {
                "code": rate_code,
                "name": rate_name,
                "exchRate": 7.2,
                "baseCurrId": {"id": curr_id},
                "tarCurrId": {"id": curr_id},
                "genCurrExchangeRateTypeCf": {"id": rate_type_id}
            }
            save_response, delete_rate_id = self.standard_api_call(
                api_key="GEN-汇率-保存服务",
                set_dict=save_set_dict,
                fields_to_filter=["code", "name", "exchRate", "baseCurrId", "tarCurrId", "genCurrExchangeRateTypeCf"]
            )
            self.assert_util.assert_response_data(save_response)

            # 2. 使用标准化API调用删除
            set_dict = {"id": delete_rate_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
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
            # 1. 准备测试数据（原有业务逻辑完全保留）
            rate_type_code = self.mock_data.generate_unique_code(tag="DEL_RATETYPE")
            rate_type_name = f"待删除汇率类型_{self.mock_data.get_timestamp()}"

            save_set_dict = {
                "code": rate_type_code,
                "name": rate_type_name,
                "description": "待删除汇率类型描述"
            }
            save_response, delete_rate_type_id = self.standard_api_call(
                api_key="GEN-汇率类型-保存服务",
                set_dict=save_set_dict,
                fields_to_filter=["code", "name", "description"]
            )
            self.assert_util.assert_response_data(save_response)

            # 2. 使用标准化API调用删除
            set_dict = {"id": delete_rate_type_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-汇率类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 币种配置导入导出管理 ================


    # ================ 综合测试场景 ================
    @case_decorator(
        story="币种综合测试",
        title="测试币种汇率完整业务流程",
        description="验证币种、汇率、汇率类型的完整业务流程",
        severity="critical",
        file_level_order=31,
        tags=["币种管理", "综合测试", "业务流程"]
    )
    def test_currency_complete_workflow(self):
        """币种汇率完整业务流程测试用例"""
        try:
            # 1. 创建币种（原有完整流程保留）
            currency_code = self.mock_data.generate_unique_code(tag="WORKFLOW_CURR")
            currency_name = f"流程测试币种_{self.mock_data.get_timestamp()}"

            # 创建币种
            currency_set_dict = {
                "currCode": currency_code,
                "currName": currency_name,
                "symbol": currency_code,
                "decimalPlace": 2
            }
            currency_fields_to_filter = ["currCode", "currName", "symbol", "decimalPlace"]
            
            currency_response, workflow_currency_id = self.standard_api_call(
                api_key="GEN-币种配置-保存服务",
                set_dict=currency_set_dict,
                fields_to_filter=currency_fields_to_filter
            )
            self.assert_util.assert_response_data(currency_response)
            
            workflow_currency_id = workflow_currency_id  # 存储用于后续

            # 2. 创建汇率类型
            rate_type_code = self.mock_data.generate_unique_code(tag="WORKFLOW_RATETYPE")
            rate_type_name = f"流程测试汇率类型_{self.mock_data.get_timestamp()}"

            rate_type_set_dict = {
                "code": rate_type_code,
                "name": rate_type_name,
                "description": "流程测试汇率类型"
            }
            rate_type_fields_to_filter = ["code", "name", "description"]
            
            rate_type_response, rate_type_id = self.standard_api_call(
                api_key="GEN-汇率类型-保存服务",
                set_dict=rate_type_set_dict,
                fields_to_filter=rate_type_fields_to_filter
            )
            self.assert_util.assert_response_data(rate_type_response)

            # 3. 创建汇率
            rate_code = self.mock_data.generate_unique_code(tag="WORKFLOW_RATE")
            rate_name = f"流程测试汇率_{self.mock_data.get_timestamp()}"

            # 获取币种ID和汇率类型ID（原有逻辑，安全访问）
            curr_id = None
            if self.init_data:
                currency_info = self.init_data.get("currency_info", [])
                if currency_info:
                    curr_id = currency_info[0].get("curr_id", 2000001)
            if not curr_id:
                curr_id = 2000001  # 默认值
            
            rate_type_id = None
            if self.init_data:
                rate_type_info = self.init_data.get("exchange_rate_type_info", [])
                if rate_type_info:
                    rate_type_id = rate_type_info[0].get("exchange_rate_type_id")
            
            rate_set_dict = {
                "code": rate_code,
                "name": rate_name,
                "exchRate": 0.14,
                "baseCurrId": {"id": curr_id},
                "tarCurrId": {"id": curr_id},
                "genCurrExchangeRateTypeCf": {"id": rate_type_id}
            }
            rate_fields_to_filter = ["code", "name", "exchRate", "baseCurrId", "tarCurrId", "genCurrExchangeRateTypeCf"]
            
            rate_response, _ = self.standard_api_call(
                api_key="GEN-汇率-保存服务",
                set_dict=rate_set_dict,
                fields_to_filter=rate_fields_to_filter
            )
            self.assert_util.assert_response_data(rate_response)

            # 4. 原有最终日志（保留）
            a.json({"workflow": "complete"}, "完整流程执行成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 
