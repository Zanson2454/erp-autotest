from pathlib import Path
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from data_factory.base import DataFactory
from data_factory.fin_apar_base_factory import FinAparBaseFactory
from utils.mysql_util import DBManager
from utils.log_util import Loggers

class FinApFactory(FinAparBaseFactory):
    """应付单数据工厂类，继承FinAparBaseFactory"""
    
    # 默认结算项目类型配置
    DEFAULT_SETT_ITEM_TYPE = {
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
    }
    
    # 第二个结算项目类型配置
    SECOND_SETT_ITEM_TYPE = {
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
    }
    
    # 明细配置模板
    ITEM_CONFIGS = [
        {
            "amount": 5000, "qty": 10, "price": 500, 
            "tax_amt": 283.02, "net_amt": 4716.98, "tax_rate": 6,
            "sett_item_type": None  # 使用默认
        },
        {
            "amount": 2500, "qty": 25, "price": 100,
            "tax_amt": 287.61, "net_amt": 2212.39, "tax_rate": 13,
            "sett_item_type": "SECOND"  # 使用第二个类型
        }
    ]
    
    def __init__(self):
        """初始化，调用父类初始化方法"""
        super().__init__()

    def _get_sett_item_type(self, type_key: str = None) -> Dict[str, Any]:
        """获取结算项目类型配置"""
        if type_key == "SECOND":
            return self.SECOND_SETT_ITEM_TYPE.copy()
        return self.DEFAULT_SETT_ITEM_TYPE.copy()

    def create_ap_item(self, mat, tax_code, sett_item_type=None, amount=5000, qty=10, price=500, tax_amt=283.02, net_amt=4716.98, tax_rate=6, mat_id=None) -> Dict[str, Any]:
        """生成apItems明细，结构与页面json一致"""
        # 获取结算项目类型
        if isinstance(sett_item_type, str):
            sett_item_type = self._get_sett_item_type(sett_item_type)
        elif sett_item_type is None:
            sett_item_type = self._get_sett_item_type()
        
        return {
            "taxAmt": tax_amt,
            "grossBaseAmt": amount,
            "netBaseAmt": 1,
            "settItemTypeId": sett_item_type,
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
        if len(mat_list) != len(tax_code_list):
            raise ValueError("物料列表和税码列表长度不匹配")
        
        items = []
        for i, (mat, tax_code) in enumerate(zip(mat_list, tax_code_list)):
            if i < len(self.ITEM_CONFIGS):
                config = self.ITEM_CONFIGS[i].copy()
                # 处理结算项目类型
                sett_type = config.pop("sett_item_type")
                if sett_type == "SECOND":
                    config["sett_item_type"] = self._get_sett_item_type("SECOND")
                else:
                    config["sett_item_type"] = self._get_sett_item_type()
                
                items.append(self.create_ap_item(
                    mat=mat,
                    tax_code=tax_code,
                    mat_id=mat["id"],
                    **config
                ))
        
        return items

    def create_ap_schl(self, amount=1080000, due_date=None) -> Dict[str, Any]:
        """生成apSchls明细，结构与页面一致"""
        base_schl = self.create_fin_doc_schedule_base(amount, due_date)
        # 应付单特有字段映射
        ap_schl = {
            "apDocAmt": base_schl["docAmt"],
            "apBaseAmt": base_schl["baseAmt"],
            "apPercent": base_schl["percent"]
        }
        # 合并基础字段
        base_schl.update(ap_schl)
        return base_schl

    # 保留原有的查询方法以保持向后兼容
    def _query_org(self, org_code: str) -> Optional[Dict[str, Any]]:
        """查询组织"""
        try:
            return self.query_single_record("org_struct_md", "org_code = %s AND deleted = 0", [org_code], f"编码为{org_code}的组织")
        except Exception:
            return None

    def _query_currency(self, curr_code: str) -> Optional[Dict[str, Any]]:
        """查询币种"""
        try:
            return self.query_single_record("gen_curr_type_cf", "curr_code = %s AND deleted = 0", [curr_code], f"编码为{curr_code}的币种")
        except Exception:
            return None

    def _query_tax_code(self, tax: int) -> Optional[Dict[str, Any]]:
        """查询税码"""
        try:
            return self.query_single_record("gen_tax_type_cf", "tax = %s AND deleted = 0", [tax], f"税率为{tax}%的税码")
        except Exception:
            return None

    def _query_material(self, mat_code: str) -> Optional[Dict[str, Any]]:
        """查询物料"""
        try:
            return self.query_single_record("gen_mat_md", "mat_code = %s AND deleted = 0", [mat_code], f"编码为{mat_code}的物料")
        except Exception:
            return None

    @classmethod
    def get_or_create_ap_doc(cls, status: str = None) -> Dict[str, Any]:
        """
        获取或创建应付单
        :param status: 状态（CREATED-已创建, CONFIRMED-已确认, APPROVED-已审核）
        :return: 应付单数据
        """
        # 初始化数据库连接
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
            
        try:
            result = DBManager.query(sql, params)
            return result[0] if result else None
        except Exception as e:
            Loggers.error(f"查询应付单失败: {str(e)}")
            return None

    @staticmethod
    def _create_ap_doc_via_api() -> Optional[Dict[str, Any]]:
        """通过接口创建应付单"""
        return None

    @classmethod
    def _insert_ap_doc(cls, status: str = None) -> Dict[str, Any]:
        """直接插入应付单"""
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        id = f'0{str(int(now.timestamp() * 1000))[-7:]}'
        
        # 获取基础数据 - 使用父类方法
        factory = cls()
        base_data = factory.get_base_data_for_fin_doc("AP")
        
        # 构建应付单头表数据
        head_data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'ap_head_code': f'AUTOTEST-APD{now.strftime("%Y%m%d%H%M%S")}',
            'ap_status': status or 'DRAFT',
            'com_org_id': base_data['com_org']['id'],
            'pur_org_id': base_data['bus_org']['id'],  # 使用业务组织作为采购组织
            'pay_org_id': base_data['pay_org']['id'],
            'sett_partner_id': 2117001,  # 使用固定的供应商ID
            'sett_partner_type': 'SUPPLIER',
            'doc_curr_id': base_data['currency']['id'],
            'base_curr_id': base_data['currency']['id'],
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
            'doc_type_id': 2101001
        }
        
        # 构建应付单行表数据
        item_data = {
            'created_at': now_str,
            'updated_at': now_str,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'apm_ap_head_tr_id': id,
            'ap_item_code': f'AUTOTEST-API{now.strftime("%Y%m%d%H%M%S")}',
            'ap_head_code': head_data['ap_head_code'],
            'mat_id': 14431009,  # 使用已存在的物料ID
            'basic_unit_id': 2007001,  # 使用已存在的基本单位ID
            'ap_qty': 10.00,
            'gross_doc_price': 100.00,
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
        
        try:
            # 插入应付单头表
            DBManager.insert('fin_apm_ap_head_tr', head_data)
            
            return cls._query_ap_doc(status)
        except Exception as e:
            Loggers.error(f"插入应付单数据失败: {str(e)}")
            raise

    def get_latest_ap_doc_id_by_status(self, status: str) -> str:
        """根据状态获取最新的应付单ID"""
        return self.get_latest_fin_doc_id_by_status('fin_apm_ap_head_tr', 'ap_status', status)

    def query_payment_request_by_ap_id(self, ap_doc_id: str) -> Optional[Dict[str, Any]]:
        """
        根据应付单ID查询付款申请单信息
        :param ap_doc_id: 应付单ID
        :return: 付款申请单信息字典，包含cm_pr_head_tr_id和pr_head_code
        """
        try:
            sql = """
                SELECT 
                    item.cm_pr_head_tr_id,
                    head.pr_head_code,
                    item.rel_doc_head_id,
                    item.id as pr_item_id,
                    head.pr_status,
                    head.created_at,
                    head.updated_at
                FROM fin_cm_pr_item_tr item
                INNER JOIN fin_cm_pr_head_tr head ON item.cm_pr_head_tr_id = head.id
                WHERE item.rel_doc_head_id = %s 
                AND item.deleted = 0 
                AND head.deleted = 0
                ORDER BY item.created_at DESC
                LIMIT 1
            """
            
            result = DBManager.query(sql, [ap_doc_id])
            
            if result:
                pr_info = result[0]
                Loggers.info(f"根据应付单ID {ap_doc_id} 查询到付款申请单信息: cm_pr_head_tr_id={pr_info.get('cm_pr_head_tr_id')}, pr_head_code={pr_info.get('pr_head_code')}")
                return {
                    "cm_pr_head_tr_id": pr_info.get("cm_pr_head_tr_id"),
                    "pr_head_code": pr_info.get("pr_head_code"),
                    "rel_doc_head_id": pr_info.get("rel_doc_head_id"),
                    "pr_item_id": pr_info.get("pr_item_id"),
                    "pr_status": pr_info.get("pr_status"),
                    "created_at": pr_info.get("created_at"),
                    "updated_at": pr_info.get("updated_at")
                }
            else:
                Loggers.warning(f"未找到应付单ID {ap_doc_id} 对应的付款申请单信息")
                return None
                
        except Exception as e:
            Loggers.error(f"根据应付单ID {ap_doc_id} 查询付款申请单信息失败: {str(e)}")
            return None

    def query_payment_requests_by_ap_id(self, ap_doc_id: str) -> List[Dict[str, Any]]:
        """
        根据应付单ID查询所有相关的付款申请单信息（支持一对多关系）
        :param ap_doc_id: 应付单ID
        :return: 付款申请单信息列表
        """
        try:
            sql = """
                SELECT 
                    item.cm_pr_head_tr_id,
                    head.pr_head_code,
                    item.rel_doc_head_id,
                    item.id as pr_item_id,
                    head.pr_status,
                    item.pr_doc_amt,
                    item.pr_base_amt,
                    head.created_at,
                    head.updated_at
                FROM fin_cm_pr_item_tr item
                INNER JOIN fin_cm_pr_head_tr head ON item.cm_pr_head_tr_id = head.id
                WHERE item.rel_doc_head_id = %s 
                AND item.deleted = 0 
                AND head.deleted = 0
                ORDER BY item.created_at DESC
            """
            
            results = DBManager.query(sql, [ap_doc_id])
            
            if results:
                pr_list = []
                for pr_info in results:
                    pr_list.append({
                        "cm_pr_head_tr_id": pr_info.get("cm_pr_head_tr_id"),
                        "pr_head_code": pr_info.get("pr_head_code"),
                        "rel_doc_head_id": pr_info.get("rel_doc_head_id"),
                        "pr_item_id": pr_info.get("pr_item_id"),
                        "pr_status": pr_info.get("pr_status"),
                        "pr_doc_amt": pr_info.get("pr_doc_amt"),
                        "pr_base_amt": pr_info.get("pr_base_amt"),
                        "created_at": pr_info.get("created_at"),
                        "updated_at": pr_info.get("updated_at")
                    })
                
                Loggers.info(f"根据应付单ID {ap_doc_id} 查询到 {len(pr_list)} 条付款申请单信息")
                return pr_list
            else:
                Loggers.warning(f"未找到应付单ID {ap_doc_id} 对应的付款申请单信息")
                return []
                
        except Exception as e:
            Loggers.error(f"根据应付单ID {ap_doc_id} 查询付款申请单信息失败: {str(e)}")
            return []

    def get_payment_request_status_by_ap_id(self, ap_doc_id: str) -> Optional[str]:
        """
        根据应付单ID获取最新付款申请单的状态
        :param ap_doc_id: 应付单ID
        :return: 付款申请单状态
        """
        pr_info = self.query_payment_request_by_ap_id(ap_doc_id)
        return pr_info.get("pr_status") if pr_info else None

if __name__ == '__main__':
    print(FinApFactory.get_or_create_ap_doc()) 