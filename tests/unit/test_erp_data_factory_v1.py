# ruff: noqa: E402

import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from erp_data_factory.application.registry import ScenarioRegistry
from erp_data_factory.application.runner import ScenarioRunner
from erp_data_factory.client import ERPDataFactoryClient
from erp_data_factory.core.context import ExecutionContext
from erp_data_factory.core.errors import ErrorCategory
from erp_data_factory.domain.scenarios.org import OrgScenario


def test_runner_returns_param_error_for_unknown_scenario_key():
    runner = ScenarioRunner(ScenarioRegistry())
    result = runner.run("unknown", {}, context=ExecutionContext(env="test"))

    assert result.success is False
    assert result.error is not None
    assert result.error.category == ErrorCategory.PARAM_ERROR.value
    assert result.scenario_key == "unknown"


def test_org_scenario_supports_cache_fallback_without_api_call():
    scenario = OrgScenario(
        api_caller=None,
        cache_loader=lambda _payload: {"id": 1001, "org_code": "AT_ORG_001"},
    )

    result = scenario.run({"org_type": "pur"})

    assert result["id"] == 1001
    assert result["org_code"] == "AT_ORG_001"


def test_client_run_returns_success_result_with_trace_id():
    registry = ScenarioRegistry()
    registry.register(
        "master.org.run", OrgScenario(api_caller=None, cache_loader=lambda _p: {"id": 1, "org_code": "AT"})
    )
    client = ERPDataFactoryClient(env="test", registry=registry)

    result = client.run("master.org.run", {"org_type": "pur"})

    assert result.success is True
    assert result.trace_id
    assert result.scenario_key == "master.org.run"


def test_cli_command_outputs_json_response():
    from click.testing import CliRunner

    from erp_data_factory.cli import cli

    runner = CliRunner()
    completed = runner.invoke(
        cli,
        [
            "scenario",
            "run",
            "master.org.run",
            "--payload-json",
            json.dumps({"org_type": "pur"}),
            "--no-api-login",
        ],
    )

    assert completed.exit_code == 0
    lines = [line for line in completed.output.splitlines() if line.strip()]
    data = json.loads(lines[-1])
    assert data["scenario_key"] == "master.org.run"
    assert "trace_id" in data


def test_client_list_capabilities_returns_registered_scenarios():
    registry = ScenarioRegistry()
    registry.register(
        "master.org.run",
        OrgScenario(api_caller=None, cache_loader=lambda _p: {"id": 1, "org_code": "AT"}),
        description="组织主数据构造",
        tags=["master", "org"],
        supports_async=True,
    )
    client = ERPDataFactoryClient(env="test", registry=registry)

    capabilities = client.list_capabilities()
    assert len(capabilities) == 1
    assert capabilities[0]["scenario_key"] == "master.org.run"
    assert capabilities[0]["supports_async"] is True


def test_client_run_async_submits_and_completes_task():
    registry = ScenarioRegistry()
    registry.register(
        "master.org.run",
        OrgScenario(api_caller=None, cache_loader=lambda _p: {"id": 1, "org_code": "AT"}),
    )
    client = ERPDataFactoryClient(env="test", registry=registry)

    task_id = client.run_async("master.org.run", {"org_type": "pur"})
    assert task_id

    final_status = None
    for _ in range(20):
        task = client.get_task(task_id)
        final_status = task["status"]
        if final_status in {"SUCCESS", "FAILED"}:
            break
        time.sleep(0.05)

    assert final_status == "SUCCESS"
