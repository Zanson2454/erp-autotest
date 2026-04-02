"""采购交货单数据工厂"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from utils.param_util import ParamUtil
from utils.cache_util import CacheUtil


class DelPoDnFactory:
    """采购交货单工厂类"""
    
    def __init__(self, http_client, apis: dict, api_params: dict, mock_util, logger,
                 init_data: Optional[dict] = None,
                 md_cache_data: Optional[dict] = None,
                 del_cache_data: Optional[dict] = None):
        """
        初始化采购交货单工厂
        
        参数:
            http_client: HTTP客户端实例
            apis: API路径配置字典
            api_params: API参数配置字典
            mock_util: Mock工具实例
            logger: 日志实例
            init_data: 初始化数据（可选）
            md_cache_data: 主数据缓存（可选）
            del_cache_data: 交货配置缓存（可选）
        """
        self.http = http_client
        self.apis = apis
        self.api_params = api_params
        self.mock_util = mock_util
        self.logger = logger
        self.init_data = init_data or CacheUtil.get('init_cache') or {}
        self.md_cache_data = md_cache_data or CacheUtil.get('md_init_cache') or {}
        self.del_cache_data = del_cache_data or CacheUtil.get('del_init_cache') or {}
    
    def _get_default_value(self, param_value: Optional[str], cache_path: list, default: str = None) -> str:
        """
        获取参数值：优先使用传入值，否则从缓存获取
        
        参数:
            param_value: 传入的参数值
            cache_path: 缓存路径列表，如 ["md_cache_data", "org_info", "inv_org_info", 0, "id"]
            default: 最终默认值
            
        返回:
            参数值
        """
        if param_value:
            return param_value
        
        # 从缓存获取
        cache_type = cache_path[0]
        if cache_type == "md_cache_data":
            data = self.md_cache_data
        elif cache_type == "del_cache_data":
            data = self.del_cache_data
        elif cache_type == "init_data":
            data = self.init_data
        else:
            return default
        
        # 遍历路径获取值
        for key in cache_path[1:]:
            if isinstance(data, dict):
                data = data.get(key, {} if not isinstance(key, int) else [])
            elif isinstance(data, list) and isinstance(key, int):
                data = data[key] if len(data) > key else {}
            else:
                return default
        
        return data or default
    
    def create_po_delivery_note(
        self,
        po_item_id_list: List[int],
        dn_type_id: Optional[str] = None,
        inv_org_id: Optional[str] = None,
        inv_loc_id: Optional[str] = None,
        inv_wh_id: Optional[str] = None,
        com_org_id: Optional[str] = None,
        process_id: Optional[str] = None,
        cust_prtn_id: Optional[str] = None,
        vend_prtn_id: Optional[str] = None,
        recv_addr_id: Optional[str] = None,
        send_addr_id: Optional[str] = None,
        plan_del_qty: Optional[float] = None,
        remark: Optional[str] = None,
        batch_info: Optional[List[Dict]] = None
    ) -> Dict:
        """
        创建采购交货单（智能默认值：传值优先，不传从缓存获取）
        
        必需参数:
            po_item_id_list: 采购订单行ID列表
        
        可选参数（不传则从缓存/草稿数据自动获取）:
            dn_type_id: 交货单类型ID (默认获取 STND_INBN)
            inv_org_id: 库存组织ID
            inv_loc_id: 库存地点ID
            inv_wh_id: 仓库ID
            com_org_id: 公司组织ID
            process_id: 流程ID (不传则从草稿数据自动获取)
            cust_prtn_id: 客户ID
            vend_prtn_id: 供应商ID
            recv_addr_id: 收货地址ID (不传则从草稿数据自动获取)
            send_addr_id: 发货地址ID (不传则从草稿数据自动获取)
            plan_del_qty: 计划交货数量
            remark: 备注
            batch_info: 批次信息列表（可选，传入则为带批次交货单）
                示例: [
                    {
                        "batchType": "INBOUND",
                        "batchCode": "BAT202510241146100",
                        "charaClassId": 2004001,
                        "quantity": 2,
                        "charaValue": [...]
                    }
                ]
        
        返回:
            成功: {"success": True, "dn_id": xxx, "dn_code": xxx, "del_status": xxx, "response": {...}}
            失败: 抛出异常
        """
        try:
            # 智能获取默认值
            dn_type_id = self._get_dn_type_id(dn_type_id)
            inv_org_id = self._get_default_value(inv_org_id, ["md_cache_data", "org_info", "inv_org_info", 0, "id"])
            inv_loc_id = self._get_default_value(inv_loc_id, ["md_cache_data", "org_info", "inv_loc_info", 0, "id"])
            inv_wh_id = self._get_default_value(inv_wh_id, ["md_cache_data", "org_info", "inv_wh_md", 0, "id"])
            com_org_id = self._get_default_value(com_org_id, ["md_cache_data", "org_info", "gr_come_org_info", 0, "id"])
            cust_prtn_id = self._get_default_value(cust_prtn_id, ["md_cache_data", "partner_info", "cust_info", 0, "id"])
            vend_prtn_id = self._get_default_value(vend_prtn_id, ["md_cache_data", "partner_info", "vend_info", 0, "id"])
            
            # 步骤1: 调用采购订单行分组接口
            group_response = self._group_po_items(po_item_id_list)
            
            # 步骤2: 提取交货单草稿
            dn_draft = self._extract_dn_draft(group_response)
            
            # 从草稿数据中获取这些参数（如果用户没有传入值）
            if not process_id:
                process_id = dn_draft.get("processId")
            if not recv_addr_id:
                recv_addr_id = dn_draft.get("recvAddrId")
            if not send_addr_id:
                send_addr_id = dn_draft.get("sendAddrId")
            
            # 步骤3: 提交交货单
            submit_response = self._submit_delivery_note(
                dn_draft=dn_draft,
                dn_type_id=dn_type_id,
                inv_org_id=inv_org_id,
                inv_loc_id=inv_loc_id,
                inv_wh_id=inv_wh_id,
                com_org_id=com_org_id,
                process_id=process_id,
                cust_prtn_id=cust_prtn_id,
                vend_prtn_id=vend_prtn_id,
                recv_addr_id=recv_addr_id,
                send_addr_id=send_addr_id,
                plan_del_qty=plan_del_qty,
                remark=remark,
                batch_info=batch_info
            )
            
            # 提取返回结果
            return self._build_result(submit_response, dn_draft)
                
        except Exception as e:
            self.logger.error(f"创建采购交货单异常: {str(e)}")
            raise
    
    def _get_dn_type_id(self, dn_type_id: Optional[str]) -> str:
        """获取交货单类型ID，优先获取 STND_INBN（标准内向交货）"""
        if dn_type_id:
            return dn_type_id
        
        if self.del_cache_data:
            dn_types = self.del_cache_data.get("del_config", {}).get("dn_type_info", [])
            return next(
                (item.get("id") for item in dn_types if item.get("dn_type_code") == "STND_INBN"),
                dn_types[0].get("id") if dn_types else None
            )
        return None
    
    def _group_po_items(self, po_item_id_list: List[int]) -> Dict:
        """调用采购订单行分组接口"""
        api_path = ParamUtil.get_api_path(self.apis, "DN-采购-项目行分组服务")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        params["params"]["request"] = [{"id": po_item_id} for po_item_id in po_item_id_list]
        
        response = self.http.post(url, json=params, params={"tmodule": "SCM_DEL"})
        
        if not response.get("success"):
            error_msg = response.get("message", "未知错误")
            raise Exception(f"采购订单行分组接口调用失败: {error_msg}")
        
        return response
    
    def _extract_dn_draft(self, group_response: Dict) -> Dict:
        """从分组接口响应中提取交货单草稿"""
        dn_draft_list = group_response.get("data", {}).get("data", [])
        if not dn_draft_list:
            raise ValueError("采购订单行分组接口未返回交货单草稿数据")
        
        return dn_draft_list[0].get("values", {})
    
    def _submit_delivery_note(
        self,
        dn_draft: Dict,
        dn_type_id: str,
        inv_org_id: str,
        inv_loc_id: str,
        inv_wh_id: str,
        com_org_id: str,
        process_id: str,
        cust_prtn_id: str,
        vend_prtn_id: str,
        recv_addr_id: str,
        send_addr_id: str,
        plan_del_qty: Optional[float],
        remark: Optional[str],
        batch_info: Optional[List[Dict]]
    ) -> Dict:
        """提交交货单"""
        api_path = ParamUtil.get_api_path(self.apis, "DEL-保存发货单-批量服务")
        params, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        # 构建请求参数
        request_item = self._build_request_item(
            dn_draft, dn_type_id, inv_org_id, inv_loc_id, inv_wh_id, com_org_id,
            process_id, cust_prtn_id, vend_prtn_id, recv_addr_id, send_addr_id,
            plan_del_qty, remark, batch_info
        )
        
        params["params"]["request"] = [request_item]
        response = self.http.post(url, json=params, params={"tmodule": "SCM_DEL"})
        
        if not response.get("success"):
            error_msg = response.get("message", "未知错误")
            raise Exception(f"交货单提交接口调用失败: {error_msg}")
        
        return response
    
    def _build_request_item(
        self,
        dn_draft: Dict,
        dn_type_id: str,
        inv_org_id: str,
        inv_loc_id: str,
        inv_wh_id: str,
        com_org_id: str,
        process_id: str,
        cust_prtn_id: str,
        vend_prtn_id: str,
        recv_addr_id: str,
        send_addr_id: str,
        plan_del_qty: Optional[float],
        remark: Optional[str],
        batch_info: Optional[List[Dict]]
    ) -> Dict:
        """构建交货单提交请求参数"""
        # 提取并更新明细行
        dn_item_list = dn_draft.get("dnItemList", [])
        if not dn_item_list:
            raise ValueError("交货单草稿中未找到明细行数据")
        
        # 更新明细行数量和批次信息
        for dn_item in dn_item_list:
            if plan_del_qty is not None:
                dn_item["planDelQty"] = plan_del_qty
            
            # 处理批次信息：传入则使用传入值，否则使用空列表
            if batch_info is not None:
                dn_item["batchInfo"] = batch_info
            else:
                dn_item["batchInfo"] = []
        
        # 构建请求数据
        current_timestamp = int(datetime.now().timestamp() * 1000)
        request_item = {
            "dnCode": dn_draft.get("dnCode"),
            "dnType": {"id": dn_type_id},
            "btClass": "PUR",
            "delClass": "RECV",
            "invOrgId": {"id": inv_org_id},
            "delStatus": "DRAFT",
            "invLocId": {"id": inv_loc_id},
            "invWhId": {"id": inv_wh_id},
            "isInvExecuted": True,
            "wmEnabled": True,
            "remark": remark,
            "docCode": dn_draft.get("docCode"),
            "comOrgId": {"id": com_org_id},
            "processId": process_id,
            "custPrtnId": {"id": cust_prtn_id},
            "recvAddrId": recv_addr_id,
            "recvAddrDesc": dn_draft.get("recvAddrDesc", "自动化测试收货地址"),
            "recvContactInfo": dn_draft.get("recvContactInfo", "自动化测试联系人"),
            "recvContactPhone": dn_draft.get("recvContactPhone", "13800138000"),
            "vendPrtnId": {"id": vend_prtn_id},
            "sendAddrId": send_addr_id,
            "sendAddrDesc": dn_draft.get("sendAddrDesc", "自动化测试发货地址"),
            "sendContactInfo": dn_draft.get("sendContactInfo", "自动化测试发货联系人"),
            "sendContactPhone": dn_draft.get("sendContactPhone", "18808080808"),
            "planRecvDate": dn_draft.get("planRecvDate", current_timestamp),
            "planSendDate": dn_draft.get("planSendDate", current_timestamp),
            "dnItemList": dn_item_list,
            "delAttachmentList": None,
            "delTextList": None
        }
        
        return request_item
    
    def _build_result(self, submit_response: Dict, dn_draft: Dict) -> Dict:
        """构建返回结果"""
        if not submit_response.get("success"):
            error_msg = submit_response.get("message", "未知错误")
            raise Exception(f"采购交货单创建失败: {error_msg}")
        
        dn_data = submit_response.get("data", {}).get("data", [{}])[0]
        dn_id = dn_data.get("id")
        dn_code = dn_data.get("dnCode") or dn_draft.get("dnCode")
        del_status = dn_data.get("delStatus", "DRAFT")
        
        return {
            "success": True,
            "dn_id": dn_id,
            "dn_code": dn_code,
            "del_status": del_status,
            "response": submit_response,
            "dn_draft_data": dn_draft,
            "dn_full_data": dn_data
        }
    
    def submit_delivery_note(self, dn_id: int = None, dn_full_data: Dict = None) -> Dict:
        """
        提交采购交货单（从草稿态提交）
        
        参数:
            dn_id: 交货单ID（如果传入则查询完整数据后提交）
            dn_full_data: 交货单完整数据（优先使用，如果传入则直接提交）
        
        返回:
            成功: {"success": True, "dn_id": xxx, "dn_code": xxx, "del_status": xxx, "response": {...}}
            失败: 抛出异常
        """
        try:
            # 如果没有传入完整数据，需要先查询
            if not dn_full_data:
                if not dn_id:
                    raise ValueError("必须传入 dn_id 或 dn_full_data")
                dn_full_data = self._query_dn_detail(dn_id)
            
            # 调用提交接口
            api_path = ParamUtil.get_api_path(self.apis, "DEL-交货单公共-交货单提交业务处理服务")
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            # 设置请求参数（需要传入完整的交货单数据）
            params["params"]["request"] = dn_full_data
            
            response = self.http.post(url, json=params, params={"tmodule": "SCM_DEL"})
            
            if not response.get("success"):
                error_msg = response.get("message", "未知错误")
                raise Exception(f"交货单提交失败: {error_msg}")
            
            # 提取结果
            result_data = response.get("data", {}).get("data", {})
            dn_id = result_data.get("id") or dn_full_data.get("id")
            dn_code = result_data.get("dnCode") or dn_full_data.get("dnCode")
            del_status = result_data.get("delStatus", "SUBMITTED")
            
            return {
                "success": True,
                "dn_id": dn_id,
                "dn_code": dn_code,
                "del_status": del_status,
                "response": response
            }
            
        except Exception as e:
            self.logger.error(f"提交采购交货单异常: {str(e)}")
            raise
    
    def _query_dn_detail(self, dn_id: int) -> Dict:
        """查询交货单详情（用于提交前获取完整数据）"""
        api_path = ParamUtil.get_api_path(self.apis, "(系统)查询数据详情服务")
        _, url = ParamUtil.get_api_params(self.api_params, api_path)
        
        request_params = {
            "serviceKey": "SCM_DEL$SYS_FindDataByIdService",
            "params": {
                "request": {"id": dn_id},
                "modelKey": "SCM_DEL$del_dn_head_tr"
            }
        }
        
        response = self.http.post(
            url,
            json=request_params,
            params={"tmodule": "SCM_DEL", "modelKey": "SCM_DEL$del_dn_head_tr"}
        )
        
        if not response.get("success"):
            error_msg = response.get("message", "未知错误")
            raise Exception(f"查询交货单详情失败: {error_msg}")
        
        return response.get("data", {}).get("data", {})


if __name__ == "__main__":
    """独立运行测试"""
    from testcases.scm_del import ScmDelBaseTest
    
    print("📦 采购交货单数据工厂 - 独立测试")
    print("="*60)
    
    ScmDelBaseTest.setup_class()
    
    dn_factory = DelPoDnFactory(
        http_client=ScmDelBaseTest.http,
        apis=ScmDelBaseTest.apis,
        api_params=ScmDelBaseTest.api_params,
        mock_util=ScmDelBaseTest.mock_util,
        logger=ScmDelBaseTest.logger,
        init_data=ScmDelBaseTest.init_data,
        md_cache_data=ScmDelBaseTest.md_cache_data,
        del_cache_data=ScmDelBaseTest.del_cache_data
    )
    
    po_item_id = 17032083  # 替换为实际的采购订单行ID
    
    try:
        result = dn_factory.create_po_delivery_note(
            po_item_id_list=[po_item_id],
            plan_del_qty=2,
            remark="自动化测试"
        )
        
        print("✅ 采购交货单创建成功！")
        print(f"交货单ID: {result.get('dn_id')}")
        print(f"交货单编码: {result.get('dn_code')}")
        print(f"交货状态: {result.get('del_status')}")
        
    except Exception as e:
        print(f"❌ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
