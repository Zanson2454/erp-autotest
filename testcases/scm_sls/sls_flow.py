"""销售域 Flow DSL（试点）。"""

from testcases.comm.base_flow import BaseFlow


class SlsFlow(BaseFlow):
    """销售订单业务动作封装。"""

    def create_order(self, order_type: str = "STND", submit: bool = False, rebate_amount=None):
        """创建销售订单并自动注册清理动作。"""
        so_head_id = self.test.create_sales_order(order_type=order_type, submit=submit, rebate_amount=rebate_amount)
        if not so_head_id:
            return so_head_id

        self.register_db_cleanup(
            name=f"sls_so_item_cleanup_{so_head_id}",
            table="sls_so_item_tr",
            where="so_head_id = %s",
            params=[so_head_id],
            order=620,
        )
        self.register_db_cleanup(
            name=f"sls_so_head_cleanup_{so_head_id}",
            table="sls_so_head_tr",
            where="id = %s",
            params=[so_head_id],
            order=610,
        )
        return so_head_id
