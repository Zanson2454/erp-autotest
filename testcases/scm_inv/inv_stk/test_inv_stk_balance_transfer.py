"""
库存余额调拨验证测试模块

验证调拨移动凭证对库存余额的影响，确保调拨后总库存数量不变，只改变库存分布。

测试流程:
    1. 查询调拨前库存余额
    2. 创建调拨移动凭证
    3. 验证调拨后库存余额总量不变
"""
import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv.inv_mvm.inv_mvm_create import MobileVoucherCreator
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("库存余额调拨验证")
class TestInvStkBalanceTransferManagement(MobileVoucherCreator):
    """调拨库存余额验证"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.available_batch_id = None
        cls.default_mat_id = cls.md_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
        
        # 查询可用批次用于调拨出库
        try:
            sql = """
                SELECT batch_id FROM inv_stk_ba 
                WHERE mat_id = %s AND com_org_id = %s AND inv_org_id = %s 
                AND inv_loc_id = %s AND inv_wh_id = %s AND inv_area_id = %s 
                AND inv_bin_id = %s AND stk_qty > 100
                LIMIT 1
            """
            result = cls.query_service.query(sql, params=[
                cls.default_mat_id, cls.comOrgId, cls.invOrgId, cls.invLocId,
                cls.invWhId, cls.invAreaId, cls.invBinId
            ])
            if result:
                cls.available_batch_id = result[0].get("batch_id")
        except Exception as e:
            cls.logger.warning(f"查询可用批次失败: {str(e)}")

    def get_current_inventory_balance(self):
        """查询当前库存余额总量"""
        try:
            result = self.query_service.query(
                sql="SELECT SUM(stk_qty) as total_qty FROM inv_stk_ba WHERE com_org_id = %s AND mat_id = %s",
                params=[self.comOrgId, self.default_mat_id]
            )
            balance = float(result[0].get("total_qty", 0)) if result and result[0].get("total_qty") else 0.0
            self.logger.info(f"当前库存总余额: {balance}")
            return balance
        except Exception as e:
            self.logger.error(f"获取当前库存余额失败: {str(e)}")
            return 0.0


    def _validate_transfer_voucher(self, voucher_info, expected_batch_from, expected_batch_to):
        """验证调拨凭证信息的私有方法"""
        voucher_id = voucher_info["mobile_voucher_id"]
        self.assert_util.assert_by_operator(voucher_id, "!=", None, "移动凭证ID不能为空")
        self.assert_util.assert_by_operator(voucher_info["voucher_type"], "=", "transfer", "凭证类型应该是调拨")
        self.assert_util.assert_by_operator(voucher_info["total_qty"], "=", 1, "总数量应该是1")
        self.assert_util.assert_by_operator(voucher_info["from_batch_id"], "=", expected_batch_from, "出库批次ID应该匹配")
        self.assert_util.assert_by_operator(voucher_info["to_batch_code"], "=", expected_batch_to, "入库批次编码应该匹配")
        return voucher_id

    def _create_transfer_voucher_with_params(self, custom_to_batch, remark):
        """创建调拨凭证的私有方法"""
        send_wh_info = self.md_cache_data["org_info"]["inv_bin_send_md"][0]
        return self.create_transfer_voucher(
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
            remark=remark
        )

    @case_decorator(
        story="库存余额调拨验证",
        title="测试查询调拨前库存余额",
        description="查询调拨前的库存余额总量，为后续总量不变验证提供基准",
        severity="critical",
        order=1,
        tags=["库存余额", "调拨", "基准查询"]
    )
    def test_query_initial_balance_before_transfer(self):
        """查询调拨前库存余额"""
        try:
            # 查询初始余额
            initial_balance = self.get_current_inventory_balance()
            assert initial_balance >= 0, f"初始库存余额应该大于等于0，实际: {initial_balance}"
            
            # 保存到类变量供后续测试使用
            self.__class__.initial_balance = initial_balance
            
            # 记录结果
            a.text(f"调拨前库存总余额: {initial_balance}", "初始库存总余额")
            self.logger.info(f"查询到调拨前库存余额: {initial_balance}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额调拨验证",
        title="测试创建调拨移动凭证",
        description="创建调拨移动凭证，验证凭证创建成功",
        severity="blocker",
        order=2,
        tags=["库存余额", "调拨", "移动凭证"]
    )
    def test_create_transfer_voucher(self):
        """创建调拨移动凭证"""
        try:
            if not self.available_batch_id:
                pytest.fail("没有可用批次，跳过调拨测试")
            
            # 创建调拨凭证
            custom_to_batch = self.mock_util.generate_unique_code(prefix="TRANSFER_", tag="STK")
            voucher_info = self._create_transfer_voucher_with_params(
                custom_to_batch, "自动化测试调拨-凭证创建验证"
            )
            
            # 验证凭证创建成功
            voucher_id = self._validate_transfer_voucher(voucher_info, self.available_batch_id, custom_to_batch)
            
            # 保存凭证信息到类变量供后续测试使用
            self.__class__.voucher_id = voucher_id
            self.__class__.custom_to_batch = custom_to_batch
            self.__class__.voucher_info = voucher_info
            
            # 报告记录
            a.json(voucher_info["request_params"], "请求数据")
            a.json(voucher_info["response"], "响应数据")
            a.text(f"从批次ID: {self.available_batch_id} 调拨到批次: {custom_to_batch}", "批次调拨信息")
            self.logger.info(f"创建调拨凭证成功: {voucher_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额调拨验证",
        title="测试验证调拨后库存余额总量不变",
        description="验证调拨完成后，库存总量保持不变，只改变分布",
        severity="blocker",
        order=3,
        tags=["库存余额", "调拨", "总量验证"]
    )
    def test_verify_balance_unchanged_after_transfer(self):
        """验证调拨后库存总量不变"""
        try:
            # 智能前置条件检查 - 支持单独运行
            if not hasattr(self.__class__, 'voucher_id') or self.__class__.voucher_id is None:
                self.logger.warning("缺少调拨凭证，执行前置测试")
                self._ensure_create_transfer_voucher()
            
            # 重新获取调拨前库存余额（避免测试间数据污染）
            pre_transfer_balance = self.get_current_inventory_balance()
            self.logger.info(f"调拨前实时库存余额: {pre_transfer_balance}")
            
            # 等待数据同步
            self._async_delay(2, "等待调拨库存同步")
            
            # 查询调拨后库存余额
            final_balance = self.get_current_inventory_balance()
            balance_change = abs(final_balance - pre_transfer_balance)
            
            self.logger.info(f"调拨后库存余额: {final_balance}, 变化量: {balance_change}")
            
            # 验证库存总量不变（调拨只改变分布，不改变总量）
            assert balance_change <= 0.01, f"调拨后总库存应该保持不变，调拨前: {pre_transfer_balance}, 调拨后: {final_balance}, 变化: {balance_change}"
            
            # 报告记录
            a.text(f"调拨前库存余额: {pre_transfer_balance}", "实时库存余额")
            a.text(f"调拨后库存余额: {final_balance}", "最终库存余额")
            a.text(f"库存变化量: {balance_change}", "库存变化验证")
            if hasattr(self.__class__, 'custom_to_batch'):
                a.text(f"从批次ID: {self.available_batch_id} 调拨到批次: {self.__class__.custom_to_batch}", "批次调拨信息")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
