"""
BOM物料管理模块测试用例
包含BOM物料新增、查询、启用、停用等操作
"""

import sys
import allure
import pytest
from pathlib import Path
from testcases.gen import GenBaseTest
from utils.allure_simple import a  # 导入简化的Allure辅助类
from utils.param_util import ParamUtil  # 导入参数处理工具类
import random

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("BOM物料管理")
class TestBomMat(GenBaseTest):
    """BOM物料管理测试类"""
    
    # 保存BOM物料相关信息的类变量，所有测试用例共享
    bom_mat_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        # 调用GenBaseTest的初始化方法
        # 这会初始化logger、http客户端、断言工具和YAML处理器等
        super().setup_class()
        
        cls.logger.info("BOM物料管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("新增BOM物料")
    @allure.description("""
    ## 测试步骤
    1. 生成唯一的BOM物料编码和名称
    2. 准备BOM物料创建请求数据
    3. 发送创建BOM物料API请求
    4. 验证返回结果是否成功
    5. 保存BOM物料ID供后续测试使用
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("新增BOM物料流程")
    @allure.tag("BOM物料管理", "功能测试")
    def test_bom_mat_add(self):
        try:
            with a.step("1. 生成BOM物料基础信息"):
                # 使用基类方法生成唯一编码和名称
                bom_code = self.generate_unique_code("BOM")
                bom_name = self.generate_test_name("TEST_BOM")
                remark = self.generate_remark()
                vrs_code = str(random.randint(1, 9999))
                
                # 记录生成的信息
                self.logger.info(f"生成BOM物料编码: {bom_code}, 名称: {bom_name}, 版本号: {vrs_code}")
                # 添加到报告中
                a.text(
                    f"BOM物料编码: {bom_code}\nBOM物料名称: {bom_name}\n版本号: {vrs_code}\n备注: {remark}",
                    "BOM物料基本信息"
                )
                
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("物料BOM头表-创建数据服务")
                self.logger.debug(f"BOM物料新增API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["invOrgId", "matId", "bomUseId", "vrsCode", "vrsName", "baseQty", 
                                 "uomId", "statusId", "dateFrom", "dateTo", "genBomItemMdId", "batchFrom", "batchTo"], 
                                ["params", "request"])
                
                # 使用基类方法批量设置参数
                self.set_request_params(filtered_params, {
                    "invOrgId": {"id": 14375002},  # 库存组织ID
                    "matId": {"id": 14618004},     # 物料ID
                    "bomUseId": {"id": 1},         # BOM用途ID
                    "vrsCode": vrs_code,           # 随机生成的版本号
                    "vrsName": "info",             # 版本名称
                    "batchFrom": 0,
                    "batchTo": 9999999,
                    "baseQty": 1,                  # 基本数量
                    "uomId": {"id": 2004001},      # 单位ID
                    "statusId": {"id": 2000002},   # 状态ID
                    "dateFrom": 1748880000000,     # 生效日期
                    "dateTo": "9999-12-30T16:00:00.000Z",  # 失效日期
                    "genBomItemMdId": [{           # BOM组件明细
                        "matId": {"id": 14618004},
                        "qty": 1,
                        "uomId": {"id": 2004001},
                        "faxQtyIs": True,
                        "scrapRate": 0,
                        "invOrgId": {"id": 14375002},
                        "componentScrap": 0,
                        "itemTypeId": {"id": 2000001},
                        "itemTypeId": {"id": 2000001},
                        "scrapType": "SINGLE",
                        "prodInv": {"id": 14376002}
                    }]
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="新增BOM物料")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取BOM物料ID
                response_data = result.get("data", {}).get("data", {})
                bom_id = response_data.get("id")
                
                # 确保返回了有效的ID
                assert bom_id, "新增BOM物料失败：返回的ID为空"
                
                # 记录验证结果
                a.text(
                    f"BOM物料ID: {bom_id}\n验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("5. 保存测试数据"):
                # 保存测试数据到类变量，供后续测试用例使用
                TestBomMat.bom_mat_info.update({
                    "bom_id": bom_id,
                    "bom_code": bom_code,
                    "bom_name": bom_name,
                    "vrs_code": vrs_code  # 保存版本号供查询使用
                })
                
                self.logger.info(f"新增BOM物料成功 - ID: {bom_id}, 编码: {bom_code}")
                
                # 记录保存的数据
                a.json(TestBomMat.bom_mat_info, "保存的BOM物料数据")
            
        except Exception as e:
            self.logger.error(f"新增BOM物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("查询BOM物料")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备查询条件
    3. 发送查询请求
    4. 验证查询结果
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查询BOM物料流程")
    @allure.tag("BOM物料管理", "功能测试")
    def test_bom_mat_search(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保bom_mat_info中有数据
                assert TestBomMat.bom_mat_info.get("vrs_code"), "未找到要查询的BOM物料版本号，请先执行新增用例"
                
                # 添加到报告中
                a.json(TestBomMat.bom_mat_info, "待查询BOM物料信息")
            
            with a.step("2. 准备查询参数"):
                # 获取API路径
                api_path = self.get_api_path("物料BOM头表-分页数据服务_oyQmuH1")
                self.logger.debug(f"BOM物料查询API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                              ["pageable"], ["params", "request"])
                
                # 构建简化的查询参数
                search_params = {
                    "pageable": {
                        "conditionGroup": {
                            "conditions": [
                                {
                                    "type": "ConditionLeaf",
                                    "leftValue": {
                                        "type": "VarValue",
                                        "fieldType": "Text",
                                        "valueType": "VAR",
                                        "varValue": [{"valueKey": "vrsCode", "valueName": "vrsCode"}]
                                    },
                                    "operator": "CONTAINS",
                                    "rightValue": {
                                        "type": "VarValue",
                                        "fieldType": "Text",
                                        "valueType": "CONST",
                                        "constValue": TestBomMat.bom_mat_info["vrs_code"]
                                    }
                                }
                            ]
                        }
                    }
                }
                
                # 更新过滤后的参数
                filtered_params["params"]["request"].update(search_params)
                
                self.logger.info(f"查询的BOM物料版本号: {TestBomMat.bom_mat_info['vrs_code']}")
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送查询请求"):
                # 发送查询请求
                result = self.http.post(url, json=filtered_params, description="查询BOM物料")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取响应数据
                response_data = result.get("data", {}).get("data", {})
                
                # 验证总数大于0
                total = response_data.get("total", 0)
                assert total > 0, "查询结果总数为0"
                
                # 记录验证结果
                a.text(f"查询BOM物料总数: {total}", "验证结果 - 总数")
            
            with a.step("5. 验证查询内容"):
                # 获取数据列表
                data_list = response_data.get("data", [])
                
                # 验证返回的数据列表不为空
                assert data_list, "查询结果为空"
                
                # 验证查询结果包含新增的BOM物料版本号
                found = any(item.get("vrsCode") == TestBomMat.bom_mat_info["vrs_code"] for item in data_list)
                assert found, f"未找到BOM物料版本号: {TestBomMat.bom_mat_info['vrs_code']}"
                
                # 记录验证结果
                a.text(
                    f"查询结果项数: {len(data_list)}\n包含目标版本号: {found}",
                    "验证结果 - 内容"
                )
                
                # 添加查询到的第一条记录到报告
                if data_list:
                    a.json(data_list[0], "查询结果示例")
                
                self.logger.info(f"查询BOM物料成功 - 总数: {total}")
            
        except Exception as e:
            self.logger.error(f"查询BOM物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("编辑BOM物料")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备编辑请求数据
    3. 发送编辑请求
    4. 验证响应结果
    5. 保存更新后的数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("编辑BOM物料-修改版本号")
    @allure.tag("BOM物料管理", "功能测试")
    def test_bom_mat_edit(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保已经创建过BOM物料
                assert TestBomMat.bom_mat_info.get("bom_id"), "未找到要编辑的BOM物料ID，请先执行新增用例"
                
                # 生成新的版本号 (1-9999之间的数字转为字符串)
                new_vrs_code = str(random.randint(1, 9999))
                self.logger.info(f"原版本号: {TestBomMat.bom_mat_info.get('vrs_code')}, 新版本号: {new_vrs_code}")
                
                # 添加到报告中
                a.json({
                    "原版本号": TestBomMat.bom_mat_info.get("vrs_code"),
                    "新版本号": new_vrs_code,
                    "BOM_ID": TestBomMat.bom_mat_info.get("bom_id")
                }, "编辑前的BOM物料信息")
            
            with a.step("2. 准备编辑请求数据"):
                # 获取API路径
                api_path = self.get_api_path("物料BOM头表-保存主数据服务")
                self.logger.debug(f"BOM物料编辑API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                [ "vrsCode", "id"], 
                                ["params", "request"])
                
                # 使用基类方法批量设置参数
                self.set_request_params(filtered_params, {
                    "id": TestBomMat.bom_mat_info["bom_id"],  # 设置BOM ID
                    "vrsCode": new_vrs_code,       # 使用新的版本号
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送编辑请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="编辑BOM物料")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取更新后的数据
                response_data = result.get("data", {}).get("data", {})
                updated_vrs_code = response_data.get("vrsCode")
                
                # 确保返回了正确的版本号
                assert updated_vrs_code == new_vrs_code, f"版本号更新不正确。预期: {new_vrs_code}, 实际: {updated_vrs_code}"
                
                # 记录验证结果
                a.text(
                    f"BOM物料ID: {response_data.get('id')}\n"
                    f"更新后的版本号: {updated_vrs_code}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("5. 保存更新后的数据"):
                # 更新测试数据到类变量
                TestBomMat.bom_mat_info["vrs_code"] = updated_vrs_code
                
                self.logger.info(f"编辑BOM物料成功 - ID: {response_data.get('id')}, 新版本号: {updated_vrs_code}")
                
                # 记录保存的数据
                a.json(TestBomMat.bom_mat_info, "更新后的BOM物料数据")
            
        except Exception as e:
            self.logger.error(f"编辑BOM物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("删除BOM物料")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备删除请求数据
    3. 发送删除请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("删除BOM物料")
    @allure.tag("BOM物料管理", "功能测试")
    def test_bom_mat_delete(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保已经创建过BOM物料
                assert TestBomMat.bom_mat_info.get("bom_id"), "未找到要删除的BOM物料ID，请先执行新增用例"
                
                # 添加到报告中
                a.json({
                    "BOM_ID": TestBomMat.bom_mat_info.get("bom_id"),
                    "版本号": TestBomMat.bom_mat_info.get("vrs_code")
                }, "待删除的BOM物料信息")
            
            with a.step("2. 准备删除请求数据"):
                # 获取API路径
                api_path = self.get_api_path("物料BOM头表-根据ID删除数据服务")
                self.logger.debug(f"BOM物料删除API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["id"], 
                                ["params", "request"])
                
                # 使用基类方法批量设置参数
                self.set_request_params(filtered_params, {
                    "id": TestBomMat.bom_mat_info["bom_id"]  # 设置要删除的BOM ID
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送删除请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="删除BOM物料")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(
                    f"删除BOM物料成功\n"
                    f"BOM ID: {TestBomMat.bom_mat_info['bom_id']}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
                
                self.logger.info(f"删除BOM物料成功 - ID: {TestBomMat.bom_mat_info['bom_id']}")
            
        except Exception as e:
            self.logger.error(f"删除BOM物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestBomMat()
    test.setup_class()
    test.test_bom_mat_add()      # 新增BOM物料
    test.test_bom_mat_search()   # 查询BOM物料
    test.test_bom_mat_edit()     # 编辑BOM物料
    test.test_bom_mat_delete()   # 删除BOM物料

