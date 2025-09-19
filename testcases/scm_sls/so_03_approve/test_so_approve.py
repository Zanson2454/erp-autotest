import pytest
import allure
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.report_util import a, case_decorator
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil


@allure.epic("销售管理")
@allure.feature("销售订单审批流程")
class TestSalesOrderApproval(SlsBase):
    """销售订单审批流程测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.order_id = None
        cls.approval_rule_code = "CODE2025090909583810028"
        cls.logger.info("销售订单审批流程测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.order_id:
                cls.db.delete(
                    table="sls_so_head_tr",
                    where="id = %s",
                    params=[cls.order_id]
                )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="销售订单审批流程",
        title="开启审单规则",
        description="测试开启编码为CODE2025090909583810028的审单规则",
        severity="critical",
        order=1,
        smoke=True,
        tags=["销售订单", "审批", "审单规则"]
    )
    def test_01_enable_approval_rule(self):
        """测试开启审单规则"""
        try:
            # 1. 调用开启审单规则API
            api_path = self.get_api_path("SLS-审单规则-启用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            url += "?tmodule=SCM_SLS"
            
            # 2. 构造审单规则启用请求体
            request_body = {
                "sceneKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE",
                "viewKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE:list",
                "viewTitle": "list",
                "buttonKey": "ERP_SCM$SLS_APPROVAL_RULE_MANAGE-detailView-actions-enable",
                "buttonName": "启用",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SO_APPROVAL_CF_ENABLE_AND_CLEAR_CACHE_ACTION_SERVICE",
                "params": {
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
            response = self.http.post(url, json=request_body)
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
    def test_02_create_and_submit_sales_order(self):
        """测试创建销售订单并提交，校验订单状态为审批中"""
        try:
            # 1. 创建销售订单并提交（确保金额满足审单规则条件 > 1000）
            self.order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 2. 查询订单状态，验证是否为审批中
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.order_id]
            )
            actual_status = order_status[0]['so_status']
            self.assert_util.assert_by_operator(actual_status, "=", "APPROVING", "订单状态必须为审批中")
                
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
    def test_03_approve_sales_order(self):
        """测试审批订单通过，校验订单状态为已生效"""
        try:
            # 1. 确保有审批中的订单
            if not self.order_id:
                self.test_02_create_and_submit_sales_order()
            
            # 2. 查询完整的订单数据
            order_data = self.db.query(f"""
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
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 6. 查询订单状态，验证是否为已生效
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.order_id]
            )
            actual_status = order_status[0]['so_status']
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
    def test_04_create_and_reject_sales_order(self):
        """测试创建销售订单并提交，然后审批拒绝"""
        try:
            # 1. 创建销售订单并提交（确保金额满足审单规则条件 > 1000）
            self.reject_order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 2. 查询订单状态，验证是否为审批中
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.reject_order_id]
            )
            actual_status = order_status[0]['so_status']
            self.assert_util.assert_by_operator(actual_status, "=", "APPROVING", "订单状态必须为审批中")
            
            # 3. 查询完整的订单数据
            order_data = self.db.query(f"""
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
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 8. 查询订单状态，验证是否为草稿状态（审批拒绝后回到草稿）
            order_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.reject_order_id]
            )
            actual_status = order_status[0]['so_status']
            self.assert_util.assert_by_operator(actual_status, "=", "DRAFT", "订单状态必须为草稿（审批拒绝后回到草稿状态）")
            
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单审批流程",
        title="停用审单规则",
        description="测试停用编码为CODE2025090909583810028的审单规则",
        severity="normal",
        order=5,
        tags=["销售订单", "审批", "审单规则"]
    )
    def test_05_disable_approval_rule(self):
        """测试停用审单规则"""
        try:
            # 1. 调用停用审单规则API
            api_path = self.get_api_path("SLS-审单规则-停用并清理缓存服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 添加URL参数
            url += "?tmodule=SCM_SLS"
            
            # 3. 构造完整的审单规则停用请求体
            request_body = {
                "sceneKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE",
                "viewKey": "SCM_SLS$SLS_APPROVAL_RULE_MANAGE:list",
                "viewTitle": "list",
                "buttonKey": "ERP_SCM$SLS_APPROVAL_RULE_MANAGE-detailView-actions-disable",
                "buttonName": "停用",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SO_APPROVAL_CF_DISABLE_AND_CLEAR_CACHE_ACTION_SERVICE",
                "params": {
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
            response = self.http.post(url, json=request_body)
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise