import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
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
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.mock_data = MockData()
        cls.logger.info("指标中心管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_index(self):
        index_code = self.mock_data.generate_unique_code(tag="INDEX")
        index_name = f"测试指标_{self.mock_data.get_timestamp()}"

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
        response, extracted_id = self.standard_api_call(
            api_key="GEN-指标中心-保存服务",
            set_dict=set_dict,
            fields_to_filter=[
                "genIndexCode", "genIndexName", "genIndexDataResult", "genIndexDataSource",
                "genIndexDataType", "genIndexRemark", "genIndexSort", "genIndexSql",
                "genParentId", "status"
            ],
            store_id_as="index"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("index", extracted_id)
        self.assert_util.assert_by_operator(extracted_id, "not_empty")
        return extracted_id, set_dict, response

    def _ensure_save_index(self):
        index_id = self.get_runtime_id("index")
        if index_id:
            return index_id
        extracted_id, _, _ = self._create_index()
        return extracted_id

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
            _, set_dict, response = self._create_index()
            a.json(set_dict, "请求数据")
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
            set_dict = {
                "formParams": {
                    "modelKey": "GEN_MD$gen_index_md_code",
                    "request": {"ruleKey": "GEN_MD$gen_index_md_code"}
                }
            }
            response, _ = self.standard_api_call(
                api_key="指标中心表-调用取号规则服务",
                set_dict=set_dict,
                fields_to_filter=["formParams"]
            )
            self.assert_util.assert_response_data(response)
            index_code = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(index_code, "not_empty")
            a.json(set_dict, "请求数据")
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

            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable"]
            )
            self.assert_util.assert_response_data(response)
            total_count = response.get("data", {}).get("data", {}).get("totalCount", 0)
            self.assert_util.assert_by_operator(total_count, ">=", 0)

            a.json(set_dict, "请求数据")
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
            index_id = self._ensure_save_index()
            set_dict = {"id": index_id}
            response, detail_id = self.standard_api_call(
                api_key="GEN-指标中心-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_data(response)
            if detail_id is not None:
                self.assert_util.assert_by_operator(detail_id, "=", index_id)

            a.json(set_dict, "请求数据")
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
            index_id = self._ensure_save_index()
            set_dict = {"parentId": index_id}  # 查询顶级指标
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-根据父ID查询下级列表服务",
                set_dict=set_dict,
                fields_to_filter=["parentId"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
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
            set_dict = {
                "nodeId": None,  # 根节点
                "level": 1  # 查询第一级
            }
            response, _ = self.standard_api_call(
                api_key="指标中心表-查找树子数据服务",
                set_dict=set_dict,
                fields_to_filter=["nodeId", "level"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
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
            index_id = self._ensure_save_index()
            set_dict = {"id": index_id}
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
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
            index_id = self._ensure_save_index()
            set_dict = {"id": index_id}
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
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
            index_id = self._ensure_save_index()
            set_dict = {"id": index_id}
            response, _ = self.standard_api_call(
                api_key="GEN-指标中心-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
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

            set_dict = {"data": import_data}
            response, _ = self.standard_api_call(
                api_key="指标中心表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
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
            set_dict = {
                "fileKey": "test_index_import_file.xlsx",
                "taskName": f"指标中心导入任务_{self.mock_data.get_timestamp()}",
                "templateId": 1
            }
            response, _ = self.standard_api_call(
                api_key="指标中心表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
