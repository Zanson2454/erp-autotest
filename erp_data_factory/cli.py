"""ERP 数据工厂命令行入口。

作用：
1. 列出可用场景能力。
2. 执行单个场景（同步/异步）。
3. 查询异步任务状态。
"""

import json
import os

import click

from erp_data_factory.client import ERPDataFactoryClient


@click.group()
def cli():
    """CLI 根命令组。"""


@cli.group()
def scenario():
    """场景相关命令组。"""


@scenario.command("list")
@click.option("--env", default=lambda: os.getenv("TEST_ENV", "test"), show_default=True)
@click.option("--project", default=lambda: os.getenv("TEST_PROJECT"), show_default=True)
@click.option("--profile", default="default", show_default=True)
def list_scenarios(env, project, profile):
    """列出当前注册的场景能力清单。"""
    client = ERPDataFactoryClient(env=env, project=project, profile=profile, no_api_login=True)
    click.echo(json.dumps(client.list_capabilities(), ensure_ascii=False))


@scenario.command("run")
@click.argument("scenario_key")
@click.option("--env", default=lambda: os.getenv("TEST_ENV", "test"), show_default=True)
@click.option("--project", default=lambda: os.getenv("TEST_PROJECT"), show_default=True)
@click.option("--profile", default="default", show_default=True)
@click.option("--payload-file", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--payload-json", default=None)
@click.option("--no-api-login", is_flag=True, default=False, help="Skip login and use cache fallback")
@click.option("--async-run", is_flag=True, default=False, help="Run scenario in async in-process task manager")
def run_scenario(scenario_key, env, project, profile, payload_file, payload_json, no_api_login, async_run):
    """执行指定场景。

    参数说明：
    - scenario_key: 场景标识，例如 ``master.org.run``。
    - payload_file/payload_json: 场景入参，二选一。
    - async_run: 是否异步执行；异步时返回 ``task_id``。
    """
    payload = {}
    if payload_file:
        with open(payload_file, encoding="utf-8") as f:
            payload = json.load(f)
    elif payload_json:
        payload = json.loads(payload_json)

    client = ERPDataFactoryClient(
        env=env,
        project=project,
        profile=profile,
        no_api_login=no_api_login,
    )
    if async_run:
        task_id = client.run_async(scenario_key=scenario_key, payload=payload, profile=profile)
        click.echo(json.dumps({"task_id": task_id, "status": "PENDING"}, ensure_ascii=False))
        return

    result = client.run(scenario_key=scenario_key, payload=payload, profile=profile)
    click.echo(json.dumps(result.to_dict(), ensure_ascii=False))


@cli.group()
def task():
    """异步任务相关命令组。"""


@task.command("status")
@click.argument("task_id")
@click.option("--env", default=lambda: os.getenv("TEST_ENV", "test"), show_default=True)
@click.option("--project", default=lambda: os.getenv("TEST_PROJECT"), show_default=True)
@click.option("--profile", default="default", show_default=True)
def task_status(task_id, env, project, profile):
    """按 ``task_id`` 查询异步任务状态和结果快照。"""
    client = ERPDataFactoryClient(env=env, project=project, profile=profile, no_api_login=True)
    task = client.get_task(task_id)
    if not task:
        click.echo(json.dumps({"error": "TASK_NOT_FOUND", "task_id": task_id}, ensure_ascii=False))
        raise SystemExit(1)
    click.echo(json.dumps(task, ensure_ascii=False))


if __name__ == "__main__":
    cli()
