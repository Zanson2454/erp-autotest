# """
# 标准采购交货单测试
# 演示两种场景：
# - 使用现有的可用采购订单创建交货单
# - 无可用数据时，fixture 自动创建，再继续测试
# """
# from api.delivery_api import DeliveryAPI  # 假设你已封装了交货单 API
# import pytest

# class TestStdPurDeliveryCreate:
    
#     def test_create_delivery_with_available_order(self, available_std_pur_order):
#         order_no = available_std_pur_order['order_no']
#         payload = {
#             'pur_order_no': order_no,
#             'delivery_qty': 100,
#             'delivery_date': '2025-01-20'
#         }
#         resp = DeliveryAPI.create_delivery(payload)
#         assert resp['code'] == 200
#         assert resp['data'].get('delivery_no')

#     def test_create_delivery_with_fresh_order(self, fresh_std_pur_order):
#         order_no = fresh_std_pur_order['order_no']
#         payload = {
#             'pur_order_no': order_no,
#             'delivery_qty': 60,
#             'delivery_date': '2025-01-25'
#         }
#         resp = DeliveryAPI.create_delivery(payload)
#         assert resp['code'] == 200
#         assert resp['data'].get('delivery_no')