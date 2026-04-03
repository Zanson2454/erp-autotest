import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from loguru import logger

from utils.exception_util import safe_file_operation


class FileReader:
    """文件读取工具类，支持 Excel 和 CSV 文件
    
    主要功能：
    1. 支持 Excel 和 CSV 文件的读取
    2. 支持指定编码读取 CSV 文件
    3. 支持读取 Excel 指定工作表
    4. 支持 DataFrame 和字典格式的转换
    5. 支持读取文件列名和行数据
    
    使用示例：
    ```python
    # 读取 Excel 文件
    data = FileReader.read_file("path/to/file.xlsx")
    
    # 读取指定工作表
    df = FileReader.read_excel_sheet("path/to/file.xlsx", "Sheet1")
    
    # 读取 CSV 文件
    data = FileReader.read_csv_with_encoding("path/to/file.csv", "utf-8")
    ```
    """

    @staticmethod
    @safe_file_operation(error_message="文件读取失败")
    def read_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        根据文件后缀名自动选择读取方式
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict[str, Any]]: 文件内容，每行数据为一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
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
    @safe_file_operation(error_message="Excel文件读取失败")
    def _read_excel(file_path: Path) -> List[Dict[str, Any]]:
        """
        读取 Excel 文件
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            List[Dict[str, Any]]: Excel 内容，每行数据为一个字典
            
        Raises:
            Exception: 读取失败时抛出异常
        """
        logger.info(f"开始读取 Excel 文件: {file_path}")
        df = pd.read_excel(file_path)
        return df.to_dict('records')

    @staticmethod
    @safe_file_operation(error_message="CSV文件读取失败")
    def _read_csv(file_path: Path) -> List[Dict[str, Any]]:
        """
        读取 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            
        Returns:
            List[Dict[str, Any]]: CSV 内容，每行数据为一个字典
            
        Raises:
            Exception: 读取失败时抛出异常
        """
        logger.info(f"开始读取 CSV 文件: {file_path}")
        df = pd.read_csv(file_path)
        return df.to_dict('records')

    @staticmethod
    @safe_file_operation(error_message="Excel工作表读取失败")
    def read_excel_sheet(
        file_path: Union[str, Path], 
        sheet_name: Optional[str] = None,
        header: int = 0,
        usecols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """读取Excel文件的指定工作表
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            header: 表头行号，默认为0（第一行）
            usecols: 要读取的列名列表，如果为None则读取所有列
            
        Returns:
            pd.DataFrame: 工作表内容
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不是Excel文件
            Exception: 读取失败时抛出异常
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
            
        logger.info(f"开始读取 Excel 工作表: {file_path}, sheet: {sheet_name}")
        return pd.read_excel(
            file_path, 
            sheet_name=sheet_name, 
            header=header,
            usecols=usecols
        )

    @staticmethod
    @safe_file_operation(error_message="CSV文件读取失败")
    def read_csv_with_encoding(
        file_path: Union[str, Path], 
        encoding: str = 'utf-8',
        sep: str = ',',
        header: int = 0,
        usecols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        使用指定编码读取 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            encoding: 文件编码，默认为 utf-8
            sep: 分隔符，默认为逗号
            header: 表头行号，默认为0（第一行）
            usecols: 要读取的列名列表，如果为None则读取所有列
            
        Returns:
            List[Dict[str, Any]]: CSV 内容，每行数据为一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不是CSV文件
            Exception: 读取失败时抛出异常
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() != '.csv':
            raise ValueError(f"不是 CSV 文件: {file_path}")
            
        logger.info(f"开始读取 CSV 文件: {file_path}, encoding: {encoding}")
        df = pd.read_csv(
            file_path, 
            encoding=encoding,
            sep=sep,
            header=header,
            usecols=usecols
        )
        return df.to_dict('records')

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
    @safe_file_operation(error_message="Excel列名读取失败")
    def read_excel_columns(
        file_path: Union[str, Path], 
        sheet_name: Optional[str] = None,
        header: int = 0
    ) -> List[Dict[str, None]]:
        """读取Excel文件的列名
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            header: 表头行号，默认为0（第一行）
            
        Returns:
            List[Dict[str, None]]: 列名字典列表，每个字典的key为列名，value为None
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不是Excel文件
            Exception: 读取失败时抛出异常
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
            
        logger.info(f"开始读取 Excel 列名: {file_path}, sheet: {sheet_name}")
        # 只读取第一行获取列名
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header, nrows=0)
        # 将列名转换为字典，所有值设为None
        columns = df.columns.tolist()
        logger.info(f"读取的列名: {columns}")
        return [{col: None for col in columns}]

    @staticmethod
    @safe_file_operation(error_message="Excel行数据读取失败")
    def read_excel_rows(
        file_path: Union[str, Path], 
        sheet_name: Optional[str] = None,
        header: int = 0,
        usecols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """读取Excel所有行数据
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            header: 表头行号，默认为0（第一行）
            usecols: 要读取的列名列表，如果为None则读取所有列
            
        Returns:
            List[Dict[str, Any]]: 行数据字典列表，每行数据为一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不是Excel文件
            Exception: 读取失败时抛出异常
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"不是Excel文件: {file_path}")
            
        logger.info(f"开始读取 Excel 行数据: {file_path}, sheet: {sheet_name}")
        df = pd.read_excel(
            file_path, 
            sheet_name=sheet_name, 
            header=header,
            usecols=usecols
        )
        
        if df.empty:
            # 没有数据，返回列名为key、值为None的字典
            return [{col: None for col in df.columns}]
        else:
            # 有数据，返回所有行的字典列表
            return df.to_dict('records')

    @staticmethod
    def validate_file_exists(file_path: Union[str, Path]) -> None:
        """验证文件是否存在
        
        Args:
            file_path: 文件路径
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

    @staticmethod
    def validate_file_extension(file_path: Union[str, Path], allowed_extensions: List[str]) -> None:
        """验证文件扩展名是否允许
        
        Args:
            file_path: 文件路径
            allowed_extensions: 允许的文件扩展名列表
            
        Raises:
            ValueError: 文件扩展名不允许
        """
        file_path = Path(file_path)
        if file_path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}，允许的格式: {allowed_extensions}")

    
if __name__ == "__main__":
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_path, "testcases", "utils", "采购订单行导入模版.xlsx")
    columns = FileReader.read_excel_rows(file_path, "采购订单行")
    print(columns)