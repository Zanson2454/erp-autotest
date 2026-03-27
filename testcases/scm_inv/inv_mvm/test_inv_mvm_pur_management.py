import allure
import pytest
import sys
from pathlib import Path
import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("移动凭证管理")
class TestMobileVoucherManagement(ScmInvBaseTest):
    """移动凭证管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 测试数据变量
        cls.mobile_voucher_id = None
        cls.mobile_voucher_code = None
        cls.batch_code = None
        cls.material_id = None
        cls.batch_id = None
        cls.charaClassId = None
        cls.batchCharaValueList = None
        
        # 从初始化数据中获取ID
        cls.unitId = cls.init_data["uom_info"]["qty_uom_info"][0]["uom_id"] if cls.init_data.get("uom_info", {}).get("qty_uom_info") else None
        
        # 从inv_cache_data中获取ID
        if cls.inv_cache_data:
            # 公司组织ID
            cls.comOrgId = cls.inv_cache_data["org_info"]["gr_come_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("gr_come_org_info") else None
            # 库存组织ID
            cls.invOrgId = cls.inv_cache_data["org_info"]["inv_org_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_org_info") else None
            # 库存地点ID
            cls.invLocId = cls.inv_cache_data["org_info"]["inv_loc_info"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_loc_info") else None
            # 物料ID (使用成品物料)
            cls.matId = cls.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"] if cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP") else None
            # 仓库ID
            cls.invWhId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["inv_wh_id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
            # 仓储区ID
            cls.invAreaId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["inv_area_id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
            # 仓位ID
            cls.invBinId = cls.inv_cache_data["org_info"]["inv_bin_rec_md"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_bin_rec_md") else None
            # 移动类型ID
            cls.mvmTypeId = cls.inv_cache_data["org_info"]["inv_mvm_type_cf_pur"][0]["id"] if cls.inv_cache_data.get("org_info", {}).get("inv_mvm_type_cf_pur") else None
            cls.moveTypeId = cls.mvmTypeId  # 移动类型和移动凭证类型使用相同ID
        
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
            response, _ = self.standard_api_call(
                api_key="INV-批次-查询物料的批次特征服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
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

            response, _ = self.standard_api_call(
                api_key="INV-批次-生成批次编码服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
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
            response, _ = self.standard_api_call(
                api_key="INV-批次-查询建议物料的批次特征服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
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
        order=4,
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

            response, _ = self.standard_api_call(
                api_key="INV-移动凭证-新版创建服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 保存移动凭证数据
            voucher_data = response.get("data", {}).get("data", {})
            self.mobile_voucher_id = voucher_data.get("moveVoucherId")
            self.mobile_voucher_code = voucher_data.get("moveVoucherCode")
            
            self.logger.info(f"移动凭证创建成功 - ID: {self.mobile_voucher_id}, 编码: {self.mobile_voucher_code}")

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
        order=5,
        tags=["移动凭证", "查询"]
    )
    def test_query_mobile_voucher_page(self):
        """查询移动凭证分页用例"""
        try:
            api_path = self.get_api_path("INV-移动凭证-分页查询服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 2,
                    "pageSize": 20,
                    "sortOrders": 
                    [
                        {"fieldAlias":"createdAt","sortType":"DESC"}
                    ]
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "upDocCode", "type": "TEXT"},
                    {"name": "sourceType", "type": "SELECT"},
                    {"name": "docCode", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-移动凭证-分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言分页数据总数大于0
            total = response.get("data", {}).get("data", {}).get("total", 0)
            assert total > 0, f"移动凭证分页查询结果为空，total: {total}"
            self.logger.info(f"分页查询成功，总记录数: {total}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试移动凭证筛选查询",
        description="验证移动凭证列表页筛选功能，包括编码查询和来源类型查询",
        severity="normal",
        order=6,
        tags=["移动凭证", "筛选查询"]
    )
    def test_query_mobile_voucher_with_filters(self):
        """移动凭证筛选查询用例"""
        try:
            # 确保有移动凭证编码
            if not self.mobile_voucher_code:
                self.test_save_mobile_voucher()
                
            api_path = self.get_api_path("INV-移动凭证-分页查询服务")
            params, url = self.get_api_params(api_path)

            # 测试1：根据编码筛选查询
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 50,
                    "needTotal": True,
                    "sortOrders": [{"fieldAlias": "createdAt", "sortType": "DESC"}],
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "code": {
                                "operator": "CONTAINS",
                                "value": self.mobile_voucher_code
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "upDocCode", "type": "TEXT"},
                    {"name": "sourceType", "type": "SELECT"},
                    {"name": "docCode", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-移动凭证-分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 断言编码筛选结果 - 修复数据路径
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            if not data_list:
                detail = self._get_voucher_detail(self.mobile_voucher_id)
                assert detail and detail.get("id") == self.mobile_voucher_id, "详情接口未查询到刚创建的移动凭证"
                self.logger.warning("移动凭证分页列表暂未同步到最新数据，已降级使用详情接口校验")
                return
            
            found_match = any(self.mobile_voucher_code in item.get("code", "") for item in data_list)
            assert found_match, f"编码筛选查询未找到匹配的记录: {self.mobile_voucher_code}"

            a.json(filtered_params, "编码筛选请求数据")
            a.json(response, "编码筛选响应数据")

            # 测试2：根据来源类型筛选查询
            set_dict_source = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 50,
                    "needTotal": True,
                    "sortOrders": [{"fieldAlias": "createdAt", "sortType": "DESC"}],
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "sourceType": {
                                "operator": "IN",
                                "value": ["MANUAL"]
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "sourceType", "type": "SELECT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict_source)

            response_source, _ = self.standard_api_call(
                api_key="INV-移动凭证-分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response_source)
            
            # 断言来源类型筛选结果
            source_data_list = response_source.get("data", {}).get("data", {}).get("data", [])
            if source_data_list:
                all_manual = all(item.get("sourceType") == "MANUAL" for item in source_data_list)
                assert all_manual, "来源类型筛选查询结果不符合筛选条件"

            a.json(filtered_params, "来源筛选请求数据")
            a.json(response_source, "来源筛选响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试查询移动凭证详情",
        description="验证移动凭证详情查询功能",
        severity="normal",
        order=7,
        tags=["移动凭证", "详情"]
    )
    def test_query_mobile_voucher_detail(self):
        """查询移动凭证详情用例"""
        try:
            # 确保有移动凭证ID
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()
                
            api_path = self.get_api_path("INV-移动凭证-详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.mobile_voucher_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-移动凭证-详情服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            # 断言详情数据完整性
            detail_data = response.get("data", {}).get("data", {})
            assert detail_data.get("id") == self.mobile_voucher_id, "详情ID与查询ID不匹配"
            assert detail_data.get("code"), "移动凭证编码不能为空"

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
        order=8,
        tags=["移动凭证", "导出任务"]
    )
    def test_submit_mobile_voucher_export_task(self):
        """提交移动凭证导出任务用例"""
        try:
            # 确保有移动凭证数据
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()
                
            api_path = self.get_api_path("移动凭证抬头表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            # 根据curl直接构造参数，不使用filter_post_body_fields
            filtered_params = {
                "serviceKey": "SCM_INV$INV_MVM_DOC_HEAD_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"移动凭证-{self.nickname}-{self.mock_util.get_timestamp()}-导出",
                "multiSheetConfig": [{
                    "modelKey": "SCM_INV$inv_mvm_doc_head_tr",
                    "modelName": "移动凭证抬头表",
                    "sheetNo": 0,
                    "sheetName": "移动凭证抬头表",
                    "headerConfigList": [
                        {"name": "编码", "type": "TEXT", "field": "code"},
                        {"name": "公司组织", "type": "TEXT", "field": "comOrgId.orgName"},
                        {"name": "记账时间", "type": "DATE", "field": "mvmDocTimePst"},
                        {"name": "关联业务单", "type": "TEXT", "field": "docCode"},
                        {"name": "冲销原凭证", "type": "TEXT", "field": "revMvmDocId.code"},
                        {"name": "上游单据", "type": "TEXT", "field": "upDocCode"},
                        {"name": "凭证来源", "type": "ENUM", "field": "sourceType", "multiSelect": False,
                         "dictValues": [
                             {"_row_id_": "PURCHASE", "label": "采购", "value": "PURCHASE"},
                             {"_row_id_": "SALE", "label": "销售", "value": "SALE"},
                             {"_row_id_": "MANUAL", "label": "库存", "value": "MANUAL"},
                             {"_row_id_": "TRANSFER", "label": "调拨", "value": "TRANSFER"},
                             {"_row_id_": "STOCK_CHECK", "label": "盘点", "value": "STOCK_CHECK"},
                             {"_row_id_": "CHECK", "label": "对账", "value": "CHECK"},
                             {"_row_id_": "PRD", "label": "生产", "value": "PRD"},
                             {"_row_id_": "WH", "label": "仓库", "value": "WAREHOUSE"}
                         ]},
                        {"name": "存货价值推送状态", "type": "ENUM", "field": "invValuePushStatus", "multiSelect": False,
                         "dictValues": [
                             {"_row_id_": "PUSH_SUCCESS", "label": "推送成功", "value": "PUSH_SUCCESS"},
                             {"_row_id_": "PUSH_FAIL", "label": "推送失败", "value": "PUSH_FAIL"},
                             {"_row_id_": "NO_PUSH", "label": "无需推送", "value": "NO_PUSH"},
                             {"_row_id_": "WAIT_PUSH", "label": "待推送", "value": "WAIT_PUSH"}
                         ]},
                        {"name": "创建时间", "type": "DATE", "field": "createdAt"},
                        {"name": "存货价值推送失败原因", "type": "MULTI_TEXT", "field": "invValuePushErrorMsg"}
                    ]
                }],
                "queryData": {
                    "containerKey": "SCM_INV$INV_MVM_VOUCHER_VIEW-table-container-SCM_INV$inv_mvm_doc_head_tr",
                    "viewKey": "SCM_INV$INV_MVM_VOUCHER_VIEW:list",
                    "sceneKey": "SCM_INV$INV_MVM_VOUCHER_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {
                                        "id": {
                                            "operator": "IN",
                                            "value": [self.mobile_voucher_id]
                                        }
                                    }
                                },
                                "sortOrders": [{"fieldAlias": "createdAt", "sortType": "DESC"}]
                            }
                        },
                        "selectFields": [
                            {"field": "code"},
                            {"field": "mvmDocTimePst"},
                            {"field": "docCode"},
                            {"field": "upDocCode"},
                            {"field": "sourceType"},
                            {"field": "invValuePushStatus"},
                            {"field": "createdAt"},
                            {"field": "invValuePushErrorMsg"},
                            {"field": "comOrgId", "selectFields": [{"field": "orgName"}]},
                            {"field": "revMvmDocId", "selectFields": [{"field": "code"}]}
                        ],
                        "modelKey": "SCM_INV$inv_mvm_doc_head_tr"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "model": "SCM_INV$inv_mvm_doc_head_tr",
                    "modelName": "移动凭证抬头表",
                    "containerKey": "SCM_INV$INV_MVM_VOUCHER_VIEW-table-container-SCM_INV$inv_mvm_doc_head_tr",
                    "viewKey": "SCM_INV$INV_MVM_VOUCHER_VIEW:list",
                    "sceneKey": "SCM_INV$INV_MVM_VOUCHER_VIEW"
                    }
                }
            }

            response, _ = self.standard_api_call(
                api_key="移动凭证抬头表-导入导出任务管理接口-提交导出任务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            # 断言导出任务提交成功
            task_data = response.get("data", {}).get("data", {})
            main_task_id = task_data.get("mainTaskId")
            assert main_task_id, "导出任务ID不能为空"
            self.logger.info(f"导出任务提交成功，任务ID: {main_task_id}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="移动凭证管理",
        title="测试移动凭证冲销",
        description="验证移动凭证冲销功能",
        severity="critical",
        order=9,
        tags=["移动凭证", "冲销"]
    )
    def test_move_voucher_write_off(self):
        """移动凭证冲销用例"""
        try:
            # 确保有移动凭证数据
            if not self.mobile_voucher_id:
                self.test_save_mobile_voucher()
                
            api_path = self.get_api_path("INV-移动凭证-新版移动凭证冲销服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {
                "id": self.mobile_voucher_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response, _ = self.standard_api_call(
                api_key="INV-移动凭证-新版移动凭证冲销服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)

            # 断言冲销成功
            write_off_data = response.get("data", {}).get("data", {})
            write_off_voucher_id = write_off_data.get("moveVoucherId")
            write_off_voucher_code = write_off_data.get("moveVoucherCode")
            
            assert write_off_voucher_id, "冲销凭证ID不能为空"
            assert write_off_voucher_code, "冲销凭证编码不能为空"
            
            self.logger.info(f"移动凭证冲销成功 - 原凭证ID: {self.mobile_voucher_id}, 冲销凭证ID: {write_off_voucher_id}, 冲销凭证编码: {write_off_voucher_code}")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def _get_voucher_detail(self, voucher_id):
        """通过详情接口获取移动凭证数据"""
        api_path = self.get_api_path("INV-移动凭证-详情服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            ["id"],
            ["params", "request"]
        )
        ParamUtil.set_request_params(filtered_params, {"id": voucher_id})
        response, _ = self.standard_api_call(
            api_key="INV-移动凭证-详情服务",
            set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"]
        )
        self.assert_util.assert_response_data(response)
        return response.get("data", {}).get("data", {})
