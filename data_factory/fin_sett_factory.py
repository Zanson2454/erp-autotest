from pathlib import Path
import sys
from typing import Dict, Any, List
from typing import Dict, Any, Optional

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


from data_factory.base import DataFactory

from utils.mysql_util import DBManager
from utils.log_util import Loggers
from data_factory.base import DataFactory

class FinSettlementFactory:
    
    """财务结算数据工厂类"""
    # 状态常量
    STATUS_CREATED = 'CREATED'  # 已创建
    STATUS_CONFIRMED = 'CONFIRMED'  # 已确认
    STATUS_SETT_DOC_CREATED = 'SETT_DOC_CREATED'  # 已汇单
    STATUS_RECONCILED = 'RECONCILED'  # 已对账
    
    @classmethod
    def get_or_create_settlement_item(cls, status: str = None) -> Dict[str, Any]:
        """
        获取或创建结算项
        :param status: 状态（CREATED-已创建, CONFIRMED-已确认）
        :return: 结算项数据
        """
        data_factory = DataFactory() 
        db_config = data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        # 1. 尝试从数据库查询
        data = cls._query_settlement_item(status)
        if  data:
            Loggers.info(f"从数据库获取到结算项数据: {data.get('id')}")
            return data
            
        # 2. 尝试通过接口创建
        try:
            data = cls._create_settlement_item_via_api()
            if data:
                Loggers.info(f"通过接口成功创建结算项数据: {data.get('id')}")
                return data
        except Exception as e:
            Loggers.warning(f"通过接口创建结算项数据失败: {str(e)}")
            
        # 3. 如果接口创建失败，尝试直接数据库插入
        try:
            data = cls._insert_settlement_item(status)
            Loggers.info(f"通过数据库插入成功创建结算项数据: {data.get('id')}")
            return data
        except Exception as e:
            Loggers.error(f"数据库插入结算项数据失败: {str(e)}")
            raise

    @classmethod
    def get_or_create_settlement_doc(cls, status: str = None) -> Dict[str, Any]:
        """
        获取或创建结算单
        :param status: 状态（CREATED-已创建(同时得到已汇单结算项)）
        :return: 结算单数据
        """
        data_factory = DataFactory() 
        db_config = data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        # 1. 尝试从数据库查询
        data = cls._query_settlement_doc(status)
        if  data:
            Loggers.info(f"从数据库获取到结算单数据: {data.get('id')}")
            return data
            
        # 2. 尝试通过接口创建
        try:
            data = cls._create_settlement_doc_via_api()
            if data:
                Loggers.info(f"通过接口成功创建结算单数据: {data.get('id')}")
                return data
        except Exception as e:
            Loggers.warning(f"通过接口创建结算单数据失败: {str(e)}")
            
        # 3. 如果接口创建失败，尝试直接数据库插入
        try:
            data = cls._insert_settlement_doc(status)
            Loggers.info(f"通过数据库插入成功创建结算单数据: {data.get('id')}")
            return data
        except Exception as e:
            Loggers.error(f"数据库插入结算单数据失败: {str(e)}")
            raise

    @staticmethod
    def _query_settlement_item(status: str = None) -> Optional[Dict[str, Any]]:
        """从数据库查询任意状态结算项"""
        sql = """
            SELECT * FROM sett_item_tr
            WHERE deleted = 0
            AND partner_name LIKE %s
            AND pur_sls_org_name LIKE %s
        """
        params = ['%自动化%', '%自动化%']
        
        if status:
            sql += " AND sett_item_status = %s"
            params.append(status)
            
        result = DBManager.query(sql, params)
        return result[0] if result else None

    @staticmethod
    def _query_settlement_doc(status: str = None) -> Optional[Dict[str, Any]]:
        """从数据库查询结算单"""
        sql = """
            SELECT * FROM sett_doc_tr
            WHERE deleted = 0
            AND partner_name LIKE %s
            AND pur_sls_org_name LIKE %s
        """
        params = ['%自动化%', '%自动化%']
        
        if status:
            sql += " AND sett_doc_status = %s"
            params.append(status)
            
        result = DBManager.query(sql, params)
        return result[0] if result else None

    @staticmethod
    def _create_settlement_item_via_api() -> Optional[Dict[str, Any]]:
        """通过接口创建结算项"""
        """ api_url = '/api/trantor/service/engine/execute/ERP_FIN$SETT_ITEM_MANUAL_CREATE_EVENT_SERVICE'
        # 确保创建自动化测试数据
        data = {
            'partner_name': '自动化测试供应商',
            'pur_sls_org_name': '自动化测试组织'
        } """
        """ response = HttpUtil.post(api_url, json=data)
        if response.status_code == 200:
            return response.json() """
        return None

    @staticmethod
    def _create_settlement_doc_via_api() -> Optional[Dict[str, Any]]:
        """通过接口创建结算单"""
        """ api_url = '/api/trantor/service/engine/execute/ERP_FIN$SETT_DOC_CREATE_EVENT_SERVICE'
        # 确保创建自动化测试数据
        data = {
            'partner_name': '自动化测试供应商',
            'pur_sls_org_name': '自动化测试组织'
        } """
        """ response = HttpUtil.post(api_url, json=data)
        if response.status_code == 200:
            return response.json() """
        return None

    @classmethod
    def _insert_settlement_item(cls, status: str = None) -> Dict[str, Any]:
        """直接插入已创建或已对账结算项"""
        from datetime import datetime
        now = datetime.now()
        
        data = {
            'created_at': now,
            'updated_at': now,
            'version': 0,
            'deleted': 0,
            'origin_org_id': 0,
            'sett_item_code': f'AUTOTEST-SETTI{now.strftime("%Y%m%d%H%M%S")}',
            'sett_item_status': status or 'CREATED',
            'sett_doc_id': None,
            'sett_doc_type_id': 2002002,
            'sett_date': now,
            'sett_qty': 358.000000,
            'sett_doc_price': 347.000099,
            'mat_id': 14431009,
            'sett_item_type_id': 6,
            'tax_rate': 13.00,
            'dn_code': None,
            'dn_id': 0,
            'dn_item_code': None,
            'dn_item_id': 0,
            'remark': '自动化测试新增结算项',
            'inv_org_id': 14375002,
            'is_sdc_cancel_relv': 0,
            'rel_type': 'string',
            'rel_id': 0,
            'ext_latest_pi_sb_date': None,
            'sdc_type': 'CONFIRM',
            'ext_sett_doc_price': 0.000000,
            'ext_sett_qty': 0.000000,
            'ext_dpd': 0,
            'create_type': 'MANUAL',
            'idempotent_key': None,
            'async_execution_failure_reason': None,
            'ext_biz_group': 'string',
            'ext_partner': 'string',
            'pur_sls_org_type': 'SLS',
            'bkb_settlement_item_code': None,
            'bkb_settlement_item_id': None,
            'whether_auto_generate_bkb_settlement': 0,
            'counterparty_partner_id': None,
            'lock_key': None,
            'inv_mvm_item_code': None,
            'async_execution_status': 'CREATED',
            'gen_mat_type_cf_id': 2503002,
            'counterparty_com_org_id': None,
            'id': f'0{str(int(now.timestamp() * 1000))[-7:]}',
            'created_by': 540175374525637,
            'updated_by': 540175374525637,
            'basic_unit_id': 2007001,
            'sett_doc_amt': 124226.04,
            'tax_code_id': 2002001,
            'tax_amt': 14291.50,
            'net_doc_amt': 109934.54,
            'gross_base_amt': 124226.04,
            'net_base_amt': 109934.54,
            'doc_curr_id': 2000001,
            'base_curr_id': 2000001,
            'exch_rate': 1.00,
            'com_org_id': 14373001,
            'partner_code': None,
            'partner_id': 2059001,
            'partner_name': '客户(自动化)',
            'partner_type': 'CUSTOMER',
            'pur_sls_org': None,
            'pur_sls_org_id': 14579001,
            'pur_sls_org_name': '销售组织(自动化)',
            'po_so_code': None,
            'po_so_id': 0,
            'po_so_item_code': None,
            'po_so_item_id': 0,
            'pt_head_id': None
        }
        DBManager.insert('sett_item_tr', data)
        return cls._query_settlement_item(status)

    @classmethod
    def _insert_settlement_doc(cls, status: str = None) -> Dict[str, Any]:
        """直接插入结算单"""
        from datetime import datetime
        now = datetime.now()
        id = f'0{str(int(now.timestamp() * 1000))[-7:]}'
        data = {
            'created_at': now,
            'updated_at': now,
            'version': 1,
            'deleted': 0,
            'origin_org_id': 0,
            'sett_doc_code': f'AUTOTEST-SETTD{now.strftime("%Y%m%d%H%M%S")}',
            'sett_doc_type_id': 2002002,
            'sett_doc_status': 'CREATED',
            'com_org_id': 14373001,
            'partner_code': None,
            'partner_id': 2059001,
            'partner_name': '客户(自动化)',
            'partner_type': 'CUSTOMER',
            'pur_sls_org': None,
            'pur_sls_org_id': 14579001,
            'async_execution_status': 'CREATED',
            'sett_doc_assoc_doc_type_cf_id': None,
            'trading_doc_id': None,
            'async_execution_failure_reason': None,
            'pur_sls_org_name': '销售组织(自动化)',
            'sett_date': now,
            'sett_doc_amt': 124266.036442,
            'sett_base_amt': 124266.036442,
            'doc_curr_id': 2000001,
            'base_curr_id': 2000001,
            'remark': None,
            'trading_doc_status': 'NOT_CREATED',
            'trading_doc_code': None,
            'sdc_type': 'CONFIRM',
            'ext_latest_pi_sb_date': None,
            'ext_biz_group': None,
            'ext_partner': None,
            'approve_status': None,
            'client_side_confirm_status': 'PENDING_CONFIRMED',
            'id': id,
            'created_by': 476102974181637,
            'updated_by': 476102974181637,
            'exch_rate': 1.00
        }
        sett_item_data = {
            'created_at': now,
            'updated_at': now,
            'version': 0,
            'deleted': 0,
            'origin_org_id': 0,
            'sett_item_code': f'AUTOTEST-SETTI{now.strftime("%Y%m%d%H%M%S")}',
            'sett_item_status':  'SETT_DOC_CREATED',
            'sett_doc_id': id,
            'sett_doc_type_id': 2001001,
            'sett_date': now,
            'sett_qty': 358.000000,
            'sett_doc_price': 347.000099,
            'mat_id': 14431009,
            'sett_item_type_id': 6,
            'tax_rate': 13.00,
            'dn_code': None,
            'dn_id': 0,
            'dn_item_code': None,
            'dn_item_id': 0,
            'remark': '自动化测试新增结算项',
            'inv_org_id': 14375002,
            'is_sdc_cancel_relv': 0,
            'rel_type': 'string',
            'rel_id': 0,
            'ext_latest_pi_sb_date': None,
            'sdc_type': 'CONFIRM',
            'ext_sett_doc_price': 0.000000,
            'ext_sett_qty': 0.000000,
            'ext_dpd': 0,
            'create_type': 'MANUAL',
            'idempotent_key': None,
            'async_execution_failure_reason': None,
            'ext_biz_group': 'string',
            'ext_partner': 'string',
            'pur_sls_org_type': 'SLS',
            'bkb_settlement_item_code': None,
            'bkb_settlement_item_id': None,
            'whether_auto_generate_bkb_settlement': 0,
            'counterparty_partner_id': None,
            'lock_key': None,
            'inv_mvm_item_code': None,
            'async_execution_status': 'SUCCEEDED',
            'gen_mat_type_cf_id': 2503002,
            'counterparty_com_org_id': None,
            'id': f'0{str(int(now.timestamp() * 1000))[-7:]}',
            'created_by': 540175374525637,
            'updated_by': 540175374525637,
            'basic_unit_id': 2007001,
            'sett_doc_amt': 124226.04,
            'tax_code_id': 2002001,
            'tax_amt': 14291.50,
            'net_doc_amt': 109934.54,
            'gross_base_amt': 124226.04,
            'net_base_amt': 109934.54,
            'doc_curr_id': 2000001,
            'base_curr_id': 2000001,
            'exch_rate': 1.00,
            'com_org_id': 14373001,
            'partner_code': None,
            'partner_id': 2059001,
            'partner_name': '客户(自动化)',
            'partner_type': 'CUSTOMER',
            'pur_sls_org': None,
            'pur_sls_org_id': 14579001,
            'pur_sls_org_name': '销售组织(自动化)',
            'po_so_code': None,
            'po_so_id': 0,
            'po_so_item_code': None,
            'po_so_item_id': 0,
            'pt_head_id': None
        }
        DBManager.insert('sett_doc_tr', data)
        DBManager.insert('sett_item_tr', sett_item_data)
        return cls._query_settlement_doc(status)
if __name__ == '__main__':
    print(FinSettlementFactory.get_or_create_settlement_item())
    print(FinSettlementFactory.get_or_create_settlement_doc())