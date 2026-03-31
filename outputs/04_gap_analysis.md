# Issues List（2026-03-31 架构复审）

## P0

### 1. ApiCallService 仍持有 test_obj（进行中，store_id_as 命名已修复）
- **状态**：进行中，`store_id_as` 命名 bug 已修复（现同时写 `cls.{name}Id` 和 `cls.{name}_id`，覆盖两套命名约定）
- **证据**：`ApiCallService.execute(test_obj, ...)` 通过 `test_obj.http`、`test_obj.get_api_path` 等直接访问测试对象，依赖倒置不彻底。
- **影响**：无法对 `ApiCallService` 独立单测；`store_id_as` 用 `setattr(test_obj.__class__, ...)` 写类属性，并发场景（`-n auto`）存在数据竞争。
- **短期修复**：在并发场景下避免依赖 `store_id_as`，改用返回值显式赋值。
- **中期重构**：将 `ApiCallService` 改为接收 `http_client`、`apis_dict`、`api_params_dict` 参数，而非 `test_obj`；`store_id_as` 改为返回 ID 后由调用方写实例属性。

### 2. 清理模式双轨（进行中，高频模块已完成）
- **状态**：进行中
- **已迁移（注册式）**：`gen_md`、`scm_sls`、`scm_del`、`erp_fin`、`scm_pur`、`scm_inv`、`sys_common` — 7 个核心模块覆盖完整。
  - `sys_common` 注意：`org_link` 系列清理依赖运行时 `user_id`，保留在各测试类 `teardown_class` 中。
- **仍存在**：其余模块（`erp_acc`、`erp_prd`、`erp_cond` 等）的 `teardown_class` 仍分散，但为低频模块，风险较低。
- **下一步**：建立"新模块必须注册式清理"的 pre-commit 或 CI 检测规则，防止分散蔓延。

---

## P1

### 3. BaseTest 单点复杂度（进行中）
- **状态**：进行中（有改善，未关闭）
- **已改善**：`AuthContext`、`ApiClientFacade`、`ApiCallService`、`TestDataContext` 已提取，`bind_cache_data` / `module_login_*` / `load_*` 等 helper 规范化。
- **仍存在**：`base_test.py` 仍 1179 行，`BaseTest` 仍是单一入口，变更回归半径大。
- **短期修复**：禁止向 `BaseTest` 继续添加业务相关 helper，新增 helper 放到专属工具类。
- **中期重构**：继续下沉 `standard_api_call` 与 `setup_class` 流程，最终 `BaseTest` 只负责编排，不承载逻辑。

### 4. 分组策略价值依赖 CI 落地（待验证）
- **状态**：能力已就绪，CI 收益未验证
- **已完成**：`--job-group` + `serial_flow` 自动标记可用。
- **建议**：CI 拆分为两个作业：`--job-group=serial -n 1` 和 `--job-group=parallel --dist=loadfile`，运行 2 周后统计 flaky 率变化。

### 5. 权限深断言覆盖不足
- **状态**：未关闭
- **现状**：多门户 helper 已标准化，但大多数用例仅验证操作成功，未验证数据隔离效果。
- **建议**：在 `scm_sls`、`gen_md` 中补充"角色A数据对角色B不可见"的反向断言用例。

---

## P2

### 6. bind_cache_data 路径路由硬编码
- **状态**：新问题
- **现状**：`TestDataContext.resolve_cache_path` 对数据源路由硬编码了 6 个 `init_data` key 和 3 个 `md_cache_data` key，新增数据源需改基类。
- **建议**：改为配置驱动（YAML 或 dict 注册），不硬编码。

### 7. ApiClientFacade 近似匹配风险
- **状态**：新问题
- **现状**：`matched_keys` 排序取 best_key 逻辑在大型 API 字典中可能命中非预期 key，已有 warning 日志但无单测覆盖。
- **建议**：补充近似匹配的单测，并在 warning 中输出完整候选列表便于排查。

---

# Impact
- P0-1（ApiCallService 并发）：`-n auto` 并发执行下 `store_id_as` 写类属性存在竞争，可能导致偶发用例串值。
- P0-2（清理双轨）：25 个未迁移模块在并发回归中仍可能产生脏数据，影响用例稳定性。
- P1-3（BaseTest 复杂）：任何基类变更需全量回归，发布效率受限。
- 正向：`gen_md` 清理注册化后，该模块并发清理冲突理论归零；`__init_subclass__` 兜底后资源泄漏风险大幅降低。

# Short-term Fix（当前可立即执行）
1. 并发场景下禁止依赖 `store_id_as`，改为 `_, extracted_id = standard_api_call(...)` 后显式赋值。
2. 迁移 `erp_fin/conftest.py` 为注册式清理（参考 `gen_md/conftest.py` 模板）。
3. CI 拆分 serial/parallel 双作业，开始收集 flaky 数据。
4. 补充"新模块必须注册清理"的 Cursor Rule 或 pre-commit 检测脚本。

# Mid-term Refactor Plan
1. **ApiCallService 解耦**：接收 `http_client`/`apis`/`api_params` 而非 `test_obj`，`store_id_as` 移除或改为实例级。
2. **清理收敛**：按模块批次迁移（优先高频：`erp_fin` → `scm_pur` → `scm_inv`），目标 teardown_class 仅保留 `super().teardown_class()` 调用。
3. **bind_cache_data 配置化**：路径路由改为可注册字典，不再依赖硬编码 key 列表。
4. **BaseTest 降载**：`standard_api_call` 成为对 `ApiCallService` 的薄包装，BaseTest 只负责 setup 编排，不承载任何执行逻辑。

# Not Recommended Now
- 立即全量替换 `teardown_class`：存量 ~102 处，批量替换风险大，应按模块渐进迁移。
- 立即重写 `BaseTest`：拆分代价高，当前兼容性优先策略更稳；等组件层稳定后再做大重构。
