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
@allure.feature("移动凭证明细管理")
class TestMobileVoucherDetailsManagement(ScmInvBaseTest):
    """移动凭证明细管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        cls.test_voucher_code = None  # 从第一个查询结果中提取的移动凭证编码
        cls.test_mat_id = None        # 从第一个查询结果中提取的物料ID
        
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
            # 移动类型ID
            cls.mvmTypeId = cls.inv_cache_data["org_info"]["inv_mvm_type_cf_pur"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_mvm_type_cf_pur") else None
        
        cls.logger.info("移动凭证明细管理测试类初始化完成")
    @case_decorator(
        story="移动凭证明细管理",
        title="测试查询移动凭证明细分页",
        description="验证移动凭证明细分页查询功能",
        severity="normal",
        order=1,
        smoke=True,
        tags=["移动凭证明细", "分页查询"]
    )
    def test_query_mobile_voucher_details_page(self):
        """查询移动凭证明细分页用例"""
        try:
            api_path = self.get_api_path("INV-移动凭证明细-分页查询服务")
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
                    {"name": "mvmDocId", "type": "OBJECT"},
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"},
                    {"name": "invWhId", "type": "OBJECT"},
                    {"name": "invAreaId", "type": "OBJECT"},
                    {"name": "invBinId", "type": "OBJECT"},
                    {"name": "batchId", "type": "OBJECT"},
                    {"name": "invTypeId", "type": "OBJECT"},
                    {"name": "mvmPosNeg", "type": "SELECT"},
                    {"name": "spcStkTypeId", "type": "OBJECT"},
                    {"name": "docCode", "type": "TEXT"},
                    {"name": "subDocCode", "type": "TEXT"},
                    {"name": "upDocCode", "type": "TEXT"},
                    {"name": "subUpDocCode", "type": "TEXT"},
                    {"name": "sourceType", "type": "SELECT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
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
                assert "mvmDocId" in first_item, "明细记录缺少移动凭证ID字段"
                assert "matId" in first_item, "明细记录缺少物料ID字段"
                
                # 提取第一条数据的关键信息用于后续测试
                mvm_doc_info = first_item.get("mvmDocId", {})
                if isinstance(mvm_doc_info, dict) and mvm_doc_info.get("code"):
                    self.test_voucher_code = mvm_doc_info.get("code")
                    self.logger.info(f"提取到移动凭证编码: {self.test_voucher_code}")
                
                mat_info = first_item.get("matId", {})
                if isinstance(mat_info, dict) and mat_info.get("id"):
                    self.test_mat_id = mat_info.get("id")
                    self.logger.info(f"提取到物料ID: {self.test_mat_id}")
                
                self.logger.info(f"分页查询成功，总记录数: {total}, 当前页记录数: {len(data_list)}")
            else:
                self.logger.info("分页查询成功，但当前无明细数据")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证明细管理",
        title="测试根据移动凭证编码查询明细",
        description="验证根据移动凭证编码筛选查询明细功能",
        severity="normal",
        order=2,
        tags=["移动凭证明细", "编码筛选"]
    )
    def test_query_mobile_voucher_details_by_code(self):
        """根据移动凭证编码查询明细用例"""
        try:
            # 确保先执行基础查询获取测试数据
            if not self.test_voucher_code:
                self.test_query_mobile_voucher_details_page()
                
            # 如果仍然没有测试数据，跳过测试
            if not self.test_voucher_code:
                self.logger.warning("未找到可用的移动凭证编码，跳过编码筛选测试")
                return
                
            api_path = self.get_api_path("INV-移动凭证明细-分页查询服务")
            params, url = self.get_api_params(api_path)

            # 根据移动凭证编码筛选明细
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
                            "mvmDocId": {
                                "operator": "EQ",
                                "value": {"code": self.test_voucher_code}
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "mvmDocId", "type": "OBJECT"},
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"},
                    {"name": "invWhId", "type": "OBJECT"},
                    {"name": "invAreaId", "type": "OBJECT"},
                    {"name": "invBinId", "type": "OBJECT"},
                    {"name": "batchId", "type": "OBJECT"},
                    {"name": "invTypeId", "type": "OBJECT"},
                    {"name": "mvmPosNeg", "type": "SELECT"},
                    {"name": "spcStkTypeId", "type": "OBJECT"},
                    {"name": "docCode", "type": "TEXT"},
                    {"name": "subDocCode", "type": "TEXT"},
                    {"name": "upDocCode", "type": "TEXT"},
                    {"name": "subUpDocCode", "type": "TEXT"},
                    {"name": "sourceType", "type": "SELECT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 断言筛选结果
            page_data = response.get("data", {}).get("data", {})
            data_list = page_data.get("data", [])
            total = page_data.get("total", 0)
            
            # 基础断言：验证查询结果结构
            assert total >= 0, f"总记录数不能为负数，actual: {total}"
            assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
            if data_list:
                # 验证所有记录都属于指定的移动凭证编码
                for item in data_list:
                    mvm_doc_info = item.get("mvmDocId", {})
                    if isinstance(mvm_doc_info, dict):
                        actual_code = mvm_doc_info.get("code")
                        assert actual_code == self.test_voucher_code, f"筛选结果包含其他凭证编码的明细: {actual_code}"
                
                self.logger.info(f"根据移动凭证编码 [{self.test_voucher_code}] 筛选查询成功，找到 {len(data_list)} 条明细记录")
            else:
                self.logger.info(f"根据移动凭证编码 [{self.test_voucher_code}] 筛选查询成功，但未找到明细记录")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证明细管理",
        title="测试根据物料ID查询明细",
        description="验证根据物料ID筛选查询明细功能",
        severity="normal",
        order=3,
        tags=["移动凭证明细", "物料筛选"]
    )
    def test_query_mobile_voucher_details_by_material_id(self):
        """根据物料ID查询明细用例"""
        try:
            # 确保先执行基础查询获取测试数据
            if not self.test_mat_id:
                self.test_query_mobile_voucher_details_page()
                
            # 如果仍然没有测试数据，跳过测试
            if not self.test_mat_id:
                self.logger.warning("未找到可用的物料ID，跳过物料筛选测试")
                return
                
            api_path = self.get_api_path("INV-移动凭证明细-分页查询服务")
            params, url = self.get_api_params(api_path)

            # 根据物料ID筛选明细
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
                    {"name": "mvmDocId", "type": "OBJECT"},
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"},
                    {"name": "mvmPosNeg", "type": "SELECT"},
                    {"name": "sourceType", "type": "SELECT"},
                    {"name": "docCode", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
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
                        assert actual_mat_id == self.test_mat_id, f"筛选结果包含其他物料ID的明细: {actual_mat_id}"
                
                self.logger.info(f"根据物料ID [{self.test_mat_id}] 筛选查询成功，找到 {len(data_list)} 条明细记录")
            else:
                self.logger.info(f"根据物料ID [{self.test_mat_id}] 筛选查询成功，但未找到明细记录")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

