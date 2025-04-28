import os
from typing import List, Dict, Union, Any
import pandas as pd
from pathlib import Path
from loguru import logger


class FileReader:
    """文件读取工具类，支持 Excel 和 CSV 文件"""

    @staticmethod
    def read_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        根据文件后缀名自动选择读取方式
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict[str, Any]]: 文件内容，每行数据为一个字典
            
        Raises:
            ValueError: 文件格式不支持
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        file_extension = file_path.suffix.lower()
        
        if file_extension in ['.xlsx', '.xls']:
            return FileReader._read_excel(file_path)
        elif file_extension == '.csv':
            return FileReader._read_csv(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")

    @staticmethod
    def _read_excel(file_path: Path) -> List[Dict[str, Any]]:
        """
        读取 Excel 文件
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            List[Dict[str, Any]]: Excel 内容，每行数据为一个字典
        """
        try:
            logger.info(f"开始读取 Excel 文件: {file_path}")
            df = pd.read_excel(file_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"读取 Excel 文件失败: {str(e)}")
            raise

    @staticmethod
    def _read_csv(file_path: Path) -> List[Dict[str, Any]]:
        """
        读取 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            
        Returns:
            List[Dict[str, Any]]: CSV 内容，每行数据为一个字典
        """
        try:
            logger.info(f"开始读取 CSV 文件: {file_path}")
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"读取 CSV 文件失败: {str(e)}")
            raise

    @staticmethod
    def read_excel_sheet(file_path: Union[str, Path], sheet_name: str = None) -> pd.DataFrame:
        """读取Excel文件的指定工作表
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            
        Returns:
            pd.DataFrame: 工作表内容
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
            
        try:
            logger.info(f"开始读取 Excel 工作表: {file_path}, sheet: {sheet_name}")
            # 读取Excel文件，第一行作为列名
            return pd.read_excel(file_path, sheet_name=sheet_name, header=0)
        except Exception as e:
            logger.error(f"读取Excel工作表失败: {str(e)}")
            raise

    @staticmethod
    def read_csv_with_encoding(file_path: Union[str, Path], encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        使用指定编码读取 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            encoding: 文件编码，默认为 utf-8
            
        Returns:
            List[Dict[str, Any]]: CSV 内容，每行数据为一个字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() != '.csv':
            raise ValueError(f"不是 CSV 文件: {file_path}")
            
        try:
            logger.info(f"开始读取 CSV 文件: {file_path}, encoding: {encoding}")
            df = pd.read_csv(file_path, encoding=encoding)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"读取 CSV 文件失败: {str(e)}")
            raise

    @staticmethod
    def column_to_dict(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """将DataFrame转换为列数据字典列表
        
        Args:
            df: pandas DataFrame对象
            
        Returns:
            List[Dict[str, Any]]: 列数据字典列表，每个字典的key为列名，value为该列的数据列表
        """
        if df.empty:
            return [{}]
            
        result = []
        # 遍历每一列
        for col in df.columns:
            # 获取该列的所有数据，将NaN替换为None
            col_data = df[col].replace({pd.NA: None}).tolist()
            result.append({col: col_data})
                
        return result

    @staticmethod
    def read_excel_columns(file_path: Union[str, Path], sheet_name: str = None) -> Dict[str, None]:
        """读取Excel文件的列名
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            
        Returns:
            Dict[str, None]: 列名字典，key为列名，value为None
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
            
        try:
            logger.info(f"开始读取 Excel 列名: {file_path}, sheet: {sheet_name}")
            # 只读取第一行获取列名
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0, nrows=0)
            # 将列名转换为字典，所有值设为None
            columns = df.columns.tolist()
            logger.info(f"读取的列名: {columns}")
            rows = [{col: None for col in columns}]
            if len(rows) == 0:
                return [{}]
            else:
                logger.info(f"读取的行: {rows}")
                return rows
        
        except Exception as e:
            logger.error(f"读取Excel列名失败: {str(e)}")
            raise

    @staticmethod
    def read_excel_rows(file_path: Union[str, Path], sheet_name: str = None) -> list[dict]:
        """
        读取Excel所有行，若无数据则返回列名为key、值为None的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
            if df.empty:
                # 没有数据，返回列名为key、值为None的字典
                return [{col: None for col in df.columns}]
            else:
                # 有数据，返回所有行的字典列表
                return df.to_dict('records')
        except Exception as e:
            logger.error(f"读取Excel失败: {str(e)}")
            raise

    
if __name__ == "__main__":
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_path, "testcases", "utils", "采购订单行导入模版.xlsx")
    columns = FileReader.read_excel_rows(file_path, "采购订单行")
    print(columns)