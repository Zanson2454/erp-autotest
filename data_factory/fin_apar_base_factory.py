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


class FinAparBaseFactory(DataFactory):
    """应收应付模块数据工厂基类，继承DataFactory，提供通用的业务对象创建方法"""
    
    # 状态常量
    STATUS_ACTIVE = "ACTIVE"
    STATUS_INACTIVE = "INACTIVE"
    STATUS_DRAFT = "DRAFT"
    STATUS_CONFIRMED = "CONFIRMED"
    
    def __init__(self):
        """初始化，调用父类初始化方法"""
        super().__init__()

    def query_single_record(self, table_name: str, where_clause: str, params: List[Any], description: str) -> Dict[str, Any]:
        """
        查询单条记录的通用方法
        :param table_name: 表名
        :param where_clause: WHERE条件
        :param params: 参数列表
        :param description: 描述信息
        :return: 查询结果
        """
        sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1"
        try:
            result = DBManager.query(sql, params)
            if not result:
                raise Exception(f"未找到{description}")
            return result[0]
        except Exception as e:
            Loggers.error(f"查询{description}失败: {str(e)}")
            raise

    def build_common_fields(self, data: Dict[str, Any], include_id: bool = False) -> Dict[str, Any]:
        """
        构建通用字段
        :param data: 原始数据
        :param include_id: 是否包含ID字段
        :return: 通用字段字典
        """
        def to_timestamp(dt):
            """统一的时间戳转换方法"""
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            return dt
        
        common_fields = {
            "createdAt": to_timestamp(data.get("created_at")),
            "updatedAt": to_timestamp(data.get("updated_at")),
            "version": data.get("version"),
            "deleted": data.get("deleted"),
            "originOrgId": data.get("origin_org_id"),
            "createdBy": {"id": data.get("created_by")} if data.get("created_by") else None,
            "updatedBy": {"id": data.get("updated_by")} if data.get("updated_by") else None,
        }
        
        if include_id and data.get("id"):
            common_fields["id"] = data["id"]
            
        return common_fields

    def create_org(self, org_type: str = "COM") -> Dict[str, Any]:
        """创建组织"""
        if org_type == "COM":
            pattern = "AUTOTEST_COM_ORG%"
        elif org_type == "PUR":
            pattern = "AUTOTEST_PUR_ORG%"
        elif org_type == "SAL":
            pattern = "AUTOTEST_SAL_ORG%"
        else:
            pattern = "AUTOTEST_%"
            
        org = self.query_single_record(
            "org_struct_md", 
            "org_code LIKE %s AND deleted = 0", 
            [pattern],
            f"{org_type}组织数据"
        )
        
        # 构建组织特有字段
        org_fields = {
            "orgCode": org["org_code"],
            "orgName": org["org_name"],
            "orgType": org.get("org_type"),
            "status": org.get("status", org.get("org_status", "ACTIVE")),  # 兼容不同的状态字段名
            "parentOrgId": {"id": org.get("parent_org_id")} if org.get("parent_org_id") else None,
        }
        
        # 合并通用字段
        org_fields.update(self.build_common_fields(org, include_id=True))
        return org_fields

    def create_currency(self) -> Dict[str, Any]:
        """创建币种"""
        curr = self.query_single_record(
            "gen_curr_type_cf", 
            "curr_name = %s AND deleted = 0", 
            ['人民币'],
            "币种数据"
        )
        
        # 构建币种特有字段
        curr_fields = {
            "currCode": curr["curr_code"],
            "currName": curr["curr_name"],
            "currSymbol": curr.get("curr_symbol"),
            "status": curr.get("status", "ACTIVE"),
        }
        
        # 合并通用字段
        curr_fields.update(self.build_common_fields(curr, include_id=True))
        return curr_fields

    def create_tax_code(self, tax_rate: int = 13) -> Dict[str, Any]:
        """创建税码"""
        tax = self.query_single_record(
            "gen_tax_type_cf", 
            "tax = %s AND deleted = 0", 
            [tax_rate],
            f"税率为{tax_rate}%的税码"
        )
        
        # 构建税码特有字段
        tax_fields = {
            "taxCode": tax["tax_code"],
            "taxName": tax.get("tax_name", tax.get("taxcate", "")),
            "tax": tax["tax"],
            "status": tax.get("status", "ACTIVE"),
        }
        
        # 合并通用字段
        tax_fields.update(self.build_common_fields(tax, include_id=True))
        return tax_fields

    def create_material(self) -> Dict[str, Any]:
        """创建物料"""
        mat = self.query_single_record(
            "gen_mat_md", 
            "mat_code LIKE %s AND deleted = 0", 
            ['AUTOTEST_MAT%'],
            "物料数据"
        )
        
        # 构建物料特有字段
        mat_fields = {
            "matCode": mat["mat_code"],
            "matName": mat["mat_name"],
            "matType": mat.get("mat_type"),
            "status": mat.get("status", "ACTIVE"),
            "basicUnitId": {"id": mat.get("basic_unit_id")} if mat.get("basic_unit_id") else None,
        }
        
        # 合并通用字段
        mat_fields.update(self.build_common_fields(mat, include_id=True))
        return mat_fields

    def create_vendor(self) -> Dict[str, Any]:
        """创建供应商"""
        vend = self.query_single_record(
            "gen_vend_info_md", 
            "vend_code LIKE %s AND deleted = 0", 
            ['AUTOTEST_VEND%'],
            "供应商数据"
        )
        
        # 构建供应商特有字段
        vend_fields = {
            "vendCode": vend["vend_code"],
            "name": vend.get("name", vend.get("vend_name", "")),
            "status": vend.get("status", "ACTIVE"),
            "vendCateType": vend.get("vend_cate_type"),
            "vendType": {"id": vend.get("vend_type_id")},
            "com": {"id": vend.get("com_id")},
            "vendCateId": vend.get("vend_cate_id"),
            "vendPersonLink": vend.get("vend_person_link"),
        }
        
        # 合并通用字段
        vend_fields.update(self.build_common_fields(vend, include_id=True))
        return vend_fields

    def create_customer(self) -> Dict[str, Any]:
        """创建客户"""
        cust = self.query_single_record(
            "gen_cust_info_md", 
            "cust_code LIKE %s AND deleted = 0", 
            ['AUTOTEST_CUST%'],
            "客户数据"
        )
        
        # 构建客户特有字段
        cust_fields = {
            "custCode": cust["cust_code"],
            "name": cust.get("name", cust.get("cust_name", "")),
            "status": cust.get("status", "ACTIVE"),
            "custCateType": cust.get("cust_cate_type"),
            "custType": {"id": cust.get("cust_type_id")},
            "com": {"id": cust.get("com_id")},
            "custCateId": cust.get("cust_cate_id"),
            "custPersonLink": cust.get("cust_person_link"),
        }
        
        # 合并通用字段
        cust_fields.update(self.build_common_fields(cust, include_id=True))
        return cust_fields

    def get_base_data_for_fin_doc(self, doc_type: str = "AP") -> Dict[str, Any]:
        """
        获取创建财务单据所需的基础数据
        :param doc_type: 单据类型 AP-应付单, AR-应收单
        :return: 基础数据字典
        """
        try:
            # 1. 获取公司组织
            com_org_sql = """
                SELECT * FROM org_struct_md 
                WHERE deleted = 0 
                AND org_code LIKE 'AUTOTEST_COM_ORG%'
                LIMIT 1
            """
            com_org = DBManager.query(com_org_sql)[0]
            
            # 2. 根据单据类型获取业务组织
            if doc_type == "AP":
                # 应付单需要采购组织
                bus_org_sql = """
                    SELECT * FROM org_struct_md 
                    WHERE deleted = 0 
                    AND org_code LIKE 'AUTOTEST_PUR_ORG%'
                    LIMIT 1
                """
            else:
                # 应收单需要销售组织
                bus_org_sql = """
                    SELECT * FROM org_struct_md 
                    WHERE deleted = 0 
                    AND org_code LIKE 'AUTOTEST_SAL_ORG%'
                    LIMIT 1
                """
            
            bus_org = DBManager.query(bus_org_sql)[0]
            
            # 3. 获取币种
            currency_sql = """
                SELECT * FROM gen_curr_type_cf 
                WHERE deleted = 0 
                AND curr_name = '人民币'
                LIMIT 1
            """
            currency = DBManager.query(currency_sql)[0]
            
            return {
                'com_org': com_org,
                'bus_org': bus_org,  # 业务组织（采购组织或销售组织）
                'pay_org': com_org,  # 使用公司组织作为付款/收款组织
                'currency': currency,
                'doc_type': doc_type
            }
        except Exception as e:
            Loggers.error(f"获取{doc_type}单据基础数据失败: {str(e)}")
            raise

    def create_fin_doc_schedule_base(self, amount: float = 1000.0, due_date: int = None) -> Dict[str, Any]:
        """
        创建财务单据付款计划的基础结构
        :param amount: 金额
        :param due_date: 到期日期时间戳
        :return: 付款计划基础数据
        """
        if due_date is None:
            due_date = int(datetime.now().timestamp() * 1000)
            
        return {
            "context": {},
            "dueDate": due_date,
            "docAmt": amount,
            "baseAmt": amount,
            "percent": 100,
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

    def get_latest_fin_doc_id_by_status(self, table_name: str, status_field: str, status: str) -> Optional[str]:
        """
        根据状态获取最新的财务单据ID
        :param table_name: 表名
        :param status_field: 状态字段名
        :param status: 状态值
        :return: 单据ID
        """
        sql = f'''
            SELECT id FROM {table_name}
            WHERE deleted = 0 AND {status_field} = %s
            ORDER BY updated_at DESC
            LIMIT 1
        '''
        try:
            result = DBManager.query(sql, [status])
            return str(result[0]["id"]) if result else None
        except Exception as e:
            Loggers.error(f"查询最新{table_name}单据ID失败: {str(e)}")
            return None

    def get_org_by_id(self, org_id: int) -> Dict[str, Any]:
        """
        根据ID获取组织信息
        :param org_id: 组织ID
        :return: 组织信息字典
        """
        try:
            org = self.query_single_record(
                "org_struct_md",
                "id = %s AND deleted = 0",
                [org_id],
                f"ID为{org_id}的组织"
            )
            return self.create_org_from_data(org)
        except Exception as e:
            Loggers.error(f"根据ID获取组织信息失败: {str(e)}")
            raise

    def create_org_from_data(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从数据库数据创建组织对象
        :param org_data: 数据库查询结果
        :return: 组织对象
        """
        org_fields = {
            "orgCode": org_data["org_code"],
            "orgName": org_data["org_name"],
            "orgType": org_data.get("org_type"),
            "status": org_data.get("status", org_data.get("org_status", "ACTIVE")),
            "parentOrgId": {"id": org_data.get("parent_org_id")} if org_data.get("parent_org_id") else None,
        }
        
        # 合并通用字段
        org_fields.update(self.build_common_fields(org_data, include_id=True))
        return org_fields 