# -*- coding: utf-8 -*-
"""
应付初始化管理测试用例
包含：财务域通用模块初始化表管理、应付初始化管理
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付初始化管理")
class TestApInitManagement(FinBaseTest):
    """应付初始化管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        # ap_init_id 已在 ApBaseTest.setup_class() 中初始化（如果实现了自动初始化）
        # 如果未实现自动初始化，则初始化为 None
        if not hasattr(cls, 'ap_init_id'):
            cls.ap_init_id = None
        cls.logger.info("应付初始化管理测试类初始化完成")
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.ap_init_id:
                pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="应付初始化管理",
        title="测试初始化配置",
        description="验证应付初始化管理初始化功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["ap", "init", "initialize"]
    )
    def test_initialize_configuration(self):
        """测试应付初始化配置"""
        try:
            # 检查依赖数据
            if not self.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备初始化参数
            com_org_obj = {"id": self.gr_com_org_id}  # 使用 gr_com_org_id
            start_date = self.mock_util.get_timestamp(timestamp=True)
            
            # 调用前先删除初始化数据，防止触发唯一性校验
            self.db.delete(
                table="fin_gen_im_head_tr",
                where="com_org = %s and module_code = %s",
                params=[self.gr_com_org_id, "AP"]
            )
            
            # 步骤1：先保存数据到 fin_gen_im_head_tr 表
            # 注意：初始化服务要求表中必须先有记录，所以需要先调用保存接口
            save_set_dict = {
                "moduleCode": "AP",
                "comOrg": com_org_obj,
                "startDate": start_date,
                "initialBalanceType": "UNRECORDED",
                "startType": "DISABLED",
                "initializationType": "UNINITIALIZED"
            }
        
            
            save_response, saved_id = self.standard_api_call(
                api_key="财务域通用模块初始化表-保存数据服务",
                set_dict=save_set_dict,
                store_id_as="ap_init",
                query_params="modelKey=ERP_FIN$fin_gen_im_head_tr"
            )
            
            self.assert_util.assert_response_data(save_response)
            
            # 记录关键数据
            a.json(save_response, "初始化响应数据")
            a.text(f"✅ 初始化成功，初始化配置ID: {self.ap_init_id}", "初始化结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试重复初始化配置报错",
        description="验证重复初始化配置会返回错误",
        severity="normal",
        file_level_order=2,
        tags=["ap", "init", "initialize", "duplicate_error"]
    )
    def test_initialize_configuration_duplicate_error(self):
        """测试重复初始化配置报错"""
        try:
            # 确保已创建初始化配置
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            # 检查依赖数据
            if not self.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")
            
            com_org_obj = {"id": self.gr_com_org_id}
            start_date = self.mock_util.get_timestamp(timestamp=True)
            
            set_dict = {
                "moduleCode": "AP",
                "comOrg": com_org_obj,
                "startDate": start_date,
                "initialBalanceType": "UNRECORDED",
                "startType": "DISABLED",
                "initializationType": "UNINITIALIZED"
            }
            
            # 验证重复保存会报错（使用相同的 moduleCode 和 comOrg）
            response, _ = self.standard_api_call(
                api_key="财务域通用模块初始化表-保存数据服务",
                set_dict=set_dict,
                store_id_as=None,
                query_params="modelKey=ERP_FIN$fin_gen_im_head_tr"
            )
            
            # 业务断言：验证错误响应
            # 根据终端输出，错误码应该是 "M1017"，错误信息包含"数据已存在"
            err_code = response.get("err", {}).get("code")
            err_msg = response.get("err", {}).get("msg")
            
            # 验证错误码
            self.assert_util.assert_by_operator(
                err_code, "=", "M1017",
                f"错误码应为M1017，实际: {err_code}"
            )
            
            # 验证错误信息包含"数据已存在"
            self.assert_util.assert_by_operator(
                err_msg, "contain", "数据已存在",
                f"错误信息应包含'数据已存在'，实际: {err_msg}"
            )
            
            # 记录关键数据
            a.json(response, "重复保存错误响应")
            a.text(f"✅ 重复保存正确返回错误，错误码: {err_code}, 错误信息: {err_msg}", "错误验证结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试启用初始化配置",
        description="验证应付初始化管理启用功能",
        severity="normal",
        file_level_order=3,
        tags=["ap", "init", "enable"]
    )
    def test_enable_configuration(self):
        """测试启用初始化配置"""
        try:
            # 确保已创建初始化配置
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            set_dict = {
                "id": self.ap_init_id
            }
            
            response, _ = self.standard_api_call(
                api_key="IM-财务初始化管理-启用服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言（只验证响应成功，不校验状态）
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "启用响应数据")
            a.text(f"✅ 启用成功", "启用结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试反启用配置",
        description="验证应付初始化管理反启用功能",
        severity="normal",
        file_level_order=4,
        tags=["ap", "init", "disable"]
    )
    def test_disable_configuration(self):
        """测试反启用配置"""
        try:
            # 确保已创建并启用初始化配置
            if not self.ap_init_id:
                self.test_enable_configuration()
            
            
            set_dict = {
               "id": self.ap_init_id
            }

            response, _ = self.standard_api_call(
                api_key="IM-财务初始化管理-反启用服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言（只验证响应成功，不校验状态）
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "反启用响应数据")
            a.text(f"✅ 反启用成功", "反启用结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试异步执行初始化并等待完成",
        description="验证应付初始化管理异步执行初始化功能，并等待异步任务完成",
        severity="critical",
        file_level_order=5,
        tags=["ap", "init", "im_initialization", "async", "wait"]
    )
    def test_im_initialization(self):
        """
        测试异步执行初始化并等待完成
        
        测试流程：
        1. 发起异步初始化任务
        2. 验证任务已创建（如果接口返回状态）
        3. 轮询查询任务状态，等待任务完成
        4. 验证初始化状态
        
        业务说明：
        - 应付初始化可能是一个异步任务，需要等待后台处理完成
        - 初始化状态流转：UNINITIALIZED -> INITIALIZED（成功时）
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保初始化配置已创建并启用，否则先执行前置用例
            if not self.ap_init_id:
                self.test_enable_configuration()
            
            # 检查依赖数据
            if not self.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")
            
            # ========== 步骤1：发起异步初始化任务 ==========
            # 调用初始化服务，触发后台初始化处理
            # 该接口可能立即返回，也可能返回异步任务状态
            com_org_obj = {"id": self.gr_com_org_id}
            start_date = self.mock_util.get_timestamp(timestamp=True)
            
            set_dict = {
                "id": self.ap_init_id,
                "moduleCode": "AP", 
                "initialBalanceType": "UNRECORDED",
                "initializationType": "UNINITIALIZED",
                "startDate": start_date,
                "startType": "ENABLED",
                "comOrg": com_org_obj
            }
            
            response, _ = self.standard_api_call(
                api_key="IM-财务初始化管理-初始化服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # ========== 步骤2：定义查询函数 ==========
            # 定义查询函数，用于轮询检查初始化配置的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            def query_init_status():
                """
                查询初始化配置状态
                
                功能说明：
                - 调用查询详情接口，获取初始化配置的当前状态
                - 返回的数据包含初始化业务状态
                
                返回数据字段说明：
                - initializationType: 初始化业务状态
                  * UNINITIALIZED: 未初始化
                  * INITIALIZED: 初始化完成
                
                返回：
                    dict: 包含初始化配置的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="财务域通用模块初始化表-根据ID查找数据服务",
                    set_dict={"id": self.ap_init_id},
                    store_id_as=None,
                    query_params="modelKey=ERP_FIN$fin_gen_im_head_tr"
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤3：等待初始化完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            # 注意：如果初始化服务是同步的，可能需要调整等待逻辑
            # 这里使用 initializationType 字段来判断初始化是否完成
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_init_status,  # 查询函数，每次轮询时调用
                status_field="initializationType",  # 要检查的状态字段名
                success_status="INITIALIZED",  # 成功状态值，达到此状态时停止等待
                failed_status=None,  # 失败状态值（如果初始化服务有失败状态，可以设置）
                failure_reason_field=None,  # 失败原因字段名（如果初始化服务有失败原因字段，可以设置）
                max_wait=60,  # 最大等待时间（秒），初始化可能需要较长时间
                interval=2  # 轮询间隔（秒），每2秒查询一次状态
            )
            
            # ========== 步骤4：断言等待结果 ==========
            # 根据等待结果进行断言验证
            if result.status == self.wait_status.SUCCESS:
                # 等待成功，验证业务状态
                
                # 4.1 验证初始化状态
                # 初始化成功后，initializationType应该从UNINITIALIZED变为INITIALIZED
                initialization_type = result.last_data.get("initializationType")
                self.assert_util.assert_by_operator(
                    initialization_type, "=", "INITIALIZED",
                    f"初始化任务应成功完成，initializationType应为INITIALIZED，实际状态: {initialization_type}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 初始化任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"初始化状态: {initialization_type}",
                    "任务完成"
                )
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步初始化任务失败: {failure_reason}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后数据: {result.last_data}"
                )
            elif result.status == self.wait_status.TIMEOUT:
                # 等待超时，抛出异常
                raise AssertionError(
                    f"⚠️ 等待异步初始化任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('initializationType') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                raise AssertionError(
                    f"等待异步初始化任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
                
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            a.text(str(e), "失败原因")
            raise
        

    
    
    @case_decorator(
        story="应付初始化管理",
        title="测试反初始化",
        description="验证应付初始化管理反初始化功能",
        severity="critical",
        file_level_order=6,
        tags=["ap", "init", "reverse_init"]
    )
    def test_reverse_initialization(self):
        """测试反初始化"""
        try:
            # 确保已创建初始化配置
            if not self.ap_init_id:
                self.test_im_initialization()
            
            set_dict = {
                "id": self.ap_init_id,
                "initialBalanceType": "UNRECORDED",
                "initializationType": "INITIALIZED",    
                "moduleCode": "AP",
                "startDate": self.mock_util.get_timestamp(timestamp=True),
                "startType": "ENABLED",
                "comOrg":{"id":self.gr_com_org_id }
            }
            
            response, _ = self.standard_api_call(
                api_key="IM-财务初始化管理-反初始化服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "反初始化响应数据")
            a.text(f"✅ 反初始化成功", "反初始化结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试分页查询初始化配置",
        description="验证分页查询应付初始化管理数据",
        severity="normal",
        file_level_order=6,
        tags=["ap", "init", "paging"]
    )
    def test_paging_init_data(self):
        """测试分页查询初始化配置"""
        try:
            # 检查并创建依赖数据
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            # 使用标准化API调用（根据模块代码分页查询）
            # 注意：根据curl命令，pageable中包含systemParams.viewCondition
            set_dict = {
                "moduleCode": "AP",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "systemParams": {
                        "viewCondition": {
                            "conditionKey": None,
                            "rightValues": {}
                        }
                    }
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="财务域通用模块初始化表-分页数据服务_PmHKWs1_copy",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty", "没有进行应付初始化")
            
            # 记录关键数据
            a.json(response, "分页查询响应数据")
            a.text(f"✅ 查询成功，共返回 {len(data_list)} 条记录", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付初始化管理",
        title="测试根据ID查找数据",
        description="验证根据ID查找应付初始化管理数据",
        severity="normal",
        file_level_order=7,
        tags=["ap", "init", "find_by_id"]
    )
    def test_find_init_data_by_id(self):
        """测试根据ID查找数据"""
        try:
            # 检查并创建依赖数据
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            # 使用标准化API调用
            # 注意：根据 curl 命令，id 参数是字符串类型
            set_dict = {"id": self.ap_init_id}
            
            response, _ = self.standard_api_call(
                api_key="财务域通用模块初始化表-根据ID查找数据服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            init_data = response.get("data", {}).get("data", {})
            if isinstance(init_data, dict):
                self.assert_util.assert_by_operator(
                    init_data.get("id"), "=", self.ap_init_id,
                    "详情查询ID不匹配"
                )
                self.assert_util.assert_by_operator(
                    init_data.get("moduleCode"), "=", "AP",
                    "模块代码应为AP"
                )
            
            # 记录关键数据
            a.json(response, "详情查询响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="财务域通用模块初始化表",
        title="测试根据ID删除数据",
        description="验证根据ID删除财务域通用模块初始化表数据",
        severity="normal",
        file_level_order=9,
        tags=["ap", "init", "delete"]
    )
    def test_delete_init_data_by_id(self):
        """测试根据ID删除数据"""
        try:
            # 检查并创建依赖数据
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            set_dict = {"id": self.ap_init_id}
            
            # 单行删除接口需要 modelKey 查询参数
            response, _ = self.standard_api_call(
                api_key="财务域通用模块初始化表-根据ID删除数据服务",
                set_dict=set_dict,
                store_id_as=None,
                query_params="modelKey=ERP_FIN$fin_gen_im_head_tr"
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 清空ID，避免后续用例使用已删除的数据
            self.ap_init_id = None
            
            # 记录关键数据
            a.json(response, "删除响应数据")
            a.text(f"✅ 删除成功", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="财务域通用模块初始化表",
        title="测试批量删除数据",
        description="验证批量删除财务域通用模块初始化表数据",
        severity="normal",
        file_level_order=10,
        tags=["ap", "init", "batch_delete"]
    )
    def test_batch_delete_init_data(self):
        """测试批量删除数据"""
        try:
            # 创建多个数据用于批量删除
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            set_dict = {"ids": [self.ap_init_id]}
            
            response, _ = self.standard_api_call(
                api_key="财务域通用模块初始化表-批量删除数据服务",
                set_dict=set_dict,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "批量删除响应数据")
            a.text(f"✅ 批量删除成功", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="财务域通用模块初始化表",
        title="测试复制数据转换服务",
        description="验证财务域通用模块初始化表复制数据转换功能",
        severity="normal",
        file_level_order=11,
        tags=["ap", "init", "copy"]
    )
    def test_copy_data_converter(self):
        """测试复制数据转换服务"""
        try:
            if not self.ap_init_id:
                self.test_initialize_configuration()
            
            # 使用标准化API调用
            set_dict = {"id": self.ap_init_id}
            
            # 复制接口需要 modelKey 查询参数
            response, copied_id = self.standard_api_call(
                api_key="财务域通用模块初始化表-复制数据转换服务",
                set_dict=set_dict,
                store_id_as=None,
                query_params="modelKey=ERP_FIN$fin_gen_im_head_tr"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
           
            # 记录关键数据
            a.json(response, "复制响应数据")
            a.text(f"✅ 复制成功，新ID: {copied_id}", "复制结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    