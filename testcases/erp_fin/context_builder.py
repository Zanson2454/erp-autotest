from typing import Any, Dict, List, Optional


def _first_or_none(rows: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    if not rows:
        return None
    return rows[0]


def build_fin_context(
    init_data: Optional[Dict[str, Any]],
    md_cache_data: Optional[Dict[str, Any]],
    fin_cache_data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}

    init_data = init_data or {}
    md_cache_data = md_cache_data or {}
    fin_cache_data = fin_cache_data or {}

    currency = _first_or_none(init_data.get("currency_info") or [])
    tax_info = _first_or_none(init_data.get("tax_info") or [])
    qty_uom = _first_or_none((init_data.get("uom_info") or {}).get("qty_uom_info") or [])

    ctx["curr_id"] = currency.get("curr_id") if currency else None
    tax_rate_value = tax_info.get("tax") if tax_info else None
    ctx["tax_rate"] = float(tax_rate_value) if tax_rate_value is not None else None
    ctx["tax_code_id"] = tax_info.get("id") if tax_info else None
    ctx["basic_unit_id"] = qty_uom.get("uom_id") if qty_uom else None

    org_info = md_cache_data.get("org_info") or {}
    partner_info = md_cache_data.get("partner_info") or {}
    mat_info = md_cache_data.get("mat_info") or {}

    gr_come_org_info = _first_or_none(org_info.get("gr_come_org_info") or [])
    sls_org_info = _first_or_none(org_info.get("sls_org_info") or [])
    pur_org_info = _first_or_none(org_info.get("pur_org_info") or [])
    inv_org_info = _first_or_none(org_info.get("inv_org_info") or [])

    com_org_info = _first_or_none(org_info.get("com_org_info") or [])
    inv_org_info2 = _first_or_none(org_info.get("inv_org_info2") or [])
    sls_org_info2 = _first_or_none(org_info.get("sls_org_info2") or [])
    pur_org_info2 = _first_or_none(org_info.get("pur_org_info2") or [])

    cust_info = _first_or_none(partner_info.get("cust_info") or [])
    vend_info = _first_or_none(partner_info.get("vend_info") or [])

    finp_mat = _first_or_none(((mat_info.get("mat_md") or {}).get("FINP") or []))
    finp_mat_type = _first_or_none(((mat_info.get("mat_type_cf") or {}).get("FINP") or []))

    ctx["gr_com_org_id"] = gr_come_org_info.get("id") if gr_come_org_info else None
    ctx["com_org_id"] = gr_come_org_info.get("id") if gr_come_org_info else None
    ctx["sls_org_id"] = sls_org_info.get("id") if sls_org_info else None
    ctx["pur_org_id"] = pur_org_info.get("id") if pur_org_info else None
    ctx["inv_org_id"] = inv_org_info.get("id") if inv_org_info else None

    ctx["com_org_id_2"] = com_org_info.get("id") if com_org_info else None
    ctx["inv_org_id_2"] = inv_org_info2.get("id") if inv_org_info2 else None
    ctx["sls_org_id_2"] = sls_org_info2.get("id") if sls_org_info2 else None
    ctx["pur_org_id_2"] = pur_org_info2.get("id") if pur_org_info2 else None

    ctx["cust_id"] = cust_info.get("id") if cust_info else None
    ctx["vend_id"] = vend_info.get("id") if vend_info else None
    ctx["mat_id"] = finp_mat.get("id") if finp_mat else None
    ctx["mat_type_cf"] = finp_mat_type.get("id") if finp_mat_type else None

    ctx["ap_type_info"] = fin_cache_data.get("ap_type_info", {})

    sett_item_type_info_list = (fin_cache_data.get("sett_item_info", {}) or {}).get("sett_item_type_info", [])
    ctx["sett_item_type_info"] = {
        item.get("sett_item_type_code"): item
        for item in sett_item_type_info_list
        if item.get("sett_item_type_code")
    }

    ar_type_md_info_list = (fin_cache_data.get("ar_type_info", {}) or {}).get("ar_type_md_info", [])
    ctx["ar_type_md_info"] = {
        item.get("ar_type_code"): item
        for item in ar_type_md_info_list
        if item.get("ar_type_code")
    }

    sb_type_info_list = (fin_cache_data.get("sb_type_info", {}) or {}).get("sb_bill_type_info", [])
    ctx["sb_type_info"] = {
        item.get("sb_type_code"): item
        for item in sb_type_info_list
        if item.get("sb_type_code")
    }

    sett_doc_type_info_list = (fin_cache_data.get("sett_doc_info", {}) or {}).get("sett_doc_type_info", [])
    ctx["sett_doc_type_info"] = sett_doc_type_info_list[0].get("id") if sett_doc_type_info_list else None

    calender_head_info = (fin_cache_data.get("calender_info", {}) or {}).get("calender_head_info", [])
    calender_item_info = (fin_cache_data.get("calender_info", {}) or {}).get("calender_item_info", [])
    ctx["calendar_head_id"] = calender_head_info[0].get("id") if calender_head_info else None

    month_items = [item for item in calender_item_info if item.get("period_type") == "MONTH"]
    ctx["calendar_item_id"] = month_items[0].get("id") if month_items else None

    return ctx
