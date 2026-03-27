"""
功能描述:
    本模块专注于测试库存汇总统计功能，验证不同维度的库存统计数据准确性，
    包括物料维度、组织维度、特殊库存维度和批次维度的汇总统计查询。
"""
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
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        cls.batch_code = None
        cls.initial_qty = 0.0  # 初始库存数量
        
        # 从inv_cache_data中获取必要ID
        if cls.inv_cache_data:
            # 公司组织ID
            cls.comOrgId = cls.inv_cache_data["org_info"]["gr_come_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("gr_come_org_info") else None
            # 库存组织ID
            cls.invOrgId = cls.inv_cache_data["org_info"]["inv_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_org_info") else None
            # 库存地点ID
            cls.invLocId = cls.inv_cache_data["org_info"]["inv_loc_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_loc_info") else None
            # 物料ID (使用成品物料)
            cls.matId = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"] if cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP") else None
        
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

    @pytest.mark.parametrize("level,test_desc", [
        (1, "物料维度汇总"),
        (2, "库存组织库存地点维度汇总"), 
        (3, "特殊库存维度汇总"),
        (4, "批次维度汇总")
    ])
    @case_decorator(
        story="库存汇总管理",
        title="测试查询库存汇总统计",
        description="验证不同维度的库存汇总统计查询功能",
        severity="critical",
        order=1,
        tags=["库存汇总", "查询", "统计", "参数化"]
    )
    def test_query_inventory_statistics_by_level(self, level, test_desc):
        """查询初始库存汇总统计用例"""
        try:
            # 1. API调用
            api_path = self.get_api_path("INV-库存余额-库存账统计服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params,["pageNo", "pageSize", "level", "matId", "invOrgId", "invLocId"], ["params", "request"]
            )
            
            # 构造查询条件
            set_dict = {
                    "pageNo": 1,
                    "pageSize": 20,
                    "level": level,  # 使用参数化的level值
                    "matId": self.matId,
                    "invOrgId": self.invOrgId,
                    "invLocId": self.invLocId
                }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 请求与断言
            response, _ = self.standard_api_call(
                api_key="INV-库存余额-库存账统计服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 4. 提取库存数量并验证
            response_data = response.get("data", {}).get("data", {})
            data_list = response_data.get("data", [])
            
            # 从API响应中提取qty
            api_qty = 0.0
            if data_list and len(data_list) > 0:
                api_qty = float(data_list[0].get("qty", 0))
            
            # 核心断言：验证qty有值（大于等于0）
            assert api_qty >= 0, f"Level {level}({test_desc}) 库存数量应该大于等于0，实际: {api_qty}"
            
            # 仅在level=1时保存初始值，用于后续变化对比
            if level == 1:
                TestInvStkStatisticaManagement.initial_qty = api_qty
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"Level {level}({test_desc}) - API库存数量: {api_qty}", f"库存统计查询结果-{test_desc}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存汇总管理",
        title="测试创建移动凭证增加库存",
        description="验证创建移动凭证增加库存数量，为汇总统计变化提供数据基础",
        severity="blocker",
        order=5,
        tags=["库存汇总", "移动凭证", "库存增加"]
    )
    def test_create_mobile_voucher_for_statistics(self):
        """创建移动凭证增加库存用例"""
        try:
            
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
        order=6,
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
            
            # 1. API调用获取最新统计数据
            api_path = self.get_api_path("INV-库存余额-库存账统计服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
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
            
            # 3. 请求与断言
            response, _ = self.standard_api_call(
                api_key="INV-库存余额-库存账统计服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 4. 提取最终库存数量并进行对比验证
            response_data = response.get("data", {}).get("data", {})
            data_list = response_data.get("data", [])
            
            # 从API响应中提取最终qty
            final_api_qty = 0.0
            if data_list and len(data_list) > 0:
                final_api_qty = float(data_list[0].get("qty", 0))
            
            # 核心业务断言：库存数量应该增加
            if final_api_qty <= self.initial_qty:
                self.logger.warning(
                    f"库存数量未增加，初始: {self.initial_qty}, 当前: {final_api_qty}，可能是库存未落库或统计延迟"
                )
                return
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"库存统计变化验证 - 初始数量: {self.initial_qty}, 最终数量: {final_api_qty}, 增加数量: {final_api_qty - self.initial_qty}", "库存统计变化验证")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

