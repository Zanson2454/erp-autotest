"""移动类型配置的新增、查询、详情、删除、导出测试"""
import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("移动类型配置")
class TestMvmTypeManagement(ScmInvBaseTest):
    """
    移动类型配置管理测试类
    
    测试范围: 覆盖移动类型的完整生命周期管理
    执行顺序: 按order参数依次执行，确保数据依赖关系
    数据隔离: 使用AUTOMATION_TEST_REMARK标识测试数据，支持并发执行
    """
    
    # ========== 常量配置 ==========
    AUTOMATION_TEST_REMARK = "自动化测试"  # 测试数据标识
    DEFAULT_PAGE_SIZE = 20               # 默认分页大小
    DEFAULT_TEAM_ID = 22                 # 默认团队ID
    REFERENCE_DATA_NAME = "初始化-无正逆向-非限制-非限制-常规业务"  # 参考数据名称
    
    # 默认关联ID配置 - 当数据库中无参考数据时使用
    DEFAULT_IDS = {
        'bs_type_id': 2000005,          # 业务类型ID
        'fb_type_id': 2002002,          # 正逆向标识ID  
        'inv_type_trans_id': 2001002,   # 库存类型转移ID
        'mvm_ext_type_id': 2001003,     # 业务类型扩展ID
        'inv_type_id': 2000001          # 库存类型ID(非限制)
    }

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mvm_type_id = None
        cls.mvm_type_code = None
        cls.mvm_type_remark = None
        cls._save_executed = False  # 防重复执行标记
        
        # 查询现有数据获取关联ID
        try:
            sql = """
            SELECT 
                bs_type_id, fb_type_id, inv_type_trans_id, 
                remark, mvm_ext_type_id, name
            FROM inv_mvm_type_cf 
            WHERE name = %s
            LIMIT 1
            """
            result = cls.db.select(sql, [cls.REFERENCE_DATA_NAME])
            if result and len(result) > 0:
                row = result[0]  # 取第一行数据
                cls.reference_data = {
                    'bs_type_id': row[0],
                    'fb_type_id': row[1], 
                    'inv_type_trans_id': row[2],
                    'remark': row[3],
                    'mvm_ext_type_id': row[4],
                    'name': row[5]
                }
                cls.logger.info(f"获取参考数据成功: {cls.reference_data}")
            else:
                cls.logger.warning("未找到参考数据，将使用默认配置")
                cls.reference_data = {}
        except Exception as e:
            cls.logger.error(f"获取参考数据失败: {str(e)}")
            cls.reference_data = {}
            
        cls.logger.info("移动类型配置管理测试类初始化完成")

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

    def _get_mvm_type_create_params(self, code, name):
        """
        获取移动类型创建参数 - 提取复杂参数构建逻辑
        """
        return {
            "id": None,
            "createdBy": None,
            "updatedBy": None,
            "createdAt": None,
            "updatedAt": None,
            "version": 0,
            "deleted": 0,
            "code": code,
            "bsTypeId": {
                "id": self.reference_data.get('bs_type_id', self.DEFAULT_IDS['bs_type_id'])
            },
            "fbTypeId": {
                "id": self.reference_data.get('fb_type_id', self.DEFAULT_IDS['fb_type_id'])
            },
            "invTypeTransId": {
                "id": self.reference_data.get('inv_type_trans_id', self.DEFAULT_IDS['inv_type_trans_id'])
            },
            "name": name,
            "status": "INACTIVE",
            "remark": self.AUTOMATION_TEST_REMARK,
            "mvmExtTypeId": {
                "id": self.reference_data.get('mvm_ext_type_id', self.DEFAULT_IDS['mvm_ext_type_id'])
            },
            "batchCodeRuleKey": None,
            "originOrgId": 0,
            "mvmRule": [
                {
                    "isSpcStk": False,
                    "invOrgIdSource": "NONE",
                    "invTypeId": {
                        "id": self.DEFAULT_IDS['inv_type_id']
                    },
                    "mvmPosNeg": "INCREASE"
                }
            ]
        }

    @case_decorator(
        story="移动类型配置",
        title="测试保存移动类型",
        description="验证移动类型的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "移动类型", "配置"]
    )
    def test_save_mvm_type(self):
        """测试保存移动类型"""
        try:
                # 防重复执行检查
                if self.__class__._save_executed and self.mvm_type_id is not None:
                    self.logger.info(f"保存方法已执行过，跳过重复执行，ID: {self.mvm_type_id}")
                    return

                # 1. 准备测试数据
                mvm_type_code = self.mock_util.generate_unique_code(tag="AT")
                mvm_type_name = f"移动类型_{self.mock_util.get_timestamp()}"

                # 2. 获取创建参数并执行API调用
                create_params = self._get_mvm_type_create_params(mvm_type_code, mvm_type_name)
                self._execute_api_call_with_report(
                    api_key="INV-移动类型-保存服务",
                    request_params=create_params,
                    assertion_type="success"
                )

                # 3. 记录成功日志
                self.logger.info("移动类型保存成功")


        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试查询移动类型分页",
        description="验证移动类型的分页查询功能",
        severity="normal",
        order=3,
        tags=["库存", "移动类型", "查询"]
    )
    def test_query_mvm_type_page(self):
        """测试查询移动类型分页"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("INV-移动类型-查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            # 3. 设置分页查询参数（基于curl请求结构）
            query_params = {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": self.DEFAULT_PAGE_SIZE,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None
                    },
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "bsTypeId", "type": "OBJECT"},
                        {"name": "fbTypeId", "type": "OBJECT"},
                        {"name": "invTypeTransId", "type": "OBJECT"},
                        {"name": "mvmExtTypeId", "type": "OBJECT"},
                        {"name": "status", "type": "SELECT"}
                    ],
                    "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-移动类型-查询分页服务",
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
            
            # 6. 查找自动化测试创建的数据
            automation_record = None
            for record in data_list:
                if record.get("remark") == self.AUTOMATION_TEST_REMARK:
                    automation_record = record
                    # 保存关键信息供后续删除使用
                    self.__class__.mvm_type_id = record.get("id")
                    self.__class__._save_executed = True  # 标记已执行
                    self.__class__.mvm_type_code = record.get("code") 
                    self.__class__.mvm_type_remark = record.get("remark")
                    self.logger.info(f"找到自动化测试数据 - ID: {self.mvm_type_id}, Code: {self.mvm_type_code}, Remark: {self.mvm_type_remark}")
                    break
            
            if automation_record is None:
                self.logger.warning("未找到自动化测试创建的数据记录")
            
            # 7. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            if automation_record:
                a.json(automation_record, "找到的自动化测试数据")
            
            self.logger.info("移动类型分页查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试查询移动类型详情",
        description="验证移动类型的详情查询功能",
        severity="normal",
        order=4,
        tags=["库存", "移动类型", "详情查询"]
    )
    def test_query_mvm_type_detail(self):
        """测试查询移动类型详情"""
        try:
            # 确保前置数据存在
            if self.mvm_type_id is None:
                self._ensure_save_mvm_type()
                self._ensure_query_mvm_type_page()
            
            # 1. 构建URL和参数（直接写死，因为yaml中查询不到）
            
            # 2. 设置详情查询参数
            detail_params = {
                "params": {
                    "request": {
                        "id": str(self.mvm_type_id)
                    },
                    "modelKey": "SCM_INV$inv_mvm_type_cf"
                }
            }
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="INV-移动类型-查询分页服务",
                set_dict=(detail_params.get("params", {}) if isinstance(detail_params, dict) else detail_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 4. 验证返回的详情数据
            detail_data = response.get("data", {}).get("data", {})
            
            # 基础断言：验证详情数据结构
            assert detail_data is not None, "详情数据不能为空"
            assert detail_data.get("id") == self.mvm_type_id, f"ID不匹配，expected: {self.mvm_type_id}, actual: {detail_data.get('id')}"
            assert detail_data.get("code") == self.mvm_type_code, f"编码不匹配，expected: {self.mvm_type_code}, actual: {detail_data.get('code')}"
            assert detail_data.get("remark") == self.mvm_type_remark, f"备注不匹配，expected: {self.mvm_type_remark}, actual: {detail_data.get('remark')}"
            
            # 5. 报告记录
            a.json(detail_params, "请求数据")
            a.json(response, "响应数据")
            a.json(detail_data, "详情数据")
            
            self.logger.info(f"移动类型详情查询成功，ID: {self.mvm_type_id}, Code: {self.mvm_type_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试启用移动类型",
        description="验证移动类型的启用功能",
        severity="normal",
        order=5,
        tags=["库存", "移动类型", "启用"]
    )
    def test_enable_mvm_type(self):
        """测试启用移动类型"""
        try:
                # 确保前置数据存在
                if self.mvm_type_id is None:
                    self._ensure_save_mvm_type()
                    self._ensure_query_mvm_type_page()

                # 执行启用操作
                self._execute_api_call_with_report(
                    api_key="INV-移动类型-启用服务",
                    request_params={"id": self.mvm_type_id},
                    assertion_type="success"
                )

                self.logger.info(f"移动类型启用成功，ID: {self.mvm_type_id}")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试禁用移动类型",
        description="验证移动类型的禁用功能",
        severity="normal",
        order=6,
        tags=["库存", "移动类型", "禁用"]
    )
    def test_disable_mvm_type(self):
        """测试禁用移动类型"""
        try:
                # 确保前置数据存在
                if self.mvm_type_id is None:
                    self._ensure_save_mvm_type()
                    self._ensure_query_mvm_type_page()

                # 执行禁用操作
                self._execute_api_call_with_report(
                    api_key="INV-移动类型-禁用服务",
                    request_params={"id": self.mvm_type_id},
                    assertion_type="success"
                )

                self.logger.info(f"移动类型禁用成功，ID: {self.mvm_type_id}")

            #@pytest.mark.skip(reason="导出功能需要完整的业务流程支持，暂时跳过")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试导出移动类型",
        description="验证移动类型的导出功能",
        severity="normal",
        order=7,
        tags=["库存", "移动类型", "导出"]
    )
    def test_export_mvm_type(self):
        """测试导出移动类型"""
        try:
            # 依赖保存方法创建的数据
            if not self.mvm_type_id:
                self._ensure_save_mvm_type()
            
            # 1. 调用API
            api_path = self.get_api_path("移动类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 构造导出参数
            timestamp = self.mock_util.get_timestamp()
            export_params = {
                "serviceKey": "SCM_INV$INV_MVM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"移动类型-{self.nickname}-{timestamp}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "SCM_INV$inv_mvm_type_cf",
                            "modelName": "移动类型定义表",
                            "sheetNo": 0,
                            "sheetName": "移动类型定义表",
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
                                },
                                {
                                    "name": "业务类型",
                                    "type": "TEXT",
                                    "field": "bsTypeId.name"
                                },
                                {
                                    "name": "作业正逆向标识",
                                    "type": "TEXT",
                                    "field": "fbTypeId.name"
                                },
                                {
                                    "name": "库存类型转移标识",
                                    "type": "TEXT",
                                    "field": "invTypeTransId.name"
                                },
                                {
                                    "name": "业务类型扩展",
                                    "type": "TEXT",
                                    "field": "mvmExtTypeId.name"
                                },
                                {
                                    "name": "状态",
                                    "type": "ENUM",
                                    "field": "status",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {"label": "未启用", "value": "INACTIVE"},
                                        {"label": "已启用", "value": "ENABLED"},
                                        {"label": "已停用", "value": "DISABLED"}
                                    ]
                                },
                                {
                                    "name": "备注",
                                    "type": "TEXT",
                                    "field": "remark"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW-table-container-SCM_INV$inv_mvm_type_cf",
                        "viewKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW:list",
                        "sceneKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": self.DEFAULT_PAGE_SIZE
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"},
                                {"field": "status"},
                                {"field": "remark"},
                                {"field": "bsTypeId", "selectFields": [{"field": "name"}]},
                                {"field": "fbTypeId", "selectFields": [{"field": "name"}]},
                                {"field": "invTypeTransId", "selectFields": [{"field": "name"}]},
                                {"field": "mvmExtTypeId", "selectFields": [{"field": "name"}]}
                            ],
                            "modelKey": "SCM_INV$inv_mvm_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_INV$inv_mvm_type_cf",
                        "modelName": "移动类型定义表",
                        "containerKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW-table-container-SCM_INV$inv_mvm_type_cf",
                        "viewKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW:list",
                        "sceneKey": "SCM_INV$INV_MVM_TYPE_NEW_VIEW"
                    }
                }
            }
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="移动类型定义表-导入导出任务管理接口-提交导出任务",
                set_dict=(export_params.get("params", {}) if isinstance(export_params, dict) else export_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 报告记录
            a.json(export_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info("移动类型导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动类型配置",
        title="测试删除移动类型",
        description="验证移动类型的删除功能",
        severity="normal",
        order=8,
        tags=["库存", "移动类型", "删除"]
    )
    def test_delete_mvm_type(self):
        """测试删除移动类型"""
        try:
                # 确保前置数据存在
                if self.mvm_type_id is None:
                    self._ensure_save_mvm_type()
                    self._ensure_query_mvm_type_page()

                # 执行删除操作
                self._execute_api_call_with_report(
                    api_key="INV-移动类型-删除服务",
                    request_params={"id": self.mvm_type_id},
                    assertion_type="success"
                )

                self.logger.info(f"移动类型删除成功，ID: {self.mvm_type_id}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

