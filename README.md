# ERP 自动化测试项目

## 项目简介
本项目是一个基于 Python 的 ERP 系统自动化测试框架

## 技术栈
- Python 3.8+
- pytest
- Allure
- requests
- loguru
- Faker

## 项目结构
```
erp-autoest/
├── config/                # 配置文件目录
│   ├── api/              # API 配置目录
│   └── env/              # 环境配置目录
│       ├── base.yaml     # 基础配置
│       └── test.yaml     # 测试环境配置
├── docs/                  # 文档目录
│   ├── test_case_guidelines.md  # 测试用例编写指南
│   └── getting_started.md      # 新手指南
├── reports/              # 测试报告目录
│   ├── allure-results/   # Allure 报告数据
│   ├── allure-report/    # Allure 报告
│   ├── html/            # HTML 报告
│   └── junit/           # JUnit 报告
├── testcases/           # 测试用例目录
│   └── SCM/            # 模块测试目录
│       └── SO/        # 销售订单测试目录
├── utils/              # 工具类目录
├── pytest.ini         # pytest 配置
└── run_test.sh        # 测试执行脚本
```

## 环境准备
1. 安装 Python 3.8+
   ```bash
   # 验证 Python 版本
   python --version
   ```

2. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装 Allure：
   ```bash
   # macOS
   brew install allure
   
   # Windows
   scoop install allure
   ```

## 配置管理
项目使用 YAML 格式的配置文件进行配置管理，配置文件位于 `config/env` 目录下：

### 配置文件说明
1. `base.yaml` - 基础配置
   - API 配置（版本、超时、重试次数）
   - 日志配置（路径、级别、格式）
   - 报告配置（Allure、HTML、JUnit）
   - 性能监控配置
   - 测试数据默认配置
   - 超时配置

2. `test.yaml` - 测试环境配置
   - 环境标识
   - 基础 URL 配置
   - 认证配置（用户名、密码）
   - 数据库配置
   - 测试数据配置
   - 安全配置

### 配置加载机制
1. 基础配置（`base.yaml`）会被首先加载
2. 环境特定配置（如 `test.yaml`）会覆盖基础配置中的相同项
3. 配置项支持层级结构，使用点号（.）访问，如 `base.api.timeout`

### 配置使用示例
```python
from utils.config_loader import ConfigLoader

# 加载配置
config = ConfigLoader().load()

# 获取配置项
api_timeout = config.get('base.api.timeout')
db_host = config.get('database.erp_db.host')
```

### 配置注意事项
1. 敏感信息（如密码）已在配置文件中加密存储
2. 不要直接修改配置文件，使用配置管理工具
3. 添加新配置时，需要同时更新基础配置和对应环境配置
4. 配置变更需要经过评审和测试

## 测试执行
1. 运行单个测试用例：
   ```bash
   pytest testcases/SCM/SO/test_01_create.py -v
   ```

2. 运行整个模块测试：
   ```bash
   pytest testcases/SCM/SO -v
   ```

3. 运行测试并生成 Allure 报告：
   ```bash
   # 运行测试并收集结果
   pytest tests/ -v --alluredir=./reports/allure-results --clean-alluredir
   
   # 生成 Allure 报告
   allure generate ./reports/allure-results -o ./reports/allure-report --clean
   
   # 打开报告
   allure open ./reports/allure-report
   ```

4. 使用集成脚本运行测试：
   ```bash
   ./run_test.sh
   ```

## 测试报告
测试执行完成后，会生成多种格式的报告：

1. Allure 报告
   - 位置：`reports/allure-report/`
   - 特点：交互式界面，支持历史记录对比
   - 查看方式：`allure open reports/allure-report`

2. HTML 报告
   - 位置：`reports/html/report.html`
   - 特点：独立文件，方便分享

3. JUnit 报告
   - 位置：`reports/junit/junit.xml`
   - 特点：标准格式，支持 CI/CD 集成

## 测试用例说明
### 销售订单创建测试
- 测试文件：`testcases/SCM/SO/test_01_create.py`
- 主要测试点：
  - 销售订单初始化
  - 客户信息查询
  - 相关方查询
  - 销售组织查询
  - 物料查询
  - 订单行渲染
  - 自动定价
  - 订单保存
  - 订单提交

## 日志记录
- 使用 loguru 进行日志记录
- 日志级别：DEBUG, INFO, WARNING, ERROR
- 日志文件位置：`logs/`
- 日志格式：`%(asctime)s [%(levelname)s] %(message)s`

## 注意事项
1. 运行测试前确保环境配置正确
2. 检查配置文件中的接口地址是否正确
3. 确保测试数据准备充分
4. 注意测试用例之间的依赖关系
5. 环境变量文件 (.env) 不要提交到版本控制系统

## 常见问题
1. 测试失败时，查看日志和报告获取详细信息
2. 检查网络连接和接口状态
3. 确认测试数据是否有效
4. 环境变量未设置时，检查 .env 文件配置

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 遵循测试用例编写规范
5. 确保测试用例通过
6. 提交 Pull Request

## 版本历史
- v1.0.0: 初始版本
  - 实现销售订单创建流程测试
  - 集成 Allure 报告
  - 添加日志记录功能 