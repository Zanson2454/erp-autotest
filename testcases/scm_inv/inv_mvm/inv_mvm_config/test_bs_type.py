"""作业类型配置的新增、查询、详情、删除测试"""
import random
import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("作业类型配置")
class TestBsTypeManagement(ScmInvBaseTest):
    
    # ========== 常量配置 ==========
    TEST_DATA_PREFIX = "AT"           # 测试数据前缀
    DEFAULT_PAGE_SIZE = 20            # 默认分页大小
    DEFAULT_TEAM_ID = 22              # 默认团队ID
    CODE_START_NUM = 100              # 编码起始数字
    CODE_MAX_RANDOM = 999             # 编码最大随机数
    NAME_MIN_RANDOM = 100000          # 名称最小随机数
    NAME_MAX_RANDOM = 999999          # 名称最大随机数

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.bs_type_id = None
        cls._save_executed = False  # 防重复执行标记
        cls.logger.info("作业类型配置管理测试类初始化完成")

    def _execute_api_call_with_report(self, api_key, request_params=None, assertion_type="success"):
        """
        通用API调用方法 - 减少重复代码
        
        Args:
            api_key: API键名
            request_params: 请求参数字典
            assertion_type: 断言类型 ("success", "data")
        
        Returns:
            response: API响应结果
        """
        try:
            # 1. 调用API
            api_path = self.get_api_path(api_key)
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            # 3. 设置请求参数
            if request_params:
                ParamUtil.set_request_params(filtered_params, request_params)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key=api_key,
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            if assertion_type == "success":
                self.assert_util.assert_response_success(response)
            elif assertion_type == "data":
                self.assert_util.assert_response_data(response)
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            return response
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def _generate_test_data(self):
        """生成测试数据 - 提取数据生成逻辑"""
        bs_type_code = str(self.CODE_START_NUM + random.randint(0, self.CODE_MAX_RANDOM))
        bs_type_name = f"{self.TEST_DATA_PREFIX}{random.randint(self.NAME_MIN_RANDOM, self.NAME_MAX_RANDOM)}"
        return bs_type_code, bs_type_name

    def _get_bs_type_create_params(self, code, name):
        """获取作业类型创建参数 - 提取参数构建逻辑"""
        return {
            "id": None,
            "createdBy": None,
            "updatedBy": None,
            "createdAt": None,
            "updatedAt": None,
            "version": 0,
            "deleted": 0,
            "code": code,
            "uniqueCode": code,
            "name": name,
            "isCreateNewBatch": False,
            "isSupportWriteOff": True,
            "originOrgId": 0
        }

    @case_decorator(
        story="作业类型配置",
        title="测试保存作业类型",
        description="验证作业类型的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "作业类型", "配置"]
    )
    def test_save_bs_type(self):
        """测试保存作业类型"""
        try:
                # 防重复执行检查
                if self.__class__._save_executed and self.bs_type_id is not None:
                    self.logger.info(f"保存方法已执行过，跳过重复执行，ID: {self.bs_type_id}")
                    return

                # 1. 生成测试数据
                bs_type_code, bs_type_name = self._generate_test_data()

                # 2. 获取创建参数并执行API调用
                create_params = self._get_bs_type_create_params(bs_type_code, bs_type_name)
                response = self._execute_api_call_with_report(
                    api_key="INV-作业类型-保存服务",
                    request_params=create_params,
                    assertion_type="data"
                )

                # 3. 保存返回的ID
                response_data = response.get("data", {}).get("data", {})
                self.__class__.bs_type_id = response_data.get("id")
                self.__class__._save_executed = True  # 标记已执行

                self.logger.info(f"作业类型保存成功，ID: {self.bs_type_id}")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="作业类型配置",
        title="测试查询作业类型详情",
        description="验证作业类型的详情查询功能",
        severity="normal",
        order=2,
        tags=["库存", "作业类型", "查询"]
    )
    def test_query_bs_type_detail(self):
        """测试查询作业类型详情"""
        try:
                # 确保前置数据存在
                if self.bs_type_id is None:
                    self._ensure_save_bs_type()

                # 执行详情查询
                response = self._execute_api_call_with_report(
                    api_key="INV-作业类型-详情服务",
                    request_params={"id": self.bs_type_id},
                    assertion_type="data"
                )

                # 验证返回数据
                detail_data = response.get("data", {}).get("data", {})
                self.assert_util.assert_by_operator(detail_data.get("id"), "=", self.bs_type_id)

                self.logger.info(f"作业类型详情查询成功，ID: {self.bs_type_id}")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="作业类型配置",
        title="测试查询作业类型分页",
        description="验证作业类型的分页查询功能",
        severity="normal",
        order=3,
        tags=["库存", "作业类型", "查询"]
    )
    def test_query_bs_type_page(self):
        """测试查询作业类型分页"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("INV-作业类型-查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            # 3. 设置分页查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": self.DEFAULT_PAGE_SIZE,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "code": {
                                "operator": "CONTAINS",
                                "value": self.TEST_DATA_PREFIX
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-作业类型-查询分页服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 验证返回数据结构
            data = response.get("data", {}).get("data", {})
            total = data.get("total", 0)
            data_list = data.get("data", [])
            
            # 基础断言：验证分页查询结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("作业类型分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.skip(reason="导出功能需要完整的业务流程支持，暂时跳过")
    @case_decorator(
        story="作业类型配置",
        title="测试导出作业类型",
        description="验证作业类型的导出功能",
        severity="normal",
        order=4,
        tags=["库存", "作业类型", "导出"]
    )
    def test_export_bs_type(self):
        """测试导出作业类型"""
        try:
            # 依赖保存方法创建的数据
            if not self.bs_type_id:
                self._ensure_save_bs_type()
            
            # 1. 调用API
            api_path = self.get_api_path("作业类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 构造导出参数（基于curl的完整参数结构）
            timestamp = self.mock_util.get_timestamp()
            export_params = {
                "serviceKey": "SCM_INV$INV_BS_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"作业类型-{self.nickname}-{timestamp}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_INV$inv_bs_type_cf",
                            "modelName": "作业类型定义表",
                            "sheetNo": 0,
                            "sheetName": "作业类型定义表",
                            "headerConfigList": [
                                {
                                    "name": "编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "名称",
                                    "type": "TEXT",
                                    "field": "name"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_INV$INV_BS_TYPE_VIEW-table-container-SCM_INV$inv_bs_type_cf",
                        "viewKey": "SCM_INV$INV_BS_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_BS_TYPE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.bs_type_id]
                                            }
                                        }
                                    },
                                    "pageNo": 1,
                                    "pageSize": self.DEFAULT_PAGE_SIZE
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"}
                            ],
                            "modelKey": "SCM_INV$inv_bs_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_INV$inv_bs_type_cf",
                        "modelName": "作业类型定义表",
                        "containerKey": "SCM_INV$INV_BS_TYPE_VIEW-table-container-SCM_INV$inv_bs_type_cf",
                        "viewKey": "SCM_INV$INV_BS_TYPE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_BS_TYPE_VIEW"
                    }
                }
            }
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="作业类型定义表-导入导出任务管理接口-提交导出任务",
                set_dict=(export_params.get("params", {}) if isinstance(export_params, dict) else export_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("作业类型导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="作业类型配置",
        title="测试删除作业类型",
        description="验证作业类型的删除功能",
        severity="normal",
        order=5,
        tags=["库存", "作业类型", "删除"]
    )
    def test_delete_bs_type(self):
        """测试删除作业类型"""
        try:
                # 确保前置数据存在
                if self.bs_type_id is None:
                    self._ensure_save_bs_type()

                # 执行删除操作
                self._execute_api_call_with_report(
                    api_key="INV-作业类型-删除服务",
                    request_params={"id": self.bs_type_id},
                    assertion_type="success"
                )

                self.logger.info(f"作业类型删除成功，ID: {self.bs_type_id}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

