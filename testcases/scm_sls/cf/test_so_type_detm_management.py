import sys
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单类型和订单项目行分配管理")
class TestSoTypeDetmManagement(SlsBase):
    """销售订单类型和订单项目行分配管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.so_detm_id = None
        cls.logger.info("销售订单类型和订单项目行分配管理测试类初始化完成")
        
        # 获取依赖数据
        cls.so_type_id = cls.ORDER_TYPES[0]["id"]
        cls.so_item_type_id = cls.ORDER_LINE_TYPES[0]["id"]
        cls.so_item_type_group_id = cls.ORDER_LINE_TYPES[0]["id"]
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # 数据清理已移至 session 级别的 fixture 统一处理
        # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
        cls.logger.info("测试类执行完成，数据将在 session 结束时统一清理")

        super().teardown_class()
    @case_decorator(
        story="销售订单类型管理",
        title="测试销售订单类型分页查询",
        description="验证销售订单类型分页查询功能",
        severity="normal",
        order=1,
        tags=["销售订单类型", "分页查询", "sls_so_type_paging_service"]
    )
    def test_so_type_paging(self):
        """销售订单类型分页查询用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SLS-销售订单类型-分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params","request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [],
                    "conditionItems": {},
                    "conditionGroup": {}
                }
            }
        
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单类型-分页服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单项目行分配管理",
        title="测试订单项目行分配保存",
        description="验证订单项目行分配保存功能",
        severity="normal",
        order=2,
        tags=["订单项目行分配", "保存", "sls_so_detm_save_service"]
    )
    def test_so_detm_save(self):
        """订单项目行分配保存用例"""
        try:
            # 1. 准备测试数据
            self.mock_util.generate_unique_code(tag="SIT")
            
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-订单项目方分配-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "soTypeId": {"id": self.so_type_id},
                "soItemTypeId": {"id": self.so_item_type_id},
                "soItemTypeGroupId": {"id": self.so_item_type_group_id},
                "parentSoItemTypeId": None,
                "soItemTypeId1": None,
                "soItemTypeId2": None,
                "soItemTypeId3": None,
                "usageType": None,
                "remark": f"自动化测试_{self.mock_util.get_timestamp()}",
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单项目方分配-保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 5. 保存数据和报告
            self.so_detm_id = response.get("data", {}).get("data", {}).get("id")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单项目行分配管理",
        title="测试订单项目行分配详情查询",
        description="验证订单项目行分配详情查询功能",
        severity="normal",
        order=3,
        tags=["订单项目行分配", "详情查询", "sls_so_detm_detail_service"]
    )
    def test_so_detm_detail(self):
        """订单项目行分配详情查询用例"""
        try:
            # 检查依赖数据
            if not self.so_detm_id:
                self._ensure_so_detm_save()
            
            # 1. 调用API
            api_path = self.get_api_path("SLS-订单项目行分配-详情服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params","request"]
            )
            set_dict = {
                        "id": self.so_detm_id
                    }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单项目行分配-详情服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单项目行分配管理",
        title="测试订单项目行分配分页查询",
        description="验证订单项目行分配分页查询功能",
        severity="normal",
        order=4,
        tags=["订单项目行分配", "分页查询", "sls_so_detm_paging_service"]
    )
    def test_so_detm_paging(self):
        """订单项目行分配分页查询用例"""
        try:
            # 1. 调用API
            api_path = self.get_api_path("SLS-订单项目行分配-分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params","request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
                
                
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="SLS-订单项目行分配-分页服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
