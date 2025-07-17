# 类型检查配置说明

## 概述
本项目配置了全局的类型检查忽略规则，主要用于解决pytest相关的类型检查问题。

## 配置文件

### 1. pyrightconfig.json
- `typeCheckingMode`: 设置为 "off" 完全关闭类型检查
- `reportAttributeAccessIssue`: 设置为 "none" 忽略属性访问问题
- 其他各种报告类型都设置为 "none" 以忽略常见的类型检查警告

### 2. pytest.ini
- 添加了多个pytest相关的警告忽略规则
- 包括：`PytestUnknownMarkWarning`, `PytestCollectionWarning` 等

### 3. testcases/comm/type_ignores.py
- 提供了各种类型忽略注释的参考
- 可以在需要的地方使用 `# type: ignore[error-code]` 来忽略特定问题

## 常见问题

### 1. "无法访问 'Item' 类的 'funcargs' 属性"
- 这是pytest动态属性导致的类型检查问题
- 已在pyrightconfig.json中通过 `reportAttributeAccessIssue: "none"` 忽略

### 2. pytest装饰器类型问题
- pytest的装饰器（如 `@pytest.mark.skip`）可能触发类型检查警告
- 已在配置中忽略相关警告

### 3. 动态属性访问问题
- BaseTest类中的动态属性（如 `self.logger`, `self.http` 等）
- 已在BaseTest类中添加 `# type: ignore[attr-defined]` 注释

## 使用方法

### 在代码中添加类型忽略
```python
# 忽略特定行的类型检查问题
some_pytest_attr = getattr(self, 'dynamic_attr')  # type: ignore[attr-defined]

# 忽略整个函数的类型检查
def test_function(self):  # type: ignore[no-untyped-def]
    pass
```

### 在类级别忽略
```python
class TestClass:  # type: ignore[attr-defined]
    def setup_method(self, method):  # type: ignore[no-untyped-def]
        pass
```

## 注意事项
1. 这些配置主要用于开发阶段，避免类型检查器干扰开发流程
2. 在生产环境中，建议根据实际需要调整类型检查级别
3. 如果遇到新的类型检查问题，可以添加到相应的配置文件中 