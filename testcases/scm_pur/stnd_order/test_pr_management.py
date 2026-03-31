import allure
import pytest
import time

from testcases.scm_pur import ScmPurBaseTest
from utils.report_util import a, case_decorator


@allure.epic("采购管理")
@allure.feature("采购申请管理")
class TestPrManagement(ScmPurBaseTest):
    """采购申请管理：分页、新建、详情、删除、复制、任务流转与匹配。"""
    DEFAULT_PR_TYPE_ID_FROM_CURL = 14008002

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
        cls.pr_head_id = None
        cls.pr_item_id = None
        cls.created_pr_id = None

    @classmethod
    def bind_context(cls):
        super().bind_context()

        cls.pur_org_id = None
        cls.com_org_id = None
        cls.pur_employee_id = None
        cls.pr_type_id = None
        cls.vend_id = None
        cls.quota_id = None
        cls.mat_id = None
        cls.inv_org_id = None
        cls.inv_loc_id = None
        cls.uom_pur_id = None

        if cls.md_cache_data:
            org_info = cls.md_cache_data.get("org_info", {})
            pur_org_info = org_info.get("pur_org_info", [])
            com_org_info = org_info.get("gr_come_org_info", [])
            employee_info = org_info.get("employee_info", [])
            inv_org_info = org_info.get("inv_org_info", [])
            inv_loc_info = org_info.get("inv_loc_info", [])
            partner_info = cls.md_cache_data.get("partner_info", {})
            vend_info = partner_info.get("vend_info", [])
            finp_list = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])

            cls.pur_org_id = pur_org_info[0].get("id") if pur_org_info else None
            cls.com_org_id = com_org_info[0].get("id") if com_org_info else None
            cls.pur_employee_id = employee_info[0].get("id") if employee_info else None
            cls.vend_id = vend_info[0].get("id") if vend_info else None
            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None
            cls.inv_loc_id = inv_loc_info[0].get("id") if inv_loc_info else None
            cls.mat_id = finp_list[0].get("id") if finp_list else None

        if cls.pur_cache_data:
            pur_config = cls.pur_cache_data.get("pur_config", {})
            pr_type_info = pur_config.get("pr_type_info", [])
            quota_info = pur_config.get("quota_info", [])
            cls.pr_type_id = pr_type_info[0].get("id") if pr_type_info else None
            cls.quota_id = quota_info[0].get("id") if quota_info else None

        if cls.init_data:
            uom_info = cls.init_data.get("uom_info", {})
            qty_uom_info = uom_info.get("qty_uom_info", [])
            cls.uom_pur_id = qty_uom_info[0].get("uom_id") if qty_uom_info else None

        cls.logger.info("采购申请管理测试类初始化完成")

    def _query_pr_page(self):
        response, _ = self.standard_api_call(
            api_key="采购申请查询ACTION服务",
            set_dict={
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"fieldAlias": "updatedAt", "sortType": "DESC"},
                        {"fieldAlias": "createdAt", "sortType": "DESC"},
                    ],
                }
            },
            fields_to_filter=["pageable"],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_PUR"},
        )
        self.assert_util.assert_response_data(response)
        return response

    def _query_pr_page_by_name(self, pr_name):
        response, _ = self.standard_api_call(
            api_key="采购申请查询ACTION服务",
            set_dict={
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"fieldAlias": "updatedAt", "sortType": "DESC"},
                        {"fieldAlias": "createdAt", "sortType": "DESC"},
                    ],
                    "conditionItems": {
                        "type": "ConditionItems",
                        "logicOperator": "AND",
                        "conditions": {"prName": {"operator": "CONTAINS", "value": pr_name}},
                    },
                }
            },
            fields_to_filter=["pageable"],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_PUR"},
        )
        self.assert_util.assert_response_data(response)
        return response

    def _query_pr_detail(self, pr_head_id):
        response, _ = self.standard_api_call(
            api_key="采购申请单据表-根据ID查找单表数据服务",
            set_dict={"id": pr_head_id},
            fields_to_filter=["id"],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_PUR"},
        )
        self.assert_util.assert_response_data(response)
        return response

    def _to_int_id(self, value):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str):
            s = value.strip()
            if s.isdigit():
                return int(s)
            if s.endswith(".0") and s[:-2].isdigit():
                return int(s[:-2])
        return None

    def _safe_get(self, data, keys):
        cur = data
        for k in keys:
            if isinstance(cur, dict):
                cur = cur.get(k)
            elif isinstance(cur, list) and isinstance(k, int):
                if 0 <= k < len(cur):
                    cur = cur[k]
                else:
                    return None
            else:
                return None
        return cur

    def _extract_pr_head_id_from_response(self, response, new_id=None):
        candidates = []
        if new_id is not None:
            candidates.append(new_id)
        if isinstance(response, dict):
            candidates.extend([
                self._safe_get(response, ["data", "data", "id"]),
                self._safe_get(response, ["data", "id"]),
                self._safe_get(response, ["data", "request", "id"]),
                self._safe_get(response, ["data", "data", "request", "id"]),
                self._safe_get(response, ["data", "data", "prItemCode", 0, "purPrHeadTrId", "id"]),
            ])
        # 对“创建成功响应里明确返回的ID”优先信任，避免刚创建后的短暂可见性延迟导致误判。
        for c in candidates:
            cid = self._to_int_id(c)
            if cid:
                return cid
        return None

    def _extract_first_item_id(self, detail_data):
        if not isinstance(detail_data, dict):
            return None
        for key in ("prItem", "prItems", "itemList", "items", "data", "prItemCode"):
            val = detail_data.get(key)
            if isinstance(val, list) and val:
                first = val[0] or {}
                if isinstance(first, dict) and first.get("id"):
                    return first.get("id")
        return None

    def _ensure_pr_head_and_item_id(self):
        if self.__class__.pr_head_id and self.__class__.pr_item_id:
            return self.__class__.pr_head_id, self.__class__.pr_item_id

        page_resp = self._query_pr_page()
        rows = page_resp.get("data", {}).get("data", {}).get("data", []) or []
        if not rows:
            return None, None

        self.__class__.pr_head_id = rows[0].get("id")
        detail_resp = self._query_pr_detail(self.__class__.pr_head_id)
        detail_data = detail_resp.get("data", {}).get("data", {}) or {}
        self.__class__.pr_item_id = self._extract_first_item_id(detail_data)
        return self.__class__.pr_head_id, self.__class__.pr_item_id

    def _create_pr_draft(self):
        # 按录制 cURL 结构创建草稿，创建链路不混入“复制兜底”。
        pr_name = f"AT_PR_{self.mock_util.get_timestamp()}"
        self.__class__.created_pr_name = pr_name
        pr_type_id = self.pr_type_id or self.DEFAULT_PR_TYPE_ID_FROM_CURL
        if not self.pr_type_id:
            self.logger.warning(
                f"未从缓存获取 pr_type_id，回退使用录制值: {self.DEFAULT_PR_TYPE_ID_FROM_CURL}"
            )
        save_dict = {
            "id": None,
            "version": 0,
            "prCode": None,
            "prType": {"id": pr_type_id, "allowSelectionSku": False},
            "prName": pr_name,
            "remark": "自动化测试提交",
            "comOrgId": {"id": self.com_org_id} if self.com_org_id else None,
            "businessDate": int(time.time() * 1000),
            "origin": "BY_HEAD",
            "text": [{"context": {}, "textType": {"id": 2102001, "textName": None}, "note": None}],
            "partner": [{"context": {}, "partnerTypeRef": {"id": 2000005}, "partnerRef": None, "partnerName": None}],
            "attachment": [],
            "prItemCode": [{
                "context": {},
                "deleted": 0,
                "prItemType": {"id": 2000001},
                "matId": {"id": self.mat_id} if self.mat_id else None,
                "uomBaseId": {"id": self.uom_pur_id} if self.uom_pur_id else None,
                "prQty": 123,
                "prMatAmtEstimate": 1999,
                "invOrgId": {"id": self.inv_org_id} if self.inv_org_id else None,
                "prQtyOpen": 0,
                "invLocId": {"id": self.inv_loc_id} if self.inv_loc_id else None,
                "prDateDnReqful": int((time.time() + 20 * 24 * 3600) * 1000),
                "taxratePercent": "0",
                "priceGross": 0,
                "uomPurId": {"id": self.uom_pur_id} if self.uom_pur_id else None,
                "prQtyPur": 123,
                "outsourcingSupplierId": {"id": -1},
                "purEmployeeAssigned": False,
            }],
        }
        response, new_id = self.standard_api_call(
            api_key="PR-创建采购申请-保存服务",
            set_dict=save_dict,
            fields_to_filter=[
                "id", "version", "prCode", "prType", "prName", "remark", "comOrgId", "businessDate",
                "origin", "text", "partner", "attachment", "prItemCode"
            ],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_PUR"},
        )
        self.assert_util.assert_response_data(response)
        created_id = self._extract_pr_head_id_from_response(response, new_id=new_id)

        if created_id is None:
            rows = self._query_pr_page_by_name(pr_name).get("data", {}).get("data", {}).get("data", []) or []
            if rows:
                created_id = self._to_int_id(rows[0].get("id"))

        return response, created_id

    def _try_activate_pr_item(self, pr_item_id):
        if not pr_item_id:
            return False
        response, _ = self.standard_api_call(
            api_key="PR-ITEM状态变更-草稿-生效服务",
            set_dict=[{"id": pr_item_id}],
            param_path=["params", "request"],
            query_params={"tmodule": "SCM_PUR"},
        )
        return bool(response.get("success"))

    @case_decorator(
        story="采购申请管理",
        title="分页查询采购申请",
        severity="critical",
        file_level_order=1,
        tags=["scm_pur", "pr", "paging"],
    )
    def test_query_pr_page(self):
        try:
            response = self._query_pr_page()
            rows = response.get("data", {}).get("data", {}).get("data", []) or []
            self.assert_util.assert_by_operator(isinstance(rows, list), "=", True, "分页结果应为列表")
            if rows:
                self.__class__.pr_head_id = rows[0].get("id")
            a.json(response, "采购申请分页响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="新建采购申请",
        severity="critical",
        file_level_order=2,
        tags=["scm_pur", "pr", "create"],
    )
    def test_create_pr(self):
        try:
            response, created_id = self._create_pr_draft()
            if isinstance(created_id, dict):
                created_id = created_id.get("id")
            self.assert_util.assert_response_data(response)
            self.assert_util.assert_by_operator(created_id is not None, "=", True, "新建后ID不应为空")
            self.__class__.created_pr_id = created_id
            a.json(response, "采购申请新建响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="采购申请详情查询",
        severity="critical",
        file_level_order=3,
        tags=["scm_pur", "pr", "detail"],
    )
    def test_query_pr_detail(self):
        try:
            pr_head_id = self.__class__.created_pr_id or self.__class__.pr_head_id
            if not pr_head_id:
                pr_head_id, _ = self._ensure_pr_head_and_item_id()
            if not pr_head_id:
                pytest.skip("未查询到可用采购申请，跳过详情查询")

            response = self._query_pr_detail(pr_head_id)
            detail = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail is not None, "=", True, "详情不应为空")
            item_id = self._extract_first_item_id(detail)
            if item_id:
                self.__class__.pr_item_id = item_id
            a.json(response, "采购申请详情响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="删除采购申请(仅草稿态)",
        severity="normal",
        file_level_order=4,
        tags=["scm_pur", "pr", "delete", "draft"],
    )
    def test_delete_pr_draft(self):
        try:
            pr_head_id = self.__class__.created_pr_id
            if not pr_head_id:
                create_resp, pr_head_id = self._create_pr_draft()
                self.assert_util.assert_response_data(create_resp)
            if not pr_head_id:
                pytest.skip("无法准备草稿采购申请，跳过删除")

            detail_resp = self._query_pr_detail(pr_head_id)
            detail = detail_resp.get("data", {}).get("data", {}) or {}
            doc_status = detail.get("documentStatus")
            if doc_status and doc_status != "DRAFT":
                pytest.skip(f"仅草稿态可删除，当前状态: {doc_status}")

            response, _ = self.standard_api_call(
                api_key="(系统)删除数据服务",
                set_dict={"request": {"id": pr_head_id}, "modelKey": "SCM_PUR$pur_pr_head_tr"},
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_pr_head_tr"},
            )
            self.assert_util.assert_response_success(response)
            a.json(response, "采购申请删除响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="复制采购申请",
        severity="normal",
        file_level_order=5,
        tags=["scm_pur", "pr", "copy"],
    )
    def test_copy_pr(self):
        try:
            pr_head_id = self.__class__.pr_head_id or self.__class__.created_pr_id
            if not pr_head_id:
                pr_head_id, _ = self._ensure_pr_head_and_item_id()
            if not pr_head_id:
                pytest.skip("未查询到可复制采购申请")

            response, copied_id = self.standard_api_call(
                api_key="PR-申请复制服务",
                set_dict={"id": pr_head_id},
                fields_to_filter=["id"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            payload = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(isinstance(payload, dict), "=", True, "复制响应数据应为对象")
            # 复制初始化接口可不返回持久化ID，只校验关键数据结构存在。
            self.assert_util.assert_by_operator(bool(payload), "=", True, "复制响应数据不应为空")
            a.json(response, "采购申请复制响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="采购申请任务指派",
        severity="normal",
        file_level_order=6,
        tags=["scm_pur", "pr", "assign"],
    )
    def test_assign_pr_task(self):
        try:
            pr_head_id, _ = self._ensure_pr_head_and_item_id()
            if not pr_head_id:
                pytest.skip("未查询到可指派采购申请")
            if not self.pur_employee_id:
                pytest.skip("未获取到采购员ID，跳过指派")

            response, _ = self.standard_api_call(
                api_key="PR-整单指派服务",
                set_dict={"id": pr_head_id, "purEmployee": {"id": self.pur_employee_id}},
                fields_to_filter=["id", "purEmployee"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            if not response.get("success"):
                err_code = response.get("err", {}).get("code")
                if err_code == "pur.pr.item.status.is.error":
                    # 尝试推进申请行到可指派状态后重试一次。
                    _, pr_item_id = self._ensure_pr_head_and_item_id()
                    if self._try_activate_pr_item(pr_item_id):
                        response, _ = self.standard_api_call(
                            api_key="PR-整单指派服务",
                            set_dict={"id": pr_head_id, "purEmployee": {"id": self.pur_employee_id}},
                            fields_to_filter=["id", "purEmployee"],
                            param_path=["params", "request"],
                            query_params={"tmodule": "SCM_PUR"},
                        )
                    if not response.get("success"):
                        pytest.skip("当前申请行状态不满足指派前置条件，且自动推进后仍不可指派")
            self.assert_util.assert_response_data(response)
            a.json(response, "采购申请任务指派响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="匹配价格协议",
        severity="normal",
        file_level_order=7,
        tags=["scm_pur", "pr", "price_agreement"],
    )
    def test_match_price_agreement(self):
        try:
            _, pr_item_id = self._ensure_pr_head_and_item_id()
            if not pr_item_id:
                pytest.skip("未查询到可匹配价格协议的申请行")

            response, _ = self.standard_api_call(
                api_key="PR-采购申请行已指派-批量自动匹配价格协议服务",
                set_dict=[{"id": pr_item_id}],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "匹配价格协议响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="匹配配额协议",
        severity="normal",
        file_level_order=8,
        tags=["scm_pur", "pr", "quota_agreement"],
    )
    def test_match_quota_agreement(self):
        try:
            _, pr_item_id = self._ensure_pr_head_and_item_id()
            if not pr_item_id:
                pytest.skip("未查询到可匹配配额协议的申请行")
            if not self.quota_id:
                pytest.skip("未获取到配额协议ID，跳过匹配")

            response, _ = self.standard_api_call(
                api_key="PR-ITEM-匹配配额协议-保存服务",
                set_dict={"id": pr_item_id, "purQuotaId": {"id": self.quota_id}},
                fields_to_filter=["id", "purQuotaId"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "匹配配额协议响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="更新供应商",
        severity="normal",
        file_level_order=9,
        tags=["scm_pur", "pr", "update_supplier"],
    )
    def test_update_supplier(self):
        try:
            _, pr_item_id = self._ensure_pr_head_and_item_id()
            if not pr_item_id:
                pytest.skip("未查询到可更新供应商的申请行")
            if not self.vend_id:
                pytest.skip("未获取到供应商ID，跳过更新")

            response, _ = self.standard_api_call(
                api_key="根据id更新采购申请行",
                set_dict={"id": pr_item_id, "vendId": {"id": self.vend_id}},
                fields_to_filter=["id", "vendId"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "更新供应商响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="分页查询我的采购任务",
        severity="normal",
        file_level_order=10,
        tags=["scm_pur", "pr", "my_tasks", "paging"],
    )
    def test_query_my_purchase_tasks(self):
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": [
                        {"fieldAlias": "createdAt", "sortType": "DESC"},
                        {"fieldAlias": "id", "sortType": "DESC"},
                    ],
                    "conditionItems": {},
                    "conditionGroup": {},
                }
            }
            response, _ = self.standard_api_call(
                api_key="分页查询我的采购任务",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                param_path=["params"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            data = response.get("data", {}).get("data", {})
            rows = data.get("data", []) if isinstance(data, dict) else []
            self.assert_util.assert_by_operator(isinstance(rows, list), "=", True, "任务分页结果应为列表")
            a.json(response, "我的采购任务分页响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="我的采购任务转办",
        severity="normal",
        file_level_order=11,
        tags=["scm_pur", "pr", "task_transfer"],
    )
    def test_transfer_my_purchase_task(self):
        try:
            _, pr_item_id = self._ensure_pr_head_and_item_id()
            if not pr_item_id:
                pytest.skip("未查询到可转办采购任务")
            if not self.pur_employee_id:
                pytest.skip("未获取到采购员ID，跳过转办")

            response, _ = self.standard_api_call(
                api_key="PR-采购任务-转办服务",
                set_dict={"id": pr_item_id, "purEmployee": {"id": self.pur_employee_id}},
                fields_to_filter=["id", "purEmployee"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "采购任务转办响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请管理",
        title="采购任务转采购订单",
        severity="normal",
        file_level_order=12,
        tags=["scm_pur", "pr", "task_to_po"],
    )
    def test_task_to_purchase_order(self):
        try:
            _, pr_item_id = self._ensure_pr_head_and_item_id()
            if not pr_item_id:
                pytest.skip("未查询到可转采购订单的采购任务")

            response, _ = self.standard_api_call(
                api_key="PR-ITEM-创建采购订单服务",
                set_dict={"id": pr_item_id},
                fields_to_filter=["id"],
                param_path=["params", "request"],
                query_params={"tmodule": "SCM_PUR"},
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "采购任务转采购订单响应")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
