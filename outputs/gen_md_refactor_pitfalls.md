# gen_md 改造踩坑记录（合并版）

## 背景
在 `gen_md` 模块将接口调用统一到 `standard_api_call` 的过程中，`test_addr_management.py` 出现详情/删除失败。

## 已发生问题
- 错误现象1：`id.required`
- 错误现象2：`Missing modelKey from request`（HTTP 500）
- 典型场景：详情/删除接口改造后，请求结构被错误下钻，导致后端在预期位置取不到关键字段

## 根因
1. **ID回写变量名不一致**
- `standard_api_call(store_id_as="addr")` 默认写入 `addrId`。
- 用例后续读取 `self.addr_id`，导致传参为 `None`。

2. **modelKey 位置不匹配**
- 目标服务通常要求 URL query 中包含 `modelKey`（以及 `tmodule`）。
- 仅放在 body 里，可能不满足后端路由/服务取值逻辑。

3. **参数层级路径使用不当**
- 常规接口多为写入 `params.request`。
- 部分导入导出任务接口需要写入 `params`。
- 路径不匹配时，字段会落错层级，触发 `modelKey` 缺失等异常。

## 统一修正规则（最小改动）
1. **常规查询/保存/删除**
- 使用：`standard_api_call(..., set_dict=..., fields_to_filter=...)`
- 保持默认：`use_param_util=True`（写入 `params.request`）

2. **导入导出任务类（只需要 `params` 层）**
- 使用：`standard_api_call(..., use_param_util=False, param_path=["params"])`

3. **系统服务（SYS_*）额外要求**
- 优先对照线上可用 curl，确认 `tmodule/modelKey` 放在 query 还是 body。
- 详情/删除场景通常需显式传：
  - `query_params={"tmodule": "GEN_MD", "modelKey": "GEN_MD$gen_addr_type_cf"}`

4. **ID使用规范**
- 关键 ID 不依赖 `store_id_as` 自动命名推断。
- 获取后显式赋值到后续实际读取变量（如 `self.addr_id = extracted_id`）。

## 快速排查清单
- [ ] 新增后 `extracted_id` 非空且已回写到后续读取变量。
- [ ] 当前接口模板期望路径是 `params.request` 还是 `params`。
- [ ] `modelKey/tmodule` 是否要求在 query。
- [ ] `standard_api_call` 的 `set_dict` 与服务模板结构一致。
- [ ] 断言不只校验 `success`，至少覆盖关键业务字段。

## 后续改造约束
1. 仅在目标模块内改动，避免扩散。
2. 每批改造后至少跑关键闭环（创建/详情/删除）。
3. 新增接口改造前先核对模板与 curl，再选调用模式。

## 本次结论
- `gen_md` 的统一调用改造已验证可行。
- 主要风险不在接口能力，而在 **请求层级**、**query 参数**、**ID变量回写一致性**。
