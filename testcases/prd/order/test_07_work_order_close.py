# -*- coding: utf-8 -*-
"""
生产订单关闭测试用例
包含生产订单关闭的完整业务流程测试，包括订单关联和取消关闭
"""
import allure
import pytest
from testcases.prd import PrdBaseTest
from utils.allure_simple import a
from utils.param_util import ParamUtil


@allure.epic("生产管理")
@allure.feature("生产订单关闭")
class TestWorkOrderClose(PrdBaseTest):
    """生产订单关闭测试用例
    
    本测试用例验证生产订单关闭的完整业务流程，包括：
    1. 查询可关闭的生产订单列表
    2. 执行订单关闭操作
    3. 验证订单状态变更
    4. 执行取消关闭操作
    5. 验证订单恢复状态
    """
    
    # 保存测试过程中的数据
    close_info = {}
    
    def init(self):
        """初始化测试数据"""
        self.logger.info("开始初始化生产订单关闭测试数据")
        pass
    
    @pytest.mark.run(order=1)
    def test_query_closeable_orders(self):
        """查询可关闭的生产订单列表
        
        步骤：
        1. 使用SQL直接查询可关闭的生产订单列表
        2. 保存订单列表信息用于后续测试
        
        验证点：
        - 能成功查询到订单列表
        - 订单状态符合可关闭条件
        - 订单数据结构完整
        """
        try:
            with a.step("查询可关闭的生产订单列表"):
                # 构建SQL查询
                sql = f"""
                    SELECT 
                        p.id,
                        p.wo_code,
                        p.mat_id,
                        p.confirm_status,
                        p.status,
                        p.deleted
                    FROM prd_order_header_tr p
                    WHERE 
                    p.mat_id = {self.base_info["prd_mat_info"]["id"]}
                    AND p.status = 'SUBMITTED'
                    AND p.deleted = 0
                    ORDER BY p.id DESC
                    LIMIT 1
                """
                
                # 执行查询
                records = self.db.query(sql)
                self.logger.info(f"查询到{len(records)}条可关闭的生产订单记录")
                
                # 保存查询结果
                self.close_info["records"] = records
                
                # 验证查询结果
                assert records, "未找到可关闭的生产订单记录"
                
                # 添加报告附件
                a.json(records, "查询结果数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.run(order=2)
    def test_execute_order_close(self):
        """执行生产订单关闭操作
        
        步骤：
        1. 获取关闭前的订单状态
        2. 执行订单关闭操作
        3. 验证关闭后的状态变更
        
        验证点：
        - 接口调用成功
        - 订单状态正确变更为已关闭
        - 相关数据更新正确
        """
        try:
            with a.step("执行生产订单关闭操作"):
                # 获取API配置
                api_path = self.get_api_path("生产订单关闭服务")
                params, url = self.get_api_params(api_path)
                
                # 获取需要关闭的订单ID
                records = self.close_info.get("records", [])
                assert records, "没有找到需要关闭的订单记录"
                
                order_id = records[0]["id"]
                self.logger.info(f"准备关闭生产订单: {order_id}")
                
                # 获取关闭前的订单数据
                pre_close_sql = f"""
                    SELECT 
                        id, wo_code, status, confirm_status, deleted
                    FROM prd_order_header_tr
                    WHERE id = {order_id}
                """
                pre_close_data = self.db.query(pre_close_sql)
                assert pre_close_data, f"未找到订单记录，ID: {order_id}"
                
                # 设置请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": [order_id]
                        }
                    }
                }
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取关闭后的订单数据
                post_close_sql = f"""
                    SELECT 
                        id, wo_code, status, confirm_status, deleted
                    FROM prd_order_header_tr
                    WHERE id = {order_id}
                """
                post_close_data = self.db.query(post_close_sql)
                assert post_close_data, f"未找到订单记录，ID: {order_id}"
                
                # 验证状态变更
                assert post_close_data[0]["status"] == "PRODUCTION_COMPLETED", \
                    f"订单关闭后状态不正确，期望: PRODUCTION_COMPLETED，实际: {post_close_data[0]['status']}"
                
                # 保存关闭后的数据
                self.close_info["close_result"] = {
                    "pre_close": pre_close_data[0],
                    "post_close": post_close_data[0]
                }
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(self.close_info["close_result"], "关闭前后数据对比")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.run(order=3)
    def test_execute_cancel_close(self):
        """执行生产订单取消关闭操作
        
        步骤：
        1. 获取取消关闭前的订单状态
        2. 执行订单取消关闭操作
        3. 验证取消关闭后的状态恢复
        
        验证点：
        - 接口调用成功
        - 订单状态正确恢复为未关闭
        - 相关数据更新正确
        """
        try:
            with a.step("执行生产订单取消关闭操作"):
                # 获取API配置
                api_path = self.get_api_path("生产订单取消关闭服务")
                params, url = self.get_api_params(api_path)
                
                # 获取需要取消关闭的订单ID
                records = self.close_info.get("records", [])
                assert records, "没有找到需要取消关闭的订单记录"
                
                order_id = records[0]["id"]
                self.logger.info(f"准备取消关闭生产订单: {order_id}")
                
                # 获取取消关闭前的订单数据
                pre_cancel_sql = f"""
                    SELECT 
                        id, wo_code, status, confirm_status, deleted
                    FROM prd_order_header_tr
                    WHERE id = {order_id}
                """
                pre_cancel_data = self.db.query(pre_cancel_sql)
                assert pre_cancel_data, f"未找到订单记录，ID: {order_id}"
                
                # 设置请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": [order_id]
                        }
                    }
                }
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取取消关闭后的订单数据
                post_cancel_sql = f"""
                    SELECT 
                        id, wo_code, status, confirm_status, deleted
                    FROM prd_order_header_tr
                    WHERE id = {order_id}
                """
                post_cancel_data = self.db.query(post_cancel_sql)
                assert post_cancel_data, f"未找到订单记录，ID: {order_id}"
                
                # 验证状态恢复
                assert post_cancel_data[0]["status"] == "SUBMITTED", \
                    f"订单取消关闭后状态不正确，期望: SUBMITTED，实际: {post_cancel_data[0]['status']}"
                
                # 保存取消关闭后的数据
                self.close_info["cancel_result"] = {
                    "pre_cancel": pre_cancel_data[0],
                    "post_cancel": post_cancel_data[0]
                }
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(self.close_info["cancel_result"], "取消关闭前后数据对比")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """本地调试入口"""
    test = TestWorkOrderClose()
    test.setup_class()
    test.test_query_closeable_orders()     # 查询可关闭的生产订单列表
    test.test_execute_order_close()        # 执行生产订单关闭操作
    test.test_execute_cancel_close()       # 执行生产订单取消关闭操作 