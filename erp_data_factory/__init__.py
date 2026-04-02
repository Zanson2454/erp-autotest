"""ERP 数据工厂包主入口。

对外默认导出 ``ERPDataFactoryClient``，供测试代码与服务代码统一调用。
"""

from erp_data_factory.client import ERPDataFactoryClient

__all__ = ["ERPDataFactoryClient"]
