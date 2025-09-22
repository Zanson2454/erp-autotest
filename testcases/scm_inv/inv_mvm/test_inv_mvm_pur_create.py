"""
移动凭证创建器测试用例 - 采购入库专项测试
专注验证采购入库移动凭证自身创建功能，不涉及库存余额变化
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv.inv_mvm.inv_mvm_create import MobileVoucherCreator
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("移动凭证创建器-采购入库")
class TestMobileVoucherCreator(MobileVoucherCreator):
    """移动凭证创建器测试类 - 采购入库专项"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("移动凭证创建器-采购入库测试类初始化完成")
    

    @case_decorator(
        story="移动凭证创建器",
        title="测试采购入库-基础参数(库存组织+地点+5数量)",
        description="验证只传库存组织、库存地点，5个数量的采购入库移动凭证创建",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["移动凭证", "采购入库", "基础参数"]
    )
    def test_create_purchase_voucher_basic(self):
        """采购入库-基础参数测试"""
        try:
            # 1. 创建采购入库移动凭证（只传基础参数）
            voucher_info = self.create_purchase_voucher(
                qty=5,
                remark="自动化测试-基础参数采购入库"
            )
            
            # 2. 保存凭证ID
            voucher_id = voucher_info["mobile_voucher_id"]
            
            # 3. 验证凭证创建成功
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_id"], "!=", None, "采购入库移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_code"], "!=", None, "采购入库移动凭证编码不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "purchase", "凭证类型应该是采购")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 5, "总数量应该是5")
            self.assert_util.assert_by_operator(voucher_info["item_count"], "=", 1, "物料行数应该是1")
            
            # 4. 验证凭证在列表中存在
            voucher_detail = self.verify_voucher_in_list(voucher_id)
            
            self.logger.info(f"基础参数采购入库移动凭证创建成功 - ID: {voucher_info['mobile_voucher_id']}")
            
            # 5. 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            a.text(f"基础参数测试成功 - 凭证ID: {voucher_info['mobile_voucher_id']}, 数量: 5", "测试结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证创建器",
        title="测试采购入库-完整参数(公司组织+库存组织+库存地点+仓库+区域+仓位+10数量)",
        description="验证传完整参数（包括组织信息和仓库信息），10个数量的采购入库移动凭证创建",
        severity="blocker",
        order=2,
        tags=["移动凭证", "采购入库", "完整参数"]
    )
    def test_create_purchase_voucher_full_warehouse(self):
        """采购入库-完整参数测试"""
        try:
            # 1. 创建采购入库移动凭证（传完整参数）
            voucher_info = self.create_purchase_voucher(
                qty=10,
                comOrgId=self.comOrgId,      # 公司组织ID
                invOrgId=self.invOrgId,      # 库存组织ID  
                invLocId=self.invLocId,      # 库存地点ID
                invWhId=self.invWhId,        # 仓库ID
                invAreaId=self.invAreaId,    # 仓储区ID
                invBinId=self.invBinId,      # 仓位ID
                remark="自动化测试-完整参数采购入库"
            )
            
            # 2. 保存凭证ID
            voucher_id = voucher_info["mobile_voucher_id"]
            
            # 3. 验证凭证创建成功
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_id"], "!=", None, "采购入库移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_code"], "!=", None, "采购入库移动凭证编码不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "purchase", "凭证类型应该是采购")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 10, "总数量应该是10")
            self.assert_util.assert_by_operator(voucher_info["item_count"], "=", 1, "物料行数应该是1")
            
            # 4. 验证凭证在列表中存在
            voucher_detail = self.verify_voucher_in_list(voucher_id)
            
            self.logger.info(f"完整仓库参数采购入库移动凭证创建成功 - ID: {voucher_info['mobile_voucher_id']}")
            
            # 5. 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            a.text(f"完整参数测试成功 - 凭证ID: {voucher_info['mobile_voucher_id']}, 数量: 10", "测试结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证创建器",
        title="测试采购入库-多物料行(2个物料+完整参数+10数量)",
        description="验证传2个物料行，完整仓库参数，10个数量的采购入库移动凭证创建",
        severity="critical",
        order=3,
        tags=["移动凭证", "采购入库", "多物料行"]
    )
    def test_create_purchase_voucher_multi_materials(self):
        """采购入库-多物料行测试"""
        try:
            # 1. 准备多物料行数据
            mat_list = self.inv_cache_data["mat_info"]["mat_md"]["FINP"]
            if len(mat_list) < 2:
                # 如果只有一个物料，就用同一个物料创建两行
                mat_items = [
                    {"mat_id": mat_list[0]["id"], "qty": 6},  # 第一行6个
                    {"mat_id": mat_list[0]["id"], "qty": 4}   # 第二行4个（同一物料）
                ]
            else:
                # 如果有多个物料，使用不同物料
                mat_items = [
                    {"mat_id": mat_list[0]["id"], "qty": 6},  # 第一个物料6个
                    {"mat_id": mat_list[1]["id"], "qty": 4}   # 第二个物料4个
                ]
            
            # 2. 创建多物料行采购入库移动凭证
            voucher_info = self.create_purchase_voucher(
                mat_items=mat_items,
                invWhId=self.invWhId,
                invAreaId=self.invAreaId,
                invBinId=self.invBinId,
                remark="自动化测试-多物料行采购入库"
            )
            
            # 3. 保存凭证ID
            voucher_id = voucher_info["mobile_voucher_id"]
            
            # 4. 验证凭证创建成功
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_id"], "!=", None, "多物料行采购入库移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["mobile_voucher_code"], "!=", None, "多物料行采购入库移动凭证编码不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "purchase", "凭证类型应该是采购")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 10, "总数量应该是10")
            self.assert_util.assert_by_operator(voucher_info["item_count"], "=", 2, "物料行数应该是2")
            
            # 5. 验证凭证在列表中存在
            voucher_detail = self.verify_voucher_in_list(voucher_id)
            
            self.logger.info(f"多物料行采购入库移动凭证创建成功 - ID: {voucher_info['mobile_voucher_id']}, 物料行数: 2")
            
            # 6. 报告记录
            a.json(mat_items, "多物料行数据")
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            a.text(f"多物料行测试成功 - 凭证ID: {voucher_info['mobile_voucher_id']}, 物料行数: 2, 总数量: 10", "测试结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
