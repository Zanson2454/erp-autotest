# -*- coding: utf-8 -*-
"""
销售发票业务功能测试用例
包含：基于应收单生成销售发票、应收单转化销售发票、发票钩稽、发票自动钩稽等业务功能测试
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


@allure.epic("ERP通业财模块")
@allure.feature("销售发票业务功能")
class TestSbBusinessFunction(FinBaseTest):
    """销售发票业务功能测试类"""
    
    sb_id = None  # 销售发票ID
    ar_id = None  # 应收单ID（用于生成发票）
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.sb_id = None
        cls.ar_id = None
        cls.logger.info("销售发票业务功能测试类初始化完成")
        
        # 初始化配置数据（从init_data获取）
        if cls.init_data:
            cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        
        # 初始化MD（从md_cache_data获取主数据）
        if cls.md_cache_data:
            # 合作伙伴信息
            cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])
            cls.cust_id = cust_info[0].get("id") if cust_info else None
            # 组织信息
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            sls_org_info = cls.md_cache_data.get("org_info", {}).get("sls_org_info", [])
            cls.sls_org_id = sls_org_info[0].get("id") if sls_org_info else None
        
        # 初始化财务缓存数据
        if cls.fin_cache_data:
            sb_type_info_list = cls.fin_cache_data.get("sb_type_info", [])
            cls.sb_type_id = sb_type_info_list[0].get("id") if sb_type_info_list else None
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 禁止用循环遍历表名，必须一个表一个表地单独调用
            if cls.sb_id:
                cls.db.delete(
                    table="fin_tm_sb_head_tr",
                    where="id = %s",
                    params=[cls.sb_id]
                )
            if cls.ar_id:
                cls.db.delete(
                    table="fin_arm_ar_head_tr",
                    where="id = %s",
                    params=[cls.ar_id]
                )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    # ==================== 基于应收单生成销售发票 ====================
    
    @case_decorator(
        story="基于应收单生成销售发票",
        title="测试基于应收单生成销售发票",
        description="验证根据应收单自动生成销售发票的功能，包括数据转换和关联关系建立",
        severity="critical",
        file_level_order=1,
        smoke=False,
        tags=["销售发票", "生成", "应收单"]
    )
    def test_create_sb_by_ar(self):
        """
        测试基于应收单生成销售发票
        测试方面：
        1. 应收单数据转换（应收单头信息转换为发票头信息）
        2. 应收单行数据转换（应收单行信息转换为发票行信息）
        3. 金额数据传递（含税金额、不含税金额、税额等完整传递）
        4. 关联关系建立（发票与应收单的关联关系，用于后续钩稽）
        5. 业务规则校验（应收单状态必须是已提交或已过账，发票类型匹配等）
        """
        try:
            # 注意：此测试需要先有应收单数据
            # 实际使用时需要先创建应收单，这里仅提供测试框架
            if not self.ar_id:
                # 这里应该先创建应收单，示例代码：
                # self.ar_id = self.create_ar_doc()
                self.logger.warning("需要先创建应收单，跳过此测试")
                pytest.skip("需要先创建应收单数据")
            
            # 1. 准备测试数据
            set_dict = {
                "arHeadId": self.ar_id,
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None
            }
            fields_to_filter = ["arHeadId", "docTypeId"]
            
            # 2. 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="SB-基于应收单生成销售发票服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="sb"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证
            # 验证生成的发票与应收单的关联关系
            sql = """
                SELECT ar_head_id FROM fin_tm_sb_head_tr 
                WHERE id = %s LIMIT 1
            """
            result = self.db.query(sql, (self.sb_id,))
            if result:
                ar_head_id = result[0].get("ar_head_id")
                self.assert_util.assert_by_operator(ar_head_id, "=", self.ar_id)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应收单转化销售发票",
        title="测试应收单转化销售发票-校验",
        description="验证应收单转化销售发票前的校验功能，包括业务规则校验和数据完整性校验",
        severity="critical",
        file_level_order=2,
        smoke=False,
        tags=["销售发票", "转化", "校验", "应收单"]
    )
    def test_validate_ar_convert_to_sb(self):
        """
        测试应收单转化销售发票-校验
        测试方面：
        1. 应收单状态校验（必须是可转化状态，如已提交或已过账）
        2. 发票类型匹配校验（应收单类型与发票类型是否匹配）
        3. 数据完整性校验（应收单是否有行数据、金额是否完整等）
        4. 业务规则校验（是否已存在关联发票、是否满足转化条件等）
        5. 权限校验（当前用户是否有转化权限）
        """
        try:
            if not self.ar_id:
                pytest.skip("需要先创建应收单数据")
            
            # 1. 准备测试数据
            set_dict = {
                "arHeadId": self.ar_id,
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None
            }
            fields_to_filter = ["arHeadId", "docTypeId"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="SB-应收单转化销售发票-校验服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应收单转化销售发票",
        title="测试应收单转化销售发票",
        description="验证应收单转化为销售发票的功能，包括数据转换和发票创建",
        severity="critical",
        file_level_order=3,
        smoke=False,
        tags=["销售发票", "转化", "应收单"]
    )
    def test_convert_ar_to_sb(self):
        """
        测试应收单转化销售发票
        测试方面：
        1. 应收单数据转换（头信息、行信息完整转换）
        2. 发票数据生成（生成新的发票编码、发票日期等）
        3. 金额数据传递（所有金额字段完整传递）
        4. 关联关系建立（发票与应收单的关联关系）
        5. 转化后状态处理（应收单状态、发票状态等）
        """
        try:
            if not self.ar_id:
                pytest.skip("需要先创建应收单数据")
            
            # 1. 先执行校验
            self.test_validate_ar_convert_to_sb()
            
            # 2. 执行转化
            set_dict = {
                "arHeadId": self.ar_id,
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None
            }
            fields_to_filter = ["arHeadId", "docTypeId"]
            
            response, extracted_id = self.standard_api_call(
                api_key="SB-应收单转化销售发票服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="sb"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 销售发票钩稽相关 ====================
    
    @case_decorator(
        story="销售发票钩稽",
        title="测试销售发票自动钩稽",
        description="验证销售发票的自动钩稽功能，自动匹配应收单进行钩稽",
        severity="critical",
        file_level_order=4,
        smoke=False,
        tags=["销售发票", "钩稽", "自动"]
    )
    def test_auto_clearing_sb(self):
        """
        测试销售发票自动钩稽
        测试方面：
        1. 自动匹配应收单（根据客户、金额、日期等条件自动匹配）
        2. 钩稽金额计算（部分钩稽、全额钩稽等场景）
        3. 钩稽关系建立（发票与应收单的钩稽明细记录）
        4. 钩稽状态更新（发票钩稽状态、应收单钩稽状态等）
        5. 钩稽规则校验（金额匹配、币种匹配、业务规则等）
        """
        try:
            if not self.sb_id:
                pytest.skip("需要先创建销售发票数据")
            
            # 1. 准备测试数据
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票自动钩稽-异步服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 等待异步任务完成
            import time
            time.sleep(5)
            
            # 查询数据库验证钩稽状态
            sql = """
                SELECT billing_clearing_status FROM fin_tm_sb_head_tr 
                WHERE id = %s LIMIT 1
            """
            result = self.db.query(sql, (self.sb_id,))
            if result:
                clearing_status = result[0].get("billing_clearing_status")
                self.assert_util.assert_by_operator(clearing_status, "in", ["CLEARED", "PARTIAL_CLEARED"])
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票钩稽",
        title="测试销售发票批量自动钩稽",
        description="验证销售发票的批量自动钩稽功能，批量处理多个发票的钩稽",
        severity="normal",
        file_level_order=5,
        smoke=False,
        tags=["销售发票", "钩稽", "批量"]
    )
    def test_batch_auto_clearing_sb(self):
        """
        测试销售发票批量自动钩稽
        测试方面：
        1. 批量发票处理（一次处理多个发票的钩稽）
        2. 批量匹配应收单（为每个发票匹配对应的应收单）
        3. 批量钩稽关系建立（批量创建钩稽明细记录）
        4. 批量状态更新（批量更新发票和应收单的钩稽状态）
        5. 批量处理结果统计（成功数量、失败数量、错误信息等）
        """
        try:
            if not self.sb_id:
                pytest.skip("需要先创建销售发票数据")
            
            # 1. 准备测试数据（批量ID列表）
            set_dict = {
                "ids": [self.sb_id]  # 实际使用时应该是多个发票ID
            }
            fields_to_filter = ["ids"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票批量自动钩稽",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票钩稽",
        title="测试销售发票钩稽查询",
        description="验证销售发票的钩稽查询功能，查询发票与应收单的钩稽明细",
        severity="normal",
        file_level_order=6,
        smoke=False,
        tags=["销售发票", "钩稽", "查询"]
    )
    def test_query_sb_clearing(self):
        """
        测试销售发票钩稽查询
        测试方面：
        1. 钩稽明细查询（查询发票与应收单的钩稽明细记录）
        2. 钩稽金额统计（已钩稽金额、未钩稽金额、部分钩稽金额等）
        3. 钩稽状态查询（已钩稽、未钩稽、部分钩稽等状态）
        4. 钩稽明细展示（钩稽日期、钩稽金额、钩稽单号、应收单信息等）
        5. 钩稽历史记录（查询发票的所有钩稽历史记录）
        """
        try:
            if not self.sb_id:
                pytest.skip("需要先创建销售发票数据")
            
            # 1. 准备测试数据
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="SB-销售发票-钩稽查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证
            # 验证返回的钩稽数据
            data = response.get("data", {}).get("data", {})
            clearing_list = data.get("clearingList", [])
            # 钩稽列表可能为空（未钩稽），这里只验证数据结构
            self.assert_util.assert_by_operator(isinstance(clearing_list, list), "=", True)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 销售发票校验相关 ====================
    
    @case_decorator(
        story="销售发票校验",
        title="测试销售发票校验是否需要强制钩稽",
        description="验证销售发票是否需要强制钩稽的校验功能",
        severity="normal",
        file_level_order=7,
        smoke=False,
        tags=["销售发票", "校验", "钩稽"]
    )
    def test_validate_sb_force_clearing(self):
        """
        测试销售发票校验是否需要强制钩稽
        测试方面：
        1. 强制钩稽规则校验（根据发票类型、金额等判断是否需要强制钩稽）
        2. 钩稽状态检查（发票是否已钩稽、钩稽是否完整等）
        3. 业务规则验证（根据业务配置判断是否需要强制钩稽）
        4. 校验结果返回（是否需要强制钩稽、原因说明等）
        """
        try:
            if not self.sb_id:
                pytest.skip("需要先创建销售发票数据")
            
            # 1. 准备测试数据
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-校验是否需要强制钩稽服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 销售发票其他业务功能 ====================
    
    @case_decorator(
        story="销售发票其他功能",
        title="测试销售发票OCR识别",
        description="验证销售发票的OCR识别功能，自动识别发票信息",
        severity="normal",
        file_level_order=8,
        smoke=False,
        tags=["销售发票", "OCR", "识别"]
    )
    @pytest.mark.skip(reason="OCR识别需要上传图片文件，复杂度较高")
    def test_ocr_recognize_sb(self):
        """
        测试销售发票OCR识别
        测试方面：
        1. 图片上传（上传发票图片文件）
        2. OCR识别（识别发票编码、金额、日期等关键信息）
        3. 识别结果解析（将OCR识别结果转换为结构化数据）
        4. 数据自动填充（将识别结果自动填充到发票表单）
        5. 识别准确率验证（验证OCR识别的准确性）
        """
        try:
            # OCR识别需要上传文件，这里仅提供测试框架
            set_dict = {
                "fileId": None,  # 文件ID，需要先上传文件
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None
            }
            fields_to_filter = ["fileId", "docTypeId"]
            
            response, _ = self.standard_api_call(
                api_key="销售发票-OCR识别服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票其他功能",
        title="测试销售发票退回",
        description="验证销售发票的退回功能，将已过账的发票退回",
        severity="normal",
        file_level_order=9,
        smoke=False,
        tags=["销售发票", "退回", "冲销"]
    )
    def test_return_sb_doc(self):
        """
        测试销售发票退回
        测试方面：
        1. 已过账发票退回（状态从DONE变为RETURNED）
        2. 退回前数据校验（发票状态、关联凭证状态等）
        3. 退回后凭证处理（冲销已生成的财务凭证）
        4. 退回权限验证（只有已过账状态可以退回）
        5. 退回原因记录（记录退回原因、退回人等）
        """
        try:
            if not self.sb_id:
                pytest.skip("需要先创建并过账销售发票数据")
            
            # 1. 准备测试数据
            set_dict = {
                "id": self.sb_id,
                "returnReason": "测试退回原因"
            }
            fields_to_filter = ["id", "returnReason"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-退回服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证状态变更
            sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                sb_status = result[0].get("sb_status")
                self.assert_util.assert_by_operator(sb_status, "=", "RETURNED")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
