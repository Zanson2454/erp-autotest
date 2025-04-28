import os
import sys
from pathlib import Path
from loguru import logger
# 确保项目根目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from utils.FileReaderUtil import FileReader
from utils.LogUtil import Loggers

class TestFileReader:
    """文件读取工具类测试"""

    def test_read_excel_sheet(self):
        """测试读取 Excel 工作表"""
        # 获取测试文件路径
        file_path = os.path.join(os.path.dirname(__file__), "采购订单行导入模版.xlsx")
        Loggers.info(f"读取文件路径: {file_path}")
        
        # 读取Excel文件
        df = FileReader.read_excel_rows(file_path, "采购订单行")
        Loggers.info(f"读取数据: {df}")
    


if __name__ == "__main__":
    test = TestFileReader()
    test.test_read_excel_sheet()