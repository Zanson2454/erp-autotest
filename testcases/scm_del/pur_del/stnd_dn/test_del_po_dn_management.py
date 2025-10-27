"""
标准采购交货单测试
"""
import allure
import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del import ScmDelBaseTest
from utils.report_util import a, case_decorator
from data_factory.del_po_dn_factory import DelPoDnFactory
from data_factory.pur_po_factory import PurPoFactory
from utils.param_util import ParamUtil


@allure.epic("交货管理")
@allure.feature("标准采购交货单")
class TestDelPoDnManagement(ScmDelBaseTest):
    """标准采购交货单测试类"""
    
    TEST_REMARK = "执行自动化测试备注SQW"
    PLAN_DEL_QTY = 10  # 计划交货数量（同时作为批次数量）
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.dn_id = None
        cls.dn_code = None
        cls.po_id = None
        cls.po_code = None
        cls.po_item_id = None
        cls.task_list = None  # 存储生成的清点任务列表
        cls.warehouse_task_list = None  # 存储查询到的仓库任务列表
        
        if cls.md_cache_data:
            mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0]
            org_info = cls.md_cache_data.get("org_info", {})
            partner_info = cls.md_cache_data.get("partner_info", {})
            
            cls.mat_id = mat_info.get("id")
            cls.mat_code = mat_info.get("mat_code")
            cls.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id")
            cls.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id")
            cls.pur_org_id = org_info.get("pur_org_info", [{}])[0].get("id")
            cls.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id")
            cls.vend_id = partner_info.get("vend_info", [{}])[0].get("id")
            cls.pur_employee_id = org_info.get("employee_info", [{}])[0].get("id")
        
        if cls.init_data:
            cls.pur_curr_id = cls.init_data.get("currency_info", [{}])[0].get("curr_id")
            cls.uom_pur_id = cls.init_data.get("uom_info", {}).get("qty_uom_info", [{}])[0].get("uom_id")
            cls.tax_rate_id = cls.init_data.get("tax_info", [{}])[0].get("id")
        
        # 从采购缓存数据获取采购配置
        if not hasattr(cls, 'pur_cache_data') or not cls.pur_cache_data:
            from utils.cache_util import CacheUtil
            from data_factory.base import DataFactory
            
            DataFactory.init_sql_cache(
                sql_config_path=str(project_root / "config" / "erp" / "pur_init_sql.yaml"),
                db_config_name="erp_db",
                cache_key="pur_init_cache",
                cache_dir="testdata/cache"
            )
            cls.pur_cache_data = CacheUtil.get('pur_init_cache')
        
        if cls.pur_cache_data:
            pur_config = cls.pur_cache_data.get("pur_config", {})
            cls.po_type_id = pur_config.get("po_type_info", [{}])[0].get("id")
            
            po_item_types = pur_config.get("po_item_type_info", [])
            cls.po_item_type_id = next(
                (item.get("id") for item in po_item_types if item.get("po_item_type") == "STND"),
                None
            )
        
        cls.logger.info("标准采购交货单测试类初始化完成")
    
    # @classmethod
    # def teardown_class(cls):
    #     """清理测试数据"""
    #     try:
    #         cls.db.delete(
    #             table="del_dn_head_tr",
    #             where="remark like %s",
    #             params=[f"%{cls.TEST_REMARK}%"]
    #         )
    #         cls.db.delete(
    #             table="del_dn_item_tr",
    #             where="item_remark like %s",
    #             params=[f"%{cls.TEST_REMARK}%"]
    #         )
    #         cls.logger.info("测试数据清理完成")
    #     except Exception as e:
    #         cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _create_dn_factory(self):
        """创建交货单工厂实例"""
        return DelPoDnFactory(
            http_client=self.http,
            apis=self.apis,
            api_params=self.api_params,
            mock_util=self.mock_util,
            logger=self.logger,
            init_data=self.init_data,
            md_cache_data=self.md_cache_data,
            del_cache_data=self.del_cache_data
        )
    
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
    
    def _create_po_for_dn(self):
        """创建采购订单用于后续创建交货单"""
        try:
            current_ts = int(datetime.now().timestamp() * 1000)
            
            mat_items = [{
                "mat_id": str(self.mat_id),
                "mat_code": self.mat_code,
                "inv_org_id": str(self.inv_org_id),
                "inv_loc_id": str(self.inv_loc_id),
                "uom_pur_id": str(self.uom_pur_id),
                "qty": 100,
                "price": 50,
                "po_item_type_id": str(self.po_item_type_id),
                "tax_rate_id": str(self.tax_rate_id),
                "delivery_date": current_ts,
                "note": self.TEST_REMARK
            }]
            
            # 加载采购模块的API配置
            from utils.yaml_util import YamlUtil
            yaml_util = YamlUtil()
            pur_api_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_path.yaml"
            pur_api_params_path = Path(project_root) / "testdata" / "scm_pur" / "pur_api_params.yaml"
            pur_apis = yaml_util.read_yaml(pur_api_path).get("apis", {})
            pur_api_params = yaml_util.read_yaml(pur_api_params_path).get("api_params", {})
            
            po_factory = PurPoFactory(
                http_client=self.http,
                apis=pur_apis,
                api_params=pur_api_params,
                mock_util=self.mock_util,
                logger=self.logger,
                init_data=self.init_data,
                md_cache_data=self.md_cache_data,
                pur_cache_data=self.pur_cache_data
            )
            
            result = po_factory.create_standard_po(
                mat_items=mat_items,
                business_date=current_ts,
                pur_remark=self.TEST_REMARK
            )
            
            # 从数据库查询最新创建的采购订单行（因为接口可能不返回完整信息）
            query_sql = """
                SELECT po_item_code, po_code, id 
                FROM pur_po_item_tr 
                WHERE note like %s
                ORDER BY created_at DESC 
                LIMIT 1
            """
            po_items = self.db.query(query_sql, [f"%{self.TEST_REMARK}%"])
            
            if po_items:
                po_item = po_items[0]
                self.__class__.po_item_id = po_item.get("id")
                self.__class__.po_code = po_item.get("po_code")
                self.logger.info(f"成功创建采购订单: po_code={self.__class__.po_code}, po_item_id={self.__class__.po_item_id}")
            else:
                raise ValueError("未查询到采购订单行数据")
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建采购订单失败: {str(e)}")
            raise
    
    @case_decorator(
        story="标准采购交货单",
        title="创建标准采购交货单",
        description="创建标准采购交货单，验证创建成功",
        severity="critical",
        file_level_order=1,
        tags=["交货", "采购交货单", "创建"]
    )
    def test_create_standard_po_dn(self):
        """创建标准采购交货单"""
        try:
            if not self.__class__.po_item_id:
                self._create_po_for_dn()
            
            dn_factory = self._create_dn_factory()
            
            # 准备批次信息
            batch_info = [
                {
                    "batchType": "INBOUND",
                    "batchCode": f"BAT{self.mock_util.get_timestamp()}",
                    "charaClassId": None,
                    "quantity": self.PLAN_DEL_QTY,
                    "charaValue": []
                }
            ]
            
            result = dn_factory.create_po_delivery_note(
                po_item_id_list=[self.__class__.po_item_id],
                plan_del_qty=self.PLAN_DEL_QTY,
                remark=self.TEST_REMARK,
                batch_info=batch_info
            )
            
            self.__class__.dn_id = result.get("dn_id")
            self.__class__.dn_code = result.get("dn_code")
            del_status = result.get("del_status")
            
            assert self.__class__.dn_id, "交货单ID不能为空"
            assert self.__class__.dn_code, "交货单编码不能为空"
            assert del_status == "DRAFT", f"交货单状态不符合预期: 期望=DRAFT, 实际={del_status}"
            
            a.text(
                f"交货单ID: {self.__class__.dn_id}\n"
                f"交货单编码: {self.__class__.dn_code}\n"
                f"交货状态: {del_status}\n"
                f"计划交货数量: {self.PLAN_DEL_QTY}\n"
                f"采购订单编码: {self.__class__.po_code}\n"
                f"采购订单行ID: {self.__class__.po_item_id}",
                "交货单信息"
            )
            a.json(result.get("response", {}), "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购交货单",
        title="提交采购交货单",
        description="提交草稿态的采购交货单",
        severity="critical",
        file_level_order=2,
        tags=["交货", "采购交货单", "提交"]
    )
    def test_submit_po_dn(self):
        """提交采购交货单"""
        try:
            if not self.__class__.dn_id:
                self.test_create_standard_po_dn()
            
            dn_factory = self._create_dn_factory()
            result = dn_factory.submit_delivery_note(dn_id=self.__class__.dn_id)
            
            assert result.get("success"), "交货单提交失败"
            
            query_sql = """
                SELECT del_status, dn_code 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
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
        story="标准采购交货单",
        title="查询采购交货单列表",
        description="查询采购交货单列表，验证新建的交货单在列表中",
        severity="critical",
        file_level_order=3,
        tags=["交货", "采购交货单", "查询"]
    )
    def test_query_po_dn_list(self):
        """查询采购交货单列表"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_po_dn()
            
            api_path = self.get_api_path("DEL-交货单公共-数据分页查询服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["btClass", "pageable"], ["params", "request"]
            )
            
            set_dict = {
                "btClass": "PUR",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionGroup": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
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
        story="标准采购交货单",
        title="查询采购交货单详情",
        description="根据交货单ID查询采购交货单详情",
        severity="critical",
        file_level_order=4,
        tags=["交货", "采购交货单", "查询"]
    )
    def test_query_po_dn_detail(self):
        """查询采购交货单详情"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_po_dn()
            
            api_path = self.get_api_path("DEL-交货单详情服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            set_dict = {"id": str(self.__class__.dn_id)}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
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
        story="标准采购交货单",
        title="查询采购交货单行列表",
        description="根据交货单头ID查询交货单行列表",
        severity="critical",
        file_level_order=5,
        tags=["交货", "采购交货单", "行查询"]
    )
    def test_query_po_dn_items(self):
        """查询采购交货单行列表"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_po_dn()
            
            api_path = self.get_api_path("DEL-交货单公共-根据订单ID查询交货单行服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "pageable"], ["params", "request"]
            )
            
            set_dict = {"id": self.__class__.dn_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
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
        story="标准采购交货单",
        title="生成清点任务",
        description="验证生成清点任务功能",
        severity="critical",
        file_level_order=6,
        tags=["清点任务", "生成"]
    )
    def test_generate_inv_executed_task(self):
        """生成清点任务"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_po_dn()
            
            api_path = self.get_api_path("DEL-APP端仓库执行任务平铺服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            set_dict = {"id": self.__class__.dn_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            response_data = response.get("data", {}).get("data", {})
            assert response_data, "响应数据为空，未生成清点任务"
            
            task_list = response_data.get("delWmWarehouseTaskList", [])
            assert task_list, "清点任务列表为空"
            
            self.__class__.task_list = task_list
            self.logger.info(f"成功生成 {len(task_list)} 个清点任务")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"生成任务数量: {len(task_list)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准采购交货单",
        title="保存清点任务",
        description="验证保存清点任务功能",
        severity="critical",
        file_level_order=7,
        tags=["清点任务", "保存"]
    )
    def test_save_inv_executed_task(self):
        """保存清点任务"""
        try:
            if not self.__class__.task_list:
                self.test_generate_inv_executed_task()
            
            if not self.__class__.task_list:
                raise ValueError("清点任务列表为空，无法保存")
            
            api_path = self.get_api_path("仓库执行任务保存事件服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            set_dict = {"delWmWarehouseTaskList": self.__class__.task_list}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            actual_biz_status = self._verify_dn_biz_status("TASK_EXECUTING")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"保存任务数量: {len(self.__class__.task_list)}\n"
                f"交货单业务状态: {actual_biz_status}",
                "保存结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准采购交货单",
        title="查询交货单任务",
        description="验证根据交货单头ID查询任务功能",
        severity="critical",
        file_level_order=8,
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
            
            set_dict = {"id": self.__class__.dn_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
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
        story="标准采购交货单",
        title="收货完成并过账",
        description="验证收货完成并过账功能",
        severity="critical",
        file_level_order=9,
        tags=["收货完成", "过账"]
    )
    def test_dn_task_finish_post(self):
        """收货完成并过账"""
        try:
            if not self.__class__.warehouse_task_list:
                self.test_query_dn_task_by_head_id()
            
            if not self.__class__.warehouse_task_list:
                raise ValueError("仓库任务列表为空，无法完成收货")
            
            api_path = self.get_api_path("DEL-交货单公共-仓库执行完成并过账")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            set_dict = {"delWmWarehouseTaskList": self.__class__.warehouse_task_list}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
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

