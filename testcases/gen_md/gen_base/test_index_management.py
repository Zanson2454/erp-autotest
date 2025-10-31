import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("指标中心管理")
class TestIndexManagement(GenMdBaseTest):
    """指标中心管理测试类 - 覆盖所有指标中心相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 数据存储
        cls.index_id = None
        cls.parent_index_id = None
        cls.logger.info("指标中心管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_index_md",
                where="gen_index_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 指标中心基础管理 ================
    @case_decorator(
        story="指标中心管理",
        title="测试新增指标",
        description="验证GEN-指标中心-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["指标中心", "新增", "GEN_INDEX_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_index(self):
        """新增指标用例 - GEN_INDEX_MD_SAVE_ACTION_SERVICE"""
        try:
            index_code = self.mock_data.generate_unique_code(tag="INDEX")
            index_name = f"测试指标_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-指标中心-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["genIndexCode", "genIndexName", "genIndexDataResult", "genIndexDataSource", "genIndexDataType", "genIndexRemark", "genIndexSort", "genIndexSql", "genParentId", "status"], ["params", "request"]
            )
            set_dict = {
                "genIndexCode": index_code,
                "genIndexName": index_name,
                "genIndexDataResult": f"DataResult_{self.mock_data.get_timestamp()}",  
                "genIndexDataSource": f"DataSource_{self.mock_data.get_timestamp()}",  
                "genIndexDataType": "MODEL",
                "genIndexRemark": None,  
                "genIndexSort": 1,
                "genIndexSql": None,
                "genParentId": None,
                "status": "DRAFT"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.index_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试调用取号规则",
        description="验证指标中心表-调用取号规则服务功能",
        severity="normal",
        file_level_order=2,
        tags=["指标中心", "取号规则", "GEN_INDEX_MD_INVOKE_CODE_RULE_SERVICE"]
    )
    def test_invoke_code_rule(self):
        """调用取号规则用例 - GEN_INDEX_MD_INVOKE_CODE_RULE_SERVICE"""
        try:
            api_path = self.get_api_path("指标中心表-调用取号规则服务")
            params, url = self.get_api_params(api_path)

            params['modelKey'] = "GEN_MD$gen_index_md_code"
            params['request'] = {"ruleKey":"GEN_MD$gen_index_md_code"}

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)
            index_code = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(index_code, "not_empty")
            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查询指标分页列表",
        description="验证GEN-指标中心-查询分页服务功能",
        severity="normal",
        file_level_order=3,
        tags=["指标中心", "查询", "GEN_INDEX_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_index_page(self):
        """查询指标分页列表用例 - GEN_INDEX_MD_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-指标中心-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            set_dict =  {
                "pageable": {
                    "conditionGroup": {
                        "type": "ConditionGroup",
                        "logicOperator": "OR",
                        "conditions": [
                            {
                                "type": "ConditionGroup",
                                "logicOperator": "OR",
                                "conditions": [
                                    {
                                        "type": "ConditionLeaf",
                                        "leftValue": {
                                            "type": "VarValue",
                                            "varValue": [
                                                {
                                                    "valueKey": "genParentId",
                                                    "valueName": "genParentId"
                                                }
                                            ],
                                            "valueType": "VAR",
                                            "fieldType": "Number"
                                        },
                                        "operator": "IS_NULL"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查询指标详情",
        description="验证GEN-指标中心-查询详情服务功能",
        severity="normal",
        file_level_order=4,
        tags=["指标中心", "查询", "GEN_INDEX_MD_DETAIL_ACTION_SERVICE"]
    )
    def test_query_index_detail(self):
        """查询指标详情用例 - GEN_INDEX_MD_DETAIL_ACTION_SERVICE"""
        try:
            if not self.index_id:
                self.test_save_index()

            api_path = self.get_api_path("GEN-指标中心-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.index_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试根据父ID查询下级列表",
        description="验证GEN-指标中心-根据父ID查询下级列表服务功能",
        severity="normal",
        file_level_order=5,
        tags=["指标中心", "查询", "GEN_INDEX_MD_QUERY_BY_PARENT_ACTION_SERVICE"]
    )
    def test_query_by_parent(self):
        """根据父ID查询下级列表用例 - GEN_INDEX_MD_QUERY_BY_PARENT_ACTION_SERVICE"""
        try:
            if not self.index_id:
                self.test_save_index()

            api_path = self.get_api_path("GEN-指标中心-根据父ID查询下级列表服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["parentId"], ["params", "request"]
            )
            set_dict = {"parentId": self.index_id}  # 查询顶级指标
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试查找树子数据",
        description="验证指标中心表-查找树子数据服务功能",
        severity="normal",
        file_level_order=6,
        tags=["指标中心", "树形结构", "GEN_INDEX_MD_FIND_TREE_CHILDREN_DATA_SERVICE"]
    )
    def test_find_tree_children(self):
        """查找树子数据用例 - GEN_INDEX_MD_FIND_TREE_CHILDREN_DATA_SERVICE"""
        try:
            api_path = self.get_api_path("指标中心表-查找树子数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["nodeId", "level"], ["params", "request"]
            )
            set_dict = {
                "nodeId": None,  # 根节点
                "level": 1  # 查询第一级
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试启用指标",
        description="验证GEN-指标中心-启用服务功能",
        severity="normal",
        file_level_order=7,
        tags=["指标中心", "启用", "GEN_INDEX_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_index(self):
        """启用指标用例 - GEN_INDEX_MD_ENABLED_ACTION_SERVICE"""
        try:
            if not self.index_id:
                self.test_save_index()

            api_path = self.get_api_path("GEN-指标中心-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.index_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试禁用指标",
        description="验证GEN-指标中心-禁用服务功能",
        severity="normal",
        file_level_order=8,
        tags=["指标中心", "禁用", "GEN_INDEX_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_index(self):
        """禁用指标用例 - GEN_INDEX_MD_DISABLED_ACTION_SERVICE"""
        try:
            if not self.index_id:
                self.test_save_index()

            api_path = self.get_api_path("GEN-指标中心-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.index_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心管理",
        title="测试删除指标",
        description="验证GEN-指标中心-删除服务功能",
        severity="critical",
        file_level_order=9,
        tags=["指标中心", "删除", "GEN_INDEX_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_index(self):
        """删除指标用例 - GEN_INDEX_MD_DELETE_ACTION_SERVICE"""
        try:
            if not self.index_id:
                self.test_save_index()

            api_path = self.get_api_path("GEN-指标中心-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.index_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 指标中心导入管理 ================
    @case_decorator(
        story="指标中心导入管理",
        title="测试指标中心标准导入",
        description="验证指标中心表标准导入服务功能",
        severity="normal",
        file_level_order=10,
        tags=["指标中心", "导入", "GEN_INDEX_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_index_import(self):
        """指标中心标准导入用例 - GEN_INDEX_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("指标中心表标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_data.generate_unique_code(tag="IMPORT_INDEX"),
                    "name": f"导入测试指标_{self.mock_data.get_timestamp()}",
                    "type": "COUNT",
                    "unit": "个",
                    "description": "导入的指标描述"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标中心任务管理",
        title="测试指标中心OSS导入任务",
        description="验证指标中心表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=11,
        tags=["指标中心", "任务管理", "GEN_INDEX_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_index_oss_import_task(self):
        """指标中心OSS导入任务用例 - GEN_INDEX_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("指标中心表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_index_import_file.xlsx",
                "taskName": f"指标中心导入任务_{self.mock_data.get_timestamp()}",
                "templateId": 1
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
