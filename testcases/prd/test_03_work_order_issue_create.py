# -*- coding: utf-8 -*-
"""
生产订单领料单创建测试用例
包含根据生产订单分组创建待提交领料单和提交领料单等操作
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
@allure.feature("生产订单领料")
class TestPrdOrderIssueCreate(PrdBaseTest):
    """生产订单领料单创建测试类"""
    
    # 保存测试过程中的数据
    issue_create_info = {}
    rule_render_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.logger.info("生产订单领料单创建测试类初始化完成")

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
                TestPrdOrderIssueCreate.rule_render_info.update({
                    "response": result
                })
                self.logger.info("默认领料分单规则接口返回数据已保存")
                a.json(TestPrdOrderIssueCreate.rule_render_info, "保存的测试数据")

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
                                            "value": TestPrdOrderIssueCreate.rule_render_info \
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
                TestPrdOrderIssueCreate.rule_render_info.update({
                    "items": result
                })
                self.logger.info("领料分单规则明细接口返回数据已保存")
                a.json(TestPrdOrderIssueCreate.rule_render_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"获取领料分单规则明细失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("创建待提交生产订单领料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送创建待提交领料单请求
    3. 验证响应结果
    4. 保存创建结果数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("根据生产订单BOM清单创建待提交领料单")
    def test_create_issue_by_order_bom_list(self):
        """根据生产订单BOM清单创建待提交领料单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据生产订单BOM行创建领料单服务")
                self.logger.debug(f"创建待提交领料单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 获取最新的BOM项
                latest_bom_items = self.get_prd_order_pending_issue_bom_items()
                bom_item_ids = [{"id": item.get("id")} for item in latest_bom_items]
                
                # 从规则明细中获取配置项
                rule_items = self.rule_render_info.get("items", {}).get("data", {}).get("data", {}).get("data", [])
                issue_rule_items = []
                
                # 只保存defaultValue为true的规则项
                for item in rule_items:
                    if item.get("defaultValue"):
                        issue_rule_items.append({
                            "label": item.get("label"),
                            "value": item.get("value"),
                            "item": item.get("item"),
                            "defaultValue": True,
                            "isModified": item.get("isModified", False),
                            "disabled": item.get("disabled", False)
                        })
                
                # 构建创建待提交领料单的请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": bom_item_ids,
                            "issueRule": {
                                "issueRuleItems": issue_rule_items,
                                "issueRule": {
                                    "code": "aaa",
                                    "name": "默认分单规则",
                                    "defaultValue": True
                                }
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
                result = self.http.post(url, json=filtered_params, description="创建待提交领料单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取创建的待提交领料单信息
                response_data = result.get("data", {})
                
                # 确保返回了待提交领料单信息
                assert response_data is not None, "未返回待提交领料单信息"
                
                # 记录验证结果
                a.text(
                    f"生产订单BOM项ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存创建结果数据"):
                # 保存待提交领料单信息到类变量
                TestPrdOrderIssueCreate.issue_create_info.update({
                    "bom_item_ids": filtered_params['params']['request']['ids'],
                    "issue_info": response_data
                })
                
                self.logger.info(f"待提交领料单创建成功 - BOM项ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}")
                
                # 记录保存的数据
                a.json(TestPrdOrderIssueCreate.issue_create_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"创建待提交领料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("提交生产订单领料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送提交领料单请求
    3. 验证响应结果
    4. 保存提交结果数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("批量提交生产订单领料单")
    def test_submit_issue_orders(self):
        """批量提交生产订单领料单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("领料批量保存服务")
                self.logger.debug(f"提交领料单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 从创建结果中获取待提交的领料单信息
                created_issues = self.issue_create_info.get("issue_info", {}).get("data", [])
                if not created_issues:
                    raise ValueError("未找到待提交的领料单信息")
                
                # 构建提交领料单的请求参数
                filtered_params = {
                    "params": {
                        "request": []
                    }
                }
                
                # 遍历创建的领料单，构建提交请求
                for issue in created_issues:
                    issue_values = issue.get("values", {})
                    submit_issue = {
                        "issueCode": issue_values.get("issueCode"),
                        "issueDocTypeId": issue_values.get("issueDocTypeId"),
                        "issueType": issue_values.get("issueType"),
                        "issueDate": issue_values.get("issueDate"),
                        "postingDate": int(time.time() * 1000),  # 当前时间戳（毫秒级）
                        "issueItemList": issue_values.get("issueItemList", [])
                    }
                    filtered_params["params"]["request"].append(submit_issue)
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="提交领料单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取提交结果信息
                response_data = result.get("data", {})
                
                # 确保返回了提交结果信息
                assert response_data is not None, "未返回提交结果信息"
                
                # 记录验证结果
                a.text(
                    f"领料单提交结果: {json.dumps(response_data, ensure_ascii=False)}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存提交结果数据"):
                # 保存提交结果信息到类变量
                self.issue_create_info.update({
                    "submit_result": response_data
                })
                
                self.logger.info(f"领料单提交成功")
                
                # 记录保存的数据
                a.json(self.issue_create_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"提交领料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @allure.story("验证生产领料业务单据")
    @allure.description("""
    ## 测试步骤
    1. 准备请求参数
    2. 发送查询请求
    3. 验证领料单数据
    4. 验证交货入库单数据
    5. 验证移动凭证数据
    
    ## 验证内容
    1. 领料单验证：
       - 验证领料单状态为POSTED
       - 验证实际领料数量与计划数量一致
       - 验证关联信息完整性
       
    2. 交货入库单验证：
       - 验证入库单生成并过账(POSTED)
       - 验证入库数量与领料数量一致
       - 验证来源单据信息完整性
       
    3. 移动凭证验证：
       - 验证移动凭证生成
       - 验证移动数量与交货数量一致
       - 验证移动类型和来源信息
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("验证生产领料相关单据生成状态")
    def test_verify_issue_related_documents(self):
        """验证生产领料单、交货入库单及移动凭证生成状态测试用例"""
        try:
            with a.step("1. 准备请求参数"):
                # 获取API路径
                api_path = self.get_api_path("分页查询生产领料单") + \
                          "?tmodule=ERP_PRD"
                self.logger.debug(f"查询生产订单领料行项目API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 从之前的测试数据中获取生产订单编号
                created_issues = self.issue_create_info.get("issue_info", {}).get("data", [])
                if not created_issues:
                    raise ValueError("未找到已创建的领料单信息")
                
                # 获取第一个领料单的生产订单ID
                first_issue = created_issues[0]
                prd_order_id = first_issue.get("values", {}).get("issueItemList", [])[0].get("prdOrderHeadId", {}).get("id")
                if not prd_order_id:
                    raise ValueError("未找到生产订单ID")

                # 根据生产订单ID查询生产订单编号
                sql = f"""
                    SELECT wo_code
                    FROM prd_order_header_tr
                    WHERE id = {prd_order_id}
                    AND deleted = 0
                """
                result = self.db.query(sql)
                if not result:
                    raise ValueError(f"未找到生产订单信息: {prd_order_id}")
                
                prd_order_code = result[0]["wo_code"]
                self.logger.info(f"获取到生产订单编号: {prd_order_code}")
                
                # 构建查询参数
                filtered_params = {
                    "params": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "conditionGroup": {
                                "type": "ConditionGroup",
                                "logicOperator": "AND",
                                "conditions": [{
                                    "type": "ConditionGroup",
                                    "logicOperator": "AND",
                                    "conditions": [{
                                        "type": "ConditionGroup",
                                        "logicOperator": "AND",
                                        "conditions": [{
                                            "key": "E7xyvAmg29xtoBatpO7A-",
                                            "type": "ConditionLeaf",
                                            "leftValue": {
                                                "id": "3KOJzHxH69EzLe9gpKpXR",
                                                "key": "3KOJzHxH69EzLe9gpKpXR",
                                                "type": "VarValue",
                                                "fieldType": "Text",
                                                "valueType": "VAR",
                                                "varValue": [{
                                                    "valueKey": "prdOrderHeadId.woCode",
                                                    "valueName": "prdOrderHeadId.woCode"
                                                }]
                                            },
                                            "operator": "CONTAINS",
                                            "rightValue": {
                                                "key": "SHkkpuRb6QJiMy0H4W53Y",
                                                "type": "VarValue",
                                                "fieldType": "Text",
                                                "valueType": "CONST",
                                                "constValue": prd_order_code
                                            }
                                        }]
                                    }]
                                }]
                            }
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                result = self.http.post(url, json=filtered_params, description="查询生产订单领料行项目")
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取响应数据
                response_data = result.get("data", {})
                assert response_data is not None, "响应数据为空"
                
                # 验证分页数据结构
                page_data = response_data.get("data", {})
                assert isinstance(page_data, dict), "分页数据结构不正确"
                assert "total" in page_data, "分页数据缺少total字段"
                assert "data" in page_data, "分页数据缺少data字段"
                
                # 验证查询结果不为空
                data_list = page_data.get("data", [])
                assert len(data_list) > 0, "查询结果为空"
                
                a.text(f"查询到 {len(data_list)} 条领料行项目数据", "验证结果")
            
            with a.step("4. 验证领料单数据"):
                # 定义必要字段列表
                required_fields = [
                    "id", "prdOrderHeadId", "matId", "planQty", 
                    "issuedQty", "status", "dnCode"
                ]
                
                # 验证每一条数据
                for index, item in enumerate(data_list, 1):
                    self.logger.info(f"正在验证第 {index} 条数据")
                    
                    # 验证必要字段存在
                    for field in required_fields:
                        assert field in item, f"第 {index} 条数据缺少必要字段: {field}"
                    
                    # 验证领料单状态
                    assert item["status"] == "POSTED", f"第 {index} 条数据状态不正确,期望:POSTED,实际:{item['status']}"
                    
                    # 验证数量
                    assert float(item["planQty"]) > 0, f"第 {index} 条数据计划数量必须大于0"
                    assert float(item["issuedQty"]) == float(item["planQty"]), \
                        f"第 {index} 条数据实际领料数量与计划数量不相等,实际领料:{item['issuedQty']},计划领料:{item['planQty']}"
                    
                    # 验证关联数据
                    assert item["prdOrderHeadId"] is not None, f"第 {index} 条数据缺少生产订单关联"
                    assert item["matId"] is not None, f"第 {index} 条数据缺少物料关联"
                    assert item["dnCode"] is not None and item["dnCode"].strip() != "", f"第 {index} 条数据的交货单号为空"

            with a.step("5. 验证交货入库单数据"):
                # 验证入库单生成并过账(POSTED)
                for item in data_list:
                    sql = f"""
                        SELECT id, biz_status
                        FROM del_dn_head_tr 
                        WHERE dn_code = '{item["dnCode"]}'
                        AND bt_class = 'PRD_ISSUE'
                        AND deleted = 0
                    """
                    delivery_head_result = self.db.query(sql)
                    assert len(delivery_head_result) > 0, f"未找到交货入库单: {item['dnCode']}"
                    delivery_head = delivery_head_result[0]
                    assert delivery_head["biz_status"] == "POSTED", \
                        f"交货入库单 {item['dnCode']} 状态不正确,期望:POSTED,实际:{delivery_head['biz_status']}"

                    # 验证入库数量与领料数量一致
                    sql = f"""
                        SELECT id, dn_code, mat_code, doc_code, plan_del_qty, real_del_qty, 
                               biz_status, bt_class, deleted, dn_item_code, doc_item_code
                        FROM del_dn_item_tr
                        WHERE dn_code = '{item["dnCode"]}'
                        AND bt_class = 'PRD_ISSUE'
                        AND deleted = 0
                    """
                    delivery_item_results = self.db.query(sql)
                    assert len(delivery_item_results) > 0, f"交货入库单 {item['dnCode']} 没有行项目数据"

                    # 验证每个交货入库单行项目
                    for delivery_item in delivery_item_results:
                        # 验证基本状态
                        assert delivery_item["biz_status"] == "POSTED", \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 状态不正确,期望:POSTED,实际:{delivery_item['biz_status']}"
                        assert delivery_item["bt_class"] == "PRD_ISSUE", \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 业务类型不正确,期望:PRD_ISSUE,实际:{delivery_item['bt_class']}"
                        
                        # 验证数量
                        assert float(delivery_item["plan_del_qty"]) > 0, \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 计划交货数量必须大于0"
                        assert float(delivery_item["real_del_qty"]) == float(delivery_item["plan_del_qty"]), \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 实际交货数量与计划数量不相等," \
                            f"实际交货:{delivery_item['real_del_qty']},计划交货:{delivery_item['plan_del_qty']}"
                        
                        # 验证关联信息
                        assert delivery_item["mat_code"] is not None and delivery_item["mat_code"].strip() != "", \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 物料编码为空"
                        assert delivery_item["doc_code"] is not None and delivery_item["doc_code"].strip() != "", \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 来源单据编号为空"
                        assert delivery_item["doc_item_code"] is not None and delivery_item["doc_item_code"].strip() != "", \
                            f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 来源单据行号为空"
                        
                        # 先查询物料ID
                        sql = f"""
                            SELECT id
                            FROM gen_mat_md
                            WHERE mat_code = '{delivery_item["mat_code"]}'
                            AND deleted = 0
                        """
                        mat_result = self.db.query(sql)
                        assert len(mat_result) > 0, \
                            f"未找到物料编码 {delivery_item['mat_code']} 对应的物料ID"
                        mat_id = mat_result[0]["id"]

            with a.step("6. 验证移动凭证数据"):
                # 验证移动凭证生成
                for item in data_list:
                    # 验证移动凭证行项目
                    sql = f"""
                        SELECT id, code, mvm_pos_neg, mvm_qty, doc_id_pre, mat_id,
                               assn_doc_code, deleted, mvm_type_id, source_type, mvm_uom_id
                        FROM inv_mvm_doc_item_tr
                        WHERE doc_id_pre = '{item["dnCode"]}'
                        AND mat_id = {mat_id}
                        AND deleted = 0
                    """
                    mvm_item_results = self.db.query(sql)
                    assert len(mvm_item_results) > 0, \
                        f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 未找到对应的移动凭证行"

                    # 验证移动凭证行
                    for mvm_item in mvm_item_results:
                        # 验证数量
                        assert float(mvm_item["mvm_qty"]) == float(delivery_item["real_del_qty"]), \
                            f"移动凭证行 {mvm_item['code']} 移动数量与交货数量不一致," \
                            f"移动数量:{mvm_item['mvm_qty']},交货数量:{delivery_item['real_del_qty']}"

                self.logger.info(f"已完成全部 {len(data_list)} 条数据的验证")
                a.text(f"全部 {len(data_list)} 条数据验证通过", "验证结果")
        
        except Exception as e:
            self.logger.error(f"验证生产领料相关单据生成状态失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrderIssueCreate()
    test.setup_class()
    test.test_get_issue_rule_render_default()     # 获取默认领料分单规则
    test.test_get_issue_rule_items()              # 获取领料分单规则明细
    test.test_create_issue_by_order_bom_list()    # 创建待提交生产订单领料单
    test.test_submit_issue_orders()               # 提交生产订单领料单
    test.test_verify_issue_related_documents()    # 验证生产领料相关单据生成 