# -*- coding: utf-8 -*-
"""
生产基础配置初始化
专注于生产管理模块的配置数据管理，包括：
1. 配置数据的初始化
2. 配置数据的验证
3. 配置数据的查询和更新

主要功能：
1. 生产订单配置管理
2. 生产领料配置管理
3. 工艺路线配置管理
4. 成本相关配置管理
5. 组织信息配置管理
"""
import os
from pathlib import Path
from utils.mysql_util import DBManager
from utils.log_util import logger

class PrdConfigInitializer:
    """生产配置初始化器"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db = DBManager()
        self.logger = logger
        
    def ensure_configs_exist(self):
        """确保配置数据存在"""
        try:
            # 检查配置是否存在
            if not self._check_configs_exist():
                # 不存在则初始化
                self.init_configs()
            return True
        except Exception as e:
            self.logger.error(f"确保配置数据存在失败: {str(e)}")
            raise
    
    def _check_configs_exist(self):
        """检查配置是否存在"""
        try:
            # 检查各个配置表是否有数据
            tables = [
                # TODO: 其他配置表检查
                ("prd_issue_type_cf", "生产领料单类型"),
                ("prd_issue_rule_cf", "生产领料分单规则"),
                ("prd_issue_rule_item_cf", "生产领料分单规则明细"),
                ("prd_wo_type_cf", "生产订单类型"),
                ("gen_routings_type_cf", "工艺路线类别"),
                ("gen_routings_usage_cf", "工艺路线用途"),
                ("gen_routings_status_cf", "工艺路线状态"),
                ("gen_control_keys_cf", "工序控制码"),
                ("prd_mov_assign_cf", "生产移动类型分配"),
                ("prd_cost_element", "成本要素"),
                ("prd_cost_project_head_md", "成本项目主表"),
                ("prd_cost_project_item_md", "成本项目子表"),
                ("prd_cost_project_structure_head_md", "成本项结构主表"),
                ("prd_cost_project_structure_item_md", "成本项结构子表"),
                ("prd_cost_project_structure_assign_md", "成本项目结构分配")
            ]
            
            for table, desc in tables:
                count = self.db.query_one(f"SELECT COUNT(1) as cnt FROM {table} WHERE deleted = 0")
                if not count or count["cnt"] == 0:
                    self.logger.warning(f"未找到{desc}数据")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查配置是否存在失败: {str(e)}")
            raise
    
    def init_configs(self):
        """初始化所有配置"""
        try:
            # 获取SQL文件路径
            sql_file = Path(__file__).parent / "sql" / "init_config.sql"
            if not sql_file.exists():
                raise FileNotFoundError(f"SQL文件不存在: {sql_file}")
            
            # 读取SQL文件内容
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            # 执行SQL语句
            self.db.execute(sql_content)
            self.logger.info("生产基础配置初始化完成")
            
            # 验证配置是否存在
            self._verify_configs()
            
        except Exception as e:
            self.logger.error(f"生产基础配置初始化失败: {str(e)}")
            raise
    
    def _verify_configs(self):
        """验证配置是否存在"""
        try:
            # 验证生产领料单类型
            issue_types = self.db.query(
                """
                SELECT type_code, is_issue 
                FROM prd_issue_type_cf 
                WHERE type_code IN ('ISSUE_FORWARD', 'ISSUE_REVERSE')
                AND deleted = 0
                """
            )
            assert len(issue_types) == 2, "未找到完整的生产领料单类型配置"
            
            # 验证正向领料和返向退料配置
            forward_type = next((t for t in issue_types if t["type_code"] == "ISSUE_FORWARD"), None)
            reverse_type = next((t for t in issue_types if t["type_code"] == "ISSUE_REVERSE"), None)
            
            assert forward_type and forward_type["is_issue"] == 1, "正向领料单据配置错误"
            assert reverse_type and reverse_type["is_issue"] == 0, "返向退料单据配置错误"
            
            # 验证分单规则配置
            rule = self.db.query_one(
                """
                SELECT id, code, name 
                FROM prd_issue_rule_cf 
                WHERE code = 'DEFAULT_RULE'
                AND deleted = 0
                """
            )
            assert rule, "未找到默认分单规则配置"
            
            # 验证分单规则明细配置
            rule_items = self.db.query(
                """
                SELECT item, default_value, is_modified
                FROM prd_issue_rule_item_cf
                WHERE prd_issue_rule_cf_id = %s
                AND deleted = 0
                """,
                (rule["id"],)
            )
            assert len(rule_items) == 7, "分单规则明细配置不完整"
            
            # 验证必要的分单规则项
            required_items = {
                'INV_ORG': {'default_value': 1, 'is_modified': 0},
                'INV_LOC': {'default_value': 1, 'is_modified': 1},
                'WORK_CENTER': {'default_value': 1, 'is_modified': 1}
            }
            
            for item in rule_items:
                if item["item"] in required_items:
                    expected = required_items[item["item"]]
                    assert item["default_value"] == expected["default_value"], \
                        f"分单规则项 {item['item']} 的默认值配置错误"
                    assert item["is_modified"] == expected["is_modified"], \
                        f"分单规则项 {item['item']} 的可修改标志配置错误"
            
            # 验证生产订单类型配置
            wo_types = self.db.query(
                """
                SELECT type_code, type_name, business_type
                FROM prd_wo_type_cf 
                WHERE type_code IN ('01', '02', '03')
                AND deleted = 0
                """
            )
            assert len(wo_types) == 3, "未找到完整的生产订单类型配置"
            
            # 验证各类型配置
            type_map = {t["type_code"]: t for t in wo_types}
            
            # 验证量产订单
            standard_type = type_map.get("01")
            assert standard_type and standard_type["business_type"] == "STANDARD", \
                "量产生产订单配置错误"
            
            # 验证返修订单
            repair_type = type_map.get("02")
            assert repair_type and repair_type["business_type"] == "REPAIR", \
                "返修生产订单配置错误"
            
            # 验证拆卸订单
            disassembly_type = type_map.get("03")
            assert disassembly_type and disassembly_type["business_type"] == "DISASSEMBLY", \
                "拆卸订单配置错误"
            
            # 验证工艺路线类别配置
            routing_types = self.db.query(
                """
                SELECT type_code, type_name
                FROM gen_routings_type_cf 
                WHERE type_code IN ('TRIALPRD', 'STANDPRD')
                AND deleted = 0
                """
            )
            assert len(routing_types) == 2, "未找到完整的工艺路线类别配置"
            
            # 验证各类型配置
            type_map = {t["type_code"]: t for t in routing_types}
            
            # 验证试制类型
            trial_type = type_map.get("TRIALPRD")
            assert trial_type and trial_type["type_name"] == "试制", \
                "试制工艺路线类别配置错误"
            
            # 验证标准生产类型
            standard_type = type_map.get("STANDPRD")
            assert standard_type and standard_type["type_name"] == "标准生产", \
                "标准生产工艺路线类别配置错误"
            
            # 验证工艺路线用途配置
            routing_usage = self.db.query_one(
                """
                SELECT usage_code, usage_name, is_prd, is_cost
                FROM gen_routings_usage_cf 
                WHERE usage_name = '生产'
                AND deleted = 0
                """
            )
            assert routing_usage, "未找到生产用途的工艺路线配置"
            assert routing_usage["is_prd"] == 1, "工艺路线生产用途的生产标志配置错误"
            assert routing_usage["is_cost"] == 1, "工艺路线生产用途的成本标志配置错误"
            
            # 验证工艺路线状态配置
            routing_status = self.db.query_one(
                """
                SELECT status_code, status_name, is_prd, is_qc, is_cost
                FROM gen_routings_status_cf 
                WHERE status_name = '下达'
                AND deleted = 0
                """
            )
            assert routing_status, "未找到下达状态的工艺路线配置"
            assert routing_status["is_prd"] == 1, "工艺路线下达状态的生产标志配置错误"
            assert routing_status["is_qc"] == 1, "工艺路线下达状态的质检标志配置错误"
            assert routing_status["is_cost"] == 1, "工艺路线下达状态的成本标志配置错误"
            
            # 验证工序控制码配置
            control_keys = self.db.query(
                """
                SELECT 
                    control_key_code, control_key_name,
                    is_subcontracting_operation, is_key_operation, is_aut_receipt
                FROM gen_control_keys_cf 
                WHERE control_key_code IN ('1', '2', '3', '4')
                AND deleted = 0
                """
            )
            assert len(control_keys) == 4, "未找到完整的工序控制码配置"
            
            # 验证各类型配置
            key_map = {k["control_key_code"]: k for k in control_keys}
            
            # 验证普通工序
            normal_key = key_map.get("1")
            assert normal_key and normal_key["control_key_name"] == "普通工序", "普通工序配置错误"
            assert normal_key["is_key_operation"] == 0, "普通工序关键工序标志配置错误"
            assert normal_key["is_aut_receipt"] == 0, "普通工序自动收货标志配置错误"
            assert normal_key["is_subcontracting_operation"] == 0, "普通工序委外标志配置错误"
            
            # 验证关键工序
            key_operation = key_map.get("2")
            assert key_operation and key_operation["control_key_name"] == "关键工序", "关键工序配置错误"
            assert key_operation["is_key_operation"] == 1, "关键工序关键工序标志配置错误"
            assert key_operation["is_aut_receipt"] == 0, "关键工序自动收货标志配置错误"
            assert key_operation["is_subcontracting_operation"] == 0, "关键工序委外标志配置错误"
            
            # 验证入库工序
            receipt_key = key_map.get("3")
            assert receipt_key and receipt_key["control_key_name"] == "入库工序", "入库工序配置错误"
            assert receipt_key["is_key_operation"] == 1, "入库工序关键工序标志配置错误"
            assert receipt_key["is_aut_receipt"] == 1, "入库工序自动收货标志配置错误"
            assert receipt_key["is_subcontracting_operation"] == 0, "入库工序委外标志配置错误"
            
            # 验证委外工序
            subcontract_key = key_map.get("4")
            assert subcontract_key and subcontract_key["control_key_name"] == "委外工序", "委外工序配置错误"
            assert subcontract_key["is_key_operation"] == 1, "委外工序关键工序标志配置错误"
            assert subcontract_key["is_aut_receipt"] == 0, "委外工序自动收货标志配置错误"
            assert subcontract_key["is_subcontracting_operation"] == 1, "委外工序委外标志配置错误"
            
            # 验证生产移动类型分配
            mov_assigns = self.db.query(
                """
                SELECT 
                    m.bussiness_type, m.mov_type_id, m.reves_mov_type_id,
                    w.type_name, w.business_type
                FROM prd_mov_assign_cf m
                JOIN prd_wo_type_cf w ON m.wo_type_id = w.id
                WHERE m.deleted = 0 AND w.deleted = 0
                ORDER BY w.type_name, m.bussiness_type
                """
            )
            assert len(mov_assigns) >= 8, "生产移动类型分配配置不完整"
            
            # 验证量产生产订单的移动类型
            standard_assigns = [m for m in mov_assigns if m["type_name"] == "量产生产订单"]
            assert len(standard_assigns) >= 4, "量产生产订单的移动类型分配不完整"
            assert any(m["bussiness_type"] == "PRODECTIN" for m in standard_assigns), "量产生产订单缺少完工入库移动类型"
            assert any(m["bussiness_type"] == "PARTSOUT" for m in standard_assigns), "量产生产订单缺少材料出库移动类型"
            assert any(m["bussiness_type"] == "COPRODUCTIN" for m in standard_assigns), "量产生产订单缺少联产品入库移动类型"
            assert any(m["bussiness_type"] == "BYPRODUCTIN" for m in standard_assigns), "量产生产订单缺少副产品入库移动类型"
            
            # 验证返修生产订单的移动类型
            repair_assigns = [m for m in mov_assigns if m["type_name"] == "返修生产订单"]
            assert len(repair_assigns) >= 2, "返修生产订单的移动类型分配不完整"
            assert any(m["bussiness_type"] == "PRODECTIN" for m in repair_assigns), "返修生产订单缺少完工入库移动类型"
            assert any(m["bussiness_type"] == "PARTSOUT" for m in repair_assigns), "返修生产订单缺少材料出库移动类型"
            
            # 验证拆卸订单的移动类型
            disassembly_assigns = [m for m in mov_assigns if m["type_name"] == "拆卸订单"]
            assert len(disassembly_assigns) >= 2, "拆卸订单的移动类型分配不完整"
            assert any(m["bussiness_type"] == "PARTSOUT" for m in disassembly_assigns), "拆卸订单缺少材料出库移动类型"
            assert any(m["bussiness_type"] == "DISASSEMBLYIN" for m in disassembly_assigns), "拆卸订单缺少拆卸入库移动类型"
            
            # 验证成本要素配置
            cost_elements = self.db.query(
                """
                SELECT 
                    code, name, parent_cost_element, cost_category, leaf_node
                FROM prd_cost_element 
                WHERE code IN ('101', '201', '301', '10101', '10102')
                AND deleted = 0
                ORDER BY code
                """
            )
            assert len(cost_elements) == 5, "未找到完整的成本要素配置"
            
            # 验证各要素配置
            element_map = {e["code"]: e for e in cost_elements}
            
            # 验证一级要素
            material_cost = element_map.get("101")
            assert material_cost and material_cost["name"] == "材料费", "材料费配置错误"
            assert material_cost["parent_cost_element"] is None, "材料费父级配置错误"
            assert material_cost["cost_category"] == "MATERIAL_COST", "材料费成本类别配置错误"
            assert material_cost["leaf_node"] == 0, "材料费叶子节点标志配置错误"
            
            labor_cost = element_map.get("201")
            assert labor_cost and labor_cost["name"] == "人工费", "人工费配置错误"
            assert labor_cost["parent_cost_element"] is None, "人工费父级配置错误"
            assert labor_cost["cost_category"] == "LABOR_COST", "人工费成本类别配置错误"
            assert labor_cost["leaf_node"] == 0, "人工费叶子节点标志配置错误"
            
            production_cost = element_map.get("301")
            assert production_cost and production_cost["name"] == "机器费", "机器费配置错误"
            assert production_cost["parent_cost_element"] is None, "机器费父级配置错误"
            assert production_cost["cost_category"] == "PRODUCTION_COST", "机器费成本类别配置错误"
            assert production_cost["leaf_node"] == 0, "机器费叶子节点标志配置错误"
            
            # 验证二级要素
            raw_material = element_map.get("10101")
            assert raw_material and raw_material["name"] == "原材料", "原材料配置错误"
            assert raw_material["parent_cost_element"] == material_cost["id"], "原材料父级配置错误"
            assert raw_material["cost_category"] == "MATERIAL_COST", "原材料成本类别配置错误"
            assert raw_material["leaf_node"] == 1, "原材料叶子节点标志配置错误"
            
            auxiliary_material = element_map.get("10102")
            assert auxiliary_material and auxiliary_material["name"] == "辅料", "辅料配置错误"
            assert auxiliary_material["parent_cost_element"] == material_cost["id"], "辅料父级配置错误"
            assert auxiliary_material["cost_category"] == "MATERIAL_COST", "辅料成本类别配置错误"
            assert auxiliary_material["leaf_node"] == 1, "辅料叶子节点标志配置错误"
            
            # 验证成本项目配置
            cost_projects = self.db.query(
                """
                SELECT 
                    pch.code, pch.name, pch.direction,
                    pce.code as element_code, pce.name as element_name
                FROM prd_cost_project_head_md pch
                JOIN prd_cost_project_item_md pci ON pch.id = pci.cost_project_head_id
                JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
                WHERE pch.deleted = 0 AND pci.deleted = 0 AND pce.deleted = 0
                ORDER BY pch.code, pce.code
                """
            )
            assert len(cost_projects) == 4, "未找到完整的成本项目配置"
            
            # 验证各项目配置
            project_map = {}
            for project in cost_projects:
                if project["code"] not in project_map:
                    project_map[project["code"]] = {
                        "name": project["name"],
                        "direction": project["direction"],
                        "elements": []
                    }
                project_map[project["code"]]["elements"].append({
                    "code": project["element_code"],
                    "name": project["element_name"]
                })
            
            # 验证直接材料项目
            material_project = project_map.get("XM01")
            assert material_project and material_project["name"] == "直接材料", "直接材料项目配置错误"
            assert material_project["direction"] == "FORWARD", "直接材料项目方向配置错误"
            assert len(material_project["elements"]) == 2, "直接材料项目成本要素配置错误"
            material_elements = {e["code"]: e["name"] for e in material_project["elements"]}
            assert "10101" in material_elements and material_elements["10101"] == "原材料", "直接材料项目原材料要素配置错误"
            assert "10102" in material_elements and material_elements["10102"] == "辅料", "直接材料项目辅料要素配置错误"
            
            # 验证直接人工项目
            labor_project = project_map.get("XM02")
            assert labor_project and labor_project["name"] == "直接人工", "直接人工项目配置错误"
            assert labor_project["direction"] == "FORWARD", "直接人工项目方向配置错误"
            assert len(labor_project["elements"]) == 1, "直接人工项目成本要素配置错误"
            assert labor_project["elements"][0]["code"] == "201", "直接人工项目人工费要素配置错误"
            
            # 验证制造费用项目
            production_project = project_map.get("XM03")
            assert production_project and production_project["name"] == "制造费用", "制造费用项目配置错误"
            assert production_project["direction"] == "FORWARD", "制造费用项目方向配置错误"
            assert len(production_project["elements"]) == 1, "制造费用项目成本要素配置错误"
            assert production_project["elements"][0]["code"] == "301", "制造费用项目机器费要素配置错误"
            
            # 验证成本项结构配置
            cost_structure = self.db.query(
                """
                SELECT 
                    pcsh.code, pcsh.name, pcsh.direction,
                    pch.code as project_code, pch.name as project_name
                FROM prd_cost_project_structure_head_md pcsh
                JOIN prd_cost_project_structure_item_md pcsi ON pcsh.id = pcsi.prd_cost_project_structure_head_md_id
                JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
                WHERE pcsh.deleted = 0 AND pcsi.deleted = 0 AND pch.deleted = 0
                ORDER BY pcsh.code, pch.code
                """
            )
            assert len(cost_structure) == 3, "未找到完整的成本项结构配置"
            
            # 验证标准成本结构
            structure = next((s for s in cost_structure if s["code"] == "JG01"), None)
            assert structure and structure["name"] == "标准成本结构", "标准成本结构配置错误"
            assert structure["direction"] == "FORWARD", "标准成本结构方向配置错误"
            
            # 验证结构包含的成本项目
            project_codes = {s["project_code"] for s in cost_structure}
            assert "XM01" in project_codes, "标准成本结构缺少直接材料项目"
            assert "XM02" in project_codes, "标准成本结构缺少直接人工项目"
            assert "XM03" in project_codes, "标准成本结构缺少制造费用项目"
            
            # 验证成本项目结构分配配置
            cost_structure_assign = self.db.query(
                """
                SELECT 
                    pcsa.id, pcsh.id as structure_id,
                    pcsh.code as structure_code, pcsh.name as structure_name,
                    os_com.id as com_id, os_com.org_code as com_code, 
                    os_com.org_name as com_name,
                    os_inv.id as inv_id, os_inv.org_code as inv_code, 
                    os_inv.org_name as inv_name
                FROM prd_cost_project_structure_assign_md pcsa
                JOIN prd_cost_project_structure_head_md pcsh ON pcsa.prd_cost_project_structure_head_md_id = pcsh.id
                JOIN org_struct_md os_com ON pcsa.com_id = os_com.id
                JOIN org_struct_md os_inv ON pcsa.inv_org_id = os_inv.id
                WHERE pcsa.deleted = 0 AND pcsh.deleted = 0 
                AND os_com.org_status = 'ENABLED' AND os_com.org_dimension_code = 'SCM_ORG_GRP'
                AND os_inv.org_status = 'ENABLED' AND os_inv.org_dimension_code = 'SCM_ORG_GRP'
                """
            )
            assert len(cost_structure_assign) > 0, "未找到成本项目结构分配配置"
            
            # 验证标准成本结构分配
            assign = next((a for a in cost_structure_assign if a["structure_code"] == "JG01"), None)
            assert assign, "标准成本结构分配配置错误"
            assert assign["com_code"], "公司组织配置错误"
            assert assign["inv_code"], "库存组织配置错误"
            
            self.logger.info("生产基础配置验证通过")
            
        except Exception as e:
            self.logger.error(f"生产基础配置验证失败: {str(e)}")
            raise
    
    def get_issue_types(self):
        """获取生产领料单类型配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    id, type_code, type_name, code_rules,
                    is_created_by_push, is_issue
                FROM prd_issue_type_cf 
                WHERE type_code IN ('ISSUE_FORWARD', 'ISSUE_REVERSE')
                AND deleted = 0
                """
            )
        except Exception as e:
            self.logger.error(f"获取生产领料单类型配置失败: {str(e)}")
            raise
    
    def get_issue_rules(self):
        """获取生产领料分单规则配置"""
        try:
            rule = self.db.query_one(
                """
                SELECT 
                    id, code, name, default_value
                FROM prd_issue_rule_cf 
                WHERE code = 'DEFAULT_RULE'
                AND deleted = 0
                """
            )
            
            if not rule:
                return None
            
            # 获取规则明细
            rule_items = self.db.query(
                """
                SELECT 
                    id, item, default_value, is_modified
                FROM prd_issue_rule_item_cf
                WHERE prd_issue_rule_cf_id = %s
                AND deleted = 0
                ORDER BY item
                """,
                (rule["id"],)
            )
            
            return {
                "rule": rule,
                "items": rule_items
            }
            
        except Exception as e:
            self.logger.error(f"获取生产领料分单规则配置失败: {str(e)}")
            raise
    
    def get_wo_types(self):
        """获取生产订单类型配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    id, type_code, type_name, code_rules,
                    external_code_is, vrs_select_mode,
                    inv_type_cf_id, business_type,
                    pur_pr_head_type_cf_id
                FROM prd_wo_type_cf 
                WHERE type_code IN ('01', '02', '03')
                AND deleted = 0
                ORDER BY type_code
                """
            )
        except Exception as e:
            self.logger.error(f"获取生产订单类型配置失败: {str(e)}")
            raise
    
    def get_wo_type_by_business(self, business_type):
        """根据业务类型获取生产订单类型配置
        Args:
            business_type: 业务类型(STANDARD/REPAIR/DISASSEMBLY)
        Returns:
            dict: 订单类型配置
        """
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, type_code, type_name, code_rules,
                    external_code_is, vrs_select_mode,
                    inv_type_cf_id, business_type,
                    pur_pr_head_type_cf_id
                FROM prd_wo_type_cf 
                WHERE business_type = %s
                AND deleted = 0
                """,
                (business_type,)
            )
        except Exception as e:
            self.logger.error(f"获取生产订单类型配置失败: {str(e)}")
            raise
            
    def get_routing_types(self):
        """获取工艺路线类别配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    id, type_code, type_name
                FROM gen_routings_type_cf 
                WHERE type_code IN ('TRIALPRD', 'STANDPRD')
                AND deleted = 0
                ORDER BY type_code
                """
            )
        except Exception as e:
            self.logger.error(f"获取工艺路线类别配置失败: {str(e)}")
            raise
    
    def get_routing_type_by_code(self, type_code):
        """根据类型代码获取工艺路线类别配置
        Args:
            type_code: 类型代码(TRIALPRD/STANDPRD)
        Returns:
            dict: 工艺路线类别配置
        """
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, type_code, type_name
                FROM gen_routings_type_cf 
                WHERE type_code = %s
                AND deleted = 0
                """,
                (type_code,)
            )
        except Exception as e:
            self.logger.error(f"获取工艺路线类别配置失败: {str(e)}")
            raise
            
    def get_routing_usage(self):
        """获取工艺路线用途配置"""
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, usage_code, usage_name,
                    is_engineer_design, is_prd, is_qc, is_cost
                FROM gen_routings_usage_cf 
                WHERE usage_name = '生产'
                AND deleted = 0
                """
            )
        except Exception as e:
            self.logger.error(f"获取工艺路线用途配置失败: {str(e)}")
            raise
            
    def get_routing_status(self):
        """获取工艺路线状态配置"""
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, status_code, status_name,
                    is_prd, is_qc, is_cost
                FROM gen_routings_status_cf 
                WHERE status_name = '下达'
                AND deleted = 0
                """
            )
        except Exception as e:
            self.logger.error(f"获取工艺路线状态配置失败: {str(e)}")
            raise
            
    def get_control_keys(self):
        """获取工序控制码配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    id, control_key_code, control_key_name,
                    is_subcontracting_operation, is_key_operation, is_aut_receipt
                FROM gen_control_keys_cf 
                WHERE control_key_code IN ('1', '2', '3', '4')
                AND deleted = 0
                ORDER BY control_key_code
                """
            )
        except Exception as e:
            self.logger.error(f"获取工序控制码配置失败: {str(e)}")
            raise
    
    def get_control_key_by_code(self, control_key_code):
        """根据控制码获取工序控制码配置
        Args:
            control_key_code: 控制码(1/2/3/4)
        Returns:
            dict: 工序控制码配置
        """
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, control_key_code, control_key_name,
                    is_subcontracting_operation, is_key_operation, is_aut_receipt
                FROM gen_control_keys_cf 
                WHERE control_key_code = %s
                AND deleted = 0
                """,
                (control_key_code,)
            )
        except Exception as e:
            self.logger.error(f"获取工序控制码配置失败: {str(e)}")
            raise
            
    def get_mov_assign_by_type(self, wo_type_name, business_type):
        """根据生产订单类型名称和业务类型获取移动类型分配
        
        Args:
            wo_type_name (str): 生产订单类型名称
            business_type (str): 业务类型
            
        Returns:
            dict: 移动类型分配信息
        """
        try:
            mov_assign = self.db.query_one(
                """
                SELECT m.* 
                FROM prd_mov_assign_cf m
                JOIN prd_wo_type_cf w ON m.wo_type_id = w.id
                WHERE w.type_name = %s 
                AND m.bussiness_type = %s
                AND m.deleted = 0
                AND w.deleted = 0
                """,
                [wo_type_name, business_type]
            )
            return mov_assign
        except Exception as e:
            self.logger.error(f"获取移动类型分配异常: {str(e)}")
            return None
            
    def get_cost_elements(self):
        """获取成本要素配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    id, code, name, parent_cost_element,
                    cost_category, leaf_node
                FROM prd_cost_element 
                WHERE code IN ('101', '201', '301', '10101', '10102')
                AND deleted = 0
                ORDER BY code
                """
            )
        except Exception as e:
            self.logger.error(f"获取成本要素配置失败: {str(e)}")
            raise
    
    def get_cost_element_by_code(self, code):
        """根据代码获取成本要素配置
        Args:
            code: 成本要素代码
        Returns:
            dict: 成本要素配置
        """
        try:
            return self.db.query_one(
                """
                SELECT 
                    id, code, name, parent_cost_element,
                    cost_category, leaf_node
                FROM prd_cost_element 
                WHERE code = %s
                AND deleted = 0
                """,
                (code,)
            )
        except Exception as e:
            self.logger.error(f"获取成本要素配置失败: {str(e)}")
            raise
            
    def get_cost_projects(self):
        """获取成本项目配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    pch.id as head_id, pch.code, pch.name, pch.direction,
                    pci.id as item_id, pci.cost_element_id,
                    pce.code as element_code, pce.name as element_name,
                    pce.cost_category, pce.leaf_node
                FROM prd_cost_project_head_md pch
                JOIN prd_cost_project_item_md pci ON pch.id = pci.cost_project_head_id
                JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
                WHERE pch.deleted = 0 AND pci.deleted = 0 AND pce.deleted = 0
                ORDER BY pch.code, pce.code
                """
            )
        except Exception as e:
            self.logger.error(f"获取成本项目配置失败: {str(e)}")
            raise
    
    def get_cost_project_by_code(self, code):
        """根据代码获取成本项目配置
        Args:
            code: 成本项目代码
        Returns:
            dict: 成本项目配置
        """
        try:
            return self.db.query(
                """
                SELECT 
                    pch.id as head_id, pch.code, pch.name, pch.direction,
                    pci.id as item_id, pci.cost_element_id,
                    pce.code as element_code, pce.name as element_name,
                    pce.cost_category, pce.leaf_node
                FROM prd_cost_project_head_md pch
                JOIN prd_cost_project_item_md pci ON pch.id = pci.cost_project_head_id
                JOIN prd_cost_element pce ON pci.cost_element_id = pce.id
                WHERE pch.code = %s
                AND pch.deleted = 0 AND pci.deleted = 0 AND pce.deleted = 0
                ORDER BY pce.code
                """,
                (code,)
            )
        except Exception as e:
            self.logger.error(f"获取成本项目配置失败: {str(e)}")
            raise
            
    def get_cost_structures(self):
        """获取成本项结构配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    pcsh.id as head_id, pcsh.code, pcsh.name, pcsh.direction,
                    pcsi.id as item_id,
                    pch.id as project_id, pch.code as project_code, 
                    pch.name as project_name, pch.direction as project_direction
                FROM prd_cost_project_structure_head_md pcsh
                JOIN prd_cost_project_structure_item_md pcsi ON pcsh.id = pcsi.prd_cost_project_structure_head_md_id
                JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
                WHERE pcsh.deleted = 0 AND pcsi.deleted = 0 AND pch.deleted = 0
                ORDER BY pcsh.code, pch.code
                """
            )
        except Exception as e:
            self.logger.error(f"获取成本项结构配置失败: {str(e)}")
            raise
    
    def get_cost_structure_by_code(self, code):
        """根据代码获取成本项结构配置
        Args:
            code: 成本项结构代码
        Returns:
            dict: 成本项结构配置
        """
        try:
            return self.db.query(
                """
                SELECT 
                    pcsh.id as head_id, pcsh.code, pcsh.name, pcsh.direction,
                    pcsi.id as item_id,
                    pch.id as project_id, pch.code as project_code, 
                    pch.name as project_name, pch.direction as project_direction
                FROM prd_cost_project_structure_head_md pcsh
                JOIN prd_cost_project_structure_item_md pcsi ON pcsh.id = pcsi.prd_cost_project_structure_head_md_id
                JOIN prd_cost_project_head_md pch ON pcsi.prd_cost_project_head_md_id = pch.id
                WHERE pcsh.code = %s
                AND pcsh.deleted = 0 AND pcsi.deleted = 0 AND pch.deleted = 0
                ORDER BY pch.code
                """,
                (code,)
            )
        except Exception as e:
            self.logger.error(f"获取成本项结构配置失败: {str(e)}")
            raise
            
    def get_cost_structure_assigns(self):
        """获取成本项目结构分配配置"""
        try:
            return self.db.query(
                """
                SELECT 
                    pcsa.id, pcsh.id as structure_id,
                    pcsh.code as structure_code, pcsh.name as structure_name,
                    os_com.id as com_id, os_com.org_code as com_code, 
                    os_com.org_name as com_name,
                    os_inv.id as inv_id, os_inv.org_code as inv_code, 
                    os_inv.org_name as inv_name
                FROM prd_cost_project_structure_assign_md pcsa
                JOIN prd_cost_project_structure_head_md pcsh ON pcsa.prd_cost_project_structure_head_md_id = pcsh.id
                JOIN org_struct_md os_com ON pcsa.com_id = os_com.id
                JOIN org_struct_md os_inv ON pcsa.inv_org_id = os_inv.id
                WHERE pcsa.deleted = 0 AND pcsh.deleted = 0 
                AND os_com.org_status = 'ENABLED' AND os_com.org_dimension_code = 'SCM_ORG_GRP'
                AND os_inv.org_status = 'ENABLED' AND os_inv.org_dimension_code = 'SCM_ORG_GRP'
                """
            )
        except Exception as e:
            self.logger.error(f"获取成本项目结构分配配置失败: {str(e)}")
            raise
    
    def get_cost_structure_assign_by_structure_code(self, structure_code):
        """根据成本项目结构代码获取分配配置
        Args:
            structure_code: 成本项目结构代码
        Returns:
            dict: 成本项目结构分配配置
        """
        try:
            return self.db.query(
                """
                SELECT 
                    pcsa.id, pcsh.id as structure_id,
                    pcsh.code as structure_code, pcsh.name as structure_name,
                    os_com.id as com_id, os_com.org_code as com_code, 
                    os_com.org_name as com_name,
                    os_inv.id as inv_id, os_inv.org_code as inv_code, 
                    os_inv.org_name as inv_name
                FROM prd_cost_project_structure_assign_md pcsa
                JOIN prd_cost_project_structure_head_md pcsh ON pcsa.prd_cost_project_structure_head_md_id = pcsh.id
                JOIN org_struct_md os_com ON pcsa.com_id = os_com.id
                JOIN org_struct_md os_inv ON pcsa.inv_org_id = os_inv.id
                WHERE pcsh.code = %s
                AND pcsa.deleted = 0 AND pcsh.deleted = 0 
                AND os_com.org_status = 'ENABLED' AND os_com.org_dimension_code = 'SCM_ORG_GRP'
                AND os_inv.org_status = 'ENABLED' AND os_inv.org_dimension_code = 'SCM_ORG_GRP'
                """,
                (structure_code,)
            )
        except Exception as e:
            self.logger.error(f"获取成本项目结构分配配置失败: {str(e)}")
            raise 