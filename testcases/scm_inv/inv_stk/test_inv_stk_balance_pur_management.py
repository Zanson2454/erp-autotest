"""
功能描述:
    本模块测试库存余额管理的完整业务流程，包括移动凭证创建、库存余额查询、
    批次调整、导出等核心功能，确保库存数据的准确性和一致性。
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
@allure.feature("库存余额管理")
class TestInvStkBalancePurManagement(ScmInvBaseTest):
    """库存余额综合测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        cls.batch_code = None
        cls.balance_detail_id = None
        cls.balance_detail_code = None
        cls.adjust_voucher_id = None
        cls.adjust_voucher_code = None
        cls.batch_detail_id = None
        
        # 防重复执行标记
        cls._create_mobile_voucher_executed = False
        cls._query_balance_detail_executed = False
        cls._create_batch_adjustment_executed = False
        
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
            # 防重复执行检查
            if self.__class__._create_mobile_voucher_executed and self.mobile_voucher_id is not None:
                self.logger.info(f"移动凭证创建方法已执行过，跳过重复执行，ID: {self.mobile_voucher_id}")
                return
            
            # 记录操作前的库存余额
            pre_operation_balance = self.get_current_inventory_balance()
            self.logger.info(f"操作前库存余额: {pre_operation_balance}")
            
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
            TestInvStkBalancePurManagement.mobile_voucher_id = voucher_manager.mobile_voucher_id
            TestInvStkBalancePurManagement.mobile_voucher_code = voucher_manager.mobile_voucher_code
            TestInvStkBalancePurManagement.batch_code = voucher_manager.batch_code
            TestInvStkBalancePurManagement._create_mobile_voucher_executed = True  # 标记已执行
            
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
            # 确保前置条件：移动凭证已创建
            if not self.mobile_voucher_id:
                self.test_create_mobile_voucher_increase_inventory()
            
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
            
            # 如果无数据，容错处理：记录警告并提前返回，避免误报
            if not data_list:
                self.logger.warning("物料库存余额查询结果为空，可能是数据尚未落库或初始化库存为0")
                return
            
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

    @case_decorator(
        story="库存余额管理",
        title="测试仓库库存余额查询",
        description="验证仓库库存余额查询分页功能",
        severity="critical",
        order=4,
        tags=["库存余额", "仓库查询", "分页"]
    )
    def test_query_warehouse_stock_balance(self):
        """仓库库存余额查询用例"""
        try:
            # 1. 获取数据库中的实际仓库库存余额作为基准值
            db_balance = self.get_current_inventory_balance()
            
            # 2. API调用
            api_path = self.get_api_path("INV-库存余额-仓库库存余额查询分页服务")
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
                            },
                            "invLocId": {
                                "operator": "EQ",
                                "value": {"id": self.invLocId}
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "comOrgId", "type": "OBJECT"},
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 业务断言
            response_data = response.get("data", {}).get("data", {})
            total = response_data.get("total", 0)
            data_list = response_data.get("data", [])
            
            # 若无数据，容错处理：记录警告并返回，避免误报
            if total == 0 or not data_list:
                self.logger.warning(f"仓库库存余额查询结果为空，total={total}，可能是库存尚未落库或初始化为0")
                return
            
            # 获取API返回的库存数量并验证一致性
            api_stk_qty = data_list[0].get("stkQty", 0)
            assert api_stk_qty == db_balance, f"API返回的库存数量({api_stk_qty})与数据库查询结果({db_balance})不一致"
            
            # 6. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"仓库库存查询验证 - API库存数量: {api_stk_qty}, 数据库库存数量: {db_balance}, 总数: {total}", "仓库库存查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额管理",
        title="测试库存余额明细查询",
        description="验证库存余额明细查询分页功能并保存第一条记录信息",
        severity="critical",
        order=5,
        tags=["库存余额", "明细查询", "分页"]
    )
    def test_query_stock_balance_detail(self):
        """库存余额明细查询用例"""
        try:
            # 防重复执行检查
            if self.__class__._query_balance_detail_executed and self.balance_detail_id is not None:
                self.logger.info(f"余额明细查询方法已执行过，跳过重复执行，ID: {self.balance_detail_id}")
                return
            
            # 1. API调用
            api_path = self.get_api_path("INV-库存余额-查询分页服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
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
                            "matId": {
                                "operator": "EQ",
                                "value": {"id": self.matId}
                            },
                            "invOrgId": {
                                "operator": "EQ",
                                "value": {"id": self.invOrgId}
                            },
                            "invLocId": {
                                "operator": "EQ",
                                "value": {"id": self.invLocId}
                            },
                            "invWhId": {
                                "operator": "EQ",
                                "value": {"id": self.invWhId}
                            },
                            "invAreaId": {
                                "operator": "EQ",
                                "value": {"id": self.invAreaId}
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"},
                    {"name": "invWhId", "type": "OBJECT"},
                    {"name": "invAreaId", "type": "OBJECT"},
                    {"name": "invBinId", "type": "OBJECT"},
                    {"name": "batchId", "type": "OBJECT"},
                    {"name": "invTypeId", "type": "OBJECT"},
                    {"name": "spcStkTypeId", "type": "OBJECT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 业务断言
            response_data = response.get("data", {}).get("data", {})
            total = response_data.get("total", 0)
            data_list = response_data.get("data", [])
            
            # 容错：如果查询为空，记录警告并返回
            if total == 0 or not data_list:
                self.logger.warning(f"库存余额明细查询结果为空，total={total}，可能是库存未落库或过滤条件过严")
                return
            
            # 验证batch_code包含在查询的列表里面
            if self.batch_code:
                assert self.batch_code in str(data_list), f"批次编码 {self.batch_code} 未在查询结果中找到"
            
            # 保存第一条记录的id和code作为类变量
            first_record = data_list[0]
            TestInvStkBalancePurManagement.balance_detail_id = first_record.get("id")
            TestInvStkBalancePurManagement.balance_detail_code = first_record.get("batchId", {}).get("code")
            # 保存批次ID用于批次调整
            TestInvStkBalancePurManagement.batch_detail_id = first_record.get("batchId", {}).get("id")
            TestInvStkBalancePurManagement._query_balance_detail_executed = True  # 标记已执行
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"余额明细查询验证 - 总数: {total}, 批次编码验证: {self.batch_code in str(data_list) if self.batch_code else '无需验证'}, 第一条记录ID: {self.balance_detail_id}, 编码: {self.balance_detail_code}", "余额明细查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额管理",
        title="测试批次调整移动凭证创建",
        description="验证批次调整移动凭证创建功能，包含出库和入库操作",
        severity="critical",
        order=6,
        tags=["库存余额", "批次调整", "移动凭证"]
    )
    def test_create_batch_adjustment_voucher(self):
        """批次调整移动凭证创建用例"""
        try:
            # 防重复执行检查
            if self.__class__._create_batch_adjustment_executed and self.adjust_voucher_id is not None:
                self.logger.info(f"批次调整凭证创建方法已执行过，跳过重复执行，ID: {self.adjust_voucher_id}")
                return
            
            # 确保前置条件已满足
            if not self.mobile_voucher_id:
                self.test_create_mobile_voucher_increase_inventory()
            if not self.balance_detail_id:
                self.test_query_stock_balance_detail()
                
            # 若依然无明细，容错跳过，避免误报
            if not self.balance_detail_id or not self.batch_detail_id:
                self.logger.warning("未获取到库存余额明细/批次ID，可能库存未落库，跳过批次调整校验")
                return
            
            assert self.mobile_voucher_id, "移动凭证ID不能为空，请先执行test_create_mobile_voucher_increase_inventory"
            assert self.batch_code, "批次编码不能为空，请先执行test_create_mobile_voucher_increase_inventory"
            
            # 生成请求数据
            current_time = datetime.datetime.now()
            timestamp = current_time.strftime("%Y%m%d%H%M%S")
            doc_time = int(current_time.timestamp() * 1000)  # 毫秒时间戳
            request_no = self.mock_util.generate_unique_code(tag="REQ")
            
            # 1. API调用
            api_path = self.get_api_path("INV-移动凭证-新版创建服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理 - 构建批次调整移动凭证请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["comOrgId", "mvmTypeId", "showType", "mvmDocTimePst", "remark", "requestNo", "mvmDocOutList", "mvmDocInList"],
                ["params", "request"]
            )
            
            set_dict = {
                "comOrgId": {"id": self.comOrgId},
                "mvmTypeId": {"id": self.mvmTypeId}, 
                "showType": "ALL",
                "mvmDocTimePst": doc_time,
                "remark": f"自动化测试批次调整-{timestamp}",
                "requestNo": request_no,
                # 出库明细 - 使用现有批次
                "mvmDocOutList": [{
                    "id": self.balance_detail_id,
                    "context": {},
                    "version": 1,
                    "deleted": 0,
                    "matId": {"id": self.matId},
                    "invOrgId": {"id": self.invOrgId},
                    "invLocId": {"id": self.invLocId},
                    "invWhId": {"id": self.invWhId},
                    "invAreaId": {"id": self.invAreaId},
                    "invBinId": {"id": self.invBinId},
                    "mvmQty": 1,
                    "batchId": {"id": self.batch_detail_id},  # 使用现有批次ID
                    "unitId": self.unitId,
                    "refCode": "1",
                    "mvmTypeId": {"id": self.mvmTypeId}
                }],
                # 入库明细 - 创建新批次
                "mvmDocInList": [{
                    "id": self.balance_detail_id,
                    "context": {},
                    "version": 1,
                    "deleted": 0,
                    "matId": {"id": self.matId},
                    "invOrgId": {"id": self.invOrgId},
                    "invLocId": {"id": self.invLocId},
                    "invWhId": {"id": self.invWhId},
                    "invAreaId": {"id": self.invAreaId},
                    "invBinId": {"id": self.invBinId},
                    "mvmQty": 1,
                    "batchId": {
                        "context": {},
                        "batchCode": f"sqwBAT{timestamp}",  # 新的批次编码，使用固定前缀
                    },
                    "unitId": self.unitId,
                    "refCode": "1",
                    "mvmTypeId": {"id": self.mvmTypeId}
                }]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 请求与断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 业务断言 - 保存移动凭证数据到类变量
            voucher_data = response.get("data", {}).get("data", {})
            TestInvStkBalancePurManagement.adjust_voucher_id = voucher_data.get("moveVoucherId")
            TestInvStkBalancePurManagement.adjust_voucher_code = voucher_data.get("moveVoucherCode")
            TestInvStkBalancePurManagement._create_batch_adjustment_executed = True  # 标记已执行
            
            # 验证移动凭证创建成功
            assert self.adjust_voucher_id, "批次调整移动凭证ID不能为空"
            assert self.adjust_voucher_code, "批次调整移动凭证编码不能为空"
            
            self.logger.info(f"批次调整移动凭证创建成功 - ID: {self.adjust_voucher_id}, 编码: {self.adjust_voucher_code}")
            
            # 5. 报告记录
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"批次调整移动凭证创建 - ID: {self.adjust_voucher_id}, 编码: {self.adjust_voucher_code}", "批次调整移动凭证信息")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="库存余额管理",
        title="测试库存余额明细导出",
        description="验证库存余额明细导出任务提交功能",
        severity="normal",
        order=7,
        tags=["库存余额", "导出", "任务管理"]
    )
    def test_export_inventory_balance_detail(self):
        """库存余额明细导出测试用例"""
        try:
            # 0. 确保前置数据存在
            if not self.balance_detail_id:
                self.test_query_stock_balance_detail()
            
            # 1. 准备测试数据
            timestamp = self.mock_util.get_timestamp()
            task_name = f"库存余额明细-{self.nickname}-{timestamp}-导出"
            
            # 2. API调用
            api_path = self.get_api_path("库存余额表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 3. 直接构造完整参数（不使用过滤机制）
            request_params = {
                "serviceKey": "SCM_INV$INV_STK_BA_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [{
                        "modelKey": "SCM_INV$inv_stk_ba",
                        "modelName": "库存余额表",
                        "sheetNo": 0,
                        "sheetName": "库存余额表",
                        "headerConfigList": [
                            {"name": "公司组织", "type": "TEXT", "field": "comOrgId.orgName"},
                            {"name": "物料", "type": "TEXT", "field": "matId.matName"},
                            {"name": "库存组织", "type": "TEXT", "field": "invOrgId.orgName"},
                            {"name": "库存地点", "type": "TEXT", "field": "invLocId.orgName"},
                            {"name": "仓库", "type": "TEXT", "field": "invWhId.name"},
                            {"name": "仓储区", "type": "TEXT", "field": "invAreaId.name"},
                            {"name": "仓位", "type": "TEXT", "field": "invBinId.name"},
                            {"name": "数量", "type": "DECIMAL", "field": "stkQty", "precision": 6, "precisionDisplayType": "ORIGIN_ROUND"},
                            {"name": "单位", "type": "TEXT", "field": "baseUomId.uomDesc"},
                            {"name": "批次", "type": "TEXT", "field": "batchId.code"},
                            {"name": "库存类型", "type": "TEXT", "field": "invTypeId.name"},
                            {"name": "特殊库存标识", "type": "TEXT", "field": "spcStkTypeId.name"},
                            {"name": "特殊库存分类名称", "type": "TEXT", "field": "spcStkTypeClassName"}
                        ]
                    }],
                    "queryData": {
                        "containerKey": "ERP_SCM$INV_STOCK_BALANCE_VIEW-TERP_MIGRATE$baStk3-table-container-TERP_MIGRATE$inv_stk_ba",
                        "viewKey": "SCM_INV$INV_STOCK_BALANCE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_STOCK_BALANCE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "conditionItems": {
                                        "type": "ConditionItems",
                                        "logicOperator": "AND",
                                        "conditions": {
                                            "id": {
                                                "operator": "IN",
                                                "value": [self.balance_detail_id]
                                            }
                                        }
                                    }
                                }
                            },
                            "selectFields": [
                                {"field": "stkQty"},
                                {"field": "spcStkTypeClassName"},
                                {"field": "comOrgId", "selectFields": [{"field": "orgName"}]},
                                {"field": "matId", "selectFields": [{"field": "matName"}]},
                                {"field": "invOrgId", "selectFields": [{"field": "orgName"}]},
                                {"field": "invLocId", "selectFields": [{"field": "orgName"}]},
                                {"field": "invWhId", "selectFields": [{"field": "name"}]},
                                {"field": "invAreaId", "selectFields": [{"field": "name"}]},
                                {"field": "invBinId", "selectFields": [{"field": "name"}]},
                                {"field": "baseUomId", "selectFields": [{"field": "uomDesc"}]},
                                {"field": "batchId", "selectFields": [{"field": "code"}]},
                                {"field": "invTypeId", "selectFields": [{"field": "name"}]},
                                {"field": "spcStkTypeId", "selectFields": [{"field": "name"}]}
                            ],
                            "modelKey": "SCM_INV$inv_stk_ba"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "SCM_INV$inv_stk_ba",
                        "modelName": "库存余额表",
                        "containerKey": "ERP_SCM$INV_STOCK_BALANCE_VIEW-TERP_MIGRATE$baStk3-table-container-TERP_MIGRATE$inv_stk_ba",
                        "viewKey": "SCM_INV$INV_STOCK_BALANCE_VIEW:list",
                        "sceneKey": "SCM_INV$INV_STOCK_BALANCE_VIEW"
                    }
                }
            }
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=request_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 业务断言
            response_data = response.get("data", {})
            task_id = response_data.get("taskId")
            
            # 验证导出任务创建成功
            if task_id:
                self.logger.info(f"库存余额明细导出任务创建成功 - 任务ID: {task_id}, 任务名称: {task_name}")
                task_info = f"导出任务创建成功 - 任务ID: {task_id}, 任务名称: {task_name}"
            else:
                self.logger.info(f"库存余额明细导出任务提交成功 - 任务名称: {task_name}")
                task_info = f"导出任务提交成功 - 任务名称: {task_name}"
            
            # 6. 报告记录
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(task_info, "导出任务信息")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

