# ERP 自动化测试平台

## 项目简介
本项目是一个基于 Python 的 ERP 系统自动化测试平台，集成了完整的测试框架、Web API 服务、报告系统和数据工厂功能。支持多环境配置、并行测试执行、Allure 报告生成等功能。

## 技术栈
- **测试框架**: pytest 7.4.3 + pytest-xdist (并行执行)
- **Web框架**: FastAPI 0.104.1 + uvicorn
- **报告系统**: Allure 2.24.1
- **数据库**: MySQL + pymysql
- **HTTP客户端**: requests 2.31.0
- **配置管理**: PyYAML + python-dotenv
- **日志系统**: loguru 0.7.2
- **数据处理**: pandas 2.1.4 + openpyxl
- **数据生成**: faker 19.13.0

## 项目架构

### 核心组件
```
erp-autotest/
├── main.py                    # FastAPI 应用入口
├── routers/                   # API 路由模块
│   ├── api_manage.py         # 测试执行管理 API
│   ├── data_factory_api.py   # 数据工厂 API
│   └── allure_api.py         # Allure 报告 API
├── testcases/                # 测试用例目录
│   ├── conftest.py          # pytest 全局配置
│   ├── comm/                # 通用测试基类
│   │   └── base_test.py    # 基础测试类
│   ├── gen_md/             # 主数据管理测试
│   ├── erp_fin/            # 财务管理测试
│   │   ├── fin_ap/         # 应付管理
│   │   ├── fin_ar/         # 应收管理
│   │   ├── fin_iv/         # 存货价值
│   │   └── fin_sett/       # 结算管理
│   ├── scm_sls/            # 销售管理测试
│   ├── scm_pur/            # 采购管理测试
│   ├── scm_inv/            # 库存管理测试
│   ├── scm_del/            # 配送管理测试
│   ├── erp_prd/            # 生产管理测试
│   ├── erp_acc/            # 会计管理测试
│   └── sys_common/         # 系统通用测试
├── utils/                   # 工具类库
│   ├── request_util.py     # HTTP 请求工具
│   ├── mysql_util.py       # 数据库操作工具
│   ├── yaml_util.py        # YAML 配置工具
│   ├── report_util.py      # 报告生成工具
│   ├── log_util.py         # 日志管理工具
│   ├── param_util.py       # 参数处理工具
│   ├── file_util.py        # 文件操作工具
│   ├── assert_util.py      # 断言工具
│   ├── mock_util.py        # Mock 数据工具
│   ├── cache_util.py       # 缓存工具
│   ├── exception_util.py   # 异常处理工具
│   ├── response_util.py    # 响应处理工具
│   └── dingtalk_util.py    # 钉钉通知工具
├── config/                  # 配置文件目录
│   ├── base.yaml           # 基础配置
│   ├── env/                # 环境配置目录
│   └── erp/                # ERP 项目配置
│       ├── base_init_sql.yaml    # 基础数据初始化 SQL
│       ├── md_init_sql.yaml      # 主数据初始化 SQL
│       ├── sls_init_sql.yaml     # 销售管理初始化 SQL
│       ├── fin_init_sql.yaml     # 财务管理初始化 SQL
│       ├── pur_init_sql.yaml     # 采购管理初始化 SQL
│       └── del_init_sql.yaml     # 配送管理初始化 SQL
├── static/                  # 静态资源
├── reports/                 # 测试报告目录
│   ├── allure-results/     # Allure 结果数据
│   ├── allure-report/      # Allure 报告
│   ├── html/              # HTML 报告
│   └── junit/             # JUnit 报告
├── logs/                   # 日志文件目录
├── testdata/               # 测试数据目录
│   ├── cache/             # 缓存数据（init_cache.json, md_init_cache.json等）
│   └── {module}/          # 各模块API配置（api_params.yaml, api_path.yaml）
├── data_factory/           # 数据工厂目录
│   ├── base.py            # 数据工厂基类
│   └── {module}_factory.py # 各模块数据工厂
├── script/                 # 脚本工具
│   ├── swagger_parser.py  # Swagger API解析工具
│   └── case_coverage_stat.py # 用例覆盖率统计
├── pytest.ini             # pytest 配置
├── requirements.txt        # Python 依赖
├── Dockerfile             # Docker 镜像构建
├── pipeline.yml           # CI/CD 流水线配置
└── dice.yml               # Erda 平台部署配置
```

