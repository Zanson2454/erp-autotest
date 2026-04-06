# -*- coding: utf-8 -*-
"""ERP 财务模块的测试初始化 — 声明式配置 + 自定义 context_builder。"""

import random
import time

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import AsyncWaitMixin, MockUtilMixin
from testcases.erp_fin.context_builder import build_fin_context
from utils.param_util import ParamUtil


class FinBaseTest(AsyncWaitMixin, MockUtilMixin, BaseTest):
    """ERP 财务模块基础测试类 — 声明式注册。"""

    MODULE_NAME = "FIN"
    LOGIN_STRATEGY = "single"
    API_PATH_FILE = "config/api/erp_fin/fin_api_path.yaml"
    API_PARAMS_FILE = "config/api/erp_fin/fin_api_params.yaml"
    SQL_CACHES = [
        {"path": "config/erp/md_init_sql.yaml", "key": "md_init_cache", "attr": "md_cache_data"},
        {"path": "config/erp/fin_init_sql.yaml", "key": "fin_init_cache", "attr": "fin_cache_data"},
    ]
    REQUIRED_CACHE_KEYS = ("curr_id", "cust_id")

    @classmethod
    def _bind_module_context(cls) -> None:
        """在标准声明式绑定后补充财务域上下文字段。"""
        super()._bind_module_context()
        context_data = build_fin_context(
            init_data=getattr(cls, "init_data", None),
            md_cache_data=getattr(cls, "md_cache_data", None),
            fin_cache_data=getattr(cls, "fin_cache_data", None),
        )
        for key, value in context_data.items():
            setattr(cls, key, value)

        cls.logger.info(f"获取到 sett_item_type_info，可用code列表: {list(cls.sett_item_type_info.keys())}")
        cls.logger.info(f"获取到 ar_type_md_info，可用code列表: {list(cls.ar_type_md_info.keys())}")
        cls.logger.info(f"获取到 sb_type_info，可用code列表: {list(cls.sb_type_info.keys())}")
        if cls.sett_doc_type_info is not None:
            cls.logger.info(f"获取到 sett_doc_type_info: {cls.sett_doc_type_info}")
        else:
            cls.logger.warning("sett_doc_type_info 为空，无法获取 sett_doc_type_info")
        if cls.calendar_head_id is not None:
            cls.logger.info(f"获取到 calendar_head_id: {cls.calendar_head_id}")
        else:
            cls.logger.warning("calender_head_info 为空，无法获取 calendar_head_id")
        if cls.calendar_item_id is not None:
            cls.logger.info(f"获取到 calendar_item_id: {cls.calendar_item_id}")
        else:
            cls.logger.warning("calender_item_info 中没有 period_type='MONTH' 的项，无法获取 calendar_item_id")

    @classmethod
    def load_api_configs(cls):
        """向后兼容：旧测试类可继续手动调用。"""
        cls._load_module_apis()

    @classmethod
    def load_cache_data(cls):
        """向后兼容：旧测试类可继续手动调用。"""
        cls._load_module_caches()
        cls.logger.info(f"md_cache_data: {getattr(cls, 'md_cache_data', None) is not None}")

    @classmethod
    def bind_context(cls):
        """向后兼容：旧测试类可继续手动调用。"""
        cls._bind_module_context()

    def create_settlement_item(self, sett_item_type_code="E_SLS_GOODS", org=1):
        """
        创建结算项公共方法，通过结算行项目类型编码创建不同结算项
        """
        if org == 1:
            com_org_id = self.com_org_id
            inv_org_id = self.inv_org_id
            sls_org_id = self.sls_org_id
            pur_org_id = self.pur_org_id
        elif org == 2:
            com_org_id = self.com_org_id_2
            inv_org_id = self.inv_org_id_2
            sls_org_id = self.sls_org_id_2
            pur_org_id = self.pur_org_id_2
        else:
            raise ValueError("org 参数错误，请输入 1 或 2")
        # 获取对应key的sett_item_type_info的值
        if not self.sett_item_type_info:
            raise ValueError("sett_item_type_info 未初始化，请检查 setup_class 是否正确执行")
        sett_item_type_info = self.sett_item_type_info.get(sett_item_type_code)
        if not sett_item_type_info:
            available_codes = list(self.sett_item_type_info.keys())
            raise ValueError(
                f"未找到对应key的sett_item_type_info: {sett_item_type_code}\n"
                f"可用的sett_item_type_code列表: {available_codes}"
            )
        sett_item_type_name = sett_item_type_info.get("sett_item_type_name")
        api_path = self.get_api_path("SETT-ITEM-手动创建服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            [
                "settItemCode",
                "settItemStatus",
                "settItemTypeId",
                "settDate",
                "partnerType",
                "ptHeadId",
                "remark",
                "comOrgId",
                "purSlsOrgType",
                "invOrgId",
                "matId",
                "taxRate",
                "basicUnitId",
                "genMatTypeCfId",
                "settQty",
                "settDocPrice",
                "settDocAmt",
                "netDocAmt",
                "taxAmt",
                "docCurrId",
                "baseCurrId",
                "exchRate",
                "grossBaseAmt",
                "netBaseAmt",
                "settDocTypeId",
                "settDocId",
                "dnCode",
                "dnItemCode",
                "poSoCode",
                "poSoItemCode",
                "asyncExecutionStatus",
                "partnerId",
                "taxCodeId",
                "purSlsOrgId",
            ],
            ["params", "request"],
        )
        set_dict = {
            "settItemCode": "AUTOTEST-SETTI" + str(self.mock_util.get_timestamp(timestamp=True)),
            "settItemStatus": "CREATED",
            "settItemTypeId": {"id": sett_item_type_info.get("id")},
            "settDate": self.mock_util.get_timestamp(timestamp=True),
            "partnerType": "CUSTOMER" if sett_item_type_info.get("bt_class") == "SALES" else "SUPPLIER",
            "ptHeadId": None,
            "remark": f"自动化测试创建结算项-{sett_item_type_name}",
            "comOrgId": {"id": com_org_id},
            "purSlsOrgType": "SLS" if sett_item_type_info.get("bt_class") == "SALES" else "PUR",
            "invOrgId": {"id": inv_org_id},
            "matId": {"id": self.mat_id},
            "taxRate": self.tax_rate,
            "basicUnitId": {"id": self.basic_unit_id},
            "genMatTypeCfId": {"id": self.mat_type_cf},
            "settQty": 10 if sett_item_type_info.get("is_count_qty") else None,
            "settDocPrice": 30 if sett_item_type_info.get("is_count_qty") else None,
            "settDocAmt": 300,
            "netDocAmt": 265.486726,
            "taxAmt": 34.513274,
            "docCurrId": {"id": self.curr_id},
            "baseCurrId": {"id": self.curr_id},
            "exchRate": 1.00,
            "grossBaseAmt": 300,
            "netBaseAmt": 265.486726,
            "settDocTypeId": {"id": sett_item_type_info.get("sett_doc_type_code")},
            "settDocId": None,
            "dnCode": None,
            "dnItemCode": None,
            "poSoCode": None,
            "poSoItemCode": None,
            "asyncExecutionStatus": "CREATED",
            "partnerId": {"id": self.cust_id if sett_item_type_info.get("bt_class") == "SALES" else self.vend_id},
            "taxCodeId": {"id": self.tax_code_id},
            "purSlsOrgId": {"id": sls_org_id if sett_item_type_info.get("bt_class") == "SALES" else pur_org_id},
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        result, _ = self.standard_api_call(
            api_key="SETT-ITEM-手动创建服务",
            set_dict=filtered_params.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)
        # 响应数据是列表格式，取第一个元素的id
        data_list = result.get("data", {}).get("data", [])
        if not data_list or len(data_list) == 0:
            raise ValueError("创建结算项失败：响应数据为空")
        return data_list[0].get("id")

    def create_settlement_doc(self, sett_item_type_code="E_SLS_GOODS", org=1):
        """
        创建结算单公共方法,通过结算项类型编码创建不同结算单
        """
        sett_item_id = self.create_settlement_item(sett_item_type_code, org)
        api_path = self.get_api_path("SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
        params, url = self.get_api_params(api_path)
        data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
        data = ParamUtil.convert_param_type(data, ["params", "request"], "array")
        data["params"]["request"][0]["id"] = sett_item_id
        result, _ = self.standard_api_call(
            api_key="SETT-ITEM-结算项确认及汇单-关联操作-异步服务",
            set_dict=data.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)

        def query_sett_item_status():
            row = self.query_service.get_sett_item_status_row(sett_item_id)
            if not row:
                raise ValueError(f"结算项对账确认失败: 未找到结算项ID {sett_item_id}")
            return row

        result = self.async_wait_util.wait_for_async_status(
            query_func=query_sett_item_status,
            status_field="async_execution_status",
            success_status="SUCCEEDED",
            failed_status="FAILED",
            max_wait=10,
            interval=0.5,
        )
        if result.status == self.wait_status.SUCCESS:
            sett_doc_id = result.last_data.get("sett_doc_id")
            if sett_doc_id is None:
                raise ValueError(f"结算项对账确认失败: 结算项ID {sett_item_id} 未生成结算单")
            return sett_doc_id
        else:
            raise ValueError(f"结算项对账确认失败: {result.error_message}")

    def create_confirmed_settlement_doc(self, sett_item_type_code="E_SLS_GOODS", org=1):
        """
        创建已确认结算单公共方法,返回结算单id
        """
        api_path = self.get_api_path("SETT-DOC-运营端结算单确认下推应收应付-异步服务")
        params, url = self.get_api_params(api_path)
        data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
        data = ParamUtil.convert_param_type(data, ["params", "request", "id"], "array")
        data["params"]["request"]["id"][0] = self.create_settlement_doc(sett_item_type_code, org)
        result, _ = self.standard_api_call(
            api_key="SETT-DOC-运营端结算单确认下推应收应付-异步服务",
            set_dict=data.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)
        # 等待异步任务执行完成，当状态为PROCESSING时一直等待，最长超时10秒
        sett_doc_id = data["params"]["request"]["id"][0]
        if sett_doc_id is None:
            raise ValueError("结算单确认失败: 结算单ID不能为None")

        start_time = time.time()
        timeout = 10
        while True:
            row = self.query_service.get_sett_doc_status_row(sett_doc_id)
            if not row:
                raise ValueError(f"结算单确认失败: 未找到结算单ID {sett_doc_id}")
            if row.get("trading_doc_id") is not None:
                break
            if time.time() - start_time >= timeout:
                raise TimeoutError(f"等待异步任务执行超时（{timeout}秒）")
            self._async_delay(0.5, reason="等待结算单确认异步任务完成")
        return sett_doc_id

    def create_ar_doc(self, ar_type="STND", org=1, status="DRAFT"):
        """
        创建应收单公共方法,返回应收单数据
        :param ar_type: 应收单类型代码，默认"STND"（标准财务应收单）
        :param org: 组织编号，1或2，默认1
        :param status: 应收单状态，默认"DRAFT"（草稿）
        :return: 应收单数据
        """
        # 根据org参数选择组织
        if org == 1:
            com_org_id = self.com_org_id
            sls_org_id = self.sls_org_id
            inv_org_id = self.inv_org_id
        elif org == 2:
            com_org_id = self.com_org_id_2
            sls_org_id = self.sls_org_id_2
            inv_org_id = self.inv_org_id_2
        else:
            raise ValueError("org 参数错误，请输入 1 或 2")

        # 检查必要的基础数据
        if not com_org_id or not sls_org_id or not self.cust_id or not self.curr_id:
            raise ValueError("缺少必要的基础数据，请检查init_data和md_cache_data")

        # 获取税率，如果没有则使用默认值13.0
        tax_rate = self.tax_rate if self.tax_rate else 13.0

        # 应收日期（当前时间戳，毫秒）
        ar_date = int(time.time() * 1000)

        # 应收单行项基础参数（使用随机数）
        ar_qty = random.randint(10, 1000)  # 数量：随机10-1000
        gross_doc_price = round(random.uniform(1.0, 100.0), 2)  # 含税单价：随机1.0-100.0，保留2位小数

        # 计算金额（动态计算，不写死）
        gross_doc_amt = round(ar_qty * gross_doc_price, 2)  # 含税金额 = 数量 × 含税单价
        tax_amt = round(gross_doc_amt * tax_rate / (100 + tax_rate), 2)  # 税额 = 含税金额 × 税率 / (100 + 税率)
        net_doc_amt = round(gross_doc_amt - tax_amt, 2)  # 不含税金额 = 含税金额 - 税额
        sett_item_type_id = self.sett_item_type_info.get("E_SLS_GOODS").get("id")

        # 应收单行项数据
        ar_item = {
            "settItemTypeId": {"id": sett_item_type_id},
            "taxAmt": tax_amt,
            "grossBaseAmt": gross_doc_amt,
            "netBaseAmt": net_doc_amt,
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "matId": {"id": self.mat_id},
            "taxCodeId": {"id": self.tax_code_id},
            "taxRate": tax_rate,
            "arQty": ar_qty,
            "grossDocPrice": gross_doc_price,
            "invOrgId": inv_org_id,
        }

        # 应收单计划行数据
        ar_schl = {
            "dueDate": ar_date,
            "arDocAmt": gross_doc_amt,
            "arBaseAmt": gross_doc_amt,
            "arPercent": 100,
            "receivedDocAmt": 0,
            "unreceivedDocAmt": gross_doc_amt,
            "receivedBaseAmt": 0,
            "unreceivedBaseAmt": gross_doc_amt,
            "collectionClearingStatus": "UNCLEARED",
        }

        ar_type_md_info = self.ar_type_md_info.get(ar_type)
        # 构建应收单请求体
        set_dict = {
            "docTypeId": {"id": ar_type_md_info.get("id"), "arTypeCode": ar_type},
            "comOrgId": {"id": com_org_id},
            "slsOrgId": {"id": sls_org_id},
            "payOrgId": {"id": com_org_id},
            "arDate": ar_date,
            "settPartnerId": {"id": self.cust_id},
            "settPartnerType": "CUSTOMER",
            "docCurrId": {"id": self.curr_id},
            "baseCurrId": {"id": self.curr_id},
            "exchRate": 1.0,
            "arStatus": "DRAFT",
            "collectionClearingStatus": "UNCLEARED",
            "billingClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "arItems": [ar_item],
            "arSchls": [ar_schl],
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_doc_amt,
            "netBaseAmt": net_doc_amt,
            "taxAmt": tax_amt,
            "uncollectedDocAmt": gross_doc_amt,
            "uncollectedBaseAmt": gross_doc_amt,
            "unbilledDocAmt": gross_doc_amt,
            "unbilledBaseAmt": gross_doc_amt,
            "unoffsetDocAmt": gross_doc_amt,
            "unoffsetBaseAmt": gross_doc_amt,
        }

        # 需要过滤的字段列表
        fields_to_filter = [
            "docTypeId",
            "comOrgId",
            "slsOrgId",
            "payOrgId",
            "arDate",
            "settPartnerId",
            "settPartnerType",
            "docCurrId",
            "baseCurrId",
            "exchRate",
            "arStatus",
            "collectionClearingStatus",
            "billingClearingStatus",
            "headOffsetStatus",
            "arItems",
            "arSchls",
            "grossDocAmt",
            "netDocAmt",
            "grossBaseAmt",
            "netBaseAmt",
            "taxAmt",
            "uncollectedDocAmt",
            "uncollectedBaseAmt",
            "unbilledDocAmt",
            "unbilledBaseAmt",
            "unoffsetDocAmt",
            "unoffsetBaseAmt",
        ]

        # 使用标准化API调用
        response, extracted_id = self.standard_api_call(
            api_key="AR-应收单保存服务", set_dict=set_dict, fields_to_filter=fields_to_filter
        )

        # 业务断言
        self.assert_util.assert_response_data(response)

        data = response.get("data", {}).get("data", {})
        extracted_id = data.get("id")
        if extracted_id is None:
            raise ValueError("应收单保存失败：未返回应收单ID")

        if status == "DONE":
            self.db.update("fin_arm_ar_head_tr", {"ar_status": "DONE"}, f"id='{extracted_id}'")
        elif status == "CONFIRM":
            self.db.update("fin_arm_ar_head_tr", {"ar_status": "CONFIRM"}, f"id='{extracted_id}'")
        else:
            raise ValueError("status 参数错误，请输入 DRAFT, CONFIRM, DONE")
        return data

    @classmethod
    def teardown_class(cls):
        """测试类清理 (beyond super)"""
        try:
            # fin specific cleanup if needed (e.g., clear fin_cache)
            cls.logger.info("ERP财务模块测试类清理完成")
        finally:
            super().teardown_class()


if __name__ == "__main__":
    test = FinBaseTest()
    test.setup_class()
