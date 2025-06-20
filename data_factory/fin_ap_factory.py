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
    
    def __init__(self):
        """初始化，调用父类初始化方法"""
        super().__init__()
        self._sett_item_types_cache = {}  # 缓存结算项目类型

    def convert_data_for_json(self, obj):
        """
        数据转换方法，处理Decimal和datetime类型，确保JSON序列化
        :param obj: 待转换的对象
        :return: 转换后的对象
        """
        if obj is None:
            return None
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, dict):
            return {k: self.convert_data_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_data_for_json(item) for item in obj]
        else:
            return obj

    def get_settlement_item_type_by_code(self, sett_item_type_code: str) -> Dict[str, Any]:
        """
        根据结算项目类型编码从数据库查询结算项目类型
        :param sett_item_type_code: 结算项目类型编码
        :return: 结算项目类型数据
        """
        # 检查缓存
        if sett_item_type_code in self._sett_item_types_cache:
            return self._sett_item_types_cache[sett_item_type_code].copy()
        
        try:
            sql = """
                SELECT 
                    id, sett_item_type_code, sett_item_type_name, 
                    sett_class, bt_class, price_group_id, price_group_class,
                    acc_code, sett_doc_type_code, affiliate_sett_item_type_code,
                    is_count_qty, exchange_rate_type, is_acq_cost,
                    created_by, updated_by, created_at, updated_at, version,
                    deleted, origin_org_id, request_id
                FROM gen_sett_item_type_cf 
                WHERE sett_item_type_code = %s AND deleted = 0
                LIMIT 1
            """
            
            result = DBManager.query(sql, [sett_item_type_code])
            
            if result:
                row = result[0]
                sett_item_type = {
                    "settItemTypeCode": row.get("sett_item_type_code"),
                    "settItemTypeName": row.get("sett_item_type_name"),
                    "settClass": row.get("sett_class"),
                    "btClass": row.get("bt_class"),
                    "priceGroupId": {"id": row.get("price_group_id")} if row.get("price_group_id") else None,
                    "priceGroupClass": row.get("price_group_class"),
                    "accCode": row.get("acc_code"),
                    "settDocTypeCode": {"id": row.get("sett_doc_type_code")} if row.get("sett_doc_type_code") else None,
                    "affiliateSettItemTypeCode": row.get("affiliate_sett_item_type_code"),
                    "isCountQty": bool(row.get("is_count_qty", 0)),
                    "exchangeRateType": {"id": row.get("exchange_rate_type")} if row.get("exchange_rate_type") else None,
                    "isAcqCost": bool(row.get("is_acq_cost", 0)) if row.get("is_acq_cost") is not None else None,
                    "id": row.get("id"),
                    "createdBy": {"id": row.get("created_by")} if row.get("created_by") else None,
                    "updatedBy": {"id": row.get("updated_by")} if row.get("updated_by") else None,
                    "createdAt": int(row.get("created_at").timestamp() * 1000) if row.get("created_at") else None,
                    "updatedAt": int(row.get("updated_at").timestamp() * 1000) if row.get("updated_at") else None,
                    "version": row.get("version"),
                    "deleted": row.get("deleted"),
                    "originOrgId": row.get("origin_org_id"),
                    "requestId": row.get("request_id")
                }
                
                # 缓存结果
                self._sett_item_types_cache[sett_item_type_code] = sett_item_type
                
                Loggers.info(f"查询到结算项目类型[{sett_item_type_code}]: {sett_item_type.get('settItemTypeName')}")
                return sett_item_type.copy()
            else:
                Loggers.warning(f"未找到结算项目类型编码为[{sett_item_type_code}]的记录")
                return self._get_default_sett_item_type()
                
        except Exception as e:
            Loggers.error(f"查询结算项目类型失败，编码: {sett_item_type_code}, 错误: {str(e)}")
            return self._get_default_sett_item_type()

    def get_purchase_settlement_item_types(self, limit: int = 2) -> List[Dict[str, Any]]:
        """
        查询采购相关的结算项目类型
        :param limit: 查询数量限制
        :return: 结算项目类型列表
        """
        try:
            sql = """
                SELECT 
                    id, sett_item_type_code, sett_item_type_name, 
                    sett_class, bt_class, price_group_id, price_group_class,
                    acc_code, sett_doc_type_code, affiliate_sett_item_type_code,
                    is_count_qty, exchange_rate_type, is_acq_cost,
                    created_by, updated_by, created_at, updated_at, version,
                    deleted, origin_org_id, request_id
                FROM gen_sett_item_type_cf 
                WHERE bt_class = 'PURCHASE' AND deleted = 0
                ORDER BY id ASC
                LIMIT %s
            """
            
            results = DBManager.query(sql, [limit])
            
            if results:
                sett_types = []
                for row in results:
                    sett_item_type = {
                        "settItemTypeCode": row.get("sett_item_type_code"),
                        "settItemTypeName": row.get("sett_item_type_name"),
                        "settClass": row.get("sett_class"),
                        "btClass": row.get("bt_class"),
                        "priceGroupId": {"id": row.get("price_group_id")} if row.get("price_group_id") else None,
                        "priceGroupClass": row.get("price_group_class"),
                        "accCode": row.get("acc_code"),
                        "settDocTypeCode": {"id": row.get("sett_doc_type_code")} if row.get("sett_doc_type_code") else None,
                        "affiliateSettItemTypeCode": row.get("affiliate_sett_item_type_code"),
                        "isCountQty": bool(row.get("is_count_qty", 0)),
                        "exchangeRateType": {"id": row.get("exchange_rate_type")} if row.get("exchange_rate_type") else None,
                        "isAcqCost": bool(row.get("is_acq_cost", 0)) if row.get("is_acq_cost") is not None else None,
                        "id": row.get("id"),
                        "createdBy": {"id": row.get("created_by")} if row.get("created_by") else None,
                        "updatedBy": {"id": row.get("updated_by")} if row.get("updated_by") else None,
                        "createdAt": int(row.get("created_at").timestamp() * 1000) if row.get("created_at") else None,
                        "updatedAt": int(row.get("updated_at").timestamp() * 1000) if row.get("updated_at") else None,
                        "version": row.get("version"),
                        "deleted": row.get("deleted"),
                        "originOrgId": row.get("origin_org_id"),
                        "requestId": row.get("request_id")
                    }
                    sett_types.append(sett_item_type)
                
                Loggers.info(f"查询到{len(sett_types)}个采购结算项目类型")
                return sett_types
            else:
                Loggers.warning("未找到采购相关的结算项目类型")
                return [self._get_default_sett_item_type(), self._get_default_sett_item_type()]
                
        except Exception as e:
            Loggers.error(f"查询采购结算项目类型失败: {str(e)}")
            return [self._get_default_sett_item_type(), self._get_default_sett_item_type()]

    def _get_default_sett_item_type(self) -> Dict[str, Any]:
        """获取默认的结算项目类型（fallback）"""
        return {
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

    def _get_sett_item_type(self, type_key: str = None) -> Dict[str, Any]:
        """获取结算项目类型配置"""
        if type_key == "SECOND":
            # 尝试查询第二种类型
            return self.get_settlement_item_type_by_code("I_PUR_INSP")
        else:
            # 默认查询第一种类型
            return self.get_settlement_item_type_by_code("E_PUR_FRET_C")

    def get_dynamic_item_configs(self) -> List[Dict[str, Any]]:
        """
        动态生成明细配置，基于数据库查询的结算项目类型
        :return: 明细配置列表
        """
        try:
            # 获取采购相关的结算项目类型
            sett_types = self.get_purchase_settlement_item_types(2)
            
            # 动态生成配置
            configs = []
            
            # 第一个配置：使用第一个结算项目类型
            if len(sett_types) > 0:
                configs.append({
                    "amount": 5000, "qty": 10, "price": 500,
                    "tax_amt": 283.02, "net_amt": 4716.98, "tax_rate": 6,
                    "sett_item_type": sett_types[0]
                })
            
            # 第二个配置：使用第二个结算项目类型
            if len(sett_types) > 1:
                configs.append({
                    "amount": 2500, "qty": 25, "price": 100,
                    "tax_amt": 287.61, "net_amt": 2212.39, "tax_rate": 13,
                    "sett_item_type": sett_types[1]
                })
            
            Loggers.info(f"动态生成{len(configs)}个明细配置")
            return configs
            
        except Exception as e:
            Loggers.error(f"动态生成明细配置失败: {str(e)}")
            # 返回默认配置
            return [
                {
                    "amount": 5000, "qty": 10, "price": 500,
                    "tax_amt": 283.02, "net_amt": 4716.98, "tax_rate": 6,
                    "sett_item_type": self._get_default_sett_item_type()
                },
                {
                    "amount": 2500, "qty": 25, "price": 100,
                    "tax_amt": 287.61, "net_amt": 2212.39, "tax_rate": 13,
                    "sett_item_type": self._get_default_sett_item_type()
                }
            ]

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
            "netBaseAmt": net_amt,
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
        
        # 获取动态配置
        item_configs = self.get_dynamic_item_configs()
        
        items = []
        for i, (mat, tax_code) in enumerate(zip(mat_list, tax_code_list)):
            if i < len(item_configs):
                config = item_configs[i].copy()
                # 使用配置中的结算项目类型
                sett_item_type = config.pop("sett_item_type")
                
                items.append(self.create_ap_item(
                    mat=mat,
                    tax_code=tax_code,
                    mat_id=mat["id"],
                    sett_item_type=sett_item_type,
                    **{k: v for k, v in config.items() if k != "sett_item_type"}
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
                    "created_at": self.convert_data_for_json(pr_info.get("created_at")),
                    "updated_at": self.convert_data_for_json(pr_info.get("updated_at"))
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
                        "pr_doc_amt": self.convert_data_for_json(pr_info.get("pr_doc_amt")),
                        "pr_base_amt": self.convert_data_for_json(pr_info.get("pr_base_amt")),
                        "created_at": self.convert_data_for_json(pr_info.get("created_at")),
                        "updated_at": self.convert_data_for_json(pr_info.get("updated_at"))
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

    def get_ap_schl_ids_by_ap_id(self, ap_doc_id: int) -> List[int]:
        """
        根据应付单ID查询应付计划行ID列表
        :param ap_doc_id: 应付单ID
        :return: 应付计划行ID列表
        """
        if not ap_doc_id:
            Loggers.warning("ap_doc_id参数不能为空")
            return []
            
        sql = """
            SELECT id FROM fin_apm_ap_schl_tr 
            WHERE apm_ap_head_tr_id = %s AND deleted = 0
            ORDER BY created_at ASC
        """
        
        try:
            result = DBManager.query(sql, [ap_doc_id])
            ap_schl_ids = [row['id'] for row in result] if result else []
            Loggers.info(f"根据应付单ID[{ap_doc_id}]查询到{len(ap_schl_ids)}个计划行ID: {ap_schl_ids}")
            return ap_schl_ids
        except Exception as e:
            Loggers.error(f"查询应付计划行ID失败，ap_doc_id: {ap_doc_id}, 错误: {str(e)}")
            return []

    def get_ap_item_ids_by_ap_id(self, ap_doc_id: int) -> List[int]:
        """
        根据应付单ID查询应付单行ID列表  
        :param ap_doc_id: 应付单ID
        :return: 应付单行ID列表
        """
        if not ap_doc_id:
            Loggers.warning("ap_doc_id参数不能为空")
            return []
            
        sql = """
            SELECT id FROM fin_apm_ap_item_tr 
            WHERE apm_ap_head_tr_id = %s AND deleted = 0
            ORDER BY created_at ASC
        """
        
        try:
            result = DBManager.query(sql, [ap_doc_id])
            ap_item_ids = [row['id'] for row in result] if result else []
            Loggers.info(f"根据应付单ID[{ap_doc_id}]查询到{len(ap_item_ids)}个应付单行ID: {ap_item_ids}")
            return ap_item_ids
        except Exception as e:
            Loggers.error(f"查询应付单行ID失败，ap_doc_id: {ap_doc_id}, 错误: {str(e)}")
            return []

    def query_purchase_invoice_by_inv_code(self, inv_code: str) -> Optional[Dict[str, Any]]:
        """
        根据发票号（inv_code）查询采购发票头表信息
        :param inv_code: 发票号
        :return: 采购发票头表信息字典，包含pi_head_code和id等信息
        """
        try:
            sql = """
                SELECT 
                    id,
                    pi_head_code,
                    inv_code,
                    pi_status,
                    doc_type_id,
                    com_org_id,
                    pur_org_id,
                    tra_par_id,
                    tra_par_type,
                    inv_doc_amt,
                    inv_base_amt,
                    inv_doc_tax,
                    inv_base_tax,
                    pi_date,
                    created_at,
                    updated_at,
                    version
                FROM fin_tm_pi_head_tr 
                WHERE inv_code = %s 
                AND deleted = 0
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            result = DBManager.query(sql, [inv_code])
            
            if result:
                pi_info = result[0]
                Loggers.info(f"根据发票号 {inv_code} 查询到采购发票信息: pi_head_code={pi_info.get('pi_head_code')}, id={pi_info.get('id')}")
                
                # 使用统一的数据转换方法
                return self.convert_data_for_json({
                    "id": pi_info.get("id"),
                    "pi_head_code": pi_info.get("pi_head_code"),
                    "inv_code": pi_info.get("inv_code"),
                    "pi_status": pi_info.get("pi_status"),
                    "doc_type_id": pi_info.get("doc_type_id"),
                    "com_org_id": pi_info.get("com_org_id"),
                    "pur_org_id": pi_info.get("pur_org_id"),
                    "tra_par_id": pi_info.get("tra_par_id"),
                    "tra_par_type": pi_info.get("tra_par_type"),
                    "inv_doc_amt": pi_info.get("inv_doc_amt"),
                    "inv_base_amt": pi_info.get("inv_base_amt"),
                    "inv_doc_tax": pi_info.get("inv_doc_tax"),
                    "inv_base_tax": pi_info.get("inv_base_tax"),
                    "pi_date": pi_info.get("pi_date"),
                    "created_at": pi_info.get("created_at"),
                    "updated_at": pi_info.get("updated_at"),
                    "version": pi_info.get("version")
                })
            else:
                Loggers.warning(f"未找到发票号 {inv_code} 对应的采购发票信息")
                return None
                
        except Exception as e:
            Loggers.error(f"根据发票号 {inv_code} 查询采购发票信息失败: {str(e)}")
            return None

    def get_purchase_invoice_id_by_inv_code(self, inv_code: str) -> Optional[str]:
        """
        根据发票号获取采购发票ID
        :param inv_code: 发票号
        :return: 采购发票ID
        """
        pi_info = self.query_purchase_invoice_by_inv_code(inv_code)
        return pi_info.get("id") if pi_info else None

    def get_purchase_invoice_code_by_inv_code(self, inv_code: str) -> Optional[str]:
        """
        根据发票号获取采购发票编码
        :param inv_code: 发票号
        :return: 采购发票编码(pi_head_code)
        """
        pi_info = self.query_purchase_invoice_by_inv_code(inv_code)
        return pi_info.get("pi_head_code") if pi_info else None

    def create_material(self) -> Dict[str, Any]:
        """创建物料，查库加ENABLED条件，查不到自动插入标准测试数据"""
        try:
            mat = self.query_single_record(
                "gen_mat_md",
                "mat_code LIKE %s AND status = %s AND deleted = 0",
                ['AUTOTEST_MAT%', 'ENABLED'],
                "物料数据"
            )
            return self.build_common_fields(mat, include_id=True)
        except Exception as e:
            Loggers.warning(f"未找到ENABLED状态的AUTOTEST物料，尝试插入标准测试物料: {str(e)}")
            # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
            raise

    def create_vendor(self) -> Dict[str, Any]:
        """创建供应商，查库加ENABLED条件，查不到自动插入标准测试数据"""
        try:
            vend = self.query_single_record(
                "gen_vend_info_md",
                "vend_code LIKE %s AND status = %s AND deleted = 0",
                ['AUTOTEST_VEND%', 'ENABLED'],
                "供应商数据"
            )
            return self.build_common_fields(vend, include_id=True)
        except Exception as e:
            Loggers.warning(f"未找到ENABLED状态的AUTOTEST供应商，尝试插入标准测试供应商: {str(e)}")
            # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
            raise

    def get_default_user_id(self):
        """查库获取自动化测试用户或admin用户ID，查不到自动插入标准测试用户"""
        sql = "SELECT id FROM user WHERE (username = %s OR username = %s) AND deleted = 0 LIMIT 1"
        result = DBManager.query(sql, ["AUTOTEST", "admin"])
        if result:
            return result[0]["id"]
        Loggers.warning("未找到自动化测试用户或admin用户，建议插入标准测试用户")
        # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
        raise Exception("未找到自动化测试用户或admin用户ID，且插入标准测试用户失败")

if __name__ == '__main__':
    print(FinApFactory.get_or_create_ap_doc()) 