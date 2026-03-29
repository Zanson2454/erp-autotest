# ERP 手工探索录制工作流

这份文档收口 `mitmproxy 录制 -> 清洗 -> 回放 -> 沉淀正式用例` 这条链路的当前实现。录制相关资产统一放在 `api_record/`，不再散落到 `utils/`、`script/`、`config/`、`testdata/`、`testcases/` 多个目录里。

## 目录边界

以下内容全部属于录制链路，统一收口在 `api_record/`：

- `api_record/recorder.py`
- `api_record/recorder_config.json`
- `api_record/start_recorder.py`
- `api_record/recorder_control_server.py`（可选：本机录制开/关页）
- `api_record/api_config_path_registry.py`（path → YAML 服务名，供生成用例命名）
- `api_record/clean_recorded_payloads.py`
- `api_record/requirements-recorder.txt`（说明用：依赖见根目录 `requirements.txt`）
- `api_record/generated_cases/`
- `api_record/runtime_scene/`（手工放置的页面链路示例等，非录制器默认输出）
- `api_record/testdata/recorded/`
- `api_record/runtime/`（`recording_arm_switch` 开启时的状态文件目录，默认不提交 Git）

以下内容继续保留在原有 API 自动化结构中，不因为录制流程迁移而改目录：

- `testcases/comm/base_test.py`
- `testcases/gen_md/partner/test_business_partner_management.py`
- 其他正式业务模块目录
- `config/env/`
- 主测试环境 `.venv`

## 当前目录职责

### 录制入口

- `api_record/recorder.py`
  - mitmproxy 插件
  - 负责拦截请求、白名单过滤；**单次会话**生成 **一个** 场景类 `TestRecordedScene_<时间戳>` + 多个步骤方法（对齐 `.cursor/rules/testcase_temp.mdc` 骨架）
  - body 超过阈值时自动拆分 JSON 到 `api_record/testdata/recorded/`

- `api_record/recorder_config.json`
  - 录制白名单与输出路径配置
  - 当前支持：
    - `allowed_hosts`
    - `allowed_path_prefixes`
    - `blocked_hosts`
    - `blocked_path_prefixes`
    - `body_threshold`
    - `sanitize_recorded_payload`：是否按框架规范剔除噪声字段（默认 `false`，避免回放缺参失败）
    - `sanitize_remove_keys`：在内置剔除键之外追加键名
    - `redact_json_keys`：按字段名（大小写不敏感）将值替换为 `***REDACTED***`；不写该项则用内置常见敏感键；写 `[]` 可关闭脱敏
    - `auto_wrap_trantor_body`：对 `engine/execute` 类 POST，当 body 无 `params` 且无典型信封顶层字段时，自动包一层 `{"params":{"request":...}}`（默认 `true`）
    - `record_dedupe_mode`：`none` 全部落盘；`fingerprint` 同请求指纹只生成一步（推荐）
    - `record_dedupe_persist`：`false`（推荐）仅本次 mitmdump 进程内去重；`true` 则跨启动累积指纹索引
    - `record_order_mode`：`request`（默认）按浏览器发起顺序写步骤；`response` 按响应返回先后
    - `recorded_scene_epic` / `recorded_scene_feature` / `recorded_scene_story` / `recorded_scene_base_class`：场景类 Allure 与基类（`GenMdBaseTest` | `BaseTest` | `FinBaseTest`）
    - `resolve_api_config_names`：从 `config/api/**` 反查与正式用例一致的 `api_key` 中文名
    - `recording_arm_switch`：`true` 时仅当状态文件里 `armed: true` 才打序号并落盘；`false`（默认）表示代理跑着即按白名单录制
    - `recording_state_file`：武装状态 JSON 路径（默认 `api_record/runtime/recording_armed.json`），由 `recorder_control_server.py` 读写

- `api_record/start_recorder.py`
  - 使用**当前 Python 所在虚拟环境**（默认即主项目 `.venv`）里的 `mitmdump` 启动录制
  - 依赖与主项目一致：根目录执行 `pip install -r requirements.txt`（含 `mitmproxy`、`PyYAML`）

