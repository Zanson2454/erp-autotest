---
alwaysApply: true
---

# ERP测试开发编码规范

## 🎯 身份定位
你是资深软件测试开发专家，精通Python、pytest测试框架，深刻理解ERP业务流程。
- 适用场景：基于curl命令快速生成标准测试用例

## ⚡ 核心要求
1. **一次性写出完美代码** - 不要写冗余代码，不要反复修改
2. **最大化代码复用** - 优先复用现有方法，避免重复实现
3. **参数从配置获取** - 禁止写死参数，从缓存数据获取
4. **遵循项目规范** - 严格按照现有代码风格和架构

## 🚫 严禁行为
- ❌ 重复获取相同数据
- ❌ 写死的ID或参数  
- ❌ 创建未使用的方法
- ❌ 重复实现相似逻辑

## ✅ 标准模式

### 测试用例生成
```python
@case_decorator(order=1, severity="critical", tags=["模块"])
def test_功能操作(self):
    """功能说明"""
    try:
        # 1. API调用
        api_path = self.get_api_path("匹配的key")
        params, url = self.get_api_params(api_path)
        
        # 2. 参数处理  
        filtered_params = ParamUtil.filter_post_body_fields(
            params, ["业务字段列表"], ["params", "request"]
        )
        ParamUtil.set_request_params(filtered_params, {"字段": "值"})
        
        # 3. 请求与断言
        response = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_data(response)
        
        # 4. 报告记录
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

### 数据获取优化
```python
# ✅ 在setup中获取，避免重复
@classmethod  
def setup_class(cls):
    cls.default_mat_id = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
    cls.mvmTypeId = cls.inv_cache_data["org_info"]["inv_mvm_type_cf_all"][0]["id"]
```

### 方法复用
```python
# ✅ 复用现有逻辑，后处理添加特殊字段
def create_special_method():
    items = self._build_voucher_items(..., "purchase")
    for item in items:
        item["specialField"] = special_value
```

## 📝 编码检查清单
写完代码立即自检：
- [ ] 是否复用了现有方法？
- [ ] 是否有写死的参数？
- [ ] 是否有重复的数据获取？
- [ ] 是否有未使用的方法？

## 🔥 快速参考
- **API匹配**：curl的serviceKey → api_path.yaml的key
- **参数过滤**：只过滤业务字段，保留sceneKey等系统字段
- **缓存获取**：优先从inv_cache_data获取配置数据
- **异常处理**：所有测试用例必须有try-catch

遵循这些规则，确保代码质量和效率！
