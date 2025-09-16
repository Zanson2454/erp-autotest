import allure
import pytest
import sys
from pathlib import Path
import time

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("库存余额管理")
class TestInventoryBalance(ScmInvBaseTest):
    """库存余额综合测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        
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
            # 仓库ID
            cls.invWhId = cls.inv_cache_data["org_info"]["inv_wh_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_wh_info") else None
            # 库区ID
            cls.invAreaId = cls.inv_cache_data["org_info"]["inv_area_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_area_info") else None
            # 仓位ID
            cls.invBinId = cls.inv_cache_data["org_info"]["inv_bin_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_info") else None
        
        cls.logger.info("库存余额综合测试类初始化完成")

    def get_current_inventory_balance(self):
        """获取当前库存余额"""
        try:
            result = self.db.query(
                sql="SELECT stk_qty FROM inv_stk_wh_ba WHERE com_org_id = %s AND mat_id = %s",
                params=[self.comOrgId, self.matId]
            )
            balance = result[0].get("stk_qty", 0) if result else 0
            self.logger.info(f"当前库存余额: {balance}")
            return balance
        except Exception as e:
            self.logger.error(f"获取当前库存余额失败: {str(e)}")
            return 0


    @case_decorator(
        story="库存余额管理",
        title="测试创建移动凭证增加库存",
        description="验证创建移动凭证增加库存数量",
        severity="blocker",
        order=1,
        tags=["库存余额", "移动凭证", "库存增加"]
    )
    def test_create_mobile_voucher_increase_inventory(self):
        """创建移动凭证增加库存用例"""
        try:
            # 记录操作前的库存余额
            pre_operation_balance = self.get_current_inventory_balance()
            self.logger.info(f"操作前库存余额: {pre_operation_balance}")
            
            # 使用pytest.importorskip动态导入，避免pytest收集移动凭证测试类
            mobile_voucher_module = pytest.importorskip('testcases.scm_inv.mobile_voucher.test_mobile_voucher_management')
            TestMobileVoucherManagement = mobile_voucher_module.TestMobileVoucherManagement
            
            # 创建移动凭证管理实例
            voucher_manager = TestMobileVoucherManagement()
            voucher_manager.setup_class()
            
            # 直接调用业务逻辑方法，避免pytest测试收集
            # 这些方法虽然有@case_decorator但在这里直接调用不会被pytest执行
            voucher_manager.test_query_material_batch_feature()
            voucher_manager.test_generate_batch_code() 
            voucher_manager.test_save_batch()
            voucher_manager.test_save_mobile_voucher()
            
            # 保存移动凭证数据到类变量
            TestInventoryBalance.mobile_voucher_id = voucher_manager.mobile_voucher_id
            TestInventoryBalance.mobile_voucher_code = voucher_manager.mobile_voucher_code
            
            # 验证移动凭证创建成功
            assert self.mobile_voucher_id, "移动凭证ID不能为空"
            assert self.mobile_voucher_code, "移动凭证编码不能为空"
            
            self.logger.info(f"移动凭证创建成功 - ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}")

            a.text(f"移动凭证ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}", "移动凭证信息")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额管理",
        title="测试验证库存余额变化",
        description="验证移动凭证创建后库存余额的正确变化",
        severity="blocker",
        order=2,
        tags=["库存余额", "余额验证", "数据一致性"]
    )
    def test_verify_inventory_balance_change(self):
        """验证库存余额变化用例"""
        try:
            # 获取当前库存余额（移动凭证已创建）
            current_balance = self.get_current_inventory_balance()
            self.logger.info(f"当前库存余额: {current_balance}")
            
            # 验证移动凭证已创建
            assert self.mobile_voucher_id, "移动凭证ID不能为空，请先执行test_create_mobile_voucher_increase_inventory"
            assert self.mobile_voucher_code, "移动凭证编码不能为空，请先执行test_create_mobile_voucher_increase_inventory"
            
            # 验证库存有增加（至少大于0）
            assert current_balance > 0, f"库存余额应该大于0，当前余额: {current_balance}"
            
            a.text(f"库存余额验证 - 当前余额: {current_balance}, 移动凭证ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}", "库存余额变化验证")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额管理",
        title="测试物料库存余额查询",
        description="验证物料库存余额查询分页功能",
        severity="critical",
        order=3,
        tags=["库存余额", "查询", "分页"]
    )
    def test_query_material_stock_balance(self):
        """物料库存余额查询用例"""
        try:
            # 1. 获取数据库中的实际库存余额作为基准值
            db_balance = self.get_current_inventory_balance()
            
            # 2. API调用
            api_path = self.get_api_path("INV-库存余额-物料库存余额查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            
            # 构造查询条件
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "comOrgId": {
                                "operator": "EQ",
                                "value": {"id": self.comOrgId}
                            },
                            "matId": {
                                "operator": "EQ", 
                                "value": {"id": self.matId}
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "stkQty", "type": "DECIMAL"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 业务断言
            response_data = response.get("data", {}).get("data", {})
            data_list = response_data.get("data", [])
            
            # 断言查询结果存在
            assert len(data_list) > 0, f"查询结果数据列表不能为空，实际长度: {len(data_list)}"
            
            # 获取API返回的库存数量并验证一致性
            api_stk_qty = data_list[0].get("stkQty", 0)
            assert api_stk_qty == db_balance, f"API返回的库存数量({api_stk_qty})与数据库查询结果({db_balance})不一致"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"库存数量一致性验证 - API: {api_stk_qty}, 数据库: {db_balance}", "库存查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

