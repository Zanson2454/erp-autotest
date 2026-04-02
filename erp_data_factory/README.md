# ERP Data Factory

`erp_data_factory` 是 ERP 自动化测试框架中的“数据工厂产品包”，目标是把造数能力从“零散脚本调用”升级为“可编排、可观测、可复用”的统一能力。

它同时提供三种入口：
- SDK：Python 直接调用（推荐）
- CLI：命令行执行场景（本地调试/流水线）
- FastAPI：HTTP 服务化调用（平台集成）

## 1. 设计目标

- 统一入口：通过 `scenario_key` 管理不同造数场景。
- 稳定契约：统一 `ScenarioResult` 返回结构，包含 `trace_id/audit/error`。
- 双轨兼容：
  - 新架构：`application + domain + core + interfaces`
  - 兼容迁移：`compat -> legacy`
- 降耦复用：场景逻辑下沉到 `domain/scenarios`，调用编排在 `application`。
- 失败可诊断：标准错误码 + 错误分类，便于在 CI/平台中定位问题。

## 2. 分层架构

```text
调用方（TestCase / CLI / FastAPI）
            |
            v
     ERPDataFactoryClient
            |
            v
      ScenarioRunner
            |
            v
    ScenarioRegistry -> Domain Scenario (Org/Material/Partner)
            |                     |
            |                     +-> API 模式：StandardApiCaller -> ApiCallService
            |                     |
            |                     +-> Cache/DB 模式：DataFactory.init_sql_cache (legacy)
            v
      ScenarioResult（统一返回）
```

### 分层职责

- `interfaces`：对外协议层（CLI/FastAPI）。
- `client`：统一门面（同步/异步、能力列表、任务查询）。
- `application`：场景注册、执行编排、任务调度。
- `domain`：业务场景实现（组织/物料/伙伴）。
- `core`：上下文、错误码、错误模型、结果模型。
- `compat`：兼容导入路径（薄转发）。
- `legacy`：历史数据工厂实现（SQL 缓存、业务造单能力）。

## 3. 核心执行链路

### 同步执行

1. 调用方执行 `ERPDataFactoryClient.run(scenario_key, payload)`。
2. `client` 组装 `ExecutionContext`，交给 `ScenarioRunner`。
3. `runner` 从 `ScenarioRegistry` 获取场景处理器。
4. 场景先尝试 API 造数（当 `payload` 非空且可用）。
5. API 不可用或无数据时回退缓存/SQL 初始化。
6. 返回统一 `ScenarioResult`。

### 异步执行

1. 调用 `ERPDataFactoryClient.run_async(...)`。
2. `TaskManager` 提交线程池任务并生成 `task_id`。
3. 状态机：`PENDING -> RUNNING -> SUCCESS/FAILED`。
4. 任务结果落盘：`testdata/cache/edf_tasks.json`。

## 4. 如何使用

## 4.1 Python SDK（推荐）

```python
from erp_data_factory import ERPDataFactoryClient

client = ERPDataFactoryClient(env="test", project="project1")

# 查看可用场景
caps = client.list_capabilities()

# 同步执行
res = client.run(
    scenario_key="master.org.run",
    payload={"org_code": "AT_ORG_001", "org_type": "pur"}
)
print(res.to_dict())

# 异步执行
task_id = client.run_async(
    scenario_key="master.material.run",
    payload={"mat_code": "AT_MAT_001"}
)
print(client.get_task(task_id))
```

## 4.2 Facade 快捷调用

```python
from erp_data_factory import ERPDataFactoryClient

client = ERPDataFactoryClient(env="test")
org_res = client.master.org.run({"org_code": "AT_ORG_001"})
mat_res = client.master.material.run({"mat_code": "AT_MAT_001"})
ptn_res = client.master.partner.run({"partner_code": "AT_PARTNER_001", "partner_type": "cust"})
```

## 4.3 CLI

项目根目录可直接使用：

```bash
# 查看可用场景
./edf scenario list --env test --project project1

# 同步执行
./edf scenario run master.org.run --env test --payload-json '{"org_code":"AT_ORG_001"}'

# 异步执行
./edf scenario run master.partner.run --env test --async-run --payload-json '{"partner_type":"vend"}'

# 查询异步任务
./edf task status <task_id> --env test
```

> `edf` 实际执行：`python -m erp_data_factory.cli`。

## 4.4 FastAPI

`main.py` 已注册路由 `erp_data_factory.interfaces.fastapi_router.router`。

- 能力列表：`GET /erp-data-factory/v1/capabilities`
- 同步执行：`POST /erp-data-factory/v1/scenarios/{scenario_key}:run`
- 异步执行：`POST /erp-data-factory/v1/tasks/scenarios/{scenario_key}:run`
- 任务查询：`GET /erp-data-factory/v1/tasks/{task_id}`

请求体示例：

```json
{
  "env": "test",
  "project": "project1",
  "profile": "default",
  "payload": {
    "org_code": "AT_ORG_001"
  },
  "no_api_login": false
}
```

## 5. 场景与返回约定

当前内置场景（`application/bootstrap.py`）：

- `master.org.run`：组织主数据构造
- `master.material.run`：物料主数据构造
- `master.partner.run`：伙伴主数据构造（客户/供应商）

统一返回（`ScenarioResult.to_dict()`）核心字段：

- `success`：是否成功
- `scenario_key`：场景标识
- `data`：业务结果
- `trace_id`：链路追踪 ID
- `audit`：执行上下文（`request_id/env/profile`）
- `error`：失败时的错误对象（`code/message/category/details`）

## 6. 配置与依赖

- 环境：`env` 参数或 `TEST_ENV` 环境变量。
- 项目：`project` 参数或 `TEST_PROJECT` 环境变量。
- API 模式依赖：
  - `config/env/...` 环境配置
  - `config/api/gen_md/md_api_path.yaml`
  - `config/api/gen_md/md_api_params.yaml`
- 缓存/回退模式依赖：
  - `config/erp/md_init_sql.yaml`
  - `testdata/cache/*`

`no_api_login=True` 可在离线/预热缓存场景下跳过登录，直接使用缓存回退路径。

## 7. 文件清单（每个文件作用）

以下为 `erp_data_factory` 下所有核心 `.py` 文件职责说明（`__pycache__` 省略）。

### 根目录

| 文件 | 作用 |
|---|---|
| `__init__.py` | 包主入口，导出 `ERPDataFactoryClient`。 |
| `client.py` | SDK 门面：同步/异步执行、任务查询、能力列表、`master.*` 快捷 facade。 |
| `cli.py` | Click CLI 入口：`scenario list/run`、`task status`。 |

### application（编排层）

| 文件 | 作用 |
|---|---|
| `application/__init__.py` | 包标记文件。 |
| `application/bootstrap.py` | 构建 `ScenarioRunner` 并注册内置场景与元信息。 |
| `application/registry.py` | 场景注册中心与能力清单（`Capability`）。 |
| `application/runner.py` | 执行入口：场景分发、统一成功/失败包装。 |
| `application/task_manager.py` | 异步任务管理：线程池、状态流转、结果持久化。 |
| `application/api_caller.py` | `standard_api_call` 适配器，脱离 `BaseTest` 复用 API 调用能力。 |

### core（基础模型层）

| 文件 | 作用 |
|---|---|
| `core/__init__.py` | 包标记文件。 |
| `core/context.py` | 执行上下文模型（env/project/profile/request_id）。 |
| `core/error_codes.py` | 标准错误码常量。 |
| `core/errors.py` | 业务异常模型（`ScenarioError` + `ErrorCategory`）。 |
| `core/models.py` | 结果模型（`ScenarioResult`, `ErrorInfo`）。 |

### domain（业务场景层）

| 文件 | 作用 |
|---|---|
| `domain/__init__.py` | 包标记文件。 |
| `domain/scenarios/__init__.py` | 场景导出集合。 |
| `domain/scenarios/base.py` | 场景基类：API 优先 + cache fallback 执行策略。 |
| `domain/scenarios/org.py` | 组织主数据场景实现。 |
| `domain/scenarios/material.py` | 物料主数据场景实现。 |
| `domain/scenarios/partner.py` | 伙伴主数据场景实现（客户/供应商）。 |

### interfaces（接口层）

| 文件 | 作用 |
|---|---|
| `interfaces/__init__.py` | 包标记文件。 |
| `interfaces/fastapi_router.py` | FastAPI 路由：capabilities、同步/异步 run、task 查询。 |

### compat（兼容层）

| 文件 | 作用 |
|---|---|
| `compat/__init__.py` | 聚合导出兼容类。 |
| `compat/base.py` | 导出 legacy `DataFactory` 兼容路径。 |
| `compat/pur_po_factory.py` | 导出 legacy `PurPoFactory` 兼容路径。 |
| `compat/del_po_dn_factory.py` | 导出 legacy `DelPoDnFactory` 兼容路径。 |
| `compat/fin_ap_factory.py` | 导出 legacy `FinApFactory` 兼容路径。 |
| `compat/fin_ar_factory.py` | 导出 legacy `FinArFactory` 兼容路径。 |

### legacy（迁移承接层）

| 文件 | 作用 |
|---|---|
| `legacy/__init__.py` | 导出旧能力入口（当前含 `DataFactory`, `PurPoFactory`）。 |
| `legacy/base.py` | 历史核心：环境配置加载、SQL 执行、缓存初始化、通用 DataFactory 能力。 |
| `legacy/fin_apar_base_factory.py` | 应收应付公共基类：公共对象构建、查询与基础装配。 |
| `legacy/fin_ap_factory.py` | 应付相关造单/配置查询工厂。 |
| `legacy/fin_ar_factory.py` | 应收相关造单/配置查询工厂。 |
| `legacy/pur_po_factory.py` | 采购订单造单工厂（保存/提交链路）。 |
| `legacy/del_po_dn_factory.py` | 采购交货单造单工厂（分组草稿 + 提交流程）。 |

## 8. 新增场景开发规范

1. 在 `domain/scenarios/` 新增场景类，继承 `BaseMasterScenario`。
2. 实现：
   - `api_key`
   - `_extract_data_from_response()`
   - `_run_by_cache()`
3. 在 `application/bootstrap.py` 注册 `scenario_key`、`description`、`tags`。
4. 通过 SDK/CLI/FastAPI 验证同步与异步路径。
5. 为异常返回补齐标准错误码与 `ScenarioError`。

## 9. 迁移建议

- 新代码优先使用：`ERPDataFactoryClient`（SDK）或 `/erp-data-factory/v1/*`（API）。
- 历史调用保持：`erp_data_factory.compat.*`，不要直接依赖 `legacy/*` 内部细节。
- 若需要重构 legacy：优先“按场景”下沉到 `domain + application`，确保兼容路径不破坏。

## 10. 常见问题

### Q1: 场景执行失败但没有抛异常？

`ScenarioRunner` 会把异常封装进 `ScenarioResult.error`，请优先判断 `success` 并查看 `error.code/error.message`。

### Q2: 为什么返回了 fallback 的 `id=0`？

通常表示 API 不可用且缓存中未命中有效数据，场景走了兜底逻辑。请检查：环境配置、数据库连通性、缓存内容。

### Q3: 如何跳过登录仅用缓存？

创建客户端时设置 `no_api_login=True`，或接口请求体带 `no_api_login=true`。

