"""采购订单数据工厂"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from utils.param_util import ParamUtil
from utils.cache_util import CacheUtil


class PurPoFactory:
    """采购订单工厂类"""
    
    def __init__(self, http_client, apis: dict, api_params: dict, mock_util, logger,
                 init_data: Optional[dict] = None,
                 md_cache_data: Optional[dict] = None,
                 pur_cache_data: Optional[dict] = None):
        """
        初始化采购订单工厂
        
        参数:
            http_client: HTTP客户端实例
            apis: API路径配置字典
            api_params: API参数配置字典
            mock_util: Mock工具实例
            logger: 日志实例
            init_data: 初始化数据（可选，用于获取默认值）
            md_cache_data: 主数据缓存（可选，用于获取默认值）
            pur_cache_data: 采购配置缓存（可选，用于获取默认值）
        """
        self.http = http_client
        self.apis = apis
        self.api_params = api_params
        self.mock_util = mock_util
        self.logger = logger
        self.init_data = init_data or CacheUtil.get('init_cache') or {}
        self.md_cache_data = md_cache_data or CacheUtil.get('md_init_cache') or {}
        self.pur_cache_data = pur_cache_data or CacheUtil.get('pur_init_cache') or {}
    
    def _get_default_value(self, param_value: Optional[str], cache_path: list, default: str = None) -> str:
        """
        获取参数值：优先使用传入值，否则从缓存获取
        
        参数:
            param_value: 传入的参数值
            cache_path: 缓存路径列表，如 ["md_cache_data", "org_info", "pur_org_info", 0, "id"]
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
        elif cache_type == "pur_cache_data":
            data = self.pur_cache_data
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
    
    def create_standard_po(
        self,
        mat_items: List[Dict],
        po_type_id: Optional[str] = None,
        vend_id: Optional[str] = None,
        pur_employee_id: Optional[str] = None,
        pur_org_id: Optional[str] = None,
        com_org_id: Optional[str] = None,
        business_date: Optional[int] = None,
        pur_remark: Optional[str] = None,
        pur_curr_id: Optional[str] = None
    ) -> Dict:
        """
        创建标准采购订单（智能默认值：传值优先，不传从缓存获取）
        
        必需参数:
            mat_items: 物料明细列表，每个元素可包含:
                - mat_id: 物料ID (必需)
                - mat_code: 物料编码 (可选，不传从缓存获取)
                - inv_org_id: 库存组织ID (可选，不传从缓存获取)
                - inv_loc_id: 库存位置ID (可选，不传从缓存获取)
                - uom_pur_id: 采购单位ID (可选，不传从缓存获取)
                - qty: 数量 (默认1)
                - price: 价格 (默认0)
                - po_item_type_id: 订单明细类型ID (可选，不传从缓存获取)
                - tax_rate_id: 税率ID (可选，不传从缓存获取)
                - delivery_date: 交货日期 (默认当前时间)
                - note: 备注 (默认"执行自动化测试备注")
                - po_schl_list: 计划行列表 (可选，支持自定义拆分计划行)
                    示例: [
                        {"qty": 10, "delivery_date": 1761033525000},
                        {"qty": 2, "delivery_date": 1760976000000}
                    ]
                    注意: 所有计划行数量之和不能超过订单行数量
        
        可选参数（不传则从缓存自动获取）:
            po_type_id: 采购订单类型ID (默认从 pur_cache_data 获取)
            vend_id: 供应商ID (默认从 md_cache_data 获取)
            pur_employee_id: 采购员ID (默认从 md_cache_data 获取)
            pur_org_id: 采购组织ID (默认从 md_cache_data 获取)
            com_org_id: 公司组织ID (默认从 md_cache_data 获取)
            business_date: 业务日期 (默认当前时间)
            pur_remark: 采购备注 (默认"执行自动化测试备注")
            pur_curr_id: 采购币种ID (默认从 init_data 获取)
        
        返回:
            成功: {"success": True, "response": {...}}
            失败: 抛出异常
        """
        try:
            # 智能获取默认值（传值优先，不传从缓存获取）
            po_type_id = self._get_default_value(
                po_type_id, 
                ["pur_cache_data", "pur_config", "po_type_info", 0, "id"]
            )
            vend_id = self._get_default_value(
                vend_id,
                ["md_cache_data", "partner_info", "vend_info", 0, "id"]
            )
            pur_employee_id = self._get_default_value(
                pur_employee_id,
                ["md_cache_data", "org_info", "employee_info", 0, "id"]
            )
            pur_org_id = self._get_default_value(
                pur_org_id,
                ["md_cache_data", "org_info", "pur_org_info", 0, "id"]
            )
            com_org_id = self._get_default_value(
                com_org_id,
                ["md_cache_data", "org_info", "gr_come_org_info", 0, "id"]
            )
            pur_curr_id = self._get_default_value(
                pur_curr_id,
                ["init_data", "currency_info", 0, "curr_id"],
                default="2000001"  # 默认人民币
            )
            
            # 获取采购相关方类型ID（用于partner参数）
            pur_partner_type_id = self._get_default_value(
                None,
                ["md_cache_data", "partner_info", "partner_type_cf", "pur_partner_type", "id"]
            )
            
            api_path = ParamUtil.get_api_path(self.apis, "PO-创建订单-提交服务")
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            po_items = self._build_po_items(mat_items, vend_id, pur_employee_id)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["poCode", "poType", "vendId", "purEmployee", "purOrgId", "comOrgId", 
                 "purRemark", "poItem", "businessDate", "purCurrId", "currTypeCode",
                 "partner", "attachment"],
                ["params", "request"]
            )
            
            # 构建partner参数（智能获取相关方类型ID）
            partner_list = []
            if pur_partner_type_id:
                partner_list.append({
                    "partnerTypeRef": {"id": pur_partner_type_id},
                    "partnerRef": {"id": vend_id}
                })
            
            ParamUtil.set_request_params(filtered_params, {
                "poCode": None,
                "poType": {"id": po_type_id},
                "vendId": {"id": vend_id},
                "purEmployee": {"id": pur_employee_id},
                "purOrgId": {"id": pur_org_id},
                "comOrgId": {"id": com_org_id},
                "purRemark": pur_remark or "执行自动化测试备注",
                "poItem": po_items,
                "businessDate": business_date or int(datetime.now().timestamp() * 1000),
                "purCurrId": {"id": pur_curr_id},
                "currTypeCode": {"id": pur_curr_id},
                "partner": partner_list,
                "attachment": []
            })
            
            try:
                response = self.http.post(url, json=filtered_params, params={"tmodule": "SCM_PUR"})
            except Exception as http_error:
                # 捕获HTTP错误（如500、504等）
                error_detail = str(http_error)
                self.logger.error(f"HTTP请求失败: {error_detail}")
                self.logger.error(f"请求URL: {url}")
                self.logger.error(f"请求参数: {filtered_params}")
                # 尝试获取响应内容
                if hasattr(http_error, 'response') and http_error.response is not None:
                    try:
                        error_response = http_error.response.json()
                        self.logger.error(f"错误响应内容: {error_response}")
                    except:
                        self.logger.error(f"错误响应文本: {http_error.response.text}")
                raise Exception(f"采购订单创建失败（HTTP错误）: {error_detail}") from http_error
            
            if response.get("success"):
                self.logger.info("采购订单创建成功")
                return {
                    "success": True,
                    "response": response
                }
            else:
                error_msg = response.get("message") or response.get("errorMessage") or response.get("error") or "未知错误"
                self.logger.error(f"采购订单创建失败: {error_msg}")
                self.logger.error(f"完整响应内容: {response}")
                raise Exception(f"采购订单创建失败: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"创建采购订单异常: {str(e)}")
            # 如果不是我们自定义的异常，记录完整的异常信息
            if not isinstance(e, Exception) or "采购订单创建失败" not in str(e):
                import traceback
                self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            raise
    
    def _build_po_items(self, mat_items: List[Dict], vend_id: str, pur_employee_id: str) -> List[Dict]:
        """构建采购订单明细（支持智能默认值 + 计划行拆分）"""
        po_items = []
        tax_rate = 0.13
        
        # 从缓存获取默认值
        default_inv_org_id = self._get_default_value(None, ["md_cache_data", "org_info", "inv_org_info", 0, "id"])
        default_inv_loc_id = self._get_default_value(None, ["md_cache_data", "org_info", "inv_loc_info", 0, "id"])
        default_uom_pur_id = self._get_default_value(None, ["init_data", "uom_info", "qty_uom_info", 0, "uom_id"])
        default_po_item_type_id = None
        default_tax_rate_id = self._get_default_value(None, ["init_data", "tax_info", 0, "id"])
        default_pur_curr_id = self._get_default_value(None, ["init_data", "currency_info", 0, "curr_id"], default="2000001")
        
        # 获取 STND 类型的订单明细类型ID
        if self.pur_cache_data:
            po_item_types = self.pur_cache_data.get("pur_config", {}).get("po_item_type_info", [])
            default_po_item_type_id = next(
                (item.get("id") for item in po_item_types if item.get("po_item_type") == "STND"),
                None
            )
        
        for idx, item in enumerate(mat_items, start=1):
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            
            amount_gross = round(qty * price, 2)
            amount_net = round(amount_gross / (1 + tax_rate), 2)
            tax_amount = round(amount_gross - amount_net, 2)
            price_net = round(price / (1 + tax_rate), 2)
            
            # 智能获取参数（传值优先，不传使用默认值）
            inv_org_id = item.get("inv_org_id") or default_inv_org_id
            inv_loc_id = item.get("inv_loc_id") or default_inv_loc_id
            uom_pur_id = item.get("uom_pur_id") or default_uom_pur_id
            po_item_type_id = item.get("po_item_type_id") or default_po_item_type_id
            tax_rate_id = item.get("tax_rate_id") or default_tax_rate_id
            pur_curr_id = item.get("pur_curr_id") or default_pur_curr_id
            
            # 构建计划行（支持用户自定义拆分）
            po_schl_list = self._build_po_schl(
                item=item,
                qty=qty,
                inv_org_id=inv_org_id,
                inv_loc_id=inv_loc_id,
                uom_pur_id=uom_pur_id,
                vend_id=vend_id,
                pur_employee_id=pur_employee_id
            )
            
            po_item = {
                "poItemType": {"id": po_item_type_id},
                "poItemUsge": "ORDINARY",
                "note": item.get("note", "执行自动化测试备注"),
                "matId": {"id": item.get("mat_id")},
                "matCode": item.get("mat_code"),
                "uomPurId": {"id": uom_pur_id},
                "poItemQtyPur": qty,
                "priceGross": price,
                "priceNet": price_net,
                "priceNetBus": price_net,
                "currTypePur": {"id": pur_curr_id},
                "taxRateCode": {"id": tax_rate_id},
                "amountGross": amount_gross,
                "amountNet": amount_net,
                "taxAmount": tax_amount,
                "poSchl": po_schl_list,
                "invOrgId": {"id": inv_org_id},
                "invLocId": {"id": inv_loc_id},
                "poDateDel": item.get("delivery_date", int(datetime.now().timestamp() * 1000)),
                "uomPurIdBus": {"id": uom_pur_id},
                "poItemQtyPurBus": qty,
                "priceGrossBus": price,
                "poItemQtyFul": 0,
                "deliveryFrozen": False,
                "deliveryCompleted": False,
                "verificationCompleted": False,
                "deliveryMaximum": 100,
                "deliveryMinimum": 1,
                "itemLevelCode": f"{idx}0",
                "isWriteOff": False
            }
            
            po_items.append(po_item)
        
        return po_items
    
    def _build_po_schl(
        self, 
        item: Dict, 
        qty: float,
        inv_org_id: str,
        inv_loc_id: str,
        uom_pur_id: str,
        vend_id: str,
        pur_employee_id: str
    ) -> List[Dict]:
        """
        构建计划行列表（支持自定义拆分）
        
        参数:
            item: 订单行配置
            qty: 订单行总数量
            inv_org_id: 库存组织ID
            inv_loc_id: 库存位置ID
            uom_pur_id: 采购单位ID
            vend_id: 供应商ID
            pur_employee_id: 采购员ID
            
        返回:
            计划行列表
        """
        po_schl_list = []
        custom_schl_list = item.get("po_schl_list", [])
        
        if custom_schl_list:
            # 用户自定义计划行：校验数量总和
            total_schl_qty = sum(schl.get("qty", 0) for schl in custom_schl_list)
            if total_schl_qty > qty:
                raise ValueError(
                    f"计划行数量总和 ({total_schl_qty}) 不能超过订单行数量 ({qty})"
                )
            
            # 构建多个计划行
            for schl in custom_schl_list:
                schl_qty = schl.get("qty", 0)
                schl_delivery_date = schl.get("delivery_date", int(datetime.now().timestamp() * 1000))
                
                po_schl_list.append({
                    "matId": {"id": item.get("mat_id")},
                    "poSchlQtyDel": schl_qty,
                    "poSchlQtyFul": 0,
                    "poSchlDateDel": schl_delivery_date,
                    "invOrgId": {"id": inv_org_id},
                    "invLocId": {"id": inv_loc_id},
                    "uomPurId": {"id": uom_pur_id},
                    "vendId": {"id": vend_id},
                    "purEmployee": {"id": pur_employee_id}
                })
        else:
            # 默认：单个计划行
            po_schl_list.append({
                "matId": {"id": item.get("mat_id")},
                "poSchlQtyDel": qty,
                "poSchlQtyFul": 0,
                "invOrgId": {"id": inv_org_id},
                "invLocId": {"id": inv_loc_id},
                "uomPurId": {"id": uom_pur_id},
                "vendId": {"id": vend_id},
                "purEmployee": {"id": pur_employee_id}
            })
        
        return po_schl_list


# if __name__ == "__main__":
#     """独立运行测试采购订单创建（演示智能默认值）"""
#     from testcases.scm_pur import ScmPurBaseTest
    
#     print("\n" + "="*60)
#     print("📦 采购订单数据工厂 - 独立测试（智能默认值）")
#     print("="*60 + "\n")
    
#     ScmPurBaseTest.setup_class()
    
#     # 初始化工厂（自动从缓存加载默认值）
#     po_factory = PurPoFactory(
#         http_client=ScmPurBaseTest.http,
#         apis=ScmPurBaseTest.apis,
#         api_params=ScmPurBaseTest.api_params,
#         mock_util=ScmPurBaseTest.mock_util,
#         logger=ScmPurBaseTest.logger,
#         init_data=ScmPurBaseTest.init_data,
#         md_cache_data=ScmPurBaseTest.md_cache_data,
#         pur_cache_data=ScmPurBaseTest.pur_cache_data
#     )
    
#     # 获取物料ID（从缓存）
#     mat_id = ScmPurBaseTest.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0].get("id")
#     mat_code = ScmPurBaseTest.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0].get("mat_code")
    
#     current_ts = int(datetime.now().timestamp() * 1000)
    
#     # 示例1：只传必需参数（mat_id），其他从缓存自动获取
#     print("【示例1】只传 mat_id，其他参数自动从缓存获取：")
#     mat_items_simple = [
#         {
#             "mat_id": mat_id,
#             "mat_code": mat_code,
#             "qty": 10,
#             "price": 100
#         }
#     ]
    
#     try:
#         result = po_factory.create_standard_po(mat_items=mat_items_simple)
#         print("✅ 采购订单创建成功（使用默认值）")
#         print(f"订单ID: {result.get('response', {}).get('data', {}).get('data')}\n")
#     except Exception as e:
#         print(f"❌ 创建失败: {str(e)}\n")
#         import traceback
#         traceback.print_exc()
    
#     # 示例2：自定义计划行拆分（关键功能）
#     print("\n【示例2】自定义计划行拆分（1个订单行拆成2个计划行）：")
#     mat_items_split_schl = [
#         {
#             "mat_id": mat_id,
#             "mat_code": mat_code,
#             "qty": 12,  # 订单行总数量
#             "price": 11,
#             "po_schl_list": [  # 自定义计划行
#                 {"qty": 10, "delivery_date": current_ts + 86400000 * 5},  # 5天后
#                 {"qty": 2, "delivery_date": current_ts}  # 今天
#             ]
#         }
#     ]
    
#     try:
#         result = po_factory.create_standard_po(mat_items=mat_items_split_schl)
#         print("✅ 采购订单创建成功（计划行拆分：10 + 2 = 12）")
#         print(f"订单ID: {result.get('response', {}).get('data', {}).get('data')}\n")
#     except Exception as e:
#         print(f"❌ 创建失败: {str(e)}\n")
#         import traceback
#         traceback.print_exc()
    
#     # 示例3：计划行数量校验（预期失败）
#     print("\n【示例3】计划行数量校验（故意触发错误）：")
#     mat_items_invalid = [
#         {
#             "mat_id": mat_id,
#             "mat_code": mat_code,
#             "qty": 12,
#             "price": 11,
#             "po_schl_list": [
#                 {"qty": 10, "delivery_date": current_ts},
#                 {"qty": 5, "delivery_date": current_ts}  # 总和15 > 订单行12
#             ]
#         }
#     ]
    
#     try:
#         result = po_factory.create_standard_po(mat_items=mat_items_invalid)
#         print("❌ 应该触发校验错误，但成功了！\n")
#     except ValueError as e:
#         print(f"✅ 校验成功拦截：{str(e)}\n")
#     except Exception as e:
#         print(f"⚠️  其他异常: {str(e)}\n")
    
#     # 示例4：不传计划行（默认行为，兼容旧代码）
#     print("\n【示例4】不传计划行（默认行为，向后兼容）：")
#     mat_items_default = [
#         {
#             "mat_id": mat_id,
#             "mat_code": mat_code,
#             "qty": 15,
#             "price": 50
#         }
#     ]
    
#     try:
#         result = po_factory.create_standard_po(mat_items=mat_items_default)
#         print("✅ 采购订单创建成功（使用默认单个计划行）")
#         print(f"订单ID: {result.get('response', {}).get('data', {}).get('data')}\n")
#     except Exception as e:
#         print(f"❌ 创建失败: {str(e)}\n")
#         import traceback
#         traceback.print_exc()
    
#     print("="*60)
#     print("测试完成！")
#     print("="*60 + "\n")
