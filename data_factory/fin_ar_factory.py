from pathlib import Path
import sys
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from decimal import Decimal

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from data_factory.fin_apar_base_factory import FinAparBaseFactory
from utils.mysql_util import DBManager
from utils.log_util import Loggers
from utils.mock_util import MockData

class FinArFactory(FinAparBaseFactory):
    """应收单数据工厂类，继承FinAparBaseFactory"""
    
    def __init__(self):
        """初始化"""
        super().__init__()
        self.mock_data = MockData()
        self._cache = {
            'sett_item_types': {},
            'settlement_methods': {},
            'payment_purposes': {},
            'trading_accounts': {},
            'doc_types': {},
            'base_data': None,
        }

    def _get_cached_or_query(self, cache_key: str, query_func, *args, **kwargs) -> Any:
        """通用缓存查询方法"""
        cache_full_key = f"{cache_key}_{hash(str(args) + str(kwargs))}"
        
        if cache_full_key in self._cache.get(cache_key, {}):
            Loggers.debug(f"从缓存获取数据: {cache_key}")
            return self._cache[cache_key][cache_full_key]
        
        result = query_func(*args, **kwargs)
        
        if cache_key not in self._cache:
            self._cache[cache_key] = {}
        self._cache[cache_key][cache_full_key] = result
        
        return result

    def _query_basic_config_table(self, table_name: str, name_field: str, 
                                 code_field: str = None, where_condition: str = None, 
                                 params: List = None) -> Dict[str, Any]:
        """
        通用基础配置表查询方法
        :param table_name: 表名
        :param name_field: 名称字段
        :param code_field: 编码字段
        :param where_condition: 额外的WHERE条件
        :param params: 查询参数
        :return: 查询结果
        """
        try:
            # 构建基础SQL
            base_fields = "id"
            if code_field:
                base_fields += f", {code_field}"
            base_fields += f", {name_field}"
            
            base_where = "deleted = 0 AND status = 'ENABLED'"
            if where_condition:
                base_where += f" AND {where_condition}"
            
            sql = f"""
                SELECT {base_fields}
                FROM {table_name} 
                WHERE {base_where}
                ORDER BY id ASC
                LIMIT 1
            """
            
            result = DBManager.query(sql, params or [])
            if result:
                row = result[0]
                Loggers.info(f"获取到{table_name}数据: {row.get(name_field)}")
                return {"id": row.get("id")}
            
            # 备用查询：移除status条件
            Loggers.warning(f"未找到启用的{table_name}数据，尝试查找任何可用的数据")
            fallback_where = "deleted = 0"
            if where_condition:
                fallback_where += f" AND {where_condition}"
                
            fallback_sql = f"""
                SELECT {base_fields}
                FROM {table_name} 
                WHERE {fallback_where}
                ORDER BY id ASC
                LIMIT 1
            """
            
            fallback_result = DBManager.query(fallback_sql, params or [])
            if fallback_result:
                row = fallback_result[0]
                Loggers.info(f"使用备用{table_name}数据: {row.get(name_field)}")
                return {"id": row.get("id")}
            
            raise Exception(f"数据库中未找到任何{table_name}数据")
            
        except Exception as e:
            Loggers.error(f"查询{table_name}失败: {str(e)}")
            raise Exception(f"获取{table_name}失败，请检查基础数据配置: {str(e)}")

    def get_settlement_method(self) -> Dict[str, Any]:
        """获取结算方式"""
        return self._get_cached_or_query(
            'settlement_methods',
            self._query_basic_config_table,
            'gen_settlement_method_cf',
            'settlement_method_name',
            'settlement_method_code'
        )

    def get_payment_purpose(self) -> Dict[str, Any]:
        """获取付款目的"""
        return self._get_cached_or_query(
            'payment_purposes',
            self._query_basic_config_table,
            'gen_payment_purpose_cf',
            'payment_purpose_name',
            'payment_purpose_code'
        )

    def get_trading_account(self) -> Dict[str, Any]:
        """获取交易账户"""
        return self._get_cached_or_query(
            'trading_accounts',
            self._query_basic_config_table,
            'gen_trading_account_cf',
            'trading_account_name',
            'trading_account_code'
        )

    def get_doc_type_by_code(self, doc_type_code: str) -> Dict[str, Any]:
        """根据单据类型编码获取单据类型"""
        def _query_doc_type(doc_type_code: str) -> Dict[str, Any]:
            try:
                # 首先尝试精确匹配
                result = self._query_basic_config_table(
                    'gen_doc_type_cf',
                    'doc_type_name',
                    'doc_type_code',
                    'doc_type_code = %s',
                    [doc_type_code]
                )
                return result
            except:
                # 如果精确匹配失败，尝试模糊匹配
                try:
                    Loggers.warning(f"精确匹配{doc_type_code}失败，尝试模糊匹配")
                    pattern = f"%{doc_type_code.split('_')[0]}%"
                    result = self._query_basic_config_table(
                        'gen_doc_type_cf',
                        'doc_type_name',
                        'doc_type_code',
                        'doc_type_code LIKE %s',
                        [pattern]
                    )
                    return result
                except:
                    raise Exception(f"未找到任何匹配{doc_type_code}的单据类型")
        
        return self._get_cached_or_query(
            'doc_types',
            _query_doc_type,
            doc_type_code
        )

    def get_settlement_item_type_by_code(self, sett_item_type_code: str) -> Dict[str, Any]:
        """
        根据结算项目类型编码从数据库查询结算项目类型
        :param sett_item_type_code: 结算项目类型编码
        :return: 结算项目类型数据
        """
        # 检查缓存
        if sett_item_type_code in self._cache['sett_item_types']:
            return self._cache['sett_item_types'][sett_item_type_code].copy()
        
        try:
            sql = """
                SELECT * FROM gen_sett_item_type_cf 
                WHERE sett_item_type_code = %s AND deleted = 0 AND status = 'ENABLED'
                LIMIT 1
            """
            result = DBManager.query(sql, [sett_item_type_code])
            if result:
                row = result[0]
                self._cache['sett_item_types'][sett_item_type_code] = row
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

    def get_base_data_for_fin_doc(self, doc_type: str = "AR") -> Dict[str, Any]:
        """获取财务单据基础数据，使用父类方法"""
        if self._cache['base_data'] is None:
            # 使用父类的基础数据获取方法
            self._cache['base_data'] = super().get_base_data_for_fin_doc(doc_type)
        return self._cache['base_data']

    def clear_cache(self, cache_type: str = None) -> None:
        """
        清理缓存
        :param cache_type: 要清理的缓存类型，None表示清理所有缓存
        """
        if cache_type is None:
            # 清理所有缓存
            for key in self._cache:
                if isinstance(self._cache[key], dict):
                    self._cache[key].clear()
                else:
                    self._cache[key] = None
            Loggers.info("已清理所有缓存")
        elif cache_type in self._cache:
            if isinstance(self._cache[cache_type], dict):
                self._cache[cache_type].clear()
            else:
                self._cache[cache_type] = None
            Loggers.info(f"已清理{cache_type}缓存")
        else:
            Loggers.warning(f"缓存类型{cache_type}不存在")

    def create_pn_request_data(self, ar_info: Dict[str, Any], partial_amount: float = None) -> Dict[str, Any]:
        """
        创建收款单请求数据
        :param ar_info: 应收单信息，包含ar_doc_id, ar_head_code, ar_schl_ids, gross_doc_amt等
        :param partial_amount: 部分收款金额，不传则全额收款
        :return: 收款单请求数据
        """
        try:
            # 基础数据
            ar_doc_id = ar_info.get("ar_doc_id")
            ar_head_code = ar_info.get("ar_head_code")
            ar_schl_ids = ar_info.get("ar_schl_ids", [])
            gross_doc_amt = ar_info.get("gross_doc_amt", 40000)
            gross_base_amt = ar_info.get("gross_base_amt", 40000)
            
            # 计算收款金额
            if partial_amount is None:
                partial_amount = gross_doc_amt
            
            ar_schl_id = ar_schl_ids[0] if ar_schl_ids else None
            ar_date = int(datetime.now().timestamp() * 1000)
            
            # 通过数据工厂获取基础数据
            base_data = self.get_base_data_for_fin_doc("AR")
            
            # 获取动态数据
            settlement_method = self.get_settlement_method()
            payment_purpose = self.get_payment_purpose()
            trading_account = self.get_trading_account()
            doc_type = self.get_doc_type_by_code("PN_REC")
            
            # 构建收款单数据
            pn_request_data = {
                "collectedPaidDocAmt": partial_amount,
                "collectedPaidBaseAmt": partial_amount,
                "headOffsetStatus": "UNOFFSET",
                "relatedCreated": "RELATED",
                "pnClass": "REC",
                "pnStatus": "DRAFT",
                "docTypeId": doc_type,
                "pnDate": ar_date,
                "comOrgId": {"id": base_data["com_org"]["id"]},
                "purSlsOrgId": {"id": base_data["sls_org"]["id"]},
                "payRecOrgId": {"id": base_data["com_org"]["id"]},
                "tradingPartnerType": "CUSTOMER",
                "tradingPartnerId": {"id": base_data["customer"]["id"]},
                "payerType": "CUSTOMER",
                "payerId": {"id": base_data["customer"]["id"]},
                "currId": {"id": base_data["currency"]["id"]},
                "baseCurrId": {
                    "currName": base_data["currency"]["currName"],
                    "currCode": base_data["currency"]["currCode"],
                    "id": base_data["currency"]["id"]
                },
                "exchRate": 1,
                "pnItems": [{
                    "arApDocAmt": partial_amount,
                    "collectedPaidDocAmt": partial_amount,
                    "arApBaseAmt": partial_amount,
                    "collectedPaidBaseAmt": partial_amount,
                    "clearingDocAmt": gross_doc_amt,
                    "clearingBaseAmt": gross_base_amt,
                    "relDocClass": "AR",
                    "relDocHeadCode": ar_head_code,
                    "relDocItemCode": f"ARS{ar_head_code[2:]}",
                    "relDocHeadId": {"id": ar_doc_id},
                    "relDocItemId": {"id": ar_schl_id},
                    "settlementMethodCode": settlement_method,
                    "paymentPurposeCode": payment_purpose,
                    "tradingAccountCode": trading_account
                }],
                "pnLinks": [{
                    "sourceType": "AR",
                    "sourceHeadCode": ar_head_code,
                    "sourceSchlCode": f"ARS{ar_head_code[2:]}",
                    "sourceCurrId": {"id": base_data["currency"]["id"]},
                    "expireDate": ar_date,
                    "sourceArApAmt": gross_doc_amt,
                    "thisTimePnAmt": partial_amount,
                    "thisTimePnBaseAmt": partial_amount,
                    "sourceHeadId": {"id": ar_doc_id},
                    "sourceItemId": {"id": ar_schl_id}
                }]
            }
            
            Loggers.info(f"创建收款单请求数据完成，应收单ID: {ar_doc_id}, 收款金额: {partial_amount}")
            return pn_request_data
            
        except Exception as e:
            Loggers.error(f"创建收款单请求数据失败: {str(e)}")
            raise

    def create_sb_request_data(self, ar_info: Dict[str, Any], partial_amount: float = None, 
                              partial_qty: int = None, bil_code: str = None) -> Dict[str, Any]:
        """
        创建销售发票请求数据
        :param ar_info: 应收单信息，包含ar_doc_id, ar_head_code, ar_item_ids, gross_doc_amt等
        :param partial_amount: 部分开票金额，不传则全额开票
        :param partial_qty: 部分开票数量，不传则按比例计算
        :param bil_code: 发票编码，不传则自动生成
        :return: 销售发票请求数据
        """
        try:
            # 基础数据
            ar_doc_id = ar_info.get("ar_doc_id")
            ar_head_code = ar_info.get("ar_head_code")
            ar_item_ids = ar_info.get("ar_item_ids", [])
            gross_doc_amt = ar_info.get("gross_doc_amt", 40000)
            
            # 计算开票金额和数量
            if partial_amount is None:
                partial_amount = gross_doc_amt
            
            # 假设总数量为100，按比例计算部分数量
            total_qty = 100
            if partial_qty is None:
                partial_qty = int(total_qty * (partial_amount / gross_doc_amt))
            
            if bil_code is None:
                bil_code = self.mock_data.generate_unique_code("AUTO")
            
            sb_date = int(datetime.now().timestamp() * 1000)
            
            # 通过数据工厂获取基础数据
            base_data = self.get_base_data_for_fin_doc("AR")
            
            # 获取动态数据
            sb_doc_type = self.get_doc_type_by_code("SB")
            sett_item_type = self.get_sales_settlement_item_type()
            
            # 计算税额和不含税金额 (假设税率13%)
            tax_rate = 0.13
            partial_net_doc_amt = round(partial_amount / (1 + tax_rate), 2)  # 不含税金额
            partial_tax_doc_amt = partial_amount - partial_net_doc_amt  # 税额
            
            ar_item_id = ar_item_ids[0] if ar_item_ids else None
            
            # 构建销售发票数据
            sb_request_data = {
                "bilCode": bil_code,
                "docTypeId": sb_doc_type,
                "posNeg": "BLUE",
                "sbDate": sb_date,
                "pstDate": sb_date,
                "slsOrgId": {"id": base_data["sls_org"]["id"]},
                "comOrgId": {"id": base_data["com_org"]["id"]},
                "traParType": "CUSTOMER",
                "traParId": {"id": base_data["customer"]["id"]},
                "docCurrId": {"id": base_data["currency"]["id"]},
                "baseCurrId": {"id": base_data["currency"]["id"]},
                "exchRate": 1,
                "createType": "AUTO",
                "bilBaseAmt": partial_amount,  # 发票总金额(本位币)
                "bilDocAmt": partial_amount,   # 发票总金额(原币)
                "unoffsetDocAmt": partial_amount,  # 未冲销金额(原币)
                "unoffsetBaseAmt": partial_amount, # 未冲销金额(本位币)
                "relatedCreated": "RELATED",
                "sbItems": [{
                    "matId": {"id": base_data["material"]["id"]},
                    "taxCodeId": {"id": base_data["tax_code"]["id"]},
                    "taxRate": 13,
                    "valQty": partial_qty,  # 开票数量
                    "grossDocPrice": partial_amount / partial_qty,  # 单价
                    "grossDocAmt": partial_amount,  # 含税金额(原币)
                    "grossBaseAmt": partial_amount,  # 含税金额(本位币)
                    "netDocAmt": partial_net_doc_amt,  # 不含税金额(原币)
                    "netBaseAmt": partial_net_doc_amt,  # 不含税金额(本位币)
                    "taxDocAmt": partial_tax_doc_amt,  # 税额(原币)
                    "taxBaseAmt": partial_tax_doc_amt,  # 税额(本位币)
                    "netDocPrice": partial_net_doc_amt / partial_qty,  # 不含税单价
                    "netBasePrice": partial_net_doc_amt / partial_qty,  # 不含税单价(本位币)
                    "unoffsetQty": partial_qty,  # 未冲销数量
                    "unoffsetDocAmt": partial_amount,  # 未冲销金额(原币)
                    "unoffsetBaseAmt": partial_amount,  # 未冲销金额(本位币)
                    "relDocClass": "AR",
                    "relDocHeadCode": ar_head_code,
                    "relDocItemCode": f"ARI{ar_head_code[2:]}",
                    "relDocHeadId": {"id": ar_doc_id},
                    "relDocItemId": {"id": ar_item_id},
                    "settItemTypeId": sett_item_type,
                    "clearingQty": partial_qty,  # 结算数量
                    "clearingDocAmt": partial_amount,  # 结算金额(原币)
                    "clearingBaseAmt": partial_amount   # 结算金额(本位币)
                }]
            }
            
            Loggers.info(f"创建销售发票请求数据完成，应收单ID: {ar_doc_id}, 开票金额: {partial_amount}, 开票数量: {partial_qty}")
            return sb_request_data
            
        except Exception as e:
            Loggers.error(f"创建销售发票请求数据失败: {str(e)}")
            raise

if __name__ == '__main__':
    factory = FinArFactory()
    print(factory.create_currency()) 