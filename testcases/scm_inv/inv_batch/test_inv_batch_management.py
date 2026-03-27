import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("批次主数据管理")
class TestBatchManagement(ScmInvBaseTest):
    """批次主数据管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 测试数据变量
        cls.batch_id = None
        cls.batch_code = None
        cls.test_batch_code = None  # 从第一个查询结果中提取的批次编码
        cls.test_mat_id = None      # 从第一个查询结果中提取的物料ID
        cls.test_batch_id = None    # 从第一个查询结果中提取的批次ID
        
        # 从初始化数据中获取ID
        cls.unitId = cls.init_data["uom_info"]["qty_uom_info"][0]["uom_id"] if cls.init_data.get("uom_info", {}).get("qty_uom_info") else None
        
        # 从inv_cache_data中获取ID
        if cls.inv_cache_data:
            # 公司组织ID
            cls.comOrgId = cls.inv_cache_data["org_info"]["gr_come_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("gr_come_org_info") else None
            # 库存组织ID
            cls.invOrgId = cls.inv_cache_data["org_info"]["inv_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_org_info") else None
            # 库存地点ID
            cls.invLocId = cls.inv_cache_data["org_info"]["inv_loc_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_loc_info") else None
            # 物料ID (使用成品物料)
            cls.matId = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"] if cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP") else None
        
        cls.logger.info("批次主数据管理测试类初始化完成")

    @case_decorator(
        story="批次主数据管理",
        title="测试查询批次主数据分页",
        description="验证批次主数据分页查询功能",
        severity="normal",
        order=1,
        smoke=True,
        tags=["批次主数据", "分页查询"]
    )
    def test_query_batch_page(self):
        """查询批次主数据分页用例"""
        try:
            api_path = self.get_api_path("INV-批次-批次分页查询服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "charaClassId", "type": "OBJECT"},
                    {"name": "createdAt", "type": "DATE"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-批次-批次分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言分页数据
            page_data = response.get("data", {}).get("data", {})
            total = page_data.get("total", 0)
            data_list = page_data.get("data", [])
            
            # 基础断言：验证分页查询结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            # 如果有数据，验证数据结构完整性并提取测试数据
            if data_list:
                first_item = data_list[0]
                assert "matId" in first_item, "批次记录缺少物料ID字段"
                assert "code" in first_item, "批次记录缺少批次编码字段"
                assert "id" in first_item, "批次记录缺少批次ID字段"
                
                # 提取第一条数据的关键信息用于后续测试
                self.test_batch_code = first_item.get("code")
                self.test_batch_id = first_item.get("id")
                self.logger.info(f"提取到批次编码: {self.test_batch_code}")
                self.logger.info(f"提取到批次ID: {self.test_batch_id}")
                
                mat_info = first_item.get("matId", {})
                if isinstance(mat_info, dict) and mat_info.get("id"):
                    self.test_mat_id = mat_info.get("id")
                    self.logger.info(f"提取到物料ID: {self.test_mat_id}")
                
                self.logger.info(f"分页查询成功，总记录数: {total}, 当前页记录数: {len(data_list)}")
            else:
                self.logger.info("分页查询成功，但当前无批次数据")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="批次主数据管理",
        title="测试根据批次编码查询",
        description="验证根据批次编码筛选查询功能",
        severity="normal",
        order=2,
        tags=["批次主数据", "编码筛选"]
    )
    def test_query_batch_by_code(self):
        """根据批次编码查询用例"""
        try:
            # 确保先执行基础查询获取测试数据
            if not self.test_batch_code:
                self.test_query_batch_page()
                
            # 如果仍然没有测试数据，跳过测试
            if not self.test_batch_code:
                self.logger.warning("未找到可用的批次编码，跳过编码筛选测试")
                return
                
            api_path = self.get_api_path("INV-批次-批次分页查询服务")
            params, url = self.get_api_params(api_path)

            # 根据批次编码筛选
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "code": {
                                "operator": "EQ",
                                "value": self.test_batch_code
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "charaClassId", "type": "OBJECT"},
                    {"name": "createdAt", "type": "DATE"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-批次-批次分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言筛选结果
            page_data = response.get("data", {}).get("data", {})
            data_list = page_data.get("data", [])
            total = page_data.get("total", 0)
            
            # 基础断言：验证查询结果结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            if data_list:
                # 验证所有记录都是指定的批次编码
                for item in data_list:
                    actual_code = item.get("code")
                    assert actual_code == self.test_batch_code, f"筛选结果包含其他批次编码的记录: {actual_code}"
                
                self.logger.info(f"根据批次编码 [{self.test_batch_code}] 筛选查询成功，找到 {len(data_list)} 条记录")
            else:
                self.logger.info(f"根据批次编码 [{self.test_batch_code}] 筛选查询成功，但未找到记录")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="批次主数据管理",
        title="测试根据物料ID查询批次",
        description="验证根据物料ID筛选查询批次功能",
        severity="normal",
        order=3,
        tags=["批次主数据", "物料筛选"]
    )
    def test_query_batch_by_material_id(self):
        """根据物料ID查询批次用例"""
        try:
            # 确保先执行基础查询获取测试数据
            if not self.test_mat_id:
                self.test_query_batch_page()
                
            # 如果仍然没有测试数据，跳过测试
            if not self.test_mat_id:
                self.logger.warning("未找到可用的物料ID，跳过物料筛选测试")
                return
                
            api_path = self.get_api_path("INV-批次-批次分页查询服务")
            params, url = self.get_api_params(api_path)

            # 根据物料ID筛选批次
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [{"fieldAlias": "createdAt", "sortType": "DESC"}],
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "matId": {
                                "operator": "EQ",
                                "value": self.test_mat_id
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "charaClassId", "type": "OBJECT"},
                    {"name": "createdAt", "type": "DATE"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-批次-批次分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言筛选结果
            page_data = response.get("data", {}).get("data", {})
            data_list = page_data.get("data", [])
            total = page_data.get("total", 0)
            
            # 基础断言：验证查询结果结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            if data_list:
                # 验证所有记录都是指定的物料ID
                for item in data_list:
                    mat_info = item.get("matId", {})
                    if isinstance(mat_info, dict):
                        actual_mat_id = mat_info.get("id")
                        assert actual_mat_id == self.test_mat_id, f"筛选结果包含其他物料ID的批次: {actual_mat_id}"
                
                self.logger.info(f"根据物料ID [{self.test_mat_id}] 筛选查询成功，找到 {len(data_list)} 条批次记录")
            else:
                self.logger.info(f"根据物料ID [{self.test_mat_id}] 筛选查询成功，但未找到批次记录")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="批次主数据管理",
        title="测试查询批次详情",
        description="验证批次详情查询功能",
        severity="normal",
        order=4,
        tags=["批次主数据", "详情查询"]
    )
    def test_query_batch_detail(self):
        """查询批次详情用例"""
        try:
            # 确保先执行基础查询获取测试数据
            if not self.test_batch_id:
                self.test_query_batch_page()
                
            # 如果仍然没有测试数据，跳过测试
            if not self.test_batch_id:
                self.logger.warning("未找到可用的批次ID，跳过详情查询测试")
                return
                
            api_path = self.get_api_path("INV-批次-批次查询详情(后台)服务")
            params, url = self.get_api_params(api_path)

            # 根据批次ID查询详情
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.test_batch_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-批次-批次查询详情(后台)服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言详情数据
            detail_data = response.get("data", {}).get("data", {})
            
            # 基础断言：验证详情数据结构
            assert isinstance(detail_data, dict), f"详情数据类型错误，expected: dict, actual: {type(detail_data)}"
            
            if detail_data:
                # 验证关键字段存在
                assert "id" in detail_data, "详情记录缺少批次ID字段"
                assert "code" in detail_data, "详情记录缺少批次编码字段"
                assert "matId" in detail_data, "详情记录缺少物料ID字段"
                
                # 验证ID匹配
                actual_id = detail_data.get("id")
                assert actual_id == self.test_batch_id, f"详情查询的批次ID不匹配，expected: {self.test_batch_id}, actual: {actual_id}"
                
                # 验证编码匹配
                actual_code = detail_data.get("code")
                assert actual_code == self.test_batch_code, f"详情查询的批次编码不匹配，expected: {self.test_batch_code}, actual: {actual_code}"
                
                self.logger.info(f"批次详情查询成功，批次ID: {self.test_batch_id}, 批次编码: {self.test_batch_code}")
            else:
                self.logger.info(f"批次详情查询成功，但未找到批次ID为 {self.test_batch_id} 的详情数据")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
