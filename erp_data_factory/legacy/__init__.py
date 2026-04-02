"""legacy 迁移承接层包。

保留历史数据工厂能力，供迁移期间兼容使用。
"""

from .base import DataFactory
from .pur_po_factory import PurPoFactory

__all__ = ['DataFactory', 'PurPoFactory']
