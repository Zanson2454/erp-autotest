import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del import ScmDelBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("交货单管理")
@allure.feature("交货单行类型配置管理")
class TestDelDnItemTypeManagement(ScmDelBaseTest):
    """交货单行类型配置管理测试类"""
    # 常量定义
    MODEL_KEY = "SCM_DEL$del_dn_item_type_cf"
    MODULE_NAME = "SCM_DEL"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.dn_item_type_id = None
        cls.dn_item_type_code = None
        cls.logger.info("交货单行类型配置管理测试类初始化完成")
    

    @case_decorator(
        story="交货单行类型配置新建",
        title="测试创建交货单行类型配置",
        description="验证交货单行类型配置创建功能",
        severity="critical",
        file_level_order=1,
        tags=["交货单行类型配置", "创建", "DEL_DN_ITEN_TYPE_SAVE_CLEAN_CACHE_EVENT_SERVICE"]
    )
    def test_create_dn_item_type(self):
        """创建交货单行类型配置用例"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("DEL-交货单行保存清除缓存服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成测试数据
            timestamp = self.mock_util.get_timestamp()
            test_code = f"AT_{timestamp}"
            test_name = f"自动化测试交货单行类型_{timestamp}"
            
            # 3. 过滤参数 - 只保留业务字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dnItemTypeCode", "dnItemTypeName", "mvmTypeId", "wmMvmTypeId", "spcStkType", 
                 "sourceChannel", "processId", "relatedDnOpType", "packageMvmId", "packageMatMvmId", 
                 "isInvExecuting", "isAutoPostingRelatedDn", "isCreateSett", "status", "id", "remark"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
            ParamUtil.set_request_params(filtered_params, {
                "dnItemTypeCode": test_code,
                "dnItemTypeName": test_name,
                "mvmTypeId": None,
                "wmMvmTypeId": None,
                "spcStkType": None,
                "sourceChannel": None,
                "processId": None,
                "relatedDnOpType": None,
                "packageMvmId": None,
                "packageMatMvmId": None,
                "isInvExecuting": False,
                "isAutoPostingRelatedDn": True,
                "isCreateSett": True,
                "status": "ENABLED",
                "id": None
            })
            
            # 5. 执行请求
            response, _ = self.standard_api_call(
                api_key="DEL-交货单行保存清除缓存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME}
            )
            # 由于此接口返回的data为空，我们只验证请求成功
            self.assert_util.assert_response_success(response)
            
            # 6. 验证结果
            # 由于此接口返回的data为空，我们只验证请求成功
            assert response.get("success") is True, "交货单行类型配置创建失败"
            
            # 7. 保存测试数据（注意：此接口不返回ID，ID将在分页查询中获取）
            self.__class__.dn_item_type_code = test_code
            
            self.logger.info(f"✅ 交货单行类型配置创建成功，编码: {self.__class__.dn_item_type_code}")
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单行类型配置分页查询",
        title="交货单行类型配置分页数据服务",
        description="验证交货单行类型配置分页数据服务功能",
        severity="blocker",
        file_level_order=2,
        tags=["交货单行类型配置", "分页查询", "SYS_PagingDataService"]
    )
    def test_paging_dn_item_type(self):
        """交货单行类型配置分页查询测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("(系统)查询分页数据服务")
            _, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数（使用创建的编码进行条件查询）
            request_params = {
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionItems": {
                                "type": "ConditionItems",
                                "conditions": {
                                    "dnItemTypeCode": {
                                        "operator": "CONTAINS",
                                        "value": self.__class__.dn_item_type_code
                                    }
                                },
                                "logicOperator": "AND"
                            }
                        }
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 3. 执行请求
            response, _ = self.standard_api_call(
                api_key="(系统)查询分页数据服务",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            self.assert_util.assert_response_success(response)
            
            # 4. 验证响应数据并获取ID
            data_list = response["data"]["data"]["data"]
            assert len(data_list) > 0, "分页查询结果为空"
            
            # 5. 从查询结果中获取ID（直接取第一条数据）
            if not self.__class__.dn_item_type_id and data_list:
                self.__class__.dn_item_type_id = data_list[0].get("id")
                self.logger.info(f"✅ 从分页查询中获取到ID: {self.__class__.dn_item_type_id}")
            
            self.logger.info(f"✅ 分页查询成功，共查询到 {len(data_list)} 条数据")
            
            # 6. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单行类型配置详情查询",
        title="测试查询交货单行类型配置详情",
        description="验证交货单行类型配置详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["交货单行类型配置", "详情查询"]
    )
    def test_detail_dn_item_type(self):
        """查询交货单行类型配置详情用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.dn_item_type_id:
                pytest.fail("没有可用的交货单行类型配置ID，跳过详情查询测试")
            
            # 2. 获取API配置
            api_path = self.get_api_path("(系统)查询数据详情服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 构建请求参数 - 完全按照curl的结构
            request_params = {
                "params": {
                    "request": {
                        "id": self.__class__.dn_item_type_id
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 4. 执行请求
            response, _ = self.standard_api_call(
                api_key="(系统)查询数据详情服务",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert result_data.get("id") == self.__class__.dn_item_type_id, "详情查询ID不匹配"            
            self.logger.info(f"✅ 交货单行类型配置详情查询成功，ID: {self.__class__.dn_item_type_id}")
            
            # 5. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单行类型配置停用",
        title="测试停用交货单行类型配置",
        description="验证交货单行类型配置停用功能",
        severity="critical",
        file_level_order=4,
        tags=["交货单行类型配置", "停用", "DEL_DN_ITEM_TYPE_DIS_ENABLED_EVENT_SERVICE"]
    )
    def test_disable_dn_item_type(self):
        """停用交货单行类型配置用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.dn_item_type_id:
                self._ensure_create_dn_item_type()
            
            # 2. 获取API配置
            api_path = self.get_api_path("DEL-交货单缓存-行类型停用")
            params, url = self.get_api_params(api_path)
            
            # 3. 过滤参数 - 不要过滤status字段，EVENT_SERVICE会自动处理状态
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dnItemTypeCode", "dnItemTypeName", "isCreateSett", "isAutoPostingRelatedDn", 
                 "isInvExecuting", "spcStkType", "id"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数 - EVENT_SERVICE不需要传递status字段
            ParamUtil.set_request_params(filtered_params, {
                "dnItemTypeCode": self.__class__.dn_item_type_code,
                "dnItemTypeName": f"自动化测试交货单行类型_{self.mock_util.get_timestamp()}",
                "isCreateSett": True,
                "isAutoPostingRelatedDn": True,
                "isInvExecuting": False,
                "spcStkType": [],
                "id": self.__class__.dn_item_type_id
            })
            
            # 5. 执行请求
            response, _ = self.standard_api_call(
                api_key="DEL-交货单缓存-行类型停用",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME}
            )
            
            # 6. 验证停用结果
            assert response.get("success") is True, "停用请求失败"
            
            self.logger.info(f"✅ 交货单行类型配置停用成功，ID: {self.__class__.dn_item_type_id}")
            
            # 7. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单行类型配置启用",
        title="测试启用交货单行类型配置",
        description="验证交货单行类型配置启用功能",
        severity="critical",
        file_level_order=5,
        tags=["交货单行类型配置", "启用", "DEL_DN_ITEM_TYPE_ENABLED_EVENT_SERVICE"]
    )
    def test_enable_dn_item_type(self):
        """启用交货单行类型配置用例"""
        try:
            # 1. 检查是否有可用的ID（需要先停用才能启用）
            if not self.__class__.dn_item_type_id:
                self._ensure_create_dn_item_type()
                self._ensure_disable_dn_item_type()
            
            # 2. 获取API配置
            api_path = self.get_api_path("DEL-交货单缓存-行类型启用")
            params, url = self.get_api_params(api_path)
            
            # 3. 过滤参数 - 不要过滤status字段，EVENT_SERVICE会自动处理状态
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dnItemTypeCode", "dnItemTypeName", "isCreateSett", "isAutoPostingRelatedDn", 
                 "isInvExecuting", "spcStkType", "id"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数 - EVENT_SERVICE不需要传递status字段
            ParamUtil.set_request_params(filtered_params, {
                "dnItemTypeCode": self.__class__.dn_item_type_code,
                "dnItemTypeName": f"自动化测试交货单行类型_{self.mock_util.get_timestamp()}",
                "isCreateSett": True,
                "isAutoPostingRelatedDn": True,
                "isInvExecuting": False,
                "spcStkType": [],
                "id": self.__class__.dn_item_type_id
            })
            
            # 5. 执行请求
            response, _ = self.standard_api_call(
                api_key="DEL-交货单缓存-行类型启用",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME}
            )
            
            # 6. 验证启用结果
            assert response.get("success") is True, "启用请求失败"
            
            self.logger.info(f"✅ 交货单行类型配置启用成功，ID: {self.__class__.dn_item_type_id}")
            
            # 7. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单行类型配置删除",
        title="测试删除交货单行类型配置",
        description="验证交货单行类型配置删除功能",
        severity="critical",
        file_level_order=6,
        tags=["交货单行类型配置", "删除", "SYS_DeleteDataByIdService"]
    )
    def test_delete_dn_item_type(self):
        """删除交货单行类型配置用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.dn_item_type_id:
                pytest.fail("没有可用的交货单行类型配置ID，跳过删除测试")
            
            # 2. 删除前先禁用（确保数据处于可删除状态）
            self.logger.info("删除前先禁用交货单行类型配置...")
            try:
                self._ensure_disable_dn_item_type()
            except Exception as e:
                self.logger.warning(f"禁用操作失败（可能已经是禁用状态）: {str(e)}")
            
            # 3. 获取API配置 - 使用正确的服务名称
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 4. 构建请求参数 - 完全按照curl的结构
            request_params = {
                "params": {
                    "request": {
                        "id": self.__class__.dn_item_type_id
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 5. 执行请求
            response, _ = self.standard_api_call(
                api_key="(系统)删除数据服务",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 6. 验证删除结果
            if not response.get("success"):
                error_msg = response.get("message") or response.get("errorMessage") or "未知错误"
                self.logger.error(f"删除失败，响应信息: {response}")
                assert False, f"删除请求失败: {error_msg}"
            
            self.logger.info(f"✅ 交货单行类型配置删除成功，ID: {self.__class__.dn_item_type_id}")
            
            # 7. 清空类变量
            deleted_id = self.__class__.dn_item_type_id
            self.__class__.dn_item_type_id = None
            self.__class__.dn_item_type_code = None
            
            # 8. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"已删除ID: {deleted_id}", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
