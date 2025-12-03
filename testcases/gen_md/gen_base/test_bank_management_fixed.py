import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData  # 保持导入以兼容，但实际使用 self.mock_util
from utils.param_util import ParamUtil
from utils.report_util import a


@allure.epic("通用基础数据")
@allure.feature("银行系统管理")
class TestBankSystemManagement(GenMdBaseTest):
    """银行系统管理测试类 - 整合银行、银行支行等功能 - 修复版（无 @case_decorator）"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # MockData 单例自动处理，无需手动创建
        cls.bank_id = None
        cls.bank_code = None
        cls.sub_bank_id = None
        cls.sub_bank_code = None
        cls.logger.info("银行系统管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="gen_bank_cf", where="bank_code like %s", params=["AT_%"])
            cls.db.delete(table="gen_sub_bank_cf", where="sub_bank_code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @allure.story("银行管理")
    @allure.title("测试新增银行")
    @allure.description("验证新增银行功能")
    @allure.severity(allure.severity_level.blocker)
    @allure.label("银行管理", "新增")
    def test_save_bank(self):
        """新增银行用例"""
        try:
            bank_code = self.mock_util.generate_unique_code(tag="Bank")
            bank_name = f"银行_{self.mock_util.get_timestamp()}"

            set_dict = {
                "bankCode": bank_code, 
                "bankName": bank_name,
                "bankMneCode":f"bankMneCode_{self.mock_util.get_timestamp()}",
                "bankSwiftCode":f"bankSwiftCode_{self.mock_util.get_timestamp()}"
            }
            
            self.logger.info(f"set_dict: {set_dict}")
            
            response, bank_id = self.standard_api_call(
                api_key="GEN-银行配置-保存服务",
                set_dict=set_dict,
                fields_to_filter=["bankCode", "bankName","bankMneCode","bankSwiftCode"],
                store_id_as="bank"
            )
            
            self.bank_code = bank_code
            self.logger.info(f"保存银行成功，bank_id: {self.bank_id}, bank_code: {self.bank_code}")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行管理")
    @allure.title("测试查询银行列表")
    @allure.description("验证银行列表查询功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "查询")
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

    @allure.story("银行管理")
    @allure.title("测试查询银行详情")
    @allure.description("验证银行详情查询功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "查询")
    def test_query_bank_detail(self):
        """查询银行详情用例"""
        try:
            if not self.bank_id:
                self.test_save_bank()

            set_dict = {"id": self.bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行配置-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行管理")
    @allure.title("测试删除银行")
    @allure.description("验证删除银行功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "删除")
    def test_delete_bank(self):
        """删除银行用例"""
        try:
            if not self.bank_id:
                self.test_save_bank()

            set_dict = {"id": self.bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行配置-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行管理")
    @allure.title("测试新增银行支行")
    @allure.description("验证新增银行支行功能")
    @allure.severity(allure.severity_level.blocker)
    @allure.label("银行支行管理", "新增")
    def test_save_sub_bank(self):
        """新增银行支行用例"""
        try:
            sub_bank_code = self.mock_util.generate_unique_code(tag="SubBank")
            sub_bank_name = f"银行支行_{self.mock_util.get_timestamp()}"

            set_dict = {
                "subBankCode": sub_bank_code, 
                "subBankName": sub_bank_name,
                "genBankId": {"id":self.bank_id}
            }
            
            response, sub_bank_id = self.standard_api_call(
                api_key="GEN-银行支行-保存服务",
                set_dict=set_dict,
                fields_to_filter=["subBankCode", "subBankName","genBankId"],
                store_id_as="sub_bank"
            )
            
            self.sub_bank_code = sub_bank_code

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行管理")
    @allure.title("测试查询银行支行列表")
    @allure.description("验证银行支行列表查询功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "查询")
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

    @allure.story("银行支行管理")
    @allure.title("测试查询银行支行详情")
    @allure.description("验证银行支行详情查询功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "查询")
    def test_query_sub_bank_detail(self):
        """查询银行支行详情用例"""
        try:
            if not self.sub_bank_id:
                self.test_save_sub_bank()

            set_dict = {"id": self.sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行支行-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行管理")
    @allure.title("测试删除银行支行")
    @allure.description("验证删除银行支行功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "删除")
    def test_delete_sub_bank(self):
        """删除银行支行用例"""
        try:
            if not self.sub_bank_id:
                self.test_save_sub_bank()

            set_dict = {"id": self.sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-银行支行-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行管理")
    @allure.title("测试银行配置根据ID查找数据")
    @allure.description("验证银行配置-根据ID查找数据服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "查询")
    @pytest.mark.skip(reason="业务用不上")
    def test_find_bank_data_by_id(self):
        """银行配置根据ID查找数据用例"""
        try:
            if not self.bank_id:
                self.test_save_bank()

            set_dict = {"id": self.bank_id}
            
            response, _ = self.standard_api_call(
                api_key="银行配置-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行管理")
    @allure.title("测试银行支行根据ID查找数据")
    @allure.description("验证银行支行-根据ID查找数据服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "查询")
    @pytest.mark.skip(reason="业务用不上")
    def test_find_sub_bank_data_by_id(self):
        """银行支行根据ID查找数据用例"""
        try:
            if not self.sub_bank_id:
                self.test_save_sub_bank()

            set_dict = {"id": self.sub_bank_id}
            
            response, _ = self.standard_api_call(
                api_key="银行支行-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行管理")
    @allure.title("测试银行配置分页数据服务")
    @allure.description("验证银行配置-分页数据服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "查询")
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

    @allure.story("银行支行管理")
    @allure.title("测试银行支行分页数据服务")
    @allure.description("验证银行支行-分页数据服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "查询")
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

    @allure.story("银行配置导入导出管理")
    @allure.title("测试银行配置标准导入")
    @allure.description("验证银行配置标准导入服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "导入")
    @pytest.mark.skip(reason="业务用不上")
    def test_bank_import(self):
        """银行配置标准导入用例"""
        try:
            import_data = [
                {
                    "bank_code": self.mock_util.generate_unique_code(tag="IMPORT_BANK"),
                    "bank_name": f"导入测试银行_{self.mock_util.get_timestamp()}"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="银行配置标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行配置导入导出管理")
    @allure.title("测试银行配置标准导出")
    @allure.description("验证银行配置标准导出服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "导出")
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

    @allure.story("银行支行导入导出管理")
    @allure.title("测试银行支行标准导入")
    @allure.description("验证银行支行标准导入服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "导入")
    @pytest.mark.skip(reason="业务用不上")
    def test_sub_bank_import(self):
        """银行支行标准导入用例"""
        try:
            import_data = [
                {
                    "sub_bank_code": self.mock_util.generate_unique_code(tag="IMPORT_SUBBANK"),
                    "sub_bank_name": f"导入测试银行支行_{self.mock_util.get_timestamp()}"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="银行支行标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行导入导出管理")
    @allure.title("测试银行支行标准导出")
    @allure.description("验证银行支行标准导出服务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "导出")
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

    @allure.story("银行配置任务管理")
    @allure.title("测试银行配置OSS导入任务")
    @allure.description("验证银行配置-导入导出任务管理接口-通过OSS提交导入任务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "任务管理")
    @pytest.mark.skip(reason="业务用不上")
    def test_bank_oss_import_task(self):
        """银行配置OSS导入任务用例"""
        try:
            set_dict = {
                "ossPath": "/test/bank_import.xlsx",
                "taskName": f"银行配置导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="银行配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["ossPath", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行配置任务管理")
    @allure.title("测试银行配置导出任务")
    @allure.description("验证银行配置-导入导出任务管理接口-提交导出任务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行管理", "任务管理")
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

    @allure.story("银行支行任务管理")
    @allure.title("测试银行支行OSS导入任务")
    @allure.description("验证银行支行-导入导出任务管理接口-通过OSS提交导入任务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "任务管理")
    @pytest.mark.skip(reason="业务用不上")
    def test_sub_bank_oss_import_task(self):
        """银行支行OSS导入任务用例"""
        try:
            set_dict = {
                "ossPath": "/test/sub_bank_import.xlsx",
                "taskName": f"银行支行导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="银行支行-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["ossPath", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.story("银行支行任务管理")
    @allure.title("测试银行支行导出任务")
    @allure.description("验证银行支行-导入导出任务管理接口-提交导出任务功能")
    @allure.severity(allure.severity_level.normal)
    @allure.label("银行支行管理", "任务管理")
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