## 核心功能

### 1. Web API 服务
- **测试执行管理**: 支持全量、模块、单文件测试执行
- **数据工厂**: 测试数据生成和管理
- **报告查看**: Allure 报告在线查看
- **任务状态**: 异步任务执行状态查询

### 2. 测试框架
- **多环境支持**: dev/test/staging/prod
- **并行执行**: 支持多进程并行测试
- **测试标记**: 支持优先级、类型、环境标记
- **失败重试**: 支持失败用例自动重试
- **超时控制**: 支持测试用例超时设置

### 3. 数据管理
- **配置驱动**: YAML 配置文件管理
- **数据库操作**: 完整的 MySQL 操作封装
- **数据工厂**: 测试数据自动生成
- **缓存机制**: 测试数据缓存优化

### 4. 报告系统
- **Allure 报告**: 交互式测试报告
- **HTML 报告**: 静态 HTML 报告
- **JUnit 报告**: CI/CD 集成支持
- **钉钉通知**: 测试结果自动通知

## 快速开始

### 环境准备
1. **安装 Python 3.8+**
   ```bash
   python --version
   ```

2. **安装项目依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 Allure**
   ```bash
   # macOS
   brew install allure
   
   # Windows
   scoop install allure
   ```

### 本地开发
1. **启动 Web 服务**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **访问 API 文档**
   ```
   http://localhost:8000/docs
   ```

### Docker 部署
1. **构建镜像**
   ```bash
   docker build -t erp-autotest .
   ```

2. **运行容器**
   ```bash
   docker run -p 8000:8000 erp-autotest
   ```

## 配置管理

### 环境配置
项目支持多环境配置，配置文件位于 `config/env/` 目录：

```yaml
# config/env/test.yaml
environment: test
base_url: https://test-api.example.com
database:
  host: test-db.example.com
  port: 3306
  database: erp_test
  username: test_user
  password: test_pass
```

### 项目配置
支持多项目配置，配置文件位于 `config/{project}/` 目录：

```yaml
# config/erp/base_init_sql.yaml
base_info:
  currency_info:
    sql: SELECT id as curr_id, curr_code, curr_name FROM gen_curr_type_cf WHERE curr_code='CNY'
    validation:
      min_records: 1
      required_fields: ["curr_id", "curr_code", "curr_name"]
```

## 测试执行

### 命令行执行
```bash
# 运行所有测试
pytest testcases/ -v

# 运行指定模块
pytest testcases/scm_sls/ -v

# 运行指定文件
pytest testcases/scm_sls/so/test_so_create.py -v

# 并行执行
pytest testcases/ -n 4

# 指定环境
pytest testcases/ --env=test

# 生成 Allure 报告
pytest testcases/ --alluredir=./reports/allure-results
allure generate ./reports/allure-results -o ./reports/allure-report --clean
```

### API 执行
```bash
# 执行所有测试
curl -X POST "http://localhost:8000/executor/run" \
  -H "Content-Type: application/json" \
  -d '{"type": "all", "env": "test", "workers": 4}'

# 执行指定模块
curl -X POST "http://localhost:8000/executor/run" \
  -H "Content-Type: application/json" \
  -d '{"type": "module", "module": "scm_sls", "env": "test"}'

# 查询任务状态
curl "http://localhost:8000/executor/status/{task_id}"
```

## 测试用例编写

### 基础测试类结构

