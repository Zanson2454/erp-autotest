import allure
import pytest
import sys
from pathlib import Path
from typing import Any

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
        cls.so_type_id = None
        cls.so_detm_id = None
        cls.logger.info("销售订单类型和订单项目行分配管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理订单项目行分配数据
            cls.db.delete(
                table="sls_so_item_type_detm_cf",
                where="id = %s",
                params=[cls.so_detm_id] if cls.so_detm_id else []
            )
            # 清理销售订单类型数据（如果有创建的话）
            if cls.so_type_id:
                cls.db.delete(
                    table="sls_so_type_cf",
                    where="id = %s",
                    params=[cls.so_type_id]
                )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

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
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$sls_so_type_paging_service",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": [],
                            "conditionItems": {},
                            "conditionGroup": {}
                        }
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 验证返回数据
            response_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(response_data.get("pageNo"), "=", 1)
            
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
            so_item_type_code = self.mock_util.generate_unique_code(tag="SIT")
            remark = self.mock_util.get_mock_remark()
            
            # 2. 调用API
            api_path = self.get_api_path("SLS-订单项目方分配-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$sls_so_detm_save_service",
                "params": {
                    "request": {
                        "soItemTypeCode": so_item_type_code,
                        "remark": remark,
                        "usageType": "NORMAL"
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 5. 保存数据和报告
            self.so_detm_id = response.get("data", {}).get("data", {})
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
                self.test_so_detm_save()
            
            # 1. 调用API
            api_path = self.get_api_path("SLS-订单项目行分配-详情服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$sls_so_detm_detail_service",
                "params": {
                    "request": {
                        "id": self.so_detm_id
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 验证返回数据
            response_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(response_data.get("id"), "=", self.so_detm_id)
            
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
                params, ["serviceKey", "params"], ["params"]
            )
            set_dict = {
                "serviceKey": "SCM_SLS$sls_so_detm_paging_service",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": [],
                            "conditionItems": {},
                            "conditionGroup": {}
                        }
                    }
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 4. 验证返回数据
            response_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(response_data.get("pageNo"), "=", 1)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
