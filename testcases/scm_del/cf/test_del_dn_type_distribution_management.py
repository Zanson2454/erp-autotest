import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del import ScmDelBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("交货单管理")
@allure.feature("交货单类型分配管理")
class TestDelDnTypeDistributionManagement(ScmDelBaseTest):
    """交货单类型分配管理测试类"""
    # 常量定义
    MODEL_KEY = "SCM_DEL$del_dn_type_distribution_cf"
    MODULE_NAME = "SCM_DEL"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.distribution_id = None
        cls.logger.info("交货单类型分配管理测试类初始化完成")
        
        # 从缓存数据中获取ID
        if cls.del_cache_data:
            pur_config = cls.del_cache_data.get("pur_config", {})
            cls.dn_type_id = pur_config.get("dn_type_info", [{}])[0].get("id")
            cls.dn_item_type_id = pur_config.get("dn_item_type_info", [{}])[0].get("id")
    @case_decorator(
        story="交货单类型分配新建",
        title="测试创建交货单类型分配",
        description="验证交货单类型分配创建功能",
        severity="critical",
        file_level_order=1,
        tags=["交货单类型分配", "创建", "DEL_DN_TYPE_DISTRIBUTION_CACHE_CLEAR_EVENT_SERVICE"]
    )
    def test_create_dn_type_distribution(self):
        """创建交货单类型分配用例"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("DEL-保存清除分配表缓存信息服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 过滤参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["btClass", "delClass", "deliveryType", "dnTypeId", "isWriteOff", "id", "dnItemTypeId", "docTypeName", "docItemTypeName", "docTypeId", "docItemTypeId"],
                ["params", "request"]
            )
            
            # 3. 设置请求参数
            set_dict = {
                "btClass": "PUR",
                "delClass": "RECV", 
                "deliveryType": None,
                "dnTypeId": {"id": self.__class__.dn_type_id},
                "isWriteOff": False,
                "id": None,
                "dnItemTypeId": {"id": self.__class__.dn_item_type_id},
                "docTypeName": None,
                "docItemTypeName": None,
                "docTypeId": None,
                "docItemTypeId": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 执行请求
            response, _ = self.standard_api_call(
                api_key="DEL-保存清除分配表缓存信息服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME}
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert result_data is not None, "交货单类型分配创建失败"
            
            # 6. 保存测试数据
            self.__class__.distribution_id = result_data.get("id")
            
            self.logger.info(f"✅ 交货单类型分配创建成功，ID: {self.__class__.distribution_id}")
            
            # 7. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单类型分配分页查询",
        title="交货单类型分配分页数据服务",
        description="验证交货单类型分配分页数据服务功能",
        severity="blocker",
        file_level_order=2,
        tags=["交货单类型分配", "分页查询", "SYS_PagingDataService"]
    )
    def test_paging_dn_type_distribution(self):
        """交货单类型分配分页查询测试"""
        try:
            # 1. 构建完整请求参数
            request_params = {
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionItems": None
                        }
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 2. 获取API配置并构建URL
            api_path = self.get_api_path("(系统)查询分页数据服务")
            _, url = self.get_api_params(api_path)
            
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
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            assert len(data_list) > 0, "分页查询结果为空"
            
            # 5. 从查询结果中获取ID（直接取第一条数据）
            if not self.__class__.distribution_id and data_list:
                self.__class__.distribution_id = data_list[0].get("id")
                self.logger.info(f"✅ 从分页查询中获取到ID: {self.__class__.distribution_id}")
            
            self.logger.info(f"✅ 分页查询成功，共查询到 {len(data_list)} 条数据")
            
            # 6. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单类型分配详情查询",
        title="测试查询交货单类型分配详情",
        description="验证交货单类型分配详情查询功能",
        severity="normal",
        file_level_order=3,
        tags=["交货单类型分配", "详情查询"]
    )
    def test_detail_dn_type_distribution(self):
        """查询交货单类型分配详情用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.distribution_id:
                pytest.skip("没有可用的交货单类型分配ID，跳过详情查询测试")
            
            # 2. 构建完整请求参数
            request_params = {
                "params": {
                    "request": {
                        "id": self.__class__.distribution_id
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 3. 获取API配置并构建URL
            api_path = self.get_api_path("(系统)查询数据详情服务")
            _, url = self.get_api_params(api_path)
            
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
            
            # 5. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert result_data.get("id") == self.__class__.distribution_id, "详情查询ID不匹配"            
            self.logger.info(f"✅ 交货单类型分配详情查询成功，ID: {self.__class__.distribution_id}")
            
            # 6. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="交货单类型分配删除",
        title="测试删除交货单类型分配",
        description="验证交货单类型分配删除功能",
        severity="critical",
        file_level_order=4,
        tags=["交货单类型分配", "删除", "DEL_DN_ITEM_TYPE_DISTRIBUTION_DELETE_EVENT_SERVICE"]
    )
    def test_delete_dn_type_distribution(self):
        """删除交货单类型分配用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.distribution_id:
                pytest.skip("没有可用的交货单类型分配ID，跳过删除测试")
            
            # 2. 构建完整请求参数
            request_params = {
                "params": {
                    "request": {
                        "id": self.__class__.distribution_id
                    }
                }
            }
            
            # 3. 获取API配置并构建URL
            api_path = self.get_api_path("DEL-交货单类型分配表删除服务")
            _, url = self.get_api_params(api_path)
            
            # 4. 执行请求
            response, _ = self.standard_api_call(
                api_key="DEL-交货单类型分配表删除服务",
                set_dict=(request_params.get("params", {}) if isinstance(request_params, dict) else request_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
                query_params={"tmodule": self.MODULE_NAME}
            )
            
            # 5. 验证删除结果
            if not response.get("success"):
                error_msg = response.get("message") or response.get("errorMessage") or "未知错误"
                self.logger.error(f"删除失败，响应信息: {response}")
                assert False, f"删除请求失败: {error_msg}"
            
            self.logger.info(f"✅ 交货单类型分配删除成功，ID: {self.__class__.distribution_id}")
            
            # 6. 清空类变量
            deleted_id = self.__class__.distribution_id
            self.__class__.distribution_id = None
            
            # 7. 记录报告
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"已删除ID: {deleted_id}", "删除结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
