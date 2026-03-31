# Cursor Workflow Request Templates

## 1) cURL -> Testcase

```text
@workflow workflow-trigger
目标: 将 {recorded_flow_file} 转为 pytest 用例
模块: {module_name}
目标文件: {target_test_file}
必须遵循: standard_api_call, case_decorator, file_level_order, try-except, AT_前缀, 幂等分支
补充信息: {api_key_mapping_or_constraints}
```

## 2) ERP Full Flow Audit

```text
@workflow workflow-trigger
目标: 做一次 ERP 自动化框架全流程分析
范围: {repo_or_module_scope}
输出文件:
- outputs/01_project_analysis.md
- outputs/02_project_map.md
- outputs/03_erp_test_domain_map.md
- outputs/04_gap_analysis.md
输出要求: confirmed facts / inferred assumptions / unknowns + P0/P1/P2 风险
```

## 3) Systematic Debugging

```text
@workflow workflow-trigger
目标: 排查失败并给出高置信修复路径
症状: {error_message_or_failed_case}
复现方式: {command}
期望输出: 根因排序 + 证据 + 下一步验证动作
```
