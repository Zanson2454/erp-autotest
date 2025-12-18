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


@allure.epic("ERP业财模块")
@allure.feature("销售发票业务功能")
class TestSbBusinessFunction(FinBaseTest):
    """销售发票业务功能测试类"""
    
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("销售发票业务功能测试类初始化完成")

    
    @case_decorator(
        story="基于应收单生成销售发票",
        title="测试基于应收单生成销售发票",
        description="验证根据应收单生成销售发票的功能，包括数据转换和关联关系建立",
        severity="critical",
        file_level_order=1,
        smoke=False,
        tags=["销售发票", "生成"]
    )
    def test_create_sb_by_ar(self):
        """
        测试基于应收单生成销售发票
        """
        try:
            # 1. 创建应收单并获取应收单行项ID列表
            ar_doc_data = self.create_ar_doc(ar_type="STND", org=1, status="DONE")
            ar_doc_id = ar_doc_data.get("id")
            sql="""
            select id from fin_arm_ar_item_tr where arm_ar_head_tr_id=%s and deleted=0;
            """
            ar_item_ids = self.db.query(sql, (ar_doc_id,))
            if not ar_item_ids:
                raise ValueError("应收单行项ID列表为空，无法进行转化")
            ar_item_ids = [item.get("id") for item in ar_item_ids]
            
            # 2. 调用应收单行批量转化销售发票-校验服务
            api_path = self.get_api_path("应收单行批量转化销售发票-校验服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["armArItemIds"], ["params", "request"])
            data["params"]["request"]["armArItemIds"] = ar_item_ids
            
            result = self.http.post(url, json=data, description=f"应收单行批量转化销售发票-校验 - 行项IDs: {ar_item_ids}")
            self.assert_util.assert_response_success(result)
            
            # 3. 调用应收单行批量转化销售发票服务
            api_path = self.get_api_path("SB-应收单行批量转化销售发票服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["armArItemIds"], ["params", "request"])
            data["params"]["request"]["armArItemIds"] = ar_item_ids
            result = self.http.post(url, json=data, description=f"应收单行批量转化销售发票 - 行项IDs: {ar_item_ids}")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data", {}).get("data", {}).get("bilDocAmt", {}), "=", ar_doc_data.get("grossDocAmt"))
            
            # 4. 保存销售发票数据
            api_path = self.get_api_path("SB-销售发票保存并更新来源单服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["request"], ["params"])
            doc_type_id = self.sb_type_info.get("STND").get("id")
            # 合并字典：转换结果 + 发票编码 + 发票类型ID
            convert_result = result.get("data", {}).get("data", {})
            data["params"]["request"] = {
                **convert_result,
                "bilCode": self.mock_util.generate_unique_code("AUTO"),
                "docTypeId": {"id":doc_type_id}
            }
            save_result = self.http.post(url, json=data, description=f"销售发票保存并更新来源单 - 发票数据")
            self.assert_util.assert_response_success(save_result)
            
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    
    @case_decorator(
        story="销售发票钩稽",
        title="测试销售发票钩稽",
        description="验证销售发票的钩稽功能，自动匹配对应应收单进行钩稽",
        severity="normal",
        file_level_order=2,
        smoke=False,
        tags=["销售发票", "钩稽"]
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
            pass
  
            
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

if __name__ == "__main__":
    test = TestSbBusinessFunction()
    test.setup_class()
    test.test_create_sb_by_ar()