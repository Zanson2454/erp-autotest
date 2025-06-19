"""
组织类型管理模块测试用例
包含公司组织、采购组织、销售组织、库存组织、库存地点等类型组织的创建操作
"""

import sys
import time
import json
import random
import allure
import pytest
from pathlib import Path
from testcases.gen import GenBaseTest
from utils.report_util import a  # 导入简化的Allure辅助类
from utils.param_util import ParamUtil  # 导入参数处理工具类
import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("全维度组织管理")
class TestOrgType(GenBaseTest):
    """组织类型管理测试类"""
    
    # 保存组织相关信息的类变量，所有测试用例共享
    org_info = {
        "company": {},    # 公司组织信息
        "purchase": {},   # 采购组织信息
        "sales": {},      # 销售组织信息
        "inventory": {},  # 库存组织信息
        "location": {}    # 库存地点信息
    }
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.logger.info("组织类型管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("创建公司组织")
    @allure.description("""
    ## 测试步骤
    1. 生成唯一的组织编码和名称
    2. 准备公司组织创建请求数据
    3. 发送创建请求
    4. 验证响应结果
    5. 保存组织ID供后续测试使用
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建公司组织")
    @allure.tag("组织类型管理", "功能测试")
    def test_create_company_org(self):
        try:
            with a.step("1. 生成组织基础信息"):
                org_code = self.generate_unique_code("COM")
                org_name = self.generate_test_name("TEST_COMPANY")
                
                self.logger.info(f"生成公司组织编码: {org_code}, 名称: {org_name}")
                a.text(
                    f"公司组织编码: {org_code}\n公司组织名称: {org_name}",
                    "公司组织基本信息"
                )
            
            with a.step("2. 准备请求数据"):
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"创建公司组织API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgSort", "orgDimensionCode", 
                                 "orgBusinessTypeIds", "orgEnableDate", "def3", "def6", 
                                 "def12", "partnerId"], 
                                ["params", "request"])
                
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                self.set_request_params(filtered_params, {
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgSort": 1,
                    "orgDimensionCode": "SCM_ORG_GRP",  # 组织维度代码
                    "orgBusinessTypeIds": [2015007],  # 组织业务类型ID
                    "orgEnableDate": current_date,
                    "def3": 14037001,
                    "def6": 2000001,
                    "def12": 2002001,
                    "partnerId": 2058001
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送创建请求"):
                result = self.http.post(url, json=filtered_params, description="创建公司组织")
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                assert org_id, "创建公司组织失败：返回的ID为空"
                
                a.text(
                    f"公司组织ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("5. 保存测试数据"):
                TestOrgType.org_info["company"].update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                
                self.logger.info(f"创建公司组织成功 - ID: {org_id}, 编码: {org_code}")
                a.json(TestOrgType.org_info["company"], "保存的公司组织数据")
            
        except Exception as e:
            self.logger.error(f"创建公司组织失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("创建采购组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 生成唯一的组织编码和名称
    3. 准备采购组织创建请求数据
    4. 发送创建请求
    5. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建采购组织")
    @allure.tag("组织类型管理", "功能测试")
    def test_create_purchase_org(self):
        try:
            with a.step("1. 验证前置条件"):
                assert TestOrgType.org_info["company"].get("org_id"), "未找到公司组织ID，请先创建公司组织"
                a.json(TestOrgType.org_info["company"], "关联的公司组织信息")
            
            with a.step("2. 生成组织基础信息"):
                org_code = self.generate_unique_code("PUR")
                org_name = self.generate_test_name("TEST_PURCHASE")
                
                self.logger.info(f"生成采购组织编码: {org_code}, 名称: {org_name}")
                a.text(
                    f"采购组织编码: {org_code}\n采购组织名称: {org_name}",
                    "采购组织基本信息"
                )
            
            with a.step("3. 准备请求数据"):
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"创建采购组织API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgDimensionCode", 
                                 "orgBusinessTypeIds", "orgEnableDate", "orgParentId",
                                 "partnerId", "comOrgId", "orgParentCode"], 
                                ["params", "request"])
                
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 使用固定的未来日期
                
                # 获取父级组织信息
                parent_org_code = TestOrgType.org_info["company"]["org_code"]
                parent_org_id = TestOrgType.org_info["company"]["org_id"]
                
                self.set_request_params(filtered_params, {
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgDimensionCode": "SCM_ORG_GRP",  # 组织维度代码
                    "orgBusinessTypeIds": [2015006],  # 采购组织业务类型ID
                    "orgEnableDate": current_date,
                    "orgParentCode": parent_org_code,  # 父级组织编码
                    "orgParentId": parent_org_id,      # 父级组织ID
                    "comOrgId": parent_org_id,         # 公司组织ID
                    "partnerId": 2058001               # 合作伙伴ID
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("4. 发送创建请求"):
                result = self.http.post(url, json=filtered_params, description="创建采购组织")
                a.json(result, "响应数据")
            
            with a.step("5. 验证响应结果"):
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                assert org_id, "创建采购组织失败：返回的ID为空"
                
                a.text(
                    f"采购组织ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )
                
                TestOrgType.org_info["purchase"].update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                
                self.logger.info(f"创建采购组织成功 - ID: {org_id}, 编码: {org_code}")
                a.json(TestOrgType.org_info["purchase"], "保存的采购组织数据")
            
        except Exception as e:
            self.logger.error(f"创建采购组织失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("创建销售组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 生成唯一的组织编码和名称
    3. 准备销售组织创建请求数据
    4. 发送创建请求
    5. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建销售组织")
    @allure.tag("组织类型管理", "功能测试")
    def test_create_sales_org(self):
        try:
            with a.step("1. 验证前置条件"):
                assert TestOrgType.org_info["company"].get("org_id"), "未找到公司组织ID，请先创建公司组织"
                a.json(TestOrgType.org_info["company"], "关联的公司组织信息")
            
            with a.step("2. 生成组织基础信息"):
                org_code = self.generate_unique_code("SLS")
                org_name = self.generate_test_name("TEST_SALES")
                
                self.logger.info(f"生成销售组织编码: {org_code}, 名称: {org_name}")
                a.text(
                    f"销售组织编码: {org_code}\n销售组织名称: {org_name}",
                    "销售组织基本信息"
                )
            
            with a.step("3. 准备请求数据"):
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"创建销售组织API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgDimensionCode", 
                                 "orgBusinessTypeIds", "orgEnableDate", "orgParentId",
                                 "partnerId", "comOrgId", "orgParentCode", "def13"], 
                                ["params", "request"])
                
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # 获取父级组织信息
                parent_org_code = TestOrgType.org_info["company"]["org_code"]
                parent_org_id = TestOrgType.org_info["company"]["org_id"]
                
                self.set_request_params(filtered_params, {
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgDimensionCode": "SCM_ORG_GRP",  # 组织维度代码
                    "orgBusinessTypeIds": [2015005],  # 销售组织业务类型ID
                    "orgEnableDate": current_date,
                    "orgParentCode": parent_org_code,  # 父级组织编码
                    "orgParentId": parent_org_id,      # 父级组织ID
                    "comOrgId": parent_org_id,         # 公司组织ID
                    "partnerId": 2058001,              # 合作伙伴ID
                    "def13": [14378001]                # 销售组织特有字段
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("4. 发送创建请求"):
                result = self.http.post(url, json=filtered_params, description="创建销售组织")
                a.json(result, "响应数据")
            
            with a.step("5. 验证响应结果"):
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                assert org_id, "创建销售组织失败：返回的ID为空"
                
                a.text(
                    f"销售组织ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )
                
                TestOrgType.org_info["sales"].update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                
                self.logger.info(f"创建销售组织成功 - ID: {org_id}, 编码: {org_code}")
                a.json(TestOrgType.org_info["sales"], "保存的销售组织数据")
            
        except Exception as e:
            self.logger.error(f"创建销售组织失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("创建库存组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 生成唯一的组织编码和名称
    3. 准备库存组织创建请求数据
    4. 发送创建请求
    5. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建库存组织")
    @allure.tag("组织类型管理", "功能测试")
    def test_create_inventory_org(self):
        try:
            with a.step("1. 验证前置条件"):
                assert TestOrgType.org_info["company"].get("org_id"), "未找到公司组织ID，请先创建公司组织"
                a.json(TestOrgType.org_info["company"], "关联的公司组织信息")
            
            with a.step("2. 生成组织基础信息"):
                org_code = self.generate_unique_code("INV")
                org_name = self.generate_test_name("TEST_INVENTORY")
                
                self.logger.info(f"生成库存组织编码: {org_code}, 名称: {org_name}")
                a.text(
                    f"库存组织编码: {org_code}\n库存组织名称: {org_name}",
                    "库存组织基本信息"
                )
            
            with a.step("3. 准备请求数据"):
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"创建库存组织API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgDimensionCode", 
                                 "orgBusinessTypeIds", "orgEnableDate", "orgParentId",
                                 "partnerId", "comOrgId", "orgParentCode", "def14"], 
                                ["params", "request"])
                
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # 获取父级组织信息
                parent_org_code = TestOrgType.org_info["company"]["org_code"]
                parent_org_id = TestOrgType.org_info["company"]["org_id"]
                
                self.set_request_params(filtered_params, {
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgDimensionCode": "SCM_ORG_GRP",  # 组织维度代码
                    "orgBusinessTypeIds": [2015003],  # 库存组织业务类型ID
                    "orgEnableDate": current_date,
                    "orgParentCode": parent_org_code,  # 父级组织编码
                    "orgParentId": parent_org_id,      # 父级组织ID
                    "comOrgId": parent_org_id,         # 公司组织ID
                    "partnerId": 2058001,              # 合作伙伴ID
                    "def14": 70035560                  # 库存组织特有字段
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("4. 发送创建请求"):
                result = self.http.post(url, json=filtered_params, description="创建库存组织")
                a.json(result, "响应数据")
            
            with a.step("5. 验证响应结果"):
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                assert org_id, "创建库存组织失败：返回的ID为空"
                
                a.text(
                    f"库存组织ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )
                
                TestOrgType.org_info["inventory"].update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                
                self.logger.info(f"创建库存组织成功 - ID: {org_id}, 编码: {org_code}")
                a.json(TestOrgType.org_info["inventory"], "保存的库存组织数据")
            
        except Exception as e:
            self.logger.error(f"创建库存组织失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @allure.story("创建库存地点")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 生成唯一的组织编码和名称
    3. 准备库存地点创建请求数据
    4. 发送创建请求
    5. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建库存地点")
    @allure.tag("组织类型管理", "功能测试")
    def test_create_storage_location(self):
        try:
            with a.step("1. 验证前置条件"):
                assert TestOrgType.org_info["inventory"].get("org_id"), "未找到库存组织ID，请先创建库存组织"
                a.json(TestOrgType.org_info["inventory"], "关联的库存组织信息")
            
            with a.step("2. 生成组织基础信息"):
                org_code = self.generate_unique_code("LOC")
                org_name = self.generate_test_name("TEST_LOCATION")
                
                self.logger.info(f"生成库存地点编码: {org_code}, 名称: {org_name}")
                a.text(
                    f"库存地点编码: {org_code}\n库存地点名称: {org_name}",
                    "库存地点基本信息"
                )
            
            with a.step("3. 准备请求数据"):
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"创建库存地点API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgDimensionCode", 
                                 "orgBusinessTypeIds", "orgEnableDate", "orgParentId",
                                 "orgParentCode", "def2", "def7", "def8", "def9", "def10"], 
                                ["params", "request"])
                
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # 获取父级组织信息
                parent_org_code = TestOrgType.org_info["inventory"]["org_code"]
                parent_org_id = TestOrgType.org_info["inventory"]["org_id"]
                
                self.set_request_params(filtered_params, {
                    "orgCode": org_code,
                    "orgName": org_name,
                    "orgDimensionCode": "SCM_ORG_GRP",  # 组织维度代码
                    "orgBusinessTypeIds": [2015004],  # 库存地点业务类型ID
                    "orgEnableDate": current_date,
                    "orgParentCode": parent_org_code,  # 父级组织编码
                    "orgParentId": parent_org_id,      # 父级组织ID
                    "def2": 70035293,                  # 库存地点特有字段
                    "def7": "收货联系人",              # 收货联系人
                    "def8": "13732324455",            # 联系电话
                    "def9": "收货详细地址",            # 收货地址
                    "def10": 14510001                 # 其他配置
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("4. 发送创建请求"):
                result = self.http.post(url, json=filtered_params, description="创建库存地点")
                a.json(result, "响应数据")
            
            with a.step("5. 验证响应结果"):
                self.assert_util.assert_response_success(result)
                
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                assert org_id, "创建库存地点失败：返回的ID为空"
                
                a.text(
                    f"库存地点ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )
                
                TestOrgType.org_info["location"].update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                
                self.logger.info(f"创建库存地点成功 - ID: {org_id}, 编码: {org_code}")
                a.json(TestOrgType.org_info["location"], "保存的库存地点数据")
            
        except Exception as e:
            self.logger.error(f"创建库存地点失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestOrgType()
    test.setup_class()
    test.test_create_company_org()      # 创建公司组织
    test.test_create_purchase_org()     # 创建采购组织
    test.test_create_sales_org()        # 创建销售组织
    test.test_create_inventory_org()    # 创建库存组织
    test.test_create_storage_location() # 创建库存地点