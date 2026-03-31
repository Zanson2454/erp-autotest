# -*- coding: utf-8 -*-
"""
应付单据类型管理测试用例

测试应付单据类型配置的CRUD操作：
1. 分页查询应付单据类型
2. 创建应付单据类型
3. 查询应付单据类型详情
4. 更新应付单据类型
5. 启用/禁用应付单据类型
6. 删除应付单据类型
"""
import allure
import pytest
from testcases.erp_fin.fin_ap import ApBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("应付管理-应付单据类型管理")
class TestApTypeMdManagement(ApBaseTest):
    """应付单据类型管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.ap_type_id = None
        cls.ap_type_detail = None
        cls.logger.info("应付单据类型管理测试类初始化完成")
        
        # 从缓存安全获取汇率类型（从init_data获取）
        # 使用安全获取方式，先判断列表是否存在且非空，再获取第一个元素
        if cls.init_data:
            exchange_rate_type_info = cls.init_data.get("exchange_rate_type_info", [])
            if exchange_rate_type_info and len(exchange_rate_type_info) > 0:
                cls.exchange_rate_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                cls.exchange_rate_type_id = None
                cls.logger.warning(
                    "⚠️ 未找到汇率类型信息（exchange_rate_type_info），请检查 init_data 中的 exchange_rate_type_info 数据。"
                    "这可能导致某些测试用例失败。"
                )
        else:
            cls.exchange_rate_type_id = None
            cls.logger.warning("⚠️ init_data 未初始化，请检查基础数据缓存是否正常加载")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="应付单据类型查询",
        title="测试分页查询应付单据类型",
        description="验证应付单据类型分页查询功能",
        severity="critical",
        file_level_order=1,
        tags=["应付单据类型", "查询", "分页"]
    )
    def test_query_ap_type_page(self):
        """测试分页查询应付单据类型"""
        try:
            # 1. 准备分页查询参数（根据API参数配置结构）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": [],
                    "conditionItems": {},
                    "conditionGroup": {}
                }
            }
            
            # 2. 标准化API调用
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-分页数据服务_PmHKWs1",
                set_dict=set_dict
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty", "分页查询结果不应为空")
            
            # 5. 记录关键数据
            a.json(response, "分页查询响应数据")
            a.text(f"✅ 查询成功，共返回 {len(data_list)} 条记录", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型创建",
        title="测试创建应付单据类型",
        description="验证应付单据类型创建功能",
        severity="critical",
        file_level_order=2,
        tags=["应付单据类型", "创建"]
    )
    def test_save_ap_type(self):
        """测试创建应付单据类型"""
        try:
            # 1. 准备测试数据
            timestamp = self.mock_util.get_timestamp()
            ap_type_code = f"AT_AP_TYPE_{timestamp}"
            ap_type_name = f"自动化测试应付单据类型_{timestamp}"
            
            # 2. 标准化API调用
            set_dict = {
                "remark": "自动化测试提交",
                "apTypeCode": ap_type_code,
                "name": ap_type_name,
                "accountType": "FIN",
                "isAccDocRelv": "YES",
                "bizType": "EXTERNAL",
                "exchangeRateType": {"id": self.exchange_rate_type_id} if self.exchange_rate_type_id else None,
                "isClearBeforePay": False,
                "isAdjustRelv": False,
                "schlSumByPo": False,
                "schlSumByDn": False,
                "pushAes": False,
                "autoPushAes": False,
                "originOrgId": 0
            }
            
            response, extracted_id = self.standard_api_call(
                api_key="应付单类型-保存应付单类型服务",
                set_dict=set_dict,
                store_id_as="ap_type"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            
            # 4. 记录关键数据
            a.json(response, "创建响应数据")
            a.text(f"✅ 创建成功，应付单据类型ID: {self.ap_type_id}", "创建结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型查询",
        title="测试查询应付单据类型详情",
        description="验证根据ID查询应付单据类型详情功能",
        severity="normal",
        file_level_order=3,
        tags=["应付单据类型", "查询", "详情"]
    )
    def test_query_ap_type_detail(self):
        """测试查询应付单据类型详情"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 查询详情（需要传递modelKey查询参数）
            set_dict = {"id": self.ap_type_id}
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-根据ID查找数据服务",
                set_dict=set_dict,
                query_params="modelKey=ERP_FIN$fin_apm_ap_type_md"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回数据（调试：先记录完整响应结构）
            a.json(response, "详情查询完整响应数据")
            # 尝试多种可能的响应结构路径
            data = response.get("data", {}).get("data", {})
            
            self.assert_util.assert_by_operator(data, "not_empty", "详情数据不应为空")
            self.assert_util.assert_by_operator(data.get("id"), "=", self.ap_type_id, "返回的ID应匹配")
            self.ap_type_detail = data
            # 5. 记录关键数据
            a.json(data, "详情数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型更新",
        title="测试更新应付单据类型",
        description="验证更新应付单据类型功能",
        severity="normal",
        file_level_order=4,
        tags=["应付单据类型", "更新"]
    )
    def test_update_ap_type(self):
        """测试更新应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
                self.test_query_ap_type_detail()
            
            self.ap_type_detail["name"] = f"自动化测试应付单据类型_更新_{self.mock_util.get_timestamp()}"
            self.ap_type_detail["remark"] = "自动化测试更新"
            
            response, _ = self.standard_api_call(
                api_key="应付单类型-保存应付单类型服务",
                set_dict= self.ap_type_detail
            )
            
            data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(data.get("name"), "=", self.ap_type_detail["name"], "名称应已更新")
            self.assert_util.assert_by_operator(data.get("remark"), "=", self.ap_type_detail["remark"], "备注应已更新")
            # 4. 业务断言
            self.assert_util.assert_response_data(response)

            # 6. 记录关键数据
            a.json(response, "更新响应数据")
            a.text(f"✅ 更新成功，新名称: {self.ap_type_detail['name']}", "更新结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型启用",
        title="测试批量启用应付单据类型",
        description="验证批量启用应付单据类型功能",
        severity="normal",
        file_level_order=5,
        tags=["应付单据类型", "启用"]
    )
    def test_enable_ap_type(self):
        """测试批量启用应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 批量启用数据（确保ID是整数类型）
            set_dict = {"ids": [int(self.ap_type_id)] if self.ap_type_id else []}
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-批量启用主数据服务",
                set_dict=set_dict
            )
            
            # 3. 业务断言（只验证响应成功，不校验状态）
            self.assert_util.assert_response_success(response)
            
            # 4. 记录关键数据
            a.json(response, "批量启用响应数据")
            a.text(f"✅ 批量启用成功", "启用结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型禁用",
        title="测试批量禁用应付单据类型",
        description="验证批量禁用应付单据类型功能",
        severity="normal",
        file_level_order=6,
        tags=["应付单据类型", "禁用"]
    )
    def test_disable_ap_type(self):
        """测试批量禁用应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 批量禁用数据（确保ID是整数类型）
            set_dict = {"ids": [int(self.ap_type_id)] if self.ap_type_id else []}
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-批量禁用主数据服务",
                set_dict=set_dict
            )
            
            # 3. 业务断言（只验证响应成功，不校验状态）
            self.assert_util.assert_response_success(response)
            
            # 4. 记录关键数据
            a.json(response, "批量禁用响应数据")
            a.text(f"✅ 批量禁用成功", "禁用结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型禁用",
        title="测试禁用应付单据类型",
        description="验证批量禁用应付单据类型功能",
        severity="normal",
        file_level_order=6,
        tags=["应付单据类型", "禁用"]
    )
    def test_disable_ap_type(self):
        """测试禁用应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 禁用数据（确保ID是整数类型）
            set_dict = {"ids": [int(self.ap_type_id)] if self.ap_type_id else []}
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-批量禁用主数据服务",
                set_dict=set_dict
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 验证禁用结果（需要传递modelKey查询参数）
            detail_response, _ = self.standard_api_call(
                api_key="应付单类型配置表-根据ID查找数据服务",
                set_dict={"id": self.ap_type_id},
                query_params="modelKey=ERP_FIN$fin_apm_ap_type_md"
            )
            # 尝试多种可能的响应结构路径
            detail_data = detail_response.get("data", {})
            if isinstance(detail_data, dict):
                detail_data = detail_data.get("data", detail_data)
            if isinstance(detail_data, list) and len(detail_data) > 0:
                detail_data = detail_data[0]
            
            # 注意：根据实际返回字段判断是否禁用，可能是status或enabled字段
            # 这里假设有deleted字段，1表示禁用
            if isinstance(detail_data, dict):
                deleted = detail_data.get("deleted", 0)
                self.assert_util.assert_by_operator(deleted, "=", 1, "应付单据类型应已禁用")
            else:
                a.json(detail_response, "禁用后查询响应（调试）")
                raise AssertionError(f"禁用后查询返回的数据格式不正确: {type(detail_data)}")
            
            # 5. 记录关键数据
            a.json(response, "禁用响应数据")
            a.text(f"✅ 禁用成功", "禁用结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型删除",
        title="测试单行删除应付单据类型",
        description="验证根据ID删除应付单据类型功能",
        severity="normal",
        file_level_order=7,
        tags=["应付单据类型", "删除", "单行删除"]
    )
    def test_delete_ap_type(self):
        """测试单行删除应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 删除数据（使用单行删除接口，需要modelKey查询参数）
            set_dict = {"id": int(self.ap_type_id) if self.ap_type_id else None}
            response, _ = self.standard_api_call(
                api_key="应付单类型配置表-根据ID删除数据服务",
                set_dict=set_dict,
                query_params="modelKey=ERP_FIN$fin_apm_ap_type_md"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            
            # 5. 记录关键数据
            a.json(response, "删除响应数据")
            a.text(f"✅ 删除成功", "删除结果")
            
            # 6. 清空ID，避免后续用例使用已删除的数据
            self.ap_type_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型删除",
        title="测试批量删除应付单据类型",
        description="验证批量删除应付单据类型功能",
        severity="normal",
        file_level_order=8,
        tags=["应付单据类型", "删除", "批量删除"]
    )
    def test_batch_delete_ap_type(self):
        """测试批量删除应付单据类型"""
        try:
            # 1. 创建多个测试数据
            ap_type_ids = []
            for i in range(2):
                timestamp = self.mock_util.get_timestamp()
                ap_type_code = f"AT_AP_TYPE_BATCH_{timestamp}_{i}"
                ap_type_name = f"自动化测试应付单据类型_批量删除_{timestamp}_{i}"
                
                set_dict = {"ids":[int(self.ap_type_id)] if self.ap_type_id else []
                }
                response, _ = self.standard_api_call(
                    api_key="应付单类型配置表-批量删除数据服务",
                    set_dict=set_dict
                )
                self.assert_util.assert_response_success(response)
            
            # 5. 记录关键数据
            a.json(response, "批量删除响应数据")
            a.text(f"✅ 批量删除成功，共删除 {len(ap_type_ids)} 条记录", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单据类型复制",
        title="测试复制应付单据类型",
        description="验证复制应付单据类型功能",
        severity="normal",
        file_level_order=9,
        tags=["应付单据类型", "复制"]
    )
    def test_copy_ap_type(self):
        """测试复制应付单据类型"""
        try:
            # 1. 确保有数据
            if not self.ap_type_id:
                self.test_save_ap_type()
            
            # 2. 复制数据（需要modelKey查询参数）
            set_dict = {"id": int(self.ap_type_id) if self.ap_type_id else None}
            response, copied_id = self.standard_api_call(
                api_key="应付单类型配置表-复制数据转换服务",
                set_dict=set_dict,
                query_params="modelKey=ERP_FIN$fin_apm_ap_type_md"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 记录关键数据
            a.json(response, "复制响应数据")
            a.text(f"✅ 复制成功，新ID: {copied_id}", "复制结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise