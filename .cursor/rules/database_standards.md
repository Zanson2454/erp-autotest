---
alwaysApply: true
---

# 数据库操作规范

## 概述
本规范定义了ERP自动化测试项目中数据库操作的标准化方法，确保数据操作的安全性、一致性和可维护性。

## 核心原则
- **连接管理**: 使用DBManager统一管理数据库连接，支持类级别和实例级别两种模式
- **事务安全**: 所有写操作必须使用事务，失败时自动回滚
- **参数化查询**: 禁止SQL注入，所有SQL必须使用参数化查询
- **数据隔离**: 测试数据使用"AT_"前缀，确保与生产数据隔离
- **资源清理**: 测试结束后必须清理测试数据，避免数据污染

## 数据库连接管理

### 类级别连接（推荐用于测试类）
```python
from utils.mysql_util import DBManager

@classmethod
def setup_class(cls):
    super().setup_class()
    # 从环境配置获取数据库配置
    db_config = cls.env_config.get("database", {})
    DBManager.init(db_config)
    cls.db = DBManager()  # 使用类级别连接

@classmethod
def teardown_class(cls):
    # 清理测试数据
    cls.db.delete(table="table_name", where="code like %s", params=["AT_%"])
    DBManager.close()  # 关闭类级别连接
```

### 实例级别连接（特殊场景）
```python
# 创建独立数据库连接实例
db_instance = DBManager(
    host="localhost",
    port=3306,
    database="test_db",
    username="user",
    password="pass"
)
# 使用完毕后关闭
db_instance.close()
```

## SQL操作规范

### 查询操作（SELECT）
```python
# 标准查询
results = self.db.query(
    sql="SELECT * FROM table_name WHERE code = %s AND status = %s",
    params=["AT_CODE001", "ACTIVE"]
)

# 查询单条记录
result = self.db.query_one(
    sql="SELECT * FROM table_name WHERE id = %s",
    params=[123]
)

# 注意事项：
# 1. 必须使用参数化查询，禁止字符串拼接
# 2. 查询结果为空时返回空列表[]，不会返回None
# 3. 查询失败会抛出异常，需要try-catch处理
```

### 插入操作（INSERT）
```python
# 方式一：使用insert方法（推荐）
inserted_id = self.db.insert(
    table="table_name",
    data={
        "code": "AT_CODE001",
        "name": "测试数据",
        "status": "ACTIVE",
        "create_time": datetime.now()
    }
)

# 方式二：使用execute方法（复杂场景）
self.db.execute(
    sql="INSERT INTO table_name (code, name, status) VALUES (%s, %s, %s)",
    params=["AT_CODE001", "测试数据", "ACTIVE"]
)
```

### 更新操作（UPDATE）
```python
# 标准更新
affected_rows = self.db.update(
    table="table_name",
    data={
        "name": "更新后的名称",
        "status": "INACTIVE"
    },
    where="code = %s AND status = %s",
    params=["AT_CODE001", "ACTIVE"]
)

# 注意事项：
# 1. where条件必须使用参数化，避免SQL注入
# 2. 返回受影响的行数
# 3. 更新失败会自动回滚
```

### 删除操作（DELETE）
```python
# 标准删除
affected_rows = self.db.delete(
    table="table_name",
    where="code like %s",
    params=["AT_%"]
)

# 注意事项：
# 1. 删除操作必须谨慎，建议先查询确认
# 2. 批量删除使用LIKE条件，如"AT_%"
# 3. 删除失败会自动回滚
```

## 数据清理规范

### 测试类数据清理
```python
@classmethod
def teardown_class(cls):
    """测试类结束后执行清理"""
    try:
        # 禁止用循环遍历表名，必须一个表一个表地单独调用
        cls.db.delete(table="table1", where="code like %s", params=["AT_%"])
        cls.db.delete(table="table2", where="code like %s", params=["AT_%"])
        cls.db.delete(table="table3", where="code like %s", params=["AT_%"])
        cls.logger.info("测试数据清理完成")
    except Exception as e:
        cls.logger.error(f"测试数据清理失败: {str(e)}")
```

### 清理顺序规范
1. **先删除子表，再删除父表**（避免外键约束）
2. **按依赖关系倒序删除**（从最底层依赖开始）
3. **使用事务确保原子性**（DBManager自动处理）

### 反例（禁止）
```python
# ❌ 错误：使用循环遍历表名
tables = ["table1", "table2", "table3"]
for table in tables:
    cls.db.delete(table=table, where="code like %s", params=["AT_%"])

# ❌ 错误：字符串拼接SQL
sql = f"DELETE FROM {table} WHERE code = '{code}'"  # SQL注入风险

# ❌ 错误：不使用参数化查询
cls.db.execute(f"DELETE FROM table WHERE code = '{code}'")
```

## 事务处理规范

### 自动事务管理
DBManager自动管理事务：
- **查询操作**: 不需要事务，直接执行
- **写操作**: 自动开启事务，成功提交，失败回滚

### 手动事务控制（特殊场景）
```python
# 如果需要手动控制事务，使用execute方法
try:
    # 开启事务（DBManager自动处理）
    self.db.execute("BEGIN")
    
    # 执行多个操作
    self.db.insert(table="table1", data={...})
    self.db.update(table="table2", data={...}, where="...", params=[...])
    
    # 提交事务（DBManager自动处理）
    self.db.execute("COMMIT")
except Exception as e:
    # 回滚事务（DBManager自动处理）
    self.db.execute("ROLLBACK")
    raise
```

## 数据验证规范

### 查询验证
```python
# 验证数据是否存在
result = self.db.query_one(
    sql="SELECT * FROM table_name WHERE id = %s",
    params=[self.xxx_id]
)
assert result is not None, "数据不存在"

# 验证数据数量
count = self.db.query_one(
    sql="SELECT COUNT(*) as count FROM table_name WHERE code like %s",
    params=["AT_%"]
)
assert count["count"] > 0, "数据数量不正确"
```

### 数据完整性验证
```python
# 验证外键关联
parent = self.db.query_one(
    sql="SELECT * FROM parent_table WHERE id = %s",
    params=[parent_id]
)
assert parent is not None, "父表数据不存在"

child = self.db.query_one(
    sql="SELECT * FROM child_table WHERE parent_id = %s",
    params=[parent_id]
)
assert child is not None, "子表数据不存在"
```

## 性能优化规范

### 批量操作
```python
# 批量插入（使用事务）
try:
    for item in data_list:
        self.db.insert(table="table_name", data=item)
except Exception as e:
    # 自动回滚
    raise
```

### 索引使用
- 查询条件应使用索引字段（如id、code等）
- 避免全表扫描（使用WHERE条件）
- 复杂查询考虑使用EXPLAIN分析

## 异常处理规范

### 标准异常处理
```python
from utils.exception_util import safe_db_operation, DatabaseException

@safe_db_operation(error_message="查询数据失败", reraise=True)
def query_data(self, data_id):
    return self.db.query_one(
        sql="SELECT * FROM table_name WHERE id = %s",
        params=[data_id]
    )
```

### 异常捕获和处理
```python
try:
    result = self.db.query_one(
        sql="SELECT * FROM table_name WHERE id = %s",
        params=[data_id]
    )
except DatabaseException as e:
    self.logger.error(f"数据库操作失败: {str(e)}")
    raise
except Exception as e:
    self.logger.error(f"未知错误: {str(e)}")
    raise
```

## 最佳实践

### 1. 数据准备
```python
# 在setup_class中准备测试数据
@classmethod
def setup_class(cls):
    super().setup_class()
    # 从数据库获取基础数据
    currency = cls.db.query_one(
        sql="SELECT id FROM gen_curr_type_cf WHERE curr_code = %s",
        params=["CNY"]
    )
    cls.curr_id = currency.get("id") if currency else None
```

### 2. 数据验证
```python
# 在测试方法中验证数据
def test_save_data(self):
    # 创建数据
    data_id = self.db.insert(table="table_name", data={...})
    
    # 验证数据
    result = self.db.query_one(
        sql="SELECT * FROM table_name WHERE id = %s",
        params=[data_id]
    )
    assert result is not None
    assert result["code"] == "AT_CODE001"
```

### 3. 数据清理
```python
# 在teardown_class中清理数据
@classmethod
def teardown_class(cls):
    try:
        # 按依赖关系倒序删除
        cls.db.delete(table="child_table", where="code like %s", params=["AT_%"])
        cls.db.delete(table="parent_table", where="code like %s", params=["AT_%"])
    except Exception as e:
        cls.logger.error(f"清理失败: {str(e)}")
```

## 常见错误避免

1. **SQL注入风险**: 必须使用参数化查询
2. **事务未提交**: DBManager自动处理，无需手动提交
3. **连接未关闭**: 使用类级别连接时，teardown_class中关闭
4. **数据未清理**: 必须在teardown_class中清理测试数据
5. **循环删除表**: 禁止使用循环，必须逐个表删除
