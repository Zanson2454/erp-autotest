# pytest 测试执行顺序指南

> 快速上手：新旧排序方式对比和使用指南

---

## 🎯 核心概念（3分钟掌握）

### 两种排序模式

| 模式 | 参数 | 作用范围 | 推荐场景 |
|------|------|---------|---------|
| **老模式** | `order` | 全局排序（会交叉执行） | 兼容老代码 |
| **新模式** | `file_level_order` | 文件级串行 | ✅ 推荐新项目 |

### 执行顺序三层级

```
目录（01_、02_前缀） → 文件（01_、02_前缀） → 测试用例（file_level_order=1,2,3）
```

---

## 一、新排序方式：file_level_order（✅ 推荐）

### 问题 vs 解决

| 老方式（order） | 问题 | 新方式（file_level_order） | 效果 |
|----------------|------|---------------------------|------|
| 文件1: order=1,2 | 不同文件的 order=1 | 文件1: file_level_order=1,2 | ✅ 不冲突 |
| 文件2: order=1,2 | 会交叉执行 | 文件2: file_level_order=1,2 | ✅ 文件级串行 |

### 实际案例

```python
# 目录结构
testcases/scm_pur/cf/
  ├── test_pr_head_type_management.py    # 文件1
  └── test_pr_item_type_management.py    # 文件2

# 文件1: test_pr_head_type_management.py
@case_decorator(file_level_order=1, title="创建申请类型")
def test_create(): pass

@case_decorator(file_level_order=2, title="分页查询")
def test_paging(): pass

@case_decorator(file_level_order=3, title="导出任务")
def test_export(): pass

@case_decorator(file_level_order=4, title="删除")
def test_delete(): pass

# 文件2: test_pr_item_type_management.py（与文件1同样的 1,2,3,4）
@case_decorator(file_level_order=1, title="创建行类型")  # ✅ 不冲突！
def test_create(): pass

@case_decorator(file_level_order=2, title="分页查询")
def test_paging(): pass
```

### 执行顺序

```bash
pytest testcases/scm_pur/cf/ -v

# 完美串行：先执行完文件1，再执行文件2
test_pr_head_type_management.py::test_create   [12%]
test_pr_head_type_management.py::test_paging   [25%]
test_pr_head_type_management.py::test_export   [37%]
test_pr_head_type_management.py::test_delete   [50%]
test_pr_item_type_management.py::test_create   [62%]
test_pr_item_type_management.py::test_paging   [75%]
```

---

## 二、控制目录和文件顺序（01、02前缀）

### 目录级控制

```bash
testcases/
  ├── 01_scm_pur/         # 第1个执行
  ├── 02_scm_sls/         # 第2个执行
  └── 03_scm_inv/         # 第3个执行
```

### 文件级控制

```bash
testcases/scm_pur/cf/
  ├── 01_test_pr_head_type.py    # 第1个执行
  ├── 02_test_pr_item_type.py    # 第2个执行
  ├── 03_test_po_type.py         # 第3个执行
  └── 04_test_po_item_type.py    # 第4个执行
```

**原理**：字符串字母序，`"01_"` < `"02_"` < `"03_"`

---

## 三、老排序方式：order（兼容）

### 问题：order 是全局的

```python
# test_a.py
@case_decorator(order=1, title="A创建")
def test_create_a(): pass

@case_decorator(order=2, title="A查询")
def test_query_a(): pass

# test_b.py
@case_decorator(order=1, title="B创建")  # ⚠️ 与文件A的order=1冲突
def test_create_b(): pass

# 执行顺序（交叉执行）：
# test_a::test_create_a (order=1)
# test_b::test_create_b (order=1)  ← 插入了！
# test_a::test_query_a (order=2)
```

### 什么时候用 order？

✅ **可以用**：
- 老项目兼容
- 单文件内排序

❌ **不要用**：
- 跨文件使用（会交叉执行）
- 新项目（用 `file_level_order`）

---

## 四、参数对比

| 参数 | 作用范围 | 内部实现 | 同值冲突 | 推荐 |
|------|---------|---------|---------|------|
| `order` | 全局排序 | `pytest.mark.run(order)` | ❌ 会交叉 | 老代码 |
| `file_level_order` | 文件级 | `wrapper._file_level_order` | ✅ 不冲突 | ✅ 新项目 |

### 🔴 不要同时使用

```python
# ❌ 错误：冲突
@case_decorator(
    order=1,
    file_level_order=1,  # 只用一个！
    title="测试"
)
```

---

## 五、快速决策表

| 场景 | 方案 | 示例 |
|------|------|------|
| **新项目** | `file_level_order` + 前缀 | `01_test_xx.py`, `file_level_order=1` |
| **老项目** | 保持 `order` | 不动老代码 |
| **控制目录顺序** | 目录名前缀 | `01_scm_pur/`, `02_scm_sls/` |
| **控制文件顺序** | 文件名前缀 | `01_test_xx.py`, `02_test_yy.py` |
| **文件内顺序** | `file_level_order=1,2,3` | 每个文件独立 |

---

## 六、最佳实践

### ✅ 推荐做法（新项目）

```python
# 1. 文件命名用前缀
01_test_pr_head_type.py
02_test_pr_item_type.py

# 2. 测试用例用 file_level_order
@case_decorator(
    file_level_order=1,  # 文件内第1个
    title="测试创建"
)
def test_create(): pass

@case_decorator(
    file_level_order=2,  # 文件内第2个
    title="测试查询"
)
def test_query(): pass
```

### ❌ 常见错误

```python
# ❌ 1. 同时使用两种参数
@case_decorator(order=1, file_level_order=1)

# ❌ 2. 跨文件使用 order（老方式）
# test_a.py: order=1
# test_b.py: order=1  # 会交叉执行

# ❌ 3. 硬依赖其他测试
def test_query(self):
    # 假设 test_create 已执行
    data = self.__class__.created_id
```

---

## 七、常用命令

```bash
# 查看收集顺序
pytest --collect-only -q testcases/scm_pur/cf/

# 运行测试看顺序
pytest testcases/scm_pur/cf/ -v --tb=no | grep "PASSED"

# 查找使用 file_level_order 的文件
grep -r "file_level_order=" testcases/ --include="*.py"
```

---

## 总结（记住这5条）

1. **新项目用 `file_level_order`，老项目保持 `order`**
2. **目录/文件顺序用 01_、02_ 前缀**
3. **不同文件可以用相同的 `file_level_order=1,2,3,4`，不冲突**
4. **不要同时使用 `order` 和 `file_level_order`**
5. **用 `_ensure` 方法实现测试自给自足**

---

## FAQ

**Q: 为什么要引入 file_level_order？**  
A: 解决 order 跨文件冲突问题，实现文件级串行执行。

**Q: 老代码需要改吗？**  
A: 不需要，保持兼容。新代码推荐用 `file_level_order`。

**Q: 01_前缀是必须的吗？**  
A: 不是，只是推荐用来明确顺序。字母序自然排序也可以。

**Q: file_level_order=0 是什么意思？**  
A: 与不写一样，表示不参与排序，按代码定义顺序。
