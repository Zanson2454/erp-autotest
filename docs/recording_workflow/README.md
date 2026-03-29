# ERP 手工探索录制转 pytest 用例工作流

## 目的

这份文档用于暂存当前已经落地的“手工探索 -> mitmproxy 录制 -> 清洗去重 -> pytest 回放 -> 沉淀正式用例”方案，后续还会继续迭代。

当前目标分成两类：

1. 手工探索后快速生成可执行的 pytest 基线，用于 first run 和链路确认。
2. 从录制结果里挑出稳定、有业务价值的场景，沉淀到正式业务用例，提升覆盖率。

## 当前目录设计

### 录制与清洗脚本

- `utils/recorder.py`
  - mitmproxy 插件
  - 负责拦截流量、白名单过滤、生成缓冲区用例、拆分大报文到 JSON
- `config/recorder_config.json`
  - 录制白名单配置
  - 当前可配置 `allowed_hosts`、`allowed_path_prefixes`、`blocked_hosts`、`blocked_path_prefixes`
- `script/start_recorder.py`
  - 使用独立环境 `.venv_mitmproxy` 启动录制器
- `script/clean_recorded_cases.py`
  - 清洗缓冲区用例
  - 负责过滤、去重、剔除缺失 payload 的脏 block
- `script/clean_recorded_payloads.py`
  - 扫描 `testdata/recorded/` 下孤儿 JSON
  - 默认只扫描，显式 `--delete` 才删除

### 用例落点

- `testcases/generated_cases/test_manual_flow.py`
  - 录制缓冲区
  - 先生成到这里，作为 first run 缓冲
- `testcases/recorded_flow/`
  - `service/engine` 类型的录制回放
  - 适合保留“接口级回放基线”
- `testcases/runtime_scene/`
  - `/api/trantor/runtime/scene/data-manager/...` 前缀的页面 scene 回放
  - 单独放，不和正式业务用例混放
- `testcases/<业务模块>/...`
  - 正式业务用例目录
  - 这里只放可维护的正式场景，不直接依赖录制 JSON

### 数据文件

- `testdata/recorded/`
  - 超过 200 字符的 request body 自动拆到这里
  - 这些 JSON 属于“录制资产”，默认不应被清洗脚本自动删除

## 当前规则

### 1. 继承基类选择

录制器会根据 URL path 自动选基类：

- path 包含 `gen_md` -> `testcases.gen_md.GenMdBaseTest`
- path 包含 `erp_fin` -> `testcases.erp_fin.FinBaseTest`
- 其他 -> `testcases.comm.base_test.BaseTest`

### 2. 标准调用方式

生成和沉淀后的用例都要求继续走：

```python
self.standard_api_call()
```

不改已有登录、Session、基类封装。

### 3. 请求数据处理

- 自动合并 query 参数和 body 数据
- body 超过 200 字符时拆分到 `testdata/recorded/*.json`
- 缓冲区代码会自动生成 `json.load(...)`
- UTF-8 编码统一处理

### 4. 去重和过滤

- 录制时会按请求指纹做一次去重
- 清洗脚本会继续按规则清洗缓冲区
- 白名单优先过滤域名和路径
- 清洗脚本已支持剔除“引用 JSON 文件不存在”的无效 block

## 启动方式

### 录制器

独立录制环境已经隔离到 `.venv_mitmproxy`，避免污染主测试环境。

启动命令：

```bash
python script/start_recorder.py
```

默认监听：

```text
127.0.0.1:8081
```

浏览器代理指向该地址即可。

### HTTPS 证书

首次抓 HTTPS 流量需要在已代理的浏览器里访问：

```text
http://mitm.it
```

安装并信任 mitmproxy 证书，否则无法解密 HTTPS 请求。

## 完整流程

### 第 1 步：启动录制器

```bash
python script/start_recorder.py
```

### 第 2 步：浏览器手工探索

- 浏览器代理到 `127.0.0.1:8081`
- 访问目标环境
- 正常点击页面，触发目标链路

### 第 3 步：生成缓冲区

录制结果自动落到：

- `testcases/generated_cases/test_manual_flow.py`
- `testdata/recorded/`

### 第 4 步：清洗缓冲区

```bash
python script/clean_recorded_cases.py
```

这一步不是执行 pytest，而是文件级清洗。

### 第 5 步：first run 回放

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/generated_cases/test_manual_flow.py
```

如果只想调部分录制结果：

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/generated_cases/test_manual_flow.py -k gen_md
```

说明：

- `-p no:rerunfailures` 是为了绕开当前环境里的 `pytest-rerunfailures` 启动问题
- 当前项目执行 pytest 时是“在线回放真实 HTTP 请求”，不是离线重放抓包文件

### 第 6 步：分流沉淀

录制结果不要直接长期留在 `generated_cases`。

应该分成三类：

1. `runtime_scene` 页面链路回放
   - `/api/trantor/runtime/scene/data-manager/...`
   - 单独放到 `testcases/runtime_scene/`
