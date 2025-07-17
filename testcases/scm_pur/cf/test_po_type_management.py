import allure
import pytest
import sys
from pathlib import Path
import re

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("订单类型管理")
class TestPoTypeManagement(ScmPurBaseTest):
    """订单类型管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_type_id = None
        cls.po_type_code = None
        cls.logger.info("订单类型管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 假设表名为 pur_po_type_cf，code 字段为 type_code
            cls.db.delete(
                table="pur_po_type_cf",
                where="po_type like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="订单类型标准导入",
        title="订单类型标准导入服务",
        description="验证订单类型标准导入功能",
        severity="normal",
        order=5,
        tags=["订单类型", "标准导入"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_import_po_type(self):
        pass

    @case_decorator(
        story="订单类型OSS导入任务",
        title="订单类型-导入导出任务管理接口-通过OSS提交导入任务",
        description="验证订单类型OSS导入任务接口功能",
        severity="normal",
        order=6,
        tags=["订单类型", "OSS导入任务"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_import_task_oss_po_type(self):
        pass

    @case_decorator(
        story="订单类型导出任务",
        title="订单类型导出任务接口",
        description="验证订单类型导出任务接口功能",
        severity="normal",
        order=3,
        tags=["订单类型", "导出任务"]
    )
    def test_export_task_po_type(self):
        try:
            api_path = self.get_api_path("订单类型-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            params["params"]= {
                "taskName": f"订单类型-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_PUR$pur_po_type_cf",
                        "modelName": "订单类型",
                        "sheetNo": 0,
                        "sheetName": "订单类型",
                        "headerConfigList": [
                            {
                                "name": "类型编码",
                                "type": "TEXT",
                                "field": "poType"
                            },
                            {
                                "name": "类型名称",
                                "type": "TEXT",
                                "field": "poTypeName"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "SCM_PUR$PUR_PO_TYPE_VIEW-list-SCM_PUR$pur_po_type_cf",
                    "viewKey": "SCM_PUR$PUR_PO_TYPE_VIEW:list",
                    "sceneKey": "SCM_PUR$PUR_PO_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {

                            }
                        },
                        "selectFields": [
                            {
                                "field": "poType"
                            },
                            {
                                "field": "poTypeName"
                            }
                        ],
                        "modelKey": "SCM_PUR$pur_po_type_cf"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_PUR$pur_po_type_cf",
                    "modelName": "订单类型",
                    "containerKey": "SCM_PUR$PUR_PO_TYPE_VIEW-list-SCM_PUR$pur_po_type_cf",
                    "viewKey": "SCM_PUR$PUR_PO_TYPE_VIEW:list",
                    "sceneKey": "SCM_PUR$PUR_PO_TYPE_VIEW"
                }
            }

            a.json(params, "请求数据")
            response = self.http.post(url, json=params)
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="订单类型标准导出",
        title="订单类型标准导出服务",
        description="验证订单类型标准导出功能",
        severity="normal",
        order=4,
        tags=["订单类型", "标准导出"]
    )
    @pytest.mark.skip(reason="业务未引用暂时跳过")
    def test_export_po_type(self):
        try:
            api_path = self.get_api_path("订单类型标准导出服务")
            params, url = self.get_api_params(api_path)
            a.json(params, "请求数据")
            response = self.http.post(url, json=params)
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
