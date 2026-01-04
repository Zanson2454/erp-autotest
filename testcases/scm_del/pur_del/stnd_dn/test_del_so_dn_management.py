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
from testcases.scm_del import ScmDelBaseTest
from testcases.scm_sls import SlsBase
from utils.report_util import a, case_decorator
from data_factory.del_po_dn_factory import DelPoDnFactory
from utils.param_util import ParamUtil
from utils.cache_util import CacheUtil
from data_factory.base import DataFactory


@allure.epic("交货管理")
@allure.feature("标准销售交货单")
class TestDelSoDnManagement(ScmDelBaseTest):
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
        
        # 初始化销售配置
        cls._init_sls_config()
        
        # 初始化销售订单工厂（用于创建销售订单）
        cls._init_sls_base()
        
        # 更新交货单行项目配置（拣配）
        cls._update_dn_item_type_config()
        
        cls.logger.info("标准销售交货单测试类初始化完成")
    
    @classmethod
    def _update_dn_item_type_config(cls):
        """更新配置：1.交货单行项目类型库存执行标记；2.SO行项目类型自动交货标记"""
        try:
            # 1. 从缓存获取标准发货类型ID（交货单行项目类型）
            dn_item_type_list = cls.del_cache_data.get("pur_config", {}).get("dn_item_type_info", [])
            item_type_id = next(
                (item["id"] for item in dn_item_type_list if item.get("dn_item_type_code") == "s_send"),
                None
            )
            if not item_type_id:
                cls.logger.warning("未找到标准发货(s_send)类型配置")
                return
            
            cls.db.update(
                table="del_dn_item_type_cf",
                data={"is_inv_executing": 1},
                where="id = %s",
                params=[item_type_id]
            )
            cls._dn_item_type_id = item_type_id
            cls.logger.info(f"成功更新交货单行项目类型配置：标准发货(ID={item_type_id})库存执行标记设为启用")
            
            # 更新SO行项目类型自动交货配置
            if cls.sls_cache_data:
                so_item_type_list = cls.sls_cache_data.get("sls_config", {}).get("so_item_type_info", [])
                so_item_type_id = next(
                    (item["id"] for item in so_item_type_list if item.get("so_item_type_code") == "NORM"),
                    None
                )
                if so_item_type_id:
                    cls.db.update(
                        table="sls_so_item_type_cf",
                        data={"is_auto_delivery": 1},
                        where="id = %s",
                        params=[so_item_type_id]
                    )
                    cls._so_item_type_id = so_item_type_id
                    cls.logger.info(f"成功更新SO行项目类型配置：常规销售(ID={so_item_type_id})自动交货标记设为启用")
        except Exception as e:
            cls.logger.error(f"更新项目类型配置失败: {str(e)}")
    
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
    
    @classmethod
    def _init_cache_data(cls):
        """初始化缓存数据"""
        if not cls.md_cache_data:
            return
            
        # 物料信息
        mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0]
        cls.mat_id = mat_info.get("id")
        cls.mat_code = mat_info.get("mat_code")
        
        # 组织信息
        org_info = cls.md_cache_data.get("org_info", {})
        cls.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id")
        cls.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id")
        cls.sls_org_id = org_info.get("sls_org_info", [{}])[0].get("id")
        cls.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id")
        
        # 合作伙伴信息
        partner_info = cls.md_cache_data.get("partner_info", {})
        cls.cust_id = partner_info.get("cust_info", [{}])[0].get("id")
        
        # 初始化数据
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info", [{}])[0].get("curr_id") if cls.init_data.get("currency_info") else 2000001
    
    @classmethod
    def _init_sls_config(cls):
        """初始化销售配置"""
        # 加载销售模块缓存数据
        if not hasattr(cls, 'sls_cache_data') or not cls.sls_cache_data:
            DataFactory.init_sql_cache(
                sql_config_path=str(project_root / "config" / "erp" / "sls_init_sql.yaml"),
                db_config_name="erp_db",
                cache_key="sls_init_cache",
                cache_dir="testdata/cache"
            )
            cls.sls_cache_data = CacheUtil.get('sls_init_cache')
        
        if cls.sls_cache_data:
            sls_config = cls.sls_cache_data.get("sls_config", {})
            cls.so_type_id = sls_config.get("so_type_info", [{}])[0].get("id")
            
            so_item_types = sls_config.get("so_item_type_info", [])
            cls.so_item_type_id = next(
                (item.get("id") for item in so_item_types if item.get("so_item_type_code") == "STND"),
                None
            )
        
        # 初始化订单配置数据（从 init_data 获取）
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.curr_id = currency_info[0].get("curr_id")
            else:
                cls.curr_id = 2000001
            
            exchange_rate_type_info = cls.init_data.get("exchange_rate_type_info") or []
            if exchange_rate_type_info:
                cls.exchange_rate_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                cls.exchange_rate_type_id = None
            
            country_info = cls.init_data.get("country_info") or []
            if country_info:
                cls.coun_id = country_info[0].get("coun_id")
            else:
                cls.coun_id = None
        else:
            cls.curr_id = 2000001
            cls.exchange_rate_type_id = None
            cls.coun_id = None
    
    @classmethod
    def _init_sls_base(cls):
        """初始化销售订单基础类（用于创建销售订单）"""
        # 加载销售模块API配置
        from utils.yaml_util import YamlUtil
        yaml_util = YamlUtil()
        sls_api_path = project_root / "config" / "api" / "scm_sls" / "sls_api_path.yaml"
        sls_api_params_path = project_root / "config" / "api" / "scm_sls" / "sls_api_params.yaml"
        cls.sls_apis = yaml_util.read_yaml(sls_api_path).get("apis", {})
        cls.sls_api_params = yaml_util.read_yaml(sls_api_params_path).get("api_params", {})
        
        # 创建 SlsBase 实例用于创建销售订单
        # 使用类方法创建实例，避免复杂的初始化
        cls.sls_base = type('SlsBaseProxy', (SlsBase,), {})()
        
        # 设置必要的属性
        cls.sls_base.http = cls.http
        cls.sls_base.apis = cls.sls_apis
        cls.sls_base.api_params = cls.sls_api_params
        cls.sls_base.mock_util = cls.mock_util
        cls.sls_base.logger = cls.logger
        cls.sls_base.init_data = cls.init_data
        cls.sls_base.md_cache_data = cls.md_cache_data
        cls.sls_base.sls_cache_data = cls.sls_cache_data
        cls.sls_base.db = cls.db
        cls.sls_base.assert_util = cls.assert_util
        cls.sls_base.yaml_util = cls.yaml_util
        cls.sls_base.path_params = {"tmodule": "SCM_SLS"}
        cls.sls_base.nickname = cls.nickname
        cls.sls_base.user_id = cls.user_id
        cls.sls_base.exchange_rate_type_id = cls.exchange_rate_type_id
        cls.sls_base.curr_id = cls.curr_id
        cls.sls_base.coun_id = cls.coun_id
        
        # 设置必要的缓存数据引用（用于 SlsBase 的方法）
        if cls.md_cache_data:
            partner_info = cls.md_cache_data.get("partner_info", {})
            cls.sls_base.cust_id = partner_info.get("cust_info", [{}])[0].get("id") if partner_info.get("cust_info") else None
            
            org_info = cls.md_cache_data.get("org_info", {})
            cls.sls_base.sls_org_id = org_info.get("sls_org_info", [{}])[0].get("id") if org_info.get("sls_org_info") else None
            cls.sls_base.sls_dc_id = org_info.get("sls_dc_md", [{}])[0].get("id") if org_info.get("sls_dc_md") else None
            cls.sls_base.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id") if org_info.get("gr_come_org_info") else None
            cls.sls_base.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id") if org_info.get("inv_org_info") else None
            cls.sls_base.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id") if org_info.get("inv_loc_info") else None
            
            # 物料信息
            mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])
            if mat_info:
                cls.sls_base.mat_id = mat_info[0].get("id")
                cls.sls_base.mat_code = mat_info[0].get("mat_code")
                cls.sls_base.mat_name = mat_info[0].get("mat_name")
        
        # 设置必要的缓存数据属性
        if cls.sls_cache_data:
            sls_config = cls.sls_cache_data.get("sls_config", {})
            cls.sls_base.so_type_info = sls_config.get("so_type_info", [])
            cls.sls_base.ORDER_TYPES = cls.sls_base.so_type_info
            cls.sls_base.so_item_type_info = sls_config.get("so_item_type_info", [])
            cls.sls_base.ORDER_LINE_TYPES = cls.sls_base.so_item_type_info
            # 订单类型ID
            cls.sls_base.stnd_so_type_id = next(
                (item.get("id") for item in cls.sls_base.so_type_info if item.get("so_type_code") == "STND"),
                None
            )
            # 行项目类型ID
            cls.sls_base.stnd_so_item_type_id = next(
                (item.get("id") for item in cls.sls_base.so_item_type_info if item.get("so_item_type_code") == "STND"),
                None
            )
        
        # 设置必要的初始化数据属性
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.sls_base.curr_id = currency_info[0].get("curr_id")
            else:
                cls.sls_base.curr_id = 2000001
        
        # 初始化订单相关配置（与SlsBase中setup_class一致）
        import random
        cls.sls_base.addr_id = None
        cls.sls_base.addr_detail = None
        cls.sls_base.cust_person_name = None
        cls.sls_base.cust_phone = None
        cls.sls_base.sls_person_obj = None
        cls.sls_base.sls_phone = None
        cls.sls_base.sls_person_name = None
        cls.sls_base.sls_partner_links = None
        cls.sls_base.so_items = None
        cls.sls_base.sls_org_obj = None
        cls.sls_base.mat_obj = None
        cls.sls_base.so_head_id_save = None
        cls.sls_base.so_head_id_submit = None
        cls.sls_base.so_item_id = None
        cls.sls_base.so_item_data = None
        cls.sls_base.render_qty = random.randint(1, 99)
        cls.sls_base.so_data_render = None
        cls.sls_base.so_data_price = None
        cls.sls_base.priceIdempotent = None
        cls.sls_base.so_head_data = None
    
    
    
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
            # 使用 SlsBase 创建已生效的销售订单
            self.__class__.so_id = self.sls_base.create_sales_order(order_type="STND", submit=True)
            
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
            
            # 使用 SlsBase 的 create_delivery_order 方法创建交货单
            delivery_id = self.sls_base.create_delivery_order(self.__class__.so_id)
            
            # API返回为空字典，需要从数据库查询
            if not delivery_id or delivery_id == {}:
                # 从数据库查询交货单
                so_code = self.__class__.so_code
                query_sql = """
                    SELECT id, dn_code, del_status 
                    FROM del_dn_head_tr 
                    WHERE doc_code = %s AND bt_class = 'SLS'
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                dn_result = self.db.query(query_sql, [so_code])
                if dn_result:
                    self.__class__.dn_id = dn_result[0].get("id")
                else:
                    raise ValueError(f"❌ API未返回交货单ID，且数据库中也查不到交货单: so_code={so_code}")
            else:
                self.__class__.dn_id = delivery_id
            
            # 从数据库查询交货单信息
            query_sql = """
                SELECT dn_code, del_status 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
            dn_result = self.db.query(query_sql, [self.__class__.dn_id])
            if dn_result:
                self.__class__.dn_code = dn_result[0].get("dn_code")
                del_status = dn_result[0].get("del_status")
            else:
                raise ValueError(f"未查询到交货单数据: dn_id={self.__class__.dn_id}")
            
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
        description="提交草稿态的销售交货单",
        severity="critical",
        file_level_order=2,
        tags=["交货", "销售交货单", "提交"]
    )
    def test_submit_so_dn(self):
        """提交销售交货单"""
        try:
            if not self.__class__.dn_id:
                self.test_create_standard_so_dn()
            
            result = self.dn_factory.submit_delivery_note(dn_id=self.__class__.dn_id)
            
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
        title="生成拣配任务",
        description="验证生成拣配任务功能",
        severity="critical",
        file_level_order=6,
        tags=["拣配任务", "生成"]
    )
    def test_generate_inv_executed_task(self):
        """生成拣配任务"""
        try:
            if not self.__class__.dn_id:
                self.test_submit_so_dn()
            
            api_path = self.get_api_path("DEL-APP端仓库执行任务平铺服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            response_data = response.get("data", {}).get("data", {})
            assert response_data, "响应数据为空，未生成拣配任务"
            
            task_list = response_data.get("delWmWarehouseTaskList", [])
            assert task_list, "拣配任务列表为空"
            
            self.__class__.task_list = task_list
            self.logger.info(f"成功生成 {len(task_list)} 个拣配任务")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"生成拣配任务数量: {len(task_list)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="保存拣配任务",
        description="验证保存拣配任务功能",
        severity="critical",
        file_level_order=7,
        tags=["拣配任务", "保存"]
    )
    def test_save_inv_executed_task(self):
        """保存拣配任务"""
        try:
            if not self.__class__.task_list:
                self.test_generate_inv_executed_task()
            
            if not self.__class__.task_list:
                raise ValueError("拣配任务列表为空，无法保存")
            
            api_path = self.get_api_path("仓库执行任务保存事件服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"delWmWarehouseTaskList": self.__class__.task_list})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            actual_biz_status = self._verify_dn_biz_status("TASK_EXECUTING")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"保存拣配任务数量: {len(self.__class__.task_list)}\n"
                f"交货单业务状态: {actual_biz_status}",
                "保存结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="交货单列表下拉查看拣配",
        description="验证交货单列表下拉查看拣配功能",
        severity="critical",
        file_level_order=8,
        tags=["交货单", "拣配", "查看"]
    )
    def test_query_dn_inv_executed(self):
        """交货单列表下拉查看拣配"""
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
            assert response_data, "响应数据为空，未查询到拣配数据"
            
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
        title="查询交货单拣配任务",
        description="验证根据交货单头ID查询拣配任务功能",
        severity="critical",
        file_level_order=9,
        tags=["交货单拣配任务", "查询"]
    )
    def test_query_dn_task_by_head_id(self):
        """查询交货单拣配任务"""
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
            assert response_data, "响应数据为空，未查询到拣配任务数据"
            
            task_list = response_data.get("delWmWarehouseTaskList", [])
            assert task_list, "拣配任务列表为空"
            
            self.__class__.warehouse_task_list = task_list
            self.logger.info(f"成功查询到 {len(task_list)} 个拣配任务")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"查询拣配任务数量: {len(task_list)}", "任务统计")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准销售交货单",
        title="拣配完成并过账",
        description="验证拣配完成并过账功能",
        severity="critical",
        file_level_order=10,
        tags=["拣配完成", "过账"]
    )
    def test_dn_task_finish_post(self):
        """拣配完成并过账"""
        try:
            if not self.__class__.warehouse_task_list:
                self.test_query_dn_task_by_head_id()
            
            if not self.__class__.warehouse_task_list:
                raise ValueError("拣配任务列表为空，无法完成拣配")
            
            api_path = self.get_api_path("DEL-交货单公共-仓库执行完成并过账")
            params, url = self.get_api_params(api_path)
            
            # 补充拣配任务必要信息：executedQty和batchId
            for task in self.__class__.warehouse_task_list:
                # 设置已拣配数量 = 计划数量
                task["executedQty"] = task.get("planQty", 0)
                
                # 从数据库动态查询批次ID
                mat_id = task.get("genMatMdId", {}).get("id")
                inv_org_id = task.get("invOrgId", {}).get("id")
                inv_loc_id = task.get("invLocId", {}).get("id")
                source_wh_bin = task.get("sourceWhBin", {}).get("id")
                
                batch_sql = """
                    SELECT batch_id
                    FROM inv_stk_ba 
                    WHERE mat_id = %s 
                      AND inv_org_id = %s 
                      AND inv_loc_id = %s 
                      AND inv_bin_id = %s 
                      AND batch_id IS NOT NULL 
                      AND stk_qty > 1000
                      AND deleted = 0
                    LIMIT 1
                """
                batch_result = self.db.query(batch_sql, [mat_id, inv_org_id, inv_loc_id, source_wh_bin])
                
                if batch_result and batch_result[0].get("batch_id"):
                    batch_id = batch_result[0].get("batch_id")
                    task["batchId"] = {"id": batch_id}
                    self.logger.info(f"从数据库查询到批次ID: {batch_id}")
                else:
                    self.logger.warning(f"未查询到满足条件的批次: mat_id={mat_id}, inv_org_id={inv_org_id}, inv_loc_id={inv_loc_id}, source_wh_bin={source_wh_bin}")
                    # 如果没有查到，跳过添加batchId
                    pass
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["delWmWarehouseTaskList"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {"delWmWarehouseTaskList": self.__class__.warehouse_task_list})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            actual_biz_status = self._verify_dn_biz_status("POSTED")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"完成拣配任务数量: {len(self.__class__.warehouse_task_list)}\n"
                f"交货单业务状态: {actual_biz_status}",
                "完成结果"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

