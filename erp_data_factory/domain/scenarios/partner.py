"""合作伙伴主数据场景实现。"""

from typing import Any, Dict

from erp_data_factory.compat.base import DataFactory
from erp_data_factory.domain.scenarios.base import BaseMasterScenario


class PartnerScenario(BaseMasterScenario):
    """通过 API 或缓存构建/解析客户/供应商伙伴数据。"""

    api_key = "GEN-合作伙伴-保存服务"

    def _extract_data_from_response(
        self, response: Dict[str, Any], extracted_id: Any, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取伙伴标识，并规范化返回伙伴类型。"""
        return {
            "id": extracted_id,
            "partner_code": payload.get("code") or payload.get("partner_code"),
            "partner_type": payload.get("partner_type", "cust"),
        }

    def _run_by_cache(self, payload: Dict[str, Any], context=None) -> Dict[str, Any]:
        """从主数据缓存加载伙伴；失败时返回稳定兜底占位值。"""
        env = getattr(context, "env", "test")
        project = getattr(context, "project", None)
        try:
            DataFactory.__init__(env_name=env, project=project)
            md_cache = DataFactory.init_sql_cache(
                sql_config_path="config/erp/md_init_sql.yaml",
                db_config_name="erp_db",
                cache_key="md_init_cache",
            )
        except Exception:
            partner_type = str(payload.get("partner_type", "cust")).lower()
            return {
                "id": 0,
                "partner_code": payload.get("partner_code", "AT_PARTNER_FALLBACK"),
                "partner_type": "vend" if partner_type in {"vend", "supplier"} else "cust",
            }

        partner_type = str(payload.get("partner_type", "cust")).lower()
        key = "vend_info" if partner_type in {"vend", "supplier"} else "cust_info"
        row = ((md_cache or {}).get("partner_info") or {}).get(key) or []
        if row:
            first = row[0]
            code = first.get("cust_code") or first.get("vend_code") or first.get("code")
            return {
                "id": first.get("id"),
                "partner_code": code,
                "partner_type": "vend" if key == "vend_info" else "cust",
            }
        return {
            "id": 0,
            "partner_code": payload.get("partner_code", "AT_PARTNER_FALLBACK"),
            "partner_type": "vend" if key == "vend_info" else "cust",
        }
