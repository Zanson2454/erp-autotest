from utils.yaml_util import YamlUtil
from data_factory.base import DataFactory

class ErpDataFactory(DataFactory):
    @classmethod
    def get_structured_data(cls, raw_data):
        """
        按原有业务结构组织数据，兼容老用例。
        :param raw_data: 通用工厂返回的原始数据（dict，key为sql_templates.yaml的key，value为list[dict]）
        :return: 结构化数据
        """
        return {
            "user_info": {"user_info": (raw_data.get("user_info", [{}]) or [{}])[0]},
            "base_info": {
                "so_type_info": (raw_data.get("so_type_info", [{}]) or [{}])[0],
                "sales_channel_info": (raw_data.get("sales_channel_info", [{}]) or [{}])[0],
                "exchange_rate_type_info": (raw_data.get("exchange_rate_type_info", [{}]) or [{}])[0],
                "currency_info": (raw_data.get("currency_info", [{}]) or [{}])[0],
            },
            "org_info": {
                "sls_org_info": (raw_data.get("sls_org_info", [{}]) or [{}])[0],
                "pur_org_info": (raw_data.get("pur_org_info", [{}]) or [{}])[0],
                "inv_org_info": (raw_data.get("inv_org_info", [{}]) or [{}])[0],
                "com_org_info": (raw_data.get("com_org_info", [{}]) or [{}])[0],
            },
            "partner_info": {
                "cust_info": (raw_data.get("cust_info", [{}]) or [{}])[0],
            },
            "material_info": {
                "inv_loc_info": (raw_data.get("inv_loc_info", [{}]) or [{}])[0],
            }
        }

    @classmethod
    def extract_ids(cls, structured_data):
        """
        按id_mappings.yaml配置路径提取ID，兼容老用例。
        :param structured_data: 结构化数据
        :return: id字典
        """
        id_mappings = YamlUtil.get_project_config("erp", "id_mappings.yaml")
        ids = {}
        for attr_name, path in id_mappings.items():
            value = structured_data
            for key in path:
                value = value.get(key, {}) if isinstance(value, dict) else {}
            ids[attr_name] = value
        return ids 