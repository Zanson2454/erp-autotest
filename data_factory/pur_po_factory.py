"""采购订单数据工厂"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from utils.param_util import ParamUtil


class PurPoFactory:
    """采购订单工厂类"""
    
    def __init__(self, http_client, apis: dict, api_params: dict, mock_util, logger):
        """
        初始化采购订单工厂
        
        参数:
            http_client: HTTP客户端实例
            apis: API路径配置字典
            api_params: API参数配置字典
            mock_util: Mock工具实例
            logger: 日志实例
        """
        self.http = http_client
        self.apis = apis
        self.api_params = api_params
        self.mock_util = mock_util
        self.logger = logger
    
    def create_standard_po(
        self,
        po_type_id: str,
        vend_id: str,
        pur_employee_id: str,
        pur_org_id: str,
        com_org_id: str,
        mat_items: List[Dict],
        business_date: Optional[int] = None,
        pur_remark: Optional[str] = None,
        pur_curr_id: Optional[str] = "2000001"
    ) -> Dict:
        """
        创建标准采购订单
        
        必需参数:
            po_type_id: 采购订单类型ID
            vend_id: 供应商ID
            pur_employee_id: 采购员ID
            pur_org_id: 采购组织ID
            com_org_id: 公司组织ID
            mat_items: 物料明细列表，每个元素需包含:
                - mat_id: 物料ID (必需)
                - mat_code: 物料编码 (必需)
                - inv_org_id: 库存组织ID (必需)
                - inv_loc_id: 库存位置ID (必需)
                - uom_pur_id: 采购单位ID (必需，需从物料主数据获取)
                - qty: 数量 (默认1)
                - price: 价格 (默认0)
                - po_item_type_id: 订单明细类型ID (默认2012001)
                - tax_rate_id: 税率ID (默认2002001)
                - delivery_date: 交货日期 (默认当前时间)
                - note: 备注 (默认"执行自动化测试备注")
        
        可选参数:
            business_date: 业务日期 (默认当前时间)
            pur_remark: 采购备注 (默认"执行自动化测试备注")
            pur_curr_id: 采购币种ID (默认"2000001")
        
        返回:
            成功: {"success": True, "response": {...}}
            失败: 抛出异常
        """
        try:
            # 1. 获取API配置
            api_path = ParamUtil.get_api_path(self.apis, "PO-创建订单-提交服务")
            params, url = ParamUtil.get_api_params(self.api_params, api_path)
            
            # 2. 构建采购订单明细
            po_items = self._build_po_items(mat_items, vend_id, pur_employee_id)
            
            # 3. 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["poCode", "poType", "vendId", "purEmployee", "purOrgId", "comOrgId", 
                 "purRemark", "poItem", "businessDate", "purCurrId", "currTypeCode",
                 "partner", "attachment"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
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
                "partner": [{"partnerTypeRef": {"id": "2000005"}, "partnerRef": {"id": vend_id}}],
                "attachment": []
            })
            
            # 5. 执行请求
            response = self.http.post(url, json=filtered_params, params={"tmodule": "SCM_PUR"})
            
            # 6. 处理响应
            if response.get("success"):
                self.logger.info("✅ 采购订单创建成功")
                return {
                    "success": True,
                    "response": response
                }
            else:
                error_msg = response.get("message", "未知错误")
                self.logger.error(f"❌ 采购订单创建失败: {error_msg}")
                raise Exception(f"采购订单创建失败: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"❌ 创建采购订单异常: {str(e)}")
            raise
    
    def _build_po_items(self, mat_items: List[Dict], vend_id: str, pur_employee_id: str) -> List[Dict]:
        """构建采购订单明细"""
        po_items = []
        tax_rate = 0.13  # 13% 税率
        
        for idx, item in enumerate(mat_items, start=1):
            # 获取价格和数量
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            
            # 计算金额
            amount_gross = round(qty * price, 2)
            amount_net = round(amount_gross / (1 + tax_rate), 2)
            tax_amount = round(amount_gross - amount_net, 2)
            price_net = round(price / (1 + tax_rate), 2)
            
            po_item = {
                "poItemType": {"id": item.get("po_item_type_id", "2012001")},
                "poItemUsge": "ORDINARY",
                "note": item.get("note", "执行自动化测试备注"),
                "matId": {"id": item.get("mat_id")},
                "matCode": item.get("mat_code"),
                "uomPurId": {"id": item.get("uom_pur_id", "2002011")},
                "poItemQtyPur": qty,
                "priceGross": price,
                "priceNet": price_net,
                "priceNetBus": price_net,
                "currTypePur": {"id": "2000001"},
                "taxRateCode": {"id": item.get("tax_rate_id", "2002001")},
                "amountGross": amount_gross,
                "amountNet": amount_net,
                "taxAmount": tax_amount,
                "poSchl": [{
                    "matId": {"id": item.get("mat_id")},
                    "poSchlQtyDel": qty,
                    "poSchlQtyFul": 0,
                    "invOrgId": {"id": item.get("inv_org_id")},
                    "invLocId": {"id": item.get("inv_loc_id")},
                    "uomPurId": {"id": item.get("uom_pur_id", "2002011")},
                    "vendId": {"id": vend_id},
                    "purEmployee": {"id": pur_employee_id}
                }],
                "invOrgId": {"id": item.get("inv_org_id")},
                "invLocId": {"id": item.get("inv_loc_id")},
                "poDateDel": item.get("delivery_date", int(datetime.now().timestamp() * 1000)),
                "uomPurIdBus": {"id": item.get("uom_pur_id", "2002011")},
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


if __name__ == "__main__":
    """独立运行测试采购订单创建"""
    from testcases.scm_pur import ScmPurBaseTest
    from utils.mock_util import MockData
    
    print("\n" + "="*60)
    print("📦 采购订单数据工厂 - 独立测试")
    print("="*60 + "\n")
    
    # 1. 初始化测试环境
    ScmPurBaseTest.setup_class()
    
    # 2. 初始化工厂
    po_factory = PurPoFactory(
        http_client=ScmPurBaseTest.http,
        apis=ScmPurBaseTest.apis,
        api_params=ScmPurBaseTest.api_params,
        mock_util=ScmPurBaseTest.mock_util,
        logger=ScmPurBaseTest.logger
    )
    
    # 3. 准备测试数据（从缓存获取）
    pur_cache = ScmPurBaseTest.pur_cache_data or {}
    vend_id = pur_cache.get("vend_info", [{}])[0].get("id", "2058001")
    pur_employee_id = pur_cache.get("pur_employee_info", [{}])[0].get("id", "14081002")
    pur_org_id = pur_cache.get("pur_org_info", [{}])[0].get("id", "14376001")
    com_org_id = pur_cache.get("com_org_info", [{}])[0].get("id", "14507001")
    inv_org_id = pur_cache.get("inv_org_info", [{}])[0].get("id", "14375002")
    inv_loc_id = pur_cache.get("inv_loc_info", [{}])[0].get("id", "14376002")
    mat_id = pur_cache.get("mat_info", [{}])[0].get("id", "14097001")
    
    # 构建物料明细
    current_ts = int(datetime.now().timestamp() * 1000)
    mat_items = [
        {
            "mat_id": mat_id,
            "mat_code": "AUTOTEST_MAT_FINP",
            "inv_org_id": inv_org_id,
            "inv_loc_id": inv_loc_id,
            "uom_pur_id": "2004001",  # 采购单位（从物料主数据获取）
            "qty": 12,
            "price": 11,
            "delivery_date": current_ts,
            "note": "执行自动化测试备注"
        },
        {
            "mat_id": "14725001",
            "mat_code": "SQWATP001",
            "inv_org_id": inv_org_id,
            "inv_loc_id": inv_loc_id,
            "uom_pur_id": "2000001",  # 采购单位（从物料主数据获取）
            "qty": 14,
            "price": 11,
            "delivery_date": current_ts,
            "note": "执行自动化测试备注"
        }
    ]
    
    # 4. 创建采购订单
    try:
        po_result = po_factory.create_standard_po(
            po_type_id="2000002",
            vend_id=vend_id,
            pur_employee_id=pur_employee_id,
            pur_org_id=pur_org_id,
            com_org_id=com_org_id,
            mat_items=mat_items
        )
        
        print("\n✅ 采购订单创建成功！")
        print(f"响应: {po_result}\n")
        
    except Exception as e:
        print(f"\n❌ 采购订单创建失败: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
