-- 生产领料单类型配置
INSERT INTO prd_issue_type_cf (
    type_code, type_name, code_rules, is_created_by_push, is_issue,
    created_by, updated_by, created_at, updated_at, 
    version, deleted, origin_org_id
)
SELECT 
    'ISSUE_FORWARD', '正向领料单据', NULL, 1, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_type_cf 
    WHERE type_name = '正向领料单据' AND deleted = 0
);

INSERT INTO prd_issue_type_cf (
    type_code, type_name, code_rules, is_created_by_push, is_issue,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'ISSUE_REVERSE', '返向退料单据', NULL, 1, 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_type_cf 
    WHERE type_name = '返向退料单据' AND deleted = 0
);

-- 生产领料分单规则配置
INSERT INTO prd_issue_rule_cf (
    code, name, default_value,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'DEFAULT_RULE', '默认分单规则', 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_cf 
    WHERE name = '默认分单规则' AND deleted = 0
);

-- 生产领料分单规则明细配置
INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'INV_ORG', 1, 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'INV_ORG' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'INV_LOC', 1, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'INV_LOC' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'PRD_ORDER_TYPE', 0, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'PRD_ORDER_TYPE' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'PRD_ORDER', 0, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'PRD_ORDER' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'ROUTING_ITEM', 0, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'ROUTING_ITEM' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'WORK_CENTER', 1, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'WORK_CENTER' AND deleted = 0
);

INSERT INTO prd_issue_rule_item_cf (
    item, default_value, is_modified,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, prd_issue_rule_cf_id
)
SELECT 
    'PLAN_START_DATE', 0, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, (SELECT id FROM prd_issue_rule_cf WHERE name = '默认分单规则' AND deleted = 0)
WHERE NOT EXISTS (
    SELECT 1 FROM prd_issue_rule_item_cf 
    WHERE item = 'PLAN_START_DATE' AND deleted = 0
);

-- 生产订单类型配置
INSERT INTO prd_wo_type_cf (
    type_code, type_name, code_rules, external_code_is,
    vrs_select_mode, pln_cost_variation, actual_cost_variation,
    inv_type_cf_id, business_type, check_prd_vrs_exist,
    pur_pr_head_type_cf_id, prd_return_order_type_cf_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '01', '量产生产订单', NULL, 0,
    'AUTOMATIC', NULL, NULL,
    2000001, 'STANDARD', NULL,
    14007001, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_wo_type_cf 
    WHERE type_name = '量产生产订单' AND deleted = 0
);

INSERT INTO prd_wo_type_cf (
    type_code, type_name, code_rules, external_code_is,
    vrs_select_mode, pln_cost_variation, actual_cost_variation,
    inv_type_cf_id, business_type, check_prd_vrs_exist,
    pur_pr_head_type_cf_id, prd_return_order_type_cf_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '02', '返修生产订单', NULL, 0,
    NULL, NULL, NULL,
    2000001, 'REPAIR', NULL,
    NULL, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_wo_type_cf 
    WHERE type_name = '返修生产订单' AND deleted = 0
);

INSERT INTO prd_wo_type_cf (
    type_code, type_name, code_rules, external_code_is,
    vrs_select_mode, pln_cost_variation, actual_cost_variation,
    inv_type_cf_id, business_type, check_prd_vrs_exist,
    pur_pr_head_type_cf_id, prd_return_order_type_cf_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '03', '拆卸订单', NULL, 0,
    NULL, NULL, NULL,
    NULL, 'DISASSEMBLY', NULL,
    NULL, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_wo_type_cf 
    WHERE type_name = '拆卸订单' AND deleted = 0
);

-- 工艺路线类别配置
INSERT INTO prd_routings_type_cf (
    type_code, type_name,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'TRIALPRD', '试制',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM p'r'd_routings_type_cf 
    WHERE type_name = '试制' AND deleted = 0
);

INSERT INTO prd_routings_type_cf (
    type_code, type_name,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'STANDPRD', '标准生产',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_routings_type_cf 
    WHERE type_name = '标准生产' AND deleted = 0
);

-- 工艺路线用途配置
INSERT INTO prd_routings_usage_cf (
    usage_code, usage_name, is_engineer_design, is_prd, is_qc, is_cost,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '1', '生产', 0, 1, 0, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_routings_usage_cf 
    WHERE usage_name = '生产' AND deleted = 0
);

-- 工艺路线状态配置
INSERT INTO prd_routings_status_cf (
    status_code, status_name, is_prd, is_qc, is_cost,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'RELEASED', '下达', 1, 1, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_routings_status_cf 
    WHERE status_name = '下达' AND deleted = 0
);

-- 工序控制码配置
INSERT INTO prd_control_keys_cf (
    control_key_code, control_key_name, 
    is_subcontracting_operation, is_key_operation, is_aut_receipt,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '1', '普通工序', 0, 0, 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_control_keys_cf 
    WHERE control_key_name = '普通工序' AND deleted = 0
);

