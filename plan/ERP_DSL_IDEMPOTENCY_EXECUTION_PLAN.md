# ERP 自动化测试工程提效专项执行计划（可执行版）

## 1. 文档信息
- 版本: v1.1
- 制定日期: 2026-04-03
- 执行周期: 5 周（W0-W4）
- 目标方向: 业务语义化封装（Domain DSL）+ 幂等造数与环境自愈
- 变更记录:
1. v1.1: 补充指标强制口径、W1 前置决策、迁移覆盖率目标与复评修订项。

## 2. 目标与边界
### 2.1 目标
1. 建立统一 Flow 协议，降低用例编写复杂度。
2. 建立 Ensure 幂等造数机制，降低重复造数和环境依赖。
3. 先完成高频链路试点，再按批次替换旧调用模式。

### 2.2 非目标（本周期不做）
1. 不在 W4 内一次性完成全仓 613 处改造。
2. 不在首轮直接物理删除 `erp_data_factory/legacy`，仅冻结并去新依赖。
3. 不做与 DSL/幂等无关的框架重构。

## 3. 统一度量口径（先定指标再施工）
### 3.1 指标与验收阈值
1. SLOC 收敛: 同等业务覆盖下，`testcases/` 代码行数下降 >= 40%。
2. 稳定性: 环境数据/顺序依赖/状态竞争导致的 flaky 占比 < 1%。
3. 造数效率: 同用例二次执行时 Setup 耗时下降 >= 70%。
4. 上手体验: 新人 30 分钟内基于 Flow 写出“采购到入库”链路。
5. Agent Ready: Flow 方法 Docstring 完整且可被 LLM 正确联想参数。

指标计算口径（强制）：
1. `flaky_rate = flaky_failures / total_case_executions`。
2. `total_case_executions` 为统计窗口内所有执行次数，不使用提前中断参数。
3. `setup_gain = (baseline_setup_p50 - rerun_setup_p50) / baseline_setup_p50`。

### 3.2 基线采集（D0 必做）
- 基线日: 2026-04-03
- 命令与产物:
```bash
# 0) 清空历史日志，避免追加污染
: > outputs/baseline_pytest_2026-04-03.log
: > outputs/baseline_setup_2026-04-03.log

# 1) 当前规模
cloc testcases > outputs/baseline_cloc_2026-04-03.txt

# 2) 当前稳定性（固定 20 轮，禁止 --maxfail）
for i in {1..20}; do
  pytest -m "smoke or p0" -n 4 --dist=loadscope >> outputs/baseline_pytest_2026-04-03.log
done

# 3) 当前 Setup 耗时（5 条链路 x 2 轮）
for i in {1..2}; do
  pytest testcases/scm_pur -k "core" -n 0 --durations=20 >> outputs/baseline_setup_2026-04-03.log
  pytest testcases/scm_sls -k "core" -n 0 --durations=20 >> outputs/baseline_setup_2026-04-03.log
  pytest testcases/scm_inv -k "core" -n 0 --durations=20 >> outputs/baseline_setup_2026-04-03.log
  pytest testcases/gen_md -k "core" -n 0 --durations=20 >> outputs/baseline_setup_2026-04-03.log
  pytest testcases/erp_fin -k "core" -n 0 --durations=20 >> outputs/baseline_setup_2026-04-03.log
done
```

## 4. 里程碑计划（Sprint Backlog）

## W0: 启动准备（先做后开工）
### T0.1 D0 基线采集与归档
- 交付物: `outputs/baseline_*.txt|log` + 基线记录页
- 实现要求:
1. 执行基线采集命令并保留原始输出，不手工修改结果。
2. 在文档中记录基线时间、命令、执行环境（env/project/并发参数）。
3. 若命令失败，记录失败原因与阻塞项，不允许“空基线开工”。
- DoD:
1. 2026-04-03 基线产物齐全可追溯。
2. 至少覆盖 SLOC、flaky、setup 三类基线指标。
- 人天: 0.5
- 依赖: 无
- 回滚点: 无（基线不可回滚，只能补采）

### T0.2 周度 Gate 机制落地
- 交付物: `outputs/gates/` 周度 Gate 报告（W1-W4）
- 实现要求:
1. 固化 Gate 模板：输入（测试范围/命令）+ 输出（通过/阻塞/风险）。
2. 每周结束必须出一份 Go/No-Go 结论，未通过不得进入下一周任务。
3. 每个 Gate 报告必须包含失败用例清单、责任任务 ID、下一步修复动作。
- DoD:
1. W1-W4 每周均有一份可审计的 Gate 报告文件。
2. Gate 结论与下一周开工记录一致。
- Gate 模板（固定字段）:
1. `window_start/window_end`
2. `total_case_executions/flaky_failures/flaky_rate`
3. `flaky_case_count/infra_failures`
4. `setup_p50_baseline/setup_p50_current/setup_gain`
5. `blocked_tasks/risk_items/go_no_go`
- 人天: 0.5
- 依赖: T0.1
- 回滚点: 若 Gate 机制执行不全，冻结后续周任务进入缺陷修复

