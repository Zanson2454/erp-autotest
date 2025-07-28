  # @case_decorator(
    #     story="销售订单",
    #     title="删除单个订单",
    #     description="验证单个订单删除接口",
    #     severity="critical",
    #     order=170,
    #     tags=["销售订单", "删除", "单个删除"]
    # )
    # def test_delete_single_order(self):
    #     """删除单个销售订单"""
    #     try:
    #         # 确保有可删除的订单
    #         if not hasattr(self, 'order_id') or not self.order_id:
    #             self.test_submit_multiple_order_types()

    #         url = self.sls_api_paths["订单管理"]["删除订单"]
    #         data = self.sls_api_params.get(url, {})
    #         data['params']['request']['orderId'] = self.order_id

    #         result = self.http.post(url, json=data, description="删除单个订单")
    #         a.json(data, "删除请求参数")
    #         a.json(result, "删除响应数据")

    #         self.assert_util.assert_response_success(result)

    #         # 验证订单已被删除
    #         query_url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         query_data = self.sls_api_params.get(query_url, {})
    #         query_data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "id",
    #                     "operator": "EQ",
    #                     "rightValue": {
    #                         "constValue": self.order_id
    #                     }
    #                 }]
    #             }]
    #         }

    #         query_result = self.http.post(query_url, json=query_data, description="验证订单是否已删除")
    #         query_response_data = query_result.get("data", {}).get("data", {}).get("data", [])
    #         self.assert_util.assert_eq(len(query_response_data), 0, f"订单删除失败，仍能查询到订单ID: {self.order_id}")
    #     except Exception as e:
    #         a.text(str(e), "删除失败原因")
    #         raise

    # @case_decorator(
    #     story="销售订单",
    #     title="批量删除订单",
    #     description="验证批量订单删除接口",
    #     severity="critical",
    #     order=180,
    #     tags=["销售订单", "删除", "批量删除"]
    # )
    # def test_batch_delete_orders(self):
    #     """批量删除销售订单"""
    #     try:
    #         # 创建多个订单用于批量删除测试
    #         order_ids = []
    #         for _ in range(3):
    #             self.order_id = None
    #             self.so_items = None
    #             self.so_price_data = None
    #             self.test_01_init_sales_order()
    #             self.test_07_render_order_line()
    #             self.test_08_calculate_pricing()
    #             order_id = self._save_or_submit_order(submit=True)
    #             order_ids.append(order_id)

    #         url = self.sls_api_paths["订单管理"]["批量删除订单"]
    #         data = self.sls_api_params.get(url, {})
    #         data['params']['request']['orderIds'] = order_ids

    #         result = self.http.post(url, json=data, description="批量删除订单")
    #         a.json(data, "批量删除请求参数")
    #         a.json(result, "批量删除响应数据")

    #         self.assert_util.assert_response_success(result)

    #         # 验证所有订单已被删除
    #         query_url = self.sls_api_paths["订单管理"]["查询订单列表"]
    #         query_data = self.sls_api_params.get(query_url, {})
    #         query_data['params']['request']['pageable']['conditionGroup'] = {
    #             "logic": "AND",
    #             "conditions": [{
    #                 "logic": "AND",
    #                 "conditions": [{
    #                     "field": "id",
    #                     "operator": "IN",
    #                     "rightValue": {
    #                         "constValue": order_ids
    #                     }
    #                 }]
    #             }]
    #         }

    #         query_result = self.http.post(query_url, json=query_data, description="验证订单是否已删除")
    #         query_response_data = query_result.get("data", {}).get("data", {}).get("data", [])
    #         self.assert_util.assert_eq(len(query_response_data), 0, f"批量删除失败，仍能查询到{len(query_response_data)}个订单")
    #     except Exception as e:
    #         a.text(str(e), "批量删除失败原因")
    #         raise