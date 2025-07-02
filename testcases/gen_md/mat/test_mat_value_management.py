import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("物料价值管理")
class TestMat_ValueManagement(GenMdBaseTest):
    """物料价值管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mat_value_id = None
        cls.mat_value_code = None
        cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
        cls.mat_type_id = cls.md_cache_data.get("mat_info",{}).get("mat_type_cf",{}).get("FINP",[])[0].get("id")
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
        cls.logger.info("物料价值管理测试类初始化完成")
        

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料价值管理数据
        """
        try:
            # 使用SQL删除测试数据
            sql = f"select id from gen_inv_org_mat_type_link_cf where mat_type_id = {cls.mat_type_id} and inv_org_id = {cls.inv_org_id} limit 1"
            mat_value_id = cls.db.query(sql)[0].get("id")
            if not mat_value_id:
                cls.db.insert(
                    table="gen_inv_org_mat_type_link_cf",
                    data={
                        "mat_type_id": cls.mat_type_id,
                        "inv_org_id": cls.inv_org_id,
                        "mat_qty_update": True,
                        "mat_val_update": True,
                        "created_by": cls.user_id,
                        "created_at": cls.mock_util.get_timestamp(),
                        "updated_by": cls.user_id,
                        "updated_at": cls.mock_util.get_timestamp()
                    }
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="物料价值管理",
        title="测试新增物料价值管理",
        description="验证新增物料价值管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["物料价值管理", "新增"]
    )
    def test_save_mat_value(self):
        """
        新增物料价值管理用例
        """
        try:
          
            # 调用保存接口
            api_path = self.get_api_path("GEN-物料价值数量配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["invOrgId", "matTypeId","matQtyUpdate","matValUpdate"],
                ["params", "request"]
            )
            set_dict = {
                "invOrgId": {"id": self.inv_org_id},
                "matTypeId": {"id": self.mat_type_id},
                "matQtyUpdate": True,
                "matValUpdate": False
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")
            
            # 判断是否存在数据
            sql = f"select id from gen_inv_org_mat_type_link_cf where inv_org_id = {self.inv_org_id} and mat_type_id = {self.mat_type_id} limit 1"
            self.mat_value_id = self.db.query(sql)[0].get("id")
            if not self.mat_value_id:
                response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_data(response)
                self.mat_value_id = response.get("data", {}).get("data", {})
                a.json(filtered_params, "请求数据")
                a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试查询物料价值管理列表",
        description="验证物料价值管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["物料价值管理", "查询"]
    )
    def test_query_mat_value_list(self):
        """
        查询物料价值管理列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-物料价值数量配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            set_dict =  {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            },
            "fields": [
                {
                    "name": "invOrgId",
                    "type": "OBJECT"
                },
                {
                    "name": "matTypeId",
                    "type": "OBJECT"
                }
            ],
            "systemParams": None
        }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="物料价值管理",
        title="测试查询物料价值管理详情",
        description="验证物料价值管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["物料价值管理", "查询"]
    )
    def test_query_mat_value_detail(self):
        """
        查询物料价值管理详情用例
        """
        try:
            # 获取物料价值管理ID
            if not self.mat_value_id:
                self.test_save_mat_value()

            # 调用详情查询接口
            api_path = self.get_api_path("GEN-物料价值数量配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mat_value_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置标准导出",
        description="验证物料价值数量配置标准导出功能",
        severity="normal",
        order=4,
        tags=["物料价值管理", "导出"]
    )
    def test_export_mat_value(self):
        """
        物料价值数量配置标准导出用例
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料价值数量配置导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料价值数量配置"
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="物料价值管理",
        title="测试物料价值数量配置标准导入",
        description="验证物料价值数量配置标准导入功能",
        severity="normal",
        order=5,
        tags=["物料价值管理", "导入"]
    )
    def test_import_mat_value(self):
        """
        物料价值数量配置标准导入用例（需要文件上传）
        """
        pass

    @case_decorator(
        story="物料价值管理",
        title="测试提交物料价值数量配置导出任务",
        description="验证提交物料价值数量配置导出任务功能",
        severity="normal",
        order=6,
        tags=["物料价值管理", "导出任务"]
    )
    def test_submit_export_task(self):
        """
        提交物料价值数量配置导出任务用例
        """
        try:
            api_path = self.get_api_path("物料数量价值更新配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params={
                "serviceKey": "GEN_MD$GEN_INV_ORG_MAT_TYPE_LINK_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"物料数量价值配置-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_inv_org_mat_type_link_cf",
                            "modelName": "物料数量价值更新配置",
                            "sheetNo": 0,
                            "sheetName": "物料数量价值更新配置",
                            "headerConfigList": [
                                {
                                    "name": "库存组织",
                                    "type": "TEXT",
                                    "field": "invOrgId.orgName"
                                },
                                {
                                    "name": "物料类型",
                                    "type": "TEXT",
                                    "field": "matTypeId.matTypeName"
                                },
                                {
                                    "name": "是否数量更新",
                                    "type": "BOOL",
                                    "field": "matQtyUpdate"
                                },
                                {
                                    "name": "是否价值更新",
                                    "type": "BOOL",
                                    "field": "matValUpdate"
                                },
                                {
                                    "name": "更新时间",
                                    "type": "DATE",
                                    "field": "updatedAt"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW-table-container-GEN_MD$gen_inv_org_mat_type_link_cf",
                        "viewKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW",
                        "params": {
                            "request": {
                                "pageable": {

                                }
                            },
                            "selectFields": [
                                {
                                    "field": "matQtyUpdate"
                                },
                                {
                                    "field": "matValUpdate"
                                },
                                {
                                    "field": "updatedAt"
                                },
                                {
                                    "field": "invOrgId",
                                    "selectFields": [
                                        {
                                            "field": "orgName"
                                        }
                                    ]
                                },
                                {
                                    "field": "matTypeId",
                                    "selectFields": [
                                        {
                                            "field": "matTypeName"
                                        }
                                    ]
                                }
                            ],
                            "modelKey": "GEN_MD$gen_inv_org_mat_type_link_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_inv_org_mat_type_link_cf",
                        "modelName": "物料数量价值更新配置",
                        "containerKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW-table-container-GEN_MD$gen_inv_org_mat_type_link_cf",
                        "viewKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW:list",
                        "sceneKey": "GEN_MD$GEN_MAT_QTY_VALUE_VIEW"
                    }
                }
            }
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="物料价值管理",
        title="测试删除物料价值管理",
        description="验证删除物料价值管理功能",
        severity="normal",
        order=8,
        smoke=True,
        tags=["物料价值管理", "删除"]
    )
    def test_delete_mat_value(self):
        """
        删除物料价值管理用例
        """
        try:
            # 获取物料价值管理信息
            if not self.mat_value_id:
                self.test_save_mat_value()

            # 调用删除接口
            api_path = self.get_api_path("GEN-物料价值数量配置-删除服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mat_value_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
