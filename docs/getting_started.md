# ERP-SAAS系统测试用例编写新手指南

## 1. 环境准备

### 1.1 开发环境配置
1. 安装 Python 3.8+
```bash
# 验证 Python 版本
python --version
# 预期输出：Python 3.8.x 或更高版本
```

2. 安装依赖包
```bash
pip install -r requirements.txt

# 验证依赖包安装
pip list
# 预期输出：显示所有已安装的包，确认所需包都已安装
```

### 1.2 环境变量配置
1. 复制环境变量模板
```bash
cp .env.template .env

# 验证文件是否创建成功
ls -la .env
# 预期输出：显示 .env 文件信息
```

2. 编辑 `.env` 文件，填写必要的环境变量
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=erp_db

# API配置
BASE_URL=http://api.example.com
IAM_URL=http://iam.example.com

# 认证配置
AUTH_USERNAME=your_username
AUTH_PASSWORD=your_password

# 日志配置
LOG_LEVEL=INFO

# 验证环境变量是否生效
python -c "import os; print(os.getenv('DB_HOST'))"
# 预期输出：localhost
```

## 2. 项目结构说明

```
erp-autoest/
├── tests/                  # 测试代码目录
│   ├── testcases/         # 测试用例目录
│   │   └── SCM/          # 模块测试目录
│   │       └── SO/      # 子模块测试目录
│   └── conftest.py       # pytest 配置文件
├── utils/                 # 工具类目录
├── config/               # 配置文件目录
├── docs/                # 文档目录
└── reports/            # 测试报告目录

# 验证项目结构
ls -R
# 预期输出：显示完整的项目目录结构
```

## 3. 编写第一个测试用例

### 3.1 创建测试文件
1. 在 `tests/testcases/SCM/SO/` 目录下创建测试文件
```bash
touch test_so_create.py

# 验证文件是否创建成功
ls -l tests/testcases/SCM/SO/test_so_create.py
# 预期输出：显示文件信息
```

2. 编写测试用例
```python
import pytest
from utils.HttpUtil import HttpUtil
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers

class TestSOCreate:
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
        self.http = HttpUtil()
        self.assert_helper = AssertHelper()
        self.logger = Loggers()
        yield
        # 测试后清理

    def test_create_so_success(self):
        """创建销售订单成功测试
        
        测试场景：
        1. 准备有效的订单数据
        2. 调用创建订单API
        3. 验证订单创建成功
        """
        # 1. 准备测试数据
        order_data = {
            "customer_id": "CUST001",
            "items": [
                {"product_id": "PROD001", "quantity": 2},
                {"product_id": "PROD002", "quantity": 1}
            ]
        }
        self.logger.info(f"准备测试数据: {order_data}")
        
        # 2. 执行测试
        response = self.http.post('/api/v1/sales/orders', json=order_data)
        
        # 3. 验证结果
        self.assert_helper.assert_http_status(response, 200)
        result = response.json()
        self.assert_helper.assert_response_status(result)
        self.assert_helper.assert_fields_exist(
            result["data"],
            ["order_no", "status", "total_amount"],
            {"order_no": "订单编号", "status": "订单状态", "total_amount": "订单总额"}
        )
        
        self.logger.info("测试通过：订单创建成功")

# 验证代码格式
ruff check test_so_create.py
# 预期输出：无错误信息
```

### 3.2 运行测试
```bash
# 运行单个测试文件
pytest tests/testcases/SCM/SO/test_so_create.py

# 验证测试结果
# 预期输出：
# ============================= test session starts ==============================
# collected 1 item
# test_so_create.py .                                                      [100%]
# ============================== 1 passed in 0.xxs ==============================

# 运行特定测试用例
pytest tests/testcases/SCM/SO/test_so_create.py::TestSOCreate::test_create_so_success

# 验证测试结果
# 预期输出：同上

# 运行带标记的测试用例
pytest -m smoke

# 验证测试结果
# 预期输出：显示所有标记为 smoke 的测试用例结果
```

## 4. 常用工具类说明

### 4.1 HttpUtil
用于发送 HTTP 请求
```python
from utils.HttpUtil import HttpUtil

