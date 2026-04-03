# -*- coding: utf-8 -*-
"""
工单取消确认测试用例
包含工单取消确认的完整业务流程测试
"""

import json
from datetime import date, datetime
from decimal import Decimal

import allure

from testcases.erp_prd import PrdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("生产管理")
@allure.feature("工单取消确认")
class TestWorkOrderCancelConfirm(PrdBaseTest):
    """工单取消确认测试用例

    本测试用例验证工单取消确认的完整业务流程，包括：
    1. 查询待取消确认的工单列表
    2. 查询已过账入库工序送货单详情
    3. 执行工单取消确认操作
    4. 验证工单状态变更
    5. 验证移动凭证冲销
    """

    # 保存测试过程中的数据
    cancel_info = {}

    def json_default(self, obj):
        """处理特殊类型的JSON序列化"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return str(obj)

    def init(self):
        """初始化测试数据"""
        self.logger.info("开始初始化工单取消确认测试数据")
        # 不再需要获取生产订单信息
        pass

    @case_decorator(
        story="工单取消确认",
        title="查询测试物料待取消确认的工单列表",
        description="""
    步骤：
    1. 使用SQL直接查询待取消确认的工单列表
    2. 保存工单列表信息用于后续测试
    
    验证点：
    - 能成功查询到工单列表
    - 工单数据结构完整
    """,
        severity="normal",
        file_level_order=1,
    )
    def test_query_cancel_confirm_list(self):
        """查询测试物料待取消确认的工单列表

        步骤：
        1. 使用SQL直接查询待取消确认的工单列表
        2. 保存工单列表信息用于后续测试

        验证点：
        - 能成功查询到工单列表
        - 工单数据结构完整
        """
        try:
            with a.step("查询待取消确认的工单列表"):
                # 构建SQL查询
                sql = f"""
                    SELECT 
                        p.id,
                        p.confirm_code,
                        p.wo_id,
                        p.mat_id,
                        p.inv_org_id,
                        p.operation_id,
                        p.yield_qty,
                        p.scrapped_qty,
                        p.operation_uom_id,
                        p.doc_date,
                        p.status,
                        p.mov_type_id,
                        p.mov_assign_cf_id,
                        p.qty,
                        p.uom_id,
                        p.inv_loc_id,
                        p.post_inv_type_id,
                        p.move_voucher_id,
                        p.posting_date,
                        p.dn_code,
                        d.biz_status as dn_biz_status,
                        d.del_status as dn_del_status,
                        d.updated_at
                    FROM prd_order_confirm_header_tr p
                    JOIN del_dn_head_tr d ON p.dn_code = d.dn_code COLLATE utf8mb4_general_ci
                    WHERE 
                    p.mat_id = {self.base_info["prd_mat_info"]["id"]}
                    AND p.mov_type_id IS NOT NULL
                    AND p.cancel_is IS NULL
                    AND d.biz_status = 'POSTED'
                    AND p.deleted = 0
                    ORDER BY d.updated_at DESC
                    LIMIT 1
                """

                # 执行查询
                records = self.query_service.query(sql)
                self.logger.info(f"查询到{len(records)}条待取消确认的工单记录")

                # 保存查询结果
                self.cancel_info["records"] = records

                # 验证查询结果
                assert records, "未找到待取消确认的工单记录"

                # 添加报告附件 - 使用自定义的JSON序列化处理
                records_json = json.dumps(records, default=self.json_default, ensure_ascii=False, indent=2)
                a.text(records_json, "查询结果数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工单取消确认",
        title="查询已过账入库工序送货单详情",
        description="""
    步骤：
    1. 使用已过账入库工序送货单进行详情查询
    2. 验证送货单相关信息的完整性
    
    验证点：
    - 能成功查询到已过账入库工序送货单明细
    - 送货单状态正确（未生效、已过账）
    - 相关业务数据完整
    """,
        severity="normal",
        file_level_order=2,
    )
    def test_query_posted_dn_detail(self):
        """查询已过账入库工序送货单详情

        步骤：
        1. 使用已过账入库工序送货单进行详情查询
        2. 验证送货单相关信息的完整性

        验证点：
        - 能成功查询到已过账入库工序送货单明细
        - 送货单状态正确（未生效、已过账）
        - 相关业务数据完整
        """
        try:
            with a.step("查询已过账入库工序送货单详情"):
                # 获取SCM模块的API配置
                api_path = self.get_cross_module_api_path("scm", "DEL-过账专属交货单详情服务")
                params, url = self.get_cross_module_api_params("scm", api_path)

                # 获取需要查询的送货单信息
                records = self.cancel_info.get("records", [])
                assert records, "没有找到需要查询的送货单记录"

                # 查询送货单头表ID
                dn_codes = [f"'{record['dn_code']}'" for record in records]
                head_sql = f"""
                    SELECT id, dn_code, del_status, biz_status, bt_class
                    FROM del_dn_head_tr 
                    WHERE dn_code IN ({','.join(dn_codes)})
                    AND bt_class = 'PRD_CONFIRM'
                    AND biz_status = 'POSTED'
                    AND deleted = 0
                """
                head_results = self.query_service.query(head_sql)
                assert head_results, "没有找到符合条件的送货单头表记录"

                post_detail_results = []
                for head_record in head_results:
                    dn_code = head_record["dn_code"]
                    self.logger.info(f"查询已过账入库工序送货单{dn_code}的详情")

                    # 设置查询参数
                    filtered_params = {"params": {"request": {"id": head_record["id"]}}}

                    # 发送请求
                    result, _ = self.standard_api_call(
                        api_key="DEL-过账专属交货单详情服务",
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"],
                        cross_module_name="scm",
                    )
                    # 验证响应
                    self.assert_util.assert_response_success(result)

                    # 保存查询结果
                    detail = result.get("data", {}).get("data", {})
                    post_detail_results.append({"dnCode": dn_code, "detail": detail})

                    # 验证送货单基本信息
                    assert detail.get("dnCode") == dn_code, "送货单号不匹配"
                    assert detail.get("btClass") == "PRD_CONFIRM", "业务类型不是生产确认"
                    assert detail.get("delStatus") == "INEFFECT", "单据状态不是未生效"
                    assert detail.get("bizStatus") == "POSTED", "业务状态不是已过账"

                    # 验证库存相关信息
                    assert detail.get("invOrgId"), "未找到库存组织"
                    assert detail.get("invLocId"), "未找到库存地点"

                    # 验证移动凭证信息
                    assert detail.get("moveVoucherId"), "未找到移动凭证ID"
                    assert detail.get("postingDate"), "未找到过账日期"

                    self.logger.info(f"已过账入库工序送货单{dn_code}详情查询成功")

                # 保存所有查询结果
                self.cancel_info["post_detail_results"] = post_detail_results

                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(post_detail_results, "送货单详情查询结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工单取消确认",
        title="执行送货单冲销操作",
        description="""
    步骤：
    1. 使用已过账入库工序送货单详情进行冲销操作
    2. 验证冲销操作的结果
    
    验证点：
    - 冲销操作成功执行
    - 送货单状态从POSTED变为WAIT_POST
    - 移动凭证被冲销
    """,
        severity="blocker",
        file_level_order=3,
    )
    def test_execute_dn_cancel_posting(self):
        """执行送货单冲销操作

        步骤：
        1. 使用已过账入库工序送货单详情进行冲销操作
        2. 验证冲销操作的结果

        验证点：
        - 冲销操作成功执行
        - 送货单状态从POSTED变为WAIT_POST
        - 移动凭证被冲销
        """
        try:
            with a.step("执行送货单冲销操作"):
                # 获取SCM模块的API配置
                api_path = self.get_cross_module_api_path("scm", "DEL-交货单取消过账服务")
                params, url = self.get_cross_module_api_params("scm", api_path)

                # 获取需要冲销的送货单详情
                post_detail_results = self.cancel_info.get("post_detail_results", [])
                assert post_detail_results, "没有找到需要冲销的送货单详情"

                cancel_results = []
                for detail_result in post_detail_results:
                    dn_code = detail_result["dnCode"]
                    detail = detail_result["detail"]
                    self.logger.info(f"执行送货单{dn_code}的冲销操作")

                    # 设置冲销请求参数
                    filtered_params = {
                        "params": {
                            "request": {
                                "id": detail["id"],
                                "btClass": detail["btClass"],
                                "dnCode": detail["dnCode"],
                                "delStatus": detail["delStatus"],
                                "delClass": detail["delClass"],
                                "recvContactPhone": detail.get("recvContactPhone", ""),
                                "recvContactInfo": detail.get("recvContactInfo", ""),
                                "recvAddrId": detail.get("recvAddrId"),
                                "invOrgId": detail["invOrgId"],
                                "isInvExecuted": detail.get("isInvExecuted", False),
                                "wmEnabled": detail.get("wmEnabled", False),
                                "bizStatus": detail["bizStatus"],
                                "invLocId": detail["invLocId"],
                                "postingDate": detail["postingDate"],
                                "moveVoucherId": detail["moveVoucherId"],
                                "docCode": detail["docCode"],
                                "custPrtnId": detail.get("custPrtnId"),
                                "groupConditionKey": detail.get("groupConditionKey"),
                                "docCreateFinal": False,
                                "sourceType": "SYSTEM",
                                "dnItemList": detail.get("dnItemList", []),
                            }
                        }
                    }

                    # 发送冲销请求
                    result, _ = self.standard_api_call(
                        api_key="DEL-交货单取消过账服务",
                        set_dict=filtered_params.get("params", {}),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"],
                        cross_module_name="scm",
                    )

                    # 断言接口返回success
                    if not result.get("success", False):
                        err_msg = result.get("err", {}).get("msg", "未知错误")
                        assert err_msg, f"送货单{dn_code}冲销失败且未返回错误信息"
                        raise AssertionError(f"送货单{dn_code}冲销操作失败: {err_msg}")

                    # 加强断言：冲销后立即查询送货单头表，校验状态
                    head_sql = f"""
                        SELECT biz_status, del_status, id
                        FROM del_dn_head_tr
                        WHERE dn_code = '{dn_code}' AND deleted = 0
                    """
                    head_results = self.query_service.query(head_sql)
                    assert head_results, f"冲销后未查到送货单{dn_code}头表"
                    head_record = head_results[0]
                    assert (
                        head_record["biz_status"] == "WAIT_POST"
                    ), f"送货单{dn_code}冲销后业务状态应为WAIT_POST，实际为{head_record['biz_status']}"
                    assert (
                        head_record["del_status"] == "INEFFECT"
                    ), f"送货单{dn_code}冲销后单据状态应为INEFFECT，实际为{head_record['del_status']}"

                    # 验证行项目状态
                    item_sql = f"""
                        SELECT biz_status, real_del_qty, plan_del_qty
                        FROM del_dn_item_tr
                        WHERE dn_id = {head_record['id']} AND deleted = 0
                    """
                    item_results = self.query_service.query(item_sql)
                    for item in item_results:
                        assert (
                            item["biz_status"] == "WAIT_POST"
                        ), f"送货单{dn_code}行项目业务状态应为WAIT_POST，实际为{item['biz_status']}"

                    # 验证移动凭证是否被冲销
                    # 1. 验证移动凭证头
                    mvm_head_sql = f"""
                        SELECT id, code, doc_id_pre, deleted
                        FROM inv_mvm_doc_head_tr
                        WHERE doc_id_pre = '{dn_code}'
                        AND rev_mvm_doc_id is not null
                        AND deleted = 0
                    """
                    mvm_head_results = self.query_service.query(mvm_head_sql)
                    assert len(mvm_head_results) > 0, f"送货单{dn_code}未找到对应的移动凭证头"
                    mvm_head = mvm_head_results[0]
                    self.logger.info(f"送货单{dn_code}移动凭证头验证通过: code={mvm_head['code']}")

                    # 2. 验证移动凭证行
                    # 2.1 查询原移动凭证行
                    original_mvm_sql = f"""
                        SELECT id, code, mvm_pos_neg, mvm_qty, doc_id_pre, mat_id,
                               assn_doc_code, deleted, mvm_type_id, source_type, mvm_uom_id
                        FROM inv_mvm_doc_item_tr
                        WHERE doc_id_pre = '{dn_code}'
                        AND mvm_pos_neg = 'INCREASE'
                        AND deleted = 0
                    """
                    original_mvm_results = self.query_service.query(original_mvm_sql)
                    assert len(original_mvm_results) > 0, f"送货单{dn_code}未找到对应的原移动凭证行"

                    # 2.2 查询冲销移动凭证行
                    mvm_sql = f"""
                        SELECT id, code, mvm_pos_neg, mvm_qty, doc_id_pre, mat_id,
                               assn_doc_code, deleted, mvm_type_id, source_type, mvm_uom_id
                        FROM inv_mvm_doc_item_tr
                        WHERE doc_id_pre = '{dn_code}'
                        AND mvm_pos_neg = 'DECREASE'
                        AND deleted = 0
                    """
                    mvm_results = self.query_service.query(mvm_sql)
                    assert len(mvm_results) > 0, f"送货单{dn_code}未找到对应的已冲销移动凭证行"

                    # 2.3 验证冲销行数量与原行数量一致
                    assert (
                        len(mvm_results) == len(original_mvm_results)
                    ), f"送货单{dn_code}冲销移动凭证行数量({len(mvm_results)})与原移动凭证行数量({len(original_mvm_results)})不一致"

                    # 2.4 验证每行冲销数量与原数量一致
                    original_mvm_map = {item["mat_id"]: item for item in original_mvm_results}
                    for mvm_item in mvm_results:
                        mat_id = mvm_item["mat_id"]
                        assert mat_id in original_mvm_map, f"冲销移动凭证行物料ID {mat_id} 未在原移动凭证行中找到"
                        original_item = original_mvm_map[mat_id]
                        assert (
                            float(mvm_item["mvm_qty"]) == float(original_item["mvm_qty"])
                        ), f"冲销移动凭证行物料 {mat_id} 数量({mvm_item['mvm_qty']})与原移动凭证行数量({original_item['mvm_qty']})不一致"

                    self.logger.info(
                        f"送货单{dn_code}移动凭证行验证通过: 原行{len(original_mvm_results)}行, 冲销行{len(mvm_results)}行"
                    )

                    # 保存冲销结果
                    cancel_result = {"dnCode": dn_code, "result": result.get("data", {})}
                    cancel_results.append(cancel_result)

                    self.logger.info(f"送货单{dn_code}冲销操作成功")

                # 保存所有冲销结果
                self.cancel_info["cancel_results"] = cancel_results

                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(cancel_results, "冲销操作结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="工单取消确认",
        title="执行工单取消确认操作",
        description="""
    本测试用例验证工单取消确认的完整业务流程，包括数据验证和状态变更。
    
    前置条件：
    1. 已完成送货单冲销操作
    2. 工单状态为已确认或部分确认
    3. 相关送货单状态为已冲销
    
    测试步骤：
    1. 获取取消确认前的数据状态
    2. 执行工单取消确认操作
    3. 验证取消确认后的数据状态
    
    验证点：
    1. 接口调用成功，响应正确
    2. 工艺路线确认数量正确扣减
    3. 工单状态正确变更
    4. 确认单取消标识正确设置
    5. 数据完整性保持
    """,
        severity="critical",
        file_level_order=4,
    )
    def test_execute_cancel_confirm(self):
        """执行工单取消确认操作

        本测试用例验证工单取消确认的完整业务流程，包括数据验证和状态变更。

        前置条件：
        1. 已完成送货单冲销操作
        2. 工单状态为已确认或部分确认
        3. 相关送货单状态为已冲销

        测试步骤：
        1. 获取取消确认前的数据状态
           - 工艺路线数据：已确认数量、工序数量、确认状态
           - 生产订单数据：确认状态
           - 确认单数据：取消标识、删除标识
           - 入库单数据：单据状态、业务状态

        2. 执行工单取消确认操作
           - 调用取消确认服务接口
           - 传入确认单ID列表

        3. 验证取消确认后的数据状态
           - 工艺路线数据变化
             * 确认数量 = 原确认数量 - 报工数量
             * 工序数量保持不变
             * 确认状态根据数量自动计算
           - 生产订单状态变化
             * 根据所有工艺路线状态自动计算
             * UNCONFIRMED: 所有工艺路线未确认
             * CONFIRMED: 所有工艺路线已确认
             * PARTIAL_CONFIRMED: 部分工艺路线已确认
           - 确认单状态变化
             * 取消标识设置为1
             * 删除标识保持为0
           - 入库单状态变化
             * 单据状态变更为作废

        验证点：
        1. 接口调用成功，响应正确
        2. 工艺路线确认数量正确扣减
        3. 工单状态正确变更
        4. 确认单取消标识正确设置
        5. 数据完整性保持

        数据说明：
        1. 工艺路线状态计算规则：
           - UNCONFIRMED: confirmed_qty = 0
           - CONFIRMED: operation_qty <= confirmed_qty
           - PARTIAL_CONFIRMED: 0 < confirmed_qty < operation_qty

        2. 工单状态计算规则：
           - 基于所有工艺路线的确认状态
           - 采用最保守原则判断整单状态

        异常处理：
        1. 数据验证失败时提供详细的错误信息
        2. 使用断言确保关键数据的正确性
        3. 记录完整的数据变更日志
        """
        try:
            with a.step("执行工单取消确认操作"):
                # 获取API配置
                api_path = self.get_api_path("订单确认单-交货确认取消服务")
                params, url = self.get_api_params(api_path)

                # 从工单列表中获取工单ID
                wo_ids = [{"id": record["id"]} for record in self.cancel_info["records"]]
                self.logger.info(f"批量取消确认的工单ID列表: {wo_ids}")

                # 获取需要验证的记录
                record = self.cancel_info["records"][0]
                confirm_id = record["id"]
                wo_id = record["wo_id"]
                dn_code = record["dn_code"]
                operation_id = record["operation_id"]
                yield_qty = float(record["yield_qty"] or 0)  # 获取确认单的良品数量(报工数量)

                with a.step("获取取消确认前的数据"):
                    # 1.1 工艺路线数据
                    pre_routing_sql = f"""
                        SELECT confirmed_qty, operation_qty, confirm_status
                        FROM prd_order_routings_item_tr 
                        WHERE id = {operation_id}
                        AND deleted = 0
                    """
                    pre_routing_results = self.query_service.query(pre_routing_sql)
                    assert pre_routing_results, f"未找到工艺路线记录，ID: {operation_id}"
                    pre_routing = pre_routing_results[0]

                    # 1.2 生产订单数据
                    pre_order_sql = f"""
                        SELECT confirm_status
                        FROM prd_order_header_tr 
                        WHERE id = {wo_id}
                        AND deleted = 0
                    """
                    pre_order_results = self.query_service.query(pre_order_sql)
                    assert pre_order_results, f"未找到生产订单记录，ID: {wo_id}"
                    pre_order = pre_order_results[0]

                    # 1.3 确认单数据
                    pre_confirm_sql = f"""
                        SELECT cancel_is, deleted
                        FROM prd_order_confirm_header_tr 
                        WHERE id = {confirm_id}
                        AND deleted = 0
                    """
                    pre_confirm_results = self.query_service.query(pre_confirm_sql)
                    assert pre_confirm_results, f"未找到确认单记录，ID: {confirm_id}"
                    pre_confirm = pre_confirm_results[0]

                    # 1.4 入库单数据
                    pre_dn_sql = f"""
                        SELECT del_status, biz_status
                        FROM del_dn_head_tr 
                        WHERE dn_code = '{dn_code}'
                    """
                    pre_dn_results = self.query_service.query(pre_dn_sql)
                    assert pre_dn_results, f"未找到入库单记录，单号: {dn_code}"
                    pre_dn = pre_dn_results[0]

                    # 记录取消确认前的数据
                    pre_data = {
                        "routing": {
                            "confirmed_qty": float(pre_routing["confirmed_qty"] or 0),
                            "operation_qty": float(pre_routing["operation_qty"] or 0),
                            "confirm_status": pre_routing["confirm_status"],
                        },
                        "order": {"confirm_status": pre_order["confirm_status"]},
                        "confirm": {"cancel_is": pre_confirm["cancel_is"], "deleted": pre_confirm["deleted"]},
                        "dn": {"del_status": pre_dn["del_status"], "biz_status": pre_dn["biz_status"]},
                    }
                    a.json(pre_data, "取消确认前的数据")

                # 2. 执行取消确认操作
                filtered_params = {"params": {"request": {"ids": [confirm_id]}}}

                # 发送请求
                result, _ = self.standard_api_call(
                    api_key="订单确认单-交货确认取消服务",
                    set_dict=(
                        filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params
                    ),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"],
                )

                # 验证响应成功
                self.assert_util.assert_response_success(result)

                with a.step("获取并验证取消确认后的数据"):
                    # 3.1 工艺路线数据
                    post_routing_sql = f"""
                        SELECT confirmed_qty, operation_qty, confirm_status
                        FROM prd_order_routings_item_tr 
                        WHERE id = {operation_id}
                        AND deleted = 0
                    """
                    post_routing_results = self.query_service.query(post_routing_sql)
                    assert post_routing_results, f"未找到工艺路线记录，ID: {operation_id}"
                    post_routing = post_routing_results[0]

                    # 3.2 生产订单数据
                    post_order_sql = f"""
                        SELECT confirm_status
                        FROM prd_order_header_tr 
                        WHERE id = {wo_id}
                        AND deleted = 0
                    """
                    post_order_results = self.query_service.query(post_order_sql)
                    assert post_order_results, f"未找到生产订单记录，ID: {wo_id}"
                    post_order = post_order_results[0]

                    # 3.3 确认单数据
                    post_confirm_sql = f"""
                        SELECT cancel_is, deleted
                        FROM prd_order_confirm_header_tr 
                        WHERE id = {confirm_id}
                        AND deleted = 0
                    """
                    post_confirm_results = self.query_service.query(post_confirm_sql)
                    assert post_confirm_results, f"未找到确认单记录，ID: {confirm_id}"
                    post_confirm = post_confirm_results[0]

                    # 3.4 入库单数据
                    post_dn_sql = f"""
                        SELECT del_status, biz_status
                        FROM del_dn_head_tr 
                        WHERE dn_code = '{dn_code}'
                    """
                    post_dn_results = self.query_service.query(post_dn_sql)
                    assert post_dn_results, f"未找到入库单记录，单号: {dn_code}"
                    post_dn = post_dn_results[0]

                    # 记录取消确认后的数据
                    post_data = {
                        "routing": {
                            "confirmed_qty": float(post_routing["confirmed_qty"] or 0),
                            "operation_qty": float(post_routing["operation_qty"] or 0),
                            "confirm_status": post_routing["confirm_status"],
                        },
                        "order": {"confirm_status": post_order["confirm_status"]},
                        "confirm": {"cancel_is": post_confirm["cancel_is"], "deleted": post_confirm["deleted"]},
                        "dn": {"del_status": post_dn["del_status"], "biz_status": post_dn["biz_status"]},
                    }
                    a.json(post_data, "取消确认后的数据")

                    # 3.5 验证数据变化
                    with a.step("验证数据变化"):
                        # 验证工艺路线数据变化
                        assert (
                            post_data["routing"]["operation_qty"] == pre_data["routing"]["operation_qty"]
                        ), "工序数量不应该改变"
                        assert (
                            post_data["routing"]["confirmed_qty"] == pre_data["routing"]["confirmed_qty"] - yield_qty
                        ), (
                            f"工艺路线确认数量扣减不正确，"
                            f"原确认数量: {pre_data['routing']['confirmed_qty']}，"
                            f"扣减数量: {yield_qty}，"
                            f"期望数量: {pre_data['routing']['confirmed_qty'] - yield_qty}，"
                            f"实际数量: {post_data['routing']['confirmed_qty']}"
                        )

                        # 验证确认单状态变化
                        assert post_data["confirm"]["cancel_is"] == 1, "确认单取消状态应为1"
                        assert post_data["confirm"]["deleted"] == 0, "确认单不应被删除"

                        # 验证入库单状态变化
                        assert post_data["dn"]["del_status"] == "DISCARDED", "入库单状态应为作废"

                        # 验证生产订单状态变化
                        routing_items_sql = f"""
                            SELECT confirm_status
                            FROM prd_order_routings_item_tr 
                            WHERE prd_order_header_tr_id = {wo_id}
                            AND deleted = 0
                        """
                        routing_items = self.query_service.query(routing_items_sql)
                        routing_statuses = [item["confirm_status"] for item in routing_items]

                        expected_order_status = (
                            "UNCONFIRMED"
                            if all(status == "UNCONFIRMED" for status in routing_statuses)
                            else "CONFIRMED"
                            if all(status == "CONFIRMED" for status in routing_statuses)
                            else "PARTIAL_CONFIRMED"
                        )
                        assert post_data["order"]["confirm_status"] == expected_order_status, (
                            f"生产订单状态不正确，期望为: {expected_order_status}，"
                            f"实际为: {post_data['order']['confirm_status']}，"
                            f"工艺路线状态列表: {routing_statuses}"
                        )

                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    """本地调试入口"""
    test = TestWorkOrderCancelConfirm()
    test.setup_class()
    test.test_query_cancel_confirm_list()  # 查询待取消确认的工单列表
    test.test_query_posted_dn_detail()  # 查询已过账入库工序送货单详情
    test.test_execute_dn_cancel_posting()  # 执行送货单冲销操作
    test.test_execute_cancel_confirm()  # 执行工单取消确认操作
