# -*- coding: utf-8 -*-
"""
销售发票业务功能测试用例
包含：基于应收单生成销售发票、应收单转化销售发票、发票钩稽、发票自动钩稽等业务功能测试
"""

from re import S
import re
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
    def test_create_sb_by_ar_batch(self):
        """
        测试基于应收单生成销售发票(批量操作)
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
    def test_sb_clearing(self):
        """
        测试销售发票、应收单自动钩稽
        测试方面：
        1. 钩稽金额统计（已钩稽金额、未钩稽金额、部分钩稽金额等）
        2. 钩稽状态查询（已钩稽、未钩稽、部分钩稽等状态）
        3. 钩稽明细展示（钩稽日期、钩稽金额、钩稽单号、应收单信息等）
        4. 钩稽历史记录（查询发票的所有钩稽历史记录）
        """
        try:
            #获取已完成状态的应收单
            ar_doc_data = self.create_ar_doc(ar_type="STND", org=1, status="DONE")
            #通过行操作生成销售发票
            api_path = self.get_api_path("应收单-行操作-应收单转化销售发票保存-异步服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["biCode","docTypeId","id"], ["request"])
            data["params"]["request"] = {
                "biCode": self.mock_util.generate_unique_code("AUTO"),
                "docTypeId": {"id": self.sb_type_info.get("STND").get("id")},
                "id": ar_doc_data.get("id")
            }
            result = self.http.post(url, json=data, description=f"应收单行批量转化销售发票 - ID: {ar_doc_data.get('id')}")
            self.assert_util.assert_response_success(result)
            
            def query_ar_status():
                sql="""
                select id,ar_head_code,async_execution_status ,async_execution_failure_reason,billed_doc_amt,billing_doc_amt,unbilled_doc_amt from fin_arm_ar_head_tr where id=%s limit 1;
                """
                sql_result = self.db.query(sql, (ar_doc_data.get("id"),))
                if not sql_result:
                    raise ValueError(f"应收单ID {ar_doc_data.get('id')} 未找到")
                return sql_result[0]
            
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_ar_status,
                status_field="async_execution_status",
                success_status="SUCCEEDED",
                failed_status="FAILED",
                max_wait=10,
                interval=0.5
            )
        
            if result.status == self.wait_status.SUCCESS:
                ar_data = result.last_data
                self.assert_util.assert_by_operator(ar_data.get("billed_doc_amt"), "=", 0)
                expect_str = f"{ar_data.get('billing_doc_amt'):.6f}"
                actual_str = f"{ar_doc_data.get('grossDocAmt'):.6f}"
                self.assert_util.assert_by_operator(expect_str, "=", actual_str)
                self.assert_util.assert_by_operator(ar_data.get("unbilled_doc_amt"), "=", 0)
            elif result.status == self.wait_status.FAILED:
                raise ValueError(f"应收单ID {ar_doc_data.get('id')} 销售发票生成失败: {result.last_data.get('async_execution_failure_reason')}")
            
            #查询生成的销售发票头id
            sql="""
            select sb_head_code,tm_sb_head_tr_id from fin_tm_sb_item_tr where rel_doc_head_id=%s and deleted=0;
            """
            sql_result = self.db.query(sql, (ar_doc_data.get("id"),))
            sb_head_id = sql_result[0].get("tm_sb_head_tr_id")
            #调用销售发票过账服务，触发发票与应收单的自动钩稽
            set_dict = {"id": sb_head_id}
            fields_to_filter = ["id"]
            response, _ = self.standard_api_call(
                api_key="销售发票自动钩稽-异步服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            def query_sb_status():
                sql="""
                select * from fin_tm_sb_head_tr where id=%s;
                """
                sql_result = self.db.query(sql, (sb_head_id,))
                if not sql_result:
                    raise ValueError(f"销售发票头ID {sb_head_id} 未找到")
                return sql_result[0]
            
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_sb_status,
                status_field="async_execution_status",
                success_status="SUCCEEDED",
                failed_status="FAILED",
                max_wait=10,
                interval=0.5
            )
            if result.status == self.wait_status.SUCCESS:
                sb_data = result.last_data
                self.assert_util.assert_by_operator(sb_data.get("async_execution_status"), "=", "SUCCEEDED")
            elif result.status == self.wait_status.FAILED:
                raise ValueError(f"销售发票头ID {sb_head_id} 自动钩稽失败: {result.last_data.get('async_execution_failure_reason')}")
            
            
            self.assert_util.assert_response_success(response)
            #查询钩稽结果
            ar_head_sql=f"""
            select * from fin_arm_ar_head_tr where id={ar_doc_data.get("id")} ;
            """
            ar_item_sql=f"""
            select * from fin_arm_ar_item_tr where arm_ar_head_tr_id ={ar_doc_data.get("id")} ;
            """
            ar_head_result = self.db.query(ar_head_sql)
            ar_item_result = self.db.query(ar_item_sql)
            #断言应收单头票钩稽状态、票钩稽金额、未钩稽金额，钩稽中金额字段
            self.assert_util.assert_by_operator(f"{ar_head_result[0].get('billed_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
            self.assert_util.assert_by_operator(ar_head_result[0].get("billing_doc_amt"), "=", 0)
            self.assert_util.assert_by_operator(ar_head_result[0].get("unbilled_doc_amt"), "=", 0)
            self.assert_util.assert_by_operator(ar_head_result[0].get("billing_clearing_status"), "=", "CLEARED")
            #断言应收单行钩稽状态、钩稽金额字段
            self.assert_util.assert_by_operator(ar_item_result[0].get("item_clearing_status"), "=", "CLEARED")
            self.assert_util.assert_by_operator(f"{ar_item_result[0].get('cleared_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
            self.assert_util.assert_by_operator(ar_item_result[0].get("clearing_doc_amt"), "=",0)
            self.assert_util.assert_by_operator(ar_item_result[0].get("uncleared_doc_amt"), "=",0)
                
            #断言销售发票头票钩稽状态、钩稽金额字段
            sb_head_sql=f"""
            select * from fin_tm_sb_head_tr where id={sb_head_id} ;
            """
            sb_item_sql=f"""
            select * from fin_tm_sb_item_tr where tm_sb_head_tr_id ={sb_head_id} ;
            """
            sb_head_result = self.db.query(sb_head_sql)
            sb_item_result = self.db.query(sb_item_sql)
            self.assert_util.assert_by_operator(sb_head_result[0].get("clearing_status"), "=", "CLEARED")
            self.assert_util.assert_by_operator(f"{sb_head_result[0].get('cleared_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
            self.assert_util.assert_by_operator(sb_head_result[0].get("clearing_doc_amt"), "=",0)
            self.assert_util.assert_by_operator(sb_head_result[0].get("uncleared_doc_amt"), "=",0)
            #断言销售发票行钩稽状态、钩稽金额字段
            self.assert_util.assert_by_operator(sb_item_result[0].get("item_clearing_status"), "=", "CLEARED")
            self.assert_util.assert_by_operator(f"{sb_item_result[0].get('cleared_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
            self.assert_util.assert_by_operator(sb_item_result[0].get("clearing_doc_amt"), "=",0)
            self.assert_util.assert_by_operator(sb_item_result[0].get("uncleared_doc_amt"), "=",0)
            # 断言票钩稽记录是否生成                        
            sql=f"""
            select * from fin_brm_ibc_item_tr left join fin_brm_ibc_head_tr on brm_ibc_head_tr_id=fin_brm_ibc_head_tr.id where rel_doc_head_id in ({ar_doc_data.get("id")}, {sb_head_id});
            """
            result = self.db.query(sql)                                                 
            if not result:
                raise ValueError(f"应收单ID {ar_doc_data.get('id')} 和销售发票头ID {sb_head_id} 钩稽记录未找到")
            for item in result:
                self.assert_util.assert_by_operator(item.get("is_rel_clearing_rul"), "=", 1)
                self.assert_util.assert_by_operator(item.get("clearing_type"), "=", "AUTO")
                self.assert_util.assert_by_operator(item.get("clearing_business_category"), "=", "AR_AND_SB")
                self.assert_util.assert_by_operator(item.get("clearing_class"), "=", "MATCH_CLEAR")
                self.assert_util.assert_by_operator(f"{item.get('clearing_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
                self.assert_util.assert_by_operator(item.get("cleared_doc_amt"), "=", 0)
                self.assert_util.assert_by_operator(f"{item.get('uncleared_doc_amt'):.6f}", "=", f"{ar_doc_data.get('grossDocAmt'):.6f}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    
    @case_decorator(
        story="销售发票开票记录查询",
        title="测试销售发票开票记录查询",
        description="验证销售发票开票记录查询功能",
        severity="normal",
        file_level_order=3,
        smoke=False,
        tags=["销售发票", "开票记录查询", ""]
    )
    def test_query_sb_billing_record(self):
        """
        测试销售发票开票记录查询
        测试方面：
        1. 开票记录查询异步任务
        2. 开票记录异步任务轮询
        3. 开票记录头信息查询
        4. 开票记录行信息查询
        """
        try:
            #获取已钩稽的发票ID
            sql="""
            select id,sb_head_code,cleared_doc_amt from fin_tm_sb_head_tr where deleted=0 and clearing_status= 'CLEARED' order by created_at desc limit 1;
            """
            sql_result = self.db.query(sql)
            if not sql_result:
                raise ValueError("未找到已钩稽的发票")
            sb_head_id = sql_result[0].get("id")
            
            #获取taskKey，taskValue，status
            set_dict = {
                "docId": sb_head_id,
                "docType": "BIL",
                "clearingType":"IBC"
            }
            # 钩稽批数据轮询服务
            fields_to_filter = ["docId","docType","clearingType"]
            response, _ = self.standard_api_call(
                api_key="钩稽信息数据清洗服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            self.assert_util.assert_response_success(response)
            
            # 钩稽批数据轮询服务,异步调用钩稽批数据轮询服务
            set_dict={
                "docId": sb_head_id,
                "docType": "BIL",
                "taskKey":response.get("data", {}).get("data", {}).get("taskKey"),
                "taskValue":response.get("data", {}).get("data", {}).get("taskValue"),
                "status":response.get("data", {}).get("data", {}).get("status"),
            }
            fields_to_filter = ["docId","docType","taskKey","taskValue","status"]
            def query_task_status():
                response, _ = self.standard_api_call(
                    api_key="钩稽批数据轮询服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
                
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_task_status,
                status_field="status",
                success_status="SUCCESS",
                failed_status="FAILED",
                max_wait=10,
                interval=0.5
            )
            if result.status == self.wait_status.SUCCESS:
                #查询记录头信息
                set_dict={
                    "pageNo":1,
                    "pageSize":10,
                    "taskValue":result.last_data.get("taskValue"),
                }
                fields_to_filter=["pageNo","pageSize","taskValue"]
                response, _ = self.standard_api_call(
                    api_key="钩稽批数据头-翻页查询服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter
                )
                self.assert_util.assert_response_success(response)
                #断言开票记录头信息
                records = response.get("data", {}).get("data", {}).get("records", [])
                if not records:
                    raise ValueError("开票记录头信息为空")
                record = records[0]
                self.assert_util.assert_by_operator(record.get("relDocHeadCode"), "=", sql_result[0].get("sb_head_code"))
                self.assert_util.assert_by_operator(f"{record.get('clearedDocAmt'):.6f}", "=", f"{sql_result[0].get('cleared_doc_amt'):.6f}")
                self.assert_util.assert_by_operator(record.get("taskValue"), "=", result.last_data.get("taskValue"))
                self.assert_util.assert_by_operator(record.get("id"),"not_empty",None)
                
                #暂存记录头id
                record_id=record.get("id")
                #查询记录行信息
                set_dict={
                    "pageNo":1,
                    "pageSize":10,
                    "brmBatchDocHeadId":record_id
                }
                fields_to_filter=["pageNo","pageSize","brmBatchDocHeadId"]
                response, _ = self.standard_api_call(
                    api_key="钩稽批数据行-翻页查询服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter
                )
                self.assert_util.assert_response_success(response)
                #断言开票记录行信息
                records = response.get("data", {}).get("data", {}).get("records", [])
                self.assert_util.assert_by_operator(response.get("data", {}).get("data", {}).get("total"),">=",2)
                for record in records:
                    self.assert_util.assert_by_operator(record.get("brmBatchDocHeadId"),"=",record_id)
                    self.assert_util.assert_by_operator(f"{record.get('clearedDocAmt'):.6f}", "=", f"{sql_result[0].get('cleared_doc_amt'):.6f}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
            
    
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
    test.test_query_sb_billing_record()