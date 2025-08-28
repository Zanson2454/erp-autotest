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
│   ├── scm_sls/            # 销售管理测试
│   ├── scm_pur/            # 采购管理测试
│   ├── prd/                # 生产管理测试
│   ├── fin/                # 财务管理测试
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
│       └── sls_init_sql.yaml     # 销售管理初始化 SQL
├── static/                  # 静态资源
├── reports/                 # 测试报告目录
│   ├── allure-results/     # Allure 结果数据
│   ├── allure-report/      # Allure 报告
│   ├── html/              # HTML 报告
│   └── junit/             # JUnit 报告
├── logs/                   # 日志文件目录
├── testdata/               # 测试数据目录
├── data_factory/           # 数据工厂目录
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

### 基础测试类
```python
from testcases.scm_sls import SlsBase
from utils.report_util import case_decorator
import allure

@allure.epic("销售管理")
@allure.feature("销售订单管理")
class TestSalesOrder(SlsBase):
    
    @case_decorator(
        story="销售订单",
        title="创建销售订单",
        description="验证销售订单创建功能",
        severity="critical",
        order=1,
        tags=["销售订单", "创建"]
    )
    def test_create_sales_order(self):
        """创建销售订单测试"""
        # 测试实现
        pass
```

### 数据驱动测试
```python
@pytest.mark.parametrize("order_type", ["STND", "THRD", "CENT"])
def test_order_types(self, order_type):
    """测试不同订单类型"""
    # 测试实现
    pass
```

## 工具类使用

### HTTP 请求
```python
from utils.request_util import HttpUtil

http = HttpUtil("https://api.example.com")
response = http.post("/api/orders", json={"order_id": "123"})
```

### 数据库操作
```python
from utils.mysql_util import DBManager

# 类方法模式
DBManager.init(config)
result = DBManager.query("SELECT * FROM orders")

# 实例模式
db = DBManager(host="localhost", database="test", user="root", password="pass")
result = db.query("SELECT * FROM orders")
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

### 测试用例编写
1. **命名规范**: 使用描述性的测试方法名
2. **数据准备**: 使用数据工厂生成测试数据
3. **断言验证**: 使用专门的断言工具类
4. **异常处理**: 合理处理测试异常情况
5. **清理资源**: 测试完成后清理测试数据

### 配置管理
1. **环境隔离**: 不同环境使用不同配置文件
2. **敏感信息**: 密码等敏感信息使用环境变量
3. **版本控制**: 配置文件纳入版本控制
4. **配置验证**: 启动时验证配置有效性

### 性能优化
1. **并行执行**: 使用 pytest-xdist 并行执行
2. **数据缓存**: 使用缓存减少重复数据查询
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

### 测试规范
- 测试用例命名清晰明确
- 使用数据驱动测试
- 合理使用测试标记
- 确保测试用例独立性

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

- **项目维护者**: ERP 测试团队
- **技术支持**: 内部技术支持
- **问题反馈**: 通过 Git 仓库 Issues 反馈

---

**注意**: 本项目为内部 ERP 系统自动化测试平台，请确保在授权环境下使用。 