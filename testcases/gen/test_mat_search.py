import os
import sys
import allure
from pathlib import Path
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

# 添加项目根目录到 Python 路径，确保可以正确导入项目模块
project_root = Path(__file__).resolve().parent.parent.parent  # 值: /Users/shengqiaowei/Desktop/erp-autotest
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("物料管理_物料列表查询")
class TestMatSearch(BaseTest):
    @classmethod
    def setup_class(cls):
        # 调用父类的初始化方法
        super().setup_class()
        
        # 初始化配置文件路径和YAML工具
        cls.base_api_path = Path(project_root) / "testdata" / "gen" / "mat.yaml"
        # 值: /Users/shengqiaowei/Desktop/erp-autotest/testdata/gen/mat.yaml
        
        cls.base_config_path = Path(project_root) / "testdata" / "gen" / "mat_api_params.yaml"
        # 值: /Users/shengqiaowei/Desktop/erp-autotest/testdata/gen/mat_api_params.yaml
        
        cls.yaml_util = YamlUtil()
        
        # 从YAML文件读取接口路径和参数
        cls.mat_path = cls.yaml_util.read_yaml(cls.base_api_path)["通用基础"]["物料管理"]
        # mat_path值示例: {
        #   "物料主数据默认页面": "/api/trantor/service/engine/execute/ERP_GEN$gen_mat_md_PAGING_DATA_SERVICE?tmodule=ERP_SCM"
        # }
        
        cls.mat_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})
        # mat_params值示例: {
        #   "/api/.../gen_mat_md_PAGING_DATA_SERVICE?tmodule=ERP_SCM": {
        #     "params": {
        #       "request": {
        #         "pageable": {
        #           "pageNo": 1,
        #           "pageSize": 20,
        #           "keyword": "",
        #           "conditionGroup": None,
        #           "sortOrders": [{"fieldAlias": "updatedAt", "id": "updatedAt-0", "sortType": "DESC"}]
        #         },
        #         "cateId": None
        #       }
        #     }
        #   }
        # }
        
        cls.logger.info("测试类初始化完成")

    @allure.story("物料列表查询")
    @allure.description("测试步骤：物料列表查询")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("物料列表查询")
    def test_mat_search(self):
        try:
            # 1. 获取接口路径和参数
            url = self.mat_path["物料主数据默认页面"]
            # url作为key，用于从mat_params中获取对应的请求参数
            self.logger.debug(f"接口URL: {url}")
            self.logger.debug(f"mat_params原始数据: {self.mat_params}")
            
            # 使用url作为key从mat_params中获取对应的参数配置，如果获取不到就返回{}
            data = self.mat_params.get(url, {})
            self.logger.debug(f"获取到的请求参数: {data}")
            
            # 2. 发送POST请求并获取响应
            result = self.http.post(url, json=data, description="查询物料列表")
            #result里的值先取第一层data，再取第二层data，data是参数名，拿到第三层data才是我们想要的数据
            response_data = result.get("data", {}).get("data", {})
            # response_data值示例: {
            #   "data": [
            #     {
            #       "matCode": "W1790",
            #       "matName": "XB三力士普通带001",
            #       "genMatTypeCfId": {"matTypeName": "成品", "id": 2000001},
            #       "baseUomId": {"uomDesc": "件", "id": 2004001},
            #       "status": "ENABLED",
            #       "bizStatus": "SALE",
            #       ...
            #     },
            #     ...
            #   ],
            #   "total": 330
            # }
            
            # 3. 验证响应结果，调用工具类判断是否=200 和 success是否=true
            self.assert_util.assert_response_success(result)
            # 验证result["success"] == true
            
            # 验证返回的total字段（总记录数）不为空且大于0
            total = response_data.get("total")  # 值示例: 330
            assert total is not None and total > 0, f"物料总数异常: {total}"
            
            # 验证返回的数据列表不为空
            data_list = response_data.get("data", [])  
            # data_list值示例: [
            #   {
            #     "matCode": "W1790",
            #     "matName": "XB三力士普通带001",
            #     "status": "ENABLED",
            #     "bizStatus": "SALE",
            #     ...
            #   },
            #   ...
            # ]
            assert len(data_list) > 0, "返回的物料列表为空"
            
            self.logger.info(f"物料列表查询完成，总记录数: {total}")
            
        except Exception as e:
            self.logger.error(f"物料列表查询失败: {str(e)}")
            raise

if __name__ == "__main__":
    # 直接运行测试用例
    test = TestMatSearch()
    test.setup_class()
    test.test_mat_search()