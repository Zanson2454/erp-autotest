# ERP-SAAS系统测试用例编写规范

## 1. 文档说明

本文档旨在规范ERP-SAAS系统自动化测试用例的编写，确保测试用例的可维护性、可读性和可复用性。

## 2. 测试用例命名规范

### 2.1 文件命名
- 测试文件必须以 `test_` 开头
- 文件名应清晰表达测试模块和功能
- 示例：
  - `test_so_create.py` - 销售订单创建测试
  - `test_so_approve.py` - 销售订单审批测试

### 2.2 测试类命名
- 测试类名应以 `Test` 结尾
- 类名应清晰表达测试场景
- 示例：
  - `class TestSOCreate`
  - `class TestSOApprove`

### 2.3 测试方法命名
- 测试方法必须以 `test_` 开头
- 方法名应清晰表达测试场景和预期结果
- 命名格式：`test_<场景>_<预期结果>`
- 示例：
  - `test_create_so_success`
  - `test_create_so_with_invalid_data`

## 3. 测试用例结构规范

### 3.1 基本结构
```python
import pytest
from utils.HttpUtil import HttpUtil
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers

class TestModuleName:
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
        self.http = HttpUtil()
        self.assert_helper = AssertHelper()
        self.logger = Loggers()
        yield
        # 测试后清理

    def test_scenario_expected_result(self):
        """测试场景描述
        
        Args:
            param1: 参数说明
            param2: 参数说明
            
        Returns:
            返回值说明
        """
        # 1. 准备测试数据
        test_data = {
            "field1": "value1",
            "field2": "value2"
        }
        self.logger.info(f"准备测试数据: {test_data}")
        
        # 2. 执行测试步骤
        response = self.http.post('/api/endpoint', json=test_data)
        
        # 3. 验证结果
        self.assert_helper.assert_http_status(response, 200)
        response_data = response.json()
        self.assert_helper.assert_response_status(response_data)
        self.assert_helper.assert_fields_exist(
            response_data["data"],
            ["id", "status", "created_at"],
            {"id": "记录ID", "status": "状态", "created_at": "创建时间"}
        )
        
        self.logger.info("测试通过：操作成功")

### 3.2 测试用例组成
1. **文档字符串**：清晰描述测试目的、参数和返回值
2. **测试数据准备**：使用数据生成器准备测试数据
3. **测试步骤**：按顺序执行测试步骤
4. **结果验证**：使用断言验证测试结果

## 4. 测试数据管理

### 4.1 数据生成
- 使用 `faker` 库生成随机测试数据
- 关键业务数据应使用固定值
- 敏感数据应使用环境变量或配置文件

### 4.2 数据清理
- 测试完成后必须清理测试数据
- 使用 `CleanupManager` 进行数据清理
- 支持按模块清理和全局清理
- 支持事务和错误处理
- 示例：
  ```python
  from utils.CleanupUtil import CleanupManager
  
  class TestModuleName:
      @pytest.fixture(autouse=True)
      def setup(self):
          """测试前置条件"""
          self.cleanup_manager = CleanupManager()
          yield
          # 测试后清理
          self.cleanup_test_data()
          
      def cleanup_test_data(self):
          """清理测试数据"""
          # 按模块清理
          self.cleanup_manager.cleanup_module('sales', {
              'order_nos': ['SO001', 'SO002']
          })
          
          # 或者清理所有模块
          self.cleanup_manager.cleanup_all({
              'order_nos': ['SO001', 'SO002'],
              'po_nos': ['PO001', 'PO002'],
              'transaction_nos': ['TR001', 'TR002']
          })
  ```

### 4.3 数据清理配置
- 清理配置位于 `data/cleanup/cleanup.yaml`
- 按模块组织清理脚本
- 支持参数化 SQL
- 支持依赖关系管理
- 支持事务和错误处理配置
- 示例配置：
  ```yaml
  modules:
    sales:
      description: "销售模块数据清理"
      tables:
        - name: "sales_orders"
          sql: "DELETE FROM sales_orders WHERE order_no IN (%(order_nos)s)"
          params:
            order_nos: "{{ order_nos }}"
          dependencies: ["sales_order_items"]
  config:
    transaction: true
    error_handling: "rollback"
    logging: true
    dry_run: false
  ```

## 5. 测试用例标记

### 5.1 测试级别标记
- `@pytest.mark.smoke` - 冒烟测试
- `@pytest.mark.regression` - 回归测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.database` - 数据库测试

### 5.2 测试优先级标记
- `@pytest.mark.p0` - 最高优先级
- `@pytest.mark.p1` - 高优先级
- `@pytest.mark.p2` - 中优先级
- `@pytest.mark.p3` - 低优先级

## 6. 断言规范

### 6.1 基本断言
- 使用 `assert` 语句进行断言
- 断言消息应清晰表达预期结果
- 示例：
  ```python
  assert response.status_code == 200, "API请求失败"
  assert result['status'] == 'success', "业务状态不正确"
  ```

### 6.2 数据验证
- 验证必要字段的存在性
- 验证字段值的正确性
- 验证数据类型的正确性

## 7. 错误处理

### 7.1 异常处理
- 使用 `try-except` 处理预期异常
- 记录详细的错误信息
- 示例：
  ```python
  try:
      response = self.api.post('/endpoint', data=test_data)
  except Exception as e:
      logger.error(f"API请求失败: {str(e)}")
      raise
  ```

### 7.2 日志记录
- 使用 `loguru` 记录关键操作
- 记录测试步骤和结果
- 记录错误和异常信息

## 8. 测试用例维护

### 8.1 代码审查
- 提交前进行代码审查
- 确保符合编码规范
- 确保测试用例的可维护性

### 8.2 版本控制
- 使用有意义的提交信息
- 关联需求或问题编号
- 定期更新测试用例

## 9. 最佳实践

### 9.1 测试用例设计
- 遵循单一职责原则
- 避免测试用例之间的依赖
- 保持测试用例的独立性

### 9.2 性能考虑
- 避免不必要的数据库操作
- 使用批量操作代替循环操作
- 优化测试执行时间

### 9.3 可维护性
- 提取公共方法到工具类
- 使用配置文件管理测试参数
- 保持代码结构清晰

## 10. 示例测试用例

```python
import pytest
from utils.HttpUtil import HttpUtil
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers
from utils.MysqlUtil import MysqlUtil

@pytest.mark.api
@pytest.mark.p0
class TestSOCreate:
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
        self.http = HttpUtil()
        self.assert_helper = AssertHelper()
        self.logger = Loggers()
        self.mysql = MysqlUtil()
        self.base_url = "/api/v1/sales/orders"
        yield
        # 清理测试数据
        self.cleanup_test_data()

    def test_create_so_success(self):
        """创建销售订单成功测试
        
        测试场景：
        1. 准备有效的订单数据
        2. 调用创建订单API
        3. 验证订单创建成功
        4. 验证数据库记录
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
        response = self.http.post(self.base_url, json=order_data)
        
        # 3. 验证API响应
        self.assert_helper.assert_http_status(response, 200)
        result = response.json()
        self.assert_helper.assert_response_status(result)
        self.assert_helper.assert_fields_exist(
            result["data"],
            ["order_no", "status", "total_amount"],
            {"order_no": "订单编号", "status": "订单状态", "total_amount": "订单总额"}
        )
        
        # 4. 验证数据库记录
        order_no = result["data"]["order_no"]
        db_result = self.mysql.query(
            "SELECT * FROM sales_orders WHERE order_no = %s",
            (order_no,)
        )
        self.assert_helper.assert_list_not_empty(db_result, "数据库查询结果")
        
        self.logger.info(f"测试通过：订单 {order_no} 创建成功")

    def cleanup_test_data(self):
        """清理测试数据"""
        # 实现数据清理逻辑
        pass
```

## 11. 注意事项

1. 测试用例应独立运行，不依赖其他测试用例
2. 避免硬编码，使用配置文件和常量
3. 保持测试用例的简洁性和可读性
4. 定期更新和维护测试用例
5. 遵循DRY原则，避免代码重复 

## 12. 环境配置管理

### 12.1 配置文件结构
- 基础配置：`config/env/base.yaml`
  - 包含所有环境通用的配置
  - 如日志、报告、性能监控等配置
  
- 环境特定配置：`config/env/{env}.yaml`
  - 包含特定环境的配置
  - 如数据库连接、API地址等
  
- 配置覆盖：通过 `--config-override` 参数指定
  - 用于临时覆盖某些配置
  - 支持本地开发和调试

### 12.2 环境变量支持
- 支持通过环境变量覆盖配置
- 主要环境变量：
  - 数据库配置：
    - `DB_HOST`
    - `DB_PORT`
    - `DB_USER`
    - `DB_PASSWORD`
    - `DB_NAME`
  - API配置：
    - `BASE_URL`
    - `IAM_URL`
  - 认证配置：
    - `AUTH_USERNAME`
    - `AUTH_PASSWORD`

### 12.3 配置使用示例
```python
import pytest

class TestModuleName:
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """测试前置条件"""
        self.config = config
        self.base_url = config["base_url"]
        self.db_config = config["database"]["erp_db"]
        
    def test_api_endpoint(self):
        """测试API端点"""
        # 使用配置的API地址
        response = self.http.get(f"{self.base_url}/api/v1/endpoint")
        
        # 使用配置的超时时间
        timeout = self.config["timeouts"]["api_request"]
        response = self.http.get(
            f"{self.base_url}/api/v1/endpoint",
            timeout=timeout
        )
```

### 12.4 运行测试
```bash
# 使用测试环境
pytest --env=test

# 使用开发环境
pytest --env=dev

# 使用覆盖配置
pytest --env=test --config-override=local_config.yaml

# 使用环境变量
DB_HOST=localhost DB_PORT=3306 pytest --env=test
```

### 12.5 配置优先级
1. 环境变量（最高优先级）
2. 配置覆盖文件
3. 环境特定配置
4. 基础配置（最低优先级） 

## 13. 环境变量管理

### 13.1 环境变量定义

项目使用 `.env` 文件管理环境变量，支持以下类型的环境变量：

1. 数据库配置
   - `DB_HOST`: 数据库主机地址
   - `DB_PORT`: 数据库端口
   - `DB_USER`: 数据库用户名
   - `DB_PASSWORD`: 数据库密码
   - `DB_NAME`: 数据库名称

2. API配置
   - `BASE_URL`: API基础URL
   - `IAM_URL`: IAM服务URL

3. 认证配置
   - `AUTH_USERNAME`: 认证用户名
   - `AUTH_PASSWORD`: 认证密码

4. 日志配置
   - `LOG_LEVEL`: 日志级别

### 13.2 环境变量模板

项目根目录下的 `.env.template` 文件是环境变量的模板文件，包含所有支持的环境变量及其说明。首次运行测试时会自动生成此文件。

### 13.3 环境变量验证

环境变量管理器会自动验证：
1. 必需的环境变量是否已设置
2. 环境变量的值是否符合类型要求
3. 环境变量的值是否符合验证规则（如正则表达式）

### 13.4 使用示例

1. 创建环境变量文件
```bash
# 复制模板文件
cp .env.template .env

# 编辑环境变量
vim .env
```

2. 运行测试时指定环境变量文件
```bash
# 使用默认的.env文件
pytest tests/

# 指定环境变量文件
pytest tests/ --env-file .env.test
```

3. 在测试中使用环境变量
```python
def test_example(config):
    # 使用配置中的环境变量
    db_config = config["database"]["erp_db"]
    assert db_config["host"] == "localhost"
    assert db_config["port"] == 3306
```

### 13.5 环境变量优先级

环境变量的优先级从高到低：
1. 命令行参数
2. 环境变量文件（.env）
3. 系统环境变量
4. 配置文件中的默认值 