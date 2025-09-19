"""
库存综合管理测试 - 使用移动凭证创建器
验证采购、销售、调拨对库存统计和余额的影响
"""
import allure
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from testcases.scm_inv.inv_mvm.mobile_voucher_creator import MobileVoucherCreator
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("库存综合管理")
class TestInvStkComprehensiveManagement(ScmInvBaseTest):
    """库存综合管理测试类 - 使用移动凭证创建器"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 初始化移动凭证创建器
        cls.voucher_creator = MobileVoucherCreator()
        cls.voucher_creator.setup_class()
        
        # 测试数据存储
        cls.initial_inventory = 0.0
        cls.voucher_records = []
        
        cls.logger.info("库存综合管理测试类初始化完成")
    
    def get_current_inventory_statistics(self, level=1):
        """获取当前库存统计数据"""
        try:
            api_path = self.get_api_path("INV-库存余额-库存账统计服务")
            params, url = self.get_api_params(api_path)
            
            mat_id = self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            
            filtered_params = {
                "params": {
                    "request": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "level": level,
                        "matId": mat_id,
                        "invOrgId": self.invOrgId,
                        "invLocId": self.invLocId
                    }
                }
            }
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 提取数量
            response_data = response.get("data", {}).get("data", {})
            data_list = response_data.get("data", [])
            qty = float(data_list[0].get("qty", 0)) if data_list else 0.0
            
            return {
                "qty": qty,
                "response": response,
                "request_params": filtered_params
            }
        except Exception as e:
            self.logger.error(f"获取库存统计失败: {str(e)}")
            return {"qty": 0.0, "response": None, "request_params": None}

    @case_decorator(
        story="库存综合管理",
        title="测试查询初始库存统计",
        description="查询初始库存统计数据，为后续对比提供基准",
        severity="critical",
        order=1,
        tags=["库存统计", "初始状态"]
    )
    def test_query_initial_inventory_statistics(self):
        """查询初始库存统计用例"""
        try:
            # 1. 查询初始库存统计
            result = self.get_current_inventory_statistics(level=1)
            
            # 2. 保存初始库存数据
            TestInvStkComprehensiveManagement.initial_inventory = result["qty"]
            
            # 3. 验证查询成功
            assert result["qty"] >= 0, f"初始库存数量应该大于等于0，实际: {result['qty']}"
            
            self.logger.info(f"初始库存统计: {result['qty']}")
            
            # 4. 报告记录
            a.json(result["request_params"], "请求数据")
            a.json(result["response"], "响应数据")
            a.text(f"初始库存统计数量: {result['qty']}", "初始库存统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.parametrize("voucher_type,qty,expected_change", [
        ("purchase", 3, "increase"),
        ("sale", 1, "decrease"),
        ("purchase", 2, "increase")
    ])
    @case_decorator(
        story="库存综合管理",
        title="测试不同移动凭证对库存的影响",
        description="使用移动凭证创建器创建不同类型凭证，验证库存变化",
        severity="blocker",
        order=2,
        tags=["移动凭证", "库存变化", "参数化"]
    )
    def test_inventory_change_by_voucher_type(self, voucher_type, qty, expected_change):
        """不同移动凭证对库存影响用例"""
        try:
            # 1. 确保有初始库存数据
            if not hasattr(self, 'initial_inventory') or self.initial_inventory is None:
                self.test_query_initial_inventory_statistics()
            
            # 2. 记录操作前库存
            before_result = self.get_current_inventory_statistics(level=1)
            before_qty = before_result["qty"]
            
            # 3. 根据类型创建移动凭证
            voucher_info = None
            if voucher_type == "purchase":
                voucher_info = self.voucher_creator.create_purchase_voucher(
                    qty=qty,
                    remark=f"参数化测试采购入库-数量{qty}"
                )
            elif voucher_type == "sale":
                voucher_info = self.voucher_creator.create_sale_voucher(
                    qty=qty,
                    remark=f"参数化测试销售出库-数量{qty}"
                )
            
            # 4. 验证凭证创建成功
            assert voucher_info, "移动凭证创建失败"
            assert voucher_info["mobile_voucher_id"], "移动凭证ID不能为空"
            assert voucher_info["mobile_voucher_code"], "移动凭证编码不能为空"
            
            # 5. 记录凭证信息
            TestInvStkComprehensiveManagement.voucher_records.append({
                "type": voucher_type,
                "qty": qty,
                "expected_change": expected_change,
                "voucher_id": voucher_info["mobile_voucher_id"],
                "voucher_code": voucher_info["mobile_voucher_code"]
            })
            
            # 6. 等待数据同步并验证库存变化
            time.sleep(2)
            after_result = self.get_current_inventory_statistics(level=1)
            after_qty = after_result["qty"]
            
            # 7. 验证库存变化方向
            actual_change = after_qty - before_qty
            if expected_change == "increase":
                assert actual_change > 0, f"{voucher_type}应该增加库存，实际变化: {actual_change}"
            elif expected_change == "decrease":
                assert actual_change < 0, f"{voucher_type}应该减少库存，实际变化: {actual_change}"
            
            self.logger.info(f"{voucher_type}移动凭证创建成功 - 数量: {qty}, 库存变化: {before_qty} -> {after_qty}")
            
            # 8. 报告记录
            a.json(voucher_info["request_params"], f"{voucher_type}请求数据")
            a.json(voucher_info["response"], f"{voucher_type}响应数据")
            a.text(f"{voucher_type}凭证 - ID: {voucher_info['mobile_voucher_id']}, 编码: {voucher_info['mobile_voucher_code']}, 数量: {qty}, 库存变化: {before_qty} -> {after_qty} ({actual_change:+})", f"{voucher_type}凭证验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存综合管理",
        title="测试调拨移动凭证对库存的影响",
        description="创建调拨移动凭证，验证总库存不变但库存分布改变",
        severity="blocker",
        order=3,
        tags=["移动凭证", "调拨", "库存分布"]
    )
    def test_transfer_voucher_inventory_impact(self):
        """调拨移动凭证对库存影响用例"""
        try:
            # 1. 确保有足够库存进行调拨
            current_result = self.get_current_inventory_statistics(level=1)
            current_qty = current_result["qty"]
            
            if current_qty < 1:
                # 先创建采购入库确保有库存
                purchase_info = self.voucher_creator.create_purchase_voucher(
                    qty=2,
                    remark="为调拨准备库存"
                )
                time.sleep(2)
                current_result = self.get_current_inventory_statistics(level=1)
                current_qty = current_result["qty"]
            
            assert current_qty >= 1, f"调拨前必须有足够库存，当前库存: {current_qty}"
            
            # 2. 记录调拨前库存
            before_qty = current_qty
            
            # 3. 创建调拨移动凭证
            transfer_info = self.voucher_creator.create_transfer_voucher(
                qty=1,
                remark="参数化测试调拨"
            )
            
            # 4. 验证调拨凭证创建成功
            assert transfer_info["mobile_voucher_id"], "调拨移动凭证ID不能为空"
            assert transfer_info["mobile_voucher_code"], "调拨移动凭证编码不能为空"
            assert transfer_info["voucher_type"] == "transfer", "凭证类型应该是调拨"
            
            # 5. 记录调拨凭证信息
            TestInvStkComprehensiveManagement.voucher_records.append({
                "type": "transfer",
                "qty": 1,
                "expected_change": "no_change",
                "voucher_id": transfer_info["mobile_voucher_id"],
                "voucher_code": transfer_info["mobile_voucher_code"]
            })
            
            # 6. 等待数据同步并验证库存不变
            time.sleep(2)
            after_result = self.get_current_inventory_statistics(level=1)
            after_qty = after_result["qty"]
            
            # 7. 验证总库存不变（允许小误差）
            change = abs(after_qty - before_qty)
            assert change < 0.001, f"调拨不应该改变总库存，操作前: {before_qty}, 操作后: {after_qty}, 变化: {change}"
            
            self.logger.info(f"调拨移动凭证创建成功 - 总库存保持不变: {before_qty} -> {after_qty}")
            
            # 8. 报告记录
            a.json(transfer_info["request_params"], "调拨请求数据")
            a.json(transfer_info["response"], "调拨响应数据")
            a.text(f"调拨凭证 - ID: {transfer_info['mobile_voucher_id']}, 编码: {transfer_info['mobile_voucher_code']}, 总库存: {before_qty} -> {after_qty} (不变)", "调拨凭证验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.parametrize("level,test_desc", [
        (1, "物料维度汇总"),
        (2, "库存组织库存地点维度汇总"),
        (3, "特殊库存维度汇总"),
        (4, "批次维度汇总")
    ])
    @case_decorator(
        story="库存综合管理",
        title="测试最终库存统计验证",
        description="验证所有移动凭证操作后不同维度的库存统计数据",
        severity="blocker",
        order=4,
        tags=["库存统计", "最终验证", "参数化"]
    )
    def test_final_inventory_statistics_verification(self, level, test_desc):
        """最终库存统计验证用例"""
        try:
            # 1. 查询最终库存统计
            result = self.get_current_inventory_statistics(level=level)
            final_qty = result["qty"]
            
            # 2. 基本验证
            assert final_qty >= 0, f"Level {level}({test_desc}) 最终库存数量应该大于等于0，实际: {final_qty}"
            
            # 3. Level 1进行详细对比
            if level == 1:
                # 计算预期净变化（根据参数化测试：+3, -1, +2 = +4）
                expected_net_change = 3 - 1 + 2  # 4
                expected_final = self.initial_inventory + expected_net_change
                
                # 验证最终库存在合理范围内
                assert final_qty >= expected_final, f"Level 1最终库存应该至少为{expected_final}，实际: {final_qty}"
                
                # 生成变化汇总
                change_summary = f"初始: {self.initial_inventory}, 最终: {final_qty}, 净变化: {final_qty - self.initial_inventory}"
                a.text(change_summary, "库存变化汇总")
            
            self.logger.info(f"Level {level}({test_desc}) 最终库存统计: {final_qty}")
            
            # 4. 报告记录
            a.json(result["request_params"], f"Level {level}请求数据")
            a.json(result["response"], f"Level {level}响应数据")
            a.text(f"Level {level}({test_desc}) - 最终库存数量: {final_qty}", f"最终库存统计-{test_desc}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存综合管理",
        title="测试移动凭证创建汇总报告",
        description="汇总所有移动凭证创建情况和库存变化",
        severity="normal",
        order=5,
        tags=["汇总报告", "测试总结"]
    )
    def test_voucher_creation_summary_report(self):
        """移动凭证创建汇总报告用例"""
        try:
            # 1. 获取最终库存
            final_result = self.get_current_inventory_statistics(level=1)
            final_qty = final_result["qty"]
            
            # 2. 生成汇总报告
            summary = {
                "initial_inventory": self.initial_inventory,
                "final_inventory": final_qty,
                "net_change": final_qty - self.initial_inventory,
                "voucher_records": self.voucher_records,
                "total_vouchers_created": len(self.voucher_records)
            }
            
            # 3. 验证凭证数量
            assert len(self.voucher_records) > 0, "应该至少创建了一个移动凭证"
            
            # 4. 统计各类型凭证数量
            voucher_stats = {}
            for record in self.voucher_records:
                voucher_type = record["type"]
                if voucher_type not in voucher_stats:
                    voucher_stats[voucher_type] = 0
                voucher_stats[voucher_type] += 1
            
            summary["voucher_stats"] = voucher_stats
            
            self.logger.info(f"移动凭证创建汇总 - 初始库存: {self.initial_inventory}, 最终库存: {final_qty}, 净变化: {final_qty - self.initial_inventory}")
            self.logger.info(f"凭证统计: {voucher_stats}")
            
            # 5. 报告记录
            a.json(summary, "移动凭证创建汇总报告")
            a.text(f"测试完成 - 创建{len(self.voucher_records)}个移动凭证，库存从{self.initial_inventory}变为{final_qty}，净变化{final_qty - self.initial_inventory}", "测试汇总")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理移动凭证测试数据
            cls.db.delete(
                table="inv_mvm_doc_head_tr",
                where="request_no like %s",
                params=["AT_REQ_%"]
            )
            # 清理批次测试数据
            cls.db.delete(
                table="inv_batch_tr",
                where="code like %s",
                params=["SQW%"]
            )
            cls.logger.info("库存综合管理测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
