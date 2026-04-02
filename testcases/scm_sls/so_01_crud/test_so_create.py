import pytest
import json
from datetime import datetime
from pathlib import Path
import allure
import sys


# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.report_util import a, case_decorator
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil


@allure.epic("销售管理")
@allure.feature("销售订单主表管理")
class TestSoHeadManagement(SlsBase):
    """销售订单主表（so_head）增删改查及接口专项测试类"""

    # 定义要测试的订单类型
    TEST_ORDER_TYPES = ["STND", "THRD", "CENT"]

    @classmethod
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
    
        # 初始化销售配置数据
        # cls.so_type_id = cls.ids.get("so_type_id")
        cls.so_head_id_save = None
        cls.so_head_id_submit = None
  

        a.text(f"初始化渲染数量: {cls.render_qty}", "初始化信息")
        a.text("测试类初始化完成", "初始化信息")

    

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-保存服务",
        description="验证SLS_SO_SAVE_ACTION_SERVICE接口",
        severity="critical",
        order=90,
        tags=["销售订单", "保存", "SLS_SO_SAVE_ACTION_SERVICE"]
    )
    def test_so_save(self):
        """SLS-销售订单-保存服务"""
        try:
            # 保存订单并赋值ID
            self.so_head_id_save = self.create_sales_order(submit=False)
            assert self.so_head_id_save is not None, "保存订单失败，未返回订单ID"
            a.text(f"销售订单保存成功，订单ID: {self.so_head_id_save}", "保存结果")
        except Exception as e:
            a.text(str(e), "保存失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-提交服务",
        description="验证SLS_SO_SUBMIT_ACTION_SERVICE接口",
        severity="critical",
        order=110,
        tags=["销售订单", "提交", "SLS_SO_SUBMIT_ACTION_SERVICE"]
    )
    def test_so_submit(self):
        """SLS-销售订单-提交服务"""
        try:
             # 提交订单并赋值ID
            self.so_head_id_submit = self.create_sales_order(submit=True)
            assert self.so_head_id_submit is not None, "提交订单失败，未返回订单ID"
            a.text(f"销售订单提交成功，订单ID: {self.so_head_id_submit}", "提交结果")
        except Exception as e:
            a.text(str(e), "提交失败原因")
            raise


    @case_decorator(
        story="销售订单",
        title="销售订单页面完整查询",
        description="验证SLS_SO_QUERY_DETAIL_EVENT_SERVICE接口",
        severity="critical",
        order=120,
        tags=["销售订单", "查询", "SLS_SO_QUERY_DETAIL_EVENT_SERVICE"]
    )
    def test_so_query_detail_event_service(self):
        """销售订单页面完整查询"""
        try:
            # 确保有可查询的订单ID
            if not self.so_head_id_save:
                self._ensure_so_save()

            api_path = self.get_api_path("销售订单页面完整查询")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {
                "id": self.so_head_id_save
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="销售订单页面完整查询",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "查询失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SO-查看定价记录服务",
        description="验证SO_QUERY_PRICE_RECORDS_EVENT_SERVICE接口",
        severity="critical",
        order=130,
        tags=["销售订单", "定价记录", "SO_QUERY_PRICE_RECORDS_EVENT_SERVICE"]
    )
    def test_so_query_price_records_event_service(self):
        """SO-查看定价记录服务"""
        try:
            # 确保有可查询定价记录的订单ID和幂等码
            if not self.so_head_id_save or not self.priceIdempotent:
                self._ensure_so_save()

            api_path = self.get_api_path("SO-查看定价记录服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["soId", "priceIdempotent"], ["params", "request"]
            )
            set_dict = {
                "soItem": self.so_item_data[0],
                "soPartnerLinks": self.sls_partner_links,
                "priceIdempotent": self.priceIdempotent
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="SO-查看定价记录服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            so_priceItem_records = response.get("data", {}).get("data", {}).get("soPriceItemRecords", [])
            self.assert_util.assert_by_operator(so_priceItem_records, "not_empty",message="定价记录ID不能为空")
         
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            # 验证返回的定价记录数据
        

        except Exception as e:
            a.text(str(e), "查询定价记录失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SO-维护发货计划行服务",
        description="验证SO_INIT_SCHEDULE_LINE_EVENT_SERVICE接口",
        severity="critical",
        order=140,
        tags=["销售订单", "发货计划", "SO_INIT_SCHEDULE_LINE_EVENT_SERVICE"]
    )
    def test_so_init_schedule_line_event_service(self):
        """SO-维护发货计划行服务"""
        try:
            # 确保有可维护发货计划的订单行ID
            if not self.so_item_id:
                self._ensure_so_save()

            api_path = self.get_api_path("SO-维护发货计划行服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["currentItem", "soHeader", "soItems"], ["params", "request"]
            )
            
            # 设置发货计划参数
            schedule_date = self.mock_util.get_timestamp(timestamp=True, day_offset=7)  # 7天后发货
            set_dict = {
                "currentItem": self.so_item_data[0],
                "soHeader": self.so_head_data,  # 使用渲染时的数量
                "soItems": self.so_item_data
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="SO-维护发货计划行服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
        
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"发货计划行维护完成，计划发货日期: {schedule_date}", "维护结果")
            
        except Exception as e:
            a.text(str(e), "维护发货计划行失败原因")
            raise
