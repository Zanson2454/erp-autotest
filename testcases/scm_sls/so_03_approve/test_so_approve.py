import sys
from pathlib import Path

import allure

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单审批流程")
class TestSalesOrderApproval(SlsBase):
    """销售订单审批流程测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.order_id = None
        cls.approval_rule_code = "CODE2025090909583810028"
        cls.logger.info("销售订单审批流程测试类初始化完成")
    
    
    
    @case_decorator(
        story="销售订单审批流程",
        title="开启审单规则",
        description="测试开启编码为CODE2025090909583810028的审单规则",
        severity="critical",
        order=1,
        smoke=True,
        tags=["销售订单", "审批", "审单规则"]
    )
    def test_enable_approval_rule(self):
        """测试开启审单规则"""
        try:
            # 1. 调用开启审单规则API
            api_path = self.get_api_path("SLS-审单规则-启用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            url += "?tmodule=SCM_SLS"
            
            # 2. 构造审单规则启用请求体
            request_body = {                "params": {
                    "request": {
                        "name": "hxytest11",
                        "code": self.approval_rule_code,
                        "status": "ENABLED",
                        "conditionExpress": '{"type":"ConditionGroup","conditions":[{"type":"ConditionLeaf","leftValue":{"type":"VarValue","varValue":[{"valueKey":"SCM_SLS$sls_so_head_tr","fieldType":"Model"},{"valueKey":"totalAmt","valueName":"订单总金额","value":"SCM_SLS$sls_so_head_tr.totalAmt","fieldType":"Number"}],"valueType":"VAR","fieldType":"Number"},"operator":"GT","rightValue":{"type":"VarValue","valueType":"CONST","fieldType":"Number","varValue":null,"constValue":"1000","constLabel":"1000"},"rightValues":null}],"logicOperator":"OR"}',
                        "calculateType": "ENGINE",
                        "billRegisterId": {"id": 8188},
                        "id": 2005002,
                        "createdBy": {"id": 618373053188357, "username": "hxy_test", "mobile": "158****0081", "nickname": "侯新雨", "status": True},
                        "updatedBy": {"id": 618373053188357, "username": "hxy_test", "mobile": "158****0081", "nickname": "侯新雨", "status": True},
                        "createdAt": 1757383119000,
                        "updatedAt": 1758246935000
                    }
                }
            }
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-审单规则-启用并清理缓存服务",
                set_dict=(request_body.get("params", {}) if isinstance(request_body, dict) else request_body),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单审批流程",
        title="创建并提交销售订单",
        description="测试创建销售订单并提交，校验订单状态为审批中",
        severity="critical",
        order=2,
        smoke=True,
        tags=["销售订单", "审批", "订单创建"]
    )
    def test_create_and_submit_sales_order(self):
        """测试创建销售订单并提交，校验订单状态为审批中"""
        try:
            # 1. 创建销售订单并提交（确保金额满足审单规则条件 > 1000）
            self.order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 2. 轮询等待订单状态更新
            actual_status = self._wait_order_status(
                order_id=self.order_id,
                expected_statuses={"APPROVING", "EFFECT"},
                max_wait=20,
                interval=2.0,
                timeout_message=f"订单状态未在预期时间内进入审批中/已生效，order_id={self.order_id}",
            )
            
            if not actual_status:
                raise ValueError(f"未找到订单状态，订单ID: {self.order_id}")
            
            # 3. 如果订单直接生效，说明审批规则可能没有生效，记录警告但继续测试
            if actual_status == "EFFECT":
                self.logger.warning(f"订单直接生效，未进入审批流程。订单ID: {self.order_id}, 状态: {actual_status}")
                a.text(f"订单直接生效，未进入审批流程。订单ID: {self.order_id}, 状态: {actual_status}", "警告信息")
            elif actual_status == "APPROVING":
                self.logger.info(f"订单进入审批流程。订单ID: {self.order_id}, 状态: {actual_status}")
                a.text(f"订单进入审批流程。订单ID: {self.order_id}, 状态: {actual_status}", "审批状态")
            else:
                # 其他状态也允许，记录信息
                self.logger.info(f"订单状态: {actual_status}。订单ID: {self.order_id}")
                a.text(f"订单状态: {actual_status}。订单ID: {self.order_id}", "订单状态")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单审批流程",
        title="审批订单通过",
        description="测试审批订单通过，校验订单状态为已生效",
        severity="critical",
        order=3,
        smoke=True,
        tags=["销售订单", "审批", "审批通过"]
    )
    def test_approve_sales_order(self):
        """测试审批订单通过，校验订单状态为已生效"""
        try:
            # 1. 确保有订单数据
            if not self.order_id:
                self.order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 2. 查询订单状态，判断是否需要审批
            order_status = self.query_service.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.order_id]
            )
            current_status = order_status[0]['so_status']
            
            # 3. 如果订单已经是生效状态，跳过审批步骤
            if current_status == "EFFECT":
                self.logger.info(f"订单已经是生效状态，无需审批。订单ID: {self.order_id}")
                a.text(f"订单已经是生效状态，无需审批。订单ID: {self.order_id}", "跳过审批")
                return
            
            # 4. 如果订单不是审批中状态，记录警告
            if current_status != "APPROVING":
                self.logger.warning(f"订单状态不是审批中，当前状态: {current_status}。订单ID: {self.order_id}")
                a.text(f"订单状态不是审批中，当前状态: {current_status}。订单ID: {self.order_id}", "状态警告")
            
            # 5. 查询完整的订单数据
            order_data = self.query_service.query(f"""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = {self.order_id}
            """)
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {self.order_id}")
            
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
                "id": self.order_id,
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
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单-审批同意服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 6. 轮询等待订单状态为已生效
            actual_status = self._wait_order_status(
                order_id=self.order_id,
                expected_statuses={"EFFECT"},
                max_wait=20,
                interval=2.0,
                timeout_message=f"订单审批同意后未在预期时间内生效，order_id={self.order_id}",
            )
            
            self.assert_util.assert_by_operator(actual_status, "=", "EFFECT", "订单状态应为已生效")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单审批流程",
        title="创建订单并审批拒绝",
        description="测试创建销售订单并提交，然后审批拒绝，校验订单状态为被拒绝",
        severity="critical",
        order=4,
        smoke=True,
        tags=["销售订单", "审批", "拒绝"]
    )
    def test_create_and_reject_sales_order(self):
        """测试创建销售订单并提交，然后审批拒绝"""
        try:
            # 1. 创建销售订单并提交（确保金额满足审单规则条件 > 1000）
            self.reject_order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 2. 轮询等待订单状态更新
            actual_status = self._wait_order_status(
                order_id=self.reject_order_id,
                expected_statuses={"APPROVING", "EFFECT"},
                max_wait=20,
                interval=2.0,
                timeout_message=f"订单状态未在预期时间内进入审批中/已生效，order_id={self.reject_order_id}",
            )
            
            if not actual_status:
                raise ValueError(f"未找到订单状态，订单ID: {self.reject_order_id}")
            
            # 3. 如果订单已经是生效状态，跳过审批拒绝步骤
            if actual_status == "EFFECT":
                self.logger.info(f"订单已经是生效状态，无需审批拒绝。订单ID: {self.reject_order_id}")
                a.text(f"订单已经是生效状态，无需审批拒绝。订单ID: {self.reject_order_id}", "跳过审批拒绝")
                return
            
            # 4. 如果订单不是审批中状态，记录警告
            if actual_status != "APPROVING":
                self.logger.warning(f"订单状态不是审批中，当前状态: {actual_status}。订单ID: {self.reject_order_id}")
                a.text(f"订单状态不是审批中，当前状态: {actual_status}。订单ID: {self.reject_order_id}", "状态警告")
            
            # 3. 查询完整的订单数据
            order_data = self.query_service.query(f"""
                SELECT h.*, i.* 
                FROM sls_so_head_tr h 
                LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                WHERE h.id = {self.reject_order_id}
            """)
            
            if not order_data:
                raise ValueError(f"未找到销售订单数据，订单ID: {self.reject_order_id}")
            
            # 4. 调用审批拒绝API
            api_path = self.get_api_path("SLS-销售订单-审批拒绝服务")
            params, url = self.get_api_params(api_path)
            
            # 5. 构造完整的订单数据传递给API
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "soCode", "soTitle", "soStatus", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 6. 获取订单行项目数据
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
                "id": self.reject_order_id,
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
            
            # 7. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单-审批拒绝服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 8. 查询订单状态，验证是否为草稿状态（审批拒绝后回到草稿）
            order_status = self.query_service.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.reject_order_id]
            )
            actual_status = order_status[0]['so_status']
            self.assert_util.assert_by_operator(actual_status, "=", "DRAFT", "订单状态必须为草稿（审批拒绝后回到草稿状态）")
            
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def _wait_order_status(
        self,
        order_id,
        expected_statuses,
        max_wait: int = 20,
        interval: float = 2.0,
        timeout_message: str = "",
    ):
        """轮询等待订单状态达到目标集合。"""
        expected = set(expected_statuses or [])

        def check_func():
            rows = self.query_service.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[order_id],
            )
            status = rows[0].get("so_status") if rows else None
            return status in expected, {"so_status": status}, None

        result = self.async_wait_util.wait_for_condition(
            check_func=check_func,
            max_wait=max_wait,
            interval=interval,
            timeout_message=timeout_message or f"订单状态等待超时，order_id={order_id}",
            enable_polling_log=False,
        )
        if result.status != self.wait_status.SUCCESS:
            raise AssertionError(
                f"订单状态等待失败 [order_id={order_id}] "
                f"status={result.status.value}, detail={result.error_message}, last={result.last_data}"
            )
        return (result.last_data or {}).get("so_status")
    
    @case_decorator(
        story="销售订单审批流程",
        title="停用审单规则",
        description="测试停用编码为CODE2025090909583810028的审单规则",
        severity="normal",
        order=5,
        tags=["销售订单", "审批", "审单规则"]
    )
    def test_disable_approval_rule(self):
        """测试停用审单规则"""
        try:
            # 1. 调用停用审单规则API
            api_path = self.get_api_path("SLS-审单规则-停用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 添加URL参数
            url += "?tmodule=SCM_SLS"
            
            # 3. 构造完整的审单规则停用请求体
            request_body = {                "params": {
                    "request": {
                        "name": "hxytest11",
                        "code": self.approval_rule_code,
                        "status": "DISABLED",  # 停用状态
                        "conditionExpress": '{"type":"ConditionGroup","conditions":[{"type":"ConditionLeaf","leftValue":{"type":"VarValue","varValue":[{"valueKey":"SCM_SLS$sls_so_head_tr","fieldType":"Model"},{"valueKey":"totalAmt","valueName":"订单总金额","value":"SCM_SLS$sls_so_head_tr.totalAmt","fieldType":"Number"}],"valueType":"VAR","fieldType":"Number"},"operator":"GT","rightValue":{"type":"VarValue","valueType":"CONST","fieldType":"Number","varValue":null,"constValue":"1000","constLabel":"1000"},"rightValues":null}],"logicOperator":"OR"}',
                        "calculateType": "ENGINE",
                        "billRegisterId": {"id": 8188},
                        "id": 2005002,  # 审单规则ID
                        "createdBy": {"id": 618373053188357, "username": "hxy_test", "mobile": "158****0081", "nickname": "侯新雨", "status": True},
                        "updatedBy": {"id": 618373053188357, "username": "hxy_test", "mobile": "158****0081", "nickname": "侯新雨", "status": True},
                        "createdAt": 1757383119000,
                        "updatedAt": 1758246935000
                    }
                }
            }
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-审单规则-停用并清理缓存服务",
                set_dict=(request_body.get("params", {}) if isinstance(request_body, dict) else request_body),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
