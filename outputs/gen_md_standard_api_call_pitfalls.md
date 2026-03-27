# gen_md 改造踩坑记录（standard_api_call）

## 1. 已发生问题
- 错误现象：`Missing modelKey from request`（HTTP 500）
- 典型报错场景：详情/删除接口改造后，请求结构被错误下钻，导致后端在预期位置取不到 `modelKey`

## 2. 根因
- 并非接口本身不可用，而是 `standard_api_call` 的参数路径使用不当：
  - 某些接口需要写入 `params.request`
  - 某些导入导出任务接口需要写入 `params`
- 若路径不匹配，顶层或关键字段会被放错层级，触发 `modelKey` 缺失等异常

## 3. 统一修正规则（最小改动）
- 常规查询/保存/删除：
  - `standard_api_call(..., set_dict=..., fields_to_filter=...)`
  - 保持默认 `use_param_util=True`（默认路径 `params.request`）
- 导入导出任务类（明确只需要 `params` 层）：
  - `standard_api_call(..., use_param_util=False, param_path=["params"])`

## 4. 快速排查清单
- 若出现 `Missing modelKey from request`：
  1. 先核对该接口模板期望路径是 `params.request` 还是 `params`
  2. 检查是否误用了 `use_param_util=False` 或 `param_path`
  3. 对照前端 curl 中 `params` 结构，确认 `modelKey` 所在层级

## 5. 本次结论
- `gen_md` 下 `self.http.post(...)` 已全部替换为 `standard_api_call(...)`
- 后续新增改造，优先按“接口模板路径”判断调用模式，避免再次触发同类问题