## W1: 协议与基座（必须达成）
### T1.0 架构前置决策冻结（W1 Gate 前置）
- 交付物: `outputs/gates/W1_arch_decisions.md`
- 决策项:
1. Ensure 业务唯一键: 组织 `org_name + tenant_id`，物料 `material_code + tenant_id`。
2. Context 并发方案: `ContextVar + nodeid + worker_id`。
3. Flow DTO 最小字段: `id/biz_code/status/raw_status/trace_id`。
- DoD:
1. 三项决策冻结后才允许进入 T1.1 开发。
2. 决策文档被 PRD/LLD 引用并保持一致。
- 人天: 0.5
- 依赖: T0.2
- 回滚点: 决策冲突时冻结 W1，先修文档再编码

### T1.1 DSL 抽象协议制定
- 交付物: `testcases/comm/base_flow.py`
- 实现要求:
1. Flow 入参使用 Pydantic 模型。
2. Flow 返回业务对象（DTO/Domain Object），不暴露原始 Response。
3. 统一异常捕获与业务错误包装（保留原始异常上下文）。
4. 全部公共方法必须 Type Hint + 中文 Docstring（含参数、返回、异常）。
- DoD:
1. 至少 2 个示例 Flow 通过静态检查与单测。
2. 失败时 Allure 中可见业务错误与上下文。
- 人天: 2.0
- 依赖: T1.0
- 回滚点: 保留旧调用入口并由开关控制（`USE_FLOW_DSL=false`）

### T1.2 Context 管理器
- 交付物: `testcases/comm/test_context.py`
- 实现要求:
1. 支持用例级上下文（单据 ID、业务对象 ID、租户标识）。
2. 支持 xdist 并发隔离（进程维度隔离，禁止全局可变共享）。
3. 提供 `set/get/clear/snapshot` API。
- DoD:
1. `pytest -n 4` 下无跨用例污染。
2. 每条链路结束自动 clear。
- 人天: 1.5
- 依赖: T1.1
- 回滚点: Context 仅注入试点模块，旧模块不依赖

## W2: Repository + Ensure + Fixture
### T2.1 Repository 层建立（只读）
- 交付物: `repository/mdm_repo.py`
- 实现要求:
1. 在 `utils/mysql_util.py` 上封装 `get_org_by_name/get_material_by_name`。
2. 全部 SQL 参数化，禁止 f-string 拼接。
3. 返回结构化对象（id/name/code/status）。
- DoD:
1. 覆盖“存在/不存在/重复名称”查询分支。
2. SQL 语句通过参数化审查。
- 人天: 1.5
- 依赖: W1 完成
- 回滚点: 保留原查询函数只读兼容

### T2.2 Ensure 模式开发
- 交付物: `erp_data_factory/domain/scenarios/common_skill.py`
- 实现要求:
1. `ensure_org_exists`、`ensure_material_exists` 采用“先查后建”。
2. 对并发竞争引入幂等兜底（唯一键冲突后回查返回）。
3. 返回稳定 ID 与业务对象摘要。
- DoD:
1. 同参数调用 2 次不新增记录。
2. 并发调用（4 并发）不产生脏重复。
- 人天: 2.0
- 依赖: T2.1
- 回滚点: `ensure_*` 失败时降级为显式创建流程

### T2.3 Fixture 自动触发重构
- 交付物: `testcases/conftest.py`（增量）
- 实现要求:
1. 提供 `ensure_org`, `ensure_material` fixture。
2. 支持参数注入（名称、编码前缀、分类）。
3. fixture 内记录造数来源（created/reused）到 Allure。
- DoD:
1. 试点用例不再手写 SQL 初始化。
2. fixture 失败日志可定位到 ensure 步骤。
- 人天: 1.0
- 依赖: T2.2
- 回滚点: 允许保留手动初始化作为 fallback fixture

## W3: 三条高频链路试点 DSL
### T3.1 采购链路 PurFlow
- 交付物: `testcases/scm_pur/pur_flow.py`
- 范围: 创建订单 -> 提交 -> 审核（支持 patch）
- DoD:
1. 单用例调用从 10+ 行收敛为 1-3 行。
2. 支持订单行自定义并可断言关键状态。
- 人天: 2.0
- 依赖: W1+W2
- 回滚点: 保留旧测试实现，Flow 仅在 `@pytest.mark.dsl_pilot` 使用

### T3.2 销售链路 SlsFlow
- 交付物: `testcases/scm_sls/sls_flow.py`
- 范围: 销售订单 -> 出库 -> 对账
- DoD:
1. 自动处理状态机流转。
2. 失败点能定位在具体业务动作。
- 人天: 2.0
- 依赖: W1+W2
- 回滚点: 保留旧链路用例可单独运行

### T3.3 库存链路 InvFlow
- 交付物: `testcases/scm_inv/inv_flow.py`
- 范围: 即时库存查询、库位调整
- DoD:
1. 支持语义断言（示例: `assert inv.get_qty() == 10`）。
2. 与 Ensure 机制打通（依赖物料/组织自动补齐）。
- 人天: 2.0
- 依赖: W1+W2
- 回滚点: 库存相关场景保留传统 API 用例

