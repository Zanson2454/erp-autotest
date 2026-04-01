from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional


@dataclass
class TestDataContext:
    """测试数据上下文，承接缓存路径解析与批量绑定能力。

    路径首段（如 ``currency_info``、``pur_config``）必须在 ``_SOURCE_REGISTRY`` 中有映射，
    指向测试类上的数据源属性（``init_data`` / ``md_cache_data`` / ``pur_cache_data`` 等）。

    扩展方式（不改基类）::

        TestDataContext.register_source("pur_config", "pur_cache_data")
    """

    # ------------------------------------------------------------------ #
    # 类级注册表：路径第一段 key → 测试类上的数据源属性名
    # ------------------------------------------------------------------ #
    _SOURCE_REGISTRY: ClassVar[Dict[str, str]] = {
        # init_data（base_init_sql → get_base_data）
        "currency_info": "init_data",
        "country_info": "init_data",
        "addr_info": "init_data",
        "bank_info": "init_data",
        "gen_wc_head_info": "init_data",
        "timezone_info": "init_data",
        "tax_info": "init_data",
        "uom_info": "init_data",
        "exchange_rate_type_info": "init_data",
        # md_cache_data（md_init_sql）
        "partner_info": "md_cache_data",
        "org_info": "md_cache_data",
        "mat_info": "md_cache_data",
        "index_info": "md_cache_data",
        "dynamic_form_info": "md_cache_data",
        # pur / sls / fin 模块 SQL 根 key（与 config/erp/*_init_sql.yaml 一致）
        "pur_config": "pur_cache_data",
        "sls_config": "sls_cache_data",
        # scm_del：根 key 为 del_config（del_init_sql.yaml，避免与 pur_config 混淆）
        "del_config": "del_cache_data",
        # 财务 SQL 根 key（fin_init_sql.yaml 顶层分段，如 calender_info）
        "calender_info": "fin_cache_data",
        "sett_doc_info": "fin_cache_data",
        "sett_item_info": "fin_cache_data",
        "sb_type_info": "fin_cache_data",
        "ar_type_info": "fin_cache_data",
        "ap_type_info": "fin_cache_data",
    }

    # 运行时数据源字典：attr_name → data（由 from_class 填充）
    _sources: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # 便捷属性（向下兼容）
    # ------------------------------------------------------------------ #
    @property
    def init_data(self) -> Optional[Dict[str, Any]]:
        return self._sources.get("init_data")

    @property
    def md_cache_data(self) -> Optional[Dict[str, Any]]:
        return self._sources.get("md_cache_data")

    # ------------------------------------------------------------------ #
    # 公开 API
    # ------------------------------------------------------------------ #
    @classmethod
    def register_source(cls, top_level_key: str, source_attr: str) -> None:
        """将一个 top-level key 注册到对应数据源属性名。

        Args:
            top_level_key: 路径第一段，如 ``pur_config``
            source_attr:   测试类上的属性名，如 ``pur_cache_data``
        """
        cls._SOURCE_REGISTRY[top_level_key] = source_attr

    @classmethod
    def from_class(cls, owner_cls: Any) -> "TestDataContext":
        """从测试类收集所有已注册数据源，构建上下文实例。"""
        source_attrs = set(cls._SOURCE_REGISTRY.values())
        sources = {attr: getattr(owner_cls, attr, None) for attr in source_attrs}
        return cls(_sources=sources)

    def resolve_cache_path(self, path: str, logger: Any = None, *, strict: bool = False) -> Any:
        """解析点分路径，自动路由到对应数据源。

        路径首段必须在 _SOURCE_REGISTRY 中注册；未注册时，``strict=True`` 抛错，否则返回 None 并 warning。

        ``strict=True`` 时，数据源未初始化（None）也会抛错，避免静默 None 流入用例。
        """
        if not path:
            return None

        parts = path.split(".")
        top = parts[0]
        source_attr = self._SOURCE_REGISTRY.get(top)

        if source_attr is None:
            msg = (
                f"未知数据源: '{top}'，"
                f"已注册的 key: {sorted(self._SOURCE_REGISTRY.keys())}，"
                f"可调用 TestDataContext.register_source(key, attr) 扩展"
            )
            if strict:
                raise ValueError(msg)
            if logger:
                logger.warning(msg)
            return None

        data = self._sources.get(source_attr)
        if data is None:
            msg = f"{source_attr} 未初始化，无法解析路径: {path}"
            if strict:
                raise RuntimeError(msg)
            if logger:
                logger.warning(f"{msg}，跳过绑定")
            return None

        try:
            for part in parts:
                if isinstance(data, dict):
                    data = data.get(part, {})
                elif isinstance(data, list):
                    if data:
                        data = data[0].get(part, {}) if isinstance(data[0], dict) else {}
                    else:
                        return None
                else:
                    return None

                if isinstance(data, list):
                    data = data[0] if data else None

            return data
        except Exception as exc:  # pragma: no cover
            msg = f"解析缓存路径失败: {path}, 错误: {exc}"
            if strict:
                raise RuntimeError(msg) from exc
            if logger:
                logger.warning(msg)
            return None
