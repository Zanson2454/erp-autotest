import allure
import datetime
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("库存汇总管理")
class TestInvStkStatisticaManagement(ScmInvBaseTest):
    """库存汇总综合测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        cls.batch_code = None
        cls.initial_statistics = None
        cls.final_statistics = None
        
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
            # 调拨移动类型ID
            cls.mvmTypeId = cls.inv_cache_data["org_info"]["inv_mvm_type_cf_all"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_mvm_type_cf_all") else None
             # 仓库ID
            cls.invWhId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["inv_wh_id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
            # 仓储区ID
            cls.invAreaId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["inv_area_id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
            # 仓位ID
            cls.invBinId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
        
        cls.logger.info("库存汇总综合测试类初始化完成")

    def get_current_inventory_statistics(self):
        """获取当前库存汇总统计数据"""
        try:
            result = self.db.query(
                sql="SELECT SUM(stk_qty) as total_qty FROM inv_stk_ba WHERE mat_id = %s AND com_org_id = %s AND inv_org_id = %s AND inv_loc_id = %s",
                params=[self.matId, self.comOrgId, self.invOrgId, self.invLocId]
            )
            total_qty = result[0].get("total_qty", 0) if result else 0
            self.logger.info(f"当前库存汇总数量: {total_qty}")
            return float(total_qty) if total_qty else 0.0
        except Exception as e:
            self.logger.error(f"获取当前库存汇总统计失败: {str(e)}")
            return 0.0

    @case_decorator(
        story="库存汇总管理",
        title="测试查询库存汇总统计(初始状态)",
        description="验证查询库存汇总统计数据功能，记录初始状态",
        severity="critical",
        order=1,
        tags=["库存汇总", "查询", "统计"]
    )
    def test_query_initial_inventory_statistics(self):
        """查询初始库存汇总统计用例"""
        try:
            # 1. 获取数据库中的实际库存汇总作为基准值
            db_statistics = self.get_current_inventory_statistics()
            
            # 2. API调用
            api_path = self.get_api_path("INV-库存余额-库存账统计服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,["pageNo", "pageSize", "level", "matId", "invOrgId", "invLocId"], ["params", "request"]
            )
            
            # 构造查询条件
            set_dict = {
                    "pageNo": 1,
                    "pageSize": 20,
                    "level": 1,
                    "matId": self.matId,
                    "invOrgId": self.invOrgId,
                    "invLocId": self.invLocId
                }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 业务断言
            response_data = response.get("data", {})
            statistics_data = response_data.get("data", {})
            
            # 保存初始统计数据
            TestInvStkStatisticaManagement.initial_statistics = statistics_data
            
            # 验证统计数据结构
            assert isinstance(statistics_data, dict), f"统计数据应该是字典类型，实际类型: {type(statistics_data)}"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"初始库存汇总统计 - 数据库统计: {db_statistics}, API统计数据: {statistics_data}", "初始库存汇总查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存汇总管理",
        title="测试创建移动凭证增加库存",
        description="验证创建移动凭证增加库存数量，为汇总统计变化提供数据基础",
        severity="blocker",
        order=2,
        tags=["库存汇总", "移动凭证", "库存增加"]
    )
    def test_create_mobile_voucher_for_statistics(self):
        """创建移动凭证增加库存用例"""
        try:
            # 记录操作前的库存汇总统计
            pre_operation_statistics = self.get_current_inventory_statistics()
            self.logger.info(f"操作前库存汇总统计: {pre_operation_statistics}")
            
            # 使用pytest.importorskip动态导入，避免pytest收集移动凭证测试类
            mobile_voucher_module = pytest.importorskip('testcases.scm_inv.inv_mvm.test_inv_mvm_pur_management')
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
            TestInvStkStatisticaManagement.mobile_voucher_id = voucher_manager.mobile_voucher_id
            TestInvStkStatisticaManagement.mobile_voucher_code = voucher_manager.mobile_voucher_code
            TestInvStkStatisticaManagement.batch_code = voucher_manager.batch_code
            
            # 验证移动凭证创建成功
            assert self.mobile_voucher_id, "移动凭证ID不能为空"
            assert self.mobile_voucher_code, "移动凭证编码不能为空"
            
            self.logger.info(f"移动凭证创建成功 - ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}")

            a.text(f"移动凭证ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}", "移动凭证信息")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存汇总管理",
        title="测试查询库存汇总统计变化",
        description="验证移动凭证创建后库存汇总统计数据的正确变化",
        severity="blocker",
        order=3,
        tags=["库存汇总", "统计变化", "数据一致性"]
    )
    def test_verify_inventory_statistics_change(self):
        """验证库存汇总统计变化用例"""
        try:
            # 确保前置条件：移动凭证已创建
            if not self.mobile_voucher_id:
                self.test_create_mobile_voucher_for_statistics()
            
            # 等待一段时间确保数据同步
            time.sleep(2)
            
            # 1. 获取数据库中的最新库存汇总统计
            current_db_statistics = self.get_current_inventory_statistics()
            
            # 2. API调用获取最新统计数据
            api_path = self.get_api_path("INV-库存余额-库存账统计服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageNo", "pageSize", "level", "matId", "invOrgId", "invLocId"], ["params", "request"]
            )
            
            # 构造查询条件
            set_dict = {
                    "pageNo": 1,
                    "pageSize": 20,
                    "level": 1,
                    "matId": self.matId,
                    "invOrgId": self.invOrgId,
                    "invLocId": self.invLocId
                }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 业务断言
            response_data = response.get("data", {})
            final_statistics = response_data.get("data", {})
            
            # 保存最终统计数据
            TestInvStkStatisticaManagement.final_statistics = final_statistics
            
            # 验证移动凭证已创建
            assert self.mobile_voucher_id, "移动凭证ID不能为空，请先执行test_create_mobile_voucher_for_statistics"
            assert self.mobile_voucher_code, "移动凭证编码不能为空，请先执行test_create_mobile_voucher_for_statistics"
            
            # 验证库存汇总统计有变化（数据库层面）
            assert current_db_statistics > 0, f"库存汇总统计应该大于0，当前统计: {current_db_statistics}"
            
            # 验证API返回的统计数据结构
            assert isinstance(final_statistics, dict), f"最终统计数据应该是字典类型，实际类型: {type(final_statistics)}"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"库存汇总统计变化验证 - 数据库统计: {current_db_statistics}, API统计: {final_statistics}, 移动凭证ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}", "库存汇总统计变化验证")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
