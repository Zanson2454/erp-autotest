import allure
import pytest
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import datetime

@allure.epic("库存管理")
@allure.feature("移动凭证管理")
class TestMobileVoucherManagement(ScmInvBaseTest):
    """移动凭证管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.batch_code = None
        cls.material_id = None
        cls.batch_id = None
        cls.charaClassId = None
        cls.batchCharaValueList = None
        
        # 固定ID常量
        cls.comOrgId = 14507001
        cls.matId = 14097001
        cls.invOrgId = 14375002
        cls.invLocId = 14376002
        cls.mvmTypeId = 2112005
        cls.moveTypeId = 2112005
        cls.unitId = 2004001
        cls.invWhId = 2002001
        cls.invAreaId = 2002001
        cls.invBinId = 2002003
        
        cls.logger.info("移动凭证管理测试类初始化完成")

    # @classmethod
    # def teardown_class(cls):
    #     """测试类结束后执行清理"""
    #     try:
    #         cls.db.delete(
    #             table="inv_mobile_voucher_md", 
    #             where="voucher_code like %s", 
    #             params=["AT_%"]
    #         )
    #         cls.logger.info("测试数据清理完成")
    #     except Exception as e:
    #         cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="移动凭证管理",
        title="测试查询物料批次特征服务",
        description="验证查询物料批次特征功能，为移动凭证创建提供批次数据支持",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["批次管理", "查询", "前置条件"]
    )
    def test_query_material_batch_feature(self):
        """查询物料批次特征服务用例"""
        try:
            # 获取API配置
            api_path = self.get_api_path("INV-批次-查询物料的批次特征服务")
            params, url = self.get_api_params(api_path)

            # 构造请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["matId", "invOrgId","invLocId"],
                ["params", "request"]
            )
            set_dict = {
                "matId": self.matId,
                "invOrgId": self.invOrgId,
                "invLocId": self.invLocId
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            # 发起请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 提取并保存批次特征数据
            self.charaClassId = response.get("data",{}).get("data",{}).get("charaClassId",{})
            self.batchCharaValueList = response.get("data",{}).get("data",{}).get("batchCharaValueList",{})

            self.logger.info(f"保存成功，charaClassId: {self.charaClassId}")
            self.logger.info(f"保存成功，batchCharaValueList: {self.batchCharaValueList}")
            # 4. 断言与附件
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试生成批次编码服务",
        description="验证生成批次编码功能，为移动凭证创建提供批次编码",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["批次管理", "生成编码", "前置条件"]
    )
    def test_generate_batch_code(self):
        """生成批次编码服务用例"""
        try:
            api_path = self.get_api_path("INV-批次-生成批次编码服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["invLocId", "invOrgId", "matId","mvmTypeId",],
                ["params", "request"]
            )
            set_dict = {
                "invLocId": self.invLocId,
                "invOrgId": self.invOrgId,
                "matId": self.matId,
                "mvmTypeId": self.mvmTypeId
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存生成的批次编码，供后续移动凭证创建使用
            self.batch_code = response.get("data", {}).get("data",{}).get("code")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试保存批次服务",
        description="验证保存批次功能，为移动凭证创建提供批次数据",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["批次管理", "保存", "前置条件"]
    )
    def test_save_batch(self):
        """保存批次服务用例"""
        try:
            # 获取API配置 
            api_path = self.get_api_path("INV-批次-查询建议物料的批次特征服务")
            params, url = self.get_api_params(api_path)

            # 构造请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["moveTypeId", "matId", "invOrgId", "invLocId", "quantity", "batchDetailList"],
                ["params", "request"]
            )
            set_dict = {
                "moveTypeId": self.moveTypeId,
                "matId": self.matId,
                "invOrgId": self.invOrgId,
                "invLocId": self.invLocId,
                "quantity": 1,
                "batchDetailList": [{
                    "charaClassId": self.charaClassId,
                    "qty": 1,
                    "batchNo": self.batch_code,
                    "batchCharaValueList": self.batchCharaValueList
                }]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            # 发起请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 断言与附件
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试新增移动凭证",
        description="验证新增移动凭证功能",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["移动凭证", "新增"]
    )
    def test_save_mobile_voucher(self):
        """新增移动凭证用例"""
        try:
            # 确保前置条件已满足
            if not self.charaClassId or not self.batchCharaValueList:
                self.test_query_material_batch_feature()
            if not self.batch_code:
                self.test_generate_batch_code()

            # 生成请求数据
            current_time = datetime.datetime.now()
            timestamp = current_time.strftime("%Y%m%d%H%M%S")  # 格式：20250912170147
            doc_time = current_time.strftime("%Y-%m-%d %H:%M:%S")  # 格式：2025-09-12 17:01:47
            request_no = self.mock_util.generate_unique_code(tag="REQ")
            
            api_path = self.get_api_path("INV-移动凭证-新版创建服务")
            params, url = self.get_api_params(api_path)

            # 构建移动凭证创建请求参数 - 直接使用完整的请求结构
            filtered_params = {
                "params": {
                    "request": {
                        "comOrgId": {"id": self.comOrgId},
                        "mvmTypeId": {"id": self.mvmTypeId},
                        "showType": "IN",
                        "mvmDocTimePst": doc_time,
                        "remark": f"自动化测试移动凭证-{timestamp}",
                        "requestNo": request_no,
                        "mvmDocInList": [{
                            "matId": {"id": self.matId},
                            "mvmQty": 1,
                            "refCode": "1",
                            "mvmTypeId": {"id": self.mvmTypeId},
                            "unitId": {"id": self.unitId},
                            "invOrgId": {"id": self.invOrgId},
                            "invLocId": {"id": self.invLocId},
                            "invWhId": {"id": self.invWhId},
                            "invAreaId": {"id": self.invAreaId},
                            "invBinId": {"id": self.invBinId},
                            "batchId": {
                                "batchType": "INBOUND",
                                "batchCode": self.batch_code,
                                "charaClassId": self.charaClassId,
                                "quantity": 1,
                                 "charaValue": self.batchCharaValueList
                            }
                        }]
                    }
                }
            }

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存移动凭证数据
            voucher_data = response.get("data", {}).get("data", {})
            self.mobile_voucher_id = voucher_data.get("moveVoucherId")
            voucher_code = voucher_data.get("moveVoucherCode")
            
            self.logger.info(f"移动凭证创建成功 - ID: {self.mobile_voucher_id}, 编码: {voucher_code}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试查询移动凭证分页",
        description="验证移动凭证分页查询功能",
        severity="normal",
        order=4,
        tags=["移动凭证", "查询"]
    )
    def test_query_mobile_voucher_page(self):
        """查询移动凭证分页用例"""
        try:
            api_path = self.get_api_path("SCM_INV-移动凭证-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "voucherCode", "type": "TEXT"},
                    {"name": "voucherName", "type": "TEXT"},
                    {"name": "voucherType", "type": "TEXT"}
                ]
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
        story="移动凭证管理",
        title="测试查询移动凭证详情",
        description="验证移动凭证详情查询功能",
        severity="normal",
        order=5,
        tags=["移动凭证", "详情"]
    )
    def test_query_mobile_voucher_detail(self):
        """查询移动凭证详情用例"""
        try:
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()

            api_path = self.get_api_path("SCM_INV-移动凭证-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mobile_voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试移动凭证分页数据服务",
        description="验证移动凭证分页数据服务功能",
        severity="normal",
        order=6,
        tags=["移动凭证", "分页数据"]
    )
    def test_mobile_voucher_paging_data(self):
        """移动凭证分页数据服务用例"""
        try:
            api_path = self.get_api_path("移动凭证-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "queryCondition"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "queryCondition": {}
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
        story="移动凭证管理",
        title="测试修改移动凭证",
        description="验证修改移动凭证功能",
        severity="normal",
        order=7,
        tags=["移动凭证", "修改"]
    )
    def test_update_mobile_voucher(self):
        """修改移动凭证用例"""
        try:
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()

            api_path = self.get_api_path("SCM_INV-移动凭证-修改服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "voucherName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.mobile_voucher_id,
                "voucherName": f"修改后移动凭证_{self.mock_util.get_timestamp()}",
                "remark": f"自动化测试修改移动凭证-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试启用移动凭证",
        description="验证启用移动凭证功能",
        severity="normal",
        order=8,
        tags=["移动凭证", "启用"]
    )
    def test_enable_mobile_voucher(self):
        """启用移动凭证用例"""
        try:
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()

            api_path = self.get_api_path("SCM_INV-移动凭证-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mobile_voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试禁用移动凭证",
        description="验证禁用移动凭证功能",
        severity="normal",
        order=9,
        tags=["移动凭证", "禁用"]
    )
    def test_disable_mobile_voucher(self):
        """禁用移动凭证用例"""
        try:
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()

            api_path = self.get_api_path("SCM_INV-移动凭证-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mobile_voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试删除移动凭证",
        description="验证删除移动凭证功能",
        severity="normal",
        order=10,
        tags=["移动凭证", "删除"]
    )
    def test_delete_mobile_voucher(self):
        """删除移动凭证用例"""
        try:
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()

            api_path = self.get_api_path("SCM_INV-移动凭证-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mobile_voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试提交移动凭证导出任务",
        description="验证提交移动凭证导出任务功能",
        severity="normal",
        order=11,
        tags=["移动凭证", "导出任务"]
    )
    def test_submit_mobile_voucher_export_task(self):
        """提交移动凭证导出任务用例"""
        try:
            api_path = self.get_api_path("移动凭证-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            params["params"] = {
                "taskName": f"移动凭证-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [
                    {
                        "modelKey": "SCM_INV$inv_mobile_voucher_md",
                        "modelName": "移动凭证",
                        "sheetNo": 0,
                        "sheetName": "移动凭证",
                        "headerConfigList": [
                            {
                                "name": "凭证编码",
                                "type": "TEXT",
                                "field": "voucherCode"
                            },
                            {
                                "name": "凭证名称",
                                "type": "TEXT",
                                "field": "voucherName"
                            },
                            {
                                "name": "凭证类型",
                                "type": "ENUM",
                                "field": "voucherType",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "调拨",
                                        "label": "调拨",
                                        "value": "TRANSFER"
                                    },
                                    {
                                        "_row_id_": "入库",
                                        "label": "入库",
                                        "value": "IN"
                                    },
                                    {
                                        "_row_id_": "出库",
                                        "label": "出库",
                                        "value": "OUT"
                                    }
                                ]
                            },
                            {
                                "name": "状态",
                                "type": "ENUM",
                                "field": "status",
                                "multiSelect": False,
                                "dictValues": [
                                    {
                                        "_row_id_": "未启用",
                                        "label": "未启用",
                                        "value": "INACTIVE"
                                    },
                                    {
                                        "_row_id_": "已启用",
                                        "label": "已启用",
                                        "value": "ENABLED"
                                    },
                                    {
                                        "_row_id_": "已停用",
                                        "label": "已停用",
                                        "value": "DISABLED"
                                    }
                                ]
                            },
                            {
                                "name": "备注",
                                "type": "TEXT",
                                "field": "remark"
                            }
                        ]
                    }
                ],
                "queryData": {
                    "containerKey": "SCM_INV$MOBILE_VOUCHER_VIEW-table-container-SCM_INV$inv_mobile_voucher_md",
                    "viewKey": "SCM_INV$MOBILE_VOUCHER_VIEW:list",
                    "sceneKey": "SCM_INV$MOBILE_VOUCHER_VIEW",
                    "params": {
                        "request": {
                            "pageable": {}
                        },
                        "selectFields": [
                            {"field": "voucherCode"},
                            {"field": "voucherName"},
                            {"field": "voucherType"},
                            {"field": "status"},
                            {"field": "remark"}
                        ],
                        "modelKey": "SCM_INV$inv_mobile_voucher_md"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_INV$inv_mobile_voucher_md",
                    "modelName": "移动凭证",
                    "containerKey": "SCM_INV$MOBILE_VOUCHER_VIEW-table-container-SCM_INV$inv_mobile_voucher_md",
                    "viewKey": "SCM_INV$MOBILE_VOUCHER_VIEW:list",
                    "sceneKey": "SCM_INV$MOBILE_VOUCHER_VIEW"
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="OSS导入依赖文件，暂时跳过")
    @case_decorator(
        story="移动凭证管理",
        title="测试通过OSS提交移动凭证导入任务",
        description="验证通过OSS提交移动凭证导入任务功能",
        severity="normal",
        order=12,
        tags=["移动凭证", "OSS导入"]
    )
    def test_submit_mobile_voucher_import_task_by_oss(self):
        """通过OSS提交移动凭证导入任务用例"""
        try:
            api_path = self.get_api_path("移动凭证-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["taskName", "ossConfig", "importConfig"],
                ["params", "request"]
            )
            set_dict = {
                "taskName": f"移动凭证OSS导入任务_{self.mock_util.get_timestamp()}",
                "ossConfig": {
                    "bucketName": "test-bucket",
                    "objectKey": f"mobile_voucher_import_{self.mock_util.get_timestamp()}.xlsx"
                },
                "importConfig": {
                    "fileType": "EXCEL",
                    "sheetName": "移动凭证"
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
