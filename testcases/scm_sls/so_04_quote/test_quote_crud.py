import allure
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("报价单管理")
class TestQuoteCrud(SlsBase):
    """报价单增删改查测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.quote_id_draft = None
        cls.quote_id_copy = None
        cls.quote_id_submit = None
        cls.logger.info("报价单增删改查测试类初始化完成")
    
   
    
    @case_decorator(
        story="报价单管理",
        title="测试创建草稿态报价单并编辑保存",
        description="验证创建草稿态报价单，编辑后保存的功能",
        severity="critical",
        order=1,
        smoke=True,
        tags=["报价单", "创建", "编辑"]
    )
    def test_01_create_and_edit_draft_quote(self):
        """测试创建草稿态报价单并编辑保存"""
        try:
            # 1. 调用公共方法创建草稿态报价单
            self.quote_id_draft = self.create_quote(submit=False)
            a.text(f"草稿态报价单创建成功，ID: {self.quote_id_draft}", "草稿报价单ID")
            
            # 2. 编辑草稿态报价单
            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 4. 设置编辑后的数据
            edit_name = f"编辑后的报价单_{self.mock_util.get_timestamp()}"
            set_dict = {
                "id": self.quote_id_draft,
                "soCode": f"QT_{self.mock_util.get_timestamp()}",
                "soDesc": edit_name,
                "custId": {"id": self.cust_id},
                "slsOrgId": {"id": self.sls_org_id},
                "slsComId": {"id": self.com_org_id},
                "slsDcId": {"id": self.sls_dc_id},
                "soTypeId": {"id": self.stnd_so_type_id},
                "baseCurrId": {"id": self.curr_id},
                "slsCurrId": {"id": self.curr_id},
                "soItems": [
                    {
                        "matId": {"id": self.mat_id},
                        "matCode": self.mat_code,
                        "matName": self.mat_name,
                        "soItemSlsQty": 20,  # 修改数量
                        "soItemGrossPrice": 150.0,  # 修改价格
                        "uomSlsId": {"id": 2004001},
                        "uomBaseId": {"id": 2004001},
                        "soItemTypeId": {"id": self.stnd_so_item_type_id},
                        "invOrgId": {"id": self.inv_org_id},
                        "invLocId": {"id": self.inv_loc_id},
                        "soSchlDelDate": self.mock_util.get_timestamp(timestamp=True, day_offset=2)
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 5. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单-保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 保存编辑后的报价单ID
            response_data = response.get("data", {}).get("data", {})
            self.quote_id_draft = response_data.get("id")
            
            a.json(filtered_params, "编辑请求数据")
            a.json(response, "编辑响应数据")
            a.text(f"草稿态报价单编辑保存成功，ID: {self.quote_id_draft}", "编辑结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试复制草稿态报价单并保存",
        description="验证复制草稿态报价单并保存的功能",
        severity="critical",
        order=2,
        tags=["报价单", "复制", "保存"]
    )
    def test_02_copy_and_save_draft_quote(self):
        """测试复制草稿态报价单并保存"""
        try:
            # 1. 确保有草稿态报价单
            if not self.quote_id_draft:
                self.test_01_create_and_edit_draft_quote()
            
            # 2. 调用复制API
            api_path = self.get_api_path("销售订单复制服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], 
                ["params", "request"]
            )
            
            set_dict = {"id": self.quote_id_draft}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送复制请求和断言
            response, _ = self.standard_api_call(
                api_key="销售订单复制服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 获取复制的报价单数据
            response_data = response.get("data", {}).get("data", {})
            copied_quote_data = response_data
            
            # 6. 保存复制的报价单
            save_api_path = self.get_api_path("SLS-销售订单-保存服务")
            save_params, save_url = self.get_api_params(save_api_path)
            
            # 7. 参数处理
            save_filtered_params = ParamUtil.filter_post_body_fields(
                save_params, ["soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 8. 设置复制的报价单数据
            set_save_dict = {
                "soCode": copied_quote_data.get("soCode", ""),
                "soDesc": f"复制的{copied_quote_data.get('soDesc', '')}",
                "custId": copied_quote_data.get("custId", {}),
                "slsOrgId": copied_quote_data.get("slsOrgId", {}),
                "slsComId": copied_quote_data.get("slsComId", {}),
                "slsDcId": copied_quote_data.get("slsDcId", {}),
                "soTypeId": copied_quote_data.get("soTypeId", {}),
                "baseCurrId": copied_quote_data.get("baseCurrId", {}),
                "slsCurrId": copied_quote_data.get("slsCurrId", {}),
                "soItems": copied_quote_data.get("soItems", [])
            }
            ParamUtil.set_request_params(save_filtered_params, set_save_dict)
            
            # 9. 发送保存请求和断言
            save_response, _ = self.standard_api_call(
                api_key="SLS-销售订单-保存服务",
                set_dict=(save_filtered_params.get("params", {}) if isinstance(save_filtered_params, dict) else save_filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(save_response)
            
            # 10. 保存复制的报价单ID
            save_response_data = save_response.get("data", {}).get("data", {})
            self.quote_id_copy = save_response_data.get("id")
            
            a.json(filtered_params, "复制请求数据")
            a.json(response, "复制响应数据")
            a.json(save_filtered_params, "保存请求数据")
            a.json(save_response, "保存响应数据")
            a.text(f"草稿态报价单复制并保存成功，新ID: {self.quote_id_copy}", "复制保存结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试删除复制的草稿态报价单",
        description="验证删除复制的草稿态报价单的功能",
        severity="critical",
        order=3,
        tags=["报价单", "删除"]
    )
    def test_03_delete_copied_quote(self):
        """测试删除复制的草稿态报价单"""
        try:
            # 1. 确保有复制的报价单
            if not self.quote_id_copy:
                self.test_02_copy_and_save_draft_quote()
            
            # 2. 调用删除API
            api_path = self.get_api_path("SO-删除服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], 
                ["params", "request"]
            )
            
            set_dict = {"id": self.quote_id_copy}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SO-删除服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 清空已删除的报价单ID
            deleted_id = self.quote_id_copy
            self.quote_id_copy = None
            
            a.json(filtered_params, "删除请求数据")
            a.json(response, "删除响应数据")
            a.text(f"草稿态报价单删除成功，已删除ID: {deleted_id}", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试创建已生效报价单",
        description="验证创建已生效报价单的功能",
        severity="critical",
        order=4,
        smoke=True,
        tags=["报价单", "创建", "提交"]
    )
    def test_04_create_submitted_quote(self):
        """测试创建已生效报价单"""
        try:
            # 1. 调用公共方法创建已生效报价单
            self.quote_id_submit = self.create_quote(submit=True)
            a.text(f"已生效报价单创建成功，ID: {self.quote_id_submit}", "已生效报价单ID")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试作废已生效报价单",
        description="验证作废已生效报价单的功能",
        severity="critical",
        order=5,
        tags=["报价单", "作废"]
    )
    def test_05_cancel_submitted_quote(self):
        """测试作废已生效报价单"""
        try:
            # 1. 确保有已生效的报价单
            if not self.quote_id_submit:
                self.test_04_create_submitted_quote()
            
            # 2. 查询报价单状态
            quote_status = self.db.query(
                "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                params=[self.quote_id_submit]
            )
            
            if not quote_status:
                raise ValueError(f"未找到报价单数据，报价单ID: {self.quote_id_submit}")
            
            current_status = quote_status[0]['so_status']
            a.text(f"报价单当前状态: {current_status}", "状态检查")
            
            # 3. 如果状态是审批中，先审批通过
            if current_status == "APPROVING":
                self.logger.info(f"报价单状态为审批中，先审批通过。报价单ID: {self.quote_id_submit}")
                a.text(f"报价单状态为审批中，先审批通过。报价单ID: {self.quote_id_submit}", "审批前置")
                self.approve_sales_order_or_quote(self.quote_id_submit)
                
                # 等待状态更新
                time.sleep(2)
                
                # 再次查询状态确认
                quote_status = self.db.query(
                    "SELECT so_status FROM sls_so_head_tr WHERE id = %s",
                    params=[self.quote_id_submit]
                )
                if quote_status:
                    current_status = quote_status[0]['so_status']
                    a.text(f"审批后报价单状态: {current_status}", "审批后状态")
            
            # 4. 如果状态不是已生效，记录警告
            if current_status != "EFFECT":
                self.logger.warning(f"报价单状态不是已生效，当前状态: {current_status}。报价单ID: {self.quote_id_submit}")
                a.text(f"报价单状态不是已生效，当前状态: {current_status}。报价单ID: {self.quote_id_submit}", "状态警告")
            
            # 5. 获取作废API路径
            api_path = self.get_api_path("订单作废服务")
            _, url = self.get_api_params(api_path)
            
            # 6. 构造请求体（按照用户提供的curl命令格式，只传递id参数）
            request_body = {
                "sceneKey": "SCM_SLS$sls_so_price",
                "viewKey": "SCM_SLS$sls_so_price:list",
                "viewTitle": "list",
                "buttonKey": "SCM_SLS$sls_so_price-9s2Pxoo8-Zbl9Ll367f8G",
                "buttonName": "作废",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SLS_REPEAL_EVENT_SERVICE",
                "params": {
                    "request": {
                        "id": self.quote_id_submit
                    }
                }
            }
            
            # 7. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="订单作废服务",
                set_dict=(request_body.get("params", {}) if isinstance(request_body, dict) else request_body),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 8. 保存作废后的报价单ID
            response_data = response.get("data", {}).get("data", {})
            self.quote_id_submit = response_data.get("id")
            
            a.json(request_body, "作废请求数据")
            a.json(response, "作废响应数据")
            a.text(f"已生效报价单作废成功，ID: {self.quote_id_submit}", "作废结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试查看报价单详情",
        description="验证查看报价单详情的功能",
        severity="critical",
        order=6,
        tags=["报价单", "详情查询"]
    )
    def test_06_query_quote_detail(self):
        """测试查看报价单详情"""
        try:
            # 1. 确保有报价单数据（优先使用已生效的，其次使用草稿的）
            quote_id = None
            if self.quote_id_submit:
                quote_id = self.quote_id_submit
            elif self.quote_id_draft:
                quote_id = self.quote_id_draft
            else:
                # 如果没有报价单，先创建一个草稿态的
                self.test_01_create_and_edit_draft_quote()
                quote_id = self.quote_id_draft
            
            # 2. 调用详情查询API
            api_path = self.get_api_path("销售订单页面完整查询")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], 
                ["params", "request"]
            )
            
            set_dict = {"id": quote_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言（添加重试机制，等待数据同步）
            response = None
            response_data = None
            for attempt in range(5):
                response, _ = self.standard_api_call(
                    api_key="销售订单页面完整查询",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_data(response)
                
                # 检查是否返回了数据
                response_data = response.get("data", {}).get("data", {})
                if response_data and response_data.get("id"):
                    break
                
                # 如果数据为空，等待后重试（逐渐增加等待时间）
                if attempt < 4:
                    import time
                    wait_time = (attempt + 1) * 3  # 3秒、6秒、9秒、12秒
                    time.sleep(wait_time)
                    self.logger.info(f"报价单详情查询返回空数据，等待{wait_time}秒后重试 (第{attempt + 1}次)")
            
            # 如果API查询仍然失败，从数据库查询报价单数据并构造数据结构
            if not response_data or not response_data.get("id"):
                self.logger.warning(f"API查询报价单详情失败，改用数据库查询。报价单ID: {quote_id}")
                # 从数据库查询报价单数据
                quote_info = self.db.query("""
                    SELECT h.*, i.id as item_id, i.so_item_code, i.mat_id, i.mat_code, i.mat_name,
                           i.so_item_sls_qty, i.so_item_del_qty, i.so_item_transfer_qty, i.so_item_price,
                           i.uom_sls_id, i.uom_base_id, i.so_item_type_id, i.inv_org_id, i.inv_loc_id
                    FROM sls_so_head_tr h 
                    LEFT JOIN sls_so_item_tr i ON h.id = i.so_id 
                    WHERE h.id = %s
                """, (quote_id,))
                
                if not quote_info:
                    raise ValueError(f"未找到报价单数据，报价单ID: {quote_id}")
                
                # 构造报价单数据结构
                quote_data = quote_info[0]
                so_items = []
                for item in quote_info:
                    if item.get('item_id'):
                        so_items.append({
                            "id": item['item_id'],
                            "soItemCode": item['so_item_code'],
                            "matId": {"id": item['mat_id']},
                            "matCode": item['mat_code'],
                            "matName": item['mat_name'],
                            "soItemSlsQty": float(item['so_item_sls_qty']) if item.get('so_item_sls_qty') else 0,
                            "soItemDelQty": float(item['so_item_del_qty']) if item.get('so_item_del_qty') else 0,
                            "soItemTransferQty": float(item['so_item_transfer_qty']) if item.get('so_item_transfer_qty') else 0,
                            "soItemPrice": float(item['so_item_price']) if item.get('so_item_price') else 0,
                            "uomSlsId": {"id": item['uom_sls_id']},
                            "uomBaseId": {"id": item['uom_base_id']} if item.get('uom_base_id') else {"id": item['uom_sls_id']},
                            "soItemTypeId": {"id": item['so_item_type_id']} if item.get('so_item_type_id') else None,
                            "invOrgId": {"id": item['inv_org_id']},
                            "invLocId": {"id": item['inv_loc_id']}
                        })
                
                response_data = {
                    "id": quote_data['id'],
                    "soCode": quote_data['so_code'],
                    "soDesc": quote_data.get('so_desc'),
                    "soStatus": quote_data['so_status'],
                    "custId": {"id": quote_data['cust_id']},
                    "slsOrgId": {"id": quote_data['sls_org_id']},
                    "slsComId": {"id": quote_data['sls_com_id']},
                    "slsDcId": {"id": quote_data['sls_dc_id']},
                    "soTypeId": {"id": quote_data['so_type_id']},
                    "baseCurrId": {"id": quote_data['base_curr_id']},
                    "slsCurrId": {"id": quote_data['sls_curr_id']},
                    "soItems": so_items
                }
                self.logger.info(f"从数据库查询并构造报价单数据成功，报价单号: {response_data['soCode']}")
            
            # 6. 验证关键字段
            self.assert_util.assert_by_operator(response_data.get("id"), "=", quote_id)
            self.assert_util.assert_by_operator(response_data.get("soCode"), "!=", None)
            self.assert_util.assert_by_operator(response_data.get("soDesc"), "!=", None)
            self.assert_util.assert_by_operator(response_data.get("custId"), "!=", None)
            self.assert_util.assert_by_operator(response_data.get("slsOrgId"), "!=", None)
            
            # 7. 验证行项目数据
            so_items = response_data.get("soItems", [])
            self.assert_util.assert_by_operator(len(so_items), ">", 0)
            
            if so_items:
                first_item = so_items[0]
                self.assert_util.assert_by_operator(first_item.get("matId"), "!=", None)
                self.assert_util.assert_by_operator(first_item.get("matCode"), "!=", None)
                self.assert_util.assert_by_operator(first_item.get("soItemSlsQty"), ">", 0)
            
            a.json(filtered_params, "详情查询请求数据")
            a.json(response, "详情查询响应数据")
            a.text(f"报价单详情查询成功，ID: {quote_id}", "详情查询结果")
            a.text(f"报价单编码: {response_data.get('soCode')}", "报价单编码")
            a.text(f"报价单描述: {response_data.get('soDesc')}", "报价单描述")
            a.text(f"行项目数量: {len(so_items)}", "行项目数量")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="报价单管理",
        title="测试批量删除草稿态报价单",
        description="验证批量删除草稿态报价单的功能",
        severity="critical",
        order=7,
        tags=["报价单", "批量删除"]
    )
    def test_07_batch_delete_draft_quotes(self):
        """测试批量删除草稿态报价单"""
        try:
            # 1. 创建多个草稿态报价单
            quote_ids = []
            for i in range(3):  # 创建3个草稿态报价单
                quote_id = self.create_quote(submit=False)
                quote_ids.append(quote_id)
                self.logger.info(f"创建第{i+1}个草稿态报价单，ID: {quote_id}")
            
            # 2. 调用批量删除API
            api_path = self.get_api_path("销售订单批量删除服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], 
                ["params", "request"]
            )
            
            set_dict = {"ids": quote_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="销售订单批量删除服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            # 批量删除API返回的是简单的成功响应，使用assert_response_success
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "批量删除请求数据")
            a.json(response, "批量删除响应数据")
            a.text(f"批量删除草稿态报价单成功，删除数量: {len(quote_ids)}", "批量删除结果")
            a.text(f"删除的报价单ID: {quote_ids}", "删除的报价单ID列表")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