INSERT INTO prd_control_keys_cf (
    control_key_code, control_key_name, 
    is_subcontracting_operation, is_key_operation, is_aut_receipt,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '2', '关键工序', 0, 1, 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_control_keys_cf 
    WHERE control_key_name = '关键工序' AND deleted = 0
);

INSERT INTO prd_control_keys_cf (
    control_key_code, control_key_name, 
    is_subcontracting_operation, is_key_operation, is_aut_receipt,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '3', '入库工序', 0, 1, 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_control_keys_cf 
    WHERE control_key_name = '入库工序' AND deleted = 0
);

INSERT INTO prd_control_keys_cf (
    control_key_code, control_key_name, 
    is_subcontracting_operation, is_key_operation, is_aut_receipt,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '4', '委外工序', 1, 1, 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_control_keys_cf 
    WHERE control_key_name = '委外工序' AND deleted = 0
);

-- 生产移动类型分配配置
INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'PRODECTIN', 4010005, 4010005,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '返修生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'PRODECTIN' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '返修生产订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'PRODECTIN', 4010005, 4010005,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'PRODECTIN' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'PARTSOUT', 4010004, 4010004,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '返修生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'PARTSOUT' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '返修生产订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'PARTSOUT', 4010004, 4010006,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'PARTSOUT' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'PARTSOUT', 4010004, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '拆卸订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'PARTSOUT' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '拆卸订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'DISASSEMBLYIN', 14013001, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '拆卸订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'DISASSEMBLYIN' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '拆卸订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'COPRODUCTIN', 14012001, 4010005,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'COPRODUCTIN' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0)
    AND deleted = 0
);

INSERT INTO prd_mov_assign_cf (
    bussiness_type, mov_type_id, reves_mov_type_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id, wo_type_id, inv_type_id
)
SELECT 
    'BYPRODUCTIN', 14012003, NULL,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0, 
    (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0),
    2000001
WHERE NOT EXISTS (
    SELECT 1 FROM prd_mov_assign_cf 
    WHERE bussiness_type = 'BYPRODUCTIN' 
    AND wo_type_id = (SELECT id FROM prd_wo_type_cf WHERE type_name = '量产生产订单' AND deleted = 0)
    AND deleted = 0
);

-- 成本要素配置
INSERT INTO prd_cost_element (
    code, name, parent_cost_element, cost_category, leaf_node,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '101', '材料费', NULL, 'MATERIAL_COST', 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_element 
    WHERE code = '101' AND deleted = 0
);

INSERT INTO prd_cost_element (
    code, name, parent_cost_element, cost_category, leaf_node,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '201', '人工费', NULL, 'LABOR_COST', 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_element 
    WHERE code = '201' AND deleted = 0
);

INSERT INTO prd_cost_element (
    code, name, parent_cost_element, cost_category, leaf_node,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '301', '机器费', NULL, 'PRODUCTION_COST', 0,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_element 
    WHERE code = '301' AND deleted = 0
);

INSERT INTO prd_cost_element (
    code, name, parent_cost_element, cost_category, leaf_node,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '10101', '原材料', 
    (SELECT id FROM prd_cost_element WHERE code = '101' AND deleted = 0), 
    'MATERIAL_COST', 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_element 
    WHERE code = '10101' AND deleted = 0
);

INSERT INTO prd_cost_element (
    code, name, parent_cost_element, cost_category, leaf_node,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    '10102', '辅料', 
    (SELECT id FROM prd_cost_element WHERE code = '101' AND deleted = 0), 
    'MATERIAL_COST', 1,
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_element 
    WHERE code = '10102' AND deleted = 0
);

-- 成本项目主表配置
INSERT INTO prd_cost_project_head_md (
    code, name, direction,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'XM01', '直接材料', 'FORWARD',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_head_md 
    WHERE code = 'XM01' AND deleted = 0
);

INSERT INTO prd_cost_project_head_md (
    code, name, direction,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'XM02', '直接人工', 'FORWARD',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_head_md 
    WHERE code = 'XM02' AND deleted = 0
);

INSERT INTO prd_cost_project_head_md (
    code, name, direction,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'XM03', '制造费用', 'FORWARD',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_head_md 
    WHERE code = 'XM03' AND deleted = 0
);