2. `recorded_flow` 接口回放
   - `service/engine` 类接口
   - 放到 `testcases/recorded_flow/`
3. 正式业务用例
   - 只吸收真正有覆盖价值、可稳定维护的场景
   - 放到正式业务模块目录

## 当前 gen_md/partner 落地结果

### 正式业务用例

- 文件：
  - `testcases/gen_md/partner/test_business_partner_management.py`
- 已新增并验证通过的正式场景：
  - 查询当前用户组织上下文
  - 页面场景分页查询
  - 页面场景详情查询
  - 页面场景地址树辅助查询
  - 页面场景用户分页辅助查询
  - 页面场景编辑保存并回查

这些场景的特点：

- 继续走 `self.standard_api_call()`
- 不依赖 `testdata/recorded/*.json`
- 用代码动态构造请求
- 目的是把手工探索沉淀成正式覆盖，而不是保留“纯录制脚本”

### service/engine 回放目录

- 文件：
  - `testcases/recorded_flow/gen_md/partner/test_business_partner_recorded_flow.py`
- 用途：
  - 保留接口级回放基线
  - 辅助定位“录制报文是否仍然可回放”

### runtime scene 回放目录

- 文件：
  - `testcases/runtime_scene/gen_md/partner/test_business_partner_runtime_scene_flow.py`
- 用途：
  - 专门承载 `/api/trantor/runtime/scene/data-manager/...` 页面链路回放
  - 不与正式业务用例混放

## 已验证命令

### 正式业务场景

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/gen_md/partner/test_business_partner_management.py -k "query_user_company_context or scene_query_business_partner_page_by_code or scene_query_business_partner_detail or scene_query_partner_address_tree or scene_query_partner_user_page or scene_save_business_partner_from_detail"
```

结果：

```text
6 passed
```

### runtime scene 回放

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/runtime_scene/gen_md/partner/test_business_partner_runtime_scene_flow.py
```

结果：

```text
6 passed
```

### service/engine 回放

```bash
./.venv/bin/pytest -q -s -n 0 -p no:rerunfailures testcases/recorded_flow/gen_md/partner/test_business_partner_recorded_flow.py
```

结果：

```text
6 passed
```

## 当前注意事项

### 1. pytest 执行时会访问真实环境

录制只是保存参数。

执行 pytest 时仍然会：

- 登录
- 建立 Session
- 调用真实接口

所以会受以下因素影响：

- 登录态
- 环境可访问性
- 数据库缓存初始化
- HTTPS 证书校验配置

### 2. 当前测试环境关闭了 HTTPS 严格校验

当前为了让 Python `requests` 在测试环境里可回放，已允许测试链路关闭严格证书校验。

这不是浏览器认证问题，而是 Python HTTPS 请求链的校验问题。

### 3. `testdata/recorded/` 默认不要自动清空

原因：

- 一旦正式回放文件引用了某个 JSON，它就已经变成测试资产
- 自动清空会把回放文件变成坏用例

建议流程：

```bash
./.venv/bin/python script/clean_recorded_payloads.py
./.venv/bin/python script/clean_recorded_payloads.py --delete
```

先扫描，再决定是否删孤儿文件。

### 4. 不是所有录制结果都应该沉淀成正式用例

适合沉淀的通常是：

- 业务价值明确
- 可以参数动态化
- 可以链路关联
- 对环境变化不太敏感

不适合直接沉淀的通常是：

- 页面权限元数据
- 纯 view 配置拉取
- 强依赖前端结构 key 的配置接口
- 纯回放价值大于业务断言价值的链路

## 正式沉淀建议

从录制结果搬到正式业务模块时，建议至少做这几步：

1. 把固定编码、时间戳、手机号、企业名等改为 `mock_util` 动态生成
2. 把前一步返回的 `id/code` 提取出来，串联给下一接口
3. 用正式业务断言替换“只看 success=True”
4. 如果已有语义化 `api_key`，优先回归到语义化配置，而不是长期用原始 path
5. 清理或隔离测试数据，避免正式用例互相污染

## 下一步可继续优化的点

### 录制器层面

- 增加更细粒度的模块白名单
- 支持根据 path 规则自动路由到 `runtime_scene` / `recorded_flow` / `generated_cases`
- 支持录制结束后自动触发清洗

### 清洗层面

- 增加按模块名、serviceKey、sceneKey 清洗
- 增加“只保留业务主链路”的模式
- 增加自动生成清洗报告

### 正式沉淀层面

- 自动识别“可提升为正式场景”的录制片段
- 辅助生成动态化模板
- 自动提示可做链路关联的字段

## 当前推荐实践

建议把这条链路长期分成三层来维护：

1. `generated_cases`
   - 临时缓冲区
2. `recorded_flow` / `runtime_scene`
   - 可回放的探索资产
3. 正式业务模块
   - 可维护的长期回归资产

这样不会把“探索回放”和“正式业务覆盖”混在一起，后续迭代也更清晰。
