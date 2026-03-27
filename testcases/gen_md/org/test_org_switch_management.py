import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织切换管理")
class TestOrg_SwitchManagement(GenMdBaseTest):
    """组织切换管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        cls.org_switch_id = None
        cls.org_switch_name = None
        cls.org_switch_des = None
        cls.org_switch_model_id = None
        cls.modelKey = None
        cls.modelName = None
        cls.logger.info("组织切换管理测试类初始化完成")
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        if cls.md_cache_data:
            cls.orgDimensionId = cls.md_cache_data["org_info"].get("org_dimension_cf",[])[0]["id"]
            cls.com_org_id = cls.md_cache_data["org_info"].get("com_org_info",[])[0]["id"]
    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织切换管理数据
        """
        condition = f"switch_org_id = {cls.com_org_id}"
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_switch_list_cf",
                where=condition,
            )
            cls.db.delete(
                table="org_switch_model_cf",
                where="model_key like %s",
                params=["org_switch_model_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织切换管理",
        title="测试新增组织切换模型",
        description="验证新增组织切换模型功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["组织切换管理", "新增模型"]
    )
    def test_save_org_switch_model(self):
        """
        新增组织切换模型用例
        """
        try:
            # 调用保存接口前准备数据
            menu = f"菜单名称_{self.mock_util.get_timestamp(timestamp=True)}"
            self.modelKey =f"org_switch_model_{self.mock_util.get_timestamp(timestamp=True)}"
            self.modelName = f"组织切换模型表名_{self.mock_util.get_timestamp(timestamp=True)}"     

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "menu": menu,
                "modelKey": self.modelKey,
                "modelName": self.modelName,
                "isOpen": True,
                "describe": f"自动化测试组织切换模型-{self.mock_util.get_timestamp()}"
            }
            fields_to_filter = ["menu", "modelKey", "modelName", "isOpen", "describe"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-保存组织切换模型服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 保存组织切换模型信息供后续用例使用（保持原有SQL逻辑）
            sql = f"select id from org_switch_model_cf where model_key = '{self.modelKey}'"
            result = self.db.query(sql)
            if result:
                self.org_switch_model_id = result[0]["id"]
            else:
                self.logger.warning(f"组织切换模型 {self.modelKey} 在数据库中不存在")
                # 如果数据不存在，说明保存操作失败，需要重新尝试或抛出异常
                raise Exception(f"组织切换模型保存失败，model_key: {self.modelKey}")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试分页查询组织切换模型",
        description="验证分页查询组织切换模型功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["组织切换管理", "模型分页查询"]
    )
    def test_query_org_switch_model_page(self):
        """
        分页查询组织切换模型用例
        """
        try:
            if not self.modelKey:
                self.test_save_org_switch_model()
                
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "modelKey": {
                                "operator": "CONTAINS",
                                "value": self.modelKey
                            }
                        }
                    }
                },
                "fields": [
                    {
                        "name": "modelKey",
                        "type": "TEXT"
                    },
                    {
                        "name": "modelName",
                        "type": "TEXT"
                    },
                    {
                        "name": "isOpen",
                        "type": "BOOL"
                    },
                    {
                        "name": "menu",
                        "type": "TEXT"
                    }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields","systemParams"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-分页查询组织切换模型服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            total = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total, "=", 1)
            
            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试查询组织切换模型详情",
        description="验证查询组织切换模型详情功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["组织切换管理", "模型详情查询"]
    )
    def test_query_org_switch_model_detail(self):
        """
        查询组织切换模型详情用例
        """
        try:
            # 获取组织切换模型信息
            if not self.org_switch_model_id:
                self.test_save_org_switch_model()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_model_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-查询组织切换模型详情服务",
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




    @pytest.mark.skip(
        reason="实际未引用"
    )
    @case_decorator(
        story="组织切换管理",
        title="测试模型是否开启了组织切换",
        description="验证模型是否开启了组织切换功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["组织切换管理", "模型开启判断"]
    )
    def test_judge_model_org_switch_enable(self):
        """
        判断模型是否开启了组织切换用例
        """
        try:
            set_dict = {"model_key": "GEN_MD$ORG_SWITCH_MODEL_CF"}
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-模型是否开启了组织切换服务",
                set_dict=set_dict,
                fields_to_filter=["model_key"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试新增组织切换",
        description="验证新增组织切换功能",
        severity="blocker",
        file_level_order=5,
        smoke=True,
        tags=["组织切换管理", "新增"]
    )
    def test_save_org_switch(self):
        """
        新增组织切换用例
        """
        try:
            
            condition = f"switch_org_id = {self.com_org_id}"
            self.db.delete(
                table="org_switch_list_cf",
                where=condition
            )
            
            # 获取组织切换模型信息
            if not self.org_switch_model_id:
                self.test_save_org_switch_model()
    
            # 准备组织切换数据
            self.org_switch_des = self.mock_util.generate_unique_code(tag="OrgSwitch")
            self.org_switch_name = f"组织切换_{self.mock_util.get_timestamp(timestamp=True)}"

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "switchName": self.org_switch_name,
                "switchDescribe": self.org_switch_des,
                "switchOrgId": {"id": self.com_org_id},
                "switchStatus": "ENABLED", 
                "orgDimensionId": {"id": self.orgDimensionId}
            }
            fields_to_filter = ["switchName","switchOrgId","orgDimensionId","switchStatus","switchName","switchDesc"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-保存组织切换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 保存组织切换信息供后续用例使用（保持原有SQL逻辑）
            sql = f"select id from org_switch_list_cf where switch_name = '{self.org_switch_name}'"
            result = self.db.query(sql)
            self.logger.info(f"查询结果: {result}")
            if result:
                self.org_switch_id = result[0]["id"]
            else:
                self.logger.warning(f"组织切换 {self.org_switch_name} 在数据库中不存在")
                # 如果数据不存在，说明保存操作失败，需要重新尝试或抛出异常
                raise Exception(f"组织切换保存失败，switch_name: {self.org_switch_name}")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试启用组织切换",
        description="验证启用组织切换功能",
        severity="normal",
        file_level_order=6,
        smoke=True,
        tags=["组织切换管理", "启用"]
    )
    def test_enable_org_switch(self):
        """
        启用组织切换用例
        """
        try:
            # 获取组织切换信息
            if not self.org_switch_id:
                self.test_save_org_switch()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-启用组织切换服务",
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
        story="组织切换管理",
        title="测试停用组织切换",
        description="验证停用组织切换功能",
        severity="normal",
        file_level_order=7,
        smoke=True,
        tags=["组织切换管理", "停用"]
    )
    def test_disable_org_switch(self):
        """
        停用组织切换用例
        """
        try:
            # 获取组织切换信息
            if not self.org_switch_id:
                self.test_enable_org_switch()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-停用组织切换服务",
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
        story="组织切换管理",
        title="测试分页查询组织切换",
        description="验证分页查询组织切换功能",
        severity="normal",
        file_level_order=8,
        smoke=True,
        tags=["组织切换管理", "分页查询"]
    )
    def test_query_org_switch_page(self):
        """
        分页查询组织切换用例
        """
        try:
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "orgSwitchName": {"operator": "CONTAINS", "value": self.org_switch_name}
                        }
                    }
                },
                "fields": [
                    {"name": "switch_code", "type": "TEXT"},
                    {"name": "switch_name", "type": "TEXT"},
                    {"name": "status", "type": "SELECT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields","systemParams"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-分页查询组织切换服务",
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
        story="组织切换管理",
        title="测试查询组织切换详情",
        description="验证查询组织切换详情功能",
        severity="normal",
        file_level_order=9,
        smoke=True,
        tags=["组织切换管理", "详情查询"]
    )
    def test_query_org_switch_detail(self):
        """
        查询组织切换详情用例
        """
        try:
            # 获取组织切换信息
            if not self.org_switch_id:
                self.test_save_org_switch()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-查询组织切换详情服务",
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
        story="组织切换管理",
        title="测试查询用户所在的公司",
        description="验证查询用户所在的公司功能",
        severity="normal",
        file_level_order=10,
        smoke=True,
        tags=["组织切换管理", "用户公司查询"]
    )
    def test_query_user_company(self):
        """
        查询用户所在的公司用例
        """
        try:
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {}
            fields_to_filter = []

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-查询用户所在的公司服务",
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

    @pytest.mark.skip(
        reason="实际未引用"
    )
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司列表标准导出",
        description="验证切换公司列表标准导出功能",
        severity="normal",
        file_level_order=11,
        smoke=True,
        tags=["组织切换管理", "列表导出"]
    )
    def test_export_org_switch_list(self):
        """
        切换公司列表标准导出用例
        """
        try:
            set_dict = {
                "exportConfig": {
                    "exportType": "EXCEL",
                    "conditions": {}
                }
            }
            response, _ = self.standard_api_call(
                api_key="切换公司列表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(
        reason="实际未引用"
    )
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司模型表标准导出",
        description="验证切换公司模型表标准导出功能",
        severity="normal",
        file_level_order=12,
        smoke=True,
        tags=["组织切换管理", "模型导出"]
    )
    def test_export_org_switch_model(self):
        """
        切换公司模型表标准导出用例
        """
        try:
            set_dict = {
                "exportConfig": {
                    "exportType": "EXCEL",
                    "conditions": {}
                }
            }
            response, _ = self.standard_api_call(
                api_key="切换公司模型表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["exportConfig"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要上传文件，暂时跳过")
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司列表标准导入",
        description="验证切换公司列表标准导入功能",
        severity="normal",
        file_level_order=13,
        smoke=True,
        tags=["组织切换管理", "列表导入"]
    )
    def test_import_org_switch_list(self):
        """
        切换公司列表标准导入用例
        """
        try:
            # 调用标准导入接口
            api_path = self.get_api_path("切换公司列表标准导入服务")
            params, url = self.get_api_params(api_path)

            # 标准导入需要文件上传，这里暂时跳过实现
            self.logger.info("标准导入需要文件上传，暂时跳过")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要上传文件，暂时跳过")
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司模型表标准导入",
        description="验证切换公司模型表标准导入功能",
        severity="normal",
        file_level_order=14,
        smoke=True,
        tags=["组织切换管理", "模型导入"]
    )
    def test_import_org_switch_model(self):
        """
        切换公司模型表标准导入用例
        """
        try:
            # 调用标准导入接口
            api_path = self.get_api_path("切换公司模型表标准导入服务")
            params, url = self.get_api_params(api_path)

            # 标准导入需要文件上传，这里暂时跳过实现
            self.logger.info("切换公司模型表标准导入需要文件上传，暂时跳过")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试删除组织切换",
        description="验证删除组织切换功能",
        severity="normal",
        file_level_order=15,
        smoke=True,
        tags=["组织切换管理", "删除"]
    )
    def test_delete_org_switch(self):
        """
        删除组织切换用例
        """
        try:
            # 获取组织切换信息
            if not self.org_switch_id:
                self.test_save_org_switch()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-删除组织切换服务",
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
        story="组织切换管理",
        title="测试删除组织切换模型",
        description="验证删除组织切换模型功能",
        severity="normal",
        file_level_order=16,
        smoke=True,
        tags=["组织切换管理", "删除模型"]
    )
    def test_delete_org_switch_model(self):
        """
        删除组织切换模型用例
        """
        try:
            # 获取组织切换模型信息
            if not self.org_switch_model_id:
                self.test_save_org_switch_model()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": self.org_switch_model_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-多组织-删除组织切换模型服务",
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
    
    
    @pytest.mark.skip(
        reason="实际未引用"
    )     
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司列表导出任务提交",
        description="验证切换公司列表导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=17,
        smoke=True,
        tags=["组织切换管理", "列表导出任务"]
    )
    def test_submit_org_switch_list_export_task(self):
        """
        切换公司列表-导入导出任务管理接口-提交导出任务用例
        """
        try:
            # 构建导出任务参数
            export_params = {
                "serviceKey": "GEN_MD$ORG_SWITCH_LIST_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"切换公司列表-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "sheetName": "切换公司列表",
                            "exportConfig": {
                                "exportType": "EXCEL",
                                "conditions": {}
                            }
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$ORG_SWITCH_LIST_VIEW-table-container-GEN_MD$org_switch_list_cf",
                        "viewKey": "GEN_MD$ORG_SWITCH_LIST_VIEW:list",
                        "sceneKey": "GEN_MD$ORG_SWITCH_LIST_VIEW",
                        "params": {
                            "request": {
                                "pageable": {}
                            },
                            "selectFields": [
                                "switchName",
                                "switchDescribe", 
                                "switchStatus",
                                "switchOrgId",
                                "orgDimensionId"
                            ]
                        }
                    }
                }
            }

            response, _ = self.standard_api_call(
                api_key="切换公司列表-导入导出任务管理接口-提交导出任务",
                set_dict=export_params.get("params", {}),
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(export_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试切换公司模型表导出任务提交",
        description="验证切换公司模型表导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=18,
        smoke=True,
        tags=["组织切换管理", "模型导出任务"]
    )
    def test_submit_org_switch_model_export_task(self):
        """
        切换公司模型表-导入导出任务管理接口-提交导出任务用例
        """
        try:
            # 构建导出任务参数
            export_params = {
                "serviceKey": "GEN_MD$ORG_SWITCH_MODEL_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"子公司模型切换-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$org_switch_model_cf",
                            "modelName": "切换公司模型表",
                            "sheetNo": 0,
                            "sheetName": "切换公司模型表",
                            "headerConfigList": [
                                {
                                    "name": "菜单名称",
                                    "type": "TEXT",
                                    "field": "menu"
                                },
                                {
                                    "name": "模型表名",
                                    "type": "TEXT",
                                    "field": "modelKey"
                                },
                                {
                                    "name": "模型表中文名",
                                    "type": "TEXT",
                                    "field": "modelName"
                                },
                                {
                                    "name": "是否切换开关",
                                    "type": "BOOL",
                                    "field": "isOpen"
                                },
                                {
                                    "name": "功能说明",
                                    "type": "TEXT",
                                    "field": "describe"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW-table-container-GEN_MD$org_switch_model_cf",
                        "viewKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW:list",
                        "sceneKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "menu"
                                },
                                {
                                    "field": "modelKey"
                                },
                                {
                                    "field": "modelName"
                                },
                                {
                                    "field": "isOpen"
                                },
                                {
                                    "field": "describe"
                                }
                            ],
                            "modelKey": "GEN_MD$org_switch_model_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$org_switch_model_cf",
                        "modelName": "切换公司模型表",
                        "containerKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW-table-container-GEN_MD$org_switch_model_cf",
                        "viewKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW:list",
                        "sceneKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW"
                    }
                }
            }
                        
            response, _ = self.standard_api_call(
                api_key="切换公司模型表-导入导出任务管理接口-提交导出任务",
                set_dict=export_params.get("params", {}),
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            a.json(export_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司列表OSS导入任务提交",
        description="验证切换公司列表导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=19,
        smoke=True,
        tags=["组织切换管理", "列表OSS导入任务"]
    )
    def test_submit_org_switch_list_import_task_by_oss(self):
        """
        切换公司列表-导入导出任务管理接口-通过OSS提交导入任务用例
        """
        try:
            # 调用通过OSS提交导入任务接口
            api_path = self.get_api_path("切换公司列表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # OSS导入任务需要复杂的文件上传和OSS配置，这里暂时跳过实现
            self.logger.info("OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")
    @case_decorator(
        story="组织切换管理",
        title="测试切换公司模型表OSS导入任务提交",
        description="验证切换公司模型表导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=20,
        smoke=True,
        tags=["组织切换管理", "模型OSS导入任务"]
    )
    def test_submit_org_switch_model_import_task_by_oss(self):
        """
        切换公司模型表-导入导出任务管理接口-通过OSS提交导入任务用例
        """
        try:
            # 调用通过OSS提交导入任务接口
            api_path = self.get_api_path("切换公司模型表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # OSS导入任务需要复杂的文件上传和OSS配置，这里暂时跳过实现
            self.logger.info("OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
