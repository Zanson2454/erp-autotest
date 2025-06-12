from pathlib import Path
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from data_factory.base import DataFactory
from utils.mysql_util import DBManager
from utils.log_util import Loggers

class FinArFactory:
    """应收单数据工厂类"""
    # 状态常量
    STATUS_DRAFT = 'DRAFT'  # 草稿态
    STATUS_CONFIRM = 'CONFIRM'  # 提交态
    STATUS_DONE = 'DONE'  # 完成态
    STATUS_DELETE = 'DELETE'  # 删除态
    
    def __init__(self):
        """初始化"""
        self.data_factory = DataFactory()
        db_config = self.data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        self.next_id = int(datetime.now().timestamp() * 1000)

    def get_next_id(self) -> int:
        """获取下一个ID"""
        self.next_id += 1
        return self.next_id

    @staticmethod
    def convert_obj_for_json(obj):
        """递归将字典/列表中的 datetime 转为字符串，Decimal 转为 float"""
        if isinstance(obj, dict):
            return {k: FinArFactory.convert_obj_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [FinArFactory.convert_obj_for_json(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    @staticmethod
    def to_ts(dt):
        if isinstance(dt, datetime):
            return int(dt.timestamp() * 1000)
        if isinstance(dt, str):
            try:
                return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
            except:
                return dt
        return dt

    def get_org_by_id(self, org_id: int) -> dict:
        sql = "SELECT id FROM org_struct_md WHERE id = %s AND deleted = 0"
        result = DBManager.query(sql, [org_id])
        if not result:
            raise Exception(f"未找到ID为{org_id}的组织")
        return {"id": result[0]["id"]}

    def get_customer_by_id(self, cust_id: int) -> dict:
        sql = "SELECT id FROM gen_cust_info_md WHERE id = %s AND deleted = 0"
        result = DBManager.query(sql, [cust_id])
        if not result:
            raise Exception(f"未找到ID为{cust_id}的客户")
        return {"id": result[0]["id"]}

    def get_material_by_id(self, mat_id: int) -> dict:
        sql = "SELECT id FROM gen_mat_md WHERE id = %s AND deleted = 0"
        result = DBManager.query(sql, [mat_id])
        if not result:
            raise Exception(f"未找到ID为{mat_id}的物料")
        return {"id": result[0]["id"]}

    def get_tax_code_by_id(self, tax_code_id: int) -> dict:
        sql = "SELECT id FROM gen_tax_type_cf WHERE id = %s AND deleted = 0"
        result = DBManager.query(sql, [tax_code_id])
        if not result:
            raise Exception(f"未找到ID为{tax_code_id}的税码")
        return {"id": result[0]["id"]}

    def get_sett_item_type_by_id(self, sett_item_type_id: int) -> dict:
        # 只返回id
        return {"id": sett_item_type_id}

    def create_currency(self) -> dict:
        sql = "SELECT id FROM gen_curr_type_cf WHERE deleted = 0 AND curr_name = '人民币'"
        result = DBManager.query(sql)
        return {"id": result[0]["id"]}

    def create_ar_item(self, mat_id, tax_code_id, sett_item_type_id, amount=40000, qty=100, price=400, tax_amt=4601.77, tax_rate=13) -> dict:
        return {
            "matId": {"id": mat_id},
            "taxCodeId": {"id": tax_code_id},
            "settItemTypeId": {"id": sett_item_type_id},
            "arQty": qty,
            "grossDocPrice": price,
            "grossDocAmt": amount,
            "grossBaseAmt": amount,
            "netDocAmt": amount,
            "netBaseAmt": amount,
            "taxRate": tax_rate,
            "taxAmt": tax_amt
        }

    def create_ar_items_full(self, mat_id, tax_code_id, sett_item_type_id) -> list:
        return [self.create_ar_item(mat_id, tax_code_id, sett_item_type_id)]

    def create_ar_schl(self, amount=40000, due_date=None) -> dict:
        if due_date is None:
            due_date = int(datetime.now().timestamp() * 1000)
        return {
            "dueDate": due_date,
            "arDocAmt": amount,
            "arBaseAmt": amount,
            "arPercent": 100,
            "collectionClearingStatus": "UNCLEARED"
        }

    def create_ar_schls_full(self, amount=40000, due_date=None) -> list:
        return [self.create_ar_schl(amount, due_date)]

    def create_org(self, org_type: str) -> Dict[str, Any]:
        """
        创建组织（COM和SLS都返回公司组织）
        :param org_type: 组织类型（COM-公司组织, SLS-销售组织）
        :return: 组织数据
        """
        # 统一只查公司组织
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE 'AUTOTEST_COM_ORG%'
        """
        result = DBManager.query(sql)
        if not result:
            raise Exception("未找到已初始化的公司组织，请先在后台做应收单初始化配置")
        org = result[0]
        return self.create_org_from_row(org)

    def create_customer(self) -> Dict[str, Any]:
        """创建客户"""
        sql = """
            SELECT * FROM gen_cust_info_md 
            WHERE deleted = 0 
            AND cust_code LIKE 'AUTOTEST_CUST%'
        """
        result = DBManager.query(sql)
        cust = result[0]
        return self.create_customer_from_row(cust)

    def create_tax_code(self) -> Dict[str, Any]:
        """创建税码"""
        sql = """
            SELECT * FROM gen_tax_type_cf 
            WHERE deleted = 0 
            AND tax = 6
        """
        result = DBManager.query(sql)
        tax = result[0]
        return self.create_tax_code_from_row(tax)

    def create_material(self) -> Dict[str, Any]:
        """创建物料"""
        sql = """
            SELECT * FROM gen_mat_md 
            WHERE deleted = 0 
            AND mat_code LIKE 'AUTOTEST_MAT%'
        """
        result = DBManager.query(sql)
        mat = result[0]
        return self.create_material_from_row(mat)

    def create_customer_from_row(self, cust: dict) -> dict:
        return {
            "custCode": cust["cust_code"],
            "custName": cust["cust_name"],
            "status": cust["status"],
            "custCateType": cust.get("cust_cate_type"),
            "custType": {"id": cust.get("cust_type_id")},
            "com": {"id": cust.get("com_id")},
            "id": cust["id"],
            "createdBy": {"id": cust.get("created_by")},
            "updatedBy": {"id": cust.get("updated_by")},
            "createdAt": self.to_ts(cust.get("created_at")),
            "updatedAt": self.to_ts(cust.get("updated_at")),
            "version": cust.get("version"),
            "deleted": cust.get("deleted"),
            "originOrgId": cust.get("origin_org_id"),
        }

    def create_material_from_row(self, mat: dict) -> dict:
        return {
            "matCode": mat["mat_code"],
            "matName": mat["mat_name"],
            "status": mat["status"],
            "id": mat["id"],
            "createdBy": {"id": mat.get("created_by")},
            "updatedBy": {"id": mat.get("updated_by")},
            "createdAt": self.to_ts(mat.get("created_at")),
            "updatedAt": self.to_ts(mat.get("updated_at")),
            "version": mat.get("version"),
            "deleted": mat.get("deleted"),
            "originOrgId": mat.get("origin_org_id"),
        }

    def create_tax_code_from_row(self, tax: dict) -> dict:
        return {
            "taxCode": tax["tax_code"],
            "taxcate": tax["taxcate"],
            "tax": tax["tax"],
            "id": tax["id"],
            "createdBy": {"id": tax.get("created_by")},
            "updatedBy": {"id": tax.get("updated_by")},
            "createdAt": self.to_ts(tax.get("created_at")),
            "updatedAt": self.to_ts(tax.get("updated_at")),
            "version": tax.get("version"),
            "deleted": tax.get("deleted"),
            "originOrgId": tax.get("origin_org_id"),
        }

    def create_doc_type(self) -> Dict[str, Any]:
        """创建单据类型"""
        # 直接返回标准应收单据类型，避免查询不存在的表
        return {
            "arTypeCode": "STND",
            "name": "标准财务应收单",
            "isAccDocRelv": "YES",
            "accountType": "FIN",
            "finDocTypeId": None,
            "relPnTypeId": {"id": 2002002},
            "isAdjustRelv": False,
            "exchangeRateType": {"id": 2000001},
            "schlSumBySo": False,
            "schlSumByDn": False,
            "isEnableCostAcq": True,
            "pushAes": True,
            "autoPushAes": False,
            "id": 14003001,
            "createdBy": {"id": 477234922377861},
            "updatedBy": {"id": 477517877510789},
            "createdAt": 1707016426000,
            "updatedAt": 1739954250000,
            "version": 11,
            "deleted": 0,
            "originOrgId": 0
        }

    def create_ar_items_full_by_page(self, mat, tax_code, sett_item_type):
        """按页面抓包结构生成arItems明细列表"""
        return [
            {
                "taxAmt": 4601.77,
                "grossBaseAmt": 40000,
                "netBaseAmt": 1,
                "settItemTypeId": sett_item_type,
                "grossDocAmt": 40000,
                "netDocAmt": 35398.23,
                "matId": mat,
                "taxCodeId": tax_code,
                "taxRate": 13,
                "arQty": 100,
                "grossDocPrice": 400
            }
        ]

    def create_ar_schls_full_by_page(self, now_ts):
        """按页面抓包结构生成arSchls计划列表"""
        return [
            {
                "context": {},
                "dueDate": now_ts,
                "arDocAmt": 40000,
                "arBaseAmt": 40000,
                "arPercent": 100,
                "receivedDocAmt": 0,
                "unreceivedDocAmt": 40000,
                "receivedBaseAmt": 0,
                "unreceivedBaseAmt": 40000,
                "collectionClearingStatus": "UNCLEARED",
                "receivingDocAmt": 0,
                "receivingBaseAmt": 0
            }
        ]

    def get_latest_ar_doc_id_by_status(self, status: str) -> str:
        """根据状态查询fin_arm_ar_head_tr表最新应收单id，返回字符串类型id"""
        sql = '''
            SELECT id FROM fin_arm_ar_head_tr
            WHERE deleted = 0 AND ar_status = %s
            ORDER BY updated_at DESC
            LIMIT 1
        '''
        result = DBManager.query(sql, [status])
        return str(result[0]["id"]) if result else None

    @classmethod
    def get_or_create_ar_doc(cls, status: str = None) -> dict:
        """
        获取或创建应收单
        :param status: 状态（DRAFT/CONFIRM/DONE）
        :return: 应收单数据
        """
        data_factory = DataFactory()
        db_config = data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        # 1. 先查库
        data = cls._query_ar_doc(status)
        if data:
            Loggers.info(f"从数据库获取到应收单数据: {data.get('id')}")
            return data
        # 2. 可扩展接口创建
        try:
            data = cls._create_ar_doc_via_api()
            if data:
                Loggers.info(f"通过接口成功创建应收单数据: {data.get('id')}")
                return data
        except Exception as e:
            Loggers.warning(f"通过接口创建应收单数据失败: {str(e)}")
        # 3. 插库兜底
        try:
            data = cls._insert_ar_doc(status)
            Loggers.info(f"通过数据库插入成功创建应收单数据: {data.get('id')}")
            return data
        except Exception as e:
            Loggers.error(f"数据库插入应收单数据失败: {str(e)}")
            raise

    @staticmethod
    def _query_ar_doc(status: str = None) -> Optional[dict]:
        """从数据库查询应收单"""
        sql = """
            SELECT h.* 
            FROM fin_arm_ar_head_tr h
            WHERE h.deleted = 0
            AND h.ar_head_code LIKE %s
        """
        params = ['AUTOTEST-ARD%']
        if status:
            sql = sql.strip() + " AND h.ar_status = %s ORDER BY h.created_at DESC"
            params.append(status)
        result = DBManager.query(sql, params)
        return result[0] if result else None

    @staticmethod
    def _create_ar_doc_via_api() -> Optional[dict]:
        """通过接口创建应收单（可扩展）"""
        return None

    @classmethod
    def _insert_ar_doc(cls, status: str = None) -> dict:
        """直接插入应收单（兜底）"""
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        id = f'0{str(int(now.timestamp() * 1000))[-7:]}'
        # 获取基础数据
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE 'AUTOTEST_COM_ORG%'
        """
        com_org = DBManager.query(sql)[0]
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE 'AUTOTEST_SLS_ORG%'
        """
        sls_org = DBManager.query(sql)[0]
        pay_org = com_org
        sql = """
            SELECT * FROM gen_curr_type_cf 
            WHERE deleted = 0 
            AND curr_name = '人民币'
        """
        currency = DBManager.query(sql)[0]
        sql = """
            SELECT * FROM gen_cust_info_md 
            WHERE deleted = 0 
            AND cust_code LIKE 'AUTOTEST_CUST%'
        """
        customer = DBManager.query(sql)[0]
        # 插入应收单头表
        data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'ar_head_code': f'AUTOTEST-ARD{now.strftime("%Y%m%d%H%M%S")}',
            'ar_status': status or 'DRAFT',
            'com_org_id': com_org['id'],
            'sls_org_id': sls_org['id'],
            'pay_org_id': pay_org['id'],
            'sett_partner_id': customer['id'],
            'sett_partner_type': 'CUSTOMER',
            'doc_curr_id': currency['id'],
            'base_curr_id': currency['id'],
            'exch_rate': 1.00,
            'gross_doc_amt': 40000.00,
            'net_doc_amt': 35398.23,
            'gross_base_amt': 40000.00,
            'net_base_amt': 35398.23,
            'remark': '自动化测试应收单',
            'async_execution_status': 'CREATED',
            'id': id,
            'created_by': 476102974181637,
            'updated_by': 476102974181637,
            'doc_type_id': 14003001
        }
        DBManager.insert('fin_arm_ar_head_tr', data)
        # 插入应收单明细表
        item_data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'arm_ar_head_tr_id': id,
            'ar_item_code': f'AUTOTEST-ARI{now.strftime("%Y%m%d%H%M%S")}',
            'ar_head_code': data['ar_head_code'],
            'mat_id': 14672002,
            'ar_qty': 100.00,
            'gross_doc_price': 400.00,
            'tax_rate': 13.00,
            'net_doc_amt': 35398.23,
            'gross_doc_amt': 40000.00,
            'net_base_amt': 35398.23,
            'gross_base_amt': 40000.00,
            'remark': '自动化测试应收单明细',
            'id': f'0{str(int(now.timestamp() * 1000) + 1)[-7:]}',
            'created_by': 476102974181637,
            'updated_by': 476102974181637
        }
        DBManager.insert('fin_arm_ar_item_tr', item_data)
        return cls._query_ar_doc(status)

if __name__ == '__main__':
    factory = FinArFactory()
    print(factory.create_currency()) 