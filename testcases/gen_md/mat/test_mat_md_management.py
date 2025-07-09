import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("标准物料管理")
class TestStndMatManagement(GenMdBaseTest):
    """标准物料管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.matId = None
        
         # 获取初始化数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
        cls.uom_info = cls.init_data["uom_info"] if cls.init_data.get("uom_info") else None
        if cls.uom_info:
            cls.qty_uomId= cls.uom_info.get("qty_uom_info",[])[0]["uom_id"] if cls.uom_info.get("qty_uom_info") else None
            cls.mass_uomId = cls.uom_info.get("mass_uom_info",[])[0]["uom_id"] if cls.uom_info.get("mass_uom_info") else None
            cls.len_uomId = cls.uom_info.get("len_uom_info",[])[0]["uom_id"] if cls.uom_info.get("len_uom_info") else None
            cls.volume_uomId = cls.uom_info.get("volume_uom_info",[])[0]["uom_id"] if cls.uom_info.get("volume_uom_info") else None
        cls.logger.info(f'init_data: {cls.init_data}')
        cls.nickname = cls.init_data["user_info"]['user_info']["nickname"]
      

        
        # 获取md_cache_data缓存数据
        if cls.md_cache_data:
            cls.brandId = cls.md_cache_data.get("mat_info",{}).get("mat_brand_md",[])[0]["id"] if cls.md_cache_data.get("mat_info") else None
            cls.mat_cateId = cls.md_cache_data.get("mat_info", {}).get("mat_cate_md", [])[0]["id"] if cls.md_cache_data.get("mat_info", {}).get("mat_cate_md") else None
            cls.finp_matTypeId = cls.md_cache_data.get("mat_info", {}).get("mat_type_cf", {}).get("FINP",[])[0]["id"] if cls.md_cache_data.get("mat_info", []).get("mat_type_cf") else None
            cls.atpGroupId = cls.md_cache_data.get("mat_info", {}).get("inv_atp_group_md",[])[0]["id"] if cls.md_cache_data.get("mat_info", {}).get("inv_atp_group_md") else None
            cls.labelId = cls.md_cache_data.get("mat_info", {}).get("gen_label_md",[])[0]["id"] if cls.md_cache_data.get("mat_info", {}).get("gen_label_md") else None
        
        cls.logger.info("标准物料管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的物料数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="gen_mat_md",
                where="mat_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    
    @case_decorator(
        story="标准物料管理",
        title="测试新增物料主数据保存",
        description="验证新增物料主数据保存接口功能",
        severity="critical",
        order=1,
        tags=["标准物料管理", "新增", "保存"]
    )
    def test_save_mat(self):
        """
        新增物料主数据保存用例
        """
        try:
            # 1. 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-物料主数据-保存服务")  # 建议配置到md_api_path.yaml
            params, url = self.get_api_params(api_path)

        
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["matCode", "matName", "cateId", "genMatTypeCfId", "baseUomId", "matAbbr", "outerCode", "brandId", "isKitSls", "bomUseId", "isCompleteSetDel", "specModel", "bizStatus", "remark", "customMat", "labelList", "id", "weightUomId", "grossWeight", "netWeight", "volumeUomId", "matVolume", "lengthUnitId", "length", "width", "height", "purchaseReferPrice", "saleReferPrice", "shelfLife", "costPrice", "atpGroupId", "matPurList", "matSlsList", "matInvList", "matWmList"],
                ["params", "request"]
            )
            # 2. 构造请求参数，补充更多字段
            mat_code = self.mock_util.generate_unique_code(tag="MAT")
            set_dict = {
                        "imageUrl": None,
                        "matCode": mat_code,
                        "matName": f"测试物料_{mat_code}",
                        "cateId": self.mat_cateId ,
                        "genMatTypeCfId": {"id": self.finp_matTypeId} ,
                        "baseUomId": {"id": self.qty_uomId},
                        "matAbbr": f"测试物料_{self.mock_util.get_timestamp()}",
                        "outerCode": f"OUTCODE_{self.mock_util.get_timestamp()}",
                        "brandId": self.brandId ,
                        "isKitSls": False,
                        "bomUseId": None,
                        "isCompleteSetDel": False,
                        "specModel": mat_code,
                        "bizStatus": "SALE",
                        "remark": f"自动化测试_{self.mock_util.get_mock_date(include_time=True)}",
                        "customMat": False,
                        "labelList": [{"id": self.labelId}],
                        "id": None,
                        "weightUomId": {"id": self.mass_uomId},
                        "grossWeight": 10,
                        "netWeight": 8.88,
                        "volumeUomId": {"id": self.volume_uomId},
                        "matVolume": 1.23,
                        "lengthUnitId": {"id": self.len_uomId},
                        "length": 999,
                        "width": 888,
                        "height": 666,
                        "purchaseReferPrice": 999.99,
                        "saleReferPrice": 10000,
                        "shelfLife": "1",
                        "costPrice": 999.99,
                        "atpGroupId": { "id": self.atpGroupId},
                        "matPurList": None,
                        "matSlsList": None,
                        "matInvList": None,
                        "matWmList": None
                    }
            ParamUtil.set_request_params(filtered_params, set_dict)

            # 3. 发起请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response,"保存失败")

            self.matId = response.get("data",{}).get("data",{})
            self.logger.info(f"保存成功，物料ID: {TestStndMatManagement.matId}")

            # 4. 断言与附件
            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="标准物料管理",
        title="测试基于类目查询物料",
        description="验证基于类目查询物料列表功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["标准物料管理", "查询"]
    )
    def test_query_mat_by_cate(self):
        """
        基于类目查询物料用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-物料主数据-查询分页服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["cateId", "pageable"],
                ["params", "request"]
            )
            set_dict = {
                "cateId": self.mat_cateId,  # 使用指定的类目ID
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": [],
                    "conditionItems": None
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data = response.get("data", {}).get("data", {})
            # 验证返回数据的正确性
            self.assert_util.assert_response_data(response,"物料列表无数据")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试物料详情查询",
        description="验证物料保存后可通过ID查询详情",
        severity="critical",
        order=3,
        tags=["标准物料管理", "详情", "查询"]
    )
    def test_query_mat_detail(self):
        """
        物料详情查询用例，依赖 test_save_mat 先执行
        """
        try:
            if not self.matId:
                self.test_save_mat()
            # 获取接口路径和参数模板
            api_path = self.get_api_path("GEN-物料主数据-查询详情服务")
            params, url = self.get_api_params(api_path)
         
            # 构造请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.matId}
            
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"详情请求参数: {filtered_params}")

            # 发起请求
            response = self.http.post(url, json=filtered_params)
            status = response.get("data",{}).get("data",{}).get("status",{})
            self.assert_util.assert_response_data(response, "详情查询失败")
            self.assert_util.assert_by_operator(status, "=", "INACTIVE")
            
            
            a.json(filtered_params, "详情请求数据")
            a.json(response, "详情响应数据")
            a.text(f"物料详情查询成功", "在库状态")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试根据ID查找物料数据",
        description="验证根据ID查找物料数据服务",
        severity="normal",
        order=4,
        tags=["标准物料管理", "查找", "ID"]
    )
    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    def test_find_mat_by_id(self):
        """
        根据ID查找物料数据用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("物料主数据-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.matId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试启用物料",
        description="验证物料启用功能",
        severity="normal",
        order=5,
        tags=["标准物料管理", "启用"]
    )
    def test_enable_mat(self):
        """
        启用物料用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.matId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试禁用物料",
        description="验证物料禁用功能",
        severity="normal",
        order=6,
        tags=["标准物料管理", "禁用"]
    )
    def test_disable_mat(self):
        """
        禁用物料用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.matId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试批量生成物料条码",
        description="验证批量生成物料条码功能",
        severity="normal",
        order=7,
        tags=["标准物料管理", "批量", "条码"]
    )
    def test_batch_create_barcode(self):
        """
        批量生成物料条码用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-批量生成条码服务")
            params, url = self.get_api_params(api_path)

            
            self.logger.info(f"原始请求参数: {params}")
            params['params']['request'] = [{"id": self.matId}]
            self.logger.info(f"修改后的请求参数: {params}")
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试批量物料打标",
        description="验证批量物料打标功能",
        severity="normal",
        order=8,
        tags=["标准物料管理", "批量", "打标"]
    )
    def test_batch_set_label(self):
        """
        批量物料打标用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-批量打标服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["mat_ids", "label_list"],
                ["params", "request"]
            )
            set_dict = {
                "mat_ids": [self.matId],
                "label_list": [{"id":self.labelId}]
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
        story="标准物料管理",
        title="测试批量取消物料打标",
        description="验证批量取消物料打标功能",
        severity="normal",
        order=9,
        tags=["标准物料管理", "批量", "取消打标"]
    )
    def test_batch_cancel_label(self):
        """
        批量取消物料打标用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-批量取消打标服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["mat_ids", "label_list"],
                ["params", "request"]
            )
            set_dict = {
                "mat_ids": [self.matId],
                "label_list": [{"id":self.labelId}]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="标准物料管理",
        title="测试物料标准导出",
        description="验证物料标准导出功能",
        severity="normal",
        order=10,
        tags=["标准物料管理", "导出"]
    )
    def test_export_mat(self):
        """
        物料标准导出用例
        """
        try:
            api_path = self.get_api_path("物料主数据标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料主数据导出_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料主数据"
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

    @pytest.mark.skip(reason="业务未引用，暂时跳过")
    @case_decorator(
        story="标准物料管理",
        title="测试物料标准导入",
        description="验证物料标准导入功能",
        severity="normal",
        order=11,
        tags=["标准物料管理", "导入"]
    )
    def test_import_mat(self):
        """
        物料标准导入用例（需要文件上传）
        """
        try:
            api_path = self.get_api_path("物料主数据标准导入服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["exportConfig"],
                ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fileName": f"物料主数据导入_{self.mock_util.get_timestamp()}",
                    "sheetName": "物料主数据"
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

    @case_decorator(
        story="标准物料管理",
        title="测试提交物料导出任务",
        description="验证提交物料导出任务功能",
        severity="normal",
        order=12,
        tags=["标准物料管理", "导出任务"]
    )
    def test_submit_export_task(self):
        """
        提交物料导出任务用例
        """
        try:
            api_path = self.get_api_path("物料主数据-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
    
            params = {
                "serviceKey": "GEN_MD$GEN_MAT_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params":{
                    "taskName": f"物料_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_mat_md",
                            "modelName": "物料主数据",
                            "sheetNo": 0,
                            "sheetName": "物料主数据",
                            "headerConfigList": [
                                {
                                    "name": "物料图片",
                                    "type": "ATTACHMENT",
                                    "field": "imageUrl"
                                },
                                {
                                    "name": "物料编码",
                                    "type": "TEXT",
                                    "field": "matCode"
                                },
                                {
                                    "name": "物料名称",
                                    "type": "TEXT",
                                    "field": "matName"
                                },
                                {
                                    "name": "物料类型",
                                    "type": "TEXT",
                                    "field": "genMatTypeCfId.matTypeName"
                                },
                                {
                                    "name": "类目",
                                    "type": "TEXT",
                                    "field": "cateId.matCateName"
                                },
                                {
                                    "name": "品牌",
                                    "type": "TEXT",
                                    "field": "brandId.brandName"
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
                                    "name": "业务状态",
                                    "type": "ENUM",
                                    "field": "bizStatus",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "SALE",
                                            "label": "可销售",
                                            "value": "SALE"
                                        },
                                        {
                                            "_row_id_": "OFF_SALE",
                                            "label": "已停售",
                                            "value": "OFF_SALE"
                                        },
                                        {
                                            "_row_id_": "STOP_PRODUCT",
                                            "label": "已停产",
                                            "value": "STOP_PRODUCT"
                                        },
                                        {
                                            "_row_id_": "UNSALE",
                                            "label": "不可销售",
                                            "value": "UNSALE"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_SCM$GEN_MAT_NEW_VIEW-r8WLZs8B_0Zu8fIHUDWOu",
                        "viewKey": "GEN_MD$GNE_MAT_VIEW:list",
                        "sceneKey": "GEN_MD$GNE_MAT_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": [

                                    ]
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "imageUrl"
                                },
                                {
                                    "field": "matCode"
                                },
                                {
                                    "field": "matName"
                                },
                                {
                                    "field": "status"
                                },
                                {
                                    "field": "bizStatus"
                                },
                                {
                                    "field": "genMatTypeCfId",
                                    "selectFields": [
                                        {
                                            "field": "matTypeName"
                                        }
                                    ]
                                },
                                {
                                    "field": "cateId",
                                    "selectFields": [
                                        {
                                            "field": "matCateName"
                                        }
                                    ]
                                },
                                {
                                    "field": "brandId",
                                    "selectFields": [
                                        {
                                            "field": "brandName"
                                        }
                                    ]
                                }
                            ],
                            "modelKey": "GEN_MD$gen_mat_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_mat_md",
                        "modelName": "物料主数据",
                        "containerKey": "ERP_SCM$GEN_MAT_NEW_VIEW-r8WLZs8B_0Zu8fIHUDWOu",
                        "viewKey": "GEN_MD$GNE_MAT_VIEW:list",
                        "sceneKey": "GEN_MD$GNE_MAT_VIEW"
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

    @pytest.mark.skip(reason="暂时未配置，先跳过")
    @case_decorator(
        story="标准物料管理",
        title="测试通过OSS提交物料导入任务",
        description="验证通过OSS提交物料导入任务功能",
        severity="normal",
        order=13,
        tags=["标准物料管理", "OSS导入"]
    )
    def test_submit_import_task_by_oss(self):
        """
        通过OSS提交物料导入任务用例（需要OSS配置）
        """
        pass

    @case_decorator(
        story="标准物料管理",
        title="测试物料主数据分页数据服务",
        description="验证物料主数据分页数据服务",
        severity="normal",
        order=13,
        tags=["标准物料管理", "分页数据"]
    )
    def test_mat_paging_data(self):
        """
        物料主数据分页数据服务用例
        """
        try:
            api_path = self.get_api_path("物料主数据-分页数据服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageNo", "pageSize"],
                ["params", "request"]
            )
            set_dict = {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "conditionGroup": None,
                "sortOrders": None,
                "keyword": None
            }}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标准物料管理",
        title="测试删除物料",
        description="验证删除物料功能",
        severity="normal",
        order=14,
        tags=["标准物料管理", "删除"]
    )
    def test_delete_mat(self):
        """
        删除物料用例
        """
        try:
            if not self.matId:
                self.test_save_mat()

            api_path = self.get_api_path("GEN-物料主数据-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.matId}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
