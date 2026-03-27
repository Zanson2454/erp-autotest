"""移动凭证创建器测试用例 - 调拨专项测试"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv.inv_mvm.inv_mvm_create import MobileVoucherCreator
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("移动凭证创建器-调拨")
class TestMobileVoucherTransferCreator(MobileVoucherCreator):
    """移动凭证创建器测试类 - 调拨专项"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.available_batch_id = None
        cls.default_mat_id = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
        
        # 查询可用批次用于调拨出库
        try:
            sql = """
                SELECT batch_id FROM inv_stk_ba 
                WHERE mat_id = %s AND com_org_id = %s AND inv_org_id = %s 
                AND inv_loc_id = %s AND inv_wh_id = %s AND inv_area_id = %s 
                AND inv_bin_id = %s AND stk_qty > 100
                LIMIT 1
            """
            result = cls.db.query(sql, params=[
                cls.default_mat_id, cls.comOrgId, cls.invOrgId, cls.invLocId,
                cls.invWhId, cls.invAreaId, cls.invBinId
            ])
            if result:
                cls.available_batch_id = result[0].get("batch_id")
        except Exception as e:
            cls.logger.warning(f"查询可用批次失败: {str(e)}")

    @case_decorator(
        story="移动凭证创建器",
        title="测试调拨-跨仓位调拨",
        description="验证从收货区调拨到发货区的跨仓位调拨移动凭证创建，包含完整的出入库仓位参数和批次",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["移动凭证", "调拨", "跨仓位"]
    )
    def test_create_transfer_voucher_specific_warehouse(self):
        """调拨-指定完整仓位和批次测试"""
        try:
            if not self.available_batch_id:
                pytest.skip("没有可用批次，跳过调拨测试")
            
            # 准备调拨参数
            custom_to_batch = f"TRANSFER_{self.mock_util.get_timestamp()}"
            send_wh_info = self.inv_cache_data["org_info"]["inv_bin_send_md"][0]
            
            # 创建调拨移动凭证
            voucher_info = self.create_transfer_voucher(
                mat_id=self.default_mat_id,
                qty=1,
                from_batch_id=self.available_batch_id,
                to_batch_code=custom_to_batch,
                from_wh_info={
                    "invWhId": self.invWhId,
                    "invAreaId": self.invAreaId,
                    "invBinId": self.invBinId
                },
                to_wh_info={
                    "invWhId": send_wh_info["inv_wh_id"],
                    "invAreaId": send_wh_info["inv_area_id"], 
                    "invBinId": send_wh_info["id"]
                },
                remark="自动化测试-收货区调拨到发货区"
            )
            
            # 验证凭证创建成功
            voucher_id = voucher_info["mobile_voucher_id"]
            self.assert_util.assert_by_operator(voucher_id, "!=", None, "移动凭证ID不能为空")
            self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "transfer", "凭证类型应该是调拨")
            self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 1, "总数量应该是1")
            
            # 验证批次信息
            self.assert_util.assert_by_operator(voucher_info["from_batch_id"], "=", self.available_batch_id, "出库批次ID应该匹配")
            self.assert_util.assert_by_operator(voucher_info["to_batch_code"], "=", custom_to_batch, "入库批次编码应该匹配")
            
            # 验证凭证在列表中存在
            self.verify_voucher_in_list(voucher_id)
            
            # 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            a.text(f"出库仓位: 收货区 - {self.invAreaId}:{self.invBinId}", "仓位信息")
            a.text(f"入库仓位: 发货区 - {send_wh_info['inv_area_id']}:{send_wh_info['id']}", "仓位信息")
            a.text(f"指定出库批次ID: {self.available_batch_id}", "批次信息")
            a.text(f"指定入库批次编码: {custom_to_batch}", "批次信息")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
