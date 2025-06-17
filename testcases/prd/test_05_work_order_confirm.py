# -*- coding: utf-8 -*-
import allure
import pytest
from testcases.prd import PrdBaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a


@allure.epic("生产管理")
@allure.feature("工序报工")
class TestWorkOrderConfirm(PrdBaseTest):
    """工序报工测试用例
    
    本测试用例验证工序报工的完整业务流程，包括：
    1. 查询工序报工列表
    2. 批量确认工序
    3. 批量报工确认
    4. 查询送货单状态验证
    
    业务规则：
    - 入库工序：生成送货单，需要手工过账(WAIT_POST)
    - 物料消耗工序：生成送货单，自动过账(POSTED)
    - 普通工序：不生成送货单
    """
    
    # 保存测试过程中的数据
    confirm_info = {}
    
    def init(self):
        """初始化测试数据
        
        获取最新的已提交状态的生产订单信息，用于后续的工序报工测试。
        订单必须是SUBMITTED状态才能进行工序报工。
        """
        self.logger.info("开始初始化工序报工测试数据")
        
        # 获取最新的生产订单信息
        order_info = self.get_latest_prd_order(status="SUBMITTED")
        print(f"order_info: {order_info}")
        # 检查生产订单状态
        assert order_info["status"] == "SUBMITTED", f"生产订单状态不是已提交状态，当前状态: {order_info['status']}"
        
        # 保存生产订单信息
        self.confirm_info.update(order_info)
        self.logger.info(f"获取到生产订单ID: {self.confirm_info['id']}, 编号: {self.confirm_info['wo_code']}, 状态: {self.confirm_info['status']}")
    
    @pytest.mark.run(order=1)
    def test_query_confirm_list(self):
        """查询工序报工列表
        
        步骤：
        1. 初始化测试数据，获取生产订单信息
        2. 根据生产订单编号查询待报工的工序列表
        3. 保存工序列表信息用于后续测试
        
        验证点：
        - 能成功查询到工序列表
        - 工序数据结构完整
        """
        try:
            # 初始化测试数据
            self.init()
            
            with a.step(f"查询工序报工列表-{self.confirm_info['wo_code']}"):
                # 获取API配置
                api_path = self.get_api_path("报工确认页面列表查询")
                params, url = self.get_api_params(api_path)
                
                # 设置查询参数
                filtered_params = {
                    "params": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "needTotal": True,
                            "conditionGroup": {
                                "type": "ConditionGroup",
                                "logicOperator": "AND",
                                "conditions": [
                                    {
                                        "type": "ConditionGroup",
                                        "logicOperator": "AND",
                                        "conditions": [
                                            {
                                                "type": "ConditionGroup",
                                                "logicOperator": "AND",
                                                "conditions": [
                                                    {
                                                        "key": "UoBp_c0Ul9_29TYf5Q55k",
                                                        "type": "ConditionLeaf",
                                                        "leftValue": {
                                                            "id": "eD8vABnsVeoXzeXZdfSIq",
                                                            "key": "eD8vABnsVeoXzeXZdfSIq",
                                                            "type": "VarValue",
                                                            "fieldType": "Text",
                                                            "valueType": "VAR",
                                                            "varValue": [
                                                                {
                                                                    "valueKey": "prdOrderHeaderTrId.woCode",
                                                                    "valueName": "prdOrderHeaderTrId.woCode"
                                                                }
                                                            ]
                                                        },
                                                        "operator": "CONTAINS",
                                                        "rightValue": {
                                                            "key": "MPVu67KXO025vw9_vYcmv",
                                                            "type": "VarValue",
                                                            "fieldType": "Text",
                                                            "valueType": "CONST",
                                                            "constValue": self.confirm_info["wo_code"]
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                print(f"hfhsdhfhdsfhdshfresult: {result}")
                # 验证响应
                self.assert_util.assert_response_success(result)
                
                # 保存数据
                self.confirm_info.update({
                    "total": result.get("data", {}).get("data", {}).get("total", 0),
                    "records": result.get("data", {}).get("data", {}).get("data", [])
                })
                
                # 打印工序ID列表用于调试
                routing_ids = [{"id": routing["id"]} for routing in self.confirm_info["records"]]
                self.logger.info(f"提取的工序ID列表: {routing_ids}")
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(self.confirm_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    def test_batch_confirm_routings(self):
        """批量确认工序
        
        步骤：
        1. 使用上一步获取的工序ID列表进行批量确认
        2. 获取每个工序的报工单号和相关信息
        
        验证点：
        - 每个工序都生成唯一的报工单号
        - 报工数据包含必要的字段（工序ID、物料、数量等）
        """
        try:
            with a.step(f"批量确认工序-{self.confirm_info['wo_code']}"):
                # 获取API配置
                api_path = self.get_api_path("报工确认-批量-页面渲染服务")
                params, url = self.get_api_params(api_path)
                
                # 从工序列表中获取工序ID
                routing_ids = [{"id": routing["id"]} for routing in self.confirm_info["records"]]
                self.logger.info(f"批量确认的工序ID列表: {routing_ids}")
                
                # 设置请求参数
                filtered_params = {
                    "params": {
                        "request": routing_ids
                    }
                }
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                # 验证响应
                self.assert_util.assert_response_success(result)
                
                # 保存批量确认结果
                self.confirm_info["confirm_result"] = result.get("data", {})
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    def test_delivery_confirm_batch(self):
        """批量报工确认
        
        步骤：
        1. 使用批量确认的结果进行报工确认
        2. 根据工序类型生成送货单
        
        验证点：
        - 入库工序生成送货单且需要手工过账
        - 物料消耗工序生成送货单且自动过账
        - 普通工序不生成送货单
        - 所有报工确认都成功，无失败原因
        """
        try:
            with a.step(f"批量报工确认-{self.confirm_info['wo_code']}"):
                # 获取API配置
                api_path = self.get_api_path("订单确认单-批量过账服务")
                params, url = self.get_api_params(api_path)
                
                # 遍历工序记录构造报工单
                request_list = []
                
                # 获取批量确认的结果数据
                confirm_data_list = self.confirm_info.get("confirm_result", {}).get("data", [])
                
                for confirm_data in confirm_data_list:
                    values = confirm_data.get("values", {})
                    # 直接使用values中的字段构造请求参数
                    request_data = {
                        "confirmCode": values.get("confirmCode"),  # 报工单号
                        "woId": values.get("woId"),  # 工单ID
                        "matId": values.get("matId"),  # 物料ID
                        "invOrgId": values.get("invOrgId"),  # 库存组织
                        "operationId": values.get("operationId"),  # 工序ID
                        "yieldQty": values.get("yieldQty"),  # 产量
                        "scrappedQty": values.get("scrappedQty", 0),  # 报废量
                        "operationUomId": values.get("operationUomId"),  # 单位
                        "prdOrderConfirmActivityItemMd": values.get("prdOrderConfirmActivityItemMd", []),
                        "docDate": values.get("docDate"),  # 单据日期
                        "itemList": values.get("itemList", [])  # 物料消耗列表
                    }
                    
                    # 如果是入库工序，添加入库相关信息
                    if values.get("movTypeId"):
                        request_data.update({
                            "movAssignCfId": values.get("movAssignCfId"),
                            "movTypeId": values.get("movTypeId"),
                            "qty": values.get("qty"),
                            "uomId": values.get("uomId"),
                            "invLocId": values.get("invLocId"),
                            "postInvTypeId": values.get("postInvTypeId")
                        })
                    
                    request_list.append(request_data)
                
                # 设置请求参数
                filtered_params = {
                    "sceneKey": "ERP_PRD$PRD_CONFIRM_VIEW",
                    "viewKey": "ERP_PRD$PRD_CONFIRM_VIEW:RS7T_DQ7LY1O8JCNDwtds",
                    "teamId": 22,
                    "serviceKey": "ERP_PRD$PRD_ORDER_DELIVERY_CONFIRM_BATCH_EVENT_SERVICE",
                    "params": {
                        "request": request_list
                    }
                }
                
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                # 验证响应
                self.assert_util.assert_response_success(result)
                
                # 保存确认结果和dnCode信息
                confirm_result = result.get("data", {})
                self.confirm_info["confirm_result"] = confirm_result
                
                # 提取dnCode用于后续查询
                dn_codes = []
                confirm_data = confirm_result.get("data", [])
                for confirm, request in zip(confirm_data, request_list):
                    dn_code = confirm.get("dnCode", "")
                    if dn_code:
                        dn_info = {
                            "dnCode": dn_code,
                            "confirmCode": confirm.get("confirmCode"),
                            "isInboundOperation": bool(request.get("movTypeId")),  # 是否入库工序
                            "hasMaterialConsumption": bool(request.get("itemList"))  # 是否有物料消耗
                        }
                        dn_codes.append(dn_info)
                
                self.confirm_info["dn_codes"] = dn_codes
                self.logger.info(f"生成的送货单信息: {dn_codes}")
                
                # 验证每个工序的报工结果
                assert len(confirm_data) == len(request_list), "报工确认数量与请求不符"
                
                for confirm, request in zip(confirm_data, request_list):
                    # 验证failReason为空
                    assert confirm.get("failReason") == "", f"报工单{confirm.get('confirmCode')}报工失败: {confirm.get('failReason')}"
                    
                    # 如果是入库工序或有物料消耗，验证dnCode不为空
                    if request.get("movTypeId") or request.get("itemList"):
                        assert confirm.get("dnCode", ""), f"报工单{confirm.get('confirmCode')}未生成送货单号"
                
                # 添加报告附件
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(self.confirm_info["confirm_result"], "确认结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    def test_query_dn_status(self):
        """查询送货单状态验证过账情况
        
        步骤：
        1. 查询送货单头表和行表数据
        2. 验证送货单状态和过账情况
        
        验证点：
        - 入库工序送货单：
          * 单据状态=INEFFECT
          * 业务状态=WAIT_POST（等待手工过账）
          * 业务类型=PRD_CONFIRM
        
        - 物料消耗送货单：
          * 单据状态=INEFFECT
          * 业务状态=POSTED（已自动过账）
          * 业务类型=PRD_CONFIRM
          * 行项目数据完整且数量正确
        """
        try:
            with a.step(f"查询送货单状态-{self.confirm_info['wo_code']}"):
                # 验证是否有送货单需要查询
                dn_codes = self.confirm_info.get("dn_codes", [])
                assert dn_codes, "没有找到需要查询的送货单"
                
                dn_status_results = []
                
                for dn_info in dn_codes:
                    dn_code = dn_info["dnCode"]
                    
                    # 查询送货单头表信息
                    head_sql = f"""
                        SELECT 
                            id,
                            dn_code,
                            del_status,
                            biz_status,
                            bt_class,
                            del_class,
                            doc_code,
                            deleted
                        FROM del_dn_head_tr 
                        WHERE dn_code = '{dn_code}' 
                        AND deleted = 0
                    """
                    
                    self.logger.info(f"查询送货单头表SQL: {head_sql}")
                    head_results = self.db.query(head_sql)
                    
                    if not head_results:
                        raise AssertionError(f"未找到送货单{dn_code}的头表记录")
                    
                    head_record = head_results[0]
                    del_status = head_record.get("del_status", "")
                    biz_status = head_record.get("biz_status", "")
                    bt_class = head_record.get("bt_class", "")
                    
                    # 查询送货单行表信息（根据新字段结构）
                    item_sql = f"""
                        SELECT 
                            id,
                            dn_id,
                            mat_id,
                            plan_del_qty,
                            real_del_qty,
                            biz_status,
                            status,
                            del_class,
                            mvm_type_id,
                            inv_loc_id,
                            inv_org_id,
                            deleted
                        FROM del_dn_item_tr 
                        WHERE dn_id = {head_record['id']} 
                        AND deleted = 0
                    """
                    
                    self.logger.info(f"查询送货单行表SQL: {item_sql}")
                    item_results = self.db.query(item_sql)
                    
                    dn_status_info = {
                        "dnCode": dn_code,
                        "confirmCode": dn_info["confirmCode"],
                        "delStatus": del_status,
                        "bizStatus": biz_status,
                        "btClass": bt_class,
                        "isInboundOperation": dn_info["isInboundOperation"],
                        "hasMaterialConsumption": dn_info["hasMaterialConsumption"],
                        "headRecord": head_record,
                        "itemCount": len(item_results),
                        "itemRecords": item_results
                    }
                    dn_status_results.append(dn_status_info)
                    
                    self.logger.info(f"送货单{dn_code}状态: delStatus={del_status}, bizStatus={biz_status}, btClass={bt_class}")
                    self.logger.info(f"送货单{dn_code}行项目数量: {len(item_results)}")
                    
                    # 验证送货单基本信息
                    assert head_record.get("deleted") == 0, f"送货单{dn_code}已被删除"
                    assert head_record.get("doc_code") == self.confirm_info["wo_code"], f"送货单{dn_code}关联的生产订单不匹配"
                    
                    # 验证送货单状态
                    self.logger.info(f"送货单{dn_code}详细信息: delStatus={del_status}, bizStatus={biz_status}, btClass={bt_class}")
                    self.logger.info(f"送货单{dn_code}是否入库工序: {dn_info['isInboundOperation']}, 是否有物料消耗: {dn_info['hasMaterialConsumption']}")
                    
                    # 根据业务规则验证状态
                    # status(del_status): 不管是否自动过账都是INEFFECT
                    # biz_status: 手动过账=WAIT_POST, 自动过账=POSTED
                    assert del_status == "INEFFECT", f"送货单{dn_code}单据状态应该是INEFFECT，当前状态: {del_status}"
                    assert bt_class == "PRD_CONFIRM", f"送货单{dn_code}业务类型应该是PRD_CONFIRM，当前类型: {bt_class}"
                    
                    if dn_info["isInboundOperation"]:
                        # 入库工序生成的送货单需要手工过账
                        assert biz_status == "WAIT_POST", f"入库工序送货单{dn_code}业务状态应该是WAIT_POST，当前状态: {biz_status}"
                        self.logger.info(f"✓ 入库工序送货单{dn_code}状态正确: 需要手工过账 (WAIT_POST)")
                    elif dn_info["hasMaterialConsumption"]:
                        # 物料消耗的送货单是自动过账
                        assert biz_status == "POSTED", f"物料消耗送货单{dn_code}业务状态应该是POSTED，当前状态: {biz_status}"
                        self.logger.info(f"✓ 物料消耗送货单{dn_code}状态正确: 自动过账 (POSTED)")
                    else:
                        # 普通工序不应该有送货单
                        self.logger.warning(f"⚠ 普通工序不应该生成送货单: {dn_code}")
                    
                    # 验证行项目数据（根据新字段结构）
                    if dn_info["hasMaterialConsumption"]:
                        assert len(item_results) > 0, f"物料消耗送货单{dn_code}应该有行项目数据"
                        for item in item_results:
                            # 验证计划交货数量
                            plan_del_qty = item.get("plan_del_qty", 0)
                            real_del_qty = item.get("real_del_qty", 0)
                            item_biz_status = item.get("biz_status", "")
                            item_status = item.get("status", "")
                            
                            assert plan_del_qty > 0, f"送货单{dn_code}行项目计划交货数量应该大于0，当前值: {plan_del_qty}"
                            assert item.get("mat_id") is not None, f"送货单{dn_code}行项目物料ID不能为空"
                            assert item.get("mvm_type_id") is not None, f"送货单{dn_code}行项目移动类型ID不能为空"
                            
                            # 验证行项目状态
                            assert item_status == "INEFFECT", f"送货单{dn_code}行项目状态应该是INEFFECT，当前状态: {item_status}"
                            
                            # 对于自动过账的物料消耗，行项目业务状态应该是POSTED
                            if biz_status == "POSTED":
                                assert item_biz_status == "POSTED", f"自动过账送货单{dn_code}行项目业务状态应该是POSTED，当前状态: {item_biz_status}"
                                # 自动过账的情况下，实际交货数量应该等于计划数量
                                assert real_del_qty == plan_del_qty, f"自动过账送货单{dn_code}实际交货数量应该等于计划数量，计划: {plan_del_qty}, 实际: {real_del_qty}"
                                self.logger.info(f"✓ 物料消耗行项目自动过账正确: 计划数量={plan_del_qty}, 实际数量={real_del_qty}")
                            
                            self.logger.info(f"送货单{dn_code}行项目详情: 物料ID={item.get('mat_id')}, 计划数量={plan_del_qty}, 实际数量={real_del_qty}, 状态={item_status}, 业务状态={item_biz_status}")
                    
                    # 对于入库工序，验证头表数据
                    if dn_info["isInboundOperation"]:
                        # 入库工序的送货单头表应该有相关入库信息
                        self.logger.info(f"✓ 入库工序送货单{dn_code}验证通过: 状态为未生效，等待手工过账")
                
                # 保存查询结果
                self.confirm_info["dn_status_results"] = dn_status_results
                
                # 添加报告附件（处理datetime字段）
                report_data = []
                for dn_result in dn_status_results:
                    # 只保存关键信息，避免datetime字段
                    report_item = {
                        "dnCode": dn_result["dnCode"],
                        "confirmCode": dn_result["confirmCode"],
                        "delStatus": dn_result["delStatus"],
                        "bizStatus": dn_result["bizStatus"],
                        "btClass": dn_result["btClass"],
                        "isInboundOperation": dn_result["isInboundOperation"],
                        "hasMaterialConsumption": dn_result["hasMaterialConsumption"],
                        "itemCount": dn_result["itemCount"],
                        "headRecordId": dn_result["headRecord"]["id"] if dn_result.get("headRecord") else None
                    }
                    report_data.append(report_item)
                
                a.json(report_data, "送货单状态查询结果")
                
                # 汇总验证结果
                summary = {
                    "total_dn_count": len(dn_status_results),
                    "inbound_dn_count": len([dn for dn in dn_status_results if dn["isInboundOperation"]]),
                    "material_consumption_dn_count": len([dn for dn in dn_status_results if dn["hasMaterialConsumption"]]),
                    "verification_passed": True
                }
                a.json(summary, "验证结果汇总")
                
                self.logger.info(f"送货单状态验证完成: 共{summary['total_dn_count']}个送货单，"
                               f"入库工序{summary['inbound_dn_count']}个，"
                               f"物料消耗{summary['material_consumption_dn_count']}个")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """本地调试入口
    
    按照测试用例执行顺序运行：
    1. 初始化测试类
    2. 执行setup_class
    3. 依次执行4个测试方法
    """
    test = TestWorkOrderConfirm()
    test.setup_class()
    test.test_query_confirm_list()
    test.test_batch_confirm_routings()
    test.test_delivery_confirm_batch()
    test.test_query_dn_status() 