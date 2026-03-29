"""
组织业务类型管理测试用例
覆盖组织业务类型表的增删改查、启用禁用、导入导出等功能
"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("组织业务类型管理")
class TestOrgBusinessTypeManagement(SysCommonBaseTest):
    """组织业务类型管理测试类"""
    
    biz_type_id = None
    biz_type_code = None
    biz_type_name = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.biz_type_id = None
        cls.biz_type_code = None
        cls.biz_type_name = None
        cls.logger.info("组织业务类型管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="org_business_type_cf",
                where="biz_type_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("组织业务类型测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"组织业务类型测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    # ==================== 创建相关测试 ====================
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试创建组织业务类型",
        description="验证ORG_BUSINESS_TYPE_CF_CREATE_DATA_SERVICE功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "org_biz_type", "创建"]
    )
    def test_create_biz_type(self):
        """创建组织业务类型数据"""
        try:
            biz_type_code = self.mock_util.generate_unique_code(tag="AT_BIZ")
            biz_type_name = f"自动化测试业务类型_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织业务类型表-创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, 
                ["bizTypeCode", "bizTypeName", "status"],
                ["params", "request"]
            )
            set_dict = {
                "bizTypeCode": biz_type_code,
                "bizTypeName": biz_type_name,
                "status": "ENABLED"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            self.__class__.biz_type_id = response.get("data", {}).get("data", {})
            self.__class__.biz_type_code = biz_type_code
            self.__class__.biz_type_name = biz_type_name
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建组织业务类型成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试保存组织业务类型",
        description="验证ORG_BUSINESS_TYPE_CF_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=2,
        tags=["sys_common", "org_biz_type", "创建"]
    )
    def test_save_biz_type(self):
        """保存组织业务类型数据（新增或更新）"""
        try:
            biz_type_code = self.mock_util.generate_unique_code(tag="AT_BIZ_SAVE")
            biz_type_name = f"保存测试业务类型_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织业务类型表-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bizTypeCode", "bizTypeName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "bizTypeCode": biz_type_code,
                "bizTypeName": biz_type_name,
                "status": "ENABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-保存数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存组织业务类型成功: Code={biz_type_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试批量创建组织业务类型",
        description="验证ORG_BUSINESS_TYPE_CF_BATCH_CREATE_DATA_SERVICE功能",
        severity="normal",
        order=3,
        tags=["sys_common", "org_biz_type", "创建"]
    )
    def test_batch_create_biz_type(self):
        """批量创建组织业务类型数据"""
        try:
            biz_type_list = []
            for i in range(3):
                biz_type_code = self.mock_util.generate_unique_code(tag=f"AT_BIZ_BATCH_{i}")
                biz_type_name = f"批量测试业务类型{i}_{self.mock_util.get_timestamp()}"
                biz_type_list.append({
                    "bizTypeCode": biz_type_code,
                    "bizTypeName": biz_type_name,
                    "status": "ENABLED"
                })
            
            api_path = self.get_api_path("组织业务类型表-批量创建数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dataList"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"dataList": biz_type_list})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-批量创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"批量创建组织业务类型成功: 共{len(biz_type_list)}条")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试保存主数据",
        description="验证ORG_BUSINESS_TYPE_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="critical",
        order=4,
        tags=["sys_common", "org_biz_type", "创建"]
    )
    def test_master_data_save(self):
        """保存组织业务类型主数据"""
        try:
            biz_type_code = self.mock_util.generate_unique_code(tag="AT_BIZ_MD")
            biz_type_name = f"主数据业务类型_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织业务类型表-保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bizTypeCode", "bizTypeName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "bizTypeCode": biz_type_code,
                "bizTypeName": biz_type_name,
                "status": "ENABLED"
            })
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-保存主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"保存组织业务类型主数据成功: Code={biz_type_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 查询相关测试 ====================
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试分页查询",
        description="验证ORG_BUSINESS_TYPE_CF_PAGING_DATA_SERVICE功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_paging_query(self):
        """分页查询组织业务类型"""
        try:
            api_path = self.get_api_path("组织业务类型表-分页数据服务")
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
                api_key="组织业务类型表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("分页查询组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试查找单条数据",
        description="验证ORG_BUSINESS_TYPE_CF_FIND_ONE_DATA_SERVICE功能",
        severity="critical",
        order=6,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_find_one_data(self):
        """查找单条组织业务类型数据"""
        try:
            if not self.biz_type_code:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-查找单条数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bizTypeCode"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"bizTypeCode": self.biz_type_code})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-查找单条数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"查找单条组织业务类型数据成功: Code={self.biz_type_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试查找列表数据",
        description="验证ORG_BUSINESS_TYPE_CF_FIND_LIST_DATA_SERVICE功能",
        severity="critical",
        order=7,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_find_list_data(self):
        """查找组织业务类型列表数据"""
        try:
            api_path = self.get_api_path("组织业务类型表-查找列表数据服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-查找列表数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("查找组织业务类型列表数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试根据ID查找数据",
        description="验证ORG_BUSINESS_TYPE_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=8,
        smoke=True,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_find_data_by_id(self):
        """根据ID查找组织业务类型数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.biz_type_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-根据ID查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找组织业务类型数据成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试根据ID查找单表数据",
        description="验证ORG_BUSINESS_TYPE_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=9,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_find_single_data_by_id(self):
        """根据ID查找单表组织业务类型数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-根据ID查找单表数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.biz_type_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-根据ID查找单表数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"根据ID查找单表数据成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试根据ID列表查找数据",
        description="验证ORG_BUSINESS_TYPE_CF_FIND_DATA_BY_IDS_SERVICE功能",
        severity="normal",
        order=10,
        tags=["sys_common", "org_biz_type", "查询"]
    )
    def test_find_data_by_ids(self):
        """根据ID列表查找组织业务类型数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-根据ID列表查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.biz_type_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-根据ID列表查找数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("根据ID列表查找组织业务类型数据成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 更新相关测试 ====================
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试根据ID更新数据",
        description="验证ORG_BUSINESS_TYPE_CF_UPDATE_DATA_BY_ID_SERVICE功能",
        severity="blocker",
        order=11,
        smoke=True,
        tags=["sys_common", "org_biz_type", "更新"]
    )
    def test_update_data_by_id(self):
        """根据ID更新组织业务类型数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            new_name = f"更新后业务类型_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织业务类型表-根据ID更新数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "bizTypeName"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": self.biz_type_id,
                "bizTypeName": new_name
            })
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-根据ID更新数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"更新组织业务类型成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 启用禁用相关测试 ====================
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试启用主数据",
        description="验证ORG_BUSINESS_TYPE_CF_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="critical",
        order=12,
        tags=["sys_common", "org_biz_type", "启用禁用"]
    )
    def test_enable_data(self):
        """启用组织业务类型主数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.biz_type_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"启用组织业务类型成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试禁用主数据",
        description="验证ORG_BUSINESS_TYPE_CF_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="critical",
        order=13,
        tags=["sys_common", "org_biz_type", "启用禁用"]
    )
    def test_disable_data(self):
        """禁用组织业务类型主数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.biz_type_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"禁用组织业务类型成功: ID={self.biz_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试批量启用主数据",
        description="验证ORG_BUSINESS_TYPE_CF_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="normal",
        order=14,
        tags=["sys_common", "org_biz_type", "启用禁用"]
    )
    def test_multi_enable_data(self):
        """批量启用组织业务类型主数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-批量启用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.biz_type_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-批量启用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量启用组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试批量禁用主数据",
        description="验证ORG_BUSINESS_TYPE_CF_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="normal",
        order=15,
        tags=["sys_common", "org_biz_type", "启用禁用"]
    )
    def test_multi_disable_data(self):
        """批量禁用组织业务类型主数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-批量禁用主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [self.biz_type_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-批量禁用主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量禁用组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 导入导出测试 ====================
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="组织业务类型管理",
        title="测试标准导入",
        description="验证ORG_BUSINESS_TYPE_CF_GEI_IMPORT_SERVICE功能",
        severity="normal",
        order=16,
        tags=["sys_common", "org_biz_type", "导入"]
    )
    def test_gei_import(self):
        """标准导入组织业务类型数据"""
        try:
            api_path = self.get_api_path("组织业务类型表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表标准导入服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("标准导入组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="组织业务类型管理",
        title="测试标准导出",
        description="验证ORG_BUSINESS_TYPE_CF_GEI_EXPORT_SERVICE功能",
        severity="normal",
        order=17,
        tags=["sys_common", "org_biz_type", "导出"]
    )
    def test_gei_export(self):
        """标准导出组织业务类型数据"""
        try:
            api_path = self.get_api_path("组织业务类型表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表标准导出服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("标准导出组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="组织业务类型管理",
        title="测试通过OSS提交导入任务",
        description="验证ORG_BUSINESS_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        order=18,
        tags=["sys_common", "org_biz_type", "导入"]
    )
    def test_import_by_oss(self):
        """通过OSS提交导入任务"""
        try:
            api_path = self.get_api_path("组织业务类型表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("OSS导入任务提交成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导出任务需要具体配置，复杂度较高")
    @case_decorator(
        story="组织业务类型管理",
        title="测试提交导出任务",
        description="验证ORG_BUSINESS_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST功能",
        severity="normal",
        order=19,
        tags=["sys_common", "org_biz_type", "导出"]
    )
    def test_export_task(self):
        """提交导出任务"""
        try:
            api_path = self.get_api_path("组织业务类型表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-导入导出任务管理接口-提交导出任务",
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
        story="组织业务类型管理",
        title="测试根据ID删除数据",
        description="验证ORG_BUSINESS_TYPE_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        order=20,
        tags=["sys_common", "org_biz_type", "删除"]
    )
    def test_delete_data_by_id(self):
        """根据ID删除组织业务类型数据"""
        try:
            if not self.biz_type_id:
                self.test_create_biz_type()
            
            api_path = self.get_api_path("组织业务类型表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.biz_type_id})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-根据ID删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除组织业务类型成功: ID={self.biz_type_id}")
            
            self.__class__.biz_type_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="组织业务类型管理",
        title="测试批量删除数据",
        description="验证ORG_BUSINESS_TYPE_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="normal",
        order=21,
        tags=["sys_common", "org_biz_type", "删除"]
    )
    def test_batch_delete_data(self):
        """批量删除组织业务类型数据"""
        try:
            # 创建测试数据用于删除
            test_id = None
            biz_type_code = self.mock_util.generate_unique_code(tag="AT_BIZ_DEL")
            biz_type_name = f"待删除业务类型_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("组织业务类型表-创建数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["bizTypeCode", "bizTypeName", "status"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "bizTypeCode": biz_type_code,
                "bizTypeName": biz_type_name,
                "status": "ENABLED"
            })
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-创建数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            test_id = response.get("data", {}).get("data", {})
            
            # 批量删除
            api_path = self.get_api_path("组织业务类型表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"ids": [test_id]})
            
            response, _ = self.standard_api_call(
                api_key="组织业务类型表-批量删除数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info("批量删除组织业务类型成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