所有测试类必须继承对应的基类：
- **通用基类**: `BaseTest` (位于 `testcases.comm.base_test`)
- **主数据模块**: `GenMdBaseTest` (继承 `BaseTest`)
- **财务模块**: `FinBaseTest`、`ApBaseTest`、`ArBaseTest` (继承 `BaseTest`)
- **销售模块**: `SlsBaseTest` (继承 `BaseTest`)

### 标准测试类模板

```python
import allure
import pytest
from testcases.{module} import {Module}BaseTest
from utils.report_util import a, case_decorator

@allure.epic("模块名称")
@allure.feature("功能模块")
class Test{Module}Management({Module}BaseTest):
    """模块管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.{module}_id = None
        cls.logger.info("{模块}管理测试类初始化完成")
        
        # 初始化配置数据（从init_data获取）
        if cls.init_data:
            cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
            cls.coun_id = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        
        # 初始化MD数据（从md_cache_data获取主数据）
        if cls.md_cache_data:
            cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])
            cls.cust_id = cust_info[0].get("id") if cust_info else None
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="{table_name}", where="{code_field} like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
```

### 标准测试方法模板（推荐使用 standard_api_call）

```python
@case_decorator(
    story="业务故事",
    title="测试{功能}",
    description="验证{具体功能}",
    severity="critical",
    file_level_order=1,  # 使用文件级排序，确保文件内串行执行
    smoke=True,  # 可选
    tags=["{模块}", "{功能}"]
)
def test_save_{object}(self):
    """测试方法说明"""
    try:
        # 1. 准备测试数据
        {object}_code = self.mock_util.generate_unique_code(tag="AT")
        {object}_name = f"{对象名称}_{self.mock_util.get_timestamp()}"
        
        # 2. 使用标准化API调用（推荐方式）
        set_dict = {
            "{field1}": value1,
            "{field2}": value2
        }
        fields_to_filter = ["{field1}", "{field2}"]
        
        response, extracted_id = self.standard_api_call(
            api_key="{API服务名称}",
            set_dict=set_dict,
            fields_to_filter=fields_to_filter,
            store_id_as="{object}"  # 可选：自动存储为 self.{object}_id
        )
        
        # 3. 业务断言（standard_api_call不包含断言）
        self.assert_util.assert_response_data(response)
        
        # 4. 保存数据（如果store_id_as未设置）
        if not hasattr(self, '{object}_id'):
            self.{object}_id = extracted_id
        
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

### standard_api_call 方法详解

`standard_api_call` 是统一的标准API调用方法，自动处理参数过滤、设置、请求发送和日志记录。

**方法签名**:
```python
def standard_api_call(
    self, 
    api_key,                    # API服务名称键（必填）
    set_dict=None,              # 要设置的参数字典（可选）
    fields_to_filter=None,      # 需要过滤的字段列表（可选）
    store_id_as=None,           # ID存储属性名，如"partner"会存储为self.partner_id（可选）
    use_param_util=True,        # 是否使用ParamUtil过滤/设置，默认True（可选）
    param_path=None             # 参数路径，默认为["params", "request"]（可选）
) -> tuple[dict, Any]:          # 返回(response, extracted_id)
```

**使用示例**:
```python
# 示例1：创建接口（自动存储ID）
response, id = self.standard_api_call(
    api_key="GEN-币种配置-保存服务",
    set_dict={"currCode": "USD", "currName": "美元"},
    fields_to_filter=["currCode", "currName"],
    store_id_as="currency"  # 自动存储为 self.currency_id
)
self.assert_util.assert_response_data(response)

# 示例2：查询接口
response, _ = self.standard_api_call(
    api_key="GEN-币种配置-查询分页服务",
    set_dict={
        "pageable": {"pageNo": 1, "pageSize": 20},
        "fields": [{"name": "currCode", "type": "TEXT"}]
    },
    fields_to_filter=["pageable", "fields"]
)