- `api_record/recorder_control_server.py`（可选）
  - 本机 HTTP 面板（默认 `http://127.0.0.1:18765/`）：「开始录制 / 停止录制 / 切换」
  - 与 `recording_arm_switch: true` 配合使用；API：`GET /api/status`，`POST /api/arm|disarm|toggle`（带 CORS，便于油猴脚本调用）

### 录制武装（快捷开关）

- **默认**：`recording_arm_switch: false`，只要 mitmproxy 在跑且过白名单就会写用例，**没有**单独「关录制」按钮。
- **需要开/关时再录**：在 `recorder_config.json` 中设 `recording_arm_switch: true`，另开终端运行 `python api_record/recorder_control_server.py`，浏览器打开控制台页面；**开启**后再在 ERP 里操作，**停止**后不再落盘（代理仍可照常上网）。
- **能否做在业务系统页面里**：ERP 若是远程部署，浏览器混合内容/CORS 会阻止页面直接 `fetch` 本机 `127.0.0.1`。可行做法：**固定标签并排控制台**、**书签打开控制台**、或在 **Tampermonkey** 里用 `GM_xmlhttpRequest` 请求 `http://127.0.0.1:18765/api/toggle`。若要把开关画进 ERP 菜单，需要 **改 ERP 前端或接内部网关**，本仓库不提供。
- 状态文件目录已加入 `.gitignore`（`api_record/runtime/`）。

### 清洗与整理

- 用例去重请在 `recorder_config.json` 中配置 `record_dedupe_mode`（见上），不再单独维护「清洗用例」脚本。

- `api_record/clean_recorded_payloads.py`
  - 扫描 `api_record/testdata/recorded/` 里的孤儿 JSON
  - 默认只扫描，显式 `--delete` 才删除

### 用例落点

- `api_record/generated_cases/test_manual_flow.py`
  - 录制输出缓冲区，用于 first run 回放

- `api_record/runtime_scene/`
  - 可手工放置页面链路示例用例（与 `generated_cases` 区分）

- `testcases/<业务模块>/...`
  - 正式业务用例
  - 这里只保留可维护的正式场景，不直接依赖录制 JSON

## 当前录制规则

### 基类选择

- path 包含 `gen_md` -> `testcases.gen_md.GenMdBaseTest`
- path 包含 `erp_fin` -> `testcases.erp_fin.FinBaseTest`
- 其他 -> `testcases.comm.base_test.BaseTest`

### 调用规范

生成和沉淀后的用例都继续走：

```python
self.standard_api_call()
```

不改已有登录、Session 和基类封装。

### 数据策略

- 自动合并 query 和 body 到 `set_dict`
- body 超过 200 字符时拆到 `api_record/testdata/recorded/*.json`
- 统一 UTF-8 编码
- 录制类名带时间戳，避免冲突
- 生成用例中 `API_RECORD_ROOT` 指向 `api_record/` 目录（用于 `open(testdata/recorded/...)`），勿与仓库根目录混淆

### 安全与凭证

- 录制流量可能含 Cookie、Token、个人信息；**不要**把未脱敏的 `testdata/recorded/*.json` 提交到公开仓库。
- 默认对常见敏感 JSON 键名做值脱敏（`redact_json_keys`）；仍建议在分享前人工检查。
- 需要「贴近手写用例、去掉 sceneKey 等噪声」时，再打开 `sanitize_recorded_payload`，并自行验证回放仍成功。

### 顺序与去重

- **发起顺序（默认）**：`record_order_mode` 为 `request` 时，在 `request` 钩子里为命中的 API 打全局递增序号，在 `response` 里按序号**缓冲并连续刷盘**，因此生成用例在文件中的先后 = 浏览器发起先后（后返回的请求不会插队）。
- **响应顺序（兼容）**：`record_order_mode` 为 `response` 时与旧版一致，按响应完成先后落盘。
- **未录制占位**：同一序号在 response 阶段若未通过录制过滤、或因指纹去重被丢弃，会记为「跳过」，避免阻塞后续序号的刷盘。
- **无正常 response**：例如 mitm 日志里出现 `<< Client disconnected.`、上游失败等，不会进入 `response` 钩子；录制器在 `error` 钩子中补「跳过」该序号，否则后续响应会一直积压在缓冲里，表现为**几乎只落盘最后几条或一个 JSON**。
- **JSON 数量少于接口数**：`body` 短于 `body_threshold`（默认 200 字符）时载荷**内联进 `.py`**，不一定有独立 `testdata/recorded/*.json`；需要「每步一个文件」可把阈值调小或设为 `0`（非空 body 尽量落盘，以 `recorder_config.json` 为准）。
- **指纹去重**（可选）：`record_dedupe_mode` 为 `fingerprint` 时同指纹只写一条，并维护 `.recorder_index.json`。
- **清洗**：`clean_dedupe_mode` 为 `none` 时保持文件内先后；`api_path` / `fingerprint` 可再瘦身。
- 生成类上 `RECORDED_BROWSER_SEQ` 为发起序号，`RECORDED_OUTPUT_INDEX` 为写入用例的连续序号（1..N）。

