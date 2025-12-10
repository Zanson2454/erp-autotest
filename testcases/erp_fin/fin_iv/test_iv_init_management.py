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
from utils.param_util import ParamUtil
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
    def test_initialize_configuration(self):
        """测试存货价值初始化配置"""
        try:
            api_path = self.get_api_path("存货核算初始化配置-初始化配置")
            params, url = self.get_api_params(api_path)
            
            # 根据curl请求，参数路径是 params.reuqest（注意拼写）
            # 需要传递的字段：comOrgId, ivType, periodHeadId, startPeriod, enableStatus等
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "ivType", "periodHeadId", "startPeriod", "enableStatus", 
                        "beginStatus", "initStatus", "accountingStatus", "accountStatus", 
                        "asyncExecutionStatus", "currentPeriod"], ["params", "reuqest"]
            )
            
            # 构造期间对象（简化版，只传id）
            period_head_obj = {"id": self.calendar_head_id} if self.calendar_head_id else None
            start_period_obj = {"id": self.calendar_item_id} if self.calendar_item_id else None
            
            # 构造组织对象（简化版，只传id）
            com_org_obj = {"id": self.com_org_id} if self.com_org_id else None
            
            set_dict = {
                "comOrgId": com_org_obj,
                "ivType": "PERIOD_METHOD", # 期间成本法  or CONTINUOUS_METHOD 永续成本法
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
            # 使用自定义路径 reuqest（注意拼写），而不是默认的 request
            ParamUtil.set_request_params(filtered_params, set_dict, path=["params", "reuqest"])
            # 调用前先删除初始化数据，防止触发唯一性校验
            self.db.delete(
                table="fin_iv_init_cf",  # 存货价值初始化配置表
                where="com_org_id = %s and iv_type = 'PERIOD_METHOD'",
                params=[self.com_org_id]
            )
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            self.init_config_id = response.get("data", {}).get("data", {}).get("id")
            
            
            response2 = self.http.post(url, json=filtered_params)
            err_code = response2.get("err", {}).get("code")
            self.assert_util.assert_by_operator(err_code, "=", "fin.iv.init.cf.company.already.initialized")
            
            
            a.json(filtered_params, "初始化配置请求")
            a.json(response, "初始化配置响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试分页数据",
        description="验证分页查询存货价值初始化配置表",
        severity="normal",
        file_level_order=2,
        tags=["iv", "init", "value", "paging"]
    )
    def test_paging_init_cf_data(self):
        """测试分页数据"""
        try:
            api_path = self.get_api_path("存货价值初始化配置表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            pageable = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pageable": pageable})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 分页查询不需要验证特定ID，只要返回数据即可
            records = response.get("data", {}).get("data", {}).get("data", [])
            total_count = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total_count, ">", 0, "总记录数应大于等于0")
         
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据ID查找数据",
        description="验证根据ID查找存货价值初始化配置表数据",
        severity="normal",
        file_level_order=3,
        tags=["iv", "init", "value", "find_by_id"]
    )
    def test_find_init_cf_by_id(self):
        """测试根据ID查找数据"""
        try:
            if not self.init_cf_id:
                self.test_initialize_configuration()
            
            api_path = self.get_api_path("存货价值初始化配置表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.init_cf_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            config_data = response.get("data", {}).get("data", {})
            assert config_data.get("id") == self.init_cf_id, "详情查询ID不匹配"
            
            a.json(response, "根据ID查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="存货核算初始化配置管理",
        title="测试执行初始化后处理-启用初始化配置",
        description="验证存货核算初始化配置执行后处理流程",
        severity="normal",
        file_level_order=4,
        tags=["iv", "init", "post_process"]
    )
    def test_execute_post_initialization(self):
        """测试执行初始化后处理"""
        try:
            if not self.init_config_id:
                self.test_initialize_configuration()
            
            api_path = self.get_api_path("存货核算初始化配置-执行初始化后处理流程")
            params, url = self.get_api_params(api_path)
            
            # 根据API配置，参数路径是 params.reuqest（注意拼写），参考 test_initialize_configuration
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "reuqest"]
            )
            set_dict = {"id": self.init_config_id}
            ParamUtil.set_request_params(filtered_params, set_dict, path=["params", "reuqest"])
            
            response = self.http.post(url, json=filtered_params)
            enableStatus = response.get("data", {}).get("data", {}).get("enableStatus")
            self.assert_util.assert_by_operator(enableStatus, "=", "ENABLED", "启用状态应为ENABLED")

            
            a.json(response, "初始化后处理响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="存货价值初始化配置表",
        title="测试根据公司组织查找数据",
        description="验证根据公司组织查找存货价值初始化配置表数据",
        severity="normal",
        file_level_order=5,
        tags=["iv", "init", "value", "find_by_com_org"]
    )
    def test_find_init_cf_by_com_org_id(self):
        """测试根据公司组织查找数据"""
        try:
            # 确保初始化配置已创建并启用（依赖 test_execute_post_initialization，file_level_order=4）
            # 
            # 说明：file_level_order 只能控制 pytest 的执行顺序，有以下局限性：
            # 1. 当只运行单个测试方法时（如 pytest test_xxx.py::TestClass::test_method），
            #    pytest 不会运行其他测试方法，file_level_order 不起作用
            # 2. 即使运行整个文件，如果前面的测试失败，后面的测试仍会执行，但状态可能不正确
            # 3. 查询接口可能要求配置必须是 ENABLED 状态，而不仅仅是存在
            # 
            # 因此，需要在测试方法中显式检查和调用依赖方法，确保状态正确
            if not self.init_config_id:
                self.test_initialize_configuration()
                self.test_execute_post_initialization()
            
            api_path = self.get_api_path("存货价值初始化配置表-根据公司组织查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId"], ["params", "request"]
            )
            set_dict = {"comOrgId": {"id": self.com_org_id}}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "根据公司组织查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
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
    #     title="测试根据ID删除数据",
    #     description="验证根据ID删除存货价值初始化配置表数据",
    #     severity="normal",
    #     order=6,
    #     tags=["iv", "init", "value", "delete"]
    # )
    # def test_delete_init_cf_by_id(self):
    #     """测试根据ID删除数据"""
    #     try:
    #         if not self.init_cf_id:
    #             self.test_save_init_cf_data()
            
    #         api_path = self.get_api_path("存货价值初始化配置表-根据ID删除数据服务")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["id"], ["params", "request"]
    #         )
    #         set_dict = {"id": self.init_cf_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 验证删除
    #         self.init_cf_id = None  # 重置ID
    #         a.json(filtered_params, "删除请求数据")
    #         a.json(response, "删除响应数据")
            
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
    #     title="测试期初确认",
    #     description="验证存货核算初始化配置期初确认功能",
    #     severity="critical",
    #     order=10,
    #     tags=["iv", "init", "confirm"]
    # )
    # def test_confirm_begin(self):
    #     """测试期初确认"""
    #     try:
    #         # 准备测试数据  
    #         config_code = self.mock_util.generate_unique_code(tag="AT_IV_INIT")
    #         config_name = f"初始化配置_{self.mock_util.get_timestamp()}"
            
    #         # 调用API
    #         api_path = self.get_api_path("存货核算初始化配置-期初确认")
    #         params, url = self.get_api_params(api_path)
            
    #         # 参数处理
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["comOrgId", "invOrgId", "configCode"], ["params", "request"]
    #         )
    #         set_dict = {
    #             "comOrgId": self.com_org_id,
    #             "invOrgId": self.inv_org_id,
    #             "configCode": config_code
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         # 发送请求和断言
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 保存数据和报告
    #         self.init_config_id = response.get("data", {}).get("data", {})
    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试执行初始化",
    #     description="验证存货核算初始化配置执行初始化功能",
    #     severity="critical",
    #     order=11,
    #     tags=["iv", "init", "execute"]
    # )
    # def test_execute_initialization(self):
    #     """测试执行初始化"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         # 调用API
    #         api_path = self.get_api_path("存货核算初始化配置-执行初始化-无事务")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(response, "执行初始化响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试期初反确认",
    #     description="验证存货核算初始化配置期初反确认功能",
    #     severity="critical",
    #     order=12,
    #     tags=["iv", "init", "reverse_confirm"]
    # )
    # def test_reverse_confirm_begin(self):
    #     """测试期初反确认"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-期初反确认")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         a.json(response, "期初反确认响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试反初始化",
    #     description="验证存货核算初始化配置反初始化功能",
    #     severity="critical",
    #     order=13,
    #     tags=["iv", "init", "reverse_init"]
    # )
    # def test_reverse_initialization(self):
    #     """测试反初始化"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-反初始")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(response, "反初始化响应")
            
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
    #     story="存货核算初始化配置管理",
    #     title="测试反启用配置",
    #     description="验证存货核算初始化配置反启用功能",
    #     severity="normal",
    #     order=16,
    #     tags=["iv", "init", "disable"]
    # )
    # def test_disable_configuration(self):
    #     """测试反启用配置"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-反启用配置")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         a.json(response, "反启用配置响应")
            
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
    #     order=18,
    #     tags=["iv", "init", "accounting"]
    # )
    # def test_execute_accounting(self):
    #     """测试执行核算"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-执行核算-无事务")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         a.json(response, "执行核算响应")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    
    
    # @pytest.mark.skip(reason="异步任务发起需要监控任务状态，复杂度较高")
    # @case_decorator(
    #     story="存货核算初始化配置管理",
    #     title="测试异步执行初始化",
    #     description="验证存货核算初始化配置异步执行初始化功能",
    #     severity="normal",
    #     order=20,
    #     tags=["iv", "init", "async"]
    # )
    # def test_execute_initialization_async(self):
    #     """测试异步执行初始化（跳过）"""
    #     try:
    #         if not self.init_config_id:
    #             self.test_confirm_begin()
            
    #         api_path = self.get_api_path("存货核算初始化配置-执行初始化-异步任务发起")
    #         params, url = self.get_api_params(api_path)
            
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["configId"], ["params", "request"]
    #         )
    #         set_dict = {"configId": self.init_config_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
            
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 实际实现中需添加任务状态轮询
    #         task_id = response.get("data", {}).get("taskId")
    #         a.json(response, "异步初始化响应，任务ID: {}".format(task_id))
            
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