# 示例3：复杂参数（使用use_param_util=False）
params = {
    "serviceKey": "{SERVICE_KEY}",
    "params": {
        "taskName": f"任务名称",
        "config": {...}
    }
}
response = self.http.post(url, json=params)
```

### 数据获取模式

#### 基础数据获取（init_data）
`init_data` 在 `BaseTest.setup_class()` 中通过 `initializer.initialize_base_data()` 初始化，包含基础配置数据（币种、国家、地址、银行等）。

**安全获取方式**:
```python
if cls.init_data:
    cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
    cls.coun_id = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
    cls.addr_id = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
    cls.bank_id = cls.init_data["bank_info"][0]["bank_id"] if cls.init_data.get("bank_info") else None
```

#### 主数据获取（md_cache_data）
`md_cache_data` 在 `GenMdBaseTest.setup_class()` 中通过 `CacheUtil.get('md_init_cache')` 获取，包含主数据（合作伙伴、组织、物料等）。

**安全获取方式**:
```python
if cls.md_cache_data:
    # 合作伙伴信息
    cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])
    cls.cust_id = cust_info[0].get("id") if cust_info else None
    
    # 组织信息
    gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
    cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
    
    # 物料信息
    mat_md = cls.md_cache_data.get("mat_info", {}).get("mat_md", {})
    finp_list = mat_md.get("FINP", [])
    cls.mat_id = finp_list[0].get("id") if finp_list else None
```

### 执行顺序控制

使用 `case_decorator` 的 `file_level_order` 参数控制文件内执行顺序，**禁止使用** `@pytest.mark.run(file_level_order=N)`。

**执行顺序规范**:
- 创建(1-3) < 查询(4-6) < 更新(7-9) < 导出(10-12) < 导入(13-15) < 删除(16-18)

```python
@case_decorator(
    story="业务故事",
    title="测试创建",
    file_level_order=1,  # 创建操作
    severity="critical"
)
def test_save_xxx(self):
    pass

@case_decorator(
    story="业务故事",
    title="测试查询",
    file_level_order=4,  # 查询操作
    severity="critical"
)
def test_query_xxx(self):
    pass
```

### 数据驱动测试
```python
@pytest.mark.parametrize("iv_type, title", [
    ("PERIOD_METHOD", "测试期间成本法"),
    ("CONTINUOUS_METHOD", "测试永续成本法")
])
@case_decorator(
    story="业务故事",
    title="测试初始化配置",
    file_level_order=1,
    severity="critical"
)
def test_initialize_configuration(self, iv_type, title):
    """测试初始化配置"""
    import allure
    allure.dynamic.title(title)  # 动态设置测试标题
    
    try:
        # 测试实现
        pass
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

## 工具类使用

### 数据生成（Mock工具）
**统一使用 `self.mock_util`**（从BaseTest继承），禁止使用 `cls.mock_data = MockData()`。

```python
# 在测试方法中使用
code = self.mock_util.generate_unique_code(tag="AT")
timestamp = self.mock_util.get_timestamp()
name = self.mock_util.get_mock_name()
company = self.mock_util.get_mock_company()
phone = self.mock_util.get_mock_phone_number()
date = self.mock_util.get_mock_date(include_time=False, days_offset=0)
```

### 断言验证
```python
# 标准断言
self.assert_util.assert_response_success(response)    # 成功响应
self.assert_util.assert_response_data(response)       # 数据响应
self.assert_util.assert_by_operator(actual, "=", expected)  # 自定义断言
self.assert_util.assert_all_in(required, actual, "错误信息")  # 包含验证
```

### 报告记录
```python
from utils.report_util import a

a.json(data, "数据说明")
a.text(message, "文本说明")
self.logger.info(f"关键信息: {info}")
```

### HTTP 请求
在测试类中，HTTP客户端已通过基类初始化，直接使用 `self.http`：

```python
# 在测试方法中使用
response = self.http.post(url, json=params)
response = self.http.get(url, params=query_params)
```

### 数据库操作
在测试类中，数据库连接已通过基类初始化，直接使用 `self.db`：