## W4: 迁移清理与验收
### T4.1 测试互调清理（分批而非一次性）
- 交付物: 批次改造清单 + 改造提交
- 执行策略:
1. 按模块分 4 批（pur/sls/inv/gen），每批 <= 80 处。
2. 每批完成后跑对应模块回归再进入下一批。
3. 本周期目标覆盖率: 历史遗留互调点 >= 50%，剩余纳入 `W5+` Backlog。
- DoD:
1. 禁止 `self.test_xxx()` 互调新增。
2. 已改批次中无顺序依赖失败。
- 人天: 3.0
- 依赖: W3
- 回滚点: 按批次回滚，不回滚整仓

### T4.2 直接 HTTP 调用重构
- 交付物: 搜索结果清零报告 + 替换提交
- 执行策略:
1. 搜索 `self.http`、`requests.`、裸 URL 调用。
2. 迁移至 `standard_api_call` 并补充最小断言。
- DoD:
1. 全仓无新增 `self.http.post`。
2. 试点模块直接 HTTP 引用清零。
- 人天: 2.0
- 依赖: W1/W3
- 回滚点: 对遗留模块允许临时白名单，记录到技术债清单

### T4.3 Legacy 目录退役（两步走）
- 交付物: `legacy` 冻结说明 + 去依赖报告
- 执行策略:
1. 本周期: 冻结 `erp_data_factory/legacy`，禁止新引用。
2. 下周期: 连续两个迭代无引用后物理删除。
- DoD:
1. 新代码路径只走 `domain`。
2. CI 增加 legacy 引用检查。
- 人天: 1.0
- 依赖: T4.1/T4.2
- 回滚点: 删除前保留只读快照分支

## 5. 集成测试专项（架构回归）
### IT1 冷启动场景
- 目标: 新租户环境执行全量核心集，验证环境自愈。
- 命令:
```bash
python script/project_bootstrap.py
pytest -m "smoke or p0" -n 4
```

### IT2 并发场景
- 目标: 采购 + 销售混跑，验证 Context 隔离与 Ensure 幂等。
- 命令:
```bash
pytest testcases/scm_pur testcases/scm_sls -n 4 --dist=loadscope
```

### IT3 二次运行场景
- 目标: 同环境立即重跑，验证 ensure 跳过无效创建。
- 命令:
```bash
pytest testcases/scm_pur -n 0 --durations=20
pytest testcases/scm_pur -n 0 --durations=20
```

## 6. 风险清单与应对
1. 并发下重复造数: 通过唯一键 + 冲突回查 + 并发测试兜底。
2. DSL 抽象过度: 只做高频动作封装，不提前做跨域大一统 Flow。
3. 大规模替换引发回归: 分批迁移 + 每批独立回归 + 可回滚。
4. 指标失真: 固定基线数据集与命令，统一采集窗口。

## 7. 交付清单（本周期）
1. `testcases/comm/base_flow.py`
2. `testcases/comm/test_context.py`
3. `repository/mdm_repo.py`
4. `erp_data_factory/domain/scenarios/common_skill.py`（ensure 增量）
5. `testcases/conftest.py`（fixture 增量）
6. `testcases/scm_pur/pur_flow.py`
7. `testcases/scm_sls/sls_flow.py`
8. `testcases/scm_inv/inv_flow.py`
9. 指标采集与验收报告（`outputs/`）
10. `outputs/gates/W1_arch_decisions.md`

## 8. 周度验收关口（Go/No-Go）
1. W1 Gate: 协议、异常、Context 并发隔离通过。
2. W2 Gate: Ensure 幂等在单次/并发下都稳定。
3. W3 Gate: 三条 Flow 试点可替代旧调用并通过回归。
4. W4 Gate: 完成首批迁移与专项集成测试，输出量化对比报告。

## 9. 执行节奏与责任分工（可直接照此推进）
### 9.1 固定节奏
1. 周一: 确认本周任务范围与依赖，更新任务状态（Todo/Doing/Done/Blocked）。
2. 周三: 中期检查，输出风险清单与偏差修正动作。
3. 周五: 执行 Gate，形成 Go/No-Go 结论与下周准入条件。

### 9.2 周任务清单（最小执行单元）
1. W0: 完成 T0.1、T0.2。
2. W1: 完成 T1.0、T1.1、T1.2，并通过 W1 Gate。
3. W2: 完成 T2.1、T2.2、T2.3，并通过 W2 Gate。
4. W3: 完成 T3.1、T3.2、T3.3，并通过 W3 Gate。
5. W4: 完成 T4.1、T4.2、T4.3 + IT1/IT2/IT3，并通过 W4 Gate。

### 9.3 状态管理规则
1. 每个任务必须有唯一责任人和截止日期。
2. 任务状态只允许 `Todo`、`Doing`、`Done`、`Blocked` 四种。
3. `Blocked` 超过 1 天必须升级为风险项并给出替代路径。
