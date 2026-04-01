# GET_START — 新项目接入指南

> 本指南面向**在新业务模块/新 ERP 项目**中首次落地 API 自动化测试的工程师。  
> 阅读完成预计 20 分钟，跑通第一条用例约 45 分钟。

---

## 目录

1. [环境准备](#1-环境准备)
2. [项目结构说明](#2-项目结构说明)
3. [第一步：添加环境配置](#3-第一步添加环境配置)
4. [第二步：维护初始化 SQL 配置](#4-第二步维护初始化-sql-配置)
5. [第三步：添加 API 配置](#5-第三步添加-api-配置)
6. [第四步：创建模块目录与基类](#6-第四步创建模块目录与基类)
7. [第五步：注册模块清理](#7-第五步注册模块清理)
8. [第六步：编写第一条用例](#8-第六步编写第一条用例)
9. [编写用例技巧](#9-编写用例技巧)
10. [第七步：运行与查看报告](#10-第七步运行与查看报告)
11. [扩展数据源（可选）](#11-扩展数据源可选)
12. [快速检查清单](#12-快速检查清单)
13. [常见问题](#13-常见问题)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
pip install -r requirements.txt
```

### 1.2 必需工具

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Python | ≥ 3.10 | 使用了 `str \| None` 类型注解 |
| pytest | ≥ 7.0 | 测试运行器 |
| allure-pytest | ≥ 2.13 | 报告生成 |
| pytest-xdist | ≥ 3.0 | 并行执行（可选） |
| MySQL client | — | 测试数据清理 |

---

## 2. 项目结构说明

```
erp-autotest/
├── config/
│   ├── api/                      # API 路径与参数模板（按模块分目录）
│   │   └── {module}/
│   │       ├── {module}_api_path.yaml    # api_key → HTTP path + method
│   │       └── {module}_api_params.yaml  # path → 参数默认模板
│   └── env/                      # 环境配置
│       ├── test.yaml             # 默认（单项目模式）
│       └── {project}/
│           └── test.yaml         # 多项目模式
│
├── testcases/
│   ├── conftest.py               # 全局 pytest hooks（勿改）
│   ├── comm/
│   │   ├── base_test.py          # BaseTest 基类（勿改）
│   │   ├── api_call_service.py   # standard_api_call 核心逻辑（勿改）
│   │   ├── cleanup_registry.py   # 统一清理注册中心（勿改）
│   │   └── test_data_context.py  # 缓存路径解析（勿改）
│   │
│   └── {your_module}/            # ← 你只需要在这里添加文件
│       ├── __init__.py           # 模块基类
│       ├── conftest.py           # 模块清理注册
│       └── test_{feature}.py     # 用例文件
│
├── testdata/
│   └── cache/
│       └── init_cache.json       # 基础数据缓存（登录后自动生成）
│
└── utils/                        # 工具类（勿改）
```

---

## 3. 第一步：添加环境配置

### 3.1 复制并填写 `.env` 文件

项目已提供统一的变量模板 `config/env/.env_template`，复制后填入真实值即可：

```bash
cp config/env/.env_template config/env/.env
# 编辑 config/env/.env，填写真实的 URL、账号、密码
```

> `config/env/.env` 已加入 `.gitignore`，不会被提交。

模板内容说明（`config/env/.env_template`）：

```ini
# =========================
# 项目/运行环境开关
# =========================
TEST_PROJECT=''          # 多项目模式时填写，单项目留空
TEST_VERIFY_SSL=true     # HTTPS 证书校验（测试环境异常可临时设为 false）
TEST_CA_BUNDLE=''        # 自定义 CA 证书路径（可选）

# =========================
# TERP 门户认证信息（主门户）
# =========================
TEST_TERP_PORTAL_USERNAME=''
TEST_TERP_PORTAL_PASSWORD=''
TEST_TERP_PORTAL_IAM_URL='https://your-iam-domain.example.com'
TEST_TERP_PORTAL_IAM_REFERER='https://your-iam-domain.example.com/TERP_PORTAL-TERP'
TEST_TERP_PORTAL_URL='https://your-portal-domain.example.com'
TEST_TERP_PORTAL_REFERER='https://your-portal-domain.example.com/TERP_PORTAL-TERP'

# Cookie 登录（留空=账号密码登录）
TEST_TERP_PORTAL_COOKIE=''

# =========================
# 数据库配置（ERP/IAM）
# =========================
TEST_DB_HOST='127.0.0.1'
TEST_DB_PORT=3306
TEST_DB_USER=''
TEST_DB_PASSWORD=''
TEST_DB_NAME=''
TEST_IAM_DB_NAME=''
```

### 3.2 确认 YAML 配置文件

`.env` 中的变量会在运行时自动替换 `config/env/test.yaml`（或对应 env）里的 `${VAR}` 占位符。  
YAML 文件只需维护结构，敏感值统一写在 `.env` 中：

```yaml
# config/env/test.yaml 示例结构
portal_config:
  terp:
    TERP_PORTAL:
      iam_url: ${TEST_TERP_PORTAL_IAM_URL}
      iam_referer: ${TEST_TERP_PORTAL_IAM_REFERER}
      portal_url: ${TEST_TERP_PORTAL_URL}
      portal_referer: ${TEST_TERP_PORTAL_REFERER}
      username: ${TEST_TERP_PORTAL_USERNAME}
      password: ${TEST_TERP_PORTAL_PASSWORD}

database:
  erp_db:
    host: ${TEST_DB_HOST}
    port: ${TEST_DB_PORT}
    database: ${TEST_DB_NAME}
    username: ${TEST_DB_USER}
    password: ${TEST_DB_PASSWORD}

trantor_version: "2.5.x.xxxx.x-SNAPSHOT"
```

### 3.3 多项目模式

```
config/env/
└── project_alpha/
    ├── .env           # 项目特定变量（覆盖根 .env）
    ├── test.yaml
    └── staging.yaml
```

运行时指定：

```bash
pytest --project=project_alpha --env=test
```

---

## 4. 第二步：维护初始化 SQL 配置

测试框架在 `setup_class` 阶段会自动执行 `config/erp/` 下的 SQL 配置文件，
把查询结果缓存到 `testdata/cache/`，供用例通过 `cls.init_data` / `cls.md_cache_data` 等属性直接使用。

### 4.1 文件总览

| 文件 | 根 key | 对应缓存属性 | 加载时机 |
|------|--------|-------------|---------|
| `base_init_sql.yaml` | `base_info` | `cls.init_data` | 所有模块（BaseTest） |
| `md_init_sql.yaml` | `org_info` / `mat_info` / `partner_info` … | `cls.md_cache_data` | gen_md 及依赖主数据的模块 |
| `sls_init_sql.yaml` | `sls_config` | `cls.sls_cache_data` | scm_sls |
| `pur_init_sql.yaml` | `pur_config` | `cls.pur_cache_data` | scm_pur |
| `fin_init_sql.yaml` | `calender_info` / `sett_*` 等顶层分段 | `cls.fin_cache_data` | erp_fin |
| `del_init_sql.yaml` | `scm_del_config` | `cls.del_cache_data` | scm_del |
| `acc_init_sql.yaml` | *(待填充)* | `cls.acc_cache_data` | erp_acc |

> 缓存文件存放在 `testdata/cache/`（已加入 `.gitignore`）。  
> 测试环境缓存有效期 **5 分钟**，生产/预发环境 **1440 分钟**，到期自动重新查询。  
> 修改 `config/erp/*_init_sql.yaml` 后，框架会按 **SQL 文件内容 hash** 自动丢弃对应 json 缓存，一般无需手删 `testdata/cache/*.json`。

### 4.2 SQL 配置结构

每个配置项的结构固定为：

```yaml
# 根key（与缓存属性对应）
base_info:
  # 数据键（对应 cls.init_data["currency_info"]）
  currency_info:
    sql: |
      SELECT id AS curr_id, curr_code, curr_name
      FROM gen_curr_type_cf
      WHERE curr_code = 'CNY' AND deleted = 0
      LIMIT 1;
    description: "查询人民币基础信息"
    validation:
      required: true          # true = 数据缺失时报警
      min_records: 1
      required_fields: ["curr_id", "curr_code"]
```

SQL 中可使用 `${ENV_VAR:-默认值}` 语法引用 `.env` 变量，实现**不修改文件就能切换测试数据**：

```yaml
pur_org_info:
  sql: |
    SELECT id, org_code FROM org_struct_md
    WHERE org_code = '${TEST_PUR_ORG:-AUTOTEST_PUR_ORG}'
      AND deleted = 0
    LIMIT 1;
```

对应 `.env` 配置（参见 `config/env/.env_template`）：

```ini
TEST_PUR_ORG=MY_COMPANY_PUR_ORG   # 不填则使用默认值 AUTOTEST_PUR_ORG
```

### 4.3 新接入项目时的操作步骤

1. **在被测数据库中创建测试专用主数据**，编码统一使用 `AUTOTEST_` 前缀（或自定义前缀后在 `.env` 中覆盖）：
   - 组织：`AUTOTEST_PUR_ORG`、`AUTOTEST_SLS_ORG`、`AUTOTEST_INV_ORG` …
   - 供应商/客户：`AUTOTEST_VEND`、`AUTOTEST_CUST`
   - 物料：`AUTOTEST_MAT_FINP*`、`AUTOTEST_MAT_SERV*`
   - 仓位：`AUTOTEST_REC_BIN`（收货）、`AUTOTEST_SEND_BIN`（发货）

2. **在 `config/env/.env` 中配置对应变量**（若数据编码与默认值一致则可跳过）：

   ```ini
   TEST_PUR_ORG=YOUR_PUR_ORG_CODE
   TEST_SLS_ORG=YOUR_SLS_ORG_CODE
   TEST_INV_ORG=YOUR_INV_ORG_CODE
   TEST_VEND=YOUR_VEND_CODE
   TEST_CUST=YOUR_CUST_CODE
   TEST_REC_BIN=YOUR_REC_BIN_CODE
   TEST_SEND_BIN=YOUR_SEND_BIN_CODE
   ```

3. **首次运行任意用例验证**，框架会自动执行 SQL 并缓存结果。若缓存属性为 `None`，说明数据库中对应数据不存在，需检查步骤 1。

### 4.4 新增模块 SQL 配置

若新模块需要专属的初始化数据（现有文件中没有的），在 `config/erp/` 下新建文件：

```
config/erp/
└── mymod_init_sql.yaml    # 新建
```

然后在模块基类 `__init__.py` 中调用 `load_sql_cache` 加载：

```python
from pathlib import Path

class MyModBaseTest(BaseTest):

    @classmethod
    def load_cache_data(cls):
        cls.mymod_cache_data = cls.load_sql_cache(
            sql_config_path=Path(__file__).resolve().parent.parent.parent
                            / "config" / "erp" / "mymod_init_sql.yaml",
            cache_key="mymod_init_cache",
            db_config_name="erp_db",
        )

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.load_cache_data()
```

随后在用例中直接使用：

```python
cls.my_id = cls.mymod_cache_data.get("my_key", [{}])[0].get("id")
```

### 4.5 修改现有 SQL 配置时注意事项

- **必须保留 `deleted = 0` 条件**，防止查到已软删除的数据
- **修改 SQL 后清除本地缓存**，否则测试仍使用旧数据：

  ```bash
  rm testdata/cache/*.json
  ```

- **`validation.required: true` 的字段**：框架会在缓存为空时打印 WARNING，建议接入时仔细核查这些必需项是否已在数据库中存在

---

## 5. 第三步：添加 API 配置

每个业务模块需要两个 YAML 文件，放在 `config/api/{module}/` 下：

- `{prefix}_api_path.yaml` — API 路径注册表（`api_key → path + method`）
- `{prefix}_api_params.yaml` — 参数默认模板（`path → 参数骨架`）

**推荐方式：通过 `swagger_parser.py` 一键生成**，无需手写。

### 4.1 执行脚本自动生成

```bash
# 最简用法（从 config/env/test.yaml 自动登录，team/module 对应 Swagger 文档分组）
python script/swagger_parser.py --module gen_md --team TERP

# 指定环境 / 多项目模式
python script/swagger_parser.py --module scm_pur --team TERP --env staging --project my_project

# 手动传入 Cookie（跳过自动登录）
python script/swagger_parser.py --module gen_md --team TERP \
    --base-url https://your-erp-host:8080 \
    --cookie "t_iam_test=eyJ..."

# 包含 $SYS_ 系统服务接口（默认过滤）
python script/swagger_parser.py --module gen_md --team TERP --include-sys

# 预览解析结果，不写文件
python script/swagger_parser.py --module gen_md --team TERP --dry-run
```

脚本自动输出到对应模块目录：

```
config/api/gen_md/
├── md_api_path.yaml     # ← 自动生成
└── md_api_params.yaml   # ← 自动生成
```

> **`--team` 和 `--module` 如何确认？**  
> 打开被测系统的 Swagger UI（一般在 `/swagger-ui.html`），查看右上角分组下拉框，
> 格式为 `{team} / {module}`，例如 `TERP / gen_md`。

### 4.2 生成结果说明

`{prefix}_api_path.yaml`：

```yaml
version: '1.0'
total_apis: 3
apis:
  GEN_MD-币种配置-保存服务:
    path: /api/trantor/service/engine/execute/GEN_MD$CurrencyConfigSaveService
    method: POST
  GEN_MD-币种配置-分页查询服务:
    path: /api/trantor/service/engine/execute/GEN_MD$CurrencyConfigQueryPageService
    method: POST
```

`{prefix}_api_params.yaml`：

```yaml
api_params:
  /api/trantor/service/engine/execute/GEN_MD$CurrencyConfigSaveService:
    params:
      request:
        code: null
        name: null
        status: null
        remark: null
    serviceKey: GEN_MD$CurrencyConfigSaveService
```

> **手动补充**：脚本从 Swagger Schema 推导参数骨架，偶有漏字段或类型不准的情况。
> 生成后对照一条真实请求（DevTools / 录制产物）核对一遍，补上 `null` 字段即可。

---

## 6. 第四步：创建模块目录与基类

### 5.1 新建目录

```bash
mkdir -p testcases/my_module
touch testcases/my_module/__init__.py
touch testcases/my_module/conftest.py
```

### 5.2 编写模块基类 `testcases/my_module/__init__.py`

```python
from testcases.comm.base_test import BaseTest

# 该模块加载的 API 配置文件前缀（对应 config/api/my_module/ 下的文件名）
_API_CONFIG_MODULES = ["my_module"]


class MyModuleBaseTest(BaseTest):
    """my_module 模块测试基类。"""

    @classmethod
    def setup_class(cls) -> None:
        super().setup_class()

        # 加载本模块的 API 路径配置（可叠加多个）
        for module in _API_CONFIG_MODULES:
            cls.api_facade.load_api_config(module)

        cls.logger.info("MyModule 基类初始化完成")
```

> **说明**：`api_facade.load_api_config(module)` 会自动加载  
> `config/api/{module}/{module}_api_path.yaml` 和 `{module}_api_params.yaml`。

---

## 7. 第五步：注册模块清理

框架在 pytest session 结束时统一执行所有注册的清理函数（主进程触发一次）。  
每个模块只需在 `conftest.py` 里注册一次即可。

`testcases/my_module/conftest.py`：

```python
"""my_module 模块统一清理注册。"""

import os
from data_factory.base import DataFactory
from testcases.comm.cleanup_registry import register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_my_module() -> None:
    db = None
    try:
        env = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        data_factory = DataFactory(env_name=env, project=project)
        env_config = data_factory.get_env_config() or {}
        db_config = env_config.get("database", {}).get("erp_db")

        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 my_module 清理")
            return

        db = DBManager(**db_config)

        # 按依赖关系倒序删除（子表先于父表）
        db.delete(table="my_child_table",  where="code like %s", params=["AT_%"])
        db.delete(table="my_parent_table", where="code like %s", params=["AT_%"])

        Loggers.info("✅ my_module 测试数据清理完成")
    except Exception as e:
        Loggers.error(f"❌ my_module 清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


# order 越小越先执行；建议：主数据 < 业务单据 < 财务凭证
register_cleanup("my_module_cleanup", _cleanup_my_module, order=300)
```

---

## 8. 第六步：编写第一条用例

`testcases/my_module/test_my_feature_management.py`：

```python
import allure
from testcases.my_module import MyModuleBaseTest
from utils.report_util import a, case_decorator


@allure.epic("我的业务模块")
@allure.feature("功能管理")
class TestMyFeatureManagement(MyModuleBaseTest):
    """功能管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.feature_id = None

        # 绑定常用基础数据（无参数 → 使用 DEFAULT_CACHE_MAPPINGS）
        cls.bind_cache_data()

        cls.logger.info("TestMyFeatureManagement 初始化完成")

    @classmethod
    def teardown_class(cls):
        """模块清理已由 conftest.py 中的 cleanup_registry 统一处理。"""
        super().teardown_class()

    # ------------------------------------------------------------------ #
    # 用例：创建
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="创建功能",
        description="验证创建功能接口正常返回并持久化数据",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["my_module", "创建"]
    )
    def test_save_feature(self):
        """测试创建功能"""
        try:
            code = self.mock_util.generate_unique_code(tag="FEAT")
            name = f"自动化功能_{self.mock_util.get_timestamp()}"

            set_dict = {
                "remark": "自动化测试提交",
                "code":   code,
                "name":   name,
                "status": "ENABLED",
            }
            response, extracted_id = self.standard_api_call(
                api_key="MY_MODULE-保存服务",
                set_dict=set_dict,
                store_id_as="feature",        # 自动写入 cls.feature_id
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "创建响应")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ------------------------------------------------------------------ #
    # 用例：分页查询
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="分页查询功能列表",
        severity="normal",
        file_level_order=4,
        tags=["my_module", "查询"]
    )
    def test_query_feature_page(self):
        """测试分页查询"""
        try:
            if not self.feature_id:
                self.test_save_feature()

            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                },
                "fields": [{"name": "code", "type": "TEXT"}],
            }
            response, _ = self.standard_api_call(
                api_key="MY_MODULE-分页查询服务",
                set_dict=set_dict,
            )
            self.assert_util.assert_response_data(response)
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ------------------------------------------------------------------ #
    # 用例：删除
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="删除功能",
        severity="normal",
        file_level_order=16,
        tags=["my_module", "删除"]
    )
    def test_delete_feature(self):
        """测试删除功能"""
        try:
            if not self.feature_id:
                self.test_save_feature()

            response, _ = self.standard_api_call(
                api_key="MY_MODULE-删除服务",
                set_dict={"id": self.feature_id},
            )
            self.assert_util.assert_response_success(response)

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

---

## 9. 编写用例技巧

编写测试用例前，需要先拿到接口的真实请求数据。有两种方式：

---

### 方式一：api_record 录制（推荐）

`api_record/` 是一个基于 **mitmproxy** 的流量录制工具，可以在你操作 ERP 系统时，
自动捕获所有 `/api/trantor/` 请求并导出为 **cURL Markdown 文件**，再交给 AI 批量生成用例。

#### 步骤 1：启动录制代理

```bash
# 项目根目录执行
python api_record/start_recorder.py
# 默认监听 8080 端口，录制结果写入 api_record/raw_curls/recorded_flow.md
```

#### 步骤 2：配置浏览器代理

将浏览器（或系统）HTTP 代理指向 `127.0.0.1:8080`，然后在 ERP 界面正常操作目标业务流程。

> **录制过滤规则** 在 `api_record/recorder_config.json` 中配置：
> - `allowed_path_prefixes`：只录制 `/api/trantor/` 路径
> - `blocked_path_prefixes` / `blocked_path_contains`：过滤页面轮询、通知等噪音接口
> - `deduplicate_requests`：相同路径只保留第一次（默认开启）

#### 步骤 3：将录制产物交给 AI 生成用例

录制完成后，`api_record/raw_curls/recorded_flow.md` 中包含所有操作对应的 cURL。  
在 Cursor 中发送如下指令即可批量生成用例：

```
@workflow curl-to-testcase

录制文件：api_record/raw_curls/recorded_flow.md
目标模块：testcases/my_module/
基类：MyModuleBaseTest
```

AI 会自动完成：解析 cURL → 清洗平台噪音字段 → 映射 `api_key` → 生成标准 pytest 用例。

---

### 方式二：直接复制 cURL

适合临时验证单个接口，无需启动代理。

#### 步骤 1：从 DevTools 复制 cURL

1. 打开浏览器 DevTools → **Network** 面板
2. 在 ERP 界面执行目标操作
3. 找到对应请求 → 右键 → **Copy → Copy as cURL (bash)**

#### 步骤 2：粘贴给 AI 生成用例

将 cURL 直接粘贴到 Cursor 对话框，并附上模块说明：

```
以下是一个保存接口的 cURL，请参考项目规范生成对应的 pytest 测试用例：
目标文件：testcases/my_module/test_my_feature_management.py
基类：MyModuleBaseTest

curl -X POST 'https://your-host/api/trantor/...' \
  -H 'content-type: application/json' \
  --data-raw '{"params":{"request":{"code":"xxx","name":"yyy"}},...}'
```

> **AI 会自动清洗以下平台噪音字段**（无需手动删除）：  
> `sceneKey` / `serviceKey` / `viewTitle` / `appId` / `teamId` / `version` /
> `createdAt` / `updatedAt` / `tenantId`

---

### 两种方式对比

| | api_record 录制 | 直接复制 cURL |
|---|---|---|
| 适用场景 | 完整业务流（多接口联动） | 单个接口快速验证 |
| 操作成本 | 需启动代理 + 配置浏览器 | 直接从 DevTools 复制 |
| 批量效率 | 高（一次操作录制全部接口） | 低（每个接口单独复制） |
| 推荐场景 | 新模块首次建立用例集 | 补充单个遗漏接口 |

---

## 10. 第七步：运行与查看报告

### 10.1 运行单个文件（快速验证）

```bash
pytest testcases/my_module/test_my_feature_management.py -v
```

### 10.2 运行整个模块

```bash
pytest testcases/my_module/ -v --alluredir=reports/allure-results
```

### 10.3 指定环境 + 项目

```bash
pytest testcases/my_module/ \
  --env=test \
  --project=project_alpha \
  --alluredir=reports/allure-results
```

### 10.4 仅跑冒烟测试

```bash
pytest testcases/my_module/ -m "smoke" -v
```

### 10.5 并行执行（需先确认用例无共享写状态）

```bash
pytest testcases/my_module/ -n auto --dist loadscope
```

### 10.6 生成 Allure 报告

```bash
allure serve reports/allure-results
```

---

## 11. 扩展数据源（可选）

当你的模块需要使用**框架默认不包含**的缓存数据（如采购缓存 `pur_cache_data`）时，  
在模块基类 `load_cache_data()` 中调用 `TestDataContext.register_source`（与 `load_sql_cache` 同级），  
或在 `conftest.py` 顶层注册一次。

```python
# 模块基类 load_cache_data 内（与 scm_pur / scm_del 等一致）：
from testcases.comm.test_data_context import TestDataContext

TestDataContext.register_source("pur_config", "pur_cache_data")
```

随后在模块基类 `bind_context()` 中**先** `bind_cache_data()`，再 `bind_module_user_context(...)`（与 `scm_sls` / `scm_del` 一致）。

```python
# testcases/my_module/conftest.py 顶部（可选，与基类二选一）：
from testcases.comm.test_data_context import TestDataContext

TestDataContext.register_source("pur_config", "pur_cache_data")
```

随后在模块基类或用例的 `bind_cache_data` 中直接用路径引用：

```python
cls.bind_cache_data({
    **cls.DEFAULT_CACHE_MAPPINGS,   # 保留默认映射
    "pur_org_id": "pur_cache_data.pur_org_info.id",
})
```

同样地，如需扩展 `DEFAULT_CACHE_MAPPINGS`（增加默认绑定字段），在模块基类中整体替换：

```python
class MyModuleBaseTest(BaseTest):
    DEFAULT_CACHE_MAPPINGS = {
        **BaseTest.DEFAULT_CACHE_MAPPINGS,
        "my_special_id": "my_cache_data.my_info.id",
    }
```

---

## 12. 快速检查清单

完成开发后，过一遍以下检查：

```
基础配置
  [ ] 已复制 config/env/.env_template → config/env/.env，并填写真实 URL/账号/密码
  [ ] config/env/.env 已加入 .gitignore，不会被提交
  [ ] config/env/{env}.yaml 中 ${VAR} 占位符与 .env 中的变量名对应

初始化 SQL 配置（config/erp/）
  [ ] 被测数据库中已创建 AUTOTEST_* 前缀的测试主数据（组织/供应商/客户/物料/仓位等）
  [ ] .env 中已配置 TEST_PUR_ORG / TEST_SLS_ORG / TEST_INV_ORG / TEST_VEND / TEST_CUST 等
  [ ] 首次运行后 cls.init_data / cls.md_cache_data 中无 None 字段（否则说明数据缺失）
  [ ] 修改了 SQL 后若仍命中旧缓存，可删除 `testdata/cache/` 下对应 json（正常情况下 hash 会自动失效缓存）

API 配置
  [ ] 已执行 swagger_parser.py 生成 {prefix}_api_path.yaml 和 {prefix}_api_params.yaml
  [ ] {module}_api_path.yaml 中的 path 与系统实际 URL 一致
  [ ] {module}_api_params.yaml 中已去掉所有平台噪音字段（自动生成的已过滤）
  [ ] api_key（中文名）已与用例中 standard_api_call 的 api_key 参数对齐

模块基类
  [ ] __init__.py 调用了 api_facade.load_api_config(module)
  [ ] 继承自 BaseTest 或其已有子类

清理注册
  [ ] conftest.py 中已调用 register_cleanup(...)
  [ ] 清理顺序：子表 before 父表
  [ ] 所有测试数据使用 AT_ 前缀

用例代码
  [ ] 使用 case_decorator 而非 @pytest.mark.run
  [ ] file_level_order 按 创建(1-3)/查询(4-6)/更新(7-9)/删除(16-18) 编排
  [ ] 使用 self.mock_util 生成随机数据，无硬编码
  [ ] 每个测试方法有 try-except，失败时 a.text(str(e), "失败原因")
  [ ] store_id_as 已正确设置，后续步骤使用 self.{name}_id
  [ ] 未调用 self.test_xxx()（依赖通过 if not self.xxx_id: 驱动）
```

---

## 13. 常见问题

### Q: `standard_api_call` 报 "未找到 API 配置"

检查：
1. `__init__.py` 的 `setup_class` 是否调用了 `cls.api_facade.load_api_config("my_module")`
2. `api_key` 拼写是否与 `*_api_path.yaml` 中的 key 完全一致（包括中文）

### Q: `bind_cache_data` 绑定结果全是 `None`

检查：
1. 环境配置 URL/账号是否正确（登录失败会导致 `init_data` 为空）
2. 缓存路径第一段（如 `currency_info`）是否已在 `TestDataContext._SOURCE_REGISTRY` 中注册
3. 自定义数据源是否调用了 `TestDataContext.register_source(key, attr)`

### Q: 清理数据没有被执行

检查：
1. `conftest.py` 是否在模块目录下（pytest 加载时会自动 import）
2. `register_cleanup` 是否在模块顶层调用（而非在函数内部）
3. 是否设置了 `ENABLE_PHYSICAL_DELETE=false`（此时 `db.delete` 不执行，只记录 warning）

### Q: 用例执行顺序不符合预期

确认所有用例使用的是 `file_level_order` 而非 `order`（`order` 是全局排序，会交叉文件执行）。

### Q: 并行执行时数据冲突

将业务流转用例（创建→更新→删除有状态依赖的）标记或放入 `serial_flow` 根目录，  
在 CI 中用 `--job-group=serial -n 1` 单独跑。

---

> 遇到更复杂的场景，参考以下资源：
> - `.cursor/rules/testcase_temp.mdc` — 完整代码模板（init_data / md_cache_data / 异步任务等）
> - `.cursor/rules/coding_standards.mdc` — 规范速查
> - `api_record/recorder_config.json` — 录制过滤规则配置
> - `@workflow curl-to-testcase` — 将录制产物或 cURL 直接转换为 pytest 用例
> - `@workflow workflow-trigger` + 描述需求 — 让 AI 直接生成用例
