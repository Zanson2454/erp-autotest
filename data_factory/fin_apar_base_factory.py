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
        构建通用字段，所有日期字段用时间戳（毫秒）
        """
        def to_timestamp(dt):
            if isinstance(dt, datetime):
                return int(dt.timestamp() * 1000)
            if isinstance(dt, str):
                try:
                    return int(datetime.strptime(dt[:19], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
                except:
                    return dt
            if isinstance(dt, int):
                return dt
            return None
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
            pattern = "AUTOTEST_SLS_ORG%"
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
        :param doc_type: 单据类型 AP-应付单, AR-应收单, PR-付款申请单
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
            com_org_raw = DBManager.query(com_org_sql)[0]
            
            # 2. 根据单据类型获取业务组织
            if doc_type in ["AP", "PR"]:
                # 应付单和付款申请单需要采购组织
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
                    AND org_code LIKE 'AUTOTEST_SLS_ORG%'
                    LIMIT 1
                """
            
            bus_org_raw = DBManager.query(bus_org_sql)[0]
            
            # 3. 获取币种
            currency_sql = """
                SELECT * FROM gen_curr_type_cf 
                WHERE deleted = 0 
                AND curr_name = '人民币'
                LIMIT 1
            """
            currency_raw = DBManager.query(currency_sql)[0]
            
            # 4. 获取供应商
            vend_sql = """
                SELECT * FROM gen_business_partner_md 
                WHERE deleted = 0 
                AND code LIKE 'AUTOTEST_VEND%'
                AND status = 'ENABLED'
                LIMIT 1
            """
            vend_raw = DBManager.query(vend_sql)[0]
            
            # 构建完整的组织对象结构
            com_org = self._build_complete_org_structure(com_org_raw)
            pur_org = self._build_complete_org_structure(bus_org_raw)
            
            # 构建完整的币种对象
            currency = {
                "currName": currency_raw["curr_name"],
                "currCode": currency_raw["curr_code"],
                "id": currency_raw["id"]
            }
            
            # 构建完整的供应商对象
            vend = self._build_complete_vendor_structure(vend_raw)
            
            # 5. 获取结算方式
            settlement_method_sql = """
                SELECT * FROM fin_sett_type_cf 
                WHERE deleted = 0 
                AND status = 'ENABLED'
                AND type = 'CASH'
                LIMIT 1
            """
            settlement_method_raw = DBManager.query(settlement_method_sql)[0]
            settlement_method = {
                "id": settlement_method_raw["id"],
                "code": settlement_method_raw["code"],
                "name": settlement_method_raw["name"],
                "type": settlement_method_raw["type"],
                "status": settlement_method_raw["status"]
            }
            
            return {
                'com_org': com_org,
                'pur_org': pur_org,  # 采购组织
                'pay_org': com_org,  # 使用公司组织作为付款组织
                'currency': currency,
                'vend': vend,
                'settlement_method': settlement_method,
                'doc_type': doc_type
            }
        except Exception as e:
            Loggers.error(f"获取{doc_type}单据基础数据失败: {str(e)}")
            raise

    def _build_complete_org_structure(self, org_raw: Dict[str, Any]) -> Dict[str, Any]:
        """构建完整的组织对象结构，匹配实际API入参格式"""
        return {
            "orgCode": org_raw["org_code"],
            "orgName": org_raw["org_name"],
            "orgEnableDate": int(datetime.now().timestamp() * 1000),
            "orgStatus": "ENABLED",
            "isLeaf": org_raw.get("is_leaf", False),
            "def1": org_raw.get("def1"),
            "def2": org_raw.get("def2"),
            "def3": org_raw.get("def3"),
            "def4": org_raw.get("def4"),
            "def5": org_raw.get("def5"),
            "def6": org_raw.get("def6"),
            "def7": org_raw.get("def7"),
            "def8": org_raw.get("def8"),
            "def9": org_raw.get("def9"),
            "def10": org_raw.get("def10"),
            "def11": org_raw.get("def11"),
            "def12": org_raw.get("def12"),
            "def13": org_raw.get("def13"),
            "def14": org_raw.get("def14"),
            "def15": org_raw.get("def15"),
            "def16": org_raw.get("def16"),
            "def17": org_raw.get("def17"),
            "def18": org_raw.get("def18"),
            "def19": org_raw.get("def19"),
            "def20": org_raw.get("def20"),
            "def21": org_raw.get("def21"),
            "def22": org_raw.get("def22"),
            "def23": org_raw.get("def23"),
            "def24": org_raw.get("def24"),
            "def25": org_raw.get("def25"),
            "def26": org_raw.get("def26"),
            "def27": org_raw.get("def27"),
            "def28": org_raw.get("def28"),
            "def29": org_raw.get("def29"),
            "def30": org_raw.get("def30"),
            "def31": org_raw.get("def31"),
            "def32": org_raw.get("def32"),
            "def33": org_raw.get("def33"),
            "def34": org_raw.get("def34"),
            "def35": org_raw.get("def35"),
            "def36": org_raw.get("def36"),
            "def37": org_raw.get("def37"),
            "def38": org_raw.get("def38"),
            "def39": org_raw.get("def39"),
            "def40": org_raw.get("def40"),
            "orgDimensionCode": org_raw.get("org_dimension_code", "SCM_ORG_GRP"),
            "attachment1": [],
            "attachment2": [],
            "orgSort": org_raw.get("org_sort", 1),
            "orgBusinessTypeCode": org_raw.get("org_business_type_code"),
            "orgBusinessTypeId": {"id": org_raw.get("org_business_type_id")} if org_raw.get("org_business_type_id") else None,
            "orgDimensionId": {"id": org_raw.get("org_dimension_id")} if org_raw.get("org_dimension_id") else None,
            "orgParentId": {"id": org_raw.get("org_parent_id")} if org_raw.get("org_parent_id") else None,
            "partnerId": org_raw.get("partner_id"),
            "comOrgId": {"id": org_raw.get("com_org_id")} if org_raw.get("com_org_id") else None,
            "orgBusinessTypeIds": org_raw.get("org_business_type_ids"),
            "orgBusinessTypeCodes": org_raw.get("org_business_type_codes"),
            "path": org_raw.get("path"),
            "id": org_raw["id"],
            "createdBy": {"id": org_raw.get("created_by")} if org_raw.get("created_by") else None,
            "updatedBy": {"id": org_raw.get("updated_by")} if org_raw.get("updated_by") else None,
            "createdAt": int(datetime.fromisoformat(str(org_raw.get("created_at", datetime.now()))).timestamp() * 1000) if org_raw.get("created_at") else int(datetime.now().timestamp() * 1000),
            "updatedAt": int(datetime.fromisoformat(str(org_raw.get("updated_at", datetime.now()))).timestamp() * 1000) if org_raw.get("updated_at") else int(datetime.now().timestamp() * 1000),
            "version": org_raw.get("version", 1),
            "deleted": org_raw.get("deleted", 0),
            "originOrgId": org_raw.get("origin_org_id", 0)
        }

    def _build_complete_vendor_structure(self, vend_raw: Dict[str, Any]) -> Dict[str, Any]:
        """构建完整的供应商对象结构，匹配实际API入参格式"""
        return {
            "id": vend_raw["id"],
            "context": {},
            "version": vend_raw.get("version", 1),
            "deleted": vend_raw.get("deleted", 0),
            "createdAt": int(datetime.fromisoformat(str(vend_raw.get("created_at", datetime.now()))).timestamp() * 1000) if vend_raw.get("created_at") else int(datetime.now().timestamp() * 1000),
            "updatedAt": int(datetime.fromisoformat(str(vend_raw.get("updated_at", datetime.now()))).timestamp() * 1000) if vend_raw.get("updated_at") else int(datetime.now().timestamp() * 1000),
            "createdBy": vend_raw.get("created_by"),
            "updatedBy": vend_raw.get("updated_by"),
            "code": vend_raw["code"],
            "status": vend_raw.get("status", "ENABLED"),
            "name": vend_raw["name"],
            "partnerIdentity": ["SUPPLIER"],
            "partnerTypeId": {
                "id": vend_raw.get("partner_type_id", 2001001),
                "context": {},
                "version": 7,
                "deleted": 0,
                "createdAt": 1713247472000,
                "updatedAt": 1742799310000,
                "createdBy": 100010583,
                "updatedBy": 540175374525637,
                "code": "01",
                "name": "集团内合作伙伴-国内",
                "classType": "COMPANY",
                "isInternal": True,
                "isAddrRequired": False,
                "isBankRequired": False,
                "status": "DISABLED",
                "isOverseasPartner": False,
                "isNeedMaintainService": False,
                "role": "SUPPLIER"
            },
            "comCorporation": vend_raw.get("com_corporation", "崔月"),
            "bizLicenseNo": vend_raw.get("biz_license_no", "91441900MA56J2K400"),
            "enterpriseType": "VENDOR",
            "registeredCapital": vend_raw.get("registered_capital", "1000"),
            "socialCreditCode": vend_raw.get("social_credit_code", "91441900MA56J2K400"),
            "taxpayersNum": vend_raw.get("taxpayers_num", "91441900MA56J2K400"),
            "bizScope": vend_raw.get("biz_scope", "采购代理服务；政府采购代理服务；集贸市场管理服务；供应链管理服务"),
            "intro": vend_raw.get("intro", "自动化测试供应商"),
            "addressDetail": vend_raw.get("address_detail", "广东省东莞市"),
            "classType": "COMPANY",
            "isInternal": True
        }

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