import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴主数据")
class TestBusinessPartnerManagement(GenMdBaseTest):
    """合作伙伴主数据管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.partner_code = None
        cls.logger.info("合作伙伴主数据管理测试类初始化完成")

        # 检查 md_cache_data 是否存在
        if not cls.md_cache_data:
            cls.logger.error("md_cache_data 为 None，无法初始化合作伙伴类型等信息")
            raise ValueError("md_cache_data 为 None，请检查主数据初始化SQL配置和数据库连接")

        # 合作伙伴类型
        partner_info = cls.md_cache_data.get("partner_info", {})
        cls.business_partner_type_cf = partner_info.get("business_partner_type_cf", {})
        if cls.business_partner_type_cf:
            cls.out_cust_type_id = cls.business_partner_type_cf.get("out_cust", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("out_cust") else None
            cls.inter_cust_type_id = cls.business_partner_type_cf.get("inter_cust", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("inter_cust") else None
            cls.person_cust_type_id = cls.business_partner_type_cf.get("person_cust", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("person_cust") else None
            cls.out_supplier_type_id = cls.business_partner_type_cf.get("out_supplier", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("out_supplier") else None
            cls.outsea_supplier_type_id = cls.business_partner_type_cf.get("outsea_supplier", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("outsea_supplier") else None
            cls.inter_supplier_type_id = cls.business_partner_type_cf.get("inter_supplier", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("inter_supplier") else None
            cls.serv_supplier_type_id = cls.business_partner_type_cf.get("serv_supplier", [{}])[0].get("id", None) if cls.business_partner_type_cf.get("serv_supplier") else None
        else:
            cls.logger.warning("business_partner_type_cf not found in md_cache_data")
        
        # 相关方信息 - 从partner_info下获取
        partner_type_cf = partner_info.get("partner_type_cf", {})
        if partner_type_cf:
            sls_partner_type = partner_type_cf.get("sls_partner_type", [])
            cls.sls_partner_type_id = sls_partner_type[0].get("id", None) if sls_partner_type else None  # 销售相关方类型
            pur_partner_type = partner_type_cf.get("pur_partner_type", [])
            cls.pur_partner_type_id = pur_partner_type[0].get("id", None) if pur_partner_type else None # 采购相关方类型
        else:
            cls.logger.warning("partner_type_cf not found in md_cache_data")
        
        # 组织信息
        org_info = cls.md_cache_data.get("org_info", {})
        if org_info:
            sls_org_info = org_info.get("sls_org_info", [])
            cls.sls_org_id = sls_org_info[0].get("id", None) if sls_org_info else None  # 销售组织作为相关方
            pur_org_info = org_info.get("pur_org_info", [])
            cls.pur_org_id = pur_org_info[0].get("id", None) if pur_org_info else None  # 采购组织作为相关方
        else:
            cls.logger.warning("org_info not found in md_cache_data")
        
        # 文本类型 - 从partner_info下获取
        text_type_cf = partner_info.get("text_type_cf", {})
        if text_type_cf:
            sls_text_type = text_type_cf.get("sls_text_type", [])
            cls.sls_text_type_id = sls_text_type[0].get("id", None) if sls_text_type else None
            pur_text_type = text_type_cf.get("pur_text_type", [])
            cls.pur_text_type_id = pur_text_type[0].get("id", None) if pur_text_type else None
        else:
            cls.logger.warning("text_type_cf not found in md_cache_data")
        
        # 类目信息 - 从mat_info下获取，注意是列表结构
        mat_info = cls.md_cache_data.get("mat_info", {})
        if mat_info:
            mat_cate_md = mat_info.get("mat_cate_md", [])
            cls.mat_cate_id = mat_cate_md[0].get("id", None) if mat_cate_md else None
        else:
            cls.logger.warning("mat_info not found in md_cache_data")
        
        # 用户及员工信息 - 从org_info下获取
        if org_info:
            employee_info = org_info.get("employee_info", [])
            cls.employee_id = employee_info[0].get("id", None) if employee_info else None
        else:
            cls.logger.warning("employee_info not found in org_info")
    
        # 基础数据 - 从init_cache获取（安全访问）
        if cls.init_data:
            country_info = cls.init_data.get("country_info", [])
            cls.coun_id = country_info[0].get("coun_id", None) if country_info else None
            
            addr_info = cls.init_data.get("addr_info", [])
            cls.addr_id = addr_info[0].get("id", None) if addr_info else None
            
            bank_info = cls.init_data.get("bank_info", [])
            if bank_info:
                cls.bank_id = bank_info[0].get("bank_id", None)
                cls.sub_bank_id = bank_info[0].get("sub_bank_id", None)
            else:
                cls.bank_id = None
                cls.sub_bank_id = None
        else:
            cls.coun_id = None
            cls.addr_id = None
            cls.bank_id = None
            cls.sub_bank_id = None
            cls.logger.warning("init_data 为 None，基础数据 ID 设置为 None")
        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_business_partner_md", 
                where="code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ============= 核心功能测试 =============
    @case_decorator(
        story="合作伙伴主数据",
        title="测试新增外部客户",
        description="验证新增合作伙伴功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["合作伙伴", "新增"]
    )
    def test_save_business_partner(self):
        """新增合作伙伴用例"""
        try:
            code = self.mock_util.generate_unique_code(tag="OUT_CUST")
            bizLicenseNo = self.mock_util.get_mock_enterprise_credentials()

            # 调用保存接口
            set_dict = {
                "partnerIdentity":["CUSTOMER"], #客户
                "partnerTypeId": {"id":self.out_cust_type_id},
                "classType": "COMPANY",
                "code": code,
                "name": self.mock_util.get_mock_company(),
                "outerCode": f"outcode{self.mock_util.get_timestamp()}",
                "contactNum": str(self.mock_util.get_mock_phone_number()),
                "comCorporation": self.mock_util.get_mock_name(),
                "bizLicenseNo": bizLicenseNo,
                "socialCreditCode": bizLicenseNo,
                "taxpayersNum": bizLicenseNo,
                "enterpriseType": "EXTERNAL",
                "registeredCapital": 100,
                "counId": {"id": self.coun_id},
                "addressId": {"id": self.addr_id},
                "addressDetail": "自动化测试详细地址",
                "bizScope": self.mock_util.get_mock_business_scope(),
                "intro": self.mock_util.get_mock_company_intro(),
                "addrList": [
                    {
                        "addrDetail": "自动化测试地址",
                        "addrId": {"id": self.addr_id},
                        "addrUsage":"REC_ADDR",
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "bankList": [
                    {
                        "accountName": self.mock_util.get_mock_bank_info()['bank_name'],
                        "bankAccount": self.mock_util.get_mock_bank_info()['account_number'],
                        "isDefault": True,
                        "usage": "PAYMENT",
                        "bankId": {"id": self.bank_id},
                        "subBankId": {"id": self.sub_bank_id},   
                    }
                ],
                "attachmentList": [],
                "textList": [{
                    "textType": {"id": self.sls_text_type_id},
                    "textContent": f"自动化测试文本_{self.mock_util.get_timestamp()}"
                }],
                "qualificationsList": [],
                "contactList": [
                    {
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "userList": [
                    {
                        "employeeId": {"id": self.employee_id},
                        "isManager": True,
                    }
                ],
                "partiesList": [
                    {
                        "prtnTypeId": {"id": self.sls_partner_type_id},
                        "prtnId": {"id": self.sls_org_id}
                    }
                ],
                "cateList": [
                    {
                        "matCateId": {"id": self.mat_cate_id}
                    }
                ]
            }
            fields_to_filter = ["code","name","addrList", "addressDetail", "addressId", "attachmentList", "bankList","textList","userList","contactList","contactNum","counId","enterpriseType",
                             "cateList","bizLicenseNo","socialCreditCode","taxpayersNum","bizScope","classType","comCorporation","intro","outerCode","partiesList","partnerIdentity","partnerTypeId","qualificationsList",
                             "registeredCapital",]

            # 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="partner"
            )
            
            self.assert_util.assert_response_data(response)
            
            self.partner_id = extracted_id
            self.partner_code = code
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="合作伙伴主数据",
        title="测试新增内部客户",
        description="验证新增合作伙伴功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["合作伙伴", "新增"]
    )
    def test_save_inner_cust(self):
        """新增合作伙伴用例"""
        try:
            code = self.mock_util.generate_unique_code(tag="INNER_CUST")
            bizLicenseNo = self.mock_util.get_mock_enterprise_credentials()

            # 调用保存接口
            set_dict = {
                "partnerIdentity":["CUSTOMER"], #客户
                "partnerTypeId": {"id":self.inter_cust_type_id},
                "classType": "COMPANY",
                "code": code,
                "name": self.mock_util.get_mock_company(),
                "outerCode": f"outcode{self.mock_util.get_timestamp()}",
                "contactNum": str(self.mock_util.get_mock_phone_number()),
                "comCorporation": self.mock_util.get_mock_name(),
                "bizLicenseNo": bizLicenseNo,
                "socialCreditCode": bizLicenseNo,
                "taxpayersNum": bizLicenseNo,
                "enterpriseType": "INTERNAL",
                "registeredCapital": 100,
                "counId": {"id": self.coun_id},
                "addressId": {"id": self.addr_id},
                "addressDetail": "自动化测试详细地址",
                "bizScope": self.mock_util.get_mock_business_scope(),
                "intro": self.mock_util.get_mock_company_intro(),
                "addrList": [
                    {
                        "addrDetail": "自动化测试地址",
                        "addrId": {"id": self.addr_id},
                        "addrUsage":"REC_ADDR",
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "bankList": [
                    {
                        "accountName": self.mock_util.get_mock_bank_info()['bank_name'],
                        "bankAccount": self.mock_util.get_mock_bank_info()['account_number'],
                        "isDefault": True,
                        "usage": "PAYMENT",
                        "bankId": {"id": self.bank_id},
                        "subBankId": {"id": self.sub_bank_id},   
                    }
                ],
                "attachmentList": [],
                "textList": [{
                    "textType": {"id": self.sls_text_type_id},
                    "textContent": f"自动化测试文本_{self.mock_util.get_timestamp()}"
                }],
                "qualificationsList": [],
                "contactList": [
                    {
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "userList": [
                    {
                        "employeeId": {"id": self.employee_id},
                        "isManager": True,
                    }
                ],
                "partiesList": [
                    {
                        "prtnTypeId": {"id": self.sls_partner_type_id},
                        "prtnId": {"id": self.sls_org_id}
                    }
                ],
                "cateList": [
                    {
                        "matCateId": {"id": self.mat_cate_id}
                    }
                ]
            }
            fields_to_filter = ["code","name","addrList", "addressDetail", "addressId", "attachmentList", "bankList","textList","userList","contactList","contactNum","counId","enterpriseType",
                             "cateList","bizLicenseNo","socialCreditCode","taxpayersNum","bizScope","classType","comCorporation","intro","outerCode","partiesList","partnerIdentity","partnerTypeId","qualificationsList",
                             "registeredCapital",]

            # 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="partner"
            )
            
            self.assert_util.assert_response_data(response)
            
            self.partner_id = extracted_id
            self.partner_code = code
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="合作伙伴主数据",
        title="测试新增个人客户",
        description="验证新增合作伙伴功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["合作伙伴", "新增"]
    )
    def test_save_person_cust(self):
        """新增合作伙伴用例"""
        try:
            code = self.mock_util.generate_unique_code(tag="PERSON_CUST")
            name = self.mock_util.get_mock_name()

            # 调用保存接口
            set_dict = {
                "partnerIdentity":["CUSTOMER"], #客户
                "partnerTypeId": {"id":self.person_cust_type_id},
                "classType": "PERSON",
                "code": code,
                "name": name,
                "personName": name,
                "idCard": self.mock_util.get_mock_ssn(),
                "outerCode": f"outcode{self.mock_util.get_timestamp()}",
                "contactNum": str(self.mock_util.get_mock_phone_number()),
                "addressId": {"id": self.addr_id},
                "addressDetail": "自动化测试详细地址",
                "addrList": [
                    {
                        "addrDetail": "自动化测试地址",
                        "addrId": {"id": self.addr_id},
                        "addrUsage":"REC_ADDR",
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "bankList": [],
                "attachmentList": [],
                "textList": [],
                "qualificationsList": [],
                "contactList": [
                    {
                        "contactName": self.mock_util.get_mock_name(),
                        "contactPhone": self.mock_util.get_mock_phone_number(),
                        "isDefault": True,
                    }
                ],
                "userList": [],
                "partiesList": [],
                "cateList": [
                    {
                        "matCateId": {"id": self.mat_cate_id}
                    }
                ]
            }
            fields_to_filter = ["code","name","personName","idCard","addrList", "addressDetail", "addressId", "attachmentList", "bankList","textList","userList","contactList","contactNum","counId","enterpriseType",
                             "cateList","outerCode","partiesList","partnerIdentity","partnerTypeId","qualificationsList"]

            # 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="partner"
            )
            
            self.assert_util.assert_response_data(response)
            
            self.partner_id = extracted_id
            self.partner_code = code
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="合作伙伴主数据",
        title="测试查询合作伙伴分页",
        description="验证合作伙伴分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["合作伙伴", "查询"]
    )
    def test_query_business_partner_page(self):
        """查询合作伙伴分页用例"""
        try:
            # 调用查询接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "partnerCode", "type": "TEXT"},
                    {"name": "partnerName", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-合作伙伴-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试查询合作伙伴详情",
        description="验证合作伙伴详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["合作伙伴", "详情"]
    )
    def test_query_business_partner_detail(self):
        """查询合作伙伴详情用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            # 调用详情查询接口
            set_dict = {"id": self.partner_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-合作伙伴-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试根据ID查找合作伙伴数据",
        description="验证根据ID查找合作伙伴数据功能",
        severity="normal",
        file_level_order=4,
        tags=["合作伙伴", "查找"]
    )
    def test_find_business_partner_by_id(self):
        """根据ID查找合作伙伴数据用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            # 调用接口
            set_dict = {"id": self.partner_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="合作伙伴-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试合作伙伴分页数据服务",
        description="验证合作伙伴分页数据服务功能",
        severity="normal",
        file_level_order=5,
        tags=["合作伙伴", "分页数据"]
    )
    def test_business_partner_paging_data(self):
        """合作伙伴分页数据服务用例"""
        try:
            # 调用接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "queryCondition": {}
            }
            fields_to_filter = ["pageable", "queryCondition"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="合作伙伴-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试启用合作伙伴",
        description="验证启用合作伙伴功能",
        severity="normal",
        file_level_order=6,
        tags=["合作伙伴", "启用"]
    )
    def test_enable_business_partner(self):
        """启用合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            # 调用接口
            set_dict = {"id": self.partner_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-合作伙伴-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试禁用合作伙伴",
        description="验证禁用合作伙伴功能",
        severity="normal",
        file_level_order=7,
        tags=["合作伙伴", "禁用"]
    )
    def test_disable_business_partner(self):
        """禁用合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            # 调用接口
            set_dict = {"id": self.partner_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-合作伙伴-禁用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试提交合作伙伴导出任务",
        description="验证提交合作伙伴导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["合作伙伴", "导出任务"]
    )
    def test_submit_business_partner_export_task(self):
        """提交合作伙伴导出任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params['params'] =  {
                "taskName": f"合作伙伴-章昂-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_business_partner_md",
                        "modelName": "合作伙伴",
                        "sheetNo": 0,
                        "sheetName": "合作伙伴",
                        "headerConfigList": [
                            {
                                "name": "伙伴编码",
                                "type": "TEXT",
                                "field": "code"
                            },
                            {
                                "name": "伙伴名称",
                                "type": "TEXT",
                                "field": "name"
                            },
                            {
                                "name": "伙伴身份",
                                "type": "ENUM",
                                "field": "partnerIdentity",
                                "multiSelect": True,
                                "dictValues": [
                                    {
                                        "_row_id_": "SUPPLIER",
                                        "label": "供应商",
                                        "value": "SUPPLIER"
                                    },
                                    {
                                        "_row_id_": "CUSTOMER",
                                        "label": "客户",
                                        "value": "CUSTOMER"
                                    }
                                ]
                            },
                            {
                                "name": "伙伴类型",
                                "type": "TEXT",
                                "field": "partnerTypeId.name"
                            },
                            {
                                "name": "状态",
                                "type": "ENUM",
                                "field": "status",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "未启用",
                                        "label": "未启用",
                                        "value": "INACTIVE"
                                    },
                                    {
                                        "_row_id_": "已启用",
                                        "label": "已启用",
                                        "value": "ENABLED"
                                    },
                                    {
                                        "_row_id_": "已停用",
                                        "label": "已停用",
                                        "value": "DISABLED"
                                    }
                                ]
                            },
                            {
                                "name": "更新时间",
                                "type": "DATE",
                                "field": "updatedAt"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW-table-container-GEN_MD$gen_business_partner_md",
                    "viewKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
        
                            }
                        },
                        "selectFields": [
                            {
                                "field": "code"
                            },
                            {
                                "field": "name"
                            },
                            {
                                "field": "partnerIdentity"
                            },
                            {
                                "field": "status"
                            },
                            {
                                "field": "updatedAt"
                            },
                            {
                                "field": "partnerTypeId",
                                "selectFields": [
                                    {
                                        "field": "name"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "GEN_MD$gen_business_partner_md"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_business_partner_md",
                    "modelName": "合作伙伴",
                    "containerKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW-table-container-GEN_MD$gen_business_partner_md",
                    "viewKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW"
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="合作伙伴主数据",
        title="测试删除合作伙伴",
        description="验证删除合作伙伴功能",
        severity="normal",
        file_level_order=9,
        tags=["合作伙伴", "删除"]
    )
    def test_delete_business_partner(self):
        """删除合作伙伴用例"""
        try:
            if not self.partner_id:
                self.test_save_business_partner()

            # 调用删除接口
            set_dict = {"id": self.partner_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-合作伙伴-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ============= 跳过的测试用例 =============
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="合作伙伴主数据",
        title="测试合作伙伴标准导出",
        description="验证合作伙伴标准导出功能",
        severity="normal",
        file_level_order=10,
        tags=["合作伙伴", "导出"]
    )
    def test_export_business_partner(self):
        """合作伙伴标准导出用例"""
        try:
            api_path = self.get_api_path("合作伙伴标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"合作伙伴导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "合作伙伴"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="合作伙伴主数据",
        title="测试合作伙伴标准导入",
        description="验证合作伙伴标准导入功能",
        severity="normal",
        file_level_order=11,
        tags=["合作伙伴", "导入"]
    )
    def test_import_business_partner(self):
        """合作伙伴标准导入用例"""
        try:
            api_path = self.get_api_path("合作伙伴标准导入服务")
            params,  url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"合作伙伴导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="合作伙伴主数据",
        title="测试通过OSS提交合作伙伴导入任务",
        description="验证通过OSS提交合作伙伴导入任务功能",
        severity="normal",
        file_level_order=12,
        tags=["合作伙伴", "OSS导入"]
    )
    def test_submit_business_partner_import_task_by_oss(self):
        """通过OSS提交合作伙伴导入任务用例"""
        try:
            api_path = self.get_api_path("合作伙伴-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"合作伙伴OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"partner_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "合作伙伴"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 

    # ============= 跳过的特殊功能测试用例 =============
    @pytest.mark.skip(reason="评分查询模板信息接口业务功能暂未明确，跳过测试")
    @case_decorator(
        story="合作伙伴主数据",
        title="测试评分查询模板信息",
        description="验证评分查询模板信息功能",
        severity="normal",
        file_level_order=13,
        tags=["合作伙伴", "评分模板"]
    )
    def test_survey_query_template(self):
        """评分查询模板信息用例"""
        try:
            api_path = self.get_api_path("GEN-评分查询模板信息")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["templateId", "templateType"],
                ["params", "request"]
            )
            set_dict = {
                "templateId": 1,
                "templateType": "SURVEY_TEMPLATE"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise