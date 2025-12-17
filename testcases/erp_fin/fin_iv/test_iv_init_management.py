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
    
    init_cf_id = None
    init_config_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.init_cf_id = None
        cls.init_config_id = None
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
            # cls.db.delete(
            #     table="fin_iv_init_cf",  # 存货价值初始化配置表
            #     where="com_org_id = %s and iv_type = 'PERIOD_METHOD'",
            #     params=[cls.com_org_id]
            # )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试初始化配置",
        description="验证存货核算初始化配置初始化功能",
        severity="normal",
        file_level_order=1,
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
                com_org_obj =   {"id": self.gr_com_org_id}
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
            
            fields_to_filter = ["comOrgId", "ivType", "periodHeadId", "startPeriod", "enableStatus", "beginStatus", "initStatus", "accountingStatus", "accountStatus", "asyncExecutionStatus", "asyncExecutionFailureReason", "currentPeriod"]
            
            # 调用前先删除初始化数据，防止触发唯一性校验
            self.db.delete(
                table="fin_iv_init_cf",
                where="com_org_id = %s and iv_type = %s",
                params=[com_org_obj.get("id"), iv_type]
            )
            
            # 注意：接口定义中参数路径写错了（reuqest应该是request），使用param_path参数处理
            response, extracted_id = self.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="init_cf",  # 存储初始化配置ID
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            
            # 业务断言
            self.assert_util.assert_by_operator(extracted_id, "not_empty", "初始化配置ID为空")
            
            # 验证重复初始化会报错
            response2, _ = self.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,  # 不存储ID
                param_path=["params", "reuqest"]  # 使用reuqest路径
            )
            err_code = response2.get("err", {}).get("code")
            err_msg = response2.get("err", {}).get("msg")
            self.assert_util.assert_by_operator(err_code, "=", "fin.iv.init.cf.company.already.initialized", "错误代码应为fin.iv.init.cf.company.already.initialized")
            self.assert_util.assert_by_operator(err_msg, "=", "公司组织已初始化，请勿重复初始化", "业务提示应为公司组织已初始化，请勿重复初始化")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID删除数据",
        description="验证根据ID删除存货价值初始化配置表数据",
        severity="normal",
        file_level_order=2,
        tags=["iv", "init", "value", "delete"]
    )
    def test_delete_init_cf_by_id(self):
        """测试根据ID删除数据"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            set_dict = {"id": self.init_cf_id}
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
        file_level_order=3,
        tags=["iv", "init", "value", "paging"]
    )
    def test_paging_init_cf_data(self):
        """测试分页数据"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
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
            
            # 验证总记录数
            total_count = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID查找数据",
        description="验证根据ID查找存货价值初始化配置表数据",
        severity="normal",
        file_level_order=4,
        tags=["iv", "init", "value", "find_by_id"]
    )
    def test_find_init_cf_by_id(self):
        """测试根据ID查找数据"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            
            # 使用标准化API调用
            set_dict = {"id": self.init_cf_id}
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
            self.assert_util.assert_by_operator(config_data.get("id"), "=", self.init_cf_id, "详情查询ID不匹配")
            
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
        file_level_order=5,
        tags=["iv", "init", "post_process"]
    )
    def test_execute_post_initialization(self):
        """测试执行初始化后处理"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
            

            set_dict = {"id": self.init_cf_id}
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
        file_level_order=6,
        tags=["iv", "init", "disable"]
    )
    def test_disable_configuration(self):
        """测试反启用配置"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD"  )
                self.test_execute_post_initialization()
            
            set_dict = {"id": self.init_cf_id}
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
        file_level_order=7,
        tags=["iv", "init", "confirm"]
    )
    def test_confirm_begin(self):
        """测试期初确认"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_initialize_configuration(iv_type="CONTINUOUS_METHOD")
                self.test_execute_post_initialization()
            
            
            set_dict = {"id": self.init_cf_id}
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
        file_level_order=8,
        tags=["iv", "init", "reverse_confirm"]
    )
    def test_reverse_confirm_begin(self):
        """测试期初反确认"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_confirm_begin()
            
            # 使用use_param_util=False手动构造参数（因为需要reuqest路径）
            set_dict = {"id": self.init_cf_id}
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
        title="测试异步执行初始化",
        description="验证存货核算初始化配置异步执行初始化功能",
        severity="normal",
        file_level_order=10,
        tags=["iv", "init", "async"]
    )
    def test_execute_initialization_async(self):
        """测试异步执行初始化"""
        try:
            # 检查并创建依赖数据
            if not self.init_cf_id:
                self.test_confirm_begin()
            
            # 使用use_param_util=False手动构造参数（因为需要reuqest路径）
            set_dict = {"id": self.init_cf_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-执行初始化-异步任务发起",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            self.assert_util.assert_response_success(response)
            
            # 实际实现中需添加任务状态轮询
            task_id = response.get("data", {}).get("taskId")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试根据公司组织查找数据",
    #     description="验证根据公司组织查找存货价值初始化配置表数据",
    #     severity="normal",
    #     file_level_order=6,
    #     tags=["iv", "init", "value", "find_by_com_org"]
    # )
    # def test_find_init_cf_by_com_org_id(self):
    #     """测试根据公司组织查找数据"""
    #     try:
    #         # 确保初始化配置已创建并启用
    #         if not self.init_config_id:
    #             self.test_initialize_configuration()
    #             self.test_execute_post_initialization()
            
    #         # 使用标准化API调用
    #         set_dict = {"comOrgId": {"id": self.com_org_id}}
    #         fields_to_filter = ["comOrgId"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货价值初始化配置表-根据公司组织查找数据服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    

        
        
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试更新数据",
    #     description="验证更新存货价值初始化配置数据",
    #     severity="normal",
    #     order=5,
    #     tags=["iv", "init", "value", "update"]
    # )
    # def test_update_init_cf_data(self):
    #     """测试更新数据"""
    #     try:
    #         if not self.init_cf_id:
    #             self.test_save_init_cf_data()
            
    #         new_name = f"更新配置_{self.mock_util.get_timestamp()}"
    #         new_remark = self.mock_util.get_mock_remark()
            
    #         api_path = self.get_api_path("存货价值初始化配置表-保存数据服务")  # 更新也用save
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["id", "name", "remark"], ["params", "request"]
    #         )
    #         set_dict = {
    #             "id": self.init_cf_id,
    #             "name": new_name,
    #             "remark": new_remark
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         # 验证更新
    #         find_params, find_url = self.get_api_params(self.get_api_path("存货价值初始化配置表-根据ID查找数据服务"))
    #         find_dict = {"id": self.init_cf_id}
    #         filtered_find = ParamUtil.filter_post_body_fields(find_params, ["id"], ["params", "request"])
    #         ParamUtil.set_request_params(filtered_find, find_dict)
    #         updated_response = self.http.post(find_url, json=filtered_find)
    #         updated_data = updated_response.get("data", {}).get("data", {})
    #         assert updated_data.get("name") == new_name, "更新名称不匹配"
            
    #         a.json(filtered_params, "更新请求数据")
    #         a.json(response, "更新响应数据")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
   
    
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试批量删除数据",
    #     description="验证批量删除存货价值初始化配置表数据",
    #     severity="normal",
    #     order=7,
    #     tags=["iv", "init", "value", "batch_delete"]
    # )
    # def test_batch_delete_init_cf(self):
    #     """测试批量删除数据"""
    #     try:
    #         # 创建多个数据用于批量删除
    #         ids_to_delete = []
    #         for _ in range(2):
    #             temp_code = self.mock_util.generate_unique_code(tag="AT_IV_BATCH")
    #             temp_name = f"批量删除测试_{self.mock_util.get_timestamp()}"
    #             save_api_path = self.get_api_path("存货价值初始化配置表-保存数据服务")
    #             save_params, save_url = self.get_api_params(save_api_path)
    #             filtered_save = ParamUtil.filter_post_body_fields(save_params, ["comOrgId", "code", "name"], ["params", "request"])
    #             set_save_dict = {
    #                 "comOrgId": self.com_org_id,
    #                 "code": temp_code,
    #                 "name": temp_name
    #             }
    #             ParamUtil.set_request_params(filtered_save, set_save_dict)
    #             temp_response = self.http.post(save_url, json=filtered_save)
    #             self.assert_util.assert_response_data(temp_response)
    #             temp_id = temp_response.get("data", {}).get("data", {}).get("id")
    #             if temp_id:
    #                 ids_to_delete.append(temp_id)
            
    #         api_path = self.get_api_path("存货价值初始化配置表-批量删除数据服务")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["ids"], ["params", "request"]
    #         )
    #         set_dict = {"ids": ids_to_delete}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         a.json(filtered_params, "批量删除请求")
    #         a.json(response, "批量删除响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试复制数据转换服务",
    #     description="验证存货价值初始化配置表复制数据转换功能",
    #     severity="normal",
    #     order=8,
    #     tags=["iv", "init", "value", "copy"]
    # )
    # def test_copy_data_converter(self):
    #     """测试复制数据转换服务"""
    #     try:
    #         if not self.init_cf_id:
    #             self.test_save_init_cf_data()
            
    #         api_path = self.get_api_path("存货价值初始化配置表-复制数据转换服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 复制服务通常需要源ID参数，这里使用已保存的配置ID作为源
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["id"], ["params", "request"]
    #         )
    #         set_dict = {"id": self.init_cf_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(filtered_params, "复制数据转换请求")
    #         a.json(response, "复制数据转换响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货价值初始化配置表",
    #     title="测试复制数据转换子服务",
    #     description="验证存货价值初始化配置表复制数据转换子服务功能",
    #     severity="normal",
    #     order=9,
    #     tags=["iv", "init", "value", "copy_child"]
    # )
    # def test_copy_data_converter_child(self):
    #     """测试复制数据转换子服务"""
    #     try:
    #         if not self.init_cf_id:
    #             self.test_save_init_cf_data()
            
    #         api_path = self.get_api_path("存货价值初始化配置表-复制数据转换子服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 复制子服务通常需要源ID参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["id"], ["params", "request"]
    #         )
    #         set_dict = {"id": self.init_cf_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(filtered_params, "复制数据转换子服务请求")
    #         a.json(response, "复制数据转换子服务响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # # ==================== 存货核算初始化配置相关测试 ====================
    

    

        
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试执行初始化",
    #     description="验证存货核算初始化配置执行初始化功能",
    #     severity="critical",
    #     file_level_order=12,
    #     tags=["iv", "init", "execute"]
    # )
    # @pytest.mark.skip(reason="实际无调用",description="代码内部处理事务，服务不需要加锁")
    # def test_execute_initialization(self):
    #     """测试执行初始化"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         # 使用标准化API调用
    #         set_dict = {"configId": self.init_config_id}
    #         fields_to_filter = ["configId"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算初始化配置-执行初始化-无事务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    

    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试反初始化",
    #     description="验证存货核算初始化配置反初始化功能",
    #     severity="critical",
    #     file_level_order=13,
    #     tags=["iv", "init", "reverse_init"]
    # )
    # def test_reverse_initialization(self):
    #     """测试反初始化"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
    #             self.test_execute_post_initialization()
            
    #         # 使用标准化API调用
    #         set_dict = {"configId": self.init_config_id}
    #         fields_to_filter = ["configId"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算初始化配置-反初始",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试结账",
    #     description="验证存货核算初始化配置结账功能",
    #     severity="critical",
    #     order=14,
    #     tags=["iv", "init", "close"]
    # )
    # def test_close_account(self):
    #     """测试结账"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-结账")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         a.json(response, "结账响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
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
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试执行核算",
    #     description="验证存货核算初始化配置执行核算功能",
    #     severity="critical",
    #     file_level_order=11,
    #     tags=["iv", "init", "accounting"]
    # )
    # def test_execute_accounting(self):
    #     """测试执行核算"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.init_config_id:
    #             self.test_initialize_configuration()
    #             self.test_execute_post_initialization()
            
    #         # 使用标准化API调用
    #         set_dict = {"id": self.init_config_id}
    #         fields_to_filter = ["id"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算初始化配置-执行核算-无事务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
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

