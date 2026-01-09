# ERP 自动化测试平台

> 基于 Python + pytest 的企业级 ERP 系统自动化测试框架

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.4.3-green.svg)](https://pytest.org/)
[![Allure](https://img.shields.io/badge/Allure-2.24.1-orange.svg)](https://docs.qameta.io/allure/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-teal.svg)](https://fastapi.tiangolo.com/)

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [测试规范](#测试规范)
- [部署说明](#部署说明)
- [常见问题](#常见问题)

## 🎯 项目简介

ERP 自动化测试平台是一个面向企业级 ERP 系统的自动化测试框架，提供完整的测试基础设施、工具类和最佳实践。支持 API 测试、数据库验证、异步任务测试等多种测试场景，并集成 Allure 报告系统，提供丰富的测试报告和可视化分析。

### 核心能力

- ✅ **标准化测试流程**：统一的测试基类、工具方法和代码规范
- ✅ **多环境支持**：dev/test/staging/prod 环境配置管理
- ✅ **多项目支持**：支持多个项目独立配置，配置隔离互不干扰
- ✅ **数据驱动测试**：数据工厂模式，支持基础数据和主数据初始化
- ✅ **数据库操作**：安全的数据库连接管理、事务处理和参数化查询
- ✅ **异步任务测试**：支持异步任务状态轮询和等待机制
- ✅ **测试报告**：Allure 报告集成，支持步骤记录、截图、性能指标
- ✅ **CI/CD 集成**：支持 Docker 容器化部署和持续集成

## ✨ 功能特性

### 测试框架能力

- **测试基类体系**：`BaseTest` → `GenMdBaseTest` / `FinBaseTest` 等模块化基类
- **标准化 API 调用**：`standard_api_call` 方法统一处理 API 请求和响应
- **智能测试排序**：支持全局排序和文件级串行执行
- **测试数据管理**：自动生成、清理和管理测试数据（AT_ 前缀隔离）

### 工具类支持

- **数据库工具**：`DBManager` 统一管理数据库连接和操作
- **HTTP 工具**：`HttpUtil` 封装 HTTP 请求，支持会话管理和请求头
- **断言工具**：`AssertUtil` 提供丰富的断言方法
- **Mock 工具**：`MockUtil` 生成测试数据（编码、名称、日期等）
- **报告工具**：`ReportUtil` 增强 Allure 报告，支持步骤记录
- **异步等待工具**：`AsyncWaitUtil` 支持异步任务状态轮询

### 测试报告

- **Allure 报告**：集成 Allure 2.24.1，支持丰富的报告展示
- **测试步骤记录**：自动记录测试步骤和关键数据
- **失败截图**：测试失败时自动截图（UI 测试场景）
- **环境信息**：自动记录测试环境、版本等信息

## 🛠 技术栈

### 核心框架

- **Python 3.9+**：编程语言
- **pytest 7.4.3**：测试框架
- **Allure 2.24.1**：测试报告框架
- **FastAPI 0.104.1**：Web API 服务框架

### 主要依赖

- **数据库**：PyMySQL 1.1.0（数据库驱动）, DBUtils 3.0.3（连接池）
- **HTTP 请求**：requests 2.31.0（会话管理、请求重试）
- **数据处理**：pandas 2.1.4（数据转换）, openpyxl 3.1.2（Excel 操作）
- **配置管理**：PyYAML 6.0.1（YAML 解析）, python-dotenv 1.0.0（环境变量）
- **日志**：loguru 0.7.2（结构化日志）
- **数据生成**：Faker 19.13.0（Mock 数据，支持中文）

### 核心工具类

- **DBManager** - 数据库连接管理（查增改删、事务处理、参数化查询）
- **HttpUtil** - HTTP 请求工具（会话隔离、请求头管理）
- **AssertHelper** - 断言助手（API 响应验证、错误信息记录）
- **AsyncWaitUtil** - 异步等待工具（轮询机制、超时控制、状态追踪）
- **CacheUtil** - 缓存管理（数据持久化、过期刷新、自动加载）
- **ReportEnhancer** - 报告增强（步骤记录、性能指标、业务上下文）
- **MockData** - 数据生成（编码、日期、电话、公司名等）
- **ParamUtil** - 参数处理（字段过滤、嵌套路径、类型转换）

### 测试增强插件

- pytest-order：全局排序测试用例
- pytest-xdist：并行执行测试（支持按文件分发）
- pytest-cov：代码覆盖率统计
- pytest-rerunfailures：失败重试机制
- pytest-timeout：超时控制（防止卡死）
- pytest-mock：Mock 数据和函数
- pytest-assume：多断言支持

## 📁 项目结构

```
erp-autotest/
├── config/                 # 配置文件目录
│   ├── env/               # 环境配置
│   │   ├── test.yaml      # 默认配置（向后兼容）
│   │   ├── dev.yaml       # 默认开发环境配置
│   │   └── project1/      # 项目1配置目录（多项目模式）
│   │       ├── test.yaml
│   │       └── dev.yaml
│   │   └── project2/      # 项目2配置目录（多项目模式）
│   │       ├── test.yaml
│   │       └── dev.yaml
│   └── erp/               # 模块初始化 SQL（md_init_sql.yaml 等）
├── data_factory/          # 数据工厂（当前完善中）
│   ├── base.py           # 数据工厂基类 + 配置管理 + SQL 缓存
│   ├── MD/               # 主数据工厂（partner_fc、org_fc 等）
│   ├── CF/               # 配置工厂（待完善）
│   └── BIZ/              # 业务工厂（待完善）
├── docs/                  # 项目文档
│   └── STANDARD_API_CALL_GUIDE.md  # API 调用完整指南
├── routers/               # FastAPI 路由（Web 后台）
│   ├── allure_api.py     # 报告查看 API
│   ├── api_manage.py     # 测试执行 API
│   └── data_factory_api.py  # 数据工厂 API
├── script/                # 工具脚本
│   ├── case_coverage_stat.py    # 用例覆盖率统计
│   ├── find_unreferenced_services.py  # 查找未引用 API
│   └── swagger_parser.py  # Swagger 解析
├── testcases/             # 测试用例目录
│   ├── comm/             # 公共测试基类
│   │   ├── base_test.py  # BaseTest 基类（核心）
│   │   └── conftest.py   # pytest 配置（钩子、排序逻辑）
│   ├── gen_md/           # 主数据模块
│   ├── scm_pur/          # 采购模块
│   ├── scm_sls/          # 销售模块
│   ├── erp_fin/          # 财务模块
│   ├── scm_inv/          # 库存模块
│   └── ...               # 其他模块（acc、prd、del 等）
├── utils/                 # 工具类库（16 个工具）
│   ├── mysql_util.py    # DBManager - 数据库操作
│   ├── request_util.py  # HttpUtil - HTTP 请求
│   ├── assert_util.py   # AssertHelper - 断言验证
│   ├── async_wait_util.py # AsyncWaitUtil - 异步轮询
│   ├── cache_util.py    # CacheUtil - 缓存管理
│   ├── param_util.py    # ParamUtil - 参数处理
│   ├── report_util.py   # ReportEnhancer - 报告增强
│   ├── mock_util.py     # MockData - 数据生成
│   └── ...              # 其他工具
├── testdata/             # 测试数据
│   └── cache/           # 缓存文件（md_init_cache.json 等，框架自动生成）
├── config/               # 配置文件
│   ├── api/             # API配置文件（YAML格式）
│   │   ├── gen_md/      # 主数据API配置（md_api_path.yaml 等）
│   │   ├── scm_pur/     # 采购API配置（pur_api_path.yaml 等）
│   │   └── ...          # 其他模块配置
│   ├── env/             # 环境配置（dev/test/staging/prod.yaml）
│   └── erp/             # 模块初始化 SQL（md_init_sql.yaml 等）
├── reports/              # 测试报告目录
│   ├── allure-results/  # Allure 原始数据
│   └── allure-report/   # Allure HTML 报告
├── logs/                 # 日志目录
├── static/               # 静态资源（Swagger UI 等）
├── main.py               # FastAPI 应用入口
├── pytest.ini            # pytest 全局配置
├── conftest.py           # pytest 全局 fixture
├── requirements.txt      # Python 依赖清单
├── Dockerfile            # 容器化构建
├── .env                  # 环境变量
├── .gitignore            # Git 忽略配置
└── dice.yml              # Erda 部署配置
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- MySQL 5.7+（用于测试数据管理）
- Allure Commandline（用于生成报告）

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd erp-autotest
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境**

### 默认配置模式（单项目）

在 `config/env/` 目录下创建环境配置文件（如 `test.yaml`），包含门户配置和数据库配置：

```yaml
# config/env/test.yaml
# 门户配置（支持多个门户和多个租户）
portal_config:
  terp:                                    # 租户名称
    TERP_PORTAL:                           # 后台管理门户
      portal_url: "http://test.example.com"
      iam_url: "http://iam.example.com"
      login_type: "account"                # 登录方式：account 或 sso
      account: "admin"
      password: "password"
    TERP_CUST_PC:                          # 客户端门户（可选）
      portal_url: "http://customer.example.com"
      iam_url: "http://iam.example.com"
      login_type: "account"
      account: "customer_user"
      password: "password"

# 数据库配置
database:
  erp_db:                                  # ERP 业务库
    host: "localhost"
    port: 3306
    database: "erp_db"
    username: "root"
    password: "password"
  iam_db:                                  # IAM 库（可选）
    host: "localhost"
    port: 3306
    database: "iam_db"
    username: "root"
    password: "password"

# Trantor 版本（可通过 --trantor_version 命令行参数覆盖）
trantor_version: "2.5.25.0330.0-SNAPSHOT"

# 缓存配置（可选）
cache:
  expire_minutes: 1440                     # 缓存过期时间（分钟），默认 24 小时
  auto_refresh: true                       # 是否自动刷新过期缓存
```

### 多项目配置模式（推荐）

如果需要支持多个项目，可以按项目目录组织配置文件：

```bash
# 创建项目配置目录
mkdir -p config/env/project1
mkdir -p config/env/project2

# 在项目目录下创建配置文件
# config/env/project1/test.yaml
# config/env/project1/.env          # 项目1的环境变量（可选）
# config/env/project2/test.yaml
# config/env/project2/.env          # 项目2的环境变量（可选）
```

**配置文件说明**：
- **YAML 配置文件**：`config/env/{project}/{env}.yaml` - 项目配置结构
- **环境变量文件**：`config/env/{project}/.env` - 项目特定的环境变量（可选）

**环境变量加载优先级**：
1. **项目级 `.env`**：`config/env/{project}/.env` （优先级最高）
2. **默认 `.env`**：`config/env/.env` （作为共享/默认值）
3. **根目录 `.env`**：项目根目录的 `.env` （向后兼容）

**配置加载优先级**：
1. 如果指定 `--project=project1`，框架会从 `config/env/project1/{env}.yaml` 加载配置
2. 如果项目配置文件不存在，会自动回退到默认配置 `config/env/{env}.yaml`（向后兼容）
3. 如果不指定 `--project` 参数，直接使用默认配置 `config/env/{env}.yaml`

**环境变量配置示例**：

```bash
# config/env/demo1/.env
TEST_TERP_PORTAL_USERNAME='user1@example.com'
TEST_TERP_PORTAL_PASSWORD='password1'
TEST_DB_HOST='10.3.0.143'
TEST_DB_USER='demo1_test'
TEST_DB_PASSWORD='password1'
TEST_DB_NAME='demo1_test'

# config/env/demo2/.env
TEST_TERP_PORTAL_USERNAME='user2@example.com'
TEST_TERP_PORTAL_PASSWORD='password2'
TEST_DB_HOST='10.3.0.144'
TEST_DB_USER='demo2_test'
TEST_DB_PASSWORD='password2'
TEST_DB_NAME='demo2_test'
```

**优势**：
- ✅ 配置隔离：不同项目使用不同的数据库、门户等配置
- ✅ 环境变量隔离：每个项目可以拥有独立的 `.env` 文件
- ✅ 易于维护：项目配置独立管理，结构清晰
- ✅ 向后兼容：现有项目无需修改，继续使用默认配置
- ✅ 灵活切换：通过命令行参数快速切换项目

> 💡 **提示**：详细的多项目环境变量配置说明请参考 [docs/multi_project_env_config.md](docs/multi_project_env_config.md)

5. **初始化测试数据（首次运行）**

框架会自动初始化测试数据，包括：
- 执行 `config/erp/base_init_sql.yaml` 中的基础数据初始化脚本
- 执行 `config/erp/md_init_sql.yaml` 中的主数据初始化脚本
- 缓存初始化结果到 `testdata/cache/` 目录

首次运行较慢，后续运行会复用缓存（支持自动过期刷新）。

6. **运行测试**

```bash
# 运行所有测试（使用 test 环境，默认）
pytest

# 运行指定模块测试
pytest testcases/gen_md/
pytest testcases/scm_pur/

# 指定环境（dev/test/staging/prod）
pytest --env=test

# 指定项目（多项目模式）
pytest --project=project1 --env=test

# 指定 Trantor 版本
pytest --trantor_version=2.5.25.0330.0-SNAPSHOT

# 组合使用：指定项目和环境
pytest --project=project1 --env=test --alluredir=./reports/allure-results

# 并行执行（4 个进程，按文件分发）
pytest -n 4 --dist=loadfile

# 生成 Allure 报告
pytest --alluredir=./reports/allure-results
allure serve ./reports/allure-results

# 启动 Web 管理后台（集成报告查看和测试执行）
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# 访问：http://localhost:8000/docs（API 文档）
#      http://localhost:8000/allure（Allure 报告）
```

## 📖 使用指南

### 编写测试用例

#### 1. 创建测试类

```python
import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import case_decorator

@allure.epic("主数据管理")
@allure.feature("合作伙伴管理")
class TestPartnerManagement(GenMdBaseTest):
    """合作伙伴管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.logger.info("合作伙伴管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="partner_md", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
```

#### 2. 编写测试方法

```python
@case_decorator(
    story="创建合作伙伴",
    title="测试创建合作伙伴",
    description="验证创建合作伙伴的基本功能",
    severity="critical",
    file_level_order=1,
    smoke=True,
    tags=["主数据", "合作伙伴"]
)
def test_save_partner(self):
    """测试创建合作伙伴"""
    try:
        # 1. 准备测试数据
        partner_code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
        partner_name = f"测试合作伙伴_{self.mock_util.get_timestamp()}"
        
        # 2. 使用标准化 API 调用
        set_dict = {
            "code": partner_code,
            "name": partner_name,
            "partnerType": "CUSTOMER"
        }
        response, extracted_id = self.standard_api_call(
            api_key="PARTNER-保存服务",
            set_dict=set_dict,
            store_id_as="partner"
        )
        
        # 3. 业务断言
        self.assert_util.assert_response_data(response)
        
        # 4. 保存 ID（如果 store_id_as 未设置）
        if not hasattr(self, 'partner_id'):
            self.partner_id = extracted_id
        
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

### 数据库操作

```python
# 查询数据
result = self.db.query_one(
    sql="SELECT * FROM partner_md WHERE id = %s",
    params=[self.partner_id]
)

# 插入数据
inserted_id = self.db.insert(
    table="partner_md",
    data={
        "code": "AT_CODE001",
        "name": "测试数据",
        "status": "ENABLED"
    }
)

# 更新数据
affected_rows = self.db.update(
    table="partner_md",
    data={"name": "更新后的名称"},
    where="id = %s",
    params=[self.partner_id]
)

# 删除数据
affected_rows = self.db.delete(
    table="partner_md",
    where="code like %s",
    params=["AT_%"]
)
```

### 异步任务测试

```python
@case_decorator(
    story="异步任务",
    title="测试异步初始化并等待完成",
    description="验证异步任务的执行和状态流转",
    severity="normal",
    file_level_order=10,
    tags=["异步", "初始化"]
)
def test_async_init(self):
    """测试异步初始化并等待完成"""
    try:
        # 1. 发起异步任务
        set_dict = {"id": self.xxx_id}
        response, _ = self.standard_api_call(
            api_key="XXX-执行初始化-异步任务发起",
            set_dict=set_dict
        )
        self.assert_util.assert_response_success(response)
        
        # 2. 定义查询函数
        def query_status():
            query_response, _ = self.standard_api_call(
                api_key="XXX-查询详情服务",
                set_dict={"id": self.xxx_id}
            )
            return query_response.get("data", {}).get("data", {})
        
        # 3. 等待异步任务完成
        result = self.async_wait_util.wait_for_async_status(
            query_func=query_status,
            status_field="asyncExecutionStatus",
            success_status="SUCCEEDED",
            failed_status="FAILED",
            failure_reason_field="asyncExecutionFailureReason",
            max_wait=60,
            interval=3.0
        )
        
        # 4. 断言结果
        if result.status == self.wait_status.SUCCESS:
            a.text(f"✅ 异步任务成功完成，总耗时: {result.total_wait_time:.2f}秒", "异步任务结果")
        else:
            raise AssertionError(f"异步任务执行失败: {result.error_message}")
            
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

## 📝 测试规范

### 命名规范

- **测试文件**：`test_*.py`
- **测试类**：`Test*`（如 `TestPartnerManagement`）
- **测试方法**：`test_*`（如 `test_save_partner`）
- **测试数据编码**：使用 `AT_` 前缀（如 `AT_PARTNER001`）

### 测试用例结构

1. **setup_class**：测试类初始化（登录、数据库连接、基础数据准备）
2. **setup_method**：测试方法前置（可选）
3. **测试方法**：执行测试逻辑
4. **teardown_method**：测试方法后置（可选）
5. **teardown_class**：测试类清理（删除测试数据、关闭连接）

### 测试数据管理

- **数据隔离**：所有测试数据使用 `AT_` 前缀
- **数据清理**：在 `teardown_class` 中清理测试数据
- **数据准备**：使用 `init_data`（基础数据）和 `md_cache_data`（主数据）

### 代码规范

- 使用参数化查询，禁止 SQL 注入
- 所有写操作使用事务，失败自动回滚
- 使用 `standard_api_call` 统一 API 调用
- 使用 `case_decorator` 装饰器标记测试用例
- 使用 `file_level_order` 控制测试执行顺序

详细规范请参考 `docs/cursor_testcase_generation.md`。

## 🐳 部署说明

### Docker 部署

1. **构建镜像**

```bash
docker build -t erp-autotest:latest .
```

2. **运行容器**

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/reports:/app/reports \
  erp-autotest:latest
```

3. **访问服务**

- API 文档：http://localhost:8000/docs
- Allure 报告：http://localhost:8000/allure

### Erda 平台部署

项目已配置 `dice.yml`，可直接在 Erda 平台部署：

1. 推送代码到 Git 仓库
2. 在 Erda 平台创建应用
3. 配置环境变量和数据库连接
4. 触发部署流水线

## ❓ 常见问题

### Q1: 如何切换测试环境？

A: 使用 `--env` 参数指定环境：

```bash
pytest --env=test    # 测试环境
pytest --env=dev     # 开发环境
pytest --env=staging # 预发布环境
```

### Q2: 如何查看测试报告？

A: 运行测试后，使用 Allure 生成报告：

```bash
pytest --alluredir=./reports/allure-results
allure serve ./reports/allure-results
```

或访问 Web 服务：http://localhost:8000/allure

### Q3: 测试数据清理失败怎么办？

A: 检查以下几点：

1. 数据库连接是否正常
2. 测试数据是否使用 `AT_` 前缀
3. 删除顺序是否正确（先删除子表，再删除父表）
4. 是否有外键约束阻止删除

### Q4: 如何并行执行测试？

A: 使用 pytest-xdist 插件：

```bash
pytest -n auto  # 自动检测 CPU 核心数
pytest -n 4     # 使用 4 个进程
```

### Q5: 如何跳过某些测试？

A: 使用 `@pytest.mark.skip` 装饰器：

```python
@pytest.mark.skip(reason="功能暂未实现")
@case_decorator(...)
def test_xxx(self):
    pass
```

### Q6: 缓存数据如何更新或清除？

A: 缓存支持自动过期刷新机制（默认 24 小时）：

```bash
# 方式一：删除缓存文件，重新运行测试会自动生成
rm testdata/cache/*.json

# 方式二：设置缓存过期时间（在 setup_class 中）
from utils.cache_util import CacheUtil
CacheUtil.init(cache_dir="testdata/cache", expire_minutes=60)  # 1 小时过期

# 方式三：手动刷新特定缓存
CacheUtil.refresh_expired_cache()
```

### Q7: data_factory 如何使用？

A: data_factory 框架当前处于完善阶段：
- **已实现**：DataFactory 基类、ConfigLoader（配置加载）、SQL 缓存管理
- **部分实现**：MD 工厂（PartnerFactory、OrgFactory、MatFactory 等）

当前推荐直接使用 `standard_api_call` 创建测试数据，暂不依赖 data_factory：

```python
# 推荐做法：直接用 API 创建
response, partner_id = self.standard_api_call(
    api_key="GEN-合作伙伴-保存服务",
    set_dict={"code": "AT_PARTNER001", "name": "测试合作伙伴"}
)
```

### Q8: 多环境如何配置？

A: 在 `config/env/` 目录下创建不同环境的配置文件，使用 `--env` 参数指定：

```bash
# 开发环境
pytest --env=dev

# 测试环境（默认）
pytest --env=test

# 预发布环境
pytest --env=staging

# 生产环境（使用前需谨慎）
pytest --env=prod
```

### Q8.1: 多项目如何配置？

A: 框架支持多项目配置，通过 `--project` 参数指定项目名称：

**1. 创建项目配置目录**
```bash
mkdir -p config/env/project1
mkdir -p config/env/project2
```

**2. 在每个项目目录下创建环境配置文件**
```bash
# config/env/project1/test.yaml
# config/env/project1/dev.yaml
# config/env/project1/.env          # 项目1的环境变量（可选）
# config/env/project2/test.yaml
# config/env/project2/dev.yaml
# config/env/project2/.env          # 项目2的环境变量（可选）
```

**环境变量配置说明**：
- 每个项目可以拥有独立的 `.env` 文件（`config/env/{project}/.env`）
- 环境变量加载优先级：项目级 `.env` > 全局 `.env`
- 项目级 `.env` 不存在时，自动使用全局 `.env` 文件

**3. 运行测试时指定项目**
```bash
# 运行 project1 的测试
pytest --project=project1 --env=test

# 运行 project2 的测试
pytest --project=project2 --env=test

# 不指定项目时使用默认配置（向后兼容）
pytest --env=test
```

**配置加载逻辑**：
- 如果指定 `--project=project1`，框架会优先从 `config/env/project1/{env}.yaml` 加载配置
- 如果项目配置文件不存在，会自动回退到默认配置 `config/env/{env}.yaml`
- 不同项目的配置完全隔离，包括数据库、门户、环境变量等

**适用场景**：
- ✅ 同一套测试框架需要测试多个不同的 ERP 项目
- ✅ 不同项目使用不同的数据库和门户地址
- ✅ 需要为不同项目维护独立的配置

### Q9: 测试用例执行顺序如何控制？

A: 框架支持两种排序方式，可混用：

```python
# 方式一：文件级串行（推荐）- 同一文件内串行，不同文件可并行
@case_decorator(file_level_order=1)
def test_create_partner(self): pass

@case_decorator(file_level_order=2)
def test_update_partner(self): pass

# 方式二：全局排序 - 所有文件统一排序
@pytest.mark.order(1)
def test_xxx(self): pass
```

### Q10: 如何进行失败重试？

A: 使用 `--reruns` 参数进行自动重试：

```bash
# 重试 2 次，间隔 1 秒
pytest --reruns 2 --reruns-delay 1

# 仅对特定异常重试
pytest --reruns 2 --reruns-error-type TimeoutError
```

或在代码中使用：

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)
@case_decorator(...)
def test_xxx(self): pass
```

## 📚 相关文档

项目文档位于 `docs/` 目录，包括：

- **STANDARD_API_CALL_GUIDE.md** - API 调用完整指南（必读）：详细说明 `standard_api_call` 的参数、用法和各种场景
- **cursor_testcase_generation.md** - 用例编写详细规范（参考）：编写规范、代码示例、最佳实践

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用内部许可证，仅供公司内部使用。

## 👥 维护团队

ERP 自动化测试平台维护团队

---

**最后更新**：2025年

