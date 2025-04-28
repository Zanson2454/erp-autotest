import os
import sys
from pathlib import Path


class PathUtil:
    """路径工具类"""
    
    _project_root = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """获取项目根目录
        
        Returns:
            Path: 项目根目录路径
        """
        if cls._project_root is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取项目根目录（utils的父目录）
            cls._project_root = Path(os.path.dirname(current_dir))
            # 添加到Python路径
            if str(cls._project_root) not in sys.path:
                sys.path.insert(0, str(cls._project_root))
        return cls._project_root
    
    @classmethod
    def get_module_path(cls, module_name: str) -> Path:
        """获取模块路径
        
        Args:
            module_name: 模块名称，如 'utils', 'testcases' 等
            
        Returns:
            Path: 模块路径
        """
        return cls.get_project_root() / module_name
    
    @classmethod
    def get_data_path(cls) -> Path:
        """获取数据目录路径
        
        Returns:
            Path: 数据目录路径
        """
        return cls.get_project_root() / "data"
    
    @classmethod
    def get_config_path(cls) -> Path:
        """获取配置目录路径
        
        Returns:
            Path: 配置目录路径
        """
        return cls.get_project_root() / "config"
    
    @classmethod
    def get_log_path(cls) -> Path:
        """获取日志目录路径
        
        Returns:
            Path: 日志目录路径
        """
        return cls.get_project_root() / "logs" 