```python
# 查询数据（使用参数化查询，避免SQL注入）
sql = "SELECT org_status FROM org_struct_md WHERE id = %s LIMIT 1"
result = self.db.query(sql, (org_id_value,))  # 参数必须是元组或列表

# 删除数据
self.db.delete(
    table="table_name",
    where="code like %s",
    params=["AT_%"]
)

# 插入数据
self.db.insert(table="table_name", data={"code": "AT_001", "name": "测试"})
```

### 配置管理
```python
from utils.yaml_util import YamlUtil

# 读取配置文件
config = YamlUtil.read_yaml("env/test.yaml")

# 读取项目配置
erp_config = YamlUtil.get_project_config("erp", "base_init_sql.yaml")
```

## 报告查看

### Allure 报告
```bash
# 生成报告
allure generate ./reports/allure-results -o ./reports/allure-report --clean

# 查看报告
allure open ./reports/allure-report

# Web 服务查看
http://localhost:8000/allure/
```

### 报告特性
- **交互式界面**: 支持测试用例详情查看
- **历史对比**: 支持多版本测试结果对比
- **失败分析**: 详细的失败原因分析
- **性能统计**: 测试执行时间统计
- **趋势分析**: 测试结果趋势图表

## 持续集成

### Erda 平台集成
项目已配置 Erda 平台 CI/CD 流水线：

1. **代码检出**: 从 Git 仓库检出代码
2. **镜像构建**: 使用 Dockerfile 构建镜像
3. **应用部署**: 部署到 Erda 平台
4. **API 测试**: 执行自动化测试

### 流水线配置
- **pipeline.yml**: CI/CD 流水线定义
- **dice.yml**: Erda 平台部署配置
- **Dockerfile**: 容器镜像构建配置

## 监控和通知

### 钉钉通知
项目集成了钉钉机器人通知功能：
- 测试执行完成通知
- 失败用例详情推送
- 测试报告链接分享

### 日志监控
- **结构化日志**: JSON 格式日志输出
- **日志轮转**: 按日期自动轮转
- **日志级别**: DEBUG/INFO/WARNING/ERROR
- **日志存储**: 本地文件存储

## 最佳实践

### 测试用例编写规范

#### 必须遵循的规则
1. **优先使用standard_api_call**: 新代码必须使用`standard_api_call`方法，除非有特殊需求
2. **异常处理**: 所有测试方法必须有try-catch
3. **数据清理**: teardown_class必须清理测试数据，**禁止用循环遍历表名**，必须一个表一个表地单独调用
4. **执行顺序**: 统一使用 `case_decorator` 的 `file_level_order` 参数，禁止使用 `@pytest.mark.run(file_level_order=N)`
5. **唯一标识**: 所有测试数据使用"AT_"前缀避免冲突
6. **Mock工具**: 统一使用`self.mock_util`（从BaseTest继承），禁止使用`cls.mock_data = MockData()`
7. **业务断言**: `standard_api_call`不包含断言，必须在调用后手动添加业务断言
8. **数据获取**: 从 `init_data` 和 `md_cache_data` 获取，禁止写死参数

#### 命名规范
- **测试类**: `Test{Module}Management` (如 `TestMatCateManagement`)
- **测试方法**: `test_{action}_{object}` (如 `test_save_mat_type`)
- **文件名**: `test_{module}_management.py`
- **变量**: snake_case，常量：UPPER_CASE

#### 数据清理规范
```python
@classmethod
def teardown_class(cls):
    """测试类结束后执行清理"""
    try:
        # 禁止用循环遍历表名，必须一个表一个表地单独调用
        cls.db.delete(table="table1", where="code like %s", params=["AT_%"])
        cls.db.delete(table="table2", where="code like %s", params=["AT_%"])
        cls.logger.info("测试数据清理完成")
    except Exception as e:
        cls.logger.error(f"测试数据清理失败: {str(e)}")
```

