"""DataFactory 兼容导出。

用途：为历史调用方保留 ``erp_data_factory.compat.base`` 导入路径。
"""

from erp_data_factory.legacy.base import DataFactory

__all__ = ["DataFactory"]
