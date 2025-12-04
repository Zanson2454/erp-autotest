import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织关联管理")
class TestOrg_RelationManagement(GenMdBaseTest):
    """组织关联管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.org_relation_id = None
        cls.org_relation_code = None
        cls.export_task_id = None
        cls.import_task_id = None
        cls.logger.info("组织关联管理测试类初始化完成")
        
        # 获取组织维度管理ID
        cls.org_head_dimension_id = cls.md_cache_data.get("org_info",{}).get("org_dimension_cf",[])[0].get("id",None)
        cls.org_head_unit_id = cls.md_cache_data.get("org_info",{}).get("com_org_info",[])[0].get("id",None)
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        # 查询条件
        cls.query_condition = f"org_head_dimension_id = {cls.org_head_dimension_id} and org_head_unit_id = {cls.org_head_unit_id} and org_relation_dimension_id = {cls.org_head_dimension_id} and org_relation_unit_id = {cls.org_head_unit_id}"

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织关联管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_relation_cf",
                where=cls.query_condition
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织关联管理",
        title="测试新增组织关联管理",
        description="验证新增组织关联管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["组织关联管理", "新增"]
    )
    def test_save_org_relation(self):
        """
        新增组织关联管理用例
        """
        try:
            # 准备组织关联管理数据
            orgRelationEnabledTime = self.mock_util.get_timestamp(timestamp=True)
            orgRelationDisabledTime = self.mock_util.get_timestamp(timestamp=True,day_offset=30)
            # 调用保存接口前准备数据

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "orgHeadDimensionId": {"id":self.org_head_dimension_id},
                "orgHeadUnitId": {"id":self.org_head_unit_id},
                "orgRelationDimensionId": {"id":self.org_head_dimension_id},
                "orgRelationUnitId": {"id":self.org_head_unit_id},
                "orgRelationDisabledTime": orgRelationDisabledTime,
                "orgRelationEnabledTime": orgRelationEnabledTime,
                "orgRelationStatus": "ENABLED"
            }
            fields_to_filter = ["orgHeadDimensionId", "orgHeadUnitId","orgRelationDimensionId","orgRelationUnitId","orgRelationDisabledTime","orgRelationEnabledTime","orgRelationStatus"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织关联-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试查询组织关联管理列表",
        description="验证组织关联管理列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["组织关联管理", "查询"]
    )
    def test_query_org_relation_list(self):
        """
        查询组织关联管理列表用例
        """
        try:
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                  {
                    "name": "orgHeadDimensionId",
                    "type": "OBJECT"
                },
                {
                    "name": "orgHeadUnitId",
                    "type": "OBJECT"
                },
                {
                    "name": "orgRelationDimensionId",
                    "type": "OBJECT"
                },
                {
                    "name": "orgRelationUnitId",
                    "type": "OBJECT"
                },
                {
                    "name": "orgRelationEnabledTime",
                    "type": "DATE"
                }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-组织关联-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试查询组织关联管理详情",
        description="验证组织关联管理详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["组织关联管理", "查询"]
    )
    def test_query_org_relation_detail(self):
        """
        查询组织关联管理详情用例
        """
        try:
            # 获取组织关联管理信息（保持原有SQL逻辑）
            sql = f"select id from org_relation_cf where {self.query_condition}"
            result = self.db.query(sql)
            if not result or not result[0].get("id",None):
                self.test_save_org_relation()
                result = self.db.query(sql)
            self.org_relation_id = result[0].get("id",None)

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_relation_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="GEN-组织关联-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试启用组织关联",
        description="验证启用组织关联功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["组织关联管理", "启用"]
    )
    def test_enable_org_relation(self):
        """
        启用组织关联用例
        """
        try:
            # 获取组织关联管理ID（保持原有SQL逻辑）
            sql = f"select id,org_relation_status from org_relation_cf where {self.query_condition}"
            result = self.db.query(sql)
            if not result or not result[0].get("id",None):
                self.test_save_org_relation()
                result = self.db.query(sql)
            self.org_relation_id = result[0].get("id",None)
            # 调用启用接口前准备数据

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_relation_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织关联-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            
            sql = f"select org_relation_status from org_relation_cf where id = {self.org_relation_id}"
            org_relation_status = self.db.query(sql)[0].get("org_relation_status",None)
            self.assert_util.assert_by_operator(org_relation_status, "=", "ENABLED")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织关联管理",
        title="测试禁用组织关联",
        description="验证禁用组织关联功能",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["组织关联管理", "禁用"]
    )
    def test_disable_org_relation(self):
        """
        禁用组织关联用例
        """
        try:
            # 获取组织关联管理ID（保持原有SQL逻辑）
            sql = f"select id,org_relation_status from org_relation_cf where {self.query_condition}"
            result = self.db.query(sql)
            if not result or not result[0].get("id",None):
                self.test_enable_org_relation()
                result = self.db.query(sql)
            self.org_relation_id = result[0].get("id",None)

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_relation_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织关联-禁用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            
            sql = f"select org_relation_status from org_relation_cf where id = {self.org_relation_id}"
            org_relation_status = self.db.query(sql)[0].get("org_relation_status",None)
            self.assert_util.assert_by_operator(org_relation_status, "=", "DISABLED")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(
        reason="没有被引用"
    )
    @case_decorator(
        story="组织关联管理",
        title="测试组织关联标准导出",
        description="验证组织关联标准导出功能",
        severity="normal",
        file_level_order=6,
        smoke=True,
        tags=["组织关联管理", "标准导出"]
    )
    def test_standard_export_org_relation(self):
        """
        组织关联标准导出用例
        """
        try:
            # 调用标准导出接口
            api_path = self.get_api_path("组织关联关系表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            # 构建完整的导出参数
            self.logger.info(f"请求参数: {params}")
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise



 
    @case_decorator(
        story="组织关联管理",
        title="测试提交导出任务",
        description="验证提交组织关联导出任务功能",
        severity="normal",
        file_level_order=7,
        smoke=True,
        tags=["组织关联管理", "导出任务"]
    )
    @pytest.mark.skip(reason="业务不存在该场景，暂时跳过")
    def test_submit_export_task(self):
        """
        提交组织关联导出任务用例
        """
        try:
            # 调用提交导出任务接口
            api_path = self.get_api_path("组织关联关系表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            params = {
                "serviceKey": "GEN_MD$ORG_RELATION_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": "组织关联-章昂-20250714-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$org_relation_cf",
                            "modelName": "组织关联关系表",
                            "sheetNo": 0,
                            "sheetName": "组织关联关系表",
                            "headerConfigList": [
                                {
                                    "name": "源组织编码",
                                    "type": "TEXT",
                                    "field": "orgHeadUnitId.orgCode"
                                },
                                {
                                    "name": "源组织维度",
                                    "type": "TEXT",
                                    "field": "orgHeadDimensionId.orgDimensionName"
                                },
                                {
                                    "name": "源组织",
                                    "type": "TEXT",
                                    "field": "orgHeadUnitId.orgName"
                                },
                                {
                                    "name": "源组织状态",
                                    "type": "ENUM",
                                    "field": "orgHeadUnitId.orgStatus",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "DRAFT",
                                            "label": "草稿",
                                            "value": "DRAFT"
                                        },
                                        {
                                            "_row_id_": "ENABLED",
                                            "label": "已启用",
                                            "value": "ENABLED"
                                        },
                                        {
                                            "_row_id_": "UNENABLED",
                                            "label": "待启用",
                                            "value": "INACTIVE"
                                        },
                                        {
                                            "_row_id_": "DISABLED",
                                            "label": "已停用",
                                            "value": "DISABLED"
                                        }
                                    ]
                                },
                                {
                                    "name": "关联组织维度",
                                    "type": "TEXT",
                                    "field": "orgRelationDimensionId.orgDimensionName"
                                },
                                {
                                    "name": "关联组织",
                                    "type": "TEXT",
                                    "field": "orgRelationUnitId.orgName"
                                },
                                {
                                    "name": "关联组织编码",
                                    "type": "TEXT",
                                    "field": "orgRelationUnitId.orgCode"
                                },
                                {
                                    "name": "关联组织状态",
                                    "type": "ENUM",
                                    "field": "orgRelationUnitId.orgStatus",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "DRAFT",
                                            "label": "草稿",
                                            "value": "DRAFT"
                                        },
                                        {
                                            "_row_id_": "ENABLED",
                                            "label": "已启用",
                                            "value": "ENABLED"
                                        },
                                        {
                                            "_row_id_": "UNENABLED",
                                            "label": "待启用",
                                            "value": "INACTIVE"
                                        },
                                        {
                                            "_row_id_": "DISABLED",
                                            "label": "已停用",
                                            "value": "DISABLED"
                                        }
                                    ]
                                },
                                {
                                    "name": "生效时间",
                                    "type": "DATE",
                                    "field": "orgRelationEnabledTime"
                                },
                                {
                                    "name": "失效时间",
                                    "type": "DATE",
                                    "field": "orgRelationDisabledTime"
                                },
                                {
                                    "name": "状态",
                                    "type": "ENUM",
                                    "field": "orgRelationStatus",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "INACTIVE",
                                            "label": "未启用",
                                            "value": "INACTIVE"
                                        },
                                        {
                                            "_row_id_": "ENABLED",
                                            "label": "已启用",
                                            "value": "ENABLED"
                                        },
                                        {
                                            "_row_id_": "DISABLED",
                                            "label": "已停用",
                                            "value": "DISABLED"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "appId": 0,
                        "teamId": 22,
                        "containerKey": "GEN_MD$ORG_ORG_RELATION_VIEW-table-container-GEN_MD$org_relation_cf",
                        "viewKey": "GEN_MD$ORG_RELATION_VIEW:list",
                        "sceneKey": "GEN_MD$ORG_RELATION_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "orgRelationEnabledTime"
                                },
                                {
                                    "field": "orgRelationDisabledTime"
                                },
                                {
                                    "field": "orgRelationStatus"
                                },
                                {
                                    "field": "orgHeadUnitId",
                                    "selectFields": [
                                        {
                                            "field": "orgCode"
                                        },
                                        {
                                            "field": "orgName"
                                        },
                                        {
                                            "field": "orgStatus"
                                        }
                                    ]
                                },
                                {
                                    "field": "orgHeadDimensionId",
                                    "selectFields": [
                                        {
                                            "field": "orgDimensionName"
                                        }
                                    ]
                                },
                                {
                                    "field": "orgRelationDimensionId",
                                    "selectFields": [
                                        {
                                            "field": "orgDimensionName"
                                        }
                                    ]
                                },
                                {
                                    "field": "orgRelationUnitId",
                                    "selectFields": [
                                        {
                                            "field": "orgName"
                                        },
                                        {
                                            "field": "orgCode"
                                        },
                                        {
                                            "field": "orgStatus"
                                        }
                                    ]
                                }
                            ],
                            "modelKey": "GEN_MD$org_relation_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "appId": 0,
                        "teamId": 22,
                        "model": "GEN_MD$org_relation_cf",
                        "modelName": "组织关联关系表",
                        "containerKey": "GEN_MD$ORG_ORG_RELATION_VIEW-table-container-GEN_MD$org_relation_cf",
                        "viewKey": "GEN_MD$ORG_RELATION_VIEW:list",
                        "sceneKey": "GEN_MD$ORG_RELATION_VIEW"
                    }
                }
            }
            self.logger.info(f"请求参数: {params}")
            self.logger.info(f"请求头: {self.admin_headers}")
            response = self.http.post(url, headers=self.admin_headers,json=params)
            self.assert_util.assert_response_success(response)
            

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @pytest.mark.skip(
        reason="导入任务接口暂未开发"
    )
    @case_decorator(
        story="组织关联管理",
        title="测试标准导入",
        description="验证组织关联标准导入功能",
        severity="normal",
        file_level_order=8,
        smoke=True,
        tags=["组织关联管理", "标准导入"]
    )
    def test_standard_import_org_relation(self):
        """
        组织关联标准导入用例
        """
        try:
            # 调用标准导入接口
            api_path = self.get_api_path("组织关联关系表标准导入服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["importData", "importType"],
                ["params", "request"]
            )
            set_dict = {
                "importData": [
                    {
                        "org_relation_code": self.mock_util.generate_unique_code(tag="Import_Org_Relation"),
                        "org_relation_name": f"导入组织关联_{self.mock_util.get_timestamp()}"
                    }
                ],
                "importType": "STANDARD"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @pytest.mark.skip(
        reason="导入任务接口暂未开发"
    )
    @case_decorator(
        story="组织关联管理",
        title="测试通过OSS提交导入任务",
        description="验证通过OSS提交组织关联导入任务功能",
        severity="normal",
        file_level_order=9,
        smoke=True,
        tags=["组织关联管理", "OSS导入任务"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交组织关联导入任务用例
        """
        try:
            # 调用通过OSS提交导入任务接口
            api_path = self.get_api_path("组织关联关系表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ossFileUrl", "fileName", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "ossFileUrl": "test_oss_file_url",
                "fileName": f"组织关联导入_{self.nickname}_{self.mock_util.get_timestamp()}.xlsx",
                "importConfig": {
                    "importType": "EXCEL",
                    "skipFirstRow": True
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 保存导入任务ID供后续使用
            self.import_task_id = response.get("data", {}).get("data", {}).get("taskId")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

