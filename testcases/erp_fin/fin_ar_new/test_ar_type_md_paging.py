# -*- coding: utf-8 -*-
"""
应收单类型配置表分页查询测试用例
"""
import allure
from testcases.erp_fin import FinBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("应收单类型配置")
class TestArTypeMdPaging(FinBaseTest):
    """应收单类型配置表分页查询测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("应收单类型配置表分页查询测试类初始化完成")

    @case_decorator(
        story="应收单类型配置",
        title="测试应收单类型配置表分页查询",
        description="验证应收单类型配置表分页查询功能，包括分页参数和响应数据验证",
        severity="normal",
        file_level_order=1,
        tags=["ar", "ar_type", "paging", "query"]
    )
    def test_paging_ar_type_md(self):
        """测试应收单类型配置表分页查询"""
        try:
            # 1. 准备分页查询参数
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "modelKey": "ERP_FIN$fin_arm_ar_type_md"
            }
            # fields_to_filter 可选：不传时自动从 set_dict.keys() 获取
            fields_to_filter = ["pageable", "modelKey"]

            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="应收单类型配置表-分页数据服务_PmHKWs1",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )

            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)

            # 4. 验证分页响应数据
            data = response.get("data", {}).get("data", {})
            total = data.get("total")
            data_list = data.get("data", [])

            # 验证总记录数存在
            self.assert_util.assert_by_operator(
                total, ">=", 0,
                "总记录数应大于等于0"
            )

            # 验证返回的数据列表
            if total > 0:
                self.assert_util.assert_by_operator(
                    data_list, "not_empty",
                    "当总记录数大于0时，数据列表不应为空"
                )

            # 记录关键信息
            a.text(f"总记录数: {total}", "分页查询结果")
            a.text(f"当前页数据条数: {len(data_list)}", "分页查询结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

