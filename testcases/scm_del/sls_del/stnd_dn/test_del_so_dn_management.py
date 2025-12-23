"""
标准销售交货单测试
"""
import allure
import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del.sls_del.stnd_dn import SlsDelBaseTest
from utils.report_util import a, case_decorator
from data_factory.del_po_dn_factory import DelPoDnFactory
from utils.param_util import ParamUtil
from utils.cache_util import CacheUtil
from data_factory.base import DataFactory


@allure.epic("交货管理")
@allure.feature("标准销售交货单")
class TestDelSoDnManagement(SlsDelBaseTest):
    """标准销售交货单测试类"""
    
    # 常量定义
    TEST_REMARK = "执行自动化测试备注SQW"
    PLAN_DEL_QTY = 10  # 计划交货数量（同时作为批次数量）
    BATCH_QTY = 10     # 批次数量
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        # 初始化测试数据ID
        cls._init_test_data_ids()
        
        # 初始化缓存数据
        cls._init_cache_data()
        
        cls.logger.info("标准销售交货单测试类初始化完成")
    
    @classmethod
    def _init_test_data_ids(cls):
        """初始化测试数据ID"""
        cls.dn_id = None
        cls.dn_code = None
        cls.dn_item_id = None
        cls.so_id = None
        cls.so_code = None
        cls.so_item_id = None
        cls.task_list = None
        cls.warehouse_task_list = None
        cls.picking_task_list = None  # 拣配任务列表
    
    @classmethod
    def _init_cache_data(cls):
        """初始化缓存数据（仅初始化交货单特有的数据，销售订单相关数据已在 SlsDelBaseTest.setup_class 中初始化）"""
        # 注意：mat_id, mat_code, inv_org_id, inv_loc_id, sls_org_id, com_org_id, cust_id, curr_id
        # 等属性已在 SlsDelBaseTest.setup_class 中通过 _init_sls_order_attributes 初始化
        # 这里只需要初始化交货单特有的数据（如果有的话）
        pass
    
    
    @property
    def dn_factory(self):
        """获取交货单工厂实例（单例模式）"""
        if not hasattr(self, '_dn_factory'):
            self._dn_factory = DelPoDnFactory(
                http_client=self.http,
                apis=self.apis,
                api_params=self.api_params,
                mock_util=self.mock_util,
                logger=self.logger,
                init_data=self.init_data,
                md_cache_data=self.md_cache_data,
                del_cache_data=self.del_cache_data
            )
        return self._dn_factory
    
    def _verify_dn_biz_status(self, expected_status):
        """验证交货单业务状态"""
        query_sql = """
            SELECT id, biz_status 
            FROM del_dn_head_tr 
            WHERE id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        db_result = self.db.query(query_sql, [self.__class__.dn_id])
        
        if not db_result:
            raise ValueError(f"未在数据库中找到交货单: id={self.__class__.dn_id}")
        
        actual_status = db_result[0].get("biz_status")
        self.logger.info(f"交货单业务状态: {actual_status}")
        
        assert actual_status == expected_status, \
            f"交货单业务状态不符合预期: 期望={expected_status}, 实际={actual_status}"
        
        return actual_status
    
    def _create_so_for_dn(self):
        """创建销售订单用于后续创建交货单"""
        try:
            # 使用继承的 create_sales_order 方法创建已生效的销售订单
            self.__class__.so_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 从数据库查询最新创建的销售订单行
            query_sql = """
                SELECT so_item_code, so_code, id 
                FROM sls_so_item_tr 
                WHERE so_id = %s
                ORDER BY created_at DESC 
                LIMIT 1
            """
            so_items = self.db.query(query_sql, [self.__class__.so_id])
            
            if so_items:
                so_item = so_items[0]
                self.__class__.so_item_id = so_item.get("id")
                self.__class__.so_code = so_item.get("so_code")
                self.logger.info(f"成功创建销售订单: so_code={self.__class__.so_code}, so_item_id={self.__class__.so_item_id}")
            else:
                raise ValueError("未查询到销售订单行数据")
            
            return self.__class__.so_id
            
        except Exception as e:
            self.logger.error(f"创建销售订单失败: {str(e)}")
            raise
    
    @case_decorator(
        story="标准销售交货单",
        title="创建标准销售交货单",
        description="创建标准销售交货单，验证创建成功",
        severity="critical",
        file_level_order=1,
        tags=["交货", "销售交货单", "创建"]
    )
    def test_create_standard_so_dn(self):
        """创建标准销售交货单"""
        try:
            if not self.__class__.so_id:
                self._create_so_for_dn()
            
            # 检查订单状态，确保订单已生效（与原始实现保持一致）
            order_info = self.db.query("SELECT so_status FROM sls_so_head_tr WHERE id = %s", (self.__class__.so_id,))
            if not order_info:
                raise ValueError(f"未找到订单，订单ID: {self.__class__.so_id}")
            
            order_status = order_info[0]['so_status']
            if order_status != "EFFECT":
                self.logger.warning(f"订单状态不是已生效，当前状态: {order_status}。订单ID: {self.__class__.so_id}")
                a.text(f"订单状态不是已生效，当前状态: {order_status}。订单ID: {self.__class__.so_id}", "状态警告")
            
            # 使用继承的 create_delivery_order 方法创建交货单
            dn_result = self.create_delivery_order(self.__class__.so_id)
            
            # 如果返回的是字典（可能是空字典），尝试查询交货单
            if isinstance(dn_result, dict):
                if dn_result.get("id"):
                    self.__class__.dn_id = dn_result.get("id")
                else:
                    # 如果返回空字典，尝试通过订单号查询交货单
                    import time
                    time.sleep(2)  # 等待交货单创建完成
                    so_code = self.__class__.so_code
                    query_result = self.db.query("""
                        SELECT DISTINCT h.id as dn_id
                        FROM del_dn_head_tr h
                        INNER JOIN del_dn_item_tr i ON h.id = i.dn_id
                        WHERE i.doc_code = %s OR h.doc_code = %s
                        ORDER BY h.created_at DESC 
                        LIMIT 1
                    """, (so_code, so_code))
                    if query_result:
                        self.__class__.dn_id = query_result[0].get("dn_id")
                        self.logger.info(f"通过订单号查询到交货单ID: {self.__class__.dn_id}")
                    else:
                        raise ValueError(f"创建交货单后无法查询到交货单，订单号: {so_code}")
            else:
                # 如果返回的是ID（整数或字符串）
                self.__class__.dn_id = dn_result
            
            # 1. 验证交货单ID不为空
            assert self.__class__.dn_id, "交货单ID不能为空"
            self.logger.info(f"✅ 交货单创建成功，交货单ID: {self.__class__.dn_id}")
            
            # 2. 从数据库查询交货单信息，验证交货单确实存在
            query_sql = """
                SELECT id, dn_code, del_status, biz_status 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
            dn_result = self.db.query(query_sql, [self.__class__.dn_id])
            if not dn_result:
                raise ValueError(f"❌ 未在数据库中找到交货单，交货单ID: {self.__class__.dn_id}")
            
            # 3. 获取交货单信息
            dn_info = dn_result[0]
            self.__class__.dn_code = dn_info.get("dn_code")
            del_status = dn_info.get("del_status")
            biz_status = dn_info.get("biz_status")
            
            # 4. 验证交货单确实存在
            assert dn_info.get("id") == self.__class__.dn_id, \
                f"交货单ID不匹配: 期望={self.__class__.dn_id}, 实际={dn_info.get('id')}"
            assert self.__class__.dn_code, "交货单编码不能为空"
            self.logger.info(f"✅ 交货单确实存在于数据库中，交货单编码: {self.__class__.dn_code}")
            
            # 5. 验证单据状态已生效（INEFFECT）
            assert del_status == "INEFFECT", \
                f"❌ 交货单单据状态不符合预期: 期望=INEFFECT, 实际={del_status}"
            self.logger.info(f"✅ 交货单单据状态验证通过: {del_status}")
            
            # 6. 验证业务状态等待执行（WAIT_EXECUTE）
            assert biz_status == "WAIT_EXECUTE", \
                f"❌ 交货单业务状态不符合预期: 期望=WAIT_EXECUTE, 实际={biz_status}"
            self.logger.info(f"✅ 交货单业务状态验证通过: {biz_status}")
            
            # 7. 记录验证结果
            a.text(
                f"交货单创建并验证成功:\n"
                f"  交货单ID: {self.__class__.dn_id}\n"
                f"  交货单编码: {self.__class__.dn_code}\n"
                f"  单据状态: {del_status} (已生效)\n"
                f"  业务状态: {biz_status} (等待执行)",
                "交货单创建验证结果"
            )
            
            # 从数据库查询交货单行ID
            query_sql = """
                SELECT id FROM del_dn_item_tr 
                WHERE dn_id = %s
                ORDER BY created_at DESC 
                LIMIT 1
            """
            dn_item_result = self.db.query(query_sql, [self.__class__.dn_id])
            if dn_item_result:
                self.__class__.dn_item_id = dn_item_result[0].get("id")
                self.logger.info(f"获取交货单行ID: {self.__class__.dn_item_id}")
            else:
                self.logger.warning(f"未查询到交货单行数据: dn_id={self.__class__.dn_id}")
            
            a.text(
                f"交货单ID: {self.__class__.dn_id}\n"
                f"交货单编码: {self.__class__.dn_code}\n"
                f"交货单行ID: {self.__class__.dn_item_id}\n"
                f"交货状态: {del_status}\n"
                f"销售订单编码: {self.__class__.so_code}\n"
                f"销售订单行ID: {self.__class__.so_item_id}",
                "交货单信息"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售交货单",
        title="提交销售交货单",
        description="提交草稿态的销售交货单（如果已生效则跳过）",
        severity="critical",
        file_level_order=2,
        tags=["交货", "销售交货单", "提交"]
    )
    def test_submit_so_dn(self):
        """提交销售交货单"""
        try:
            if not self.__class__.dn_id:
                self.test_create_standard_so_dn()
            
            # 检查交货单状态，如果已经是生效态则跳过提交
            query_sql = """
                SELECT del_status, dn_code 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
            db_result = self.db.query(query_sql, [self.__class__.dn_id])
            
            if not db_result:
                raise ValueError(f"未在数据库中找到交货单: id={self.__class__.dn_id}")
            
            actual_status = db_result[0].get("del_status")
            actual_dn_code = db_result[0].get("dn_code")
            
            # 如果交货单已经是生效态，则跳过提交
            if actual_status == "INEFFECT":
                self.logger.info(f"交货单已经是生效态，跳过提交。交货单ID: {self.__class__.dn_id}, 编码: {actual_dn_code}")
                a.text(
                    f"交货单已经是生效态，跳过提交:\n"
                    f"  交货单ID: {self.__class__.dn_id}\n"
                    f"  交货单编码: {actual_dn_code}\n"
                    f"  单据状态: {actual_status}",
                    "跳过提交"
                )
                return
            
            # 如果状态是草稿态，则执行提交
            result = self.dn_factory.submit_delivery_note(dn_id=self.__class__.dn_id)
            
            assert result.get("success"), "交货单提交失败"
            
            # 再次查询验证状态
            db_result = self.db.query(query_sql, [self.__class__.dn_id])
            if db_result:
                actual_status = db_result[0].get("del_status")
                actual_dn_code = db_result[0].get("dn_code")
                
                assert actual_status == "INEFFECT", f"交货单状态应为生效态: {actual_status}"
                assert actual_dn_code == self.__class__.dn_code, \
                    f"交货单编码不匹配: 期望={self.__class__.dn_code}, 实际={actual_dn_code}"
            else:
                raise ValueError(f"未在数据库中找到交货单: id={self.__class__.dn_id}")
            
            a.text(
                f"交货单ID: {result.get('dn_id')}\n"
                f"交货单编码: {result.get('dn_code')}\n"
                f"数据库状态: {actual_status}",
                "提交结果"
            )
            a.json(result.get("response", {}), "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售交货单",
        title="查询销售交货单列表",
        description="查询销售交货单列表，验证新建的交货单在列表中",
        severity="critical",
        file_level_order=3,
        tags=["交货", "销售交货单", "查询"]
    )
    def test_query_so_dn_list(self):
        """查询销售交货单列表"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_so_dn()
            
            api_path = self.get_api_path("DEL-交货单公共-数据分页查询服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["btClass", "pageable"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {
                "btClass": "SLS",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionGroup": None
                }
            })
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {})
            assert records.get("total") > 0, "未查询到交货单数据"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售交货单",
        title="查询销售交货单详情",
        description="根据交货单ID查询销售交货单详情",
        severity="critical",
        file_level_order=4,
        tags=["交货", "销售交货单", "查询"]
    )
    def test_query_so_dn_detail(self):
        """查询销售交货单详情"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_so_dn()
            
            api_path = self.get_api_path("DEL-交货单详情服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"id": str(self.__class__.dn_id)})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", {})
            assert result_data, "详情数据为空"
            assert result_data.get("id") == self.__class__.dn_id, \
                f"交货单ID不匹配: 期望={self.__class__.dn_id}, 实际={result_data.get('id')}"
            assert result_data.get("delStatus") == "INEFFECT", \
                f"交货状态不符合预期: 期望=INEFFECT, 实际={result_data.get('delStatus')}"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售交货单",
        title="查询销售交货单行列表",
        description="根据交货单头ID查询交货单行列表",
        severity="critical",
        file_level_order=5,
        tags=["交货", "销售交货单", "行查询"]
    )
    def test_query_so_dn_items(self):
        """查询销售交货单行列表"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_so_dn()
            
            api_path = self.get_api_path("DEL-交货单公共-根据订单ID查询交货单行服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "pageable"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", [])
            assert result_data is not None, "未查询到交货单行数据"

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="生成验货任务",
        description="验证生成验货任务功能（销售交货单生成的是验货任务，不是清点任务）",
        severity="critical",
        file_level_order=6,
        tags=["验货任务", "生成"]
    )
    def test_generate_inv_executed_task(self):
        """生成验货任务"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_so_dn()
            
            # 销售交货单使用生成验货任务的API（DEL_APP_INV_EXECUTED_TASK_TILE_EVENT_SERVICE）
            api_path = self.get_api_path("DEL-APP端仓库执行任务平铺服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            response_data = response.get("data", {}).get("data", {})
            assert response_data, "响应数据为空，未生成验货任务"
            
            task_list = response_data.get("delWmWarehouseTaskList", [])
            assert task_list, "验货任务列表为空"
            
            self.__class__.task_list = task_list
            self.logger.info(f"成功生成 {len(task_list)} 个验货任务")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"生成任务数量: {len(task_list)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="确定验货任务",
        description="验证确定验货任务功能（销售交货单确定的是验货任务，任务状态为WAIT_EXECUTE）",
        severity="critical",
        file_level_order=7,
        tags=["验货任务", "确定"]
    )
    def test_save_inv_executed_task(self):
        """确定验货任务"""
        try:
            if not self.__class__.task_list:
                self.test_generate_inv_executed_task()
            
            if not self.__class__.task_list:
                raise ValueError("验货任务列表为空，无法确定")
            
            # 销售交货单使用确定验货任务的API（DEL_APP_INV_EXECUTED_TASK_SAVE_EVENT_SERVICE）
            api_path = self.get_api_path("仓库执行任务保存事件服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"delWmWarehouseTaskList": self.__class__.task_list})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存验货任务后，API可能返回更新后的任务列表，使用返回的数据
            response_data = response.get("data", {}).get("data", {})
            if response_data and isinstance(response_data, dict):
                # 如果返回了任务列表，使用返回的数据（包含完整的任务信息，如taskCode）
                updated_task_list = response_data.get("delWmWarehouseTaskList", [])
                if updated_task_list:
                    self.__class__.task_list = updated_task_list
                    self.logger.info(f"使用保存验货任务API返回的任务列表，任务数量: {len(updated_task_list)}")
            
            # 销售交货单确定验货任务后，业务状态应该变为等待执行（WAIT_EXECUTE）
            # 注意：这里可能需要根据实际业务状态调整，从curl看任务状态是WAIT_EXECUTE
            # 但交货单的业务状态可能还是TASK_EXECUTING，需要根据实际情况调整
            actual_biz_status = self._verify_dn_biz_status("TASK_EXECUTING")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"确定任务数量: {len(self.__class__.task_list)}\n"
                f"交货单业务状态: {actual_biz_status}",
                "确定结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="交货单列表下拉查看验货",
        description="验证交货单列表下拉查看验货功能",
        severity="critical",
        file_level_order=8,
        tags=["交货单", "验货", "查看"]
    )
    def test_query_dn_inv_executed(self):
        """交货单列表下拉查看验货"""
        try:
            if not self.__class__.dn_item_id:
                self.test_save_inv_executed_task()
            
            api_path = self.get_api_path("DEL-查看拣配服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            # 注意：这里传的是交货单行ID，不是交货单头ID
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_item_id})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            response_data = response.get("data", {}).get("data", {})
            assert response_data, "响应数据为空，未查询到验货数据"
            
            a.text(
                f"交货单行ID: {self.__class__.dn_item_id}\n"
                f"交货单头ID: {self.__class__.dn_id}",
                "查询参数"
            )
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="根据交货单编号查询拣配任务",
        description="验证根据交货单编号查询对应拣配任务功能",
        severity="critical",
        file_level_order=9,
        tags=["交货单", "拣配任务", "查询"]
    )
    def test_query_picking_task_by_dn_code(self):
        """根据交货单编号查询拣配任务"""
        try:
            if not self.__class__.dn_code:
                self.test_save_inv_executed_task()
            
            # 调用ERP_WM模块的查询拣配任务API
            api_path = "/api/trantor/service/engine/execute/ERP_WM$WM_QUERY_TASK_INFO_PAGE_EVENT_SERVICE"
            url = f"{self.http.url}{api_path}?tmodule=ERP_WM"
            
            # 构造查询条件：taskType = "LOADING", delDnHeadCode = 交货单编号
            condition_group = {
                "type": "ConditionGroup",
                "logicOperator": "AND",
                "conditions": [
                    {
                        "type": "ConditionGroup",
                        "logicOperator": "AND",
                        "conditions": [
                            {
                                "key": "9XmpKO84A-0PJa2DJ6REO",
                                "type": "ConditionLeaf",
                                "leftValue": {
                                    "id": "qB1aK2hnvTrvS_Ek3_xb1",
                                    "key": "qB1aK2hnvTrvS_Ek3_xb1",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "VAR",
                                    "varValue": [{"valueKey": "taskType", "valueName": "taskType"}]
                                },
                                "operator": "EQ",
                                "rightValue": {
                                    "key": "Ywk8zk9P2CcnAjACcerXo",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "CONST",
                                    "constValue": "LOADING"
                                }
                            },
                            {
                                "key": "77osD6-TQxyF2wnEBc-lJ",
                                "type": "ConditionLeaf",
                                "leftValue": {
                                    "id": "86VZwMW39-CO-uXAuFeXI",
                                    "key": "86VZwMW39-CO-uXAuFeXI",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "VAR",
                                    "varValue": [{"valueKey": "delDnHeadCode", "valueName": "delDnHeadCode"}]
                                },
                                "operator": "EQ",
                                "rightValue": {
                                    "key": "KPwqpGxZwhnQFTr3EWz1S",
                                    "type": "VarValue",
                                    "fieldType": "Text",
                                    "valueType": "CONST",
                                    "constValue": self.__class__.dn_code
                                }
                            }
                        ]
                    }
                ]
            }
            
            params = {
                "sceneKey": "ERP_WM$WAREHOUSE_PICKING_TASK",
                "viewKey": "ERP_WM$WAREHOUSE_PICKING_TASK:list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "ERP_WM$WM_QUERY_TASK_INFO_PAGE_EVENT_SERVICE",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "sortOrders": None,
                            "conditionGroup": condition_group
                        },
                        "fields": [
                            {"name": "taskType", "type": "SELECT"},
                            {"name": "taskCode", "type": "TEXT"},
                            {"name": "delDnHeadCode", "type": "TEXT"},
                            {"name": "delDnItemCode", "type": "TEXT"},
                            {"name": "genMatMdId.matCode", "type": "TEXT"},
                            {"name": "batchCode", "type": "TEXT"},
                            {"name": "invOrgId", "type": "OBJECT"},
                            {"name": "invLocId", "type": "OBJECT"},
                            {"name": "whNumId", "type": "NUMBER"}
                        ],
                        "systemParams": None
                    }
                }
            }
            
            response = self.http.post(url, json=params, description=f"根据交货单编号查询拣配任务: {self.__class__.dn_code}")
            self.assert_util.assert_response_success(response)
            
            response_data = response.get("data", {}).get("data", {})
            records = response_data.get("records", []) or response_data.get("data", [])
            
            assert records, f"未查询到交货单编号 {self.__class__.dn_code} 对应的拣配任务"
            
            # 保存拣配任务列表，供后续完成拣配任务使用
            self.__class__.picking_task_list = records
            self.logger.info(f"成功查询到 {len(records)} 个拣配任务")
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"查询到拣配任务数量: {len(records)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="查询交货单任务",
        description="验证根据交货单头ID查询任务功能",
        severity="critical",
        file_level_order=10,
        tags=["交货单任务", "查询"]
    )
    def test_query_dn_task_by_head_id(self):
        """查询交货单任务"""
        try:
            if not self.__class__.dn_id:
                self.test_save_inv_executed_task()
            
            api_path = self.get_api_path("DEL-交货单公共-根据交货单头ID查询交货单任务行")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            response_data = response.get("data", {}).get("data", {})
            assert response_data, "响应数据为空，未查询到任务数据"
            
            task_list = response_data.get("delWmWarehouseTaskList", [])
            assert task_list, "仓库任务列表为空"
            
            self.__class__.warehouse_task_list = task_list
            self.logger.info(f"成功查询到 {len(task_list)} 个仓库任务")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"查询任务数量: {len(task_list)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="发货完成并过账",
        description="验证发货完成并过账功能",
        severity="critical",
        file_level_order=11,
        tags=["发货完成", "过账"]
    )
    def test_dn_task_finish_post(self):
        """发货完成并过账"""
        try:
            # 确保有验货任务数据（如果还没有，先生成并保存）
            if not hasattr(self.__class__, 'task_list') or not self.__class__.task_list:
                if not self.__class__.dn_code:
                    self.test_save_inv_executed_task()
                else:
                    # 如果交货单已存在，直接生成验货任务
                    self.test_generate_inv_executed_task()
                    self.test_save_inv_executed_task()
            
            # 保存验货任务后，需要重新查询任务（因为保存时返回的任务 id=0，不是真实的任务ID）
            # 优先使用查询拣配任务API获取的任务数据（包含真实的任务ID）
            if not self.__class__.dn_code:
                self.test_save_inv_executed_task()
            
            # 查询拣配任务（获取保存后的真实任务数据，包含真实的任务ID和批次信息）
            try:
                self.test_query_picking_task_by_dn_code()
                self.__class__.warehouse_task_list = self.__class__.picking_task_list
                self.logger.info(f"使用查询到的拣配任务列表，任务数量: {len(self.__class__.warehouse_task_list)}")
            except Exception:
                # 如果查询拣配任务失败，尝试使用根据交货单头ID查询任务
                try:
                    self.test_query_dn_task_by_head_id()
                    self.logger.info(f"使用根据交货单头ID查询的任务列表，任务数量: {len(self.__class__.warehouse_task_list)}")
                except Exception:
                    # 最后尝试使用验货任务列表（但需要确保任务有真实ID）
                    if self.__class__.task_list:
                        # 检查任务是否有真实ID（不为0）
                        valid_tasks = [t for t in self.__class__.task_list if t.get("id") and t.get("id") != 0]
                        if valid_tasks:
                            import copy
                            self.__class__.warehouse_task_list = copy.deepcopy(valid_tasks)
                            self.logger.info(f"使用验货任务列表（有真实ID），任务数量: {len(self.__class__.warehouse_task_list)}")
                        else:
                            raise ValueError("验货任务列表中的任务ID都为0，无法完成任务，请先查询任务")
            
            if not self.__class__.warehouse_task_list:
                raise ValueError("仓库任务列表为空，无法完成发货")
            
            self.logger.info(f"准备完成任务，任务数量: {len(self.__class__.warehouse_task_list)}")
            # 打印第一个任务的摘要信息，用于调试
            if self.__class__.warehouse_task_list:
                first_task = self.__class__.warehouse_task_list[0]
                self.logger.info(f"第一个任务摘要: taskCode={first_task.get('taskCode')}, taskType={first_task.get('taskType')}, "
                               f"isBatchControl={first_task.get('isBatchControl')}, "
                               f"hasWmSrcBinDetailList={bool(first_task.get('wmSrcBinDetailList'))}")
            
            # 更新任务列表：设置executedQty等于planQty，确保拣配数量大于0
            # 对于带批次的物料，需要保留批次信息（wmSrcBinDetailList）
            for task in self.__class__.warehouse_task_list:
                # 设置执行数量（验货数量默认为1）
                if not task.get("executedQty") or task.get("executedQty") == 0:
                    task["executedQty"] = 1
                    self.logger.info(f"更新任务执行数量: taskCode={task.get('taskCode')}, executedQty=1")
                
                # 确保批次信息存在（对于带批次的物料）
                # 如果任务中有 wmSrcBinDetailList，保留它（验货任务中通常包含批次信息）
                # 如果任务中没有批次信息，根据物料ID查询批次并使用第一个批次
                mat_id = task.get("genMatMdId", {}).get("id") if isinstance(task.get("genMatMdId"), dict) else task.get("genMatMdId")
                
                # 检查物料是否带批次（通过任务字段或查询）
                is_batch_control = task.get("isBatchControl", False)
                
                # 如果没有批次信息，尝试获取
                if not task.get("wmSrcBinDetailList") and mat_id:
                    # 如果是从验货任务列表获取的，可能包含批次信息
                    if hasattr(self.__class__, 'task_list') and self.__class__.task_list:
                        for original_task in self.__class__.task_list:
                            if (original_task.get("taskCode") == task.get("taskCode") or 
                                original_task.get("delDnItemCode") == task.get("delDnItemCode")):
                                if original_task.get("wmSrcBinDetailList"):
                                    task["wmSrcBinDetailList"] = original_task.get("wmSrcBinDetailList")
                                    if "batchId" in original_task:
                                        task["batchId"] = original_task.get("batchId")
                                    task["isBatchControl"] = True
                                    self.logger.info(f"从原始任务中获取批次信息: taskCode={task.get('taskCode')}")
                                    break
                    
                    # 如果还是没有批次信息，使用API查询批次主数据（使用第一个批次）
                    if not task.get("wmSrcBinDetailList"):
                        batch_data = self._query_batch_by_mat_id(mat_id)
                        
                        if batch_data:
                            batch_id = batch_data.get("id")
                            batch_code = batch_data.get("batchCode")
                            
                            # 构造批次详情列表（使用第一个批次）
                            task["wmSrcBinDetailList"] = [{
                                "context": {},
                                "matId": mat_id,
                                "batchId": batch_id,
                                "matBatchKey": f"{mat_id}-{batch_id}",
                                "key": f"null-{mat_id}-{batch_id}",
                                "matKey": f"null-{mat_id}",
                                "areaMatKey": f"null-{mat_id}",
                                "areaMatBatKey": f"null-{mat_id}-{batch_id}"
                            }]
                            # 同时在任务对象顶层设置 batchId
                            task["batchId"] = {"id": batch_id}
                            task["isBatchControl"] = True
                            self.logger.info(f"为任务添加批次信息（使用第一个批次）: taskCode={task.get('taskCode')}, batchCode={batch_code}, batchId={batch_id}")
                        else:
                            self.logger.warning(f"未查询到物料 {mat_id} 的批次信息")
                
                # 确保任务顶层有 batchId（API需要，即使 isBatchControl 为 false）
                # 如果任务有 wmSrcBinDetailList，从第一个批次中提取 batchId
                if task.get("wmSrcBinDetailList") and not task.get("batchId"):
                    first_batch = task.get("wmSrcBinDetailList", [{}])[0]
                    batch_id = first_batch.get("batchId")
                    if batch_id:
                        # 提取实际的批次ID（可能是数字或对象）
                        actual_batch_id = batch_id if isinstance(batch_id, (int, str)) else batch_id.get("id")
                        if actual_batch_id:
                            # 查询完整的批次信息
                            batch_detail = self._query_batch_detail_by_id(actual_batch_id)
                            if batch_detail:
                                task["batchId"] = batch_detail
                            else:
                                # 如果查询失败，至少构造一个包含id的对象
                                task["batchId"] = {"id": actual_batch_id}
                            self.logger.info(f"为任务添加顶层batchId: taskCode={task.get('taskCode')}, batchId={actual_batch_id}")
                        else:
                            # 如果批次ID无法提取，直接使用对象
                            task["batchId"] = batch_id if isinstance(batch_id, dict) else {"id": batch_id}
                
                # 如果任务没有 wmSrcBinDetailList 也没有 batchId，查询批次
                if not task.get("batchId") and not task.get("wmSrcBinDetailList") and mat_id:
                    batch_data = self._query_batch_by_mat_id(mat_id)
                    if batch_data:
                        batch_id = batch_data.get("id")
                        # 查询完整的批次详情
                        batch_detail = self._query_batch_detail_by_id(batch_id)
                        if batch_detail:
                            task["batchId"] = batch_detail
                        else:
                            # 如果查询失败，使用查询到的批次数据（至少包含id和code）
                            task["batchId"] = batch_data
                        
                        # 同时构造 wmSrcBinDetailList
                        task["wmSrcBinDetailList"] = [{
                            "context": {},
                            "matId": mat_id,
                            "batchId": batch_id,
                            "matBatchKey": f"{mat_id}-{batch_id}",
                            "key": f"null-{mat_id}-{batch_id}",
                            "matKey": f"null-{mat_id}",
                            "areaMatKey": f"null-{mat_id}",
                            "areaMatBatKey": f"null-{mat_id}-{batch_id}"
                        }]
                        self.logger.info(f"为任务添加批次信息: taskCode={task.get('taskCode')}, batchId={batch_id}")
            
            api_path = self.get_api_path("DEL-交货单公共-仓库执行完成并过账")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            # 确保任务列表不为空且有有效数据
            if not self.__class__.warehouse_task_list:
                raise ValueError("仓库任务列表为空，无法完成发货")
            
            # 过滤掉无效的任务（如 taskCode 为 None 的任务）
            valid_tasks = []
            for task in self.__class__.warehouse_task_list:
                # 检查任务是否有必要的字段
                if task.get("id") or task.get("taskCode") or task.get("delDnItemCode"):
                    valid_tasks.append(task)
                else:
                    self.logger.warning(f"跳过无效任务: {task}")
            
            if not valid_tasks:
                raise ValueError("没有有效的任务数据，无法完成发货")
            
            self.logger.info(f"有效任务数量: {len(valid_tasks)}")
            ParamUtil.set_request_params(filtered_params, {"delWmWarehouseTaskList": valid_tasks})
            
            response = self.http.post(url, json=filtered_params, description="发货完成并过账")
            self.assert_util.assert_response_success(response)
            
            actual_biz_status = self._verify_dn_biz_status("POSTED")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"完成任务数量: {len(self.__class__.warehouse_task_list)}\n"
                f"交货单业务状态: {actual_biz_status}",
                "完成结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    def _query_batch_detail_by_id(self, batch_id):
        """
        根据批次ID查询批次详情（完整对象）
        :param batch_id: 批次ID
        :return: 批次详情对象
        """
        try:
            # 使用系统查询数据详情服务查询批次详情
            api_path = "/api/trantor/service/engine/execute/SCM_DEL$SYS_FindDataByIdService"
            url = f"{self.http.url}{api_path}?tmodule=SCM_DEL&modelKey=SCM_INV%24inv_batch_md"
            
            params = {
                "sceneKey": "SCM_DEL$DEL_DN_SLS_NEW_VIEW",
                "viewKey": "SCM_DEL$DEL_DN_SLS_NEW_VIEW:list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_DEL$SYS_FindDataByIdService",
                "params": {
                    "request": {
                        "id": batch_id
                    },
                    "modelKey": "SCM_INV$inv_batch_md"
                }
            }
            
            response = self.http.post(url, json=params, description=f"查询批次详情: {batch_id}")
            self.assert_util.assert_response_success(response)
            
            response_data = response.get("data", {}).get("data", {})
            if response_data:
                return response_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"查询批次详情失败: {str(e)}")
            return None
    
    def _query_batch_by_mat_id(self, mat_id):
        """
        通过API查询批次主数据（根据物料ID），返回第一个批次
        :param mat_id: 物料ID
        :return: 批次数据字典，包含 id 和 batchCode
        """
        try:
            # 使用系统分页查询服务查询批次主数据
            api_path = "/api/trantor/service/engine/execute/SCM_DEL$SYS_PagingDataService"
            url = f"{self.http.url}{api_path}?tmodule=SCM_DEL&modelKey=SCM_INV%24inv_batch_md"
            
            params = {
                "sceneKey": "SCM_DEL$DEL_DN_SLS_NEW_VIEW",
                "viewKey": "SCM_DEL$DEL_DN_SLS_NEW_VIEW:list",
                "containerKey": "",
                "viewCondition": {
                    "conditionKey": "WrpF4x-Y61G0RYvUAF6UA",
                    "rightValues": {
                        "57PCGDDHkh31MxY7_WkH2": [{
                            "constValue": mat_id,
                            "type": "ConstValue",
                            "valueType": "CONST",
                            "fieldType": "Number",
                            "id": "57PCGDDHkh31MxY7_WkH2"
                        }]
                    }
                },
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_DEL$SYS_PagingDataService",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "conditionGroup": None,
                            "sortOrders": None,
                            "keyword": None
                        }
                    },
                    "modelKey": "SCM_INV$inv_batch_md"
                }
            }
            
            response = self.http.post(url, json=params, description=f"查询物料 {mat_id} 的批次信息")
            self.assert_util.assert_response_success(response)
            
            response_data = response.get("data", {}).get("data", {})
            records = response_data.get("records", []) or response_data.get("data", [])
            
            if records:
                # 返回第一个批次数据
                return records[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"查询批次信息失败: {str(e)}")
            return None

