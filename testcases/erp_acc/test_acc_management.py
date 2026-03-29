import allure
import pytest
from testcases.erp_acc import ErpAccBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP账户模块")
@allure.feature("信用账户管理")
class TestAccManagement(ErpAccBaseTest):
    """信用账户管理测试类 - 覆盖信用账户相关服务"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.acc_id = None
        cls.logger.info("信用账户管理测试类初始化完成")
        
        # 初始化配置数据（从init_data获取）
        if cls.init_data:
            cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
            cls.coun_id = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
            cls.addr_id = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
            cls.bank_id = cls.init_data["bank_info"][0]["bank_id"] if cls.init_data.get("bank_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 禁止用循环遍历表名，必须一个表一个表地单独调用
            # 根据实际业务表名调整清理逻辑
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    # ================ 账户档案启用/停用服务 ================
    @case_decorator(
        story="信用账户档案管理",
        title="测试信用账户档案启用服务",
        description="验证信用管理-信用账户档案启用服务功能",
        severity="critical",
        file_level_order=1,
        tags=["信用账户", "启用", "ADV_CM_ARCHIVES_UN_FREEZE_ACTION_SERVICE"]
    )
    def test_archives_un_freeze(self):
        """信用账户档案启用服务用例"""
        try:
            # 前置条件：确保有账户档案ID
            if not self.acc_id:
                a.text("需要先创建账户档案", "前置条件")
                # 这里可以调用创建方法，或使用已有数据
                # self.test_save_acc_md()
            
            set_dict = {
                "id": self.acc_id if self.acc_id else 0
            }
            
            response, _ = self.standard_api_call(
                api_key="信用管理-信用账户档案启用服务",
                set_dict=set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="信用账户档案管理",
        title="测试信用账户档案停用服务",
        description="验证信用管理-信用账户档案停用服务功能",
        severity="critical",
        file_level_order=2,
        tags=["信用账户", "停用", "ADV_CM_ARCHIVES_FREEZE_ACTION_SERVICE"]
    )
    def test_archives_freeze(self):
        """信用账户档案停用服务用例"""
        try:
            # 前置条件：确保有账户档案ID
            if not self.acc_id:
                a.text("需要先创建账户档案", "前置条件")
                # 这里可以调用创建方法，或使用已有数据
                # self.test_save_acc_md()
            
            set_dict = {
                "id": self.acc_id if self.acc_id else 0
            }
            
            response, _ = self.standard_api_call(
                api_key="信用管理-信用账户档案停用服务",
                set_dict=set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 账户流水查询 ================
    @case_decorator(
        story="账户流水管理",
        title="测试账户流水分页查询",
        description="验证ACC-账户流水-分页查询功能",
        severity="critical",
        file_level_order=3,
        tags=["账户流水", "分页查询", "acc_trans_record_page_service"]
    )
    def test_acc_trans_record_page(self):
        """账户流水分页查询用例"""
        try:
            set_dict = {
                "accId": self.acc_id if self.acc_id else 0,
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="ACC-账户流水-分页查询",
                set_dict=set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 账户档案查询客户信息 ================
    @case_decorator(
        story="账户档案管理",
        title="测试账户档案查询客户信息",
        description="验证账户档案查询客户信息功能",
        severity="critical",
        file_level_order=4,
        tags=["账户档案", "查询客户信息", "account_profile_query_customer_info"]
    )
    @pytest.mark.skip(reason="账户档案查询客户信息功能未实现")
    def test_account_profile_query_customer_info(self):
        """账户档案查询客户信息用例"""
        try:
            set_dict = {
                "id": self.acc_id if self.acc_id else 0
            }
            
            response, _ = self.standard_api_call(
                api_key="账户档案查询客户信息",
                set_dict=set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 导入导出任务管理接口-提交导出任务 ================
    @case_decorator(
        story="信用账户类型抬头",
        title="测试信用账户类型抬头-提交导出任务",
        description="验证信用账户类型抬头-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=5,
        tags=["信用账户类型抬头", "导出任务", "ADV_CM_ACC_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_acc_head_cf_export_task(self):
        """信用账户类型抬头-提交导出任务用例"""
        try:
            # 导出任务接口参数复杂，使用use_param_util=False直接构造参数
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"信用账户类型抬头-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="信用账户类型抬头-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查规则抬头",
        title="测试检查规则抬头-提交导出任务",
        description="验证检查规则抬头-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=6,
        tags=["检查规则抬头", "导出任务", "ADV_CM_CR_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_cr_head_cf_export_task(self):
        """检查规则抬头-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_CR_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"检查规则抬头-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="检查规则抬头-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查项",
        title="测试检查项-提交导出任务",
        description="验证检查项-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=7,
        tags=["检查项", "导出任务", "ADV_CM_CS_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_cs_type_cf_export_task(self):
        """检查项-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_CS_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"检查项-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="检查项-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户事务抬头配置",
        title="测试账户事务抬头配置-提交导出任务",
        description="验证账户事务抬头配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["账户事务抬头配置", "导出任务", "ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_acc_trans_head_cf_export_task(self):
        """账户事务抬头配置-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"账户事务抬头配置-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户事务抬头配置-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="信用账户档案",
        title="测试信用账户档案-提交导出任务",
        description="验证信用账户档案-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=9,
        tags=["信用账户档案", "导出任务", "ADV_CM_ACC_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_acc_md_export_task(self):
        """信用账户档案-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"信用账户档案-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="信用账户档案-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户额度配置",
        title="测试账户额度配置-提交导出任务",
        description="验证账户额度配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["账户额度配置", "导出任务", "ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_acc_amount_cf_export_task(self):
        """账户额度配置-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"账户额度配置-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户额度配置-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户类别抬头",
        title="测试账户类别抬头-提交导出任务",
        description="验证账户类别抬头-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=11,
        tags=["账户类别抬头", "导出任务", "ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_acc_class_head_cf_export_task(self):
        """账户类别抬头-提交导出任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"账户类别抬头-自动化测试-{timestamp}-导出",
                    "queryData": {},
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户类别抬头-导入导出任务管理接口-提交导出任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 导入导出任务管理接口-通过OSS提交导入任务 ================
    @case_decorator(
        story="账户事务抬头配置",
        title="测试账户事务抬头配置-通过OSS提交导入任务",
        description="验证账户事务抬头配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=12,
        tags=["账户事务抬头配置", "OSS导入任务", "ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_acc_trans_head_cf_oss_import_task(self):
        """账户事务抬头配置-通过OSS提交导入任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"账户事务抬头配置-自动化测试-{timestamp}-OSS导入",
                    "fileKey": None,
                    "fileName": None,
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户事务抬头配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查项",
        title="测试检查项-通过OSS提交导入任务",
        description="验证检查项-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=13,
        tags=["检查项", "OSS导入任务", "ADV_CM_CS_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_cs_type_cf_oss_import_task(self):
        """检查项-通过OSS提交导入任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_CS_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"检查项-自动化测试-{timestamp}-OSS导入",
                    "fileKey": None,
                    "fileName": None,
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="检查项-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户额度配置",
        title="测试账户额度配置-通过OSS提交导入任务",
        description="验证账户额度配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=14,
        tags=["账户额度配置", "OSS导入任务", "ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_acc_amount_cf_oss_import_task(self):
        """账户额度配置-通过OSS提交导入任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"账户额度配置-自动化测试-{timestamp}-OSS导入",
                    "fileKey": None,
                    "fileName": None,
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户额度配置-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查规则抬头",
        title="测试检查规则抬头-通过OSS提交导入任务",
        description="验证检查规则抬头-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=15,
        tags=["检查规则抬头", "OSS导入任务", "ADV_CM_CR_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_cr_head_cf_oss_import_task(self):
        """检查规则抬头-通过OSS提交导入任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_CR_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"检查规则抬头-自动化测试-{timestamp}-OSS导入",
                    "fileKey": None,
                    "fileName": None,
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="检查规则抬头-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户类别抬头",
        title="测试账户类别抬头-通过OSS提交导入任务",
        description="验证账户类别抬头-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=16,
        tags=["账户类别抬头", "OSS导入任务", "ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_acc_class_head_cf_oss_import_task(self):
        """账户类别抬头-通过OSS提交导入任务用例"""
        try:
            timestamp = self.mock_util.get_timestamp()
            params = {
                "serviceKey": "ERP_ACC$ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"账户类别抬头-自动化测试-{timestamp}-OSS导入",
                    "fileKey": None,
                    "fileName": None,
                    "multiSheetConfig": [],
                    "processConfig": {},
                    "sheetConfig": {}
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="账户类别抬头-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 标准导入服务（全部跳过） ================
    @case_decorator(
        story="检查规则抬头",
        title="测试检查规则抬头标准导入服务",
        description="验证检查规则抬头标准导入服务功能",
        severity="normal",
        file_level_order=17,
        tags=["检查规则抬头", "标准导入", "ADV_CM_CR_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_cr_head_cf_standard_import(self):
        """检查规则抬头标准导入服务用例"""
        try:
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查项",
        title="测试检查项标准导入服务",
        description="验证检查项标准导入服务功能",
        severity="normal",
        file_level_order=18,
        tags=["检查项", "标准导入", "ADV_CM_CS_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_cs_type_cf_standard_import(self):
        """检查项标准导入服务用例"""
        try:
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户类别抬头",
        title="测试账户类别抬头标准导入服务",
        description="验证账户类别抬头标准导入服务功能",
        severity="normal",
        file_level_order=19,
        tags=["账户类别抬头", "标准导入", "ADV_CM_ACC_CLASS_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_class_head_cf_standard_import(self):
        """账户类别抬头标准导入服务用例"""
        try:
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户事务抬头配置",
        title="测试账户事务抬头配置标准导入服务",
        description="验证账户事务抬头配置标准导入服务功能",
        severity="normal",
        file_level_order=20,
        tags=["账户事务抬头配置", "标准导入", "ADV_CM_ACC_TRANS_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_trans_head_cf_standard_import(self):
        """账户事务抬头配置标准导入服务用例"""
        try:
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户额度配置",
        title="测试账户额度配置标准导入服务",
        description="验证账户额度配置标准导入服务功能",
        severity="normal",
        file_level_order=21,
        tags=["账户额度配置", "标准导入", "ADV_CM_ACC_AMOUNT_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_amount_cf_standard_import(self):
        """账户额度配置标准导入服务用例"""
        try:
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ================ 标准导出服务（全部跳过） ================
    @case_decorator(
        story="检查规则抬头",
        title="测试检查规则抬头标准导出服务",
        description="验证检查规则抬头标准导出服务功能",
        severity="normal",
        file_level_order=22,
        tags=["检查规则抬头", "标准导出", "ADV_CM_CR_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_cr_head_cf_standard_export(self):
        """检查规则抬头标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="检查项",
        title="测试检查项标准导出服务",
        description="验证检查项标准导出服务功能",
        severity="normal",
        file_level_order=23,
        tags=["检查项", "标准导出", "ADV_CM_CS_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_cs_type_cf_standard_export(self):
        """检查项标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="信用账户类型抬头",
        title="测试信用账户类型抬头标准导出服务",
        description="验证信用账户类型抬头标准导出服务功能",
        severity="normal",
        file_level_order=24,
        tags=["信用账户类型抬头", "标准导出", "ADV_CM_ACC_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_head_cf_standard_export(self):
        """信用账户类型抬头标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户事务抬头配置",
        title="测试账户事务抬头配置标准导出服务",
        description="验证账户事务抬头配置标准导出服务功能",
        severity="normal",
        file_level_order=25,
        tags=["账户事务抬头配置", "标准导出", "ADV_CM_ACC_TRANS_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_trans_head_cf_standard_export(self):
        """账户事务抬头配置标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="信用账户档案",
        title="测试信用账户档案标准导出服务",
        description="验证信用账户档案标准导出服务功能",
        severity="normal",
        file_level_order=26,
        tags=["信用账户档案", "标准导出", "ADV_CM_ACC_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_md_standard_export(self):
        """信用账户档案标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户类别抬头",
        title="测试账户类别抬头标准导出服务",
        description="验证账户类别抬头标准导出服务功能",
        severity="normal",
        file_level_order=27,
        tags=["账户类别抬头", "标准导出", "ADV_CM_ACC_CLASS_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_class_head_cf_standard_export(self):
        """账户类别抬头标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户额度配置",
        title="测试账户额度配置标准导出服务",
        description="验证账户额度配置标准导出服务功能",
        severity="normal",
        file_level_order=28,
        tags=["账户额度配置", "标准导出", "ADV_CM_ACC_AMOUNT_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_acc_amount_cf_standard_export(self):
        """账户额度配置标准导出服务用例"""
        try:
            a.text("标准导入导出业务未引用，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

