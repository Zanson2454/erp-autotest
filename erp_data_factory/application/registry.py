"""场景注册中心与能力元数据管理。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Capability:
    """场景能力描述对象（用于能力列表接口返回）。"""

    scenario_key: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    supports_async: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_key": self.scenario_key,
            "description": self.description,
            "tags": self.tags,
            "supports_async": self.supports_async,
        }


class ScenarioRegistry:
    """内存级场景注册表。

    维护：
    - ``scenario_key -> scenario_handler`` 映射
    - ``scenario_key -> capability`` 元数据
    """

    def __init__(self):
        self._scenarios: Dict[str, Any] = {}
        self._capabilities: Dict[str, Capability] = {}

    def register(
        self,
        scenario_key: str,
        scenario_handler: Any,
        description: str = "",
        tags: Optional[List[str]] = None,
        supports_async: bool = True,
    ) -> None:
        """注册场景处理器及其能力元数据。"""
        self._scenarios[scenario_key] = scenario_handler
        self._capabilities[scenario_key] = Capability(
            scenario_key=scenario_key,
            description=description,
            tags=tags or [],
            supports_async=supports_async,
        )

    def get(self, scenario_key: str) -> Optional[Any]:
        """按 ``scenario_key`` 获取场景处理器。"""
        return self._scenarios.get(scenario_key)

    def keys(self):
        """返回当前已注册的全部场景键。"""
        return list(self._scenarios.keys())

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """按 ``scenario_key`` 排序返回能力列表。"""
        return [self._capabilities[key].to_dict() for key in sorted(self._capabilities.keys())]
