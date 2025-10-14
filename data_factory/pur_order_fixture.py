# """
# 采购订单数据工厂（数据准备层）

# 作用：直接向数据库插入采购订单（头表 + 明细表），以及在需要时获取/创建“可用”的订单数据。
# 注意：查询逻辑和插入逻辑都通过这个模块暴露给外部使用，以实现数据准备的统一入口。
# """

# from datetime import datetime
# import random
# from typing import Dict, Optional
# from common.db_helper import DBHelper


# class PurOrderFixture:
#     @staticmethod
#     def _gen_order_no(prefix: str = 'PO', length: int = 20) -> str:
#         timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#         suffix_len = max(0, length - len(prefix) - len(timestamp))
#         suffix = ''.join(random.choices('0123456789', k=suffix_len))
#         return f"{prefix}{timestamp}{suffix}"

#     @classmethod
#     def create_std_order(
#         cls,
#         supplier_id: str = 'SUP001',
#         total_qty: int = 1000,
#         unit_price: float = 10.50,
#         status: str = 'approved'
#     ) -> Dict:
#         """直接插入标准采购订单（头表 + 明细表）"""
#         order_no = cls._gen_order_no('PO', 20)
#         total_amount = total_qty * unit_price

#         order_data = {
#             'order_no': order_no,
#             'order_type': 'standard',
#             'status': status,
#             'supplier_id': supplier_id,
#             'total_qty': total_qty,
#             'remaining_qty': total_qty,
#             'total_amount': round(total_amount, 2),
#             'currency': 'CNY',
#             'order_date': datetime.now().strftime('%Y-%m-%d'),
#             'created_by': 'test_auto',
#             'created_time': datetime.now(),
#             'updated_time': datetime.now()
#         }
#         order_id = DBHelper.insert('pur_order', order_data)

#         item_data = {
#             'order_id': order_id,
#             'order_no': order_no,
#             'line_no': 1,
#             'material_code': 'MAT001',
#             'material_name': '测试物料',
#             'qty': total_qty,
#             'remaining_qty': total_qty,
#             'unit_price': unit_price,
#             'amount': round(total_amount, 2),
#             'warehouse_code': 'WH01',
#             'created_time': datetime.now()
#         }
#         DBHelper.insert('pur_order_item', item_data)

#         return {
#             'order_id': order_id,
#             'order_no': order_no,
#             'order_type': 'standard',
#             'supplier_id': supplier_id,
#             'total_qty': total_qty,
#             'remaining_qty': total_qty,
#             'total_amount': round(total_amount, 2),
#             'status': status
#         }

#     @classmethod
#     def create_csm_order(
#         cls,
#         supplier_id: str = 'SUP002',
#         total_qty: int = 500,
#         unit_price: float = 8.80,
#         status: str = 'approved'
#     ) -> Dict:
#         """直接插入寄售采购订单（头表 + 明细表）"""
#         order_no = cls._gen_order_no('CSPO', 22)
#         total_amount = total_qty * unit_price

#         order_data = {
#             'order_no': order_no,
#             'order_type': 'consignment',
#             'status': status,
#             'supplier_id': supplier_id,
#             'total_qty': total_qty,
#             'remaining_qty': total_qty,
#             'total_amount': round(total_amount, 2),
#             'currency': 'CNY',
#             'settlement_type': 'consignment',
#             'order_date': datetime.now().strftime('%Y-%m-%d'),
#             'created_by': 'test_auto',
#             'created_time': datetime.now(),
#             'updated_time': datetime.now()
#         }
#         order_id = DBHelper.insert('pur_order', order_data)

#         item_data = {
#             'order_id': order_id,
#             'order_no': order_no,
#             'line_no': 1,
#             'material_code': 'MAT_CSM001',
#             'material_name': '寄售物料',
#             'qty': total_qty,
#             'remaining_qty': total_qty,
#             'unit_price': unit_price,
#             'amount': round(total_amount, 2),
#             'warehouse_code': 'CSM_WH01',
#             'is_consignment': 1,
#             'created_time': datetime.now()
#         }
#         DBHelper.insert('pur_order_item', item_data)

#         return {
#             'order_id': order_id,
#             'order_no': order_no,
#             'order_type': 'consignment',
#             'supplier_id': supplier_id,
#             'total_qty': total_qty,
#             'remaining_qty': total_qty,
#             'total_amount': round(total_amount, 2),
#             'status': status
#         }

#     @classmethod
#     def query_available_std_order(cls) -> Optional[Dict]:
#         sql = """
#         SELECT order_id, order_no, supplier_id, total_qty, remaining_qty, total_amount, status
#         FROM pur_order
#         WHERE status = 'approved'
#           AND order_type = 'standard'
#           AND remaining_qty > 0
#         ORDER BY created_time DESC
#         LIMIT 1
#         """
#         return DBHelper.query_one(sql)

#     @classmethod
#     def query_available_csm_order(cls) -> Optional[Dict]:
#         sql = """
#         SELECT order_id, order_no, supplier_id, total_qty, remaining_qty, total_amount, status
#         FROM pur_order
#         WHERE status = 'approved'
#           AND order_type = 'consignment'
#           AND remaining_qty > 0
#         ORDER BY created_time DESC
#         LIMIT 1
#         """
#         return DBHelper.query_one(sql)

#     @classmethod
#     def get_or_create_std_order(cls, **kwargs) -> Dict:
#         """先查库存再创建：获取可用标准订单，若无则创建一个"""
#         order = cls.query_available_std_order()
#         if order:
#             return order
#         return cls.create_std_order(**kwargs)

#     @classmethod
#     def get_or_create_csm_order(cls, **kwargs) -> Dict:
#         """获取可用寄售订单，若无则创建"""
#         order = cls.query_available_csm_order()
#         if order:
#             return order
#         return cls.create_csm_order(**kwargs)