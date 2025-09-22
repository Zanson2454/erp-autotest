"""移动凭证创建器测试用例 - 销售出库专项测试"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv.inv_mvm.inv_mvm_create import MobileVoucherCreator
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("移动凭证创建器-销售出库")
class TestMobileVoucherSaleCreator(MobileVoucherCreator):
    """移动凭证创建器测试类 - 销售出库专项"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.available_batch_id = None
        
        # 查询可用批次用于销售出库
        try:
            default_mat_id = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            sql = """
                SELECT batch_id 
                FROM inv_stk_ba 
                WHERE mat_id = %s 
                  AND com_org_id = %s 
                  AND inv_org_id = %s 
                  AND inv_loc_id = %s 
                  AND stk_qty > 100
                LIMIT 1
            """
            result = cls.db.query(sql, params=[
                default_mat_id, cls.comOrgId, cls.invOrgId, cls.invLocId
            ])
            if result:
                cls.available_batch_id = result[0].get("batch_id")
        except Exception as e:
            cls.logger.warning(f"查询可用批次失败: {str(e)}")

    @case_decorator(
        story="移动凭证创建器",
        title="测试销售出库-系统自动分配仓位",
        description="验证不指定具体仓位，让系统自动分配可用库存仓位的销售出库移动凭证创建",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["移动凭证", "销售出库", "自动分配"]
    )
    def test_create_sale_voucher_auto_allocation(self):
        """销售出库-系统自动分配仓位测试"""
        try:
            if not self.available_batch_id:
                pytest.skip("没有可用批次，跳过销售出库测试")
            
            # 创建销售出库移动凭证
            default_mat_id = self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            voucher_info = self.create_sale_voucher(
                mat_id=default_mat_id,
                qty=1,
                comOrgId=self.comOrgId,
                invOrgId=self.invOrgId,
                invLocId=self.invLocId,
                batch_id=self.available_batch_id,
                remark="自动化测试-自动分配销售出库"
            )
            
            # 验证凭证创建成功
            voucher_id = voucher_info["mobile_voucher_id"]
            self.assert_util.assert_by_operator(voucher_id, "!=", None, "移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "sale", "凭证类型应该是销售")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 1, "总数量应该是1")
            
            # 验证凭证在列表中存在
            self.verify_voucher_in_list(voucher_id)
            
            # 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证创建器",
        title="测试销售出库-指定完整仓位参数",
        description="验证指定完整仓位参数（仓库+仓储区+仓位），基于精确库存查询的销售出库移动凭证创建",
        severity="critical",
        order=2,
        tags=["移动凭证", "销售出库", "精确仓位"]
    )
    def test_create_sale_voucher_specific_warehouse(self):
        """销售出库-指定完整仓位测试"""
        try:
            # 查询指定仓位的库存
            default_mat_id = self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            sql = """
                SELECT stk_qty, batch_id FROM inv_stk_ba 
                WHERE mat_id = %s AND com_org_id = %s AND inv_org_id = %s 
                AND inv_loc_id = %s AND inv_wh_id = %s AND inv_area_id = %s 
                AND inv_bin_id = %s AND stk_qty > 100
            """
            result = self.db.query(sql, params=[
                default_mat_id, self.comOrgId, self.invOrgId, self.invLocId,
                self.invWhId, self.invAreaId, self.invBinId
            ])
            
            if not result:
                pytest.skip("未找到具体仓位库存，跳过精确仓位测试")
            
            warehouse_info = result[0]
            available_qty = float(warehouse_info.get("stk_qty", 0))
            if available_qty < 1:
                pytest.skip(f"仓位库存不足({available_qty})，跳过精确仓位测试")
            
            # 创建销售出库移动凭证
            voucher_info = self.create_sale_voucher(
                mat_id=default_mat_id,
                qty=1,
                comOrgId=self.comOrgId,
                invOrgId=self.invOrgId,
                invLocId=self.invLocId,
                invWhId=self.invWhId,
                invAreaId=self.invAreaId,
                invBinId=self.invBinId,
                batch_id=warehouse_info.get("batch_id"),
                remark="自动化测试-指定仓位销售出库"
            )
            
            # 验证凭证创建成功
            voucher_id = voucher_info["mobile_voucher_id"]
            self.assert_util.assert_by_operator(voucher_id, "!=", None, "移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "sale", "凭证类型应该是销售")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 1, "总数量应该是1")
            
            # 验证凭证在列表中存在
            self.verify_voucher_in_list(voucher_id)
            
            # 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证创建器",
        title="测试销售出库-多物料行(2个物料行+指定仓位+2数量)",
        description="验证传2个物料行（相同物料、相同批次），指定仓位，2个数量的销售出库移动凭证创建",
        severity="critical",
        order=3,
        tags=["移动凭证", "销售出库", "多物料行"]
    )
    def test_create_sale_voucher_multi_materials(self):
        """销售出库-多物料行测试"""
        try:
            # 查询指定仓位的多个批次库存
            default_mat_id = self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            sql = """
                SELECT stk_qty, batch_id FROM inv_stk_ba 
                WHERE mat_id = %s AND com_org_id = %s AND inv_org_id = %s 
                AND inv_loc_id = %s AND inv_wh_id = %s AND inv_area_id = %s 
                AND inv_bin_id = %s AND stk_qty > 100
                LIMIT 2
            """
            batch_result = self.db.query(sql, params=[
                default_mat_id, self.comOrgId, self.invOrgId, self.invLocId,
                self.invWhId, self.invAreaId, self.invBinId
            ])
            
            if not batch_result:
                pytest.skip("未找到具体仓位库存，跳过多物料行测试")
            
            if len(batch_result) < 2:
                pytest.skip(f"只找到{len(batch_result)}个批次，无法进行多物料行测试")
            
            # 准备多物料行数据
            mat_items = [
                {"mat_id": default_mat_id, "qty": 1, "batch_id": batch_result[0]["batch_id"]},
                {"mat_id": default_mat_id, "qty": 1, "batch_id": batch_result[1]["batch_id"]}
            ]
            
            # 创建多物料行销售出库移动凭证
            voucher_info = self.create_sale_voucher(
                mat_items=mat_items,
                comOrgId=self.comOrgId,
                invOrgId=self.invOrgId,
                invLocId=self.invLocId,
                invWhId=self.invWhId,
                invAreaId=self.invAreaId,
                invBinId=self.invBinId,
                remark="自动化测试-多物料行销售出库"
            )
            
            # 验证凭证创建成功
            voucher_id = voucher_info["mobile_voucher_id"]
            self.assert_util.assert_by_operator(voucher_id, "!=", None, "移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "sale", "凭证类型应该是销售")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 2, "总数量应该是2")
            self.assert_util.assert_by_operator(voucher_info["item_count"], "=", 2, "物料行数应该是2")
            
            # 验证凭证在列表中存在
            self.verify_voucher_in_list(voucher_id)
            
            # 报告记录
            a.json(mat_items, "多物料行数据")
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
