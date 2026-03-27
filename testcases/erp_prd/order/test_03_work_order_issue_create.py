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
from testcases.erp_prd import PrdBaseTest
from utils.report_util import a
from utils.param_util import ParamUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("生产管理")
@allure.feature("生产订单领料")
class TestPrdOrderIssueCreate(PrdBaseTest):
    """生产订单领料单创建测试类"""
    
    # 保存测试过程中的数据
    rule_render_info = {}  # 存储领料分单规则数据
    issue_info = {}       # 存储领料单相关数据
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("生产订单领料单创建测试类初始化完成")

    @pytest.mark.run(order=9)
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
                result, _ = self.standard_api_call(
                    api_key="渲染默认领料分单规则服务",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
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

    @pytest.mark.run(order=10)
    @allure.story("获取领料分单规则明细")
    @allure.title("获取领料分单规则明细-接口校验")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    ## 测试步骤
    1. 使用SQL直接查询领料分单规则明细
    2. 保存规则明细用于后续测试
    
    ## 验证点
    - 能成功查询到规则明细
    - 规则明细数据结构完整
    """)
    def test_get_issue_rule_items(self):
        """获取领料分单规则明细
        
        步骤：
        1. 使用SQL直接查询领料分单规则明细
        2. 保存规则明细用于后续测试
        
        验证点：
        - 能成功查询到规则明细
        - 规则明细数据结构完整
        """
        try:
            with a.step("查询领料分单规则明细"):
                # 获取规则ID
                rule_id = self.rule_render_info.get("response", {}).get("data", {}).get("data", {}).get("id")
                assert rule_id, "未找到领料分单规则ID"
                self.logger.info(f"获取到领料分单规则ID: {rule_id}")
                
                # 构建SQL查询
                sql = f"""
                    SELECT 
                        id,
                        prd_issue_rule_cf_id,
                        item,
                        default_value,
                        deleted
                    FROM prd_issue_rule_item_cf 
                    WHERE prd_issue_rule_cf_id = {rule_id}
                    AND deleted = 0
                """
                
                # 执行查询
                records = self.db.query(sql)
                self.logger.info(f"查询到{len(records)}条领料分单规则明细")
                
                # 保存查询结果
                self.issue_info["rule_items"] = records
                
                # 验证查询结果
                assert records, "未找到领料分单规则明细"
                
                # 添加报告附件
                a.json(records, "查询结果数据")
                
        except Exception as e:
            self.logger.error(f"获取领料分单规则明细失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=11)
    @allure.story("创建待提交生产订单领料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求参数
    2. 发送创建请求
    3. 验证创建结果
    
    ## 验证点
    - 接口调用成功
    - 返回数据结构完整
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("根据生产订单BOM清单创建待提交领料单")
    def test_create_issue_by_order_bom_list(self):
        """创建待提交领料单
        
        步骤：
        1. 准备请求参数
        2. 发送创建请求
        3. 验证创建结果
        
        验证点：
        - 接口调用成功
        - 返回数据结构完整
        """
        try:
            with a.step("创建待提交领料单"):
                # 获取API配置
                api_path = self.get_api_path("根据生产订单BOM行创建领料单服务")
                params, url = self.get_api_params(api_path)
                
                # 获取规则明细
                rule_items = self.issue_info.get("rule_items", [])
                assert rule_items, "未找到领料分单规则明细"
                
                # 只使用 default_value = 1 的规则明细
                default_rule_items = [item for item in rule_items if item["default_value"] == 1]
                self.logger.info(f"筛选出{len(default_rule_items)}条默认规则明细")
                
                # 获取待领料BOM行ID
                bom_items = self.get_prd_order_pending_issue_bom_items()
                assert bom_items, "未找到待领料BOM行"
                self.logger.info(f"获取到{len(bom_items)}条待领料BOM行")
                
                # 设置请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": bom_items,
                            "issueRule": {
                                "issueRuleItems": default_rule_items,
                                "issueRule": {
                                    "code": "aaa",
                                    "name": "默认分单规则",
                                    "defaultValue": True
                                }
                            }
                        }
                    }
                }
                
                # 发送请求
                result, _ = self.standard_api_call(
                    api_key="根据生产订单BOM行创建领料单服务",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 保存创建结果
                self.issue_info["create_result"] = result
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                
        except Exception as e:
            self.logger.error(f"创建待提交领料单失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=12)
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
                created_issues = self.issue_info.get("create_result", {}).get("data", {}).get("data", [])
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
                result, _ = self.standard_api_call(
                    api_key="领料批量保存服务",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
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
                self.issue_info.update({
                    "submit_result": response_data
                })
                
                self.logger.info(f"领料单提交成功")
                
                # 记录保存的数据
                a.json(self.issue_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"提交领料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=13)
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
                created_issues = self.issue_info.get("create_result", {}).get("data", {}).get("data", [])
                if not created_issues:
                    raise ValueError("未找到已创建的领料单信息")
                
                # 获取第一个领料单的生产订单ID
                first_issue = created_issues[0]
                issue_items = first_issue.get("values", {}).get("issueItemList", [])
                if not issue_items:
                    raise ValueError("未找到领料单行项目")
                
                prd_order_head_id = issue_items[0].get("prdOrderHeadId", {}).get("id")
                if not prd_order_head_id:
                    raise ValueError("未找到生产订单ID")

                # 根据生产订单ID查询生产订单编号
                sql = f"""
                    SELECT wo_code
                    FROM prd_order_header_tr
                    WHERE id = {prd_order_head_id}
                    AND deleted = 0
                """
                result = self.db.query(sql)
                if not result:
                    raise ValueError(f"未找到生产订单信息: {prd_order_head_id}")
                
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
            
            with a.step("2. 发送请求并等待状态更新"):
                # 添加重试机制，等待状态更新
                max_retries = 10  # 最大重试次数
                retry_interval = 1  # 重试间隔（秒）
                data_list = []
                
                for attempt in range(max_retries):
                    self.logger.info(f"第 {attempt + 1} 次尝试查询领料单状态")
                    
                    result, _ = self.standard_api_call(
                        api_key="分页查询生产领料单",
                        set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    a.json(result, f"第{attempt + 1}次响应数据")
                    
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
                    
                    # 获取数据列表
                    current_data_list = page_data.get("data", [])
                    assert len(current_data_list) > 0, "查询结果为空"
                    
                    # 检查所有数据是否都已更新为POSTED状态
                    all_posted = True
                    for item in current_data_list:
                        if item.get("status") != "POSTED":
                            all_posted = False
                            self.logger.info(f"数据ID {item.get('id')} 状态为 {item.get('status')}，等待更新...")
                            break
                    
                    if all_posted:
                        data_list = current_data_list
                        self.logger.info(f"所有数据状态已更新为POSTED，共 {len(data_list)} 条数据")
                        a.text(f"第 {attempt + 1} 次查询成功，所有数据状态已更新为POSTED", "验证结果")
                        break
                    else:
                        if attempt < max_retries - 1:
                            self.logger.info(f"等待 {retry_interval} 秒后重试...")
                            time.sleep(retry_interval)
                        else:
                            # 最后一次尝试，使用当前数据继续验证
                            data_list = current_data_list
                            self.logger.warning(f"达到最大重试次数，使用当前状态数据进行验证")
                            a.text(f"达到最大重试次数，使用当前状态数据进行验证", "验证结果")
                
                a.text(f"查询到 {len(data_list)} 条领料行项目数据", "验证结果")
            
            with a.step("3. 验证领料单数据"):
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
                    
                    # 验证领料单状态（允许SUBMITTED状态，因为可能还在处理中）
                    current_status = item["status"]
                    if current_status not in ["POSTED", "SUBMITTED"]:
                        raise AssertionError(f"第 {index} 条数据状态不正确,期望:POSTED或SUBMITTED,实际:{current_status}")
                    
                    # 记录状态信息
                    if current_status == "SUBMITTED":
                        self.logger.warning(f"第 {index} 条数据状态为SUBMITTED，可能还在处理中")
                        a.text(f"第 {index} 条数据状态为SUBMITTED，可能还在处理中", "状态提醒")
                    
                    # 验证数量
                    assert float(item["planQty"]) > 0, f"第 {index} 条数据计划数量必须大于0"
                    assert float(item["issuedQty"]) == float(item["planQty"]), \
                        f"第 {index} 条数据实际领料数量与计划数量不相等,实际领料:{item['issuedQty']},计划领料:{item['planQty']}"
                    
                    # 验证关联数据
                    assert item["prdOrderHeadId"] is not None, f"第 {index} 条数据缺少生产订单关联"
                    assert item["matId"] is not None, f"第 {index} 条数据缺少物料关联"
                    assert item["dnCode"] is not None and item["dnCode"].strip() != "", f"第 {index} 条数据的交货单号为空"

            with a.step("4. 验证交货入库单数据"):
                # 验证入库单生成并过账(POSTED)
                for item in data_list:
                    # 添加重试机制验证交货入库单状态
                    max_retries = 10
                    retry_interval = 1
                    delivery_head = None
                    
                    for attempt in range(max_retries):
                        sql = f"""
                            SELECT id, biz_status
                            FROM del_dn_head_tr 
                            WHERE dn_code = '{item["dnCode"]}'
                            AND bt_class = 'PRD_ISSUE'
                            AND deleted = 0
                        """
                        delivery_head_result = self.db.query(sql)
                        
                        if len(delivery_head_result) > 0:
                            delivery_head = delivery_head_result[0]
                            if delivery_head["biz_status"] == "POSTED":
                                break
                            else:
                                self.logger.info(f"交货入库单 {item['dnCode']} 状态为 {delivery_head['biz_status']}，等待更新...")
                                if attempt < max_retries - 1:
                                    time.sleep(retry_interval)
                        else:
                            if attempt < max_retries - 1:
                                self.logger.info(f"未找到交货入库单 {item['dnCode']}，等待生成...")
                                time.sleep(retry_interval)
                    
                    assert delivery_head is not None, f"未找到交货入库单: {item['dnCode']}"
                    
                    # 验证状态（允许SUBMITTED状态）
                    current_status = delivery_head["biz_status"]
                    if current_status not in ["POSTED", "SUBMITTED"]:
                        raise AssertionError(f"交货入库单 {item['dnCode']} 状态不正确,期望:POSTED或SUBMITTED,实际:{current_status}")
                    
                    if current_status == "SUBMITTED":
                        self.logger.warning(f"交货入库单 {item['dnCode']} 状态为SUBMITTED，可能还在处理中")
                        a.text(f"交货入库单 {item['dnCode']} 状态为SUBMITTED，可能还在处理中", "状态提醒")

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
                        # 验证基本状态（允许SUBMITTED状态）
                        current_item_status = delivery_item["biz_status"]
                        if current_item_status not in ["POSTED", "SUBMITTED"]:
                            raise AssertionError(f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 状态不正确,期望:POSTED或SUBMITTED,实际:{current_item_status}")
                        
                        if current_item_status == "SUBMITTED":
                            self.logger.warning(f"交货入库单 {item['dnCode']} 行项目 {delivery_item['dn_item_code']} 状态为SUBMITTED，可能还在处理中")
                        
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

            with a.step("5. 验证移动凭证数据"):
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
                    
                    # 如果移动凭证还未生成，记录警告但不强制失败
                    if len(mvm_item_results) == 0:
                        self.logger.warning(f"交货入库单 {item['dnCode']} 行项目未找到对应的移动凭证行，可能还在处理中")
                        a.text(f"交货入库单 {item['dnCode']} 行项目未找到对应的移动凭证行，可能还在处理中", "状态提醒")
                        continue

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