http = HttpUtil()
response = http.get('/api/v1/endpoint')
response = http.post('/api/v1/endpoint', json=data)

# 验证工具类是否可用
print(response.status_code)
# 预期输出：200
```

### 4.2 AssertHelper
用于验证测试结果
```python
from utils.AssertUtil import AssertHelper

assert_helper = AssertHelper()
assert_helper.assert_http_status(response, 200)
assert_helper.assert_response_status(result)
assert_helper.assert_fields_exist(data, fields, field_descriptions)

# 验证断言是否生效
# 预期结果：无异常抛出
```

### 4.3 Loggers
用于记录日志
```python
from utils.LogUtil import Loggers

logger = Loggers()
logger.info("信息日志")
logger.error("错误日志")

# 验证日志是否记录
# 预期结果：在日志文件中看到相应的日志记录
```

### 4.4 MysqlUtil
用于数据库操作
```python
from utils.MysqlUtil import MysqlUtil

mysql = MysqlUtil()
result = mysql.query("SELECT * FROM table WHERE id = %s", (id,))
mysql.execute("UPDATE table SET status = %s WHERE id = %s", (status, id))

# 验证数据库连接
print(mysql.is_connected())
# 预期输出：True
```

## 5. 测试用例编写规范

### 5.1 命名规范
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

# 验证命名规范
ls tests/testcases/SCM/SO/
# 预期输出：所有文件都以 test_ 开头

### 5.2 结构规范
1. 导入必要的模块
2. 定义测试类
3. 编写 setup 方法
4. 编写测试方法
5. 编写清理方法

# 验证结构规范
pytest --fixtures test_so_create.py
# 预期输出：显示所有 fixture 定义

### 5.3 文档规范
- 每个测试方法都需要有文档字符串
- 文档字符串应包含测试场景说明
- 关键步骤需要添加注释

# 验证文档规范
pytest --doc test_so_create.py
# 预期输出：显示所有测试方法的文档字符串

## 6. 常见问题解决

### 6.1 环境变量未设置
错误信息：`Missing required environment variable: DB_HOST`
解决方案：检查 `.env` 文件是否已正确配置

# 验证环境变量
python -c "import os; print(os.getenv('DB_HOST'))"
# 预期输出：显示正确的数据库主机地址

### 6.2 数据库连接失败
错误信息：`Can't connect to MySQL server`
解决方案：检查数据库配置是否正确，数据库服务是否启动

# 验证数据库连接
python -c "from utils.MysqlUtil import MysqlUtil; print(MysqlUtil().is_connected())"
# 预期输出：True

### 6.3 API 请求失败
错误信息：`Connection refused`
解决方案：检查 API 服务是否启动，BASE_URL 配置是否正确

# 验证 API 连接
python -c "from utils.HttpUtil import HttpUtil; print(HttpUtil().get('/api/v1/health').status_code)"
# 预期输出：200

## 7. 进阶指南

### 7.1 数据清理
```python
from utils.CleanupUtil import CleanupManager

class TestModuleName:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.cleanup_manager = CleanupManager()
        yield
        self.cleanup_test_data()
        
    def cleanup_test_data(self):
        self.cleanup_manager.cleanup_module('sales', {
            'order_nos': ['SO001', 'SO002']
        })

# 验证数据清理
# 预期结果：测试数据被成功清理
```

### 7.2 参数化测试
```python
@pytest.mark.parametrize("test_data,expected", [
    ({"quantity": 1}, "success"),
    ({"quantity": 0}, "error"),
])
def test_create_so_with_different_quantity(self, test_data, expected):
    # 测试代码

# 验证参数化测试
pytest -v test_so_create.py
# 预期输出：显示所有参数化测试用例的结果
```

### 7.3 测试标记
```python
@pytest.mark.smoke
@pytest.mark.p0
def test_important_feature(self):
    # 测试代码

# 验证测试标记
pytest -m smoke -v
# 预期输出：显示所有标记为 smoke 的测试用例
```

## 8. 获取帮助

1. 查看文档
   - 测试用例指南：`docs/test_case_guidelines.md`
   - 工具类文档：`docs/utils/`
