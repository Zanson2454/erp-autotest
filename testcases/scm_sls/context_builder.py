from typing import Any, Dict, List, Optional


def _first_or_none(rows: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    if not rows:
        return None
    return rows[0]


def build_sls_context(
    init_data: Optional[Dict[str, Any]],
    md_cache_data: Optional[Dict[str, Any]],
    sls_cache_data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}

    init_data = init_data or {}
    md_cache_data = md_cache_data or {}
    sls_cache_data = sls_cache_data or {}

    currency = _first_or_none(init_data.get("currency_info") or [])
    country = _first_or_none(init_data.get("country_info") or [])
    exchange_rate_type = _first_or_none(init_data.get("exchange_rate_type_info") or [])

    ctx["curr_id"] = currency.get("curr_id") if currency else 2000001
    ctx["coun_id"] = country.get("coun_id") if country else None
    ctx["exchange_rate_type_id"] = exchange_rate_type.get("exchange_rate_type_id") if exchange_rate_type else None

    partner_info = md_cache_data.get("partner_info") or {}
    org_info = md_cache_data.get("org_info") or {}
    mat_info = md_cache_data.get("mat_info") or {}
    mat_md = mat_info.get("mat_md") or {}

    cust_info = _first_or_none(partner_info.get("cust_info") or [])
    gr_come_org = _first_or_none(org_info.get("gr_come_org_info") or [])
    sls_dc = _first_or_none(org_info.get("sls_dc_md") or [])
    sls_org = _first_or_none(org_info.get("sls_org_info") or [])
    inv_org = _first_or_none(org_info.get("inv_org_info") or [])
    inv_loc = _first_or_none(org_info.get("inv_loc_info") or [])
    sls_partner_type = _first_or_none((partner_info.get("partner_type_cf") or {}).get("sls_partner_type") or [])
    finp = _first_or_none(mat_md.get("FINP") or [])

    ctx["cust_id"] = cust_info.get("id") if cust_info else None
    ctx["com_org_id"] = gr_come_org.get("id") if gr_come_org else None
    ctx["sls_dc_id"] = sls_dc.get("id") if sls_dc else None
    ctx["sls_org_id"] = sls_org.get("id") if sls_org else None
    ctx["inv_org_id"] = inv_org.get("id") if inv_org else None
    ctx["inv_loc_id"] = inv_loc.get("id") if inv_loc else None
    ctx["partner_type_id"] = sls_partner_type.get("id") if sls_partner_type else None
    ctx["mat_id"] = finp.get("id") if finp else None
    ctx["mat_code"] = finp.get("mat_code") if finp else None
    ctx["mat_name"] = finp.get("mat_name") if finp else None

    sls_config = sls_cache_data.get("sls_config") or {}
    so_type_info = sls_config.get("so_type_info") or []
    so_item_type_info = sls_config.get("so_item_type_info") or []
    rebate_type_info = sls_config.get("rebate_type_info") or []

    ctx["so_type_info"] = so_type_info
    ctx["ORDER_TYPES"] = so_type_info
    ctx["so_item_type_info"] = so_item_type_info
    ctx["ORDER_LINE_TYPES"] = so_item_type_info
    ctx["rebate_type_info"] = rebate_type_info

    ctx["stnd_so_type_id"] = None
    ctx["thrd_so_type_id"] = None
    ctx["cent_so_type_id"] = None
    ctx["quote_so_type_id"] = None
    for so_type in so_type_info:
        code = so_type.get("so_type_code")
        if code == "STND":
            ctx["stnd_so_type_id"] = so_type.get("id")
        if code == "THRD":
            ctx["thrd_so_type_id"] = so_type.get("id")
        if code == "CENT":
            ctx["cent_so_type_id"] = so_type.get("id")
        if code == "QUOTE":
            ctx["quote_so_type_id"] = so_type.get("id")

    ctx["stnd_so_item_type_id"] = None
    for so_item_type in so_item_type_info:
        if so_item_type.get("so_item_type_code") == "NORM":
            ctx["stnd_so_item_type_id"] = so_item_type.get("id")

    ctx["stnd_rebate_type_id"] = None
    for rebate_type in rebate_type_info:
        if rebate_type.get("rebate_type_code") == "STND":
            ctx["stnd_rebate_type_id"] = rebate_type.get("id")

    ctx["ORDER_TYPE_LINE_COMBINATIONS"] = []
    for so_type in so_type_info:
        for so_item_type in so_item_type_info:
            ctx["ORDER_TYPE_LINE_COMBINATIONS"].append(
                {"so_type": so_type, "so_item_type": so_item_type}
            )

    return ctx
