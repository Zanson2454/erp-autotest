# standard_api_call 完整指南

**作者**：阿里巴巴高级开发专家  
**版本**：v2.0（生产就绪）  
**最后更新**：2025-01-01

---

## 🚀 快速开始（一句话版）
```python
# 最简单的用法（95%的场景）
response, extracted_id = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"textCode": "AT_001", "textName": "测试"}
)
```

---

## 📖 方法签名

```python
def standard_api_call(
    self, 
    api_key,                    # API服务名称（必填）
    set_dict=None,              # 业务参数字典（可选）
    fields_to_filter=None,      # 字段过滤列表（可选，默认从set_dict.keys()获取）
    store_id_as=None,           # 自动存储ID属性名（可选）
    use_param_util=True,        # 是否使用ParamUtil过滤（可选，默认True）
    param_path=None,            # 参数路径（可选，默认["params", "request"]）
    method="POST",              # HTTP方法（可选，默认POST）
    query_params=None,          # URL查询参数（可选）
    extra_body_params=None      # 额外的body参数（可选）
)
```

---

## 🎯 两种参数模式

### 模式1：自动模式（95%的用例）✅ 推荐

**特点**：最简洁，适合标准CRUD操作

```python
# ✅ 新增/更新
set_dict = {
    "textCode": "AT_001",
    "textName": "测试文本"
}
response, extracted_id = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict=set_dict
)

# ✅ 查询详情/删除
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-查询详情服务",
    set_dict={"id": self.text_type_id}
)

# ✅ 分页查询
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-查询分页服务",
    set_dict={
        "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
        "fields": [{"name": "textCode", "type": "TEXT"}]
    }
)
```

---

### 模式2：手动模式（特殊场景）

**特点**：复杂接口需要URL参数 + body中params下需要多个同级字段（如采购模块）

```python
# ❌ 采购订单行类型 - 需要特殊处理
set_dict = {
    "request": {                        # 手动包 request
        "poItemType": "AT_001",
        "poItemTypeName": "测试",
        "autoComplete": False
    },
    "modelKey": self.MODEL_KEY          # 与 request 同级
}

response, extracted_id = self.standard_api_call(
    api_key="(系统)保存主数据服务",
    set_dict=set_dict,
    param_path=["params"],              # ✅ 必须
    use_param_util=False,               # ✅ 必须
    query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY},
    extra_body_params={"modelKey": self.MODEL_KEY}
)
```

---

## 📊 参数速查表

| 参数 | 自动模式 | 手动模式 | 说明 |
|------|---------|---------|------|
| `api_key` | ✅ 必传 | ✅ 必传 | API服务名称 |
| `set_dict` | ✅ 业务字段 | ✅ 完整结构 | 自动：只写字段；手动：包含request |
| `param_path` | ❌ 不传 | ✅ `["params"]` | 指定替换路径 |
| `use_param_util` | ❌ 不传 | ✅ `False` | 不使用自动过滤 |
| `query_params` | ❌ 不传 | ✅ 字典/字符串 | URL查询参数 |
| `extra_body_params` | ❌ 不传 | ✅ 字典 | body中params下的额外参数 |
| `fields_to_filter` | ❌ 不传（自动推断） | ❌ 不传 | 字段过滤列表，95%场景自动推断即可，特殊场景显式传递 |

---

## 🔧 参数详解

### query_params（URL查询参数）

```python
# 字典格式（推荐）
response, _ = self.standard_api_call(
    api_key="(系统)保存主数据服务",
    set_dict={...},
    query_params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$xxx"}
)
# → URL: ...?tmodule=SCM_PUR&modelKey=SCM_PUR%24xxx

# 字符串格式（兼容）
response, _ = self.standard_api_call(
    api_key="...",
    query_params="tmodule=SCM_PUR&modelKey=XXX"
)
```

### extra_body_params（额外body参数）

```python
# 用于在 params 下添加额外字段（不在 request 下）
response, _ = self.standard_api_call(
    api_key="...",
    set_dict={"request": {...}},
    param_path=["params"],
    use_param_util=False,
    extra_body_params={"modelKey": "XXX", "version": "1.0"}
)
# 结果：params 下包含 request、modelKey、version
```

### fields_to_filter（字段过滤列表）

**作用**：指定请求体中需要传递的字段列表，过滤掉不需要的字段。

**默认行为**：如果不传，会自动从 `set_dict.keys()` 获取字段列表。**95%的场景不需要显式传递**。

**什么时候需要显式传递？**

```python
# 场景1：set_dict 中有 None 值，但不想传递这些字段
set_dict = {
    "textCode": "AT_001",
    "textName": "测试",
    "description": None,  # 不想传递
    "remark": None        # 不想传递
}
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict=set_dict,
    fields_to_filter=["textCode", "textName"]  # 只传递这两个
)

# 场景2：分页查询等复杂结构，需要精确控制字段
set_dict = {
    "pageable": {"pageNo": 1, "pageSize": 20},
    "keyword": None,
    "filterData": {"matName": None}
}
response, _ = self.standard_api_call(
    api_key="物料类型-分页数据服务",
    set_dict=set_dict,
    fields_to_filter=["pageable", "keyword", "filterData"]  # 即使 None 也要传递
)
```

---

## ✅ 常见错误和解决方案

### ❌ 错误1：手动模式忘记 use_param_util=False

```python
# ❌ 错误：会导致过滤错误
response, _ = self.standard_api_call(
    api_key="...",
    set_dict={"request": {...}, "modelKey": "XXX"},
    param_path=["params"]
    # 少了 use_param_util=False
)

# ✅ 正确
response, _ = self.standard_api_call(
    api_key="...",
    set_dict={"request": {...}, "modelKey": "XXX"},
    param_path=["params"],
    use_param_util=False  # 必须
)
```

### ❌ 错误2：自动模式手动包 request

```python
# ❌ 错误：会导致 params.request.request.xxx
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"request": {"textCode": "AT_001"}}  # 多余
)

# ✅ 正确：只写业务字段
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"textCode": "AT_001"}
)
```

### ❌ 错误3：简单场景显式传 fields_to_filter

```python
# ❌ 多余：简单场景不需要显式传递
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"textCode": "AT_001", "textName": "测试"},
    fields_to_filter=["textCode", "textName"]  # 不需要，自动推断即可
)

# ✅ 简洁：自动推断即可
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"textCode": "AT_001", "textName": "测试"}
)
```

---

## 💡 最佳实践总结

1. **优先自动模式**：95%的用例只需 `api_key` + `set_dict`
2. **手动模式三件套**：缺一不可
3. **fields_to_filter**：95%场景自动推断即可，特殊场景才显式传递
4. **复杂请求用原生方法**：不要强行用 `standard_api_call`
5. **使用字典格式 query_params**：更清晰易读

