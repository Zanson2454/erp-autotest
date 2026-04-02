"""FinArFactory 兼容导出。

用途：为历史调用方保留 ``erp_data_factory.compat.fin_ar_factory`` 导入路径。
"""

from erp_data_factory.legacy.fin_ar_factory import FinArFactory

__all__ = ["FinArFactory"]
