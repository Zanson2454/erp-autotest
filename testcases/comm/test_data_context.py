from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional


@dataclass
class TestDataContext:
    """测试数据上下文，承接缓存路径解析与批量绑定能力。

    扩展方式（不改基类）：
        # 在模块 __init__.py 或 conftest.py 的顶层调用：
        TestDataContext.register_source("pur_cache_data", "pur_cache_data")
        TestDataContext.register_source("inv_cache_data", "inv_cache_data")

    路径格式示例：
        "currency_info.curr_id"          → init_data["currency_info"][0]["curr_id"]
        "partner_info.cust_info.id"      → md_cache_data["partner_info"]["cust_info"][0]["id"]
        "pur_cache_data.pur_org_info.id" → pur_cache_data["pur_org_info"][0]["id"]
    """

    # ------------------------------------------------------------------ #
    # 类级注册表：top-level key → 数据源属性名
    # 新增数据源调用 TestDataContext.register_source(key, attr) 即可，无需改基类
    # ------------------------------------------------------------------ #
    _SOURCE_REGISTRY: ClassVar[Dict[str, str]] = {
        # init_data 数据源
        "currency_info":    "init_data",
        "country_info":     "init_data",
        "addr_info":        "init_data",
        "bank_info":        "init_data",
        "gen_wc_head_info": "init_data",
        "calender_info":    "init_data",
        # md_cache_data 数据源
        "partner_info":     "md_cache_data",
        "org_info":         "md_cache_data",
        "mat_info":         "md_cache_data",
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
            top_level_key: 路径第一段，如 "pur_cache_data"
            source_attr:   测试类上的属性名，如 "pur_cache_data"
        """
        cls._SOURCE_REGISTRY[top_level_key] = source_attr

    @classmethod
    def from_class(cls, owner_cls: Any) -> "TestDataContext":
        """从测试类收集所有已注册数据源，构建上下文实例。"""
        source_attrs = set(cls._SOURCE_REGISTRY.values())
        sources = {attr: getattr(owner_cls, attr, None) for attr in source_attrs}
        return cls(_sources=sources)

    def resolve_cache_path(self, path: str, logger: Any = None) -> Any:
        """解析点分路径，自动路由到对应数据源。

        路径首段必须在 _SOURCE_REGISTRY 中注册，否则返回 None 并 warning。
        """
        if not path:
            return None

        parts = path.split(".")
        source_attr = self._SOURCE_REGISTRY.get(parts[0])

        if source_attr is None:
            if logger:
                logger.warning(
                    f"未知数据源: '{parts[0]}'，"
                    f"已注册的 key: {sorted(self._SOURCE_REGISTRY.keys())}，"
                    f"可调用 TestDataContext.register_source(key, attr) 扩展"
                )
            return None

        data = self._sources.get(source_attr)
        if data is None:
            if logger:
                logger.warning(f"{source_attr} 未初始化，跳过绑定: {path}")
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
            if logger:
                logger.warning(f"解析缓存路径失败: {path}, 错误: {exc}")
            return None
