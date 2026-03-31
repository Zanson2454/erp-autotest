# CURL 转测试用例提示词模板

> 基于 curl 命令一键生成 ERP 自动化测试用例

## 与其他规则的关系（必读）

| 文档 | 作用 |
|------|------|
| [`.cursor/rules/testcase_temp.mdc`](testcase_temp.mdc) | 测试类/方法模板、`file_level_order`、`init_data` / `md_cache_data` 安全获取、异步与参数化等 |
| [`.cursor/rules/coding_standards.mdc`](coding_standards.mdc) | Payload 清洗、复杂对象转 ID、`mock_util` 与环境/URL 前置校验等总则 |

本文档侧重 **curl 录制 → 参数骨架、幂等、自检清单与常见失败**；生成代码时须与上表一并遵守，不重复展开模板全文。

---

## 使用方式

将以下模板 + curl 命令一起提供给 AI，即可生成完整的测试用例代码。

---

## AI 提示词模板

```
请基于以下 curl 命令生成 ERP 自动化测试用例：

### curl 命令
```
{CURL_COMMAND}
```

### 生成要求

1. **使用 standard_api_call 方法**
2. **使用 mock_util 生成测试数据**（禁止硬编码）
3. **添加 @case_decorator 装饰器**
4. **添加 setup_class 和 teardown_class**
5. **使用 bind_cache_data 简化数据获取**
6. **禁止用例互调**（禁止 `self.test_xxx()`，改用 helper）
7. **加入幂等处理**（“已存在”错误码时回查并复用）
8. **严格按 YAML 参数骨架传参**：先查 `*_api_params.yaml` 再确定 `param_path`，不要默认都走 `["params","request"]`
9. **ID 字段强类型校验**：后续详情/删除前，必须断言 `id` 为数值或可转数值，禁止把 `dict/uuid/requestId` 当作业务 ID 透传
10. **状态前置校验**：指派/转办/转单/删除等状态敏感接口，先查询单据状态，不满足前置时 `pytest.skip`，不要直接硬断言失败

### 代码规范
- 完整模板与总则：`.cursor/rules/testcase_temp.mdc`、`.cursor/rules/coding_standards.mdc`（见本文「与其他规则的关系」）
- 使用 self.mock_util.generate_unique_code(tag="AT_XXX") 生成编码
- 使用 self.mock_util.get_timestamp() 生成时间戳
- 使用 self.bind_cache_data() 绑定常用数据（如 cust_id, org_id 等）
- 检查 `${ENV_VAR}` 占位符是否已替换，URL 必须带 `https://` 或 `http://`
- 对 `paginate_*` 类接口，重点检查 `pageable` 在 `params` 还是 `params.request`（以 YAML 为准）
- 对创建/提交类接口，禁止把 cURL 中的必填对象（如 `prType/comOrgId/prItemCode[*].prItemType`）清洗成 `None`
```

---

## 示例

### 输入 AI 的完整提示词

```
请基于以下 curl 命令生成 ERP 自动化测试用例：

### curl 命令
curl 'http://test.example.com/api/trantor/portal/data-service' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: JSESSIONID=xxx' \
  -H 'Referer: http://test.example.com/' \
  --data-raw '{"serviceKey":"GEN_PARTNER_SAVE_ACTION_SERVICE","params":{"request":{"code":"P001","name":"测试合作伙伴","partnerType":"CUSTOMER","status":"ENABLED"}}}'

### 生成要求

1. **使用 standard_api_call 方法**
2. **使用 mock_util 生成测试数据**（禁止硬编码）
3. **添加 @case_decorator 装饰器**
4. **添加 setup_class 和 teardown_class**
5. **使用 bind_cache_data 简化数据获取**
6. **禁止用例互调**（禁止 `self.test_xxx()`，改用 helper）
7. **加入幂等处理**（“已存在”错误码时回查并复用）
8. **严格按 YAML 参数骨架传参**：先查 `*_api_params.yaml` 再确定 `param_path`，不要默认都走 `["params","request"]`
9. **ID 字段强类型校验**：后续详情/删除前，必须断言 `id` 为数值或可转数值，禁止把 `dict/uuid/requestId` 当作业务 ID 透传
10. **状态前置校验**：指派/转办/转单/删除等状态敏感接口，先查询单据状态，不满足前置时 `pytest.skip`，不要直接硬断言失败

