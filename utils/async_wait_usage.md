# 异步等待工具使用指南

## 概述

`AsyncWaitUtil` 提供了通用的异步任务等待功能，支持轮询检查、超时控制、失败检测等。主要用于测试异步任务执行状态，如异步过账、异步初始化等场景。

## 快速开始

### 方式一：使用 `wait_for_async_status`（推荐）

适用于只需要检查异步任务状态的场景：

```python
@case_decorator(
    story="存货核算初始化配置管理",
    title="测试异步执行初始化并等待完成",
    file_level_order=11,
    tags=["iv", "init", "async", "wait"]
)
def test_execute_initialization_async_and_wait(self):
    """测试异步执行初始化并等待完成"""
    try:
        # 1. 发起异步任务
        response, _ = self.standard_api_call(
            api_key="存货核算初始化配置-执行初始化-异步任务发起",
            set_dict={"id": self.init_cf_id},
            fields_to_filter=["id"]
        )
        self.assert_util.assert_response_success(response)
        
        # 2. 定义查询函数
        def query_init_status():
            """查询初始化配置状态"""
            response, _ = self.standard_api_call(
                api_key="存货核算初始化配置-查询详情服务",
                set_dict={"id": self.init_cf_id},
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)
            return response.get("data", {}).get("data", {})
        
        # 3. 等待异步任务完成
        result = self.async_wait_util.wait_for_async_status(
            query_func=query_init_status,
            status_field="asyncExecutionStatus",
            success_status="SUCCEEDED",
            failed_status="FAILED",
            failure_reason_field="asyncExecutionFailureReason",
            max_wait=60,  # 最大等待60秒
            interval=3.0   # 每3秒查询一次
        )
        
        # 4. 断言等待结果
        if result.status == self.wait_status.SUCCESS:
            final_status = result.last_data.get("asyncExecutionStatus")
            self.assert_util.assert_by_operator(
                final_status, "=", "SUCCEEDED",
                f"异步任务应成功完成，实际状态: {final_status}"
            )
        elif result.status == self.wait_status.FAILED:
            raise AssertionError(f"异步任务失败: {result.error_message}")
        else:
            raise AssertionError(f"等待异步任务超时: {result.error_message}")
            
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

### 方式二：使用 `wait_for_condition`（灵活）

适用于需要自定义检查逻辑的复杂场景：

```python
@case_decorator(
    story="应收单状态校验",
    title="轮询查询应收单状态",
    file_level_order=5,
    tags=["ar", "check", "status"]
)
def test_check_ar_doc_status(self):
    """轮询查询应收单状态"""
    try:
        ar_head_code = self.ar_info.get("arHeadCode")
        
        def check_ar_status():
            """检查应收单状态"""
            # 查询应收单
            response, _ = self.standard_api_call(
                api_key="应收单头表-分页数据服务",
                set_dict={
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 1,
                        "conditionItems": {
                            "conditions": {
                                "arHeadCode": {"operator": "CONTAINS", "value": ar_head_code}
                            }
                        }
                    }
                },
                fields_to_filter=["pageable"]
            )
            self.assert_util.assert_response_success(response)
            
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            if not data_list:
                return False, None, "未找到应收单数据"
            
            ar_record = data_list[0]
            current_status = ar_record.get("arStatus")
            async_status = ar_record.get("asyncExecutionStatus")
            
            # 判断条件
            if current_status == "DONE" and async_status == "SUCCEEDED":
                return True, ar_record, None  # 成功
            elif async_status == "FAILED":
                failure_reason = ar_record.get("asyncExecutionFailureReason", "未知原因")
                return False, ar_record, failure_reason  # 失败
            else:
                return False, ar_record, None  # 继续等待
        
        # 等待条件满足
        result = self.async_wait_util.wait_for_condition(
            check_func=check_ar_status,
            max_wait=30,
            interval=2.0,
            timeout_message="应收单状态未在30秒内更新为DONE"
        )
        
        # 断言结果
        if result.status == self.wait_status.SUCCESS:
            ar_record = result.last_data
            self.assert_util.assert_by_operator(
                ar_record.get("arStatus"), "=", "DONE"
            )
            self.assert_util.assert_by_operator(
                ar_record.get("asyncExecutionStatus"), "=", "SUCCEEDED"
            )
        elif result.status == self.wait_status.FAILED:
            raise AssertionError(f"异步任务失败: {result.error_message}")
        else:
            raise AssertionError(f"等待超时: {result.error_message}")
            
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

## API 参考

### `wait_for_async_status`

等待异步任务状态（专用方法，简化异步状态检查）

**参数：**
- `query_func`: 查询函数，返回包含状态的数据字典
- `status_field`: 状态字段名，默认 `"asyncExecutionStatus"`
- `success_status`: 成功状态值，默认 `"SUCCEEDED"`
- `failed_status`: 失败状态值，默认 `"FAILED"`
- `failure_reason_field`: 失败原因字段名，默认 `"asyncExecutionFailureReason"`
- `max_wait`: 最大等待时间（秒），默认30秒
- `interval`: 轮询间隔（秒），默认2秒
- `additional_check`: 额外的检查函数（可选），接收数据字典，返回True表示满足额外条件

