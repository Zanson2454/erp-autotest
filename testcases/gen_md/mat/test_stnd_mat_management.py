import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("物料主数据")
@allure.feature("标准物料管理")
class TestStndMatManagement(GenMdBaseTest):
    """标准物料管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.matId = None
        
         # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
        cls.uom_info = cls.init_data["uom_info"] if cls.init_data.get("uom_info") else None
        cls.qty_uomId= cls.uom_info.get("qty_uom_info",[])[0]["uom_id"] if cls.uom_info.get("qty_uom_info") else None
        cls.mass_uomId = cls.uom_info.get("mass_uom_info",[])[0]["uom_id"] if cls.uom_info.get("mass_uom_info") else None
        cls.len_uomId = cls.uom_info.get("len_uom_info",[])[0]["uom_id"] if cls.uom_info.get("len_uom_info") else None
        cls.volume_uomId = cls.uom_info.get("volume_uom_info",[])[0]["uom_id"] if cls.uom_info.get("volume_uom_info") else None

        
        # 获取md_cache_data中的第一个数据
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
            mat_code = self.mock_data.generate_unique_code(tag="MAT")
            set_dict = {
                        "imageUrl": None,
                        "matCode": mat_code,
                        "matName": f"测试物料_{mat_code}",
                        "cateId": self.mat_cateId ,
                        "genMatTypeCfId": {"id": self.finp_matTypeId} ,
                        "baseUomId": {"id": self.qty_uomId},
                        "matAbbr": f"测试物料_{self.mock_data.get_timestamp()}",
                        "outerCode": f"OUTCODE_{self.mock_data.get_timestamp()}",
                        "brandId": self.brandId ,
                        "isKitSls": False,
                        "bomUseId": None,
                        "isCompleteSetDel": False,
                        "specModel": mat_code,
                        "bizStatus": "SALE",
                        "remark": f"自动化测试_{self.mock_data.get_mock_date(include_time=True)}",
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
            self.logger.info(f"请求参数: {params}")

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
                "cateId": 14082001,  # 使用指定的类目ID
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
            self.assert_util.assert_eq(status, "INACTIVE", "物料状态不正确")
            
            
            a.json(filtered_params, "详情请求数据")
            a.json(response, "详情响应数据")
            a.text(f"物料详情查询成功", "在库状态")

            # 字段一致性校验（与保存时部分字段比对）
    

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
