import os
import sys
from typing import Dict, List, Any, Optional
import yaml
from loguru import logger
from utils.mysql_util import DBManager
from utils.yaml_util import YamlReader

class CleanupManager:
    """数据清理管理器"""
    
    def __init__(self):
        """初始化数据清理管理器"""
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "cleanup",
            "cleanup.yaml"
        )
        self.config = self._load_config()
        self.db = DBManager()
        self.yaml_helper = YamlReader(self.config_path)
        
    def _load_config(self) -> Dict[str, Any]:
        """加载清理配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载清理配置失败: {str(e)}")
            raise
            
    def cleanup_module(self, module_name: str, params: Dict[str, Any]) -> None:
        """清理指定模块的数据
        
        Args:
            module_name: 模块名称
            params: 清理参数
        """
        if module_name not in self.config['modules']:
            logger.warning(f"模块 {module_name} 不存在")
            return
            
        module_config = self.config['modules'][module_name]
        logger.info(f"开始清理模块 {module_name}: {module_config['description']}")
        
        # 获取需要清理的表，按依赖关系排序
        tables = self._get_sorted_tables(module_config['tables'])
        
        try:
            with self.db as db:
                if self.config['config']['transaction']:
                    db.connection.begin()
                    
                for table in tables:
                    self._cleanup_table(db, table, params)
                    
                if self.config['config']['transaction']:
                    db.connection.commit()
                    
        except Exception as e:
            if self.config['config']['transaction']:
                db.connection.rollback()
            logger.error(f"清理模块 {module_name} 失败: {str(e)}")
            raise
            
    def _get_sorted_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取按依赖关系排序的表
        
        Args:
            tables: 表配置列表
            
        Returns:
            排序后的表配置列表
        """
        # TODO: 实现拓扑排序，确保依赖表先被清理
        return tables
        
    def _cleanup_table(self, db: DBManager, table: Dict[str, Any], params: Dict[str, Any]) -> None:
        """清理指定表的数据
        
        Args:
            db: 数据库管理器
            table: 表配置
            params: 清理参数
        """
        try:
            # 渲染SQL模板
            sql = self.yaml_helper.render_template(table['sql'], params)
            
            if self.config['config']['dry_run']:
                logger.info(f"DRY RUN: {sql}")
                return
                
            # 执行清理
            affected_rows = db.execute_update(sql)
            logger.info(f"清理表 {table['name']} 完成，影响行数: {affected_rows}")
            
        except Exception as e:
            logger.error(f"清理表 {table['name']} 失败: {str(e)}")
            if self.config['config']['error_handling'] == 'stop':
                raise
            elif self.config['config']['error_handling'] == 'rollback':
                raise
            # continue 模式下继续执行
            
    def cleanup_all(self, params: Dict[str, Any]) -> None:
        """清理所有模块的数据
        
        Args:
            params: 清理参数
        """
        for module_name in self.config['modules']:
            self.cleanup_module(module_name, params) 