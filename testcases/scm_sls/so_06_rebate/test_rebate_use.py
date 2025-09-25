# -*- coding: utf-8 -*-
"""
返利政策使用流程测试用例
测试返利政策在销售订单中的实际使用效果
"""

import time
import allure
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import case_decorator


@allure.epic("销售管理")
@allure.feature("返利政策使用流程")
class TestRebateUse(SlsBase):
    """返利政策使用流程测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("返利政策使用流程测试类初始化完成")
    
    @case_decorator(
        story="返利政策使用",
        title="测试返利政策在销售订单中的使用",
        description="验证返利政策在销售订单中的实际使用效果，包括返利金额扣减",
        severity="critical",
        order=1,
        tags=["返利政策", "销售订单", "返利使用"]
    )
    def test_01_rebate_policy_use_in_sales_order(self):
        """测试返利政策在销售订单中的使用"""
        try:
            # 1. 创建填写了返利金额的销售单并保存
            self.logger.info("开始创建填写返利金额的销售单")
            
            # 设置返利金额
            rebate_amount = 0.01  # 使用curl中的返利金额
            
            # 使用公共方法创建带返利金额的销售订单
            so_id = self.create_sales_order(order_type="STND", submit=False, rebate_amount=rebate_amount)
            
            # 获取销售订单信息
            so_info = self.db.query(f"SELECT id, so_code FROM sls_so_head_tr WHERE id={so_id}")
            so_code = so_info[0]['so_code'] if so_info else f"AT_SO_REBATE_{int(time.time() * 1000)}"
            
            self.logger.info(f"创建销售订单成功，ID: {so_id}, 订单号: {so_code}")
            
            # 2. 提交销售单
            self.logger.info("开始提交销售单")
            
            # 获取销售订单提交API
            submit_api_path = self.get_api_path("SLS-销售订单-提交服务")
            submit_params, submit_url = self.get_api_params(submit_api_path)
            
            # 设置提交参数
            filtered_submit_params = ParamUtil.filter_post_body_fields(
                submit_params, ["sceneKey", "viewKey", "viewTitle", "buttonKey", "buttonName", "appId", "teamId", "serviceKey", "params"], 
                []
            )
            
            submit_set_dict = {
                "id": so_id
            }
            ParamUtil.set_request_params(filtered_submit_params, submit_set_dict)
            
            # 发送提交请求
            submit_response = self.http.post(submit_url, json=filtered_submit_params)
            self.assert_util.assert_response_success(submit_response)
            
            self.logger.info(f"销售订单提交成功，ID: {so_id}")
            
            # 3. 查询返利账户流水记录
            self.logger.info("开始查询返利账户流水记录")
            
            # 获取返利账户流水查询API
            query_api_path = self.get_api_path("SLS-返利账户流水-查询服务")
            query_params, query_url = self.get_api_params(query_api_path)
            
            # 设置查询参数
            filtered_query_params = ParamUtil.filter_post_body_fields(
                query_params, ["sceneKey", "viewKey", "appId", "teamId", "serviceKey", "params"], 
                []
            )
            
            query_set_dict = {
                "params": {
                    "accId": 14072001,  # 返利账户ID
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None
                    }
                }
            }
            ParamUtil.set_request_params(filtered_query_params, query_set_dict)
            
            # 发送查询请求
            query_response = self.http.post(query_url, json=filtered_query_params)
            self.assert_util.assert_response_success(query_response)
            
            # 验证返利账户流水记录
            flow_data = query_response["data"]["data"]
            records = flow_data.get("data", [])
            self.logger.info(f"查询到返利账户流水记录: {len(records)} 条")
            
            # 验证第一条流水的金额是否与订单使用的返利金额一致
            if records:
                first_record = records[0]
                flow_amount = first_record.get("amount", 0)
                self.logger.info(f"第一条流水记录金额: {flow_amount}")
                self.logger.info(f"订单使用的返利金额: {rebate_amount}")
                
                # 断言验证流水金额与返利金额一致
                assert abs(float(flow_amount) - float(rebate_amount)) < 0.01, f"返利账户流水金额 {flow_amount} 与订单返利金额 {rebate_amount} 不一致"
                
                self.logger.info(f"返利账户流水金额验证通过: {flow_amount}")
            else:
                raise AssertionError("未找到返利账户流水记录")
            
            # 记录测试结果
            self.logger.info(f"返利政策使用测试完成:")
            self.logger.info(f"- 销售订单号: {so_code}")
            self.logger.info(f"- 销售订单ID: {so_id}")
            self.logger.info(f"- 返利金额: {rebate_amount}")
            self.logger.info(f"- 返利账户流水金额: {flow_amount}")
            self.logger.info(f"- 金额验证: 通过")
            
        except Exception as e:
            self.logger.error(f"返利政策使用测试失败: {str(e)}")
            raise
