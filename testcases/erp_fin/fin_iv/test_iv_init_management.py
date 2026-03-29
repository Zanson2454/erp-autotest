# -*- coding: utf-8 -*-
"""
存货价值初始化管理测试用例
包含：存货价值初始化配置表管理、存货核算初始化配置管理
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值初始化管理")
class TestIvInitManagement(FinBaseTest):
    """存货价值初始化管理测试类"""
    

    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.continuous_method_init_cf_id = None
        cls.period_method_init_cf_id = None
        cls.logger.info("存货价值初始化管理测试类初始化完成")
        # 初始化MD数据（从md_cache_data获取主数据）
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            com_org_info = cls.md_cache_data.get("org_info", {}).get("com_org_info", [])
            cls.com_org_id = com_org_info[0].get("id") if com_org_info else None
            cls.gr_com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            
        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.continuous_method_init_cf_id:
                cls.db.delete(
                    table="fin_iv_init_cf",
                    where="id = %s",
                    params=[cls.continuous_method_init_cf_id]
                )
            if cls.period_method_init_cf_id:
                cls.db.delete(
                    table="fin_iv_init_cf",
                    where="id = %s",
                    params=[cls.period_method_init_cf_id]
                )
            # cls.db.delete(
            #     table="fin_iv_init_cf",  # 存货价值初始化配置表
            #     where="com_org_id = %s and iv_type = 'PERIOD_METHOD'",
            #     params=[cls.com_org_id]
            # )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试初始化配置",
        description="验证存货核算初始化配置初始化功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "init", "initialize"]
    )
    @pytest.mark.parametrize("iv_type", ["PERIOD_METHOD", "CONTINUOUS_METHOD"])  # 永续成本法 、 期间成本法
    def test_initialize_configuration(self, iv_type):
        """测试存货价值初始化配置"""
        try:
            # 检查依赖数据
            if not self.com_org_id or not self.gr_com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            if not iv_type:
                iv_type = "CONTINUOUS_METHOD"
            if iv_type == "PERIOD_METHOD":
                com_org_obj = {"id": self.gr_com_org_id}
            if iv_type == "CONTINUOUS_METHOD":
                com_org_obj = {"id": self.com_org_id}
            
            # 构造期间对象（简化版，只传id）
            period_head_obj = {"id": self.calendar_head_id} if hasattr(self, 'calendar_head_id') and self.calendar_head_id else None
            start_period_obj = {"id": self.calendar_item_id} if hasattr(self, 'calendar_item_id') and self.calendar_item_id else None
            
            set_dict = {
                "comOrgId": com_org_obj,
                "ivType": iv_type,
                "periodHeadId": period_head_obj,
                "startPeriod": start_period_obj,
                "enableStatus": "DISABLE",
                "beginStatus": None,
                "initStatus": "NOT_INIT",
                "accountingStatus": "WAITING",
                "accountStatus": "WAITING",
                "asyncExecutionStatus": "CREATED",
                "asyncExecutionFailureReason": None,
                "currentPeriod": None
            }
            
            
            # 调用前先删除初始化数据，防止触发唯一性校验
            self.db.delete(
                table="fin_iv_init_cf",
                where="com_org_id = %s and iv_type = %s",
                params=[com_org_obj.get("id"), iv_type]
            )
            
            # 注意：接口定义中参数路径写错了（reuqest应该是request），使用param_path参数处理
            # store_id_as 会自动添加 _id 后缀，所以这里只需要提供基础名称
            iv_type_lower = iv_type.lower()  # CONTINUOUS_METHOD -> continuous_method
            response, extracted_id = self.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                store_id_as=f"{iv_type_lower}_init_cf",  # 会存储为 self.continuous_method_init_cf_id 或 self.period_method_init_cf_id
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            self.assert_util.assert_by_operator(extracted_id, "not_empty", "初始化配置ID为空")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试重复初始化配置报错",
        description="验证重复初始化配置会返回错误",
        severity="normal",
        file_level_order=2,
        tags=["iv", "init", "initialize", "duplicate_error"]
    )
    def test_initialize_configuration_duplicate_error(self):
        """测试重复初始化配置报错"""
        try:
            
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            com_org_obj = {"id": self.com_org_id}
            
            # 构造期间对象
            period_head_obj = {"id": self.calendar_head_id} if hasattr(self, 'calendar_head_id') and self.calendar_head_id else None
            start_period_obj = {"id": self.calendar_item_id} if hasattr(self, 'calendar_item_id') and self.calendar_item_id else None
            
            set_dict = {
                "comOrgId": com_org_obj,
                "ivType": "CONTINUOUS_METHOD",
                "periodHeadId": period_head_obj,
                "startPeriod": start_period_obj,
                "enableStatus": "DISABLE",
                "beginStatus": None,
                "initStatus": "NOT_INIT",
                "accountingStatus": "WAITING",
                "accountStatus": "WAITING",
                "asyncExecutionStatus": "CREATED",
                "asyncExecutionFailureReason": None,
                "currentPeriod": None
            }
            
            fields_to_filter = ["comOrgId", "ivType", "periodHeadId", "startPeriod", "enableStatus", "beginStatus", "initStatus", "accountingStatus", "accountStatus", "asyncExecutionStatus", "asyncExecutionFailureReason", "currentPeriod"]
            
            # 验证重复初始化会报错
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,  # 不存储ID
                param_path=["params", "reuqest"]  # 使用reuqest路径
            )
            
            # 业务断言：验证错误响应
            err_code = response.get("err", {}).get("code")
            err_msg = response.get("err", {}).get("msg")
            self.assert_util.assert_by_operator(
                err_code, "=", "fin.iv.init.cf.company.already.initialized",
                f"错误代码应为fin.iv.init.cf.company.already.initialized，实际: {err_code}"
            )
            self.assert_util.assert_by_operator(
                err_msg, "=", "公司组织已初始化，请勿重复初始化",
                f"业务提示应为公司组织已初始化，请勿重复初始化，实际: {err_msg}"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试更新初始化配置",
        description="验证更新存货核算初始化配置功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "init", "initialize", "update"]
    )
    def test_update_configuration(self):
        """测试更新初始化配置"""
        try:
            # 确保已创建初始化配置
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            config_id = self.continuous_method_init_cf_id
            com_org_obj = {"id": self.com_org_id}
            
            # 构造期间对象
            period_head_obj = {"id": self.calendar_head_id} if hasattr(self, 'calendar_head_id') and self.calendar_head_id else None
            start_period_obj = {"id": self.calendar_item_id} if hasattr(self, 'calendar_item_id') and self.calendar_item_id else None
            
            set_dict = {
                "id": config_id,
                "comOrgId": com_org_obj,
                "ivType": "CONTINUOUS_METHOD",
                "periodHeadId": period_head_obj,
                "startPeriod": start_period_obj,
                "enableStatus": "DISABLE",
                "beginStatus": None,
                "initStatus": "NOT_INIT",
                "accountingStatus": "WAITING",
                "accountStatus": "WAITING",
                "asyncExecutionStatus": "CREATED",
                "asyncExecutionFailureReason": None,
                "currentPeriod": None
            }
            
            fields_to_filter = ["id", "comOrgId", "ivType", "periodHeadId", "startPeriod", "enableStatus", "beginStatus", "initStatus", "accountingStatus", "accountStatus", "asyncExecutionStatus", "asyncExecutionFailureReason", "currentPeriod"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID删除数据",
        description="验证根据ID删除存货价值初始化配置表数据",
        severity="normal",
        file_level_order=4,
        tags=["iv", "init", "value", "delete"]
    )
    def test_delete_init_cf_by_id(self):
        """测试根据ID删除数据"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试分页数据",
        description="验证分页查询存货价值初始化配置表",
        severity="normal",
        file_level_order=6,
        tags=["iv", "init", "value", "paging"]
    )
    def test_paging_init_cf_data(self):
        """测试分页数据"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            # 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证总记录数（参数化测试每个类型创建一条记录，所以至少应该有1条）
            total_count = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total_count, ">=", 1, "总记录数应大于等于1")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID查找数据",
        description="验证根据ID查找存货价值初始化配置表数据",
        severity="normal",
        file_level_order=7,
        tags=["iv", "init", "value", "find_by_id"]
    )
    def test_find_init_cf_by_id(self):
        """测试根据ID查找数据"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            # 使用标准化API调用
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            config_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(config_data.get("id"), "=", self.continuous_method_init_cf_id, "详情查询ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID查找用户数据",
        description="验证根据ID查找用户数据服务功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "init", "user", "find_by_id"]
    )
    def test_find_user_by_id(self):
        """测试根据ID查找用户数据"""
        try:
            # 获取当前登录用户ID
            if not self.user_info or not self.user_info.get("id"):
                raise ValueError("user_info 未初始化或用户ID不存在，请检查登录状态")
            
            user_id = self.user_info.get("id")
            
            # 使用标准化API调用
            set_dict = {"id": user_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="用户-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的用户数据
            user_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(user_data.get("id"), "=", user_id, "用户ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试执行初始化后处理-启用初始化配置",
        description="验证存货核算初始化配置执行后处理流程",
        severity="normal",
        file_level_order=8,
        tags=["iv", "init", "post_process"]
    )
    def test_execute_post_initialization(self):
        """测试执行初始化后处理"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            

            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-执行初始化后处理流程",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            
            # 业务断言
            enableStatus = response.get("data", {}).get("data", {}).get("enableStatus")
            self.assert_util.assert_by_operator(enableStatus, "=", "ENABLED", "启用状态应为ENABLED")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试反启用配置",
        description="验证存货核算初始化配置反启用功能",
        severity="normal",
        file_level_order=9,
        tags=["iv", "init", "disable"]
    )
    def test_disable_configuration(self):
        """测试反启用配置"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD"  )
                self.test_execute_post_initialization()
            
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-反启用配置",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            enableStatus = response.get("data", {}).get("data", {}).get("enableStatus")
            self.assert_util.assert_by_operator(enableStatus, "=", "DISABLE", "启用状态应为DISABLE")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试期初确认",
        description="验证存货核算初始化配置期初确认功能",
        severity="critical",
        file_level_order=10,
        tags=["iv", "init", "confirm"]
    )
    def test_confirm_begin(self):
        """测试期初确认"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_execute_post_initialization()
            
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            # 使用use_param_util=False手动构造参数（因为需要reuqest路径）
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-期初确认",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            
            # 业务断言
            beginStatus = response.get("data", {}).get("data", {}).get("beginStatus")
            self.assert_util.assert_by_operator(beginStatus, "=", "CONFIRM", "期初确认状态应为CONFIRM")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试期初反确认",
        description="验证存货核算初始化配置期初反确认功能",
        severity="critical",
        file_level_order=11,
        tags=["iv", "init", "reverse_confirm"]
    )
    def test_reverse_confirm_begin(self):
        """测试期初反确认"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_confirm_begin()
            
            # 使用use_param_util=False手动构造参数（因为需要reuqest路径）
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-期初反确认",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            beginStatus = response.get("data", {}).get("data", {}).get("beginStatus")
            self.assert_util.assert_by_operator(beginStatus, "=", "WAIT_CONFIRM", "期初确认状态应为WAIT_CONFIRM")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试异步执行初始化并等待完成",
        description="验证存货核算初始化配置异步执行初始化功能，并等待异步任务完成",
        severity="normal",
        file_level_order=12,
        tags=["iv", "init", "async", "wait"]
    )
    def test_execute_initialization_async_and_wait(self):
        """
        测试异步执行初始化并等待完成
        
        测试流程：
        1. 发起异步初始化任务
        2. 验证任务已创建（状态为CREATED）
        3. 轮询查询任务状态，等待任务完成
        4. 验证初始化状态和异步执行状态
        
        业务说明：
        - 存货核算初始化是一个异步任务，需要等待后台处理完成
        - 异步任务状态流转：CREATED -> PROCESSING -> SUCCEEDED/FAILED
        - 初始化状态流转：WAIT_INIT -> INIT（成功时）
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保初始化配置已创建并确认开始，否则先执行前置用例
            # init_cf_id 是初始化配置的ID，由前置用例 test_confirm_begin() 创建
            if not self.continuous_method_init_cf_id:
                self.test_confirm_begin()
            
            # ========== 步骤1：发起异步初始化任务 ==========
            # 调用异步任务发起接口，触发后台初始化处理
            # 该接口会立即返回，不会等待任务完成，任务在后台异步执行
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-执行初始化-异步任务发起",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建（CREATED状态表示任务已成功提交到队列）
            # 此时任务还未开始执行，只是进入了任务队列等待处理
            asyncExecutionStatus = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            self.assert_util.assert_by_operator(
                asyncExecutionStatus, "=", "CREATED", 
                "异步任务发起初始化状态应为CREATED，表示任务已成功提交到队列"
            )
            
            # ========== 步骤2：定义查询函数 ==========
            # 定义查询函数，用于轮询检查初始化配置的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            # 注意：函数内部需要处理异常，避免异常导致轮询中断
            def query_init_status():
                """
                查询初始化配置状态
                
                功能说明：
                - 调用查询详情接口，获取初始化配置的当前状态
                - 返回的数据包含异步任务执行状态和初始化业务状态
                
                返回数据字段说明：
                - asyncExecutionStatus: 异步执行状态
                  * CREATED: 任务已创建，等待执行
                  * PROCESSING: 任务执行中
                  * SUCCEEDED: 任务执行成功
                  * FAILED: 任务执行失败
                - initStatus: 初始化业务状态
                  * WAIT_INIT: 等待初始化
                  * INIT: 初始化完成
                - asyncExecutionFailureReason: 失败原因（仅在失败时存在）
                
                返回：
                    dict: 包含初始化配置的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="存货价值初始化配置表-根据ID查找数据服务",
                    set_dict={"id": self.continuous_method_init_cf_id},
                    fields_to_filter=["id"]
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤3：等待异步任务完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            # 工具会自动：
            # - 按interval间隔（1秒）调用query_init_status函数
            # - 检查asyncExecutionStatus字段的值
            # - 如果状态为SUCCEEDED则返回成功，停止轮询
            # - 如果状态为FAILED则返回失败并记录失败原因，停止轮询
            # - 如果超过max_wait时间（10秒）仍未完成则返回超时，停止轮询
            # - 自动记录每次轮询的结果到Allure报告中
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_init_status,  # 查询函数，每次轮询时调用
                status_field="asyncExecutionStatus",  # 要检查的状态字段名
                success_status="SUCCEEDED",  # 成功状态值，达到此状态时停止等待
                failed_status="FAILED",  # 失败状态值，达到此状态时立即返回失败
                failure_reason_field="asyncExecutionFailureReason",  # 失败原因字段名，用于记录失败详情
                max_wait=10,  # 最大等待时间（秒），超过此时间仍未完成则返回超时
                interval=1  # 轮询间隔（秒），每1秒查询一次状态
            )
            
            # ========== 步骤4：断言等待结果 ==========
            # 根据等待结果进行断言验证
            # result.status 的可能值：
            # - SUCCESS: 等待成功，任务已完成
            # - FAILED: 任务执行失败
            # - TIMEOUT: 等待超时，任务未在指定时间内完成
            # - ERROR: 查询过程出错
            
            if result.status == self.wait_status.SUCCESS:
                # 等待成功，验证业务状态
                
                # 4.1 验证初始化状态
                # 初始化成功后，initStatus应该从WAIT_INIT变为INIT
                # 这表示初始化业务逻辑已成功执行
                init_status = result.last_data.get("initStatus")
                self.assert_util.assert_by_operator(
                    init_status, "=", "INIT",
                    f"初始化任务应成功完成，initStatus应为INIT，实际状态: {init_status}"
                )
                
                # 4.2 验证异步执行状态
                # 异步任务执行成功后，asyncExecutionStatus应该为SUCCEEDED
                # 这表示异步任务本身已成功完成
                asyncExecutionStatus = result.last_data.get("asyncExecutionStatus")
                self.assert_util.assert_by_operator(
                    asyncExecutionStatus, "=", "SUCCEEDED", 
                    f"异步任务状态应为SUCCEEDED，实际状态: {asyncExecutionStatus}"
                )
                
                # 4.3 验证失败原因为空
                # 任务成功时，asyncExecutionFailureReason应该为None
                # 如果存在失败原因，说明任务虽然状态是SUCCEEDED，但可能有警告信息
                asyncExecutionFailureReason = result.last_data.get("asyncExecutionFailureReason")
                self.assert_util.assert_by_operator(
                    asyncExecutionFailureReason, "=", None, 
                    f"异步任务失败原因应为None，实际原因: {asyncExecutionFailureReason}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 初始化任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"初始化状态: {init_status}\n"
                    f"异步执行状态: {asyncExecutionStatus}",
                    "任务完成"
                )
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                # 失败原因通常包含业务错误信息，有助于定位问题
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"异步初始化任务失败: {failure_reason}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后数据: {result.last_data}"
                )
            elif result.status == self.wait_status.TIMEOUT:
                # 等待超时，抛出异常
                # 超时可能的原因：
                # 1. 任务执行时间过长，超过max_wait设置
                # 2. 系统负载过高，任务处理缓慢
                # 3. 任务卡住，未正常执行
                raise AssertionError(
                    f"等待异步初始化任务超时\n"
                    f"最大等待时间: 10秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                # 这种情况通常是查询接口调用失败，而非业务逻辑问题
                raise AssertionError(
                    f"等待异步初始化任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
                
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            # 异常信息包含完整的错误堆栈和上下文信息
            a.text(str(e), "失败原因")
            raise
        
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据公司组织查找数据",
        description="验证根据公司组织查找存货价值初始化配置表数据",
        severity="normal",
        file_level_order=13,
        tags=["iv", "init", "value", "find_by_com_org"]
    )
    def test_find_init_cf_by_com_org_id(self):
        """测试根据公司组织查找数据"""
        try:
            # 确保初始化配置已创建并启用
            if not self.continuous_method_init_cf_id:
                self.test_execute_initialization_async_and_wait()
            
            # 使用标准化API调用
            set_dict = {"comOrgId": {"id": self.com_org_id}}
            fields_to_filter = ["comOrgId"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-根据公司组织查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            a.json(response, "根据公司组织查找数据响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试反初始化",
        description="验证存货核算初始化配置反初始化功能",
        severity="critical",
        file_level_order=14,
        tags=["iv", "init", "reverse_init"]
    )
    def test_reverse_initialization(self):
        """测试反初始化"""
        try:
            # 检查并创建依赖数据
            if not self.continuous_method_init_cf_id:
                self.test_execute_initialization_async_and_wait()
            
            # 使用标准化API调用
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-反初始",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证反初始化后的状态
            reverse_init_data = response.get("data", {}).get("data", {})
            init_status_after_reverse = reverse_init_data.get("initStatus")
            self.assert_util.assert_by_operator(
                init_status_after_reverse, "=", "NOT_INIT",
                f"反初始化后，initStatus应为NOT_INIT，实际状态: {init_status_after_reverse}"
            )
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
    
   
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试批量删除数据",
        description="验证批量删除存货价值初始化配置表数据",
        severity="normal",
        file_level_order=15,
        tags=["iv", "init", "value", "batch_delete"]
    )
    def test_batch_delete_init_cf(self):
        """测试批量删除数据"""
        try:
            # 创建多个数据用于批量删除
            if not self.period_method_init_cf_id:
                    self.test_initialize_configuration(iv_type="PERIOD_METHOD") 
            
            set_dict = {
                    "ids": [self.period_method_init_cf_id]
                }
                
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试复制数据转换服务",
        description="验证存货价值初始化配置表复制数据转换功能",
        severity="normal",
        file_level_order=16,
        tags=["iv", "init", "value", "copy"]
    )
    def test_copy_data_converter(self):
        """测试复制数据转换服务"""
        try:
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            # 使用标准化API调用
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-复制数据转换服务", 
                set_dict=set_dict, 
                fields_to_filter=fields_to_filter, 
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试复制数据转换子服务",
        description="验证存货价值初始化配置表复制数据转换子服务功能",
        severity="normal",
        file_level_order=17,
        tags=["iv", "init", "value", "copy_child"]
    )
    def test_copy_data_converter_child(self):
        """测试复制数据转换子服务"""
        try:
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            # 复制子服务需要源ID和modelKey参数
            # modelKey 用于后端服务构建URL路径，不能为null
            # 使用use_param_util=False手动构建参数结构，确保modelKey在params层级，不在request层级
            set_dict = {
                "request": {
                    "id": self.continuous_method_init_cf_id
                },
                "modelKey": "ERP_FIN$fin_iv_init_cf"
            }
            
            response, _ = self.standard_api_call(
                api_key="存货价值初始化配置表-复制数据转换子服务",
                set_dict=set_dict,
                fields_to_filter=None,
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    

    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试执行初始化",
        description="验证存货核算初始化配置执行初始化功能",
        severity="critical",
        file_level_order=18,
        tags=["iv", "init", "execute"]
    )
    @pytest.mark.skip(reason="实际无调用，代码内部处理事务，服务不需要加锁")
    def test_execute_initialization(self):
        """测试执行初始化"""
        try:
            # 检查并创建依赖数据
            if not self.init_config_id:
                self.test_confirm_begin()
            
            # 使用标准化API调用
            set_dict = {"configId": self.init_config_id}
            fields_to_filter = ["configId"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-执行初始化-无事务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    

    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试执行核算",
        description="验证存货核算初始化配置执行核算功能",
        severity="critical",
        file_level_order=19,
        tags=["iv", "init", "accounting"]
    )
    @pytest.mark.skip(reason="实际无调用")
    def test_execute_accounting(self):
        """测试执行核算"""
        try:
            # 检查并创建依赖数据
            if not self.init_config_id:
                self.test_initialize_configuration()
                self.test_execute_post_initialization()
            
            # 使用标准化API调用
            set_dict = {"id": self.init_config_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-执行核算-无事务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试结账",
        description="验证存货核算初始化配置结账功能",
        severity="critical",
        file_level_order=20,
        tags=["iv", "init", "close"]
    )
    def test_close_account(self):
        """测试结账"""
        try:
            if not self.continuous_method_init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            set_dict = {"id": self.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-结账",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]
            )
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试反结账",
    #     description="验证存货核算初始化配置反结账功能",
    #     severity="critical",
    #     order=15,
    #     tags=["iv", "init", "reverse_close"]
    # )
    # def test_reverse_close_account(self):
    #     """测试反结账"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
    #             self.test_close_account()  # 先结账再反结账
            
    #         api_path = self.get_api_path("存货核算初始化配置-反结账")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(response, "反结账响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    

    
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试保存数据",
    #     description="验证保存存货价值初始化配置表数据",
    #     severity="normal",
    #     order=17,
    #     tags=["iv", "init", "value", "save"]
    # )
    # def test_save_init_cf_data(self):
    #     """测试保存数据"""
    #     try:
    #         config_code = self.mock_util.generate_unique_code(tag="AT_IV_INIT_CF")
    #         name = f"价值配置_{self.mock_util.get_timestamp()}"
    #         remark = self.mock_util.get_mock_remark()
            
    #         api_path = self.get_api_path("存货价值初始化配置表-保存数据服务")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["comOrgId", "code", "name", "remark"], ["params", "request"]
    #         )
    #         set_dict = {
    #             "comOrgId": self.com_org_id,
    #             "code": config_code,
    #             "name": name,
    #             "remark": remark
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         self.init_cf_id = response.get("data", {}).get("data", {}).get("id")
    #         a.json(filtered_params, "保存请求数据")
    #         a.json(response, "保存响应数据")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    
    
    
    # @pytest.mark.skip(reason="异步核算任务需要监控，复杂度较高")
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试异步执行核算", 
    #     description="验证存货核算初始化配置异步执行核算功能",
    #     severity="normal",
    #     order=21,
    #     tags=["iv", "init", "async_accounting"]
    # )
    # def test_execute_accounting_async(self):
    #     """测试异步执行核算（跳过）"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-执行核算-异步任务发起")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         task_id = response.get("data", {}).get("taskId")
    #         a.json(response, "异步核算响应，任务ID: {}".format(task_id))
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

