"""PurPoFactory 兼容导出。

用途：为历史调用方保留 ``erp_data_factory.compat.pur_po_factory`` 导入路径。
"""

from erp_data_factory.legacy.pur_po_factory import PurPoFactory

__all__ = ["PurPoFactory"]
