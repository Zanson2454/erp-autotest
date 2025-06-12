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

class FinApFactory:
    """应付单数据工厂类"""
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
            return {k: FinApFactory.convert_obj_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [FinApFactory.convert_obj_for_json(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj

    def create_org(self, org_type: str) -> Dict[str, Any]:
        """
        创建组织
        :param org_type: 组织类型（COM-公司组织, PUR-采购组织）
        :return: 组织数据
        """
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE %s
        """
        params = [f'AUTOTEST_{org_type}_ORG%']
        result = DBManager.query(sql, params)
        org = result[0]
        def to_ts(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        # 补全页面json需要的字段
        return {
            "orgCode": org["org_code"],
            "orgName": org["org_name"],
            "orgEnableDate": to_ts(org.get("org_enable_date")),
            "orgStatus": org.get("org_status"),
            "isLeaf": org.get("is_leaf", False),
            "orgBusinessTypeId": {"id": org.get("org_business_type_id")},
            "orgDimensionId": {"id": org.get("org_dimension_id")},
            "orgParentId": {"id": org.get("org_parent_id")} if org.get("org_parent_id") else None,
            "partnerId": org.get("partner_id"),
            "comOrgId": {"id": org.get("com_org_id")} if org.get("com_org_id") else None,
            "orgBusinessTypeIds": org.get("org_business_type_ids"),
            "orgBusinessTypeCodes": org.get("org_business_type_codes"),
            "path": org.get("path"),
            "id": org["id"],
            "createdBy": {"id": org.get("created_by")},
            "updatedBy": {"id": org.get("updated_by")},
            "createdAt": to_ts(org.get("created_at")),
            "updatedAt": to_ts(org.get("updated_at")),
            "version": org.get("version"),
            "deleted": org.get("deleted"),
            "originOrgId": org.get("origin_org_id"),
        }

    def create_vendor(self) -> Dict[str, Any]:
        """创建供应商"""
        sql = """
            SELECT * FROM gen_vend_info_md 
            WHERE deleted = 0 
            AND vend_code LIKE 'AUTOTEST_VEND%'
        """
        result = DBManager.query(sql)
        vend = result[0]
        def to_ts(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        return {
            "vendCode": vend["vend_code"],
            "name": vend["name"],
            "status": vend["status"],
            "vendCateType": vend.get("vend_cate_type"),
            "vendType": {"id": vend.get("vend_type_id")},
            "com": {"id": vend.get("com_id")},
            "id": vend["id"],
            "createdBy": {"id": vend.get("created_by")},
            "updatedBy": {"id": vend.get("updated_by")},
            "createdAt": to_ts(vend.get("created_at")),
            "updatedAt": to_ts(vend.get("updated_at")),
            "version": vend.get("version"),
            "deleted": vend.get("deleted"),
            "originOrgId": vend.get("origin_org_id"),
            "vendCateId": vend.get("vend_cate_id"),
            "vendPersonLink": vend.get("vend_person_link"),
        }

    def create_currency(self) -> Dict[str, Any]:
        """创建币种"""
        sql = """
            SELECT * FROM gen_curr_type_cf 
            WHERE deleted = 0 
            AND curr_name = '人民币'
        """
        result = DBManager.query(sql)
        curr = result[0]
        def to_ts(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        return {
            "currCode": curr["curr_code"],
            "currName": curr["curr_name"],
            "symbol": curr["symbol"],
            "remark": curr["remark"],
            "id": curr["id"],
            "createdBy": {"id": curr.get("created_by")},
            "updatedBy": {"id": curr.get("updated_by")},
            "createdAt": to_ts(curr.get("created_at")),
            "updatedAt": to_ts(curr.get("updated_at")),
            "version": curr.get("version"),
            "deleted": curr.get("deleted"),
            "originOrgId": curr.get("origin_org_id"),
        }

    def create_tax_code(self) -> Dict[str, Any]:
        """创建税码"""
        sql = """
            SELECT * FROM gen_tax_type_cf 
            WHERE deleted = 0 
            AND tax = 13
        """
        result = DBManager.query(sql)
        tax = result[0]
        def to_ts(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        return {
            "taxCode": tax["tax_code"],
            "taxcate": tax["taxcate"],
            "tax": tax["tax"],
            "id": tax["id"],
            "createdBy": {"id": tax.get("created_by")},
            "updatedBy": {"id": tax.get("updated_by")},
            "createdAt": to_ts(tax.get("created_at")),
            "updatedAt": to_ts(tax.get("updated_at")),
            "version": tax.get("version"),
            "deleted": tax.get("deleted"),
            "originOrgId": tax.get("origin_org_id"),
        }

    def create_material(self) -> Dict[str, Any]:
        """创建物料"""
        sql = """
            SELECT * FROM gen_mat_md 
            WHERE deleted = 0 
            AND mat_code LIKE 'AUTOTEST_MAT%'
        """
        result = DBManager.query(sql)
        mat = result[0]
        def to_ts(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        return {
            "matCode": mat["mat_code"],
            "matName": mat["mat_name"],
            "status": mat["status"],
            "id": mat["id"],
            "createdBy": {"id": mat.get("created_by")},
            "updatedBy": {"id": mat.get("updated_by")},
            "createdAt": to_ts(mat.get("created_at")),
            "updatedAt": to_ts(mat.get("updated_at")),
            "version": mat.get("version"),
            "deleted": mat.get("deleted"),
            "originOrgId": mat.get("origin_org_id"),
        }

    def create_ap_item(self, mat, tax_code, sett_item_type=None, amount=5000, qty=10, price=500, tax_amt=283.02, net_amt=4716.98, tax_rate=6, mat_id=None) -> Dict[str, Any]:
        """生成apItems明细，结构与页面json一致"""
        # sett_item_type、tax_code、mat等都应为完整对象
        # 可根据页面json静态模板补全
        return {
            "taxAmt": tax_amt,
            "grossBaseAmt": amount,
            "netBaseAmt": 1,
            "settItemTypeId": sett_item_type or {
                "settItemTypeCode": "E_PUR_FRET_C",
                "settItemTypeName": "外部-采购-计量运费",
                "settClass": "EXTERNAL",
                "btClass": "PURCHASE",
                "priceGroupId": {"id": 2000005},
                "priceGroupClass": "EXPENSES",
                "accCode": None,
                "settDocTypeCode": {"id": 2001001},
                "affiliateSettItemTypeCode": None,
                "isCountQty": False,
                "exchangeRateType": {"id": 2003001},
                "isAcqCost": False,
                "id": 2000001,
                "createdBy": {"id": 166382094639791},
                "updatedBy": {"id": 479645949903493},
                "createdAt": 1696906084000,
                "updatedAt": 1721201191000,
                "version": 2,
                "deleted": 0,
                "originOrgId": 0,
                "requestId": None
            },
            "matId": mat_id or mat["id"],
            "grossDocAmt": amount,
            "netDocAmt": net_amt,
            "taxCodeId": tax_code,
            "taxRate": tax_rate,
            "apQty": qty,
            "grossDocPrice": price
        }

    def create_ap_items_full(self, mat_list, tax_code_list) -> list:
        """生成多个apItems明细，结构与页面json一致"""
        # 可根据页面json静态模板补全
        items = []
        # 第一条 - 使用实际的物料ID
        items.append(self.create_ap_item(
            mat=mat_list[0],
            tax_code=tax_code_list[0],
            amount=5000,
            qty=10,
            price=500,
            tax_amt=283.02,
            net_amt=4716.98,
            tax_rate=6,
            mat_id=mat_list[0]["id"]  # 使用实际查询到的物料ID
        ))
        # 第二条 - 使用实际的物料ID
        items.append(self.create_ap_item(
            mat=mat_list[1],
            tax_code=tax_code_list[1],
            sett_item_type={
                "settItemTypeCode": "I_PUR_INSP",
                "settItemTypeName": "内部-采购-检测费",
                "settClass": "INSIDE",
                "btClass": "PURCHASE",
                "priceGroupId": {"id": 2000003},
                "priceGroupClass": "EXPENSES",
                "accCode": None,
                "settDocTypeCode": {"id": 2002004},
                "affiliateSettItemTypeCode": None,
                "isCountQty": True,
                "exchangeRateType": {"id": 2003001},
                "isAcqCost": None,
                "id": 11,
                "createdBy": None,
                "updatedBy": {"id": 166382094639791},
                "createdAt": 1687778100000,
                "updatedAt": 1696760889000,
                "version": 1,
                "deleted": 0,
                "originOrgId": 0,
                "requestId": None
            },
            amount=2500,
            qty=25,
            price=100,
            tax_amt=287.61,
            net_amt=2212.39,
            tax_rate=13,
            mat_id=mat_list[1]["id"]  # 使用实际查询到的物料ID
        ))
        return items

    def create_ap_schl(self, amount=1080000, due_date=None) -> Dict[str, Any]:
        """生成apSchls明细，结构与页面一致"""
        if due_date is None:
            due_date = int(datetime.now().timestamp() * 1000)
        return {
            "context": {},
            "dueDate": due_date,
            "apDocAmt": amount,
            "apBaseAmt": amount,
            "apPercent": 100,
            "appliedDocAmt": 0,
            "unappliedDocAmt": amount,
            "applyingDocAmt": 0,
            "paidDocAmt": 0,
            "unpaidDocAmt": amount,
            "payingDocAmt": 0,
            "appliedBaseAmt": 0,
            "unappliedBaseAmt": amount,
            "paidBaseAmt": 0,
            "unpaidBaseAmt": amount,
            "payingBaseAmt": 0,
            "paymentClearingStatus": "UNCLEARED"
        }

    def _query_org(self, org_code: str) -> Optional[Dict[str, Any]]:
        """查询组织"""
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code = %s
        """
        result = DBManager.query(sql, [org_code])
        return result[0] if result else None

    def _query_vendor(self, vend_code: str) -> Optional[Dict[str, Any]]:
        """查询供应商"""
        sql = """
            SELECT * FROM gen_vend_info_md 
            WHERE deleted = 0 
            AND vend_code = %s
        """
        result = DBManager.query(sql, [vend_code])
        return result[0] if result else None

    def _query_currency(self, curr_code: str) -> Optional[Dict[str, Any]]:
        """查询币种"""
        sql = """
            SELECT * FROM gen_curr_type_cf 
            WHERE deleted = 0 
            AND curr_code = %s
        """
        result = DBManager.query(sql, [curr_code])
        return result[0] if result else None

    def _query_tax_code(self, tax: int) -> Optional[Dict[str, Any]]:
        """查询税码"""
        sql = """
            SELECT * FROM gen_tax_type_cf 
            WHERE deleted = 0 
            AND tax = %s
        """
        result = DBManager.query(sql, [tax])
        return result[0] if result else None

    def _query_material(self, mat_code: str) -> Optional[Dict[str, Any]]:
        """查询物料"""
        sql = """
            SELECT * FROM gen_mat_md 
            WHERE deleted = 0 
            AND mat_code = %s
        """
        result = DBManager.query(sql, [mat_code])
        return result[0] if result else None

    @classmethod
    def get_or_create_ap_doc(cls, status: str = None) -> Dict[str, Any]:
        """
        获取或创建应付单
        :param status: 状态（CREATED-已创建, CONFIRMED-已确认, APPROVED-已审核）
        :return: 应付单数据
        """
        data_factory = DataFactory() 
        db_config = data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        
        # 1. 尝试从数据库查询
        data = cls._query_ap_doc(status)
        if data:
            Loggers.info(f"从数据库获取到应付单数据: {data.get('id')}")
            return data
            
        # 2. 尝试通过接口创建
        try:
            data = cls._create_ap_doc_via_api()
            if data:
                Loggers.info(f"通过接口成功创建应付单数据: {data.get('id')}")
                return data
        except Exception as e:
            Loggers.warning(f"通过接口创建应付单数据失败: {str(e)}")
            
        # 3. 如果接口创建失败，尝试直接数据库插入
        try:
            data = cls._insert_ap_doc(status)
            Loggers.info(f"通过数据库插入成功创建应付单数据: {data.get('id')}")
            return data
        except Exception as e:
            Loggers.error(f"数据库插入应付单数据失败: {str(e)}")
            raise

    @staticmethod
    def _query_ap_doc(status: str = None) -> Optional[Dict[str, Any]]:
        """从数据库查询应付单"""
        sql = """
            SELECT h.* 
            FROM fin_apm_ap_head_tr h
            WHERE h.deleted = 0
            AND h.ap_head_code LIKE %s
        """
        params = ['AUTOTEST-APD%']
        
        if status:
            sql = sql.strip() + " AND h.ap_status = %s ORDER BY h.created_at DESC"
            params.append(status)
            
        result = DBManager.query(sql, params)
        return result[0] if result else None

    @staticmethod
    def _create_ap_doc_via_api() -> Optional[Dict[str, Any]]:
        """通过接口创建应付单"""
        return None

    @classmethod
    def _insert_ap_doc(cls, status: str = None) -> Dict[str, Any]:
        """直接插入应付单"""
        from datetime import datetime
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        id = f'0{str(int(now.timestamp() * 1000))[-7:]}'
        
        # 获取基础数据
        # 1. 获取公司组织
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE 'AUTOTEST_COM_ORG'
        """
        com_org = DBManager.query(sql)[0]
        
        # 2. 获取采购组织
        sql = """
            SELECT * FROM org_struct_md 
            WHERE deleted = 0 
            AND org_code LIKE 'AUTOTEST_PUR_ORG'
        """
        pur_org = DBManager.query(sql)[0]
        
        # 3. 使用公司组织作为付款组织
        pay_org = com_org
        
        # 4. 获取币种
        sql = """
            SELECT * FROM gen_curr_type_cf 
            WHERE deleted = 0 
            AND curr_name = '人民币'
        """
        currency = DBManager.query(sql)[0]
        
        data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'ap_head_code': f'AUTOTEST-APD{now.strftime("%Y%m%d%H%M%S")}',
            'ap_status': status or 'DRAFT',
            'com_org_id': com_org['id'],
            'pur_org_id': pur_org['id'],
            'pay_org_id': pay_org['id'],  # 使用付款组织ID
            'sett_partner_id': 2117001,  # 使用固定的供应商ID
            'sett_partner_type': 'SUPPLIER',
            'doc_curr_id': currency['id'],
            'base_curr_id': currency['id'],
            'exch_rate': 1.00,
            'gross_doc_amt': 1000.00,
            'net_doc_amt': 884.96,
            'gross_base_amt': 1000.00,
            'net_base_amt': 884.96,
            'remark': '自动化测试应付单',
            'async_execution_status': 'CREATED',
            'id': id,
            'created_by': 476102974181637,
            'updated_by': 476102974181637,
            'doc_type_id': 2101001  # 添加单据类型ID
        }
        
        # 插入应付单头表
        DBManager.insert('fin_apm_ap_head_tr', data)
        
        # 插入应付单行表
        item_data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'apm_ap_head_tr_id': id,  # 使用正确的字段名
            'ap_item_code': f'AUTOTEST-API{now.strftime("%Y%m%d%H%M%S")}',
            'ap_head_code': data['ap_head_code'],  # 添加应付单编号
            'mat_id': 14431009,  # 使用已存在的物料ID
            'basic_unit_id': 2007001,  # 使用已存在的基本单位ID
            'ap_qty': 10.00,
            'gross_doc_price': 100.00,  # 修改字段名
            'tax_rate': 13.00,
            'net_doc_amt': 884.96,
            'gross_doc_amt': 1000.00,
            'net_base_amt': 884.96,
            'gross_base_amt': 1000.00,
            'remark': '自动化测试应付单行',
            'id': f'0{str(int(now.timestamp() * 1000) + 1)[-7:]}',
            'created_by': 476102974181637,
            'updated_by': 476102974181637
        }
        
        # 插入应付单行表
        DBManager.insert('fin_apm_ap_item_tr', item_data)
        
        return cls._query_ap_doc(status)

    def get_latest_ap_doc_id_by_status(self, status: str) -> str:
        sql = '''
            SELECT id FROM fin_apm_ap_head_tr
            WHERE deleted = 0 AND ap_status = %s
            ORDER BY updated_at DESC
            LIMIT 1
        '''
        result = DBManager.query(sql, [status])
        return str(result[0]["id"]) if result else None

if __name__ == '__main__':
    print(FinApFactory.get_or_create_ap_doc()) 