### 代码规范
- 完整模板与总则：`.cursor/rules/testcase_temp.mdc`、`.cursor/rules/coding_standards.mdc`（见本文「与其他规则的关系」）
- 使用 self.mock_util.generate_unique_code(tag="AT_XXX") 生成编码
- 使用 self.mock_util.get_timestamp() 生成时间戳
- 使用 self.bind_cache_data() 绑定常用数据（如 cust_id, org_id 等）
- 检查 `${ENV_VAR}` 占位符是否已替换，URL 必须带 `https://` 或 `http://`
- 对 `paginate_*` 类接口，重点检查 `pageable` 在 `params` 还是 `params.request`（以 YAML 为准）
- 对创建/提交类接口，禁止把 cURL 中的必填对象（如 `prType/comOrgId/prItemCode[*].prItemType`）清洗成 `None`
```

### AI 生成的代码

```python
import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("主数据管理")
@allure.feature("合作伙伴管理")
class TestPartnerManagement(GenMdBaseTest):
    """合作伙伴管理测试类"""
    
    partner_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.bind_cache_data()  # 绑定常用数据
        cls.logger.info("合作伙伴管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="partner_md", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="合作伙伴管理",
        title="测试创建合作伙伴",
        description="验证GEN_PARTNER_SAVE_ACTION_SERVICE功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["主数据", "合作伙伴", "创建"]
    )
    def test_save_partner(self):
        """测试创建合作伙伴"""
        try:
            # 1. 准备测试数据
            partner_code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
            partner_name = f"测试合作伙伴_{self.mock_util.get_timestamp()}"
            
            # 2. 使用标准化API调用
            set_dict = {
                "code": partner_code,
                "name": partner_name,
                "partnerType": "CUSTOMER",
                "status": "ENABLED"
            }
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                store_id_as="partner"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 保存ID
            if not hasattr(self, 'partner_id'):
                self.partner_id = extracted_id
            
            a.json(response, "响应数据")
            self.logger.info(f"创建合作伙伴成功: ID={self.partner_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

---

## 常用 API Key 参考

| 业务模块 | API Key 模式 | 示例 |
|----------|-------------|------|
| 合作伙伴 | GEN-合作伙伴-{服务} | GEN-合作伙伴-保存服务 |
| 组织 | GEN-组织-{服务} | GEN-组织-保存服务 |
| 物料 | GEN-物料-{服务} | GEN-物料-保存服务 |
| 销售订单 | SLS-SO-{服务} | SLS-SO-保存服务 |
| 采购订单 | PUR-PO-{服务} | PUR-PO-保存服务 |
| 财务 | FIN-{模块}-{服务} | FIN-AP-保存服务 |

---

## 快速绑定数据

```python
# 方式1: 绑定所有常用字段
cls.bind_cache_data()

# 方式2: 只绑定需要的字段
cls.bind_cache_data({
    "cust_id": "partner_info.cust_info.id",
    "org_id": "org_info.gr_come_org_info.id",
})

# 可用字段:
# init_data:
#   - curr_id (币种)
#   - coun_id (国家)
#   - addr_id (地址)
#   - bank_id (银行)
# md_cache_data:
#   - cust_id (客户)
#   - sup_id (供应商)
#   - com_org_id (核算组织)
#   - sls_org_id (销售组织)
#   - inv_org_id (库存组织)
#   - pur_org_id (采购组织)
#   - sls_dc_id (配送中心)
#   - wh_id (仓库)
#   - mat_id (物料)
```

---

## 生成后自检 Checklist（必须逐项通过）

- [ ] **参数骨架对齐**：每个接口都已从 `*_api_params.yaml` 确认 `param_path`；禁止默认全部走 `["params","request"]`
- [ ] **参数来源优先级正确**：`缓存值 > cURL原值 > 跳过并说明原因`，禁止“缓存取不到就传 None”
- [ ] **分页参数层级正确**：`paginate_*` / `paging_*` 接口已确认 `pageable` 位于 `params.pageable` 或 `params.request.pageable`
- [ ] **平台噪音已剔除**：`sceneKey/viewKey/appId/teamId/buttonKey/viewTitle/requestId/created*/updated*` 等未被直接透传到 `set_dict`
- [ ] **ID 强类型校验**：后续详情/删除/关联前，已确保业务 ID 为数值或可转数值；未将 `dict/requestId/uuid` 当业务 ID
- [ ] **创建接口回查策略**：若创建成功但响应未直接返回 `id`，已补“唯一键分页/详情回查”确认
- [ ] **创建接口必填对象校验**：请求前已断言必填对象非空（例如 `prType.id`）；若为空，优先回退使用 cURL 原值并记录风险
- [ ] **复制接口断言分级**：若接口语义为“复制初始化/渲染”，断言“成功+关键结构”，不强制要求持久化 `id`
- [ ] **状态前置校验**：指派/转办/转单/删除等状态敏感接口，已先查状态；不满足前置时 `pytest.skip`
- [ ] **禁止用例互调**：未出现 `self.test_xxx()`；公共前置已抽为私有 helper
- [ ] **断言分层完整**：至少包含 `assert_response_success/response_data` + 业务字段断言（必要时 DB 校验）
- [ ] **测试数据规范**：新增数据使用 `AT_` 前缀，来源优先 `mock_util` 与缓存，不硬编码主数据 ID
- [ ] **清理策略合规**：`teardown_class` 逐表删除，无循环删表；不依赖物理删除开关必然生效
- [ ] **记录可追溯性**：关键请求/响应通过 `a.json/a.text` 保留，失败信息可定位

---

## 常见失败对照（录制转用例）

- `pur.pr.type.is.empty`  
  - 含义：创建采购申请时 `prType` 为空  
  - 典型原因：把 cURL 里的 `prType` 映射成缓存变量后，缓存未命中导致传 `None`  
  - 处理：`prType` 必须回退到 cURL 原值（如 `{"id":14008002}`），并在报告中标注“使用录制值兜底”

- `V0301 参数 'pageable' 不正确`  
  - 含义：分页参数层级错误  
  - 处理：核对 `*_api_params.yaml`，确认是 `params.pageable` 还是 `params.request.pageable`

- `*.status.is.error`（如 `pur.pr.item.status.is.error`）  
  - 含义：状态机前置不满足  
  - 处理：先查状态并推进状态，再重试；仍不满足则 `pytest.skip` 并记录原因
