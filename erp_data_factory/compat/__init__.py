"""compat 兼容层包。

提供稳定导入路径，向后兼容历史调用方。
"""

from erp_data_factory.compat.base import DataFactory
from erp_data_factory.compat.del_po_dn_factory import DelPoDnFactory
from erp_data_factory.compat.fin_ap_factory import FinApFactory
from erp_data_factory.compat.fin_ar_factory import FinArFactory
from erp_data_factory.compat.pur_po_factory import PurPoFactory

__all__ = [
    "DataFactory",
    "PurPoFactory",
    "DelPoDnFactory",
    "FinApFactory",
    "FinArFactory",
]
