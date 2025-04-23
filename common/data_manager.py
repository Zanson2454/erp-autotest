from pathlib import Path
import yaml
import json
from typing import Dict, Any, Optional
from loguru import logger

class DataManager:
    """测试数据管理类，负责加载和管理测试数据"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.test_data: Dict[str, Any] = {}
        self.temp_data: Dict[str, Any] = {}
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        (self.data_dir / "test_data").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "temp_data").mkdir(parents=True, exist_ok=True)
    
    def load_test_data(self, module: str, case_name: str) -> Dict[str, Any]:
        """加载测试数据
        
        Args:
            module: 模块名称，如 'SCM'
            case_name: 测试用例名称，如 'test_create_so'
            
        Returns:
            测试数据字典
        """
        data_file = self.data_dir / "test_data" / f"{module}_{case_name}.yaml"
        if not data_file.exists():
            logger.warning(f"测试数据文件不存在: {data_file}")
            return {}
            
        with open(data_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.test_data[f"{module}_{case_name}"] = data
            return data
    
    def save_temp_data(self, key: str, value: Any):
        """保存临时数据
        
        Args:
            key: 数据键名
            value: 数据值
        """
        self.temp_data[key] = value
        temp_file = self.data_dir / "temp_data" / f"{key}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
    
    def get_temp_data(self, key: str) -> Optional[Any]:
        """获取临时数据
        
        Args:
            key: 数据键名
            
        Returns:
            数据值，如果不存在则返回None
        """
        if key in self.temp_data:
            return self.temp_data[key]
            
        temp_file = self.data_dir / "temp_data" / f"{key}.json"
        if temp_file.exists():
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.temp_data[key] = data
                return data
        return None
    
    def clear_temp_data(self):
        """清理临时数据"""
        self.temp_data.clear()
        temp_dir = self.data_dir / "temp_data"
        for file in temp_dir.glob("*.json"):
            file.unlink() 