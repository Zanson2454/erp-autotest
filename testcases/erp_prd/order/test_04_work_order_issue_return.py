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
from testcases.erp_prd import PrdBaseTest
from utils.report_util import a
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

    @pytest.mark.run(order=14)
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

    @pytest.mark.run(order=15)
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
                self.issue_return_info["rule_items"] = records
                
                # 验证查询结果
                assert records, "未找到领料分单规则明细"
                
                # 添加报告附件
                a.json(records, "查询结果数据")
                
        except Exception as e:
            self.logger.error(f"获取领料分单规则明细失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=16)
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
                rule_items = self.issue_return_info.get("rule_items", [])
                
                # 只使用 default_value = 1 的规则明细
                default_rule_items = [item for item in rule_items if item["default_value"] == 1]
                self.logger.info(f"筛选出{len(default_rule_items)}条默认规则明细")
                
                # 构建创建待提交退料单的请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": issue_item_ids,
                            "issueRule": {
                                "issueRule": rule_data,
                                "issueRuleItems": default_rule_items
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

    @pytest.mark.run(order=17)
    @allure.story("提交生产订单退料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送批量提交退料单请求
    3. 验证响应结果
    4. 保存提交结果数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("批量提交生产订单退料单")
    def test_submit_issue_return_orders(self):
        """批量提交生产订单退料单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("领料批量保存服务")
                self.logger.debug(f"提交退料单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 从创建结果中获取待提交的退料单信息
                created_issues = self.issue_return_info.get("issue_info", {}).get("data", [])
                if not created_issues:
                    raise ValueError("未找到待提交的退料单信息")
                
                # 构建提交退料单的请求参数
                filtered_params = {
                    "params": {
                        "request": []
                    }
                }
                
                # 遍历创建的退料单，构建提交请求
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
                result = self.http.post(url, json=filtered_params, description="提交退料单")
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
                    f"退料单提交结果: {json.dumps(response_data, ensure_ascii=False)}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存提交结果数据"):
                # 保存提交结果信息到类变量
                self.issue_return_info.update({
                    "submit_result": response_data
                })
                
                self.logger.info("退料单提交成功")
                
                # 记录保存的数据
                a.json(self.issue_return_info, "保存的测试数据")

        except Exception as e:
            self.logger.error(f"提交退料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=18)
    @allure.story("验证退料相关单据生成")
    @allure.description("""
    ## 测试步骤
    1. 获取退料单号
    2. 验证退料单头表信息
       - 验证退料单状态为POSTED
       - 验证退料单类型为RETURNED
       - 验证删除标记为0
    3. 验证退料单行表信息
       - 验证行项目状态为POSTED
       - 验证实际退料数量与计划数量一致
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("验证退料相关单据(退料单/入库单/移动凭证)生成状态")
    def test_verify_issue_return_related_documents(self):
        """验证退料单、入库单及移动凭证生成状态测试用例"""
        try:
            with a.step("1. 获取退料单号"):
                # 从创建结果中获取退料单编号
                created_issues = self.issue_return_info.get("issue_info", {}).get("data", [])
                if not created_issues:
                    raise ValueError("未找到已创建的退料单信息")
                
                issue_codes = []
                for issue in created_issues:
                    issue_values = issue.get("values", {})
                    issue_code = issue_values.get("issueCode")
                    if issue_code:
                        issue_codes.append(f"'{issue_code}'")
                
                if not issue_codes:
                    raise ValueError("未找到退料单编号")
                
                self.logger.info(f"获取到退料单编号: {','.join(issue_codes)}")
                a.text(f"退料单编号: {','.join(issue_codes)}", "获取的退料单号")

            with a.step("2. 验证退料单头表信息"):
                # 查询退料单头表信息
                max_retries = 10  # 最大重试次数
                retry_interval = 1  # 重试间隔（秒）
                head_results = []
                
                for attempt in range(max_retries):
                    sql = f"""
                        SELECT id, issue_code, issue_type, status, deleted,
                               posting_date, issue_date, issue_doc_type_id
                        FROM prd_issue_head_tr 
                        WHERE issue_code IN ({','.join(issue_codes)})
                        AND deleted = 0
                    """
                    self.logger.debug(f"执行SQL: {sql}")
                    head_results = self.db.query(sql)
                    
                    # 检查所有数据是否都已更新为POSTED状态
                    all_posted = True
                    for head in head_results:
                        if head["status"] != "POSTED":
                            all_posted = False
                            self.logger.info(f"退料单 {head['issue_code']} 状态为 {head['status']}，等待更新...")
                            break
                    
                    if all_posted:
                        self.logger.info(f"所有退料单状态已更新为POSTED，共 {len(head_results)} 条数据")
                        break
                    else:
                        if attempt < max_retries - 1:
                            self.logger.info(f"等待 {retry_interval} 秒后重试...")
                            time.sleep(retry_interval)
                        else:
                            self.logger.warning(f"达到最大重试次数，使用当前状态数据进行验证")
                
                # 验证是否查询到数据
                assert len(head_results) > 0, f"未找到退料单信息: {','.join(issue_codes)}"
                
                # 获取头表ID列表
                head_ids = [str(head['id']) for head in head_results]
                
                # 验证退料单头表数据
                for head in head_results:
                    # 验证状态
                    assert head["status"] == "POSTED", \
                        f"退料单 {head['issue_code']} 状态不正确,期望:POSTED,实际:{head['status']}"
                    # 验证类型
                    assert head["issue_type"] == "RETURNED", \
                        f"退料单 {head['issue_code']} 类型不正确,期望:RETURNED,实际:{head['issue_type']}"     
                    self.logger.info(f"退料单 {head['issue_code']} 头表信息验证通过")
                
                # 保存头表数据供后续验证使用
                self.issue_return_info.update({
                    "head_results": head_results
                })
                
                a.text(f"验证通过 {len(head_results)} 个退料单头表信息", "验证结果")

            with a.step("3. 验证退料单行表信息"):
                # 使用头表查询结果中的ID查询行表信息
                sql = f"""
                    SELECT id, item_code, mat_id,
                           plan_qty, issued_qty, status, deleted,
                           prd_order_head_id, prd_issue_head_tr_id, dn_code
                    FROM prd_issue_item_tr
                    WHERE prd_issue_head_tr_id IN ({','.join(head_ids)})
                    AND deleted = 0
                """
                self.logger.debug(f"执行SQL: {sql}")
                item_results = self.db.query(sql)
                
                # 验证是否有行项目数据
                assert len(item_results) > 0, "未找到退料单行项目数据"
                
                # 验证行项目数据
                for item in item_results:
                    # 验证状态
                    assert item["status"] == "POSTED", \
                        f"退料单 {item['item_code']} 行项目 状态不正确,期望:POSTED,实际:{item['status']}"
                    # 验证数量
                    assert float(item["plan_qty"]) > 0, \
                        f"退料单 {item['item_code']} 行项目 计划退料数量必须大于0"
                    assert float(item["issued_qty"]) == float(item["plan_qty"]), \
                        f"退料单 {item['item_code']} 行项目 实际退料数量与计划数量不相等," \
                        f"实际退料:{item['issued_qty']},计划退料:{item['plan_qty']}"
                    # 验证删除标记
                    assert item["deleted"] == 0, \
                        f"退料单 {item['item_code']} 行项目 已被删除"
                    
                    self.logger.info(f"退料单 {item['item_code']} 行项目 验证通过")
                
                # 保存行表数据供后续验证使用
                if "item_results" not in self.issue_return_info:
                    self.issue_return_info["item_results"] = []
                self.issue_return_info["item_results"].extend(item_results)
                
                total_items = len(self.issue_return_info.get("item_results", []))
                a.text(f"验证通过 {total_items} 个退料单行项目", "验证结果")

            with a.step("4. 验证入库单信息"):
                # 从退料单行项目中获取入库单号
                dn_codes = []
                for item in self.issue_return_info.get("item_results", []):
                    if item.get("dn_code"):
                        dn_codes.append(f"'{item['dn_code']}'")
                
                if not dn_codes:
                    raise ValueError("未找到关联的入库单号")
                
                # 查询入库单头表信息
                max_retries = 10  # 最大重试次数
                retry_interval = 1  # 重试间隔（秒）
                dn_head_results = []
                
                for attempt in range(max_retries):
                    sql = f"""
                        SELECT id, dn_code, deleted, biz_status,
                               posting_date, bt_class
                        FROM del_dn_head_tr 
                        WHERE dn_code IN ({','.join(dn_codes)})
                        AND deleted = 0
                    """
                    self.logger.debug(f"执行SQL: {sql}")
                    dn_head_results = self.db.query(sql)
                    
                    # 检查所有数据是否都已更新为POSTED状态
                    all_posted = True
                    for head in dn_head_results:
                        if head["biz_status"] not in ["POSTED", "SUBMITTED"]:
                            all_posted = False
                            self.logger.info(f"入库单 {head['dn_code']} 状态为 {head['biz_status']}，等待更新...")
                            break
                    
                    if all_posted:
                        self.logger.info(f"所有入库单状态已更新为POSTED或SUBMITTED，共 {len(dn_head_results)} 条数据")
                        break
                    else:
                        if attempt < max_retries - 1:
                            self.logger.info(f"等待 {retry_interval} 秒后重试...")
                            time.sleep(retry_interval)
                        else:
                            self.logger.warning(f"达到最大重试次数，使用当前状态数据进行验证")
                
                # 验证是否查询到数据
                assert len(dn_head_results) > 0, f"未找到入库单信息: {','.join(dn_codes)}"
                
                # 验证入库单头表数据
                for head in dn_head_results:
                    # 验证业务类型
                    assert head["bt_class"] == "PRD_ISSUE_RETURN", \
                        f"入库单 {head['dn_code']} 业务类型不正确,期望:PRD_ISSUE_RETURN,实际:{head['bt_class']}"
                    self.logger.info(f"入库单 {head['dn_code']} 头表信息验证通过")
                
                # 保存头表数据供后续验证使用
                self.issue_return_info.update({
                    "dn_head_results": dn_head_results
                })
                
                a.text(f"验证通过 {len(dn_head_results)} 个入库单头表信息", "验证结果")

            with a.step("5. 验证移动凭证信息"):
                # 遍历入库单数据验证移动凭证
                for item in self.issue_return_info.get("item_results", []):
                    if not item.get("dn_code") or not item.get("mat_id"):
                        continue
                        
                    # 查询移动凭证行项目
                    sql = f"""
                        SELECT id, code, mvm_pos_neg, mvm_qty, doc_id_pre, mat_id,
                               assn_doc_code, deleted, mvm_type_id, source_type, mvm_uom_id
                        FROM inv_mvm_doc_item_tr
                        WHERE doc_id_pre = '{item["dn_code"]}'
                        AND mat_id = {item["mat_id"]}
                        AND deleted = 0
                    """
                    self.logger.debug(f"执行SQL: {sql}")
                    mvm_item_results = self.db.query(sql)
                    
                    # 验证是否生成移动凭证
                    assert len(mvm_item_results) > 0, \
                        f"入库单 {item['dn_code']} 物料ID {item['mat_id']} 未找到对应的移动凭证行"
                    
                    # 验证移动凭证行数据
                    for mvm_item in mvm_item_results:
                        # 验证移动类型（退料入库 4010006）
                        assert mvm_item["mvm_type_id"] == 4010006, \
                            f"移动凭证行 {mvm_item['code']} 移动类型不正确,期望:4010006(退料入库),实际:{mvm_item['mvm_type_id']}"
                        
                        # 验证数量
                        assert float(mvm_item["mvm_qty"]) == float(item["issued_qty"]), \
                            f"移动凭证行 {mvm_item['code']} 移动数量与退料数量不一致," \
                            f"移动数量:{mvm_item['mvm_qty']},退料数量:{item['issued_qty']}"
                            
                        self.logger.info(f"入库单 {item['dn_code']} 物料ID {item['mat_id']} 移动凭证验证通过")
                
                total_mvms = len(self.issue_return_info.get("item_results", []))
                a.text(f"验证通过 {total_mvms} 个移动凭证", "验证结果")

        except Exception as e:
            self.logger.error(f"验证退料相关单据生成失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrderIssueReturn()
    test.setup_class()
    test.test_get_issue_rule_render_default()  # 获取默认领退料分单规则
    test.test_get_issue_rule_items()           # 获取领退料分单规则项
    test.test_create_issue_return_by_issue()   # 创建待提交退料单
    test.test_submit_issue_return_orders()     # 提交退料单
    test.test_verify_issue_return_related_documents()     # 验证退料相关单据生成 