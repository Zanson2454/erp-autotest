"""Bootstrap default scenario registry and runner."""

from erp_data_factory.application.api_caller import StandardApiCaller
from erp_data_factory.application.registry import ScenarioRegistry
from erp_data_factory.application.runner import ScenarioRunner
from erp_data_factory.domain.scenarios.material import MaterialScenario
from erp_data_factory.domain.scenarios.org import OrgScenario
from erp_data_factory.domain.scenarios.partner import PartnerScenario


def build_runner(env: str = "test", project=None, no_api_login: bool = False) -> ScenarioRunner:
    """Create a runner with built-in master data scenarios registered."""
    registry = ScenarioRegistry()

    api_caller = None
    if not no_api_login:
        api_caller = StandardApiCaller(env=env, project=project, no_api_login=False)

    registry.register(
        "master.org.run",
        OrgScenario(api_caller=api_caller),
        description="组织主数据构造",
        tags=["master", "org"],
        supports_async=True,
    )
    registry.register(
        "master.material.run",
        MaterialScenario(api_caller=api_caller),
        description="物料主数据构造",
        tags=["master", "material"],
        supports_async=True,
    )
    registry.register(
        "master.partner.run",
        PartnerScenario(api_caller=api_caller),
        description="伙伴主数据构造（客户/供应商）",
        tags=["master", "partner"],
        supports_async=True,
    )

    return ScenarioRunner(registry)
