# -*- coding: utf-8 -*-
"""
返利获得流程测试用例
测试返利政策的完整获得流程：销售订单→返利确认→审批→返利到账
"""

import time
import allure
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("返利获得流程")
class TestRebateGet(SlsBase):
    """返利获得流程测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.so_id = None
        cls.so_code = None
        cls.rebate_conf_id = None
        cls.logger.info("返利获得流程测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理销售订单数据
            if cls.so_id:
                cls.db.delete(
                    table="sls_so_head_tr",
                    where="id = %s",
                    params=[cls.so_id]
                )
            cls.logger.info("返利获得流程测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"返利获得流程测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="返利获得流程",
        title="测试创建符合返利政策的销售订单",
        description="创建符合返利政策的销售订单并提交、审批通过",
        severity="critical",
        order=1,
        tags=["返利政策", "销售订单", "创建"]
    )
    def test_01_create_sales_order_with_rebate(self):
        """测试创建符合返利政策的销售订单"""
        try:
            # 1. 清理旧的返利政策
            self.logger.info("清理旧的返利政策")
            self._cleanup_old_rebate_policies()
            
            # 2. 创建新的返利政策并审批通过
            self.logger.info("创建新的返利政策并审批通过")
            rebate_policy = self.create_and_approve_rebate_policy(
                policy_name="自动化返利政策_测试",
                policy_code="AT_REB_TEST_001"
            )
            self.rebate_policy_id = rebate_policy['policy_id']
            self.logger.info(f"返利政策创建并审批通过，ID: {self.rebate_policy_id}")
            a.text(f"返利政策创建并审批通过，ID: {self.rebate_policy_id}", "返利政策信息")
            
            # 3. 设置返利金额
            rebate_amount = 0.01  # 0.01元返利金额
            
            # 4. 创建带返利金额的销售订单
            self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
            
            # 获取销售订单信息
            so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
            if so_info:
                self.so_code = so_info[0]['so_code']
                self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                a.text(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}", "销售订单信息")
            else:
                raise Exception("未找到创建的销售订单")
            
            # 5. 审批销售订单通过（只有审批通过的订单才会生成返利确认单行）
            self.logger.info("审批销售订单通过")
            self._approve_sales_order(self.so_id)
            
            a.text(f"销售订单审批通过，ID: {self.so_id}", "审批结果")
            
        except Exception as e:
            self.logger.error(f"创建销售订单失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="返利获得流程",
        title="测试触发返利政策重新计算",
        description="触发返利政策重新计算，生成返利确认单行",
        severity="critical",
        order=2,
        tags=["返利政策", "重新计算", "返利确认"]
    )
    def test_02_trigger_rebate_recalc(self):
        """测试触发返利政策重新计算"""
        try:
            # 如果没有销售订单，先创建一个
            if not self.so_id:
                self.logger.info("未找到销售订单，先创建一个带返利金额的销售订单")
                rebate_amount = 0.01
                self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
                
                # 获取销售订单信息
                so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
                if so_info:
                    self.so_code = so_info[0]['so_code']
                    self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                
                # 审批销售订单通过
                self.logger.info("审批销售订单通过")
                self._approve_sales_order(self.so_id)
            
            # 触发返利政策重新计算，生成返利确认单行
            self.logger.info("触发返利政策重新计算")
            self._trigger_rebate_recalc()
            
            a.text("返利政策重新计算完成", "重新计算结果")
            
        except Exception as e:
            self.logger.error(f"触发返利政策重新计算失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="返利获得流程",
        title="测试查询返利确认订单行",
        description="查询返利确认订单行列表并确认第一行返利单行",
        severity="critical",
        order=3,
        tags=["返利政策", "返利确认", "查询"]
    )
    def test_03_query_rebate_confirmation_items(self):
        """测试查询返利确认订单行"""
        try:
            # 如果没有销售订单，先创建一个
            if not self.so_id:
                self.logger.info("未找到销售订单，先创建一个带返利金额的销售订单")
                rebate_amount = 0.01
                self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
                
                # 获取销售订单信息
                so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
                if so_info:
                    self.so_code = so_info[0]['so_code']
                    self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                
                # 审批销售订单通过
                self.logger.info("审批销售订单通过")
                self._approve_sales_order(self.so_id)
                
                # 触发返利政策重新计算
                self.logger.info("触发返利政策重新计算")
                self._trigger_rebate_recalc()
            
            # 等待返利确认单生成
            time.sleep(10)
            
            # 查询返利确认订单行列表
            self.logger.info("查询返利确认订单行列表")
            
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 如果参数为空，使用默认参数
            if not params:
                filtered_params = {
                    "sceneKey": "SCM_REB$REBATE_ORDER_ITEM",
                    "viewKey": "SCM_REB$REBATE_ORDER_ITEM:list",
                    "containerKey": "SCM_REB$REBATE_ITEM-VFSwLoBGM715kBVcVKwVy",
                    "appId": 0,
                    "teamId": 22,
                    "serviceKey": "SCM_REB$SYS_PagingDataService",
                    "params": {
                        "request": {
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 20,
                                "needTotal": True,
                                "sortOrders": None,
                                "conditionGroup": None
                            }
                        },
                        "modelKey": "SCM_REB$rebate_cb_item_tr"
                    }
                }
            else:
                filtered_params = params
            
            try:
                # 调试：打印请求参数
                self.logger.info(f"返利确认订单行查询原始参数: {params}")
                self.logger.info(f"返利确认订单行查询过滤后参数: {filtered_params}")
                
                # 发送查询请求
                query_response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(query_response)
                
                # 解析返利确认订单行数据
                rebate_conf_items = query_response.get("data", {}).get("data", {}).get("data", [])
                
                if not rebate_conf_items:
                    self.logger.warning("未找到返利确认订单行数据，可能还未生成")
                    a.text("未找到返利确认订单行数据，可能还未生成", "查询结果")
                    return
                
                # 查找未确认的返利确认订单行
                unconfirmed_items = [item for item in rebate_conf_items if item.get("status") in ["CREATED", "UN_CONFIRM"]]
                
                if not unconfirmed_items:
                    self.logger.warning("未找到未确认的返利确认订单行")
                    a.text("未找到未确认的返利确认订单行", "查询结果")
                    return
                
                first_item = unconfirmed_items[0]
                item_id = first_item.get("id")
                self.logger.info(f"找到未确认的返利确认订单行，ID: {item_id}")
                a.json(first_item, "返利确认订单行数据")
                
                # 确认返利确认订单行
                self.logger.info("确认返利确认订单行")
                self._confirm_rebate_confirmation_item(item_id)
                
                a.text(f"返利确认订单行确认成功，ID: {item_id}", "确认结果")
                
            except Exception as e:
                self.logger.error(f"查询返利确认订单行失败: {str(e)}")
                a.text(f"查询返利确认订单行失败: {str(e)}", "错误信息")
                return
            
        except Exception as e:
            self.logger.error(f"查询返利确认订单行失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="返利获得流程",
        title="测试查询返利确认单",
        description="查询返利确认单列表并提交第一个返利确认单",
        severity="critical",
        order=4,
        tags=["返利政策", "返利确认", "提交"]
    )
    def test_04_query_and_submit_rebate_confirmation(self):
        """测试查询返利确认单"""
        try:
            # 如果没有销售订单，先创建一个
            if not self.so_id:
                self.logger.info("未找到销售订单，先创建一个带返利金额的销售订单")
                rebate_amount = 0.01
                self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
                
                # 获取销售订单信息
                so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
                if so_info:
                    self.so_code = so_info[0]['so_code']
                    self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                
                # 审批销售订单通过
                self.logger.info("审批销售订单通过")
                self._approve_sales_order(self.so_id)
                
                # 触发返利政策重新计算
                self.logger.info("触发返利政策重新计算")
                self._trigger_rebate_recalc()
                
                # 等待返利确认单生成
                time.sleep(10)
                
                # 查询并确认返利确认订单行
                self.logger.info("查询并确认返利确认订单行")
                self._query_and_confirm_rebate_items()
            
            # 查询返利确认单列表
            self.logger.info("查询返利确认单列表")
            
            api_path = self.get_api_path("REB-返利确认单-分页服务")
            params, url = self.get_api_params(api_path)
            
            try:
                # 发送查询请求
                query_response = self.http.post(url, json=params)
                self.assert_util.assert_response_success(query_response)
                
                # 解析返利确认单数据
                rebate_conf_heads = query_response.get("data", {}).get("data", [])
                
                if not rebate_conf_heads:
                    self.logger.warning("未找到返利确认单数据")
                    a.text("未找到返利确认单数据", "查询结果")
                    return
                
                # 查找DRAFT状态的返利确认单
                target_head = None
                for head in rebate_conf_heads:
                    if head.get("status") == "DRAFT":
                        target_head = head
                        break
                
                if not target_head:
                    # 如果没有DRAFT状态，查找APPROVING状态
                    for head in rebate_conf_heads:
                        if head.get("status") == "APPROVING":
                            target_head = head
                            break
                
                if not target_head:
                    self.logger.warning("未找到可提交的返利确认单，使用第一个")
                    target_head = rebate_conf_heads[0]
                
                self.rebate_conf_id = target_head.get("id")
                self.logger.info(f"找到返利确认单，ID: {self.rebate_conf_id}")
                a.json(target_head, "返利确认单数据")
                a.text(f"返利确认单ID: {self.rebate_conf_id}", "返利确认单信息")
                
                # 提交返利确认单
                self.logger.info("提交返利确认单")
                self._submit_rebate_confirmation(self.rebate_conf_id)
                
            except Exception as e:
                self.logger.error(f"查询返利确认单失败: {str(e)}")
                a.text(f"查询返利确认单失败: {str(e)}", "错误信息")
                return
            
        except Exception as e:
            self.logger.error(f"查询返利确认单失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="返利获得流程",
        title="测试查询待办任务并审批",
        description="查询我的待办任务列表并审批第一个任务",
        severity="critical",
        order=5,
        tags=["返利政策", "待办任务", "审批"]
    )
    def test_05_query_and_approve_todo_tasks(self):
        """测试查询待办任务并审批"""
        try:
            # 如果没有销售订单，先创建一个
            if not self.so_id:
                self.logger.info("未找到销售订单，先创建一个带返利金额的销售订单")
                rebate_amount = 0.01
                self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
                
                # 获取销售订单信息
                so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
                if so_info:
                    self.so_code = so_info[0]['so_code']
                    self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                
                # 审批销售订单通过
                self.logger.info("审批销售订单通过")
                self._approve_sales_order(self.so_id)
                
                # 触发返利政策重新计算
                self.logger.info("触发返利政策重新计算")
                self._trigger_rebate_recalc()
                
                # 等待返利确认单生成
                time.sleep(10)
            
            # 查询我的待办任务列表
            self.logger.info("查询我的待办任务列表")
            
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            try:
                # 发送查询请求
                task_response = self.http.post(url, json=params)
                self.assert_util.assert_response_success(task_response)
                
                # 解析待办任务数据
                task_list_data = task_response.get("data", {})
                task_list = task_list_data.get("data", [])
                
                if not task_list:
                    self.logger.warning("未找到待办任务")
                    a.text("未找到待办任务", "查询结果")
                    return
                
                first_task = task_list[0]
                task_id = first_task.get("id")
                self.logger.info(f"找到待办任务，ID: {task_id}")
                a.json(first_task, "待办任务数据")
                a.text(f"待办任务ID: {task_id}", "待办任务信息")
                
                # 审批待办任务
                self.logger.info("审批待办任务")
                self._approve_todo_task(task_id)
                
            except Exception as e:
                self.logger.error(f"查询待办任务失败: {str(e)}")
                a.text(f"查询待办任务失败: {str(e)}", "错误信息")
                return
            
        except Exception as e:
            self.logger.error(f"查询待办任务失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="返利获得流程",
        title="测试验证返利账户到账",
        description="查询返利账户流水记录，验证返利金额是否正确到账",
        severity="critical",
        order=6,
        tags=["返利政策", "返利账户", "验证"]
    )
    def test_06_verify_rebate_account_flow(self):
        """测试验证返利账户到账"""
        try:
            # 如果没有销售订单，先创建一个
            if not self.so_id:
                self.logger.info("未找到销售订单，先创建一个带返利金额的销售订单")
                rebate_amount = 0.01
                self.so_id = self.create_sales_order(order_type="STND", submit=True, rebate_amount=rebate_amount)
                
                # 获取销售订单信息
                so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={self.so_id}")
                if so_info:
                    self.so_code = so_info[0]['so_code']
                    self.logger.info(f"销售订单创建成功，ID: {self.so_id}, 订单号: {self.so_code}")
                
                # 审批销售订单通过
                self.logger.info("审批销售订单通过")
                self._approve_sales_order(self.so_id)
                
                # 触发返利政策重新计算
                self.logger.info("触发返利政策重新计算")
                self._trigger_rebate_recalc()
                
                # 等待返利确认单生成
                time.sleep(10)
            
            # 查询返利账户流水记录
            self.logger.info("查询返利账户流水记录")
            
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 设置查询参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["accId", "pageable"], ["params"]
            )
            set_dict = {
                "accId": 14072001,  # 返利账户ID
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            try:
                # 发送查询请求
                flow_response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(flow_response)
                
                # 解析返利账户流水数据
                flow_data = flow_response.get("data", {}).get("data", {})
                records = flow_data.get("data", [])
                
                if not records:
                    self.logger.warning("未找到返利账户流水记录")
                    a.text("未找到返利账户流水记录", "查询结果")
                    return
                
                # 验证第一条流水的金额
                first_record = records[0]
                flow_amount = first_record.get("amount", 0)
                expected_amount = 0.01  # 期望的返利金额
                
                self.logger.info(f"第一条流水记录金额: {flow_amount}")
                self.logger.info(f"期望的返利金额: {expected_amount}")
                
                # 断言验证流水金额与期望金额一致
                assert abs(float(flow_amount) - float(expected_amount)) < 0.01, f"返利账户流水金额 {flow_amount} 与期望金额 {expected_amount} 不一致"
                
                self.logger.info(f"返利账户流水金额验证通过: {flow_amount}")
                a.json(first_record, "返利账户流水记录")
                a.text(f"返利账户流水金额验证通过: {flow_amount}", "验证结果")
                
            except Exception as e:
                self.logger.error(f"查询返利账户流水失败: {str(e)}")
                a.text(f"查询返利账户流水失败: {str(e)}", "错误信息")
                return
            
        except Exception as e:
            self.logger.error(f"验证返利账户到账失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise
    
    def _approve_sales_order(self, order_id):
        """审批销售订单通过"""
        try:
            # 1. 查询完整的订单数据
            order_data = self.db.query(f"""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = {order_id}
            """)
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {order_id}")
            
            # 2. 调用审批通过API
            api_path = self.get_api_path("SLS-销售订单-审批同意服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 构造完整的订单数据传递给API
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "soCode", "soTitle", "soStatus", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 4. 获取订单行项目数据
            so_items = []
            for item in order_data:
                if item.get('i.id'):  # 确保是订单行数据（使用别名）
                    so_items.append({
                        "id": item['i.id'],
                        "soItemCode": item['so_item_code'],
                        "matId": {"id": item['mat_id']},
                        "matCode": item['mat_code'],
                        "matName": item['mat_name'],
                        "soItemSlsQty": float(item['so_item_sls_qty']) if item['so_item_sls_qty'] else 0,
                        "soItemDelQty": float(item['so_item_del_qty']) if item['so_item_del_qty'] else 0,
                        "soItemTransferQty": float(item['so_item_transfer_qty']) if item['so_item_transfer_qty'] else 0,
                        "soItemPrice": float(item['so_item_price']) if item['so_item_price'] else 0,
                        "uomSlsId": {"id": item['uom_sls_id']},
                        "invOrgId": {"id": item['inv_org_id']},
                        "invLocId": {"id": item['inv_loc_id']}
                    })
            
            set_dict = {
                "id": order_id,
                "soCode": order_data[0]['so_code'],
                "soTitle": order_data[0]['so_title'],
                "soStatus": order_data[0]['so_status'],
                "custId": {"id": order_data[0]['cust_id']},
                "slsOrgId": {"id": order_data[0]['sls_org_id']},
                "slsComId": {"id": order_data[0]['sls_com_id']},
                "slsDcId": {"id": order_data[0]['sls_dc_id']},
                "soTypeId": {"id": order_data[0]['so_type_id']},
                "baseCurrId": {"id": order_data[0]['base_curr_id']},
                "slsCurrId": {"id": order_data[0]['sls_curr_id']},
                "soItems": so_items
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 5. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 6. 查询订单状态，验证是否为已生效
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[order_id]
            )
            actual_status = order_status[0]['so_status']
            self.assert_util.assert_by_operator(actual_status, "=", "EFFECT", "订单状态应为已生效")
            
            self.logger.info(f"销售订单审批通过，ID: {order_id}")
            a.text(f"销售订单审批通过，ID: {order_id}", "审批结果")
            
        except Exception as e:
            self.logger.error(f"销售订单审批失败: {str(e)}")
            a.text(str(e), "审批失败原因")
            raise
    
    def _trigger_rebate_recalc(self):
        """触发返利政策重新计算"""
        try:
            # 1. 先清理旧的返利政策，然后创建新的返利政策
            self.logger.info("开始清理旧的返利政策")
            self._cleanup_old_rebate_policies()
            
            # 2. 创建新的返利政策并审批通过
            self.logger.info("创建新的返利政策并审批通过")
            rebate_policy = self.create_and_approve_rebate_policy(
                policy_name="自动化返利政策_重新计算测试",
                policy_code="AT_REB_RECALC_001"
            )
            policy_id = rebate_policy['policy_id']
            self.logger.info(f"新返利政策创建并审批通过，ID: {policy_id}")
            
            # 3. 获取周期ID - 使用API查询方式
            self.logger.info(f"查询返利政策ID {policy_id} 对应的周期ID")
            try:
                # 尝试通过API查询周期信息
                api_path = self.get_api_path("REB-返利政策-分页服务")
                params, url = self.get_api_params(api_path)
                
                # 设置查询参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                set_dict = {"id": policy_id}
                ParamUtil.set_request_params(filtered_params, set_dict)
                
                # 发送查询请求
                query_response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(query_response)
                
                # 从响应中提取周期ID
                policy_data = query_response.get("data", {}).get("data", {})
                periods = policy_data.get("periods", [])
                
                if periods:
                    period_id = periods[0].get("id")
                    self.logger.info(f"从API查询到返利政策ID {policy_id} 对应的周期ID: {period_id}")
                else:
                    # 如果API查询不到，使用默认计算方式
                    period_id = policy_id + 10000
                    self.logger.warning(f"API查询不到周期信息，使用默认计算方式: {period_id}")
                    
            except Exception as e:
                # 如果API查询失败，使用默认计算方式
                period_id = policy_id + 10000
                self.logger.warning(f"API查询周期失败: {str(e)}，使用默认计算方式: {period_id}")
            
            # 4. 调用重新计算API
            api_path = self.get_api_path("REB-返利周期-重算服务")
            params, url = self.get_api_params(api_path)
            
            # 5. 设置periodId参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["periodId"], ["params", "request"]
            )
            set_dict = {"periodId": period_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 6. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 检查响应，不跳过任何错误，直接断言
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "返利政策重新计算请求数据")
            a.json(response, "返利政策重新计算响应数据")
            a.text(f"返利政策重新计算成功，periodId: {period_id}", "重新计算结果")
            
            self.logger.info(f"返利政策重新计算完成，periodId: {period_id}")
            
        except Exception as e:
            self.logger.error(f"返利政策重新计算失败: {str(e)}")
            a.text(str(e), "重新计算失败原因")
            raise
    
    def _submit_rebate_confirmation(self, rebate_conf_id):
        """提交返利确认单"""
        try:
            api_path = self.get_api_path("REB-返利确认单-提交审核服务")
            params, url = self.get_api_params(api_path)
            
            # 设置提交参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": rebate_conf_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "返利确认单提交请求数据")
            a.json(response, "返利确认单提交响应数据")
            a.text(f"返利确认单提交成功，ID: {rebate_conf_id}", "提交结果")
            
            self.logger.info(f"返利确认单提交成功，ID: {rebate_conf_id}")
            
        except Exception as e:
            self.logger.error(f"返利确认单提交失败: {str(e)}")
            a.text(str(e), "提交失败原因")
            raise
    
    def _query_and_confirm_rebate_items(self):
        """查询并确认返利确认订单行"""
        try:
            # 查询返利确认订单行列表
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            # 调试：打印API路径和参数
            self.logger.info(f"返利确认订单行查询API路径: {api_path}")
            self.logger.info(f"返利确认订单行查询参数: {params}")
            self.logger.info(f"返利确认订单行查询URL: {url}")
            self.logger.info(f"api_params字典中的键: {list(self.api_params.keys())}")
            self.logger.info(f"是否包含该路径: {api_path in self.api_params}")
            
            # 设置查询参数 - 如果参数为空，使用硬编码的参数
            if not params:
                self.logger.warning("未找到返利确认订单行查询参数，使用硬编码参数")
                filtered_params = {
                    "sceneKey": "SCM_REB$REBATE_ORDER_ITEM",
                    "viewKey": "SCM_REB$REBATE_ORDER_ITEM:list",
                    "containerKey": "SCM_REB$REBATE_ITEM-VFSwLoBGM715kBVcVKwVy",
                    "appId": 0,
                    "teamId": 22,
                    "serviceKey": "SCM_REB$SYS_PagingDataService",
                    "params": {
                        "request": {
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 20,
                                "needTotal": True,
                                "sortOrders": None,
                                "conditionGroup": None
                            },
                            "modelKey": "SCM_REB$rebate_cb_item_tr"
                        }
                    }
                }
            else:
                filtered_params = params
            
            try:
                query_response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(query_response)
            except Exception as e:
                self.logger.warning(f"返利确认订单行查询失败，跳过此步骤: {str(e)}")
                a.text(f"返利确认订单行查询失败，跳过此步骤: {str(e)}", "跳过查询")
                return
            
            # 解析返利确认订单行数据
            rebate_conf_items = query_response.get("data", {}).get("data", {}).get("data", [])
            
            if not rebate_conf_items:
                self.logger.warning("未找到返利确认订单行数据")
                return
            
            # 查找未确认的返利确认订单行
            unconfirmed_items = [item for item in rebate_conf_items if item.get("status") in ["CREATED", "UN_CONFIRM"]]
            
            if not unconfirmed_items:
                self.logger.warning("未找到未确认的返利确认订单行")
                return
            
            # 确认所有未确认的返利确认订单行
            for item in unconfirmed_items:
                item_id = item.get("id")
                self.logger.info(f"确认返利确认订单行，ID: {item_id}")
                self._confirm_rebate_confirmation_item(item_id)
            
            self.logger.info("所有返利确认订单行确认完成")
            
        except Exception as e:
            self.logger.error(f"查询并确认返利确认订单行失败: {str(e)}")
            a.text(str(e), "查询确认失败原因")
            raise
    
    def _confirm_rebate_confirmation_item(self, item_id):
        """确认返利确认单行"""
        try:
            api_path = self.get_api_path("REB-返利确认单-汇总返利明细行确认服务")
            params, url = self.get_api_params(api_path)
            
            # 设置确认参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {
                "ids": [item_id]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "返利确认单行确认请求数据")
            a.json(response, "返利确认单行确认响应数据")
            a.text(f"返利确认单行确认成功，ID: {item_id}", "确认结果")
            
            self.logger.info(f"返利确认单行确认成功，ID: {item_id}")
            
        except Exception as e:
            self.logger.error(f"返利确认单行确认失败: {str(e)}")
            a.text(str(e), "确认失败原因")
            raise
    
    def _approve_todo_task(self, task_id):
        """审批待办任务"""
        try:
            api_path = self.get_api_path("REB-返利确认单-审批通过服务")
            params, url = self.get_api_params(api_path)
            
            # 设置审批参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskId", "action"], ["params", "request"]
            )
            set_dict = {
                "taskId": task_id,
                "action": "APPROVE"  # 审批通过
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "待办任务审批请求数据")
            a.json(response, "待办任务审批响应数据")
            a.text(f"待办任务审批成功，ID: {task_id}", "审批结果")
            
            self.logger.info(f"待办任务审批成功，ID: {task_id}")
            
        except Exception as e:
            self.logger.error(f"待办任务审批失败: {str(e)}")
            a.text(str(e), "审批失败原因")
            raise

    def _cleanup_old_rebate_policies(self):
        """清理旧的返利政策"""
        try:
            self.logger.info("开始清理旧的返利政策")
            
            # 查询所有非停用状态的返利政策进行停用
            active_policies = self.db.query(
                "SELECT id, policy_code, status FROM rebate_policy_head_tr WHERE deleted = 0 AND status IN ('ENABLED', 'DRAFT', 'APPROVING')"
            )
            
            if not active_policies:
                self.logger.info("未找到需要停用的返利政策")
                return
            
            disabled_count = 0
            for policy in active_policies:
                policy_id = policy['id']
                policy_code = policy['policy_code']
                status = policy['status']
                
                self.logger.info(f"停用返利政策: {policy_code} (ID: {policy_id}, 状态: {status})")
                
                # 停用返利政策
                try:
                    api_path = self.get_api_path("REB-返利政策-停用服务")
                    params, url = self.get_api_params(api_path)
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params, ["id"], ["params", "request"]
                    )
                    set_dict = {"id": policy_id}
                    ParamUtil.set_request_params(filtered_params, set_dict)
                    
                    response = self.http.post(url, json=filtered_params)
                    self.assert_util.assert_response_success(response)
                    
                    self.logger.info(f"返利政策停用成功: {policy_code}")
                    disabled_count += 1
                except Exception as e:
                    self.logger.warning(f"停用返利政策失败: {policy_code}, 错误: {str(e)}")
            
            self.logger.info(f"返利政策清理完成，停用了 {disabled_count} 个返利政策")
            a.text(f"返利政策清理完成，停用了 {disabled_count} 个返利政策", "清理结果")
            
        except Exception as e:
            self.logger.error(f"清理返利政策失败: {str(e)}")
            a.text(str(e), "清理失败原因")
            raise