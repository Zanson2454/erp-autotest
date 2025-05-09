import os
import sys
from pathlib import Path
from typing import Optional, Union
from loguru import logger


class PathUtil:
    """路径工具类
    
    提供项目路径管理、验证和创建功能。
    支持跨平台路径处理，确保路径存在性和权限。
    
    使用示例：
    ```python
    # 获取项目根目录
    root = PathUtil.get_project_root()
    
    # 获取并确保数据目录存在
    data_dir = PathUtil.ensure_dir(PathUtil.get_data_path())
    
    # 获取配置文件路径
    config_file = PathUtil.get_config_path() / "config.yaml"
    ```
    """
    
    _project_root: Optional[Path] = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """获取项目根目录
        
        Returns:
            Path: 项目根目录路径
            
        Raises:
            FileNotFoundError: 项目根目录不存在
        """
        if cls._project_root is None:
            # 获取当前文件所在目录
            current_file = Path(__file__).resolve()
            # 获取项目根目录（utils的父目录）
            cls._project_root = current_file.parent.parent
            # 验证项目根目录
            if not cls._project_root.exists():
                raise FileNotFoundError(f"项目根目录不存在: {cls._project_root}")
            # 添加到Python路径
            if str(cls._project_root) not in sys.path:
                sys.path.insert(0, str(cls._project_root))
            logger.debug(f"项目根目录: {cls._project_root}")
        return cls._project_root
    
    @classmethod
    def get_module_path(cls, module_name: str) -> Path:
        """获取模块路径
        
        Args:
            module_name: 模块名称，如 'utils', 'testcases' 等
            
        Returns:
            Path: 模块路径
            
        Raises:
            FileNotFoundError: 模块目录不存在
        """
        path = cls.get_project_root() / module_name
        if not path.exists():
            raise FileNotFoundError(f"模块目录不存在: {path}")
        return path
    
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
    
    @classmethod
    def ensure_dir(cls, path: Union[str, Path]) -> Path:
        """确保目录存在，如果不存在则创建
        
        Args:
            path: 目录路径
            
        Returns:
            Path: 目录路径对象
            
        Raises:
            PermissionError: 没有创建目录的权限
        """
        path = Path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保目录存在: {path}")
            return path
        except PermissionError as e:
            logger.error(f"创建目录失败，权限不足: {path}")
            raise PermissionError(f"没有创建目录的权限: {path}") from e
    
    @classmethod
    def is_writable(cls, path: Union[str, Path]) -> bool:
        """检查路径是否可写
        
        Args:
            path: 路径
            
        Returns:
            bool: 是否可写
        """
        path = Path(path)
        try:
            if not path.exists():
                return os.access(path.parent, os.W_OK)
            return os.access(path, os.W_OK)
        except Exception as e:
            logger.error(f"检查路径权限失败: {path}, 错误: {e}")
            return False
    
    @classmethod
    def get_relative_path(cls, path: Union[str, Path]) -> Path:
        """获取相对于项目根目录的路径
        
        Args:
            path: 绝对路径
            
        Returns:
            Path: 相对路径
        """
        try:
            return Path(path).relative_to(cls.get_project_root())
        except ValueError:
            return Path(path) 