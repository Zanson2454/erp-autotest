"""物料主数据场景实现。"""

from typing import Any, Dict

from erp_data_factory.compat.base import DataFactory
from erp_data_factory.domain.scenarios.base import BaseMasterScenario


class MaterialScenario(BaseMasterScenario):
    """通过 API 或缓存构建/解析物料数据。"""

    api_key = "GEN-物料主数据-保存服务"

    def _extract_data_from_response(
        self, response: Dict[str, Any], extracted_id: Any, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取并返回下游所需的最小物料标识信息。"""
        return {
            "id": extracted_id,
            "mat_code": payload.get("matCode") or payload.get("mat_code"),
        }

    def _run_by_cache(self, payload: Dict[str, Any], context=None) -> Dict[str, Any]:
        """从主数据缓存加载物料；失败时返回稳定兜底占位值。"""
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
                "mat_code": payload.get("mat_code", "AT_MAT_FALLBACK"),
            }
        mat_pool = ((md_cache or {}).get("mat_info") or {}).get("mat_md") or {}
        if isinstance(mat_pool, dict) and mat_pool:
            first = next(iter(mat_pool.values()))
            return {
                "id": first.get("id"),
                "mat_code": first.get("mat_code"),
            }
        if isinstance(mat_pool, list) and mat_pool:
            first = mat_pool[0]
            return {
                "id": first.get("id"),
                "mat_code": first.get("mat_code"),
            }
        return {
            "id": 0,
            "mat_code": payload.get("mat_code", "AT_MAT_FALLBACK"),
        }
