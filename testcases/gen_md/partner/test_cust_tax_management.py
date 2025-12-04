import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("合作伙伴管理")
@allure.feature("客户税分类管理")
class TestCustomerTaxManagement(GenMdBaseTest):
    """客户税分类管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("客户税分类管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_cust_tax_type_cf", 
                where="tax_class_code like %s", 
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="客户税分类管理",
        title="测试新增客户税分类",
        description="验证新增客户税分类功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["客户税分类管理", "新增", "GEN_CUST_TAX_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_customer_tax_type(self):
        """新增客户税分类用例"""
        try:
            # 准备客户税分类数据  
            cust_tax_code = self.mock_util.generate_unique_code(tag="CustTax")
            
            # 获取初始化数据中的国家信息
            country_info = self.init_data.get("country_info")
            coun_id = country_info[0].get("coun_id") if country_info else None
            
            set_dict = {
                "taxClassCode": cust_tax_code,
                "taxClassDesc": f"自动化测试客户税分类-{self.mock_util.get_timestamp()}",
                "counId": {"id": coun_id}
            }
            fields_to_filter = ["taxClassCode", "taxClassDesc", "counId"]

            response, extracted_id = self.standard_api_call(
                api_key="GEN-客户税分类-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 保存返回的ID用于后续测试
            self.cust_tax_id = response.get("data", {}).get("data", {})
            self.cust_tax_code = cust_tax_code
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="客户税分类管理",
        title="测试查询客户税分类分页",
        description="验证客户税分类分页查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["客户税分类管理", "查询", "GEN_CUST_TAX_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_customer_tax_type_page(self):
        """查询客户税分类分页用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "taxClassCode", "type": "TEXT"},
                    {"name": "taxClassDesc", "type": "TEXT"},
                    {"name": "counId", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            response, _ = self.standard_api_call(
                api_key="GEN-客户税分类-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据结构
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="客户税分类管理",
        title="测试查询客户税分类详情",
        description="验证客户税分类详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["客户税分类管理", "详情", "GEN_CUST_TAX_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_customer_tax_type_detail(self):
        """查询客户税分类详情用例"""
        try:
            # 如果没有ID，先创建一个
            if not hasattr(self, 'cust_tax_id') or not self.cust_tax_id:
                self.test_save_customer_tax_type()

            set_dict = {"id": self.cust_tax_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-客户税分类-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            # 验证返回的详情数据
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data, "not_empty")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="客户税分类管理",
        title="测试删除客户税分类",
        description="验证删除客户税分类功能",
        severity="normal",
        file_level_order=4,
        tags=["客户税分类管理", "删除", "GEN_CUST_TAX_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_customer_tax_type(self):
        """删除客户税分类用例"""
        try:
            # 如果没有ID，先创建一个
            if not hasattr(self, 'cust_tax_id') or not self.cust_tax_id:
                self.test_save_customer_tax_type()

            set_dict = {"id": self.cust_tax_id}
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="GEN-客户税分类-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise 

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="客户税分类管理",
        title="测试客户税分类标准导出",
        description="验证客户税分类标准导出功能",
        severity="normal",
        file_level_order=5,
        tags=["客户税分类", "导出"]
    )
    def test_export_customer_tax_type(self):
        """客户税分类标准导出用例"""
        try:
            api_path = self.get_api_path("客户税分类标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"客户税分类导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "客户税分类",
                    "format": "EXCEL"
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
        story="客户税分类管理",
        title="测试客户税分类标准导入",
        description="验证客户税分类标准导入功能",
        severity="normal",
        file_level_order=6,
        tags=["客户税分类", "导入"]
    )
    def test_import_customer_tax_type(self):
        """客户税分类标准导入用例"""
        try:
            api_path = self.get_api_path("客户税分类标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "importConfig": {
                    "fileName": f"客户税分类导入_{self.mock_util.get_timestamp()}",
                    "fileType": "EXCEL",
                    "sheetName": "客户税分类"
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

    @case_decorator(
        story="客户税分类管理",
        title="测试提交客户税分类导出任务",
        description="验证提交客户税分类导出任务功能",
        severity="normal",
        file_level_order=7,
        tags=["客户税分类", "导出任务"]
    )
    def test_submit_customer_tax_type_export_task(self):
        """提交客户税分类导出任务用例"""
        try:
            api_path = self.get_api_path("客户税分类-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] =  {
                "taskName": f"客户税分类-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "GEN_MD$gen_cust_tax_type_cf",
                        "modelName": "客户税分类",
                        "sheetNo": 0,
                        "sheetName": "客户税分类",
                        "headerConfigList": [
                            {
                                "name": "客户税分类编码",
                                "type": "TEXT",
                                "field": "taxClassCode"
                            },
                            {
                                "name": "国家",
                                "type": "TEXT",
                                "field": "counId.counName"
                            },
                            {
                                "name": "客户分类描述",
                                "type": "TEXT",
                                "field": "taxClassDesc"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW-table-container-GEN_MD$gen_cust_tax_type_cf",
                    "viewKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
        
                            }
                        },
                        "selectFields": [
                            {
                                "field": "taxClassCode"
                            },
                            {
                                "field": "taxClassDesc"
                            },
                            {
                                "field": "counId",
                                "selectFields": [
                                    {
                                        "field": "counName"
                                    }
                                ]
                            }
                        ],
                        "modelKey": "GEN_MD$gen_cust_tax_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "GEN_MD$gen_cust_tax_type_cf",
                    "modelName": "客户税分类",
                    "containerKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW-table-container-GEN_MD$gen_cust_tax_type_cf",
                    "viewKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW:list",
                    "sceneKey": "GEN_MD$GEN_CUST_TAX_TYPE_VIEW"
                }
            }
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="客户税分类管理",
        title="测试通过OSS提交客户税分类导入任务",
        description="验证通过OSS提交客户税分类导入任务功能",
        severity="normal",
        file_level_order=8,
        tags=["客户税分类", "OSS导入"]
    )
    def test_submit_customer_tax_type_import_task_by_oss(self):
        """通过OSS提交客户税分类导入任务用例"""
        try:
            api_path = self.get_api_path("客户税分类-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"客户税分类OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"customer_tax_type_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "客户税分类"
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