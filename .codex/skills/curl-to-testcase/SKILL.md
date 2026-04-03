---
name: curl-to-testcase
description: 将 `api_record/raw_curls/recorded_flow_*.md` 转为项目标准 pytest 用例。适用于“录制 -> 转用例”高频流程，保证生成风格一致并可复用给新人。
---

# cURL To Testcase

## Overview

把录制得到的 cURL Markdown（例如 `recorded_flow_001.md`）稳定转化为符合项目规范的测试代码：

- 强制遵循 `testcase_temp.mdc`、`coding_standards.mdc`、数据库规范。
- 默认使用 `standard_api_call` + `case_decorator`。
- 自动补齐顺序、断言、异常处理、清理策略。
- 对“已存在”类错误补幂等分支，避免重复运行失败。

## Inputs

- 录制文件：`api_record/raw_curls/recorded_flow_*.md`
- 目标模块（必填）：如 `gen_md`, `fin`, `sls`
- 目标文件名（建议）：`testcases/<module>/test_<topic>_flow.py`
- API 参数定义：`testdata/<module>/<module>_api_params.yaml`
- 提示词基线：`.cursor/rules/curl_to_testcase_prompt.md`

## Workflow

1. **分组 cURL**
   - 每 10-20 条为一个业务组（创建/查询/更新/导出等）。
   - 同组内按实际业务时序保留顺序。

2. **查重与落位（先查再写）**
   - 先扫描 `testcases/<module>/` 下现有文件与方法，按 `api_key`、语义关键词（save/query/update/delete/export/import）和对象名匹配。
   - 若存在同语义测试文件：优先写入原文件，并补充/更新对应 `test_*.py` 方法。
   - 若方法已存在：禁止重复生成同名方法；应更新方法体或新增差异化场景方法名（如 `_invalid_*`, `_boundary_*`）。
   - 若不存在匹配文件：按接口语义新建文件，命名为 `test_<domain>_<object>_management.py` 或 `test_<object>_flow.py`。
   - 新建文件时需先确认基类（`BaseTest/GenMdBaseTest/FinBaseTest/SlsBaseTest` 等）与模块目录一致。

3. **识别接口与参数**
   - 从 URL/path/body 提取业务字段。
   - 移除平台噪音字段（`sceneKey`、`serviceKey`、`requestId`、`created*` 等）。
   - 对对象参数做 ID 化（如 `{"id": xxx}`），禁止照搬冗余嵌套对象。
   - 严格按 YAML 参数骨架传参：先查 `*_api_params.yaml` 再确定 `param_path`，禁止默认都走 `["params", "request"]`。
   - 对 `paginate_*` 类接口，优先核对 `pageable` 在 `params` 还是 `params.request`（以 YAML 为准）。
   - **强制校验 modelKey 一致性**：若 URL/query 中携带 `modelKey`，则请求体必须显式带 `params.modelKey` 且值完全一致（避免 `V0800`）。
   - 对 `SYS_*` 通用服务（如 `SYS_SaveDataService` / `SYS_PagingDataService` / `SYS_FindDataByIdService`），优先检查 YAML 是否为 `params.request + params.modelKey` 结构；此类场景通常应使用 `use_param_util=False` + `param_path=["params"]`。

4. **映射为标准调用**
   - 95% 场景使用 `self.standard_api_call(api_key=..., set_dict=...)`。
   - 需要复杂参数时才用 `use_param_util=False`。
   - 不允许在测试方法中调用其他测试方法，抽私有 helper。

5. **补齐用例结构**
   - 测试类必须包含 `setup_class` 与 `teardown_class`，并与模块基类约定一致。
   - 优先在 `setup_class` 使用 `bind_cache_data` 绑定常用基础数据，避免在测试方法中重复取数。
   - `@case_decorator` + `file_level_order`（CRUD 顺序）。
   - 每个测试方法必须 `try-except` 并 `a.text(str(e), "失败原因")`。
   - 添加 3 层断言：响应成功、响应数据、业务结果（必要时 DB 校验）。
   - 使用 `assert_by_operator` 时，运算符仅可用框架支持值（如 `=`, `!=`, `in`, `not_in`, `contain`, `empty`, `not_empty`），禁止使用 `equal` 等别名。
   - 增加 ID 字段强类型校验：详情/删除等后续步骤前，必须断言 ID 为数值或可转数值；禁止把 `dict/uuid/requestId` 当业务 ID 透传。
   - 状态敏感操作（指派/转办/转单/删除等）先查状态，不满足前置条件时 `pytest.skip`，不要直接硬断言失败。

6. **幂等与清理**
   - 创建/关联接口遇到“已存在”错误码时，回查并复用已有数据。
   - `teardown_class` 逐表删除，禁止循环删表。
   - 清理断言不得依赖物理删除一定成功（兼容 `ENABLE_PHYSICAL_DELETE=false`）。

7. **落盘与自检**
   - 生成或更新 `testcases/**` 目标文件。
   - 运行最近编辑文件的 lints。
   - 输出“已确认信息 / 推断信息 / 待确认项”。

## Output Contract

每次执行后必须给出：

1. 目标文件路径列表
2. 已生成的测试类与测试方法清单
3. API key 映射表（cURL path -> api_key）
4. 待业务确认项（若存在）
5. 风险提示（如参数来源不明确、缺少 YAML 定义）

## Guardrails

- 不把录制 Header 直接带入测试代码（尤其 Cookie/Authorization）。
- 不硬编码业务主数据 ID，优先 `init_data` / `md_cache_data`。
- 强制使用 `mock_util` 生成测试数据（禁止硬编码业务编码/名称）。
- 不写 `@pytest.mark.run`，统一 `file_level_order`。
- 不跳过业务断言（`standard_api_call` 不含断言）。
- 不在清理中使用循环删表。
- 不在 `testcases/**` 里重复造轮子：已有文件优先复用，已有方法优先更新。
- 禁止用例互调（禁止 `self.test_xxx()`）；复用逻辑必须下沉为私有 helper。
- 检查 `${ENV_VAR}` 占位符是否已替换，URL 必须包含 `https://` 或 `http://`。
- 对带 `modelKey` 的接口，提交前必须检查“URL/query 的 modelKey”与“body.params.modelKey”一致，且与业务对象模型（如 `ERP_PLN$pln_process_tr`）一致。

## Quick Start

```text
@workflow curl-to-testcase
输入文件: api_record/raw_curls/recorded_flow_001.md
模块: gen_md
目标: testcases/gen_md/test_partner_flow.py
```

## Manual Trigger

```text
@workflow curl-to-testcase
```
