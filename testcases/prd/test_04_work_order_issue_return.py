# -*- coding: utf-8 -*-
"""
生产订单退料测试用例
包含根据生产订单领料单创建退料单等操作
"""
import sys
import time
import json
import allure
import pytest
from pathlib import Path
from testcases.prd import PrdBaseTest
from utils.allure_simple import a
from utils.param_util import ParamUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("生产管理")
@allure.feature("生产订单退料")
class TestPrdOrderIssueReturn(PrdBaseTest):
    """生产订单退料测试类"""
    
    # 保存测试过程中的数据
    issue_return_info = {}
    rule_render_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.logger.info("生产订单退料测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("获取默认领料分单规则")
    @allure.title("获取默认领料分单规则-接口校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    ## 测试步骤
    1. 准备请求参数
    2. 发送请求获取默认领料分单规则
    3. 校验接口响应结构和关键字段
    4. 保存接口返回数据
    """)
    def test_get_issue_rule_render_default(self):
        try:
            with a.step("1. 准备请求参数"):
                # 获取API路径
                api_path = self.get_api_path("渲染默认领料分单规则服务")
                self.logger.debug(f"获取默认领料分单规则API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 构建请求参数
                filtered_params = {
                    "params": {
                        "request": {}
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")

            with a.step("2. 发送请求获取默认领料分单规则"):
                result = self.http.post(url, json=filtered_params, description="获取默认领料分单规则")
                a.json(result, "接口响应")

            with a.step("3. 校验接口响应结构和关键字段"):
                self.assert_util.assert_response_success(result)
                assert result.get("data"), "响应data字段为空"
                a.text("默认领料分单规则获取成功", "验证结果")

            with a.step("4. 保存接口返回数据"):
                TestPrdOrderIssueReturn.rule_render_info.update({
                    "response": result
                })
                self.logger.info("默认领料分单规则接口返回数据已保存")
                a.json(TestPrdOrderIssueReturn.rule_render_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"获取默认领料分单规则失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("获取领料分单规则明细")
    @allure.title("获取领料分单规则明细-接口校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    ## 测试步骤
    1. 准备请求参数
    2. 发送请求获取领料分单规则明细
    3. 校验接口响应结构和关键字段
    4. 保存接口返回数据
    """)
    def test_get_issue_rule_items(self):
        try:
            with a.step("1. 准备请求参数"):
                api_path = self.get_api_path("(系统)查询分页数据服务") + \
                          "?tmodule=ERP_PRD&modelKey=ERP_PRD$prd_issue_rule_item_cf"
                self.logger.debug(f"获取领料分单规则明细API路径: {api_path}")
                
                params, url = self.get_api_params(api_path)
                
                filtered_params = {
                    "params": {
                        "modelKey": "ERP_PRD$prd_issue_rule_item_cf",
                        "request": {
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 1000,
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {
                                        "prdIssueRuleCfId": {
                                            "operator": "EQ",
                                            "value": TestPrdOrderIssueReturn.rule_render_info \
                                                    .get("response", {}) \
                                                    .get("data", {}) \
                                                    .get("data", {}) \
                                                    .get("id")
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")

            with a.step("2. 发送请求获取领料分单规则明细"):
                result = self.http.post(url, json=filtered_params, description="获取领料分单规则明细")
                a.json(result, "接口响应")

            with a.step("3. 校验接口响应结构和关键字段"):
                self.assert_util.assert_response_success(result)
                
                data_list = result.get("data", {}).get("data", {}).get("data", [])
                assert isinstance(data_list, list), "响应data字段不是列表类型"
                assert len(data_list) > 0, "响应数据列表为空"
                
                first_item = data_list[0]
                assert first_item.get("item") is not None, "数据项缺少item字段"
                assert first_item.get("defaultValue") is not None, "数据项缺少defaultValue字段"
                assert first_item.get("id") is not None, "数据项缺少id字段"
                
                a.text(f"获取到{len(data_list)}条领料分单规则明细数据", "验证结果")

            with a.step("4. 保存接口返回数据"):
                TestPrdOrderIssueReturn.rule_render_info.update({
                    "items": result
                })
                self.logger.info("领料分单规则明细接口返回数据已保存")
                a.json(TestPrdOrderIssueReturn.rule_render_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"获取领料分单规则明细失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("创建待提交生产订单退料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送创建待提交退料单请求
    3. 验证响应结果
    4. 保存创建结果数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("根据领料单创建待提交退料单")
    def test_create_issue_return_by_issue(self):
        """根据领料单创建待提交退料单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据领料单创建退料单服务")
                self.logger.debug(f"创建待提交退料单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 获取最新的可退料行项目
                sql = """
                SELECT i.id
                        FROM prd_issue_item_tr i
                        INNER JOIN prd_issue_head_tr h ON h.id = i.prd_issue_head_tr_id
                        WHERE h.issue_type = 'ISSUE'
                        AND h.deleted = 0
                        AND h.status = 'POSTED'
                        AND i.deleted = 0
                        AND i.status = 'POSTED'
                        AND (i.returned_qty = 0 OR i.returned_qty IS NULL)  and  prd_order_head_id=
                        (   SELECT prd_order_head_id
                        FROM prd_issue_item_tr i
                        INNER JOIN prd_issue_head_tr h ON h.id = i.prd_issue_head_tr_id
                        WHERE h.issue_type = 'ISSUE'
                        AND h.deleted = 0
                        AND h.status = 'POSTED'
                        AND i.deleted = 0
                        AND i.status = 'POSTED'
                        AND (i.returned_qty = 0 OR i.returned_qty IS NULL) ORDER by  prd_order_head_id desc  LIMIT 1)
                """
                issue_items = self.db.query(sql)
                issue_item_ids = [{"id": item["id"]} for item in issue_items]
                
                # 从规则明细中获取配置项
                rule_data = self.rule_render_info.get("response", {}).get("data", {}).get("data", {})
                rule_items = self.rule_render_info.get("items", {}).get("data", {}).get("data", {}).get("data", [])
                issue_rule_items = []
                
                # 只保存defaultValue为true的规则项
                for item in rule_items:
                    if item.get("defaultValue"):
                        issue_rule_items.append({
                            "label": item.get("label"),
                            "value": item.get("id"),
                            "item": item.get("item"),
                            "defaultValue": True,
                            "isModified": item.get("isModified", False),
                            "id": item.get("id"),
                            "createdBy": item.get("createdBy"),
                            "updatedBy": item.get("updatedBy"),
                            "createdAt": item.get("createdAt"),
                            "updatedAt": item.get("updatedAt"),
                            "version": item.get("version"),
                            "deleted": item.get("deleted"),
                            "originOrgId": item.get("originOrgId"),
                            "prdIssueRuleCfId": item.get("prdIssueRuleCfId"),
                            "disabled": item.get("disabled", False)
                        })
                
                # 构建创建待提交退料单的请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": issue_item_ids,
                            "issueRule": {
                                "issueRule": rule_data,
                                "issueRuleItems": issue_rule_items
                            }
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="创建待提交退料单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取创建的待提交退料单信息
                response_data = result.get("data", {})
                
                # 确保返回了待提交退料单信息
                assert response_data is not None, "未返回待提交退料单信息"
                
                # 记录验证结果
                a.text(
                    f"领料单行项目ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存创建结果数据"):
                # 保存待提交退料单信息到类变量
                TestPrdOrderIssueReturn.issue_return_info.update({
                    "issue_item_ids": filtered_params['params']['request']['ids'],
                    "issue_info": response_data
                })
                
                self.logger.info(f"待提交退料单创建成功 - 领料单行项目ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}")
                
                # 记录保存的数据
                a.json(TestPrdOrderIssueReturn.issue_return_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"创建待提交退料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrderIssueReturn()
    test.setup_class()
    test.test_get_issue_rule_render_default()  # 获取默认领退料分单规则
    test.test_get_issue_rule_items()           # 获取领退料分单规则项
    test.test_create_issue_return_by_issue()   # 创建待提交退料单 