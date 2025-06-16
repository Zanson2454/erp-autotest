from pathlib import Path
import sys
from typing import Dict, Any, Optional, List
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
    def _to_timestamp(dt):
        """统一的时间戳转换方法"""
        if isinstance(dt, datetime):
            return int(dt.timestamp() * 1000)
        if isinstance(dt, str):
            try:
                return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
            except:
                return dt
        return dt

    def _query_single_record(self, table_name: str, condition: str, params: List, entity_name: str) -> dict:
        """通用的单条记录查询方法"""
        sql = f"SELECT id FROM {table_name} WHERE {condition} AND deleted = 0"
        result = DBManager.query(sql, params)
        if not result:
            raise Exception(f"未找到{entity_name}")
        return {"id": result[0]["id"]}

    def _build_common_fields(self, obj: dict) -> dict:
        """构建通用字段映射"""
        return {
            "createdBy": {"id": obj.get("created_by")},
            "updatedBy": {"id": obj.get("updated_by")},
            "createdAt": self._to_timestamp(obj.get("created_at")),
            "updatedAt": self._to_timestamp(obj.get("updated_at")),
            "version": obj.get("version"),
            "deleted": obj.get("deleted"),
            "originOrgId": obj.get("origin_org_id"),
        }

    def _query_autotest_record(self, table_name: str, code_pattern: str) -> dict:
        """查询自动化测试记录的通用方法"""
        sql = f"SELECT * FROM {table_name} WHERE deleted = 0 AND {code_pattern}"
        result = DBManager.query(sql)
        if not result:
            raise Exception(f"未找到{table_name}表中的自动化测试数据")
        return result[0]

    # 简化的ID查询方法
    def get_org_by_id(self, org_id: int) -> dict:
        return self._query_single_record("org_struct_md", "id = %s", [org_id], f"ID为{org_id}的组织")

    def get_customer_by_id(self, cust_id: int) -> dict:
        return self._query_single_record("gen_cust_info_md", "id = %s", [cust_id], f"ID为{cust_id}的客户")

    def get_material_by_id(self, mat_id: int) -> dict:
        return self._query_single_record("gen_mat_md", "id = %s", [mat_id], f"ID为{mat_id}的物料")

    def get_tax_code_by_id(self, tax_code_id: int) -> dict:
        return self._query_single_record("gen_tax_type_cf", "id = %s", [tax_code_id], f"ID为{tax_code_id}的税码")

    def get_sett_item_type_by_id(self, sett_item_type_id: int) -> dict:
        return {"id": sett_item_type_id}

    def create_currency(self) -> dict:
        return self._query_single_record("gen_curr_type_cf", "curr_name = %s", ["人民币"], "人民币币种")

    # 应收单明细和计划配置
    AR_ITEM_CONFIG = {
        "default": {
            "arQty": 100,
            "grossDocPrice": 400,
            "grossDocAmt": 40000,
            "grossBaseAmt": 40000,
            "netDocAmt": 40000,
            "netBaseAmt": 40000,
            "taxRate": 13,
            "taxAmt": 4601.77
        },
        "page_style": {
            "arQty": 100,
            "grossDocPrice": 400,
            "grossDocAmt": 40000,
            "grossBaseAmt": 40000,
            "netDocAmt": 35398.23,
            "netBaseAmt": 1,
            "taxRate": 13,
            "taxAmt": 4601.77
        }
    }

    AR_SCHL_CONFIG = {
        "default": {
            "arDocAmt": 40000,
            "arBaseAmt": 40000,
            "arPercent": 100,
            "collectionClearingStatus": "UNCLEARED"
        },
        "page_style": {
            "arDocAmt": 40000,
            "arBaseAmt": 40000,
            "arPercent": 100,
            "receivedDocAmt": 0,
            "unreceivedDocAmt": 40000,
            "receivedBaseAmt": 0,
            "unreceivedBaseAmt": 40000,
            "collectionClearingStatus": "UNCLEARED",
            "receivingDocAmt": 0,
            "receivingBaseAmt": 0,
            "context": {}
        }
    }

    def _create_ar_item(self, mat_id, tax_code_id, sett_item_type_id, style="default") -> dict:
        """创建应收单明细项"""
        config = self.AR_ITEM_CONFIG[style]
        item = {
            "matId": {"id": mat_id},
            "taxCodeId": {"id": tax_code_id},
            "settItemTypeId": {"id": sett_item_type_id},
        }
        item.update(config)
        return item

    def _create_ar_schl(self, due_date=None, style="default") -> dict:
        """创建应收单计划项"""
        if due_date is None:
            due_date = int(datetime.now().timestamp() * 1000)
        
        config = self.AR_SCHL_CONFIG[style]
        schl = {"dueDate": due_date}
        schl.update(config)
        return schl

    # 统一的明细和计划创建方法
    def create_ar_items_full(self, mat_id, tax_code_id, sett_item_type_id) -> list:
        return [self._create_ar_item(mat_id, tax_code_id, sett_item_type_id, "default")]

    def create_ar_items_full_by_page(self, mat, tax_code, sett_item_type):
        """按页面抓包结构生成arItems明细列表"""
        return [self._create_ar_item(mat["id"], tax_code["id"], sett_item_type["id"], "page_style")]

    def create_ar_schls_full(self, amount=40000, due_date=None) -> list:
        return [self._create_ar_schl(due_date, "default")]

    def create_ar_schls_full_by_page(self, now_ts):
        """按页面抓包结构生成arSchls计划列表"""
        return [self._create_ar_schl(now_ts, "page_style")]

    # 优化的from_row方法
    def create_customer_from_row(self, cust: dict) -> dict:
        result = {
            "custCode": cust["cust_code"],
            "custName": cust["cust_name"],
            "status": cust["status"],
            "custCateType": cust.get("cust_cate_type"),
            "custType": {"id": cust.get("cust_type_id")},
            "com": {"id": cust.get("com_id")},
            "id": cust["id"],
        }
        result.update(self._build_common_fields(cust))
        return result

    def create_material_from_row(self, mat: dict) -> dict:
        result = {
            "matCode": mat["mat_code"],
            "matName": mat["mat_name"],
            "status": mat["status"],
            "id": mat["id"],
        }
        result.update(self._build_common_fields(mat))
        return result

    def create_tax_code_from_row(self, tax: dict) -> dict:
        result = {
            "taxCode": tax["tax_code"],
            "taxcate": tax["taxcate"],
            "tax": tax["tax"],
            "id": tax["id"],
        }
        result.update(self._build_common_fields(tax))
        return result

    # 优化的create方法
    def create_org(self, org_type: str) -> Dict[str, Any]:
        """创建组织（COM和SLS都返回公司组织）"""
        org = self._query_autotest_record("org_struct_md", "org_code LIKE 'AUTOTEST_COM_ORG%'")
        return self.create_org_from_row(org)

    def create_customer(self) -> Dict[str, Any]:
        """创建客户"""
        cust = self._query_autotest_record("gen_cust_info_md", "cust_code LIKE 'AUTOTEST_CUST%'")
        return self.create_customer_from_row(cust)

    def create_tax_code(self) -> Dict[str, Any]:
        """创建税码"""
        tax = self._query_autotest_record("gen_tax_type_cf", "tax = 6")
        return self.create_tax_code_from_row(tax)

    def create_material(self) -> Dict[str, Any]:
        """创建物料"""
        mat = self._query_autotest_record("gen_mat_md", "mat_code LIKE 'AUTOTEST_MAT%'")
        return self.create_material_from_row(mat)

    def create_org_from_row(self, org: dict) -> dict:
        """从数据库行创建组织对象"""
        result = {
            "orgCode": org["org_code"],
            "orgName": org["org_name"],
            "orgStatus": org["org_status"],
            "id": org["id"],
        }
        result.update(self._build_common_fields(org))
        return result

    def create_doc_type(self) -> Dict[str, Any]:
        """创建单据类型"""
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
        """获取或创建应收单"""
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
        
        # 批量获取基础数据
        base_data_queries = {
            'com_org': ("org_struct_md", "org_code LIKE 'AUTOTEST_COM_ORG%'"),
            'sls_org': ("org_struct_md", "org_code LIKE 'AUTOTEST_SLS_ORG%'"),
            'currency': ("gen_curr_type_cf", "curr_name = '人民币'"),
            'customer': ("gen_cust_info_md", "cust_code LIKE 'AUTOTEST_CUST%'")
        }
        
        base_data = {}
        for key, (table, condition) in base_data_queries.items():
            sql = f"SELECT * FROM {table} WHERE deleted = 0 AND {condition}"
            result = DBManager.query(sql)
            if not result:
                raise Exception(f"未找到{table}表中的测试数据")
            base_data[key] = result[0]
        
        # 插入应收单头表
        data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'ar_head_code': f'AUTOTEST-ARD{now.strftime("%Y%m%d%H%M%S")}',
            'ar_status': status or 'DRAFT',
            'com_org_id': base_data['com_org']['id'],
            'sls_org_id': base_data['sls_org']['id'],
            'pay_org_id': base_data['com_org']['id'],
            'sett_partner_id': base_data['customer']['id'],
            'sett_partner_type': 'CUSTOMER',
            'doc_curr_id': base_data['currency']['id'],
            'base_curr_id': base_data['currency']['id'],
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

    def get_pn_info_by_ar_id(self, ar_doc_id: int) -> dict:
        """根据应收单ID查询收款单信息"""
        sql = """
            SELECT pn_head_id, pn_head_code 
            FROM fin_cm_pn_link_tr 
            WHERE deleted = 0 
            AND source_head_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = DBManager.query(sql, [ar_doc_id])
        if result:
            return {
                "pn_head_id": result[0]["pn_head_id"],
                "pn_head_code": result[0]["pn_head_code"]
            }
        return None

    def get_sb_info_by_bil_code(self, bil_code: str) -> Optional[Dict[str, Any]]:
        """根据bil_code查询销售发票头表信息"""
        if not bil_code:
            Loggers.warning("bil_code参数不能为空")
            return None
            
        sql = """
            SELECT sb_head_code, id 
            FROM fin_tm_sb_head_tr 
            WHERE deleted = 0 
            AND bil_code = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        try:
            result = DBManager.query(sql, [bil_code])
            if result:
                sb_info = {
                    "sb_head_code": result[0]["sb_head_code"],
                    "id": result[0]["id"]
                }
                Loggers.info(f"根据bil_code[{bil_code}]查询到销售发票: {sb_info}")
                return sb_info
            else:
                Loggers.warning(f"未找到bil_code为[{bil_code}]的销售发票记录")
                return None
                
        except Exception as e:
            Loggers.error(f"查询销售发票信息失败，bil_code: {bil_code}, 错误: {str(e)}")
            raise Exception(f"查询销售发票信息失败: {str(e)}")

    def get_sb_info_by_ar_id(self, ar_doc_id: int) -> Optional[Dict[str, Any]]:
        """根据应收单ID查询销售发票头表信息"""
        if not ar_doc_id:
            Loggers.warning("ar_doc_id参数不能为空")
            return None
            
        # 先根据应收单ID查询应收单编码
        ar_sql = """
            SELECT ar_head_code 
            FROM fin_arm_ar_head_tr 
            WHERE deleted = 0 
            AND id = %s
        """
        
        try:
            ar_result = DBManager.query(ar_sql, [ar_doc_id])
            if not ar_result:
                Loggers.warning(f"未找到ID为[{ar_doc_id}]的应收单记录")
                return None
                
            bil_code = ar_result[0]["ar_head_code"]
            Loggers.info(f"根据应收单ID[{ar_doc_id}]获取到bil_code: {bil_code}")
            
            # 再根据bil_code查询销售发票信息
            return self.get_sb_info_by_bil_code(bil_code)
            
        except Exception as e:
            Loggers.error(f"根据应收单ID查询销售发票信息失败，ar_doc_id: {ar_doc_id}, 错误: {str(e)}")
            raise Exception(f"根据应收单ID查询销售发票信息失败: {str(e)}")

if __name__ == '__main__':
    factory = FinArFactory()
    print(factory.create_currency()) 