#### 跳过测试规范
```python
# 标准文件导入导出
@pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")

# OSS操作
@pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")

# 业务未引用
@pytest.mark.skip(reason="业务未引用，暂时跳过")

# 功能未实现
@pytest.mark.skip(reason="功能未实现")
```

### 配置管理
1. **环境隔离**: 不同环境使用不同配置文件
2. **敏感信息**: 密码等敏感信息使用环境变量
3. **版本控制**: 配置文件纳入版本控制
4. **配置验证**: 启动时验证配置有效性

### 性能优化
1. **并行执行**: 使用 pytest-xdist 并行执行
2. **数据缓存**: 使用缓存减少重复数据查询（init_cache.json, md_init_cache.json）
3. **连接池**: 数据库连接使用连接池
4. **资源清理**: 及时释放测试资源

## 常见问题

### 1. 测试执行失败
- 检查网络连接和 API 状态
- 验证测试数据是否正确
- 查看详细错误日志
- 确认环境配置正确

### 2. 数据库连接问题
- 检查数据库服务状态
- 验证连接参数配置
- 确认数据库权限设置
- 查看数据库连接日志

### 3. 报告生成失败
- 确认 Allure 工具安装正确
- 检查报告目录权限
- 验证测试结果数据完整性
- 查看 Allure 执行日志

### 4. 环境配置问题
- 检查配置文件格式
- 验证环境变量设置
- 确认配置文件路径正确
- 查看配置加载日志

### 5. standard_api_call 使用问题
- 确认API服务名称键是否正确（检查 `testdata/{module}/api_path.yaml`）
- 验证 `fields_to_filter` 参数是否包含所有需要设置的字段
- 检查 `set_dict` 中的字段名是否与API定义一致
- 查看日志中的请求参数和响应数据

### 6. 数据获取问题
- 确认 `init_data` 或 `md_cache_data` 是否正确初始化
- 使用安全的数据获取方式（先判断列表是否存在且非空）
- 检查缓存文件（`testdata/cache/init_cache.json`）是否存在且有效

## 版本历史

### v1.0.0 (当前版本)
- ✅ 完整的 ERP 自动化测试框架
- ✅ FastAPI Web 服务集成
- ✅ Allure 报告系统
- ✅ 多环境配置支持
- ✅ 并行测试执行
- ✅ 数据工厂功能
- ✅ 钉钉通知集成
- ✅ Docker 容器化支持
- ✅ Erda 平台 CI/CD 集成
- ✅ standard_api_call 标准化API调用方法
- ✅ 数据缓存机制（init_data, md_cache_data）
- ✅ 完整的测试用例编写规范
- ✅ 支持多模块测试（主数据、财务、销售、采购、库存等）

## 贡献指南

1. **Fork 项目**
2. **创建特性分支**: `git checkout -b feature/new-feature`
3. **提交更改**: `git commit -am 'Add new feature'`
4. **推送分支**: `git push origin feature/new-feature`
5. **创建 Pull Request**

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用类型注解
- 编写完整的文档字符串
- 添加必要的单元测试
- 遵循 KISS 原则和 SOLID 原则
- 字典取值优先使用 `.get()`，取不到key默认为None
- 路径获取统一用 `pathlib` 的 `Path` 获取

### 测试规范
- 测试用例命名清晰明确（`test_{action}_{object}`）
- 使用数据驱动测试（`@pytest.mark.parametrize`）
- 合理使用测试标记（`@case_decorator`）
- 确保测试用例独立性
- 优先使用 `standard_api_call` 方法
- 所有测试方法必须有异常处理（try-catch）
- 测试类必须有数据清理（teardown_class）
- 使用 `file_level_order` 控制执行顺序

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

- **项目维护者**: ERP 测试团队
- **技术支持**: 内部技术支持
- **问题反馈**: 通过 Git 仓库 Issues 反馈

---

**注意**: 本项目为内部 ERP 系统自动化测试平台，请确保在授权环境下使用。 