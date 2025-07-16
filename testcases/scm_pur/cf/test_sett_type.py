import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("结算类型定义表管理")
class TestSettTypeManagement(ScmPurBaseTest):
    """结算类型定义表管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.sett_type_id = None
        cls.logger.info("结算类型定义表管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 假设表名为 pur_sett_type_cf，code 字段为 type_code
            cls.db.delete(
                table="pur_sett_type_cf",
                where="type_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="结算类型定义表分页查询",
        title="结算类型定义表-分页数据服务",
        description="验证结算类型定义表分页数据服务功能",
        severity="blocker",
        order=1,
        tags=["结算类型定义表", "分页查询"]
    )
    def test_paging_sett_type(self):
        try:
            api_path = self.get_api_path("PUR_SETT_TYPE_CF_PAGING_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            ParamUtil.set_request_params(params, {"pageNo": 1, "pageSize": 10})
            a.json(params, "请求数据")
            response = self.http.post(url, json=params)
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
            # 提取第一个ID用于详情用例
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            if data_list:
                self.__class__.sett_type_id = data_list[0].get("id")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="结算类型定义表详情查询",
        title="结算类型定义表-根据ID查找数据服务",
        description="验证结算类型定义表根据ID查找数据服务功能",
        severity="critical",
        order=2,
        tags=["结算类型定义表", "详情查询"]
    )
    def test_detail_sett_type_by_id(self):
        try:
            if not self.sett_type_id:
                pytest.skip("无可用结算类型ID，跳过详情用例")
            api_path = self.get_api_path("PUR_SETT_TYPE_CF_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            ParamUtil.set_request_params(params, {"id": self.sett_type_id})
            a.json(params, "请求数据")
            response = self.http.post(url, json=params)
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
