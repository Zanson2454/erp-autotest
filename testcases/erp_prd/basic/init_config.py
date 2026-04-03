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

from pathlib import Path

from utils.log_util import logger
from utils.mysql_util import DBManager


class PrdConfigInitializer:
    """生产配置初始化器"""

    def __init__(self):
        """初始化数据库连接"""
        self.query_service = DBManager()  # 无参数调用，使用兼容模式
        self.logger = logger

    def _ensure_query_service(self):
        """兼容保护：少数旧调用链可能绕过 __init__，此处兜底补齐属性。"""
        if not hasattr(self, "query_service") or self.query_service is None:
            self.query_service = DBManager()
        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logger

    def ensure_configs_exist(self):
        """确保配置数据存在"""
        try:
            self._ensure_query_service()
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
            self._ensure_query_service()
            # 检查各个配置表是否有数据
            tables = [
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
                ("prd_cost_project_structure_assign_md", "成本项目结构分配"),
            ]

            for table, desc in tables:
                count = self.query_service.query(f"SELECT COUNT(1) as cnt FROM {table} WHERE deleted = 0")
                if not count or not count[0]["cnt"]:
                    self.logger.warning(f"未找到{desc}数据")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"检查配置是否存在失败: {str(e)}")
            raise

    def init_configs(self):
        """初始化所有配置"""
        try:
            self._ensure_query_service()
            # 获取SQL文件路径
            sql_file = Path(__file__).parent / "sql" / "init_config.sql"
            if not sql_file.exists():
                raise FileNotFoundError(f"SQL文件不存在: {sql_file}")

            # 读取SQL文件内容
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # 分割SQL语句
            sql_statements = sql_content.split(";")

            # 按顺序执行SQL语句
            for sql in sql_statements:
                sql = sql.strip()
                if sql and not sql.startswith("--"):  # 跳过空语句和注释
                    try:
                        self.query_service.execute(sql)
                        self.logger.info(f"SQL执行成功: {sql[:100]}...")  # 只记录前100个字符
                    except Exception as e:
                        self.logger.error(f"SQL执行失败: {str(e)}")
                        self.logger.error(f"SQL: {sql}")
                        raise

            self.logger.info("生产基础配置初始化完成")

            # 验证配置是否存在
            self._verify_configs()

        except Exception as e:
            self.logger.error(f"生产基础配置初始化失败: {str(e)}")
            raise

    def _verify_configs(self):
        """验证配置是否存在"""
        try:
            self._ensure_query_service()
            # 检查生产领料单类型配置
            issue_types = self.query_service.query("""
                SELECT type_code, is_issue 
                FROM prd_issue_type_cf 
                WHERE type_code IN ('ISSUE_FORWARD', 'ISSUE_REVERSE')
                AND deleted = 0
                """)
            self.logger.debug(f"生产领料单类型配置: {issue_types}")
            if not issue_types:
                self.logger.error("未找到生产领料单类型配置")
                return False

            # 检查生产领料规则配置
            issue_rules = self.query_service.query("""
                SELECT id, name, is_default
                FROM prd_issue_rule_cf 
                WHERE name = 'DEFAULT_RULE'
                AND deleted = 0
                """)
            self.logger.debug(f"生产领料规则配置: {issue_rules}")
            if not issue_rules:
                self.logger.error("未找到生产领料规则配置")
                return False

            # 检查生产领料规则项配置
            issue_rule_items = self.query_service.query("""
                SELECT pcsi.item, pcsi.default_value, pcsi.is_modified
                FROM prd_issue_rule_item_cf pcsi
                JOIN prd_issue_rule_cf pcsh ON pcsi.prd_issue_rule_cf_id = pcsh.id
                WHERE pcsh.name = 'DEFAULT_RULE'
                AND pcsi.deleted = 0 AND pcsh.deleted = 0
                """)
            self.logger.debug(f"生产领料规则项配置: {issue_rule_items}")
            if not issue_rule_items:
                self.logger.error("未找到生产领料规则项配置")
                return False

            # 检查生产工单类型配置
            wo_types = self.query_service.query("""
                SELECT id, type_code, type_name
                FROM prd_wo_type_cf 
                WHERE deleted = 0
                """)
            self.logger.debug(f"生产工单类型配置: {wo_types}")
            if not wo_types:
                self.logger.error("未找到生产工单类型配置")
                return False

            # 检查工艺路线类型配置
            routing_types = self.query_service.query("""
                SELECT id, type_code, type_name
                FROM gen_routings_type_cf 
                WHERE deleted = 0
                """)
            self.logger.debug(f"工艺路线类型配置: {routing_types}")
            if not routing_types:
                self.logger.error("未找到工艺路线类型配置")
                return False

            return True

        except Exception as e:
            self.logger.error(f"验证配置失败: {str(e)}")
            return False