**返回：**
- `AsyncWaitResult`: 等待结果对象

### `wait_for_condition`

等待条件满足（通用轮询方法）

**参数：**
- `check_func`: 检查函数，返回 `(是否满足条件, 当前数据, 错误信息)`
  - 第一个返回值：`True` 表示条件满足，`False` 表示继续等待
  - 第二个返回值：当前查询到的数据（用于记录和最终返回）
  - 第三个返回值：如果任务失败，返回失败原因；否则返回 `None`
- `max_wait`: 最大等待时间（秒），默认30秒
- `interval`: 轮询间隔（秒），默认2秒
- `timeout_message`: 超时提示信息
- `enable_polling_log`: 是否启用轮询日志，默认 `True`

**返回：**
- `AsyncWaitResult`: 等待结果对象

### `AsyncWaitResult`

等待结果对象，包含以下属性：

- `status`: 等待状态（`WaitStatus` 枚举）
  - `SUCCESS`: 等待成功，条件满足
  - `TIMEOUT`: 等待超时
  - `FAILED`: 任务失败
  - `ERROR`: 检查过程出错
- `attempts`: 检查次数
- `total_wait_time`: 总等待时间（秒）
- `last_data`: 最后一次查询到的数据
- `error_message`: 错误信息
- `polling_history`: 轮询历史记录

**方法：**
- `to_dict()`: 转换为字典格式

## 最佳实践

### 1. 合理设置超时时间

根据业务场景设置合适的 `max_wait` 值：
- 快速任务（如状态更新）：10-30秒
- 中等任务（如过账）：30-60秒
- 慢速任务（如批量处理）：60-120秒

### 2. 合理设置轮询间隔

根据任务特性设置合适的 `interval` 值：
- 快速任务：1-2秒
- 中等任务：2-3秒
- 慢速任务：3-5秒

### 3. 处理失败情况

始终检查 `result.status`，并处理失败和超时情况：

```python
if result.status == self.wait_status.SUCCESS:
    # 处理成功
    pass
elif result.status == self.wait_status.FAILED:
    # 处理失败
    raise AssertionError(f"任务失败: {result.error_message}")
else:
    # 处理超时或错误
    raise AssertionError(f"等待超时: {result.error_message}")
```

### 4. 使用额外检查条件

对于需要多个条件都满足的场景，使用 `additional_check`：

```python
def check_billing_amount(data):
    """检查开票金额是否大于0"""
    return data.get("billingDocAmt", 0) > 0

result = self.async_wait_util.wait_for_async_status(
    query_func=query_func,
    success_status="SUCCEEDED",
    additional_check=check_billing_amount
)
```

### 5. 记录轮询历史

工具会自动记录轮询历史到 Allure 报告中，无需手动记录。

## 常见场景示例

### 场景1：等待异步过账完成

```python
def query_ar_status():
    response, _ = self.standard_api_call(
        api_key="应收单-查询详情服务",
        set_dict={"id": self.ar_id},
        fields_to_filter=["id"]
    )
    return response.get("data", {}).get("data", {})

result = self.async_wait_util.wait_for_async_status(
    query_func=query_ar_status,
    max_wait=60,
    interval=3.0
)
```

### 场景2：等待状态更新并验证业务数据

```python
def check_status_and_data():
    data = query_status()
    status = data.get("asyncExecutionStatus")
    amount = data.get("amount", 0)
    
    if status == "SUCCEEDED" and amount > 0:
        return True, data, None
    elif status == "FAILED":
        return False, data, data.get("failureReason")
    else:
        return False, data, None

result = self.async_wait_util.wait_for_condition(
    check_func=check_status_and_data,
    max_wait=30,
    interval=2.0
)
```

### 场景3：数据库轮询检查

```python
def check_db_status():
    sql = "SELECT async_execution_status FROM table WHERE id = %s"
    result = self.db.query(sql, (self.record_id,))
    
    if result and result[0].get("async_execution_status") == "SUCCEEDED":
        return True, result[0], None
    elif result and result[0].get("async_execution_status") == "FAILED":
        return False, result[0], "数据库状态为失败"
    else:
        return False, result[0] if result else None, None

result = self.async_wait_util.wait_for_condition(
    check_func=check_db_status,
    max_wait=30,
    interval=1.0
)
```

## 注意事项

1. **检查函数应该幂等**：多次调用应该返回一致的结果
2. **避免在检查函数中抛出异常**：异常会被捕获并标记为 `ERROR` 状态
3. **合理设置超时时间**：避免测试时间过长
4. **轮询间隔不要太小**：避免对系统造成压力
5. **记录关键信息**：工具会自动记录，但可以在检查函数中添加额外的日志

