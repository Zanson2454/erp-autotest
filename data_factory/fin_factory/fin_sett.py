from pathlib import Path
import sys
from typing import Dict, Any, List
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.mysql_util import DBManager
from utils.log_util import Loggers
from data_factory.base import DataFactory

class FinSettlementFactory(DataFactory):
    
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
        :param status: 状态（CREATED-已创建, CONFIRMED-已确认, SETT_DOC_CREATED-已汇单）
        :return: 结算项数据
        """
        # 1. 尝试从数据库查询
        data = cls._query_settlement_item(status)
        if data:
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
        :param status: 状态（CREATED-已创建, CONFIRMED-已确认）
        :return: 结算单数据
        """
        # 1. 尝试从数据库查询
        data = cls._query_settlement_doc(status)
        if data:
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
            select * from sett_item_tr
            where deleted=0
            and partner_name like '%自动化%'
            and pur_sls_org_name like '%自动化%'
        """
        params = {}
        
        if status:
            sql += " AND sett_item_status = %(status)s"
            params['status'] = status
            
        result = DBManager.query(sql, params)
        return result[0] if result else None

    @staticmethod
    def _query_settlement_doc(status: str = None) -> Optional[Dict[str, Any]]:
        """从数据库查询结算单"""
        sql = """
            select * from sett_doc_tr
            where deleted=0
            and partner_name like '%自动化%'
            and pur_sls_org_name like '%自动化%'
        """
        params = {}
        
        if status:
            sql += " AND sett_doc_status = %(status)s"
            params['status'] = status
            
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
        sql = """
                INSERT INTO terp_test.sett_item_tr (
                    created_at, updated_at, version, deleted, origin_org_id, sett_item_code, sett_item_status, sett_doc_id, 
                    sett_doc_type_id, sett_date, sett_qty, sett_doc_price, mat_id, sett_item_type_id, tax_rate, dn_code, dn_id, 
                    dn_item_code, dn_item_id, remark, inv_org_id, is_sdc_cancel_relv, rel_type, rel_id, ext_latest_pi_sb_date, 
                    sdc_type, ext_sett_doc_price, ext_sett_qty, ext_dpd, create_type, idempotent_key, async_execution_failure_reason, 
                    ext_biz_group, ext_partner, pur_sls_org_type, bkb_settlement_item_code, bkb_settlement_item_id, 
                    whether_auto_generate_bkb_settlement, counterparty_partner_id, lock_key, inv_mvm_item_code, 
                    async_execution_status, gen_mat_type_cf_id, counterparty_com_org_id, id, created_by, updated_by, 
                    basic_unit_id, sett_doc_amt, tax_code_id, tax_amt, net_doc_amt, gross_base_amt, net_base_amt, 
                    doc_curr_id, base_curr_id, exch_rate, com_org_id, partner_code, partner_id, partner_name, 
                    partner_type, pur_sls_org, pur_sls_org_id, pur_sls_org_name, po_so_code, po_so_id, po_so_item_code,
                    po_so_item_id, pt_head_id
                ) 
                    VALUES (
                        DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 
                        DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 
                        0, 0, 0, CONCAT('AUTOTEST-SETTI', DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y%m%d%H%i%s')), %(status)s, null, 2002002, 
                        DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 
                        358.000000, 347.000099, 14431009, 6, 13.00, null, 0, null, 0, '自动化测试新增结算项', 
                        14375002, 0, 'string', 0, null, 'CONFIRM', 0.000000, 0.000000, 0, 'MANUAL', null, null, 'string', 
                        'string', 'SLS', null, null, 0, null, null, null, 'CREATED', 2503002, null, CONCAT('0', LPAD(FLOOR(RAND() * 9999999), 7, '0')), 540175374525637, 
                        540175374525637, 2007001, 124226.04, 2002001, 14291.50, 109934.54, 124226.04, 109934.54, 2000001, 2000001, 
                        1.00, 14373001, null, 2059001, '客户(自动化)', 'CUSTOMER', null, 14579001, '销售组织(自动化)', null, 0, null, 0, null
                    )
            """
        params = {'status': status or 'CREATED'}  # 如果没有传入status，默认使用'CREATED'
        DBManager.execute(sql, params)
        return cls._query_settlement_item(status)

    @classmethod
    def _insert_settlement_doc(cls, status: str = None) -> Dict[str, Any]:
        """直接插入结算单"""
        sql = """
            INSERT INTO terp_test.sett_doc_tr (
                created_at, updated_at, version, deleted, origin_org_id, sett_doc_code, sett_doc_type_id, sett_doc_status, com_org_id, 
                partner_code, partner_id, partner_name, partner_type, pur_sls_org, pur_sls_org_id, async_execution_status, 
                sett_doc_assoc_doc_type_cf_id, trading_doc_id, async_execution_failure_reason, pur_sls_org_name, sett_date, 
                sett_doc_amt, sett_base_amt, doc_curr_id, base_curr_id, remark, trading_doc_status, trading_doc_code, sdc_type, 
                ext_latest_pi_sb_date, ext_biz_group, ext_partner, approve_status, client_side_confirm_status, id, created_by, 
                updated_by, exch_rate) 
                VALUES (
                    DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 
                    DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 1, 0, 0, CONCAT('AUTOTEST-SETTD', DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y%m%d%H%i%s')), 
                    2001001, %(status)s, 14507001, null, 2058001, '供应商(自动化)', 'SUPPLIER', null, 
                    14376001, 'CREATED', null, null, null, '采购组织(自动化)', DATE_FORMAT(CONVERT_TZ(NOW(), '+00:00', '+08:00'), '%Y-%m-%d %H:%i:%s'), 
                    13393788853840942.00, 13393788853840942.00, 2000001, 2000001, null, 'NOT_CREATED', null, 
                    'CONFIRM', null, null, null, null, 'PENDING_CONFIRMED', CONCAT('0', LPAD(FLOOR(RAND() * 9999999), 7, '0')), 476102974181637, 476102974181637, 1.00
                )
        """
        params = {'status': status or 'CREATED'}
        DBManager.execute(sql, params)
        return cls._query_settlement_doc(status)
if __name__ == '__main__':
    print(FinSettlementFactory.get_or_create_settlement_item())
    #print(FinSettlementFactory.get_or_create_settlement_doc())