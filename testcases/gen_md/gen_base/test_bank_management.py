import allure
import pytest

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("银行系统管理")
class TestBankSystemManagement(GenMdBaseTest):
    """银行系统管理测试类 - 整合银行、银行支行等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # MockData 单例自动处理，无需手动创建
        cls.logger.info("银行系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_bank(self):
        bank_code = self.mock_util.generate_unique_code(tag="Bank")
        bank_name = f"银行_{self.mock_util.get_timestamp()}"

        set_dict = {
            "bankCode": bank_code,
            "bankName": bank_name,
            "bankMneCode": f"bankMneCode_{self.mock_util.get_timestamp()}",
            "bankSwiftCode": f"bankSwiftCode_{self.mock_util.get_timestamp()}"
        }

        self.logger.info(f"set_dict: {set_dict}")

        response, bank_id = self.standard_api_call(
            api_key="GEN-银行配置-保存服务",
            set_dict=set_dict,
            fields_to_filter=["bankCode", "bankName", "bankMneCode", "bankSwiftCode"],
            store_id_as="bank"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("bank", bank_id)
        self.test_data["bank_code"] = bank_code
        self.logger.info(f"保存银行成功，bank_id: {bank_id}, bank_code: {bank_code}")
        return bank_id

    def _ensure_save_bank(self):
        bank_id = self.get_runtime_id("bank")
        if bank_id:
            return bank_id
        return self._create_bank()

    def _create_sub_bank(self):
        bank_id = self._ensure_save_bank()

        sub_bank_code = self.mock_util.generate_unique_code(tag="SubBank")
        sub_bank_name = f"银行支行_{self.mock_util.get_timestamp()}"

        set_dict = {
            "subBankCode": sub_bank_code,
            "subBankName": sub_bank_name,
            "genBankId": {"id": bank_id}
        }

        response, sub_bank_id = self.standard_api_call(
            api_key="GEN-银行支行-保存服务",
            set_dict=set_dict,
            fields_to_filter=["subBankCode", "subBankName", "genBankId"],
            store_id_as="sub_bank"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("sub_bank", sub_bank_id)
        self.test_data["sub_bank_code"] = sub_bank_code
        return sub_bank_id

    def _ensure_save_sub_bank(self):
        sub_bank_id = self.get_runtime_id("sub_bank")
        if sub_bank_id:
            return sub_bank_id
        return self._create_sub_bank()
    # ================ 银行管理 ================
    @case_decorator(
        story="银行管理",
        title="测试新增银行",
        description="验证新增银行功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["银行管理", "新增"]
    )
    def test_save_bank(self):
        """新增银行用例"""
        try:
            self._create_bank()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试查询银行列表",
        description="验证银行列表查询功能",
        severity="normal",
        file_level_order=2,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_list(self):
        """查询银行列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "bankCode", "type": "TEXT"},
                    {"name": "bankName", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行配置-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )
            
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试查询银行详情",
        description="验证银行详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["银行管理", "查询"]
    )
    def test_query_bank_detail(self):
        """查询银行详情用例"""
        try:
            bank_id = self._ensure_save_bank()
            set_dict = {"id": bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行管理",
        title="测试删除银行",
        description="验证删除银行功能",
        severity="normal",
        file_level_order=4,
        tags=["银行管理", "删除"]
    )
    def test_delete_bank(self):
        """删除银行用例"""
        try:
            bank_id = self._ensure_save_bank()
            set_dict = {"id": bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行支行管理 ================
    @case_decorator(
        story="银行支行管理",
        title="测试新增银行支行",
        description="验证新增银行支行功能",
        severity="blocker",
        file_level_order=5,
        smoke=True,
        tags=["银行支行管理", "新增"]
    )
    def test_save_sub_bank(self):
        """新增银行支行用例"""
        try:
            self._create_sub_bank()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试查询银行支行列表",
        description="验证银行支行列表查询功能",
        severity="normal",
        file_level_order=6,
        tags=["银行支行管理", "查询"]
    )
    def test_query_sub_bank_list(self):
        """查询银行支行列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "sub_bank_code", "type": "TEXT"},
                    {"name": "sub_bank_name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行支行-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )
            
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试查询银行支行详情",
        description="验证银行支行详情查询功能",
        severity="normal",
        file_level_order=7,
        tags=["银行支行管理", "查询"]
    )
    def test_query_sub_bank_detail(self):
        """查询银行支行详情用例"""
        try:
            sub_bank_id = self._ensure_save_sub_bank()
            set_dict = {"id": sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行支行-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试删除银行支行",
        description="验证删除银行支行功能",
        severity="normal",
        file_level_order=8,
        tags=["银行支行管理", "删除"]
    )
    def test_delete_sub_bank(self):
        """删除银行支行用例"""
        try:
            sub_bank_id = self._ensure_save_sub_bank()
            set_dict = {"id": sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行支行-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行配置根据ID查找数据服务 ================
    @case_decorator(
        story="银行管理",
        title="测试银行配置根据ID查找数据",
        description="验证银行配置-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=9,
        tags=["银行管理", "查询", "GEN_BANK_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_find_bank_data_by_id(self):
        """银行配置根据ID查找数据用例"""
        try:
            bank_id = self._ensure_save_bank()
            set_dict = {"id": bank_id}
            
            response, _ = self.standard_api_call(
                api_key="银行配置-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试银行支行根据ID查找数据",
        description="验证银行支行-根据ID查找数据服务功能",
        severity="normal",
        file_level_order=10,
        tags=["银行支行管理", "查询", "GEN_SUB_BANK_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_find_sub_bank_data_by_id(self):
        """银行支行根据ID查找数据用例"""
        try:
            sub_bank_id = self._ensure_save_sub_bank()
            set_dict = {"id": sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="银行支行-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 分页数据服务 ================
    @case_decorator(
        story="银行管理",
        title="测试银行配置分页数据服务",
        description="验证银行配置-分页数据服务功能",
        severity="normal",
        file_level_order=11,
        tags=["银行管理", "查询", "GEN_BANK_CF_PAGING_DATA_SERVICE"]
    )
    def test_bank_paging_data(self):
        """银行配置分页数据服务用例"""
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
                    {"name": "bank_code", "type": "TEXT"},
                    {"name": "bank_name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            response, _ = self.standard_api_call(
                api_key="银行配置-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="银行支行管理",
        title="测试银行支行分页数据服务",
        description="验证银行支行-分页数据服务功能",
        severity="normal",
        file_level_order=12,
        tags=["银行支行管理", "查询", "GEN_SUB_BANK_CF_PAGING_DATA_SERVICE"]
    )
    def test_sub_bank_paging_data(self):
        """银行支行分页数据服务用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "conditionGroup": None,
                    "sortOrders": None,
                    "keyword": None
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="银行支行-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行配置导入导出管理 ================

    @case_decorator(
        story="银行配置导入导出管理",
        title="测试银行配置标准导出",
        description="验证银行配置标准导出服务功能",
        severity="normal",
        file_level_order=14,
        tags=["银行管理", "导出", "GEN_BANK_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_bank_export(self):
        """银行配置标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "bank_code", "type": "TEXT"},
                    {"name": "bank_name", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="银行配置标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行支行导入导出管理 ================

    @case_decorator(
        story="银行支行导入导出管理",
        title="测试银行支行标准导出",
        description="验证银行支行标准导出服务功能",
        severity="normal",
        file_level_order=16,
        tags=["银行支行管理", "导出", "GEN_SUB_BANK_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_sub_bank_export(self):
        """银行支行标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "sub_bank_code", "type": "TEXT"},
                    {"name": "sub_bank_name", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="银行支行标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行配置任务管理接口 ================

    @case_decorator(
        story="银行配置任务管理",
        title="测试银行配置导出任务",
        description="验证银行配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=18,
        tags=["银行管理", "任务管理", "GEN_BANK_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_bank_export_task(self):
        """银行配置导出任务用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fields": [
                        {"name": "bank_code", "type": "TEXT"},
                        {"name": "bank_name", "type": "TEXT"}
                    ],
                    "condition": {}
                },
                "taskName": f"银行配置导出任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="银行配置-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 银行支行任务管理接口 ================

    @case_decorator(
        story="银行支行任务管理",
        title="测试银行支行导出任务",
        description="验证银行支行-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=20,
        tags=["银行支行管理", "任务管理", "GEN_SUB_BANK_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_sub_bank_export_task(self):
        """银行支行导出任务用例"""
        try:
            set_dict = {
                "exportConfig": {
                    "fields": [
                        {"name": "sub_bank_code", "type": "TEXT"},
                        {"name": "sub_bank_name", "type": "TEXT"}
                    ],
                    "condition": {}
                },
                "taskName": f"银行支行导出任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="银行支行-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 
