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
        cls.mat_info = {}
        
         # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
     
        
        # 获取md_cache_data中的第一个数据
        cls.brandId = cls.md_cache_data.get("mat_info",{}).get("mat_brand_md",[])[0]["id"] if cls.md_cache_data.get("mat_info") else None
        cls.mat_cateId = cls.md_cache_data.get("mat_info", {}).get("mat_cate_md", [])[0]["id"] if cls.md_cache_data.get("mat_info", {}).get("sls_dc_md") else None
        cls.matTypeId = cls.md_cache_data.get("mat_info", {}).get("mat_type_cf", [])[0]["id"] if cls.md_cache_data.get("mat_info", {}).get("sls_dc_md") else None
        
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
        title="测试基于类目查询物料",
        description="验证基于类目查询物料列表功能",
        severity="normal",
        order=1,
        smoke=True,
        tags=["标准物料管理", "查询"]
    )
    def test_query_mat_by_cate(self):
        """
        基于类目查询物料用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("GEN-物料-查询分页服务")
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
            data_list = data.get("data", [])
            total = data.get("total", 0)
            
            # 验证返回数据的正确性
            self.assert_util.assert_true(isinstance(total, int), "返回的total不是整数类型")
            if total > 0:
                self.assert_util.assert_not_empty(data_list, "返回的物料列表为空")
                # 验证第一条数据包含必要的字段
                first_item = data_list[0]
                self.assert_util.assert_not_none(first_item.get("matCode"), "物料编码为空")
                self.assert_util.assert_not_none(first_item.get("matName"), "物料名称为空")
                self.assert_util.assert_not_none(first_item.get("matCateId"), "物料类目ID为空")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
