"""
组织维度管理测试用例
覆盖组织维度表的增删改查、启用禁用、导入导出等功能
"""
import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("组织维度管理")
class TestOrgDimensionManagement(SysCommonBaseTest):
    """组织维度管理测试类"""
    
    dimension_id = None
    dimension_code = None
    dimension_name = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.dimension_id = None
        cls.dimension_code = None
        cls.dimension_name = None
        cls.logger.info("组织维度管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="org_dimension_cf",
                where="dimension_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("组织维度测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"组织维度测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    # ==================== 创建相关测试 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试创建组织维度",
        description="验证ORG_DIMENSION_CF_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "org_dimension", "创建"]
    )
    def test_create_dimension(self):
        """创建组织维度数据"""
        try:
            # 1. 准备测试数据
            dimension_code = self.mock_util.generate_unique_code(tag="AT_DIM")
            dimension_name = f"自动化测试维度_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("组织维度表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["dimensionCode", "dimensionName", "status"],
                ["params", "request"]
            )
            set_dict = {
                "dimensionCode": dimension_code,
                "dimensionName": dimension_name,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="组织维度表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据
            self.__class__.dimension_id = response.get("data", {}).get("data", {})
            self.__class__.dimension_code = dimension_code
            self.__class__.dimension_name = dimension_name
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建组织维度成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试保存组织维度",
        description="验证ORG_DIMENSION_CF_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=2,
        tags=["sys_common", "org_dimension", "创建"]
    )
    def test_save_dimension(self):
        """保存组织维度数据（新增或更新）"""
        try:
            dimension_code = self.mock_util.generate_unique_code(tag="AT_DIM_SAVE")
            dimension_name = f"保存测试维度_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织维度表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dimensionCode", "dimensionName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "dimensionCode": dimension_code,
                "dimensionName": dimension_name,
                "status": "ENABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存组织维度成功: Code={dimension_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试批量创建组织维度",
        description="验证ORG_DIMENSION_CF_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=3,
        tags=["sys_common", "org_dimension", "创建"]
    )
    def test_batch_create_dimension(self):
        """批量创建组织维度数据"""
        try:
            dimension_list = []
            for i in range(3):
                dimension_code = self.mock_util.generate_unique_code(tag=f"AT_DIM_BATCH_{i}")
                dimension_name = f"批量测试维度{i}_{self.mock_util.get_timestamp()}"
                dimension_list.append({
                    "dimensionCode": dimension_code,
                    "dimensionName": dimension_name,
                    "status": "ENABLED"
                })
            
            api_path = self.get_api_path("组织维度表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": dimension_list})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"批量创建组织维度成功: 共{len(dimension_list)}条")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试保存主数据",
        description="验证ORG_DIMENSION_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=4,
        tags=["sys_common", "org_dimension", "创建"]
    )
    def test_master_data_save(self):
        """保存组织维度主数据"""
        try:
            dimension_code = self.mock_util.generate_unique_code(tag="AT_DIM_MD")
            dimension_name = f"主数据维度_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织维度表-保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dimensionCode", "dimensionName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "dimensionCode": dimension_code,
                "dimensionName": dimension_name,
                "status": "ENABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-保存主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存组织维度主数据成功: Code={dimension_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 查询相关测试 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试分页查询",
        description="验证ORG_DIMENSION_CF_PAGING_DATA_SERVICE功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_paging_query(self):
        """分页查询组织维度"""
        try:
            api_path = self.get_api_path("组织维度表-分页数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("分页查询组织维度成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试查找单条数据",
        description="验证ORG_DIMENSION_CF_FIND_ONE_DATA_SERVICE功能",
        severity="critical",
        order=6,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_find_one_data(self):
        """查找单条组织维度数据"""
        try:
            if not self.dimension_code:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dimensionCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dimensionCode": self.dimension_code})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-查找单条数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"查找单条组织维度数据成功: Code={self.dimension_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试查找列表数据",
        description="验证ORG_DIMENSION_CF_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=7,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_find_list_data(self):
        """查找组织维度列表数据"""
        try:
            api_path = self.get_api_path("组织维度表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织维度列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试根据ID查找数据",
        description="验证ORG_DIMENSION_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=8,
        smoke=True,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_find_data_by_id(self):
        """根据ID查找组织维度数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dimension_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找组织维度数据成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试根据ID查找单表数据",
        description="验证ORG_DIMENSION_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=9,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_find_single_data_by_id(self):
        """根据ID查找单表组织维度数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dimension_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表数据成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试根据ID列表查找数据",
        description="验证ORG_DIMENSION_CF_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=10,
        tags=["sys_common", "org_dimension", "查询"]
    )
    def test_find_data_by_ids(self):
        """根据ID列表查找组织维度数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dimension_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找组织维度数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 更新相关测试 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试根据ID更新数据",
        description="验证ORG_DIMENSION_CF_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=11,
        smoke=True,
        tags=["sys_common", "org_dimension", "更新"]
    )
    def test_update_data_by_id(self):
        """根据ID更新组织维度数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            new_name = f"更新后维度_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织维度表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "dimensionName"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": self.dimension_id,
                "dimensionName": new_name
            })
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新组织维度成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 启用禁用相关测试 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试启用主数据",
        description="验证ORG_DIMENSION_CF_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="critical",
        order=12,
        tags=["sys_common", "org_dimension", "启用禁用"]
    )
    def test_enable_data(self):
        """启用组织维度主数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dimension_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"启用组织维度成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试禁用主数据",
        description="验证ORG_DIMENSION_CF_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="critical",
        order=13,
        tags=["sys_common", "org_dimension", "启用禁用"]
    )
    def test_disable_data(self):
        """禁用组织维度主数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dimension_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"禁用组织维度成功: ID={self.dimension_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试批量启用主数据",
        description="验证ORG_DIMENSION_CF_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=14,
        tags=["sys_common", "org_dimension", "启用禁用"]
    )
    def test_multi_enable_data(self):
        """批量启用组织维度主数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-批量启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dimension_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-批量启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量启用组织维度成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试批量禁用主数据",
        description="验证ORG_DIMENSION_CF_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=15,
        tags=["sys_common", "org_dimension", "启用禁用"]
    )
    def test_multi_disable_data(self):
        """批量禁用组织维度主数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-批量禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.dimension_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-批量禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量禁用组织维度成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 导入导出测试 ====================
    
    
    
    
    @pytest.mark.skip(reason="导出任务需要具体配置，复杂度较高")
    @case_decorator(
        story="组织维度管理",
        title="测试提交导出任务",
        description="验证ORG_DIMENSION_CF_API_GEI_TASK_EXPORT_DIRECT_POST功能",
        severity="normal",
        order=19,
        tags=["sys_common", "org_dimension", "导出"]
    )
    def test_export_task(self):
        """提交导出任务"""
        try:
            api_path = self.get_api_path("组织维度表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-导入导出任务管理接口-提交导出任务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 删除相关测试 ====================
    
    @case_decorator(
        story="组织维度管理",
        title="测试根据ID删除数据",
        description="验证ORG_DIMENSION_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=20,
        tags=["sys_common", "org_dimension", "删除"]
    )
    def test_delete_data_by_id(self):
        """根据ID删除组织维度数据"""
        try:
            if not self.dimension_id:
                self._ensure_create_dimension()
            
            api_path = self.get_api_path("组织维度表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.dimension_id})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除组织维度成功: ID={self.dimension_id}")
            
            self.__class__.dimension_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织维度管理",
        title="测试批量删除数据",
        description="验证ORG_DIMENSION_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=21,
        tags=["sys_common", "org_dimension", "删除"]
    )
    def test_batch_delete_data(self):
        """批量删除组织维度数据"""
        try:
            # 创建测试数据用于删除
            test_id = None
            dimension_code = self.mock_util.generate_unique_code(tag="AT_DIM_DEL")
            dimension_name = f"待删除维度_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织维度表-创建数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dimensionCode", "dimensionName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "dimensionCode": dimension_code,
                "dimensionName": dimension_name,
                "status": "ENABLED"
            })
            response, _ = self.standard_api_call(
                api_key="组织维度表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            test_id = response.get("data", {}).get("data", {})
            
            # 批量删除
            api_path = self.get_api_path("组织维度表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [test_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织维度表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除组织维度成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
