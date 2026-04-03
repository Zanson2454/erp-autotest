# -*- coding: utf-8 -*-
"""
应付结账&反结账管理测试用例
包含：
1. 分页查询应付结账数据
2. 执行应付结账
3. 分页查询应付反结账数据（结账后的数据会进入反结账列表）
4. 执行应付反结账
前置条件：应付初始化配置已经执行初始化
"""

import allure

from testcases.erp_fin.fin_ap import ApBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付结账&反结账管理")
class TestApClosingManagement(ApBaseTest):
    """应付结账&反结账管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("应付结账&反结账管理测试类初始化完成")
        
        # 前置条件检查：确保应付初始化配置已经执行初始化
        if not cls.ap_init_id:
            cls.logger.warning("⚠️ ap_init_id 未初始化，请确保应付初始化配置已执行初始化")
        else:
            cls.logger.info(f"✅ 应付初始化配置已初始化，ID: {cls.ap_init_id}")
            
        cls.gfc_type_id = None
        cls.reverse_closing_id = None
        cls.reverse_closing_start_date = None
        cls.reverse_closing_end_date = None
        cls.closing_start_date = None
        cls.closing_end_date = None
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 结账数据通常不需要清理，因为它们是业务数据
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="应付结账&反结账管理",
        title="测试分页查询应付结账数据",
        description="验证分页查询应付结账数据功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["ap", "closing", "paging"]
    )
    def test_paging_closing_data(self):
        """测试分页查询应付结账数据"""
        try:
            # 前置条件检查：确保应付初始化配置已经执行初始化
            if not self.ap_init_id:
                raise ValueError("ap_init_id 未初始化，请确保应付初始化配置已执行初始化")
            
            # 使用标准化API调用
            # 根据curl命令，提取params.request内部的字段作为set_dict的根
            # 移除平台噪音字段：sceneKey, viewKey, appId, teamId, serviceKey
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "moduleCode": "AP",
                "processType": "CLOSING",
                "comOrg": None
            }
            
            response, _ = self.standard_api_call(
                api_key="财务域通用模块结账/反结账表-分页数据服务_PmHKWs1",
                set_dict=set_dict,
                store_id_as=None,
                query_params="tmodule=ERP_FIN"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty", "没有查询到应付结账数据,检查初始化是否成功")
            
            # 获取第一条数据的ID和状态
            if data_list and len(data_list) > 0:
                process_type = data_list[0].get("processType")
                com_org_id = data_list[0].get("comOrg").get("id")
                self.close_start_date = data_list[0].get("startDate")
                self.close_end_date = data_list[0].get("endDate")
                self.assert_util.assert_by_operator(process_type, "=", "CLOSING", "结账状态错误")
                self.assert_util.assert_by_operator(com_org_id, "=", self.gr_com_org_id, "公司组织ID错误")
                self.gfc_type_id = data_list[0].get("id")
            
           
            
            # 记录关键数据
            a.json(response, "分页查询响应数据")
            a.text(f"✅ 查询成功，共返回 {len(data_list)} 条记录", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付结账&反结账管理",
        title="测试应付结账",
        description="验证应付结账功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["ap", "closing", "execute"]
    )
    def test_execute_closing(self):
        """测试应付结账"""
        try:
            # 确保已查询到结账数据（获取gfc_type_id）
            if not self.gfc_type_id:
                self._ensure_paging_closing_data()
            
            # 使用标准化API调用
            # 根据curl命令，提取params.request内部的字段作为set_dict的根
            # 移除平台噪音字段：sceneKey, viewKey, viewTitle, buttonKey, buttonName, appId, teamId, serviceKey
            # comOrg对象只保留id字段
            set_dict = {
                "id": self.gfc_type_id,
                "moduleCode": "AP",
                "comOrg": {"id": self.gr_com_org_id},
                "processType": "CLOSING",
                "startDate": self.close_start_date,
                "endDate": self.close_end_date
            }
            
            response, _ = self.standard_api_call(
                api_key="FIN-结账模块-结账服务",
                set_dict=set_dict,
                store_id_as=None,
                query_params="tmodule=ERP_FIN"
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "结账响应数据")
            a.text(f"✅ 结账成功，结账ID: {self.gfc_type_id}", "结账结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付结账&反结账管理",
        title="测试分页查询应付反结账数据",
        description="验证分页查询应付反结账数据功能，当应付结账后，结账当月的数据会进入应付反结账列表",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["ap", "reverse_closing", "paging"]
    )
    def test_paging_reverse_closing_data(self):
        """测试分页查询应付反结账数据"""
        try:
            # 前置条件：需要先执行结账操作，结账后的数据才会进入反结账列表
            # 检查是否已执行结账，如果没有则先执行结账
            if not self.gfc_type_id:
                self._ensure_execute_closing()
            
            # 使用标准化API调用
            # 根据curl命令，提取params.request内部的字段作为set_dict的根
            # 移除平台噪音字段：sceneKey, viewKey, appId, teamId, serviceKey
            # 关键区别：processType 从 "CLOSING" 变为 "CLOSED"
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "moduleCode": "AP",
                "processType": "CLOSED",
                "comOrg": None
            }
            
            response, _ = self.standard_api_call(
                api_key="财务域通用模块结账/反结账表-分页数据服务_PmHKWs1",
                set_dict=set_dict,
                store_id_as=None,
                query_params="tmodule=ERP_FIN"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(
                data_list, "not_empty", 
                "没有查询到应付反结账数据，请确保已执行结账操作"
            )
            
            # 获取第一条数据的ID和状态
            if data_list and len(data_list) > 0:
                first_item = data_list[0]
                process_type = first_item.get("processType")
                com_org = first_item.get("comOrg")
                
                # 验证反结账状态
                self.assert_util.assert_by_operator(
                    process_type, "=", "CLOSED", 
                    "反结账状态错误，应为CLOSED"
                )
                
                # 验证公司组织ID
                if com_org:
                    com_org_id = com_org.get("id")
                    self.assert_util.assert_by_operator(
                        com_org_id, "=", self.gr_com_org_id, 
                        "公司组织ID错误"
                    )
                
                # 保存反结账ID（用于后续反结账操作）
                self.reverse_closing_id = first_item.get("id")
            
            # 记录关键数据
            a.json(response, "反结账列表查询响应数据")
            a.text(
                f"✅ 反结账列表查询成功，共返回 {len(data_list)} 条记录\n"
                f"说明：当应付结账后，结账当月的数据会进入应付反结账列表",
                "查询结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付结账&反结账管理",
        title="测试应付反结账",
        description="验证应付反结账功能",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["ap", "reverse_closing", "execute"]
    )
    def test_execute_reverse_closing(self):
        """测试应付反结账"""
        try:
            # 前置条件：需要先查询反结账列表（获取reverse_closing_id）
            if not self.reverse_closing_id:
                self._ensure_paging_reverse_closing_data()
            
            # 检查依赖数据
            if not self.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")
            
            # 使用标准化API调用
            # 根据curl命令，提取params.request内部的字段作为set_dict的根
            # 移除平台噪音字段：sceneKey, viewKey, viewTitle, buttonKey, buttonName, appId, teamId, serviceKey
            # comOrg对象只保留id字段
            # 关键区别：processType 为 "CLOSED"
            set_dict = {
                "id": self.reverse_closing_id,
                "moduleCode": "AP",
                "comOrg": {"id": self.gr_com_org_id},
                "processType": "CLOSED",
                "startDate": self.reverse_closing_start_date,
                "endDate": self.reverse_closing_end_date
            }
            
            response, _ = self.standard_api_call(
                api_key="FIN-结账模块-反结账服务",
                set_dict=set_dict,
                store_id_as=None,
                query_params="tmodule=ERP_FIN"
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 记录关键数据
            a.json(response, "反结账响应数据")
            a.text(f"✅ 反结账成功，反结账ID: {self.reverse_closing_id}", "反结账结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        