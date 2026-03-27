import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("编码规则管理")
class TestCodeRuleManagement(GenMdBaseTest):
    """编码规则管理测试类 - 覆盖编码规则的编辑、查询详情、分页查询功能"""
    
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
        cls.logger.info("编码规则管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 无需清理，编码规则通常不创建测试数据
            cls.logger.info("编码规则管理测试类清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="编码规则管理",
        title="测试分页查询编码规则",
        description="验证GEN-编码规则-分页查询服务功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["编码规则", "分页查询", "GEN_CODE_RULE_PAGE_ACTION_SERVICE"]
    )
    def test_query_code_rule_page(self):
        """分页查询编码规则用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-编码规则-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="编码规则管理",
        title="测试查询编码规则详情",
        description="验证GEN-编码规则-查询详情服务功能",
        severity="critical",
        file_level_order=2,
        tags=["编码规则", "查询详情", "GEN_CODE_RULE_DETAIL_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_query_code_rule_detail(self):
        """查询编码规则详情用例"""
        try:
            set_dict = {"id": 1}  # 示例ID
            
            response, _ = self.standard_api_call(
                api_key="GEN-编码规则-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="编码规则管理",
        title="测试编辑编码规则",
        description="验证GEN-编码规则-编辑规则服务功能",
        severity="blocker",
        file_level_order=3,
        tags=["编码规则", "编辑", "GEN_CODE_RULE_UPDATE_ACTION_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_update_code_rule(self):
        """编辑编码规则用例"""
        try:
            set_dict = {
                "id": 1,  # 示例ID
                "name": f"更新编码规则_{self.mock_util.get_timestamp()}",
                "remark": "更新后的编码规则描述"
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-编码规则-编辑规则服务",
                set_dict=set_dict,
                fields_to_filter=["id", "name", "remark"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
