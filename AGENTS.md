# AGENTS.md - ERP Autotest Framework

> Python + pytest 企业级 ERP 自动化测试框架。使用 `standard_api_call` 统一 API 调用，Allure 报告，pytest-xdist 并行执行。

## 命令速查

```bash
# 安装依赖
pip install -r requirements.txt

# 新环境 / 首次接入：全量自检（环境、库、骨架、SQL/API 配置等）
python script/project_bootstrap.py
# 仅校验仓库骨架（与 pre-commit 一致）
python script/project_bootstrap.py --section skeleton
# 连库预热 init + md 缓存（需 .env 与 DB 就绪）
python script/project_bootstrap.py --seed warm-cache --env test

# 运行所有测试（默认 env=test，并行）
pytest

# 运行单个测试文件
pytest testcases/gen_md/gen_base/test_curr_management.py -v

# 运行单个测试方法（-k 模糊匹配）
pytest testcases/gen_md/gen_base/test_curr_management.py -k "test_save_curr" -v

# 指定环境/项目
pytest --env=dev
pytest --project=project1 --env=test

# 冒烟测试 / 优先级测试
pytest -m "smoke" -v
pytest -m "p0" -v

# 串行执行（CI 关键流程）
pytest --job-group=serial -n 1

# 调试：关闭并行和重试
pytest -n 0 -p no:rerunfailures --log-cli-level=INFO testcases/gen_md

# 强制刷新缓存
pytest --fresh-cache testcases/

# 生成 Allure 报告
allure serve ./reports/allure-results

# Lint & Format（Ruff）
ruff check --fix .
ruff format .

# Pre-commit
pre-commit run --all-files
```

## 代码风格

### Imports
- 顺序：标准库 → 第三方 → 本地项目（Ruff `I` 规则强制）
- 工具类：`from utils.xxx_util import XxxClass`
- 模块基类：`from testcases.{module} import {Module}BaseTest`
- 报告装饰器：`from utils.report_util import a, case_decorator`

### 命名约定
| 类型 | 格式 | 示例 |
|------|------|------|
| 测试文件 | `test_{feature}.py` | `test_curr_management.py` |
| 测试类 | `Test{Feature}Management` | `TestCurrManagement` |
| 测试方法 | `test_{action}_{object}` | `test_save_curr` |
| API 键名 | 中文描述 | `"GEN-币种配置-保存服务"` |
| 测试数据 | `AT_` 前缀 | `AT_PARTNER001` |
| 工具类 | `{Purpose}Util/Helper` | `AssertHelper`, `DBManager` |
| 私有辅助 | `_{action}_{object}` | `_get_po_detail_by_id` |

### 类型提示
- 工具类和基类使用类型提示（`Dict[str, Any]`, `Optional[str]` 等）
- 测试方法**不使用**类型提示（遵循 pytest 惯例）
- `pyrightconfig.json` 已关闭类型检查

### 错误处理
- **每个测试方法必须用 try/except**，失败前记录原因：
  ```python
  except Exception as e:
      a.text(str(e), "失败原因")
      raise
  ```
- 数据库操作使用 try/except + 失败回滚
- 清理失败仅记录日志，不中断测试会话

## 测试模式

### 继承链
`BaseTest` → `{Module}BaseTest`（如 `GenMdBaseTest`） → `TestXxxManagement`

### 标准测试方法模板
```python
@case_decorator(
    story="业务场景",
    title="测试{功能}",
    description="验证{具体功能}",
    severity="critical",
    file_level_order=1,
    smoke=True,
    tags=["模块", "功能"]
)
def test_save_object(self):
    try:
        # 1. 准备数据（使用 self.mock_util，禁止硬编码）
        # 2. 调用 standard_api_call
        # 3. 断言响应
        # 4. 记录数据 a.json(key, value)
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

### file_level_order 排序规则
| 范围 | 操作 |
|------|------|
| 1-3 | 创建（Create） |
| 4-6 | 查询（Query） |
| 7-9 | 更新（Update） |
| 10-12 | 导出（Export） |
| 13-15 | 导入（Import） |
| 16-18 | 删除（Delete） |

### 数据依赖
- 使用私有辅助方法：`_ensure_xxx()` 而非 `self.test_xxx()`
- **禁止测试方法互相调用**
- 创建/关联操作需支持幂等（检测"已存在"错误并复用）

### 数据清理
- 使用 `cleanup_registry.py` 注册清理函数
- 在模块 `conftest.py` 中通过 `register_cleanup(name, func, order)` 注册
- 子表先删、父表后删（逆依赖顺序）
- **禁止循环批量删除**，每张表单独删除

## 核心规则（来自 .cursor/rules/）

1. **95% API 调用使用 `standard_api_call`**，禁止直接拼 URL
2. **禁止硬编码测试数据**，使用 `self.mock_util` 生成
3. Payload 清理：移除 sceneKey、serviceKey、appId 等平台噪声字段
4. 含 ID 的复杂对象只保留 ID 引用，不传完整对象
5. `remark`/`note` 字段放在 `set_dict` 首位，固定值 `"自动化测试提交"`
6. 所有 SQL 查询必须参数化，禁止字符串拼接
7. 测试数据统一使用 `AT_` 前缀
8. `teardown_class` 必须调用 `super().teardown_class()`
9. 编码前先分析，优先小步增量修改
10. 禁止硬编码密钥/密码

## 项目结构

```
config/api/{module}/     → API 路径/参数 YAML 配置
config/env/              → 多环境配置（dev/test/staging/prod）
config/erp/              → SQL 初始化配置
testcases/comm/          → 基类和服务（BaseTest, ApiCallService 等）
testcases/{module}/      → 按 ERP 模块组织的测试
utils/                   → 16 个工具模块（mysql, request, assert, mock 等）
data_factory/            → 数据工厂（SQL 驱动初始化）
routers/                 → FastAPI 路由（测试执行 + 报告服务）
api_record/              → mitmproxy API 录制工具
reports/                 → Allure 结果 + HTML 报告
testdata/cache/          → SQL 初始化缓存（自动生成）
```

## 关键依赖

| 类别 | 包 | 用途 |
|------|-----|------|
| 测试 | pytest + allure-pytest | 测试运行器 + 报告 |
| 并行 | pytest-xdist | 并行执行（`-n auto --dist loadscope`） |
| 重试 | pytest-rerunfailures | 失败重试 |
| HTTP | requests | HTTP 客户端 |
| 数据库 | PyMySQL + DBUtils | MySQL + 连接池 |
| Web | fastapi + uvicorn | API 服务 |
| Mock | Faker (zh_CN) | 中文测试数据 |
| 日志 | loguru | 结构化日志 |
| Lint | ruff | 快速 lint + 格式化 |
| 录制 | mitmproxy | API 流量录制 |