-- 成本项目子表配置
INSERT INTO prd_cost_project_item_md (
    cost_project_head_id, cost_element_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM01' AND deleted = 0),
    (SELECT id FROM prd_cost_element WHERE code = '10101' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_item_md pci
    JOIN prd_cost_project_head_md pch ON pci.cost_project_head_id = pch.id
    JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
    WHERE pch.code = 'XM01' AND pce.code = '10101'
    AND pci.deleted = 0 AND pch.deleted = 0 AND pce.deleted = 0
);

INSERT INTO prd_cost_project_item_md (
    cost_project_head_id, cost_element_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM01' AND deleted = 0),
    (SELECT id FROM prd_cost_element WHERE code = '10102' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_item_md pci
    JOIN prd_cost_project_head_md pch ON pci.cost_project_head_id = pch.id
    JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
    WHERE pch.code = 'XM01' AND pce.code = '10102'
    AND pci.deleted = 0 AND pch.deleted = 0 AND pce.deleted = 0
);

INSERT INTO prd_cost_project_item_md (
    cost_project_head_id, cost_element_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM02' AND deleted = 0),
    (SELECT id FROM prd_cost_element WHERE code = '201' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_item_md pci
    JOIN prd_cost_project_head_md pch ON pci.cost_project_head_id = pch.id
    JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
    WHERE pch.code = 'XM02' AND pce.code = '201'
    AND pci.deleted = 0 AND pch.deleted = 0 AND pce.deleted = 0
);

INSERT INTO prd_cost_project_item_md (
    cost_project_head_id, cost_element_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM03' AND deleted = 0),
    (SELECT id FROM prd_cost_element WHERE code = '301' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_item_md pci
    JOIN prd_cost_project_head_md pch ON pci.cost_project_head_id = pch.id
    JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
    WHERE pch.code = 'XM03' AND pce.code = '301'
    AND pci.deleted = 0 AND pch.deleted = 0 AND pce.deleted = 0
);

-- 成本项结构主表配置
INSERT INTO prd_cost_project_structure_head_md (
    code, name, direction,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    'JG01', '标准成本结构', 'FORWARD',
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_structure_head_md 
    WHERE code = 'JG01' AND deleted = 0
);

-- 成本项结构子表配置
INSERT INTO prd_cost_project_structure_item_md (
    prd_cost_project_structure_head_md_id, prd_cost_project_head_md_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_structure_head_md WHERE code = 'JG01' AND deleted = 0),
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM01' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_structure_item_md pcsi
    JOIN prd_cost_project_structure_head_md pcsh ON pcsi.prd_cost_project_structure_head_md_id = pcsh.id
    JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
    WHERE pcsh.code = 'JG01' AND pch.code = 'XM01'
    AND pcsi.deleted = 0 AND pcsh.deleted = 0 AND pch.deleted = 0
);

INSERT INTO prd_cost_project_structure_item_md (
    prd_cost_project_structure_head_md_id, prd_cost_project_head_md_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_structure_head_md WHERE code = 'JG01' AND deleted = 0),
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM02' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_structure_item_md pcsi
    JOIN prd_cost_project_structure_head_md pcsh ON pcsi.prd_cost_project_structure_head_md_id = pcsh.id
    JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
    WHERE pcsh.code = 'JG01' AND pch.code = 'XM02'
    AND pcsi.deleted = 0 AND pcsh.deleted = 0 AND pch.deleted = 0
);

INSERT INTO prd_cost_project_structure_item_md (
    prd_cost_project_structure_head_md_id, prd_cost_project_head_md_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_structure_head_md WHERE code = 'JG01' AND deleted = 0),
    (SELECT id FROM prd_cost_project_head_md WHERE code = 'XM03' AND deleted = 0),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_structure_item_md pcsi
    JOIN prd_cost_project_structure_head_md pcsh ON pcsi.prd_cost_project_structure_head_md_id = pcsh.id
    JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
    WHERE pcsh.code = 'JG01' AND pch.code = 'XM03'
    AND pcsi.deleted = 0 AND pcsh.deleted = 0 AND pch.deleted = 0
);

-- 成本项目结构分配配置
INSERT INTO prd_cost_project_structure_assign_md (
    prd_cost_project_structure_head_md_id, com_id, inv_org_id,
    created_by, updated_by, created_at, updated_at,
    version, deleted, origin_org_id
)
SELECT 
    (SELECT id FROM prd_cost_project_structure_head_md WHERE code = 'JG01' AND deleted = 0),
    (SELECT id FROM org_struct_md 
     WHERE org_status = 'ENABLED' 
     AND org_dimension_code = 'SCM_ORG_GRP' 
     AND org_code = 'AUTOTEST_COM_ORG' 
     LIMIT 1),
    (SELECT id FROM org_struct_md 
     WHERE org_status = 'ENABLED' 
     AND org_dimension_code = 'SCM_ORG_GRP' 
     AND org_code LIKE 'AUTOTEST%' 
     LIMIT 1),
    'SYSTEM', 'SYSTEM', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    0, 0, 0
WHERE NOT EXISTS (
    SELECT 1 FROM prd_cost_project_structure_assign_md pcsa
    JOIN prd_cost_project_structure_head_md pcsh ON pcsa.prd_cost_project_structure_head_md_id = pcsh.id
    WHERE pcsh.code = 'JG01'
    AND pcsa.deleted = 0 AND pcsh.deleted = 0
); 