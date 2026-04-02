"""组织主数据场景实现。"""

from typing import Any, Dict

from erp_data_factory.compat.base import DataFactory
from erp_data_factory.domain.scenarios.base import BaseMasterScenario


class OrgScenario(BaseMasterScenario):
    """通过 API 或缓存构建/解析组织数据。"""

    api_key = "ORG-组织架构-保存服务"

    def _extract_data_from_response(
        self, response: Dict[str, Any], extracted_id: Any, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取并返回下游所需的最小组织标识信息。"""
        return {
            "id": extracted_id,
            "org_code": payload.get("orgCode") or payload.get("org_code"),
        }

    def _run_by_cache(self, payload: Dict[str, Any], context=None) -> Dict[str, Any]:
        """从主数据缓存加载组织；失败时返回稳定兜底占位值。"""
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
            return {
                "id": 0,
                "org_code": payload.get("org_code", "AT_ORG_FALLBACK"),
            }
        org_type = str(payload.get("org_type", "pur")).lower()
        candidate_keys = {
            "pur": "pur_org_info",
            "com": "gr_come_org_info",
            "inv": "inv_org_info",
            "sls": "sls_org_info",
        }
        key = candidate_keys.get(org_type, "pur_org_info")
        org_list = ((md_cache or {}).get("org_info") or {}).get(key) or []
        if org_list:
            row = org_list[0]
            return {
                "id": row.get("id"),
                "org_code": row.get("org_code"),
            }
        return {
            "id": 0,
            "org_code": payload.get("org_code", "AT_ORG_FALLBACK"),
        }
