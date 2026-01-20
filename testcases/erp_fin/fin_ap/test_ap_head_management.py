# -*- coding: utf-8 -*-
"""
应付单管理测试用例
包含：应付单分页查询、应付单详情查询、应付单新建等
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_ap import ApBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付单管理")
class TestApHeadManagement(ApBaseTest):
    """应付单管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ap_head_id = None
        cls.ap_head_detail = None
        cls.ap_head_save_body = None
        cls.logger.info("应付单管理测试类初始化完成")
        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 应付单数据通常不需要清理，因为它们是业务单据
            # 如果需要清理，请根据实际业务需求添加清理逻辑
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单分页查询",
        description="验证应付单分页查询功能",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["应付单", "分页查询"]
    )
    def test_query_ap_head_page(self):
        """测试应付单分页查询"""
        try:
            # 1. 准备分页查询参数
            # 根据curl请求，params.request中包含pageableDTO和pageable两个字段
            # 根据规范，提取params.request内部的字段作为set_dict的根
            # 根据API配置，还需要包含enableUserPartner字段
            set_dict = {
                "enableUserPartner": False,
                "pageableDTO": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None,
                        "conditionGroup": None,
                        "keyword": None
                    }
                },
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="应付单分页查询服务",
                set_dict=set_dict
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 验证分页结果
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            total_count = response.get("data", {}).get("data", {}).get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(data_list), "<=", 20, "每页记录数不应超过20")
            
            # 5. 记录关键数据
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            a.text(f"✅ 分页查询成功，共 {total_count} 条记录，当前页 {len(data_list)} 条", "查询结果")
            
            # 6. 保存第一个ID供详情查询使用
            if data_list and len(data_list) > 0:
                self.ap_head_id = data_list[0].get("id")
                a.text(f"保存应付单ID: {self.ap_head_id}", "数据准备")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单详情查询",
        description="验证应付单详情查询功能",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["应付单", "详情查询"]
    )
    def test_query_ap_head_detail(self):
        """测试应付单详情查询"""
        try:
            # 1. 确保有数据ID（从分页查询获取）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            # 2. 准备详情查询参数
            set_dict = {"id": self.ap_head_id}
            self.logger.debug(f"set_dict: {set_dict}")
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="应付单详情查询服务",
                set_dict=set_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 验证返回的数据
            self.ap_head_detail = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(self.ap_head_detail, "not_empty", "详情数据不应为空")
            
            # 6. 记录关键数据
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            a.text(f"✅ 详情查询成功，应付单ID: {self.ap_head_id}", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
    def _build_ap_head_base(self):
        """
        构建应付单头基础数据
        """
        ap_date = self.mock_util.get_timestamp(timestamp=True)
        return {
            "docTypeId": {"id":self.ap_type_stnd_id},
            "comOrgId": {"id":self.gr_com_org_id},
            "purOrgId": {"id":self.pur_org_id},
            "payOrgId": {"id":self.gr_com_org_id},
            "apDate": ap_date,
            "settPartnerId": {"id":self.vend_id},
            "remark": f"自动化创建_{self.mock_util.get_timestamp(timestamp=True)}",
            "extPoId": None,
            "extPoSoCode": None,
            "apHeadCode": None,
            "settPartnerType": "SUPPLIER",
            "apStatus": None,
            "createType": None,
            "payClearingStatus": "UNCLEARED",
            "invClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "purEmployeeId": None,
            "apItems": [],
            "apSchls": [],
            "netBaseAmt": None,
            "grossBaseAmt": None,
            "netDocAmt": None,
            "docCurrId": {"id":self.curr_id},
            "baseCurrId": {"id":self.curr_id},
            "grossDocAmt": None,
            "exchRate": 1
        }
    
    def _build_ap_item(self):
        """
        构建应付单行数据（apItem）
        注意：金额计算必须使用round()控制精度，避免浮点数精度误差导致系统校验失败
        """
        apQty = self.mock_util.get_mock_qty()
        grossDocPrice = self.mock_util.get_mock_price()
        # 含税金额 = 数量 × 含税单价（保留2位小数）
        grossDocAmt = round(apQty * grossDocPrice, 2)
        taxRate = 13
        # 税额 = 含税金额 × 税率 / (100 + 税率)（保留2位小数）
        taxAmt = round(grossDocAmt * taxRate / (100 + taxRate), 2)
        # 不含税金额 = 含税金额 - 税额（保留2位小数）
        netDocAmt = round(grossDocAmt - taxAmt, 2)
        # 本位币金额：如果汇率=1，本位币金额等于单据金额；否则需要换算
        # 由于exchRate=1，本位币金额等于单据金额（保留2位小数）
        netBaseAmt = round(netDocAmt, 2)
        grossBaseAmt = round(grossDocAmt, 2)
        return {
            "matId": {"id": self.mat_id},
            "apQty": apQty,
            "grossDocPrice": grossDocPrice,
            "taxRate": taxRate,
            "grossDocAmt": grossDocAmt,
            "netDocAmt": netDocAmt,
            "netBaseAmt": netBaseAmt,
            "grossBaseAmt": grossBaseAmt,
            "taxAmt": taxAmt,
            "settItemTypeId": {"id": self.sett_item_type_E_PUR_GOODS_id},
            "taxCodeId": {"id": self.tax_code_id}
        }
    
    def _build_ap_head_for_init(self):
        """
        构建用于初始化应付计划行的应付单头数据
        
        Args:
            base_data: 基础数据字典（包含vend_id, mat_id, curr_id）
            ap_date: 应付单日期（时间戳）
            remark: 备注
            ap_items: 应付单行数据列表
        
        Returns:
            dict: 应付单头数据
        """
        ap_base_body = self._build_ap_head_base()
        ap_items= [self._build_ap_item()]
        init_body = {
            **ap_base_body,
            "apItems": ap_items,
            "apSchls": [],
        }
        return init_body
    
    def _extract_id_from_obj(self, obj):
        """
        从嵌套对象中提取id，如果对象不存在则返回None
        
        Args:
            obj: 可能是字典对象，包含id字段
        
        Returns:
            dict: {"id": id} 或 None
        """
        if obj and isinstance(obj, dict) and obj.get("id"):
            return {"id": obj.get("id")}
        return None
    
    

    @case_decorator(
        story="应付单管理",
        title="测试应付单新建过程，应付计划行初始化并回填应付单头",
        description="验证应付单新建过程，应付计划行初始化并回填应付单头",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["应付单", "新建", "创建", "初始化"]
    )
    def test_ap_schls_init(self):
        """
        测试应付计划行初始化并回填应付单头
        """
        try:
            ap_head_for_init = self._build_ap_head_for_init()
            ap_schls_init_response, _ = self.standard_api_call(
                api_key="AP-应付计划行初始化服务",
                set_dict=ap_head_for_init
                )
            self.assert_util.assert_response_data(ap_schls_init_response)
            self.logger.debug(f"ap_schls_init_response: {ap_schls_init_response}")
            ap_schls = ap_schls_init_response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(ap_schls, "not_empty", "应付计划行初始化失败，未返回apSchls数据")
            init_body = ap_head_for_init.copy()
            init_body["apSchls"] = ap_schls
            self.ap_head_save_body = init_body
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单新建",
        description="验证应付单新建功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["应付单", "新建", "创建"]
    )
    def test_create_ap_head(self):
        """测试应付单新建"""
        try:
            if not self.ap_head_save_body:
                self.test_ap_schls_init()
            
            # 调用保存接口
            save_response, saved_id = self.standard_api_call(
                api_key="AP-应付保存服务",
                set_dict=self.ap_head_save_body,
                store_id_as="ap_head"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(save_response)
            
            # 10. 验证保存的数据
            self.ap_head_id = save_response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_by_operator(self.ap_head_id, "not_empty", "保存的应付单数据不应为空")      
            # 11. 记录关键数据
            a.json(self.ap_head_save_body, "保存请求数据")
            a.json(save_response, "保存响应数据")
            a.text(f"✅ 应付单新建成功，应付单ID: {self.ap_head_id}", "创建结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单提交",
        description="验证应付单提交功能",
        severity="critical",
        file_level_order=5,
        smoke=True,
        tags=["应付单", "提交"]
    )
    def test_submit_ap_head(self):
        """测试应付单提交"""
        try:
            # 1. 确保有数据（先创建，再查询详情）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            # 2. 准备提交参数
            # 从详情数据中提取必要字段，移除系统字段，简化嵌套对象
            submit_dict =self.ap_head_detail
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付单-列表提交服务",
                set_dict=submit_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            
            
            # 5. 记录关键数据
            a.json(submit_dict, "提交请求数据")
            a.json(response, "提交响应数据")
            a.text(f"✅ 应付单提交成功，应付单ID: {self.ap_head_id}, 应付单编号: {submit_dict.get('apHeadCode')}", "提交结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单提交撤回",
        description="验证应付单提交撤回功能",
        severity="critical",
        file_level_order=6,
        smoke=True,
        tags=["应付单", "提交撤回", "撤回"]
    )
    def test_submit_rollback_ap_head(self):
        """测试应付单提交撤回"""
        try:
            # 1. 确保有已提交的应付单（先创建、查询详情、提交）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "CONFIRM":
                # 如果状态不是已提交，先执行提交
                self.test_submit_ap_head()
                # 提交后重新查询详情
                self.test_query_ap_head_detail()
            
            # 2. 准备撤回参数
            # 从详情数据中提取必要字段，移除系统字段，简化嵌套对象
            rollback_dict = self.ap_head_detail.copy()
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付撤回服务",
                set_dict=rollback_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证撤回后状态（可选：重新查询详情验证状态变为DRAFT）
            # 重新查询详情验证状态
            detail_response, _ = self.standard_api_call(
                api_key="应付单详情查询服务",
                set_dict={"id": self.ap_head_id}
            )
            self.assert_util.assert_response_data(detail_response)
            updated_detail = detail_response.get("data", {}).get("data", {})
            updated_status = updated_detail.get("apStatus")
            
            # 6. 记录关键数据
            a.json(rollback_dict, "撤回请求数据")
            a.json(response, "撤回响应数据")
            a.text(
                f"✅ 应付单提交撤回成功，应付单ID: {self.ap_head_id}, "
                f"应付单编号: {rollback_dict.get('apHeadCode')}, "
                f"撤回前状态: CONFIRM, 撤回后状态: {updated_status}",
                "撤回结果"
            )
            
            # 更新详情数据
            self.ap_head_detail = updated_detail
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单过账异步并等待完成",
        description="验证应付单过账异步功能，等待过账任务完成并验证状态",
        severity="critical",
        file_level_order=7,
        smoke=True,
        tags=["应付单", "过账", "异步"]
    )
    def test_post_ap_head_async_and_wait(self):
        """
        测试应付单过账异步并等待完成
        
        测试流程：
        1. 发起异步过账任务
        2. 验证任务已创建（状态为CREATED）
        3. 轮询查询任务状态，等待任务完成
        4. 验证过账状态和异步执行状态
        
        业务说明：
        - 应付单过账是一个异步任务，需要等待后台处理完成
        - 异步任务状态流转：CREATED -> PROCESSING -> SUCCEEDED/FAILED
        - 应付单状态流转：CONFIRM -> DONE（成功时）
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保有已提交的应付单（先创建、查询详情、提交）
            if not self.ap_head_id:
                self.test_create_ap_head()
            # 检查应付单状态，如果不是已提交状态，先提交
            if not self.ap_head_detail:
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "CONFIRM":
                # 如果状态不是已提交，先执行提交
                self.test_submit_ap_head()
                # 提交后重新查询详情
                self.test_query_ap_head_detail()
            
            # ========== 步骤1：发起异步过账任务 ==========
            # 调用异步过账接口，触发后台过账处理
            # 该接口会立即返回，不会等待任务完成，任务在后台异步执行
            post_dict = self.ap_head_detail.copy()
            response, _ = self.standard_api_call(
                api_key="应付单-过账-异步服务",
                set_dict=post_dict
            )
            
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建（CREATED状态表示任务已成功提交到队列）
            # 此时任务还未开始执行，只是进入了任务队列等待处理
            async_execution_status = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            if async_execution_status:
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "CREATED",
                    "异步任务发起过账状态应为CREATED，表示任务已成功提交到队列"
                )
            
            # ========== 步骤2：定义查询函数 ==========
            # 定义查询函数，用于轮询检查应付单的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            def query_ap_status():
                """
                查询应付单状态
                
                功能说明：
                - 调用查询详情接口，获取应付单的当前状态
                - 返回的数据包含异步任务执行状态和应付单业务状态
                
                返回数据字段说明：
                - asyncExecutionStatus: 异步执行状态
                  * CREATED: 任务已创建，等待执行
                  * PROCESSING: 任务执行中
                  * SUCCEEDED: 任务执行成功
                  * FAILED: 任务执行失败
                - apStatus: 应付单业务状态
                  * DRAFT: 草稿
                  * CONFIRM: 已提交
                  * DONE: 已过账
                - asyncExecutionFailureReason: 失败原因（仅在失败时存在）
                
                返回：
                    dict: 包含应付单的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="应付单详情查询服务",
                    set_dict={"id": self.ap_head_id}
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤3：等待异步任务完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            # 工具会自动：
            # - 按interval间隔（2秒）调用query_ap_status函数
            # - 检查asyncExecutionStatus字段的值
            # - 如果状态为SUCCEEDED则返回成功，停止轮询
            # - 如果状态为FAILED则返回失败并记录失败原因，停止轮询
            # - 如果超过max_wait时间（60秒）仍未完成则返回超时，停止轮询
            # - 自动记录每次轮询的结果到Allure报告中
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_ap_status,  # 查询函数，每次轮询时调用
                status_field="asyncExecutionStatus",  # 要检查的状态字段名
                success_status="SUCCEEDED",  # 成功状态值，达到此状态时停止等待
                failed_status="FAILED",  # 失败状态值，达到此状态时立即返回失败
                failure_reason_field="asyncExecutionFailureReason",  # 失败原因字段名，用于记录失败详情
                max_wait=60,  # 最大等待时间（秒），过账可能需要较长时间
                interval=2  # 轮询间隔（秒），每2秒查询一次状态
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
                
                # 4.1 验证应付单状态
                # 过账成功后，apStatus应该从CONFIRM变为DONE
                # 这表示过账业务逻辑已成功执行
                ap_status = result.last_data.get("apStatus")
                self.assert_util.assert_by_operator(
                    ap_status, "=", "DONE",
                    f"过账任务应成功完成，apStatus应为DONE，实际状态: {ap_status}"
                )
                
                # 4.2 验证异步执行状态
                # 异步任务执行成功后，asyncExecutionStatus应该为SUCCEEDED
                # 这表示异步任务本身已成功完成
                async_execution_status = result.last_data.get("asyncExecutionStatus")
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "SUCCEEDED",
                    f"异步任务状态应为SUCCEEDED，实际状态: {async_execution_status}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 过账任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"应付单状态: {ap_status}\n"
                    f"异步执行状态: {async_execution_status}",
                    "任务完成"
                )
                
                # 更新详情数据
                self.ap_head_detail = result.last_data
                
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                # 失败原因通常包含业务错误信息，有助于定位问题
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步过账任务失败: {failure_reason}\n"
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
                    f"⚠️ 等待异步过账任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                # 这种情况通常是查询接口调用失败，而非业务逻辑问题
                raise AssertionError(
                    f"等待异步过账任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
            
            # 记录关键数据
            a.json(post_dict, "过账请求数据")
            a.json(response, "过账响应数据")
            
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            # 异常信息包含完整的错误堆栈和上下文信息
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单反过账异步并等待完成",
        description="验证应付单反过账异步功能，等待反过账任务完成并验证状态",
        severity="critical",
        file_level_order=8,
        smoke=True,
        tags=["应付单", "反过账", "异步"]
    )
    def test_post_rollback_ap_head_async_and_wait(self):
        """
        测试应付单反过账异步并等待完成
        
        测试流程：
        1. 发起异步反过账任务
        2. 验证任务已创建（状态为CREATED）
        3. 轮询查询任务状态，等待任务完成
        4. 验证反过账状态和异步执行状态
        
        业务说明：
        - 应付单反过账是一个异步任务，需要等待后台处理完成
        - 异步任务状态流转：CREATED -> PROCESSING -> SUCCEEDED/FAILED
        - 应付单状态流转：DONE -> DRAFT/CONFIRM（成功时）
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保有已过账的应付单（先创建、查询详情、提交、过账）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            if not self.ap_head_detail:
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "DONE":
                # 如果状态不是已过账，先执行提交和过账
                if current_status != "CONFIRM":
                    self.test_submit_ap_head()
                    self.test_query_ap_head_detail()
                # 执行过账
                self.test_post_ap_head_async_and_wait()
                # 过账后重新查询详情
                self.test_query_ap_head_detail()
            
            # ========== 步骤1：发起异步反过账任务 ==========
            # 调用异步反过账接口，触发后台反过账处理
            # 该接口会立即返回，不会等待任务完成，任务在后台异步执行
            rollback_dict = self.ap_head_detail.copy()
            response, _ = self.standard_api_call(
                api_key="应付单-反过账-异步服务",
                set_dict=rollback_dict
            )
            
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建（CREATED状态表示任务已成功提交到队列）
            # 此时任务还未开始执行，只是进入了任务队列等待处理
            async_execution_status = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            if async_execution_status:
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "CREATED",
                    "异步任务发起反过账状态应为CREATED，表示任务已成功提交到队列"
                )
            
            # ========== 步骤2：定义查询函数 ==========
            # 定义查询函数，用于轮询检查应付单的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            def query_ap_status():
                """
                查询应付单状态
                
                功能说明：
                - 调用查询详情接口，获取应付单的当前状态
                - 返回的数据包含异步任务执行状态和应付单业务状态
                
                返回数据字段说明：
                - asyncExecutionStatus: 异步执行状态
                  * CREATED: 任务已创建，等待执行
                  * PROCESSING: 任务执行中
                  * SUCCEEDED: 任务执行成功
                  * FAILED: 任务执行失败
                - apStatus: 应付单业务状态
                  * DRAFT: 草稿
                  * CONFIRM: 已提交
                  * DONE: 已过账
                - asyncExecutionFailureReason: 失败原因（仅在失败时存在）
                
                返回：
                    dict: 包含应付单的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="应付单详情查询服务",
                    set_dict={"id": self.ap_head_id}
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤3：等待异步任务完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            # 工具会自动：
            # - 按interval间隔（2秒）调用query_ap_status函数
            # - 检查asyncExecutionStatus字段的值
            # - 如果状态为SUCCEEDED则返回成功，停止轮询
            # - 如果状态为FAILED则返回失败并记录失败原因，停止轮询
            # - 如果超过max_wait时间（60秒）仍未完成则返回超时，停止轮询
            # - 自动记录每次轮询的结果到Allure报告中
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_ap_status,  # 查询函数，每次轮询时调用
                status_field="asyncExecutionStatus",  # 要检查的状态字段名
                success_status="SUCCEEDED",  # 成功状态值，达到此状态时停止等待
                failed_status="FAILED",  # 失败状态值，达到此状态时立即返回失败
                failure_reason_field="asyncExecutionFailureReason",  # 失败原因字段名，用于记录失败详情
                max_wait=60,  # 最大等待时间（秒），反过账可能需要较长时间
                interval=2  # 轮询间隔（秒），每2秒查询一次状态
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
                
                # 4.1 验证应付单状态
                # 反过账成功后，apStatus应该从DONE变为DRAFT或CONFIRM
                # 这表示反过账业务逻辑已成功执行
                ap_status = result.last_data.get("apStatus")
                # 反过账后状态可能是DRAFT或CONFIRM，取决于业务规则
                self.assert_util.assert_by_operator(
                    ap_status, "in", ["DRAFT", "CONFIRM"],
                    f"反过账任务应成功完成，apStatus应为DRAFT或CONFIRM，实际状态: {ap_status}"
                )
                
                # 4.2 验证异步执行状态
                # 异步任务执行成功后，asyncExecutionStatus应该为SUCCEEDED
                # 这表示异步任务本身已成功完成
                async_execution_status = result.last_data.get("asyncExecutionStatus")
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "SUCCEEDED",
                    f"异步任务状态应为SUCCEEDED，实际状态: {async_execution_status}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 反过账任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"应付单状态: {ap_status}\n"
                    f"异步执行状态: {async_execution_status}",
                    "任务完成"
                )
                
                # 更新详情数据
                self.ap_head_detail = result.last_data
                
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                # 失败原因通常包含业务错误信息，有助于定位问题
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步反过账任务失败: {failure_reason}\n"
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
                    f"⚠️ 等待异步反过账任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                # 这种情况通常是查询接口调用失败，而非业务逻辑问题
                raise AssertionError(
                    f"等待异步反过账任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
            
            # 记录关键数据
            a.json(rollback_dict, "反过账请求数据")
            a.json(response, "反过账响应数据")
            
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            # 异常信息包含完整的错误堆栈和上下文信息
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单过账后冲销",
        description="验证应付单过账后冲销功能",
        severity="critical",
        file_level_order=9,
        smoke=True,
        tags=["应付单", "冲销"]
    )
    def test_reversal_ap_head(self):
        """
        测试应付单过账后冲销
        
        测试流程：
        1. 确保有已过账的应付单
        2. 准备冲销参数（包含应付单ID和冲销日期）
        3. 调用冲销接口
        4. 验证冲销成功
        
        业务说明：
        - 应付单冲销是在应付单已过账后执行的操作
        - 冲销需要指定冲销日期
        - 冲销后应付单状态会发生变化
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保有已过账的应付单（先创建、查询详情、提交、过账）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            if not self.ap_head_detail:
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "DONE":
                # 如果状态不是已过账，先执行提交和过账
                if current_status != "CONFIRM":
                    self.test_submit_ap_head()
                    self.test_query_ap_head_detail()
                # 执行过账
                self.test_post_ap_head_async_and_wait()
                # 过账后重新查询详情
                self.test_query_ap_head_detail()
            
            # ========== 步骤1：准备冲销参数 ==========
            # 从curl请求分析，冲销接口需要的参数：
            # - id: 应付单ID
            # - apDate: 冲销日期（时间戳，毫秒）
            # 移除系统字段：createdBy, updatedBy, createdAt, updatedAt, version, deleted
            reversal_date = self.mock_util.get_timestamp(timestamp=True)
            reversal_dict = {
                "id": self.ap_head_id,
                "apDate": reversal_date
            }
            
            # ========== 步骤2：调用冲销接口 ==========
            response, _ = self.standard_api_call(
                api_key="AP-应付单冲销服务",
                set_dict=reversal_dict
            )
            
            # ========== 步骤3：业务断言 ==========
            self.assert_util.assert_response_success(response)
            
            # ========== 步骤4：验证冲销结果（可选：重新查询详情验证状态） ==========
            # 重新查询详情验证冲销后的状态
            detail_response, _ = self.standard_api_call(
                api_key="应付单详情查询服务",
                set_dict={"id": self.ap_head_id}
            )
            self.assert_util.assert_response_data(detail_response)
            updated_detail = detail_response.get("data", {}).get("data", {})
            
            # ========== 步骤5：记录关键数据 ==========
            a.json(reversal_dict, "冲销请求数据")
            a.json(response, "冲销响应数据")
            a.text(
                f"✅ 应付单冲销成功，应付单ID: {self.ap_head_id}, "
                f"应付单编号: {self.ap_head_detail.get('apHeadCode')}, "
                f"冲销日期: {reversal_date}",
                "冲销结果"
            )
            
            # 更新详情数据
            self.ap_head_detail = updated_detail
            
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单过账后生成采购发票异步并等待完成",
        description="验证应付单过账后生成采购发票异步功能，等待生成任务完成并验证结果",
        severity="critical",
        file_level_order=10,
        smoke=True,
        tags=["应付单", "生成采购发票", "异步"]
    )
    def test_convert_to_pi_async_and_wait(self):
        """
        测试应付单过账后生成采购发票异步并等待完成
        
        测试流程：
        1. 发起异步生成采购发票任务
        2. 验证任务已创建（状态为CREATED）
        3. 轮询查询任务状态，等待任务完成
        4. 验证生成结果和异步执行状态
        
        业务说明：
        - 应付单生成采购发票是一个异步任务，需要等待后台处理完成
        - 异步任务状态流转：CREATED -> PROCESSING -> SUCCEEDED/FAILED
        - 生成成功后，会创建对应的采购发票
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保有已过账的应付单（先创建、查询详情、提交、过账）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            if not self.ap_head_detail:
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "DONE":
                # 如果状态不是已过账，先执行提交和过账
                if current_status != "CONFIRM":
                    self.test_submit_ap_head()
                    self.test_query_ap_head_detail()
                # 执行过账
                self.test_post_ap_head_async_and_wait()
                # 过账后重新查询详情
                self.test_query_ap_head_detail()
            
            # ========== 步骤1：准备生成采购发票参数 ==========
            # 从curl请求分析，生成采购发票接口需要的参数：
            # - id: 应付单ID
            # - invCode: 发票编码（使用mock_util生成）
            # - docTypeId: 发票类型ID（采购普通发票类型：2000008）
            inv_code = self.mock_util.generate_unique_code(tag="PI")
            convert_dict = {
                "id": self.ap_head_id,
                "invCode": inv_code,
                "docTypeId": {"id": 2000008}  # 采购普通发票类型
            }
            
            # ========== 步骤2：发起异步生成采购发票任务 ==========
            # 调用异步生成采购发票接口，触发后台处理
            # 该接口会立即返回，不会等待任务完成，任务在后台异步执行
            response, _ = self.standard_api_call(
                api_key="应付单-行操作-应付单转化销售发票保存-异步服务",
                set_dict=convert_dict
            )
            
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建（CREATED状态表示任务已成功提交到队列）
            # 此时任务还未开始执行，只是进入了任务队列等待处理
            async_execution_status = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            if async_execution_status:
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "CREATED",
                    "异步任务发起生成采购发票状态应为CREATED，表示任务已成功提交到队列"
                )
            
            # ========== 步骤3：定义查询函数 ==========
            # 定义查询函数，用于轮询检查应付单的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            def query_ap_status():
                """
                查询应付单状态
                
                功能说明：
                - 调用查询详情接口，获取应付单的当前状态
                - 返回的数据包含异步任务执行状态和应付单业务状态
                
                返回数据字段说明：
                - asyncExecutionStatus: 异步执行状态
                  * CREATED: 任务已创建，等待执行
                  * PROCESSING: 任务执行中
                  * SUCCEEDED: 任务执行成功
                  * FAILED: 任务执行失败
                - asyncExecutionFailureReason: 失败原因（仅在失败时存在）
                
                返回：
                    dict: 包含应付单的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="应付单详情查询服务",
                    set_dict={"id": self.ap_head_id}
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤4：等待异步任务完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_ap_status,  # 查询函数，每次轮询时调用
                status_field="asyncExecutionStatus",  # 要检查的状态字段名
                success_status="SUCCEEDED",  # 成功状态值，达到此状态时停止等待
                failed_status="FAILED",  # 失败状态值，达到此状态时立即返回失败
                failure_reason_field="asyncExecutionFailureReason",  # 失败原因字段名，用于记录失败详情
                max_wait=60,  # 最大等待时间（秒），生成采购发票可能需要较长时间
                interval=2  # 轮询间隔（秒），每2秒查询一次状态
            )
            
            # ========== 步骤5：断言等待结果 ==========
            if result.status == self.wait_status.SUCCESS:
                # 等待成功，验证业务状态
                
                # 5.1 验证异步执行状态
                # 异步任务执行成功后，asyncExecutionStatus应该为SUCCEEDED
                async_execution_status = result.last_data.get("asyncExecutionStatus")
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "SUCCEEDED",
                    f"异步任务状态应为SUCCEEDED，实际状态: {async_execution_status}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 生成采购发票任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"发票编码: {inv_code}\n"
                    f"异步执行状态: {async_execution_status}",
                    "任务完成"
                )
                
                # 更新详情数据
                self.ap_head_detail = result.last_data
                
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步生成采购发票任务失败: {failure_reason}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后数据: {result.last_data}"
                )
            elif result.status == self.wait_status.TIMEOUT:
                # 等待超时，抛出异常
                raise AssertionError(
                    f"⚠️ 等待异步生成采购发票任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                raise AssertionError(
                    f"等待异步生成采购发票任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
            
            # 记录关键数据
            a.json(convert_dict, "生成采购发票请求数据")
            a.json(response, "生成采购发票响应数据")
            
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单过账后生成付款申请异步并等待完成",
        description="验证应付单过账后生成付款申请异步功能，等待生成任务完成并验证结果",
        severity="critical",
        file_level_order=11,
        smoke=True,
        tags=["应付单", "生成付款申请", "异步"]
    )
    def test_convert_to_pr_async_and_wait(self):
        """
        测试应付单过账后生成付款申请异步并等待完成
        
        测试流程：
        1. 发起异步生成付款申请任务
        2. 验证任务已创建（状态为CREATED）
        3. 轮询查询任务状态，等待任务完成
        4. 验证生成结果和异步执行状态
        
        业务说明：
        - 应付单生成付款申请是一个异步任务，需要等待后台处理完成
        - 异步任务状态流转：CREATED -> PROCESSING -> SUCCEEDED/FAILED
        - 生成成功后，会创建对应的付款申请单
        """
        try:
            # ========== 前置条件检查 ==========
            # 确保有已过账的应付单（先创建、查询详情、提交、过账）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            if not self.ap_head_detail:
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "DONE":
                # 如果状态不是已过账，先执行提交和过账
                if current_status != "CONFIRM":
                    self.test_submit_ap_head()
                    self.test_query_ap_head_detail()
                # 执行过账
                self.test_post_ap_head_async_and_wait()
                # 过账后重新查询详情
                self.test_query_ap_head_detail()
            
            # ========== 步骤1：准备生成付款申请参数 ==========
            # 从curl请求分析，生成付款申请接口需要的参数：
            # - id: 应付单ID
            # - 其他字段从应付单详情中获取（使用详情数据）
            convert_dict = self.ap_head_detail.copy()
            
            # ========== 步骤2：发起异步生成付款申请任务 ==========
            # 调用异步生成付款申请接口，触发后台处理
            # 该接口会立即返回，不会等待任务完成，任务在后台异步执行
            response, _ = self.standard_api_call(
                api_key="应付单转化付款申请单-异步服务",
                set_dict=convert_dict
            )
            
            # 验证接口调用成功（HTTP状态码200，响应success=true）
            self.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建（CREATED状态表示任务已成功提交到队列）
            # 此时任务还未开始执行，只是进入了任务队列等待处理
            async_execution_status = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            if async_execution_status:
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "CREATED",
                    "异步任务发起生成付款申请状态应为CREATED，表示任务已成功提交到队列"
                )
            
            # ========== 步骤3：定义查询函数 ==========
            # 定义查询函数，用于轮询检查应付单的状态
            # 该函数会被异步等待工具多次调用，直到任务完成或超时
            def query_ap_status():
                """
                查询应付单状态
                
                功能说明：
                - 调用查询详情接口，获取应付单的当前状态
                - 返回的数据包含异步任务执行状态和应付单业务状态
                
                返回数据字段说明：
                - asyncExecutionStatus: 异步执行状态
                  * CREATED: 任务已创建，等待执行
                  * PROCESSING: 任务执行中
                  * SUCCEEDED: 任务执行成功
                  * FAILED: 任务执行失败
                - asyncExecutionFailureReason: 失败原因（仅在失败时存在）
                
                返回：
                    dict: 包含应付单的完整数据
                """
                response, _ = self.standard_api_call(
                    api_key="应付单详情查询服务",
                    set_dict={"id": self.ap_head_id}
                )
                self.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # ========== 步骤4：等待异步任务完成 ==========
            # 使用异步等待工具轮询查询任务状态，直到任务完成或超时
            result = self.async_wait_util.wait_for_async_status(
                query_func=query_ap_status,  # 查询函数，每次轮询时调用
                status_field="asyncExecutionStatus",  # 要检查的状态字段名
                success_status="SUCCEEDED",  # 成功状态值，达到此状态时停止等待
                failed_status="FAILED",  # 失败状态值，达到此状态时立即返回失败
                failure_reason_field="asyncExecutionFailureReason",  # 失败原因字段名，用于记录失败详情
                max_wait=60,  # 最大等待时间（秒），生成付款申请可能需要较长时间
                interval=2  # 轮询间隔（秒），每2秒查询一次状态
            )
            
            # ========== 步骤5：断言等待结果 ==========
            if result.status == self.wait_status.SUCCESS:
                # 等待成功，验证业务状态
                
                # 5.1 验证异步执行状态
                # 异步任务执行成功后，asyncExecutionStatus应该为SUCCEEDED
                async_execution_status = result.last_data.get("asyncExecutionStatus")
                self.assert_util.assert_by_operator(
                    async_execution_status, "=", "SUCCEEDED",
                    f"异步任务状态应为SUCCEEDED，实际状态: {async_execution_status}"
                )
                
                # 记录成功信息到Allure报告，便于查看测试执行详情
                a.text(
                    f"✅ 生成付款申请任务成功完成\n"
                    f"总耗时: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"应付单编号: {self.ap_head_detail.get('apHeadCode')}\n"
                    f"异步执行状态: {async_execution_status}",
                    "任务完成"
                )
                
                # 更新详情数据
                self.ap_head_detail = result.last_data
                
            elif result.status == self.wait_status.FAILED:
                # 任务失败，抛出异常并记录失败原因
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步生成付款申请任务失败: {failure_reason}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后数据: {result.last_data}"
                )
            elif result.status == self.wait_status.TIMEOUT:
                # 等待超时，抛出异常
                raise AssertionError(
                    f"⚠️ 等待异步生成付款申请任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}\n"
                    f"建议：检查任务是否正常执行，或增加max_wait时间"
                )
            else:
                # 其他错误（如查询过程出错、网络异常等）
                raise AssertionError(
                    f"等待异步生成付款申请任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"建议：检查网络连接和接口可用性"
                )
            
            # 记录关键数据
            a.json(convert_dict, "生成付款申请请求数据")
            a.json(response, "生成付款申请响应数据")
            
        except Exception as e:
            # 记录异常信息到Allure报告，便于问题排查
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单删除",
        description="验证应付单删除功能",
        severity="critical",
        file_level_order=16,
        tags=["应付单", "删除"]
    )
    def test_delete_ap_head(self):
        """测试应付单删除"""
        try:
            # 1. 确保有数据ID（如果没有则先创建）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            # 2. 准备删除参数
            set_dict = self.ap_head_detail
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付单删除服务",
                set_dict=set_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 记录关键数据
            a.json(set_dict, "删除请求数据")
            a.json(response, "删除响应数据")
            a.text(f"✅ 应付单删除成功，应付单ID: {self.ap_head_id}", "删除结果")
            
            # 6. 清空ID，避免后续测试使用已删除的数据
            self.ap_head_id = None
            self.ap_head_detail = None
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单批量删除",
        description="验证应付单批量删除功能",
        severity="critical",
        file_level_order=17,
        tags=["应付单", "批量删除"]
    )
    def test_batch_delete_ap_head(self):
        """测试应付单批量删除"""
        try:
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            set_dict = {"request": [self.ap_head_detail]}
          
            # 3. 使用标准化API调用
            # 注意：对于数组类型的set_dict，standard_api_call会自动处理
            response, _ = self.standard_api_call(
                api_key="AP-应付单批量删除服务",
                set_dict=set_dict,
                param_path=["params"]
                
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 记录关键数据
            a.json(set_dict, "批量删除请求数据")
            a.json(response, "批量删除响应数据")
            a.text(
                f"✅ 应付单批量删除成功，共删除 1 条应付单，ID: {self.ap_head_id}",
                "批量删除结果"
            )
            
            # 6. 清空ID列表，避免后续测试使用已删除的数据
            self.ap_head_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise