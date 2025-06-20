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
        self._sett_item_types_cache = {}  # 缓存结算项目类型

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
                SELECT * FROM gen_sett_item_type_cf 
                WHERE sett_item_type_code = %s AND deleted = 0 AND status = 'ENABLED'
                LIMIT 1
            """
            result = DBManager.query(sql, [sett_item_type_code])
            if result:
                row = result[0]
                self._sett_item_types_cache[sett_item_type_code] = row
                return row.copy()
            Loggers.warning(f"未找到ENABLED状态的结算项目类型[{sett_item_type_code}]，建议插入标准测试类型")
            # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
            raise Exception(f"未找到结算项目类型[{sett_item_type_code}]，且插入标准测试类型失败")
        except Exception as e:
            Loggers.error(f"查询结算项目类型失败，编码: {sett_item_type_code}, 错误: {str(e)}")
            raise

    def get_sales_settlement_item_type(self) -> Dict[str, Any]:
        """
        查询销售相关的结算项目类型
        :return: 结算项目类型
        """
        try:
            sql = """
                SELECT 
                    id, sett_item_type_code, sett_item_type_name
                FROM gen_sett_item_type_cf 
                WHERE bt_class = 'SALES' AND deleted = 0
                ORDER BY id ASC
                LIMIT 1
            """
            
            result = DBManager.query(sql)
            
            if result:
                row = result[0]
                sett_item_type = {"id": row.get("id")}
                Loggers.info(f"查询到销售结算项目类型: {row.get('sett_item_type_name')}")
                return sett_item_type
            else:
                Loggers.warning("未找到销售相关的结算项目类型，使用默认ID")
                return {"id": 12}
                
        except Exception as e:
            Loggers.error(f"查询销售结算项目类型失败: {str(e)}")
            return {"id": 12}

    def get_dynamic_ar_item_config(self, style="default") -> Dict[str, Any]:
        """
        动态生成应收单明细配置
        :param style: 配置样式
        :return: 明细配置
        """
        base_config = {
            "arQty": 100,
            "grossDocPrice": 400,
            "grossDocAmt": 40000,
            "grossBaseAmt": 40000,
            "taxRate": 13,
            "taxAmt": 4601.77
        }
        
        if style == "page_style":
            base_config.update({
                "netDocAmt": 35398.23,
                "netBaseAmt": 35398.23
            })
        else:
            base_config.update({
                "netDocAmt": 40000,
                "netBaseAmt": 40000
            })
        
        return base_config

    def get_dynamic_ar_schl_config(self, style="default") -> Dict[str, Any]:
        """
        动态生成应收单计划配置
        :param style: 配置样式
        :return: 计划配置
        """
        base_config = {
            "arDocAmt": 40000,
            "arBaseAmt": 40000,
            "arPercent": 100,
            "collectionClearingStatus": "UNCLEARED"
        }
        
        if style == "page_style":
            base_config.update({
                "receivedDocAmt": 0,
                "unreceivedDocAmt": 40000,
                "receivedBaseAmt": 0,
                "unreceivedBaseAmt": 40000,
                "receivingDocAmt": 0,
                "receivingBaseAmt": 0,
                "context": {}
            })
        
        return base_config

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
        """
        创建应收单明细项，所有ID均通过查库获取，日期用时间戳
        """
        config = self.get_dynamic_ar_item_config(style)
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
        
        config = self.get_dynamic_ar_schl_config(style)
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
        """查库获取单据类型，查不到自动插入标准测试类型"""
        sql = "SELECT * FROM gen_doc_type_cf WHERE doc_type_code = %s AND deleted = 0 AND status = 'ENABLED' LIMIT 1"
        result = DBManager.query(sql, ["STND"])
        if result:
            row = result[0]
            return row
        Loggers.warning("未找到ENABLED状态的标准单据类型（STND），建议插入标准测试类型")
        # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
        raise Exception("未找到标准单据类型（STND），且插入标准测试类型失败")

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

    def query_sales_invoice_by_bil_code(self, bil_code: str) -> Optional[Dict[str, Any]]:
        """根据bil_code查询销售发票完整信息，包括税额"""
        if not bil_code:
            Loggers.warning("bil_code参数不能为空")
            return None
            
        sql = """
            SELECT sb_head_code, id, bil_code, bil_doc_amt, bil_base_amt, 
                   bil_doc_tax, bil_base_tax, clearing_doc_amt, clearing_base_amt,
                   sb_status, confirm_status, created_at, updated_at
            FROM fin_tm_sb_head_tr 
            WHERE deleted = 0 
            AND bil_code = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        try:
            result = DBManager.query(sql, [bil_code])
            if result:
                row = result[0]
                # 手动转换数据类型
                sb_info = {
                    "id": row["id"],
                    "sb_head_code": row["sb_head_code"],
                    "bil_code": row["bil_code"],
                    "bil_doc_amt": float(row["bil_doc_amt"]) if row["bil_doc_amt"] is not None else 0.0,
                    "bil_base_amt": float(row["bil_base_amt"]) if row["bil_base_amt"] is not None else 0.0,
                    "bil_doc_tax": float(row["bil_doc_tax"]) if row["bil_doc_tax"] is not None else 0.0,
                    "bil_base_tax": float(row["bil_base_tax"]) if row["bil_base_tax"] is not None else 0.0,
                    "clearing_doc_amt": float(row["clearing_doc_amt"]) if row["clearing_doc_amt"] is not None else 0.0,
                    "clearing_base_amt": float(row["clearing_base_amt"]) if row["clearing_base_amt"] is not None else 0.0,
                    "sb_status": row["sb_status"],
                    "confirm_status": row["confirm_status"],
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S") if row["created_at"] else None,
                    "updated_at": row["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if row["updated_at"] else None
                }
                Loggers.info(f"根据bil_code[{bil_code}]查询到销售发票完整信息: {sb_info}")
                return sb_info
            else:
                Loggers.warning(f"未找到bil_code为[{bil_code}]的销售发票记录")
                return None
                
        except Exception as e:
            Loggers.error(f"查询销售发票完整信息失败，bil_code: {bil_code}, 错误: {str(e)}")
            raise Exception(f"查询销售发票完整信息失败: {str(e)}")

    def get_sales_invoice_id_by_bil_code(self, bil_code: str) -> Optional[int]:
        """根据bil_code获取销售发票ID"""
        sb_info = self.query_sales_invoice_by_bil_code(bil_code)
        return sb_info.get("id") if sb_info else None
        
    def get_sales_invoice_code_by_bil_code(self, bil_code: str) -> Optional[str]:
        """根据bil_code获取销售发票编码"""
        sb_info = self.query_sales_invoice_by_bil_code(bil_code)
        return sb_info.get("sb_head_code") if sb_info else None

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

    def get_ar_schl_ids_by_ar_id(self, ar_doc_id: int) -> List[int]:
        """
        根据应收单ID查询应收计划行ID列表
        :param ar_doc_id: 应收单ID
        :return: 应收计划行ID列表
        """
        if not ar_doc_id:
            Loggers.warning("ar_doc_id参数不能为空")
            return []
            
        sql = """
            SELECT id FROM fin_arm_ar_schl_tr 
            WHERE arm_ar_head_tr_id = %s AND deleted = 0
            ORDER BY created_at ASC
        """
        
        try:
            result = DBManager.query(sql, [ar_doc_id])
            ar_schl_ids = [row['id'] for row in result] if result else []
            Loggers.info(f"根据应收单ID[{ar_doc_id}]查询到{len(ar_schl_ids)}个计划行ID: {ar_schl_ids}")
            return ar_schl_ids
        except Exception as e:
            Loggers.error(f"查询应收计划行ID失败，ar_doc_id: {ar_doc_id}, 错误: {str(e)}")
            return []

    def get_ar_item_ids_by_ar_id(self, ar_doc_id: int) -> List[int]:
        """
        根据应收单ID查询应收单行ID列表
        :param ar_doc_id: 应收单ID
        :return: 应收单行ID列表
        """
        if not ar_doc_id:
            Loggers.warning("ar_doc_id参数不能为空")
            return []
            
        sql = """
            SELECT id FROM fin_arm_ar_item_tr 
            WHERE arm_ar_head_tr_id = %s AND deleted = 0
            ORDER BY created_at ASC
        """
        
        try:
            result = DBManager.query(sql, [ar_doc_id])
            ar_item_ids = [row['id'] for row in result] if result else []
            Loggers.info(f"根据应收单ID[{ar_doc_id}]查询到{len(ar_item_ids)}个应收单行ID: {ar_item_ids}")
            return ar_item_ids
        except Exception as e:
            Loggers.error(f"查询应收单行ID失败，ar_doc_id: {ar_doc_id}, 错误: {str(e)}")
            return []

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

    def create_customer(self) -> Dict[str, Any]:
        """创建客户，查库加ENABLED条件，查不到自动插入标准测试数据"""
        try:
            cust = self.query_single_record(
                "gen_cust_info_md",
                "cust_code LIKE %s AND status = %s AND deleted = 0",
                ['AUTOTEST_CUST%', 'ENABLED'],
                "客户数据"
            )
            return self.build_common_fields(cust, include_id=True)
        except Exception as e:
            Loggers.warning(f"未找到ENABLED状态的AUTOTEST客户，尝试插入标准测试客户: {str(e)}")
            # 这里可补充插入逻辑，如插入后再查一次，否则抛异常
            raise

if __name__ == '__main__':
    factory = FinArFactory()
    print(factory.create_currency()) 