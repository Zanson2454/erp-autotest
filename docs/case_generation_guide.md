# ERP自动化测试用例快速生成指南

## 📋 概述

本指南介绍如何使用测试用例生成器快速创建标准的ERP自动化测试用例，大幅提升测试用例编写效率。

## 🚀 快速开始

### 1. 生成CRUD用例

```bash
# 生成品牌管理的完整CRUD用例
python script/case_generator.py \
  --module gen_md \
  --entity brand \
  --output testcases/gen_md/mat/ \
  --type crud
```

### 2. 生成配置检查用例

```bash
# 生成物料类型配置检查用例  
python script/case_generator.py \
  --module gen_md \
  --entity mat_type \
  --output testcases/gen_md/mat/ \
  --type config
```

### 3. 分析API结构

```bash
# 分析实体相关API，不生成用例
python script/case_generator.py \
  --module gen_md \
  --entity partner \
  --output testcases/gen_md/partner/ \
  --analyze
```

## 📖 详细说明

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--module` | ✅ | 模块名称 | `gen_md`, `prd`, `fin`, `scm` |
| `--entity` | ✅ | 业务实体名称 | `brand`, `mat_cate`, `partner` |
| `--output` | ✅ | 输出目录 | `testcases/gen_md/mat/` |
| `--type` | ❌ | 用例类型 | `crud`(默认), `config` |
| `--analyze` | ❌ | 只分析API | 不生成用例文件 |

### 支持的模块

| 模块 | 说明 | 配置文件路径 |
|------|------|-------------|
| `gen_md` | 通用基础数据 | `testdata/gen_md/md_api_*.yaml` |
| `prd` | 生产管理 | `testdata/prd/prd_api_*.yaml` |
| `fin` | 财务管理 | `testdata/fin/fin_api_*.yaml` |
| `scm` | 供应链管理 | `testdata/scm/scm_api_*.yaml` |

### 生成的用例结构

#### CRUD用例包含：
- ✅ **新增用例** (order=1)：创建实体数据
- ✅ **查询列表** (order=2)：分页查询功能
- ✅ **查询详情** (order=3)：单条数据查询
- ✅ **修改用例** (order=4)：更新实体数据
- ✅ **删除用例** (order=5)：删除实体数据

#### 配置检查用例包含：
- ✅ **配置完整性检查**：验证必需配置项存在
- ✅ **数据验证**：检查配置数据格式正确性

## 🛠️ 使用示例

### 示例1：生成物料类目管理用例

```bash
python script/case_generator.py \
  --module gen_md \
  --entity mat_cate \
  --output testcases/gen_md/mat/
```

**生成文件**：`testcases/gen_md/mat/test_mat_cate_management.py`

**包含用例**：
- `test_save_mat_cate()` - 新增类目
- `test_query_mat_cate_list()` - 查询类目列表  
- `test_query_mat_cate_detail()` - 查询类目详情
- `test_update_mat_cate()` - 修改类目
- `test_delete_mat_cate()` - 删除类目

### 示例2：生成合作伙伴配置检查用例

```bash
python script/case_generator.py \
  --module gen_md \
  --entity partner \
  --output testcases/gen_md/partner/ \
  --type config
```

**生成文件**：`testcases/gen_md/partner/test_00_partner_config_check.py`

**包含用例**：
- `test_partner_type_config()` - 检查合作伙伴类型配置

### 示例3：分析生产模块工作中心API

```bash
python script/case_generator.py \
  --module prd \
  --entity work_center \
  --output testcases/prd/master/ \
  --analyze
```

**输出示例**：
```
=== Work_center 实体API分析 ===

CREATE操作 (2个API):
  - PRD-工作中心-保存服务
  - PRD-工作中心-批量保存服务

QUERY操作 (1个API):
  - PRD-工作中心-查询分页服务

DETAIL操作 (1个API):
  - PRD-工作中心-查询详情服务
  
DELETE操作: 未找到相关API
```

## 🎯 最佳实践

### 1. 命名规范
- **实体名称**：使用下划线分隔，如 `mat_cate`, `work_center`
- **模块名称**：使用项目标准缩写，如 `gen_md`, `prd`

### 2. 生成顺序建议
1. **先分析API** (`--analyze`)：了解可用接口
2. **生成配置检查**：验证基础配置完整性  
3. **生成CRUD用例**：创建完整业务流程测试

### 3. 后续调整
生成的用例是**基础模板**，需要根据实际业务逻辑进行调整：

- ✏️ **调整字段名称**：根据实际API参数调整字段
- ✏️ **补充业务逻辑**：添加特殊业务规则验证
- ✏️ **优化测试数据**：根据业务约束调整测试数据
- ✏️ **完善断言**：添加更详细的结果验证

## 🔧 高级用法

### 批量生成用例

```bash
# 创建批量生成脚本
cat > scripts/batch_generate.sh << 'EOF'
#!/bin/bash

# 生成gen_md模块所有主要实体的用例
entities=("brand" "mat_cate" "partner" "org")

for entity in "${entities[@]}"; do
    echo "正在生成 $entity 用例..."
    python script/case_generator.py \
        --module gen_md \
        --entity $entity \
        --output testcases/gen_md/${entity}/ \
        --type crud
done

echo "批量生成完成！"
EOF

chmod +x scripts/batch_generate.sh
./scripts/batch_generate.sh
```

### 自定义模板

可以修改 `script/case_generator.py` 中的模板方法：
- `_generate_create_case()` - 自定义新增用例模板
- `_generate_query_case()` - 自定义查询用例模板
- `generate_config_check_case()` - 自定义配置检查模板

## 📊 效率提升

使用用例生成器的效率对比：

| 方式 | 单个CRUD用例集 | 10个用例集 | 质量一致性 |
|------|---------------|-----------|-----------|
| **手工编写** | ~4小时 | ~40小时 | ⚠️ 中等 |  
| **生成器** | ~30分钟 | ~5小时 | ✅ 高 |
| **效率提升** | **8倍** | **8倍** | **显著改善** |

## 🚨 注意事项

1. **API配置依赖**：确保对应模块的 `*_api_path.yaml` 和 `*_api_params.yaml` 文件存在且正确
2. **实体关键词匹配**：生成器通过关键词匹配API，确保实体名称在API名称中能找到
3. **生成后调试**：生成的用例需要根据实际API参数进行微调
4. **基础测试类**：确保对应模块的基础测试类已正确实现

## 📞 支持

如遇到问题或需要功能扩展，请：
1. 检查错误日志中的具体信息
2. 确认API配置文件格式正确
3. 提交issue或联系测试框架维护者 