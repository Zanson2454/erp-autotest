from pathlib import Path
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from data_factory.fin_apar_base_factory import FinAparBaseFactory
from utils.mysql_util import DBManager
from utils.log_util import Loggers

class FinArFactory(FinAparBaseFactory):
    """应收单数据工厂类，继承FinAparBaseFactory"""
    
    def __init__(self):
        """初始化"""
        super().__init__()

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

    # 应收单特有的查询方法
    def get_customer_by_id(self, cust_id: int) -> dict:
        """根据ID查询客户"""
        cust = self.query_single_record("gen_cust_info_md", "id = %s", [cust_id], f"ID为{cust_id}的客户")
        return {"id": cust["id"]}

    def get_tax_code_by_id(self, tax_code_id: int) -> dict:
        """根据ID查询税码"""
        tax = self.query_single_record("gen_tax_type_cf", "id = %s", [tax_code_id], f"ID为{tax_code_id}的税码")
        return {"id": tax["id"]}

    def get_material_by_id(self, mat_id: int) -> dict:
        """根据ID查询物料"""
        mat = self.query_single_record("gen_mat_md", "id = %s", [mat_id], f"ID为{mat_id}的物料")
        return {"id": mat["id"]}

    def get_sett_item_type_by_id(self, sett_item_type_id: int) -> dict:
        """根据ID查询结算项目类型"""
        return {"id": sett_item_type_id}

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
        """创建应收单明细列表"""
        return [self._create_ar_item(mat_id, tax_code_id, sett_item_type_id, "default")]

    def create_ar_items_full_by_page(self, mat, tax_code, sett_item_type):
        """按页面抓包结构生成arItems明细列表"""
        return [self._create_ar_item(mat["id"], tax_code["id"], sett_item_type["id"], "page_style")]

    def create_ar_schls_full(self, amount=40000, due_date=None) -> list:
        """创建应收单计划列表"""
        return [self._create_ar_schl(due_date, "default")]

    def create_ar_schls_full_by_page(self, now_ts):
        """按页面抓包结构生成arSchls计划列表"""
        return [self._create_ar_schl(now_ts, "page_style")]

    # 应收单特有的from_row方法
    def create_customer_from_row(self, cust: dict) -> dict:
        """从数据库行创建客户对象"""
        result = {
            "custCode": cust["cust_code"],
            "custName": cust["cust_name"],
            "status": cust["status"],
            "custCateType": cust.get("cust_cate_type"),
            "custType": {"id": cust.get("cust_type_id")},
            "com": {"id": cust.get("com_id")},
            "id": cust["id"],
        }
        result.update(self.build_common_fields(cust))
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
        return self.get_latest_fin_doc_id_by_status('fin_arm_ar_head_tr', 'ar_status', status)

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