## 使用流程

### 1. 启动录制器

```bash
python api_record/start_recorder.py
```

默认监听：

```text
127.0.0.1:8081
```

### 2. 浏览器配置代理并安装证书

- 浏览器代理到 `127.0.0.1:8081`
- 首次抓 HTTPS 时，在已代理浏览器里打开 `http://mitm.it`
- 安装并信任 mitmproxy 证书

### 3. 手工探索页面

- 正常登录并点击页面
- 触发你要保留的接口链路

### 4. 录制结果落盘

录制结果会自动写到：

- `api_record/generated_cases/test_manual_flow.py`
- `api_record/testdata/recorded/`

### 5. first run 回放

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures api_record/generated_cases/test_manual_flow.py
```

按关键字调试：

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures api_record/generated_cases/test_manual_flow.py -k gen_md
```

说明：

- 当前项目执行 pytest 时是“在线回放真实 HTTP 请求”，不是离线重放抓包文件
- `-p no:rerunfailures` 用来绕开当前环境中的 `pytest-rerunfailures` 启动问题

### 6. 分流沉淀

录制结果不要长期停留在 `generated_cases/`，可按需：

1. 页面 Scene 等特殊链路：可参考 `api_record/runtime_scene/` 下示例组织代码。
2. 正式业务用例：吸收稳定场景到 `testcases/<模块>/`，并按项目规范改写 mock / 断言 / teardown。

## gen_md/partner 当前落地

### 正式业务用例

- 文件：`testcases/gen_md/partner/test_business_partner_management.py`
- 已补充并验证通过的正式场景：
  - 查询当前用户组织上下文
  - 页面场景分页查询
  - 页面场景详情查询
  - 页面场景地址树辅助查询
  - 页面场景用户分页辅助查询
  - 页面场景编辑保存并回查

这些场景的目标是把手工探索沉淀为正式覆盖，而不是保留纯录制脚本。

### runtime scene 回放

- 文件：`api_record/runtime_scene/gen_md/partner/test_business_partner_runtime_scene_flow.py`
- 用途：专门承载 `/api/trantor/runtime/scene/data-manager/...` 页面链路回放

## 已验证命令

正式业务场景：

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/gen_md/partner/test_business_partner_management.py -k "query_user_company_context or scene_query_business_partner_page_by_code or scene_query_business_partner_detail or scene_query_partner_address_tree or scene_query_partner_user_page or scene_save_business_partner_from_detail"
```

runtime scene 回放：

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures api_record/runtime_scene/gen_md/partner/test_business_partner_runtime_scene_flow.py
```

## payload 清理

默认不要自动清空 `api_record/testdata/recorded/`，因为其中一部分 JSON 已经是回放资产。

扫描孤儿 payload：

```bash
./.venv/bin/python api_record/clean_recorded_payloads.py
```

确认后删除孤儿 payload：

```bash
./.venv/bin/python api_record/clean_recorded_payloads.py --delete
```

## 注意事项

### pytest 执行时会访问真实环境

录制只是保存参数。

执行 pytest 时依然会：

- 先走 `BaseTest.setup_class()` 登录
- 再通过 `self.standard_api_call()` 用 Python `requests` 发真实 HTTP 请求

所以这条链路是“在线回放”，不是抓包文件离线回放。

### `/api/trantor/runtime/scene/data-manager` 必须单独放

这类接口属于页面 scene 链路，已经单独放到 `api_record/runtime_scene/`，不要和正式业务用例或一般 `service/engine` 回放混在一起。
