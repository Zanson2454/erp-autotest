"""
移动凭证创建器
提供采购、销售、调拨等不同类型移动凭证的创建功能
"""
import datetime
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil


class MobileVoucherCreator(ScmInvBaseTest):
    """移动凭证创建器"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        # 初始化必要的ID属性
        if cls.inv_cache_data:
            # 组织信息
            org_info = cls.inv_cache_data.get("org_info", {})
            cls.comOrgId = org_info.get("gr_come_org_info", [{}])[0].get("id")
            cls.invOrgId = org_info.get("inv_org_info", [{}])[0].get("id")
            cls.invLocId = org_info.get("inv_loc_info", [{}])[0].get("id")
            
            # 仓库信息
            inv_bin_rec = org_info.get("inv_bin_rec_md", [{}])[0]
            cls.invWhId = inv_bin_rec.get("inv_wh_id")
            cls.invAreaId = inv_bin_rec.get("inv_area_id") 
            cls.invBinId = inv_bin_rec.get("id")
            
            # 单位信息 - 从初始化数据中获取
            cls.unitId = cls.init_data["uom_info"]["qty_uom_info"][0]["uom_id"] if cls.init_data.get("uom_info", {}).get("qty_uom_info") else None
            
            cls.logger.info(f"移动凭证创建器初始化完成 - 组织ID: {cls.comOrgId}, 库存组织: {cls.invOrgId}")
        else:
            cls.logger.error("inv_cache_data 未找到，无法初始化必要属性")
            raise RuntimeError("缓存数据未找到，请检查数据初始化")
    
    def create_purchase_voucher(
        self, 
        mat_id=None,     # 可选：物料ID，不传则使用默认成品物料
        qty=1,           # 必填：数量
        mvmTypeId=None,  # 可选：移动类型ID，不传则使用采购类型
        comOrgId=None,   # 可选：公司组织ID，不传则使用默认
        invOrgId=None,   # 可选：库存组织ID，不传则使用默认
        invLocId=None,   # 可选：库存地点ID，不传则使用默认
        invWhId=None,    # 可选：仓库ID
        invAreaId=None,  # 可选：仓储区ID  
        invBinId=None,   # 可选：仓位ID
        batch_code=None, # 可选：批次编码，不传则自动生成
        remark=None,     # 可选：备注
        mat_items=None   # 可选：多物料行 [{"mat_id": xx, "qty": xx}, ...]
    ):
        """创建采购入库移动凭证"""
        try:
            # 参数默认值处理
            mvmTypeId = mvmTypeId or self.inv_cache_data["org_info"]["inv_mvm_type_cf_pur"][0]["id"]
            comOrgId, invOrgId, invLocId = self._get_default_org_params(comOrgId, invOrgId, invLocId)
            
            # 处理物料行数据
            in_items, total_qty = self._build_voucher_items(
                mat_items, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                invWhId, invAreaId, invBinId, "purchase", batch_code=batch_code
            )
            
            # 创建凭证
            result = self._create_voucher(
                mvmTypeId=mvmTypeId,
                comOrgId=comOrgId,
                show_type="IN",
                remark=remark or f"自动化测试采购入库-{self.mock_util.get_timestamp()}",
                in_items=in_items
            )
            
            result.update({
                "batch_code": batch_code if not mat_items else None,
                "voucher_type": "purchase",
                "total_qty": total_qty,
                "item_count": len(in_items)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建采购入库移动凭证失败: {str(e)}")
            raise
    def create_sale_voucher(
        self,
        mat_id=None,         # 可选：物料ID，不传则使用默认成品物料
        qty=1,               # 必填：数量
        mvmTypeId=None,      # 可选：移动类型ID，不传则使用销售类型
        comOrgId=None,       # 可选：公司组织ID，不传则使用默认
        invOrgId=None,       # 可选：库存组织ID，不传则使用默认
        invLocId=None,       # 可选：库存地点ID，不传则使用默认
        invWhId=None,        # 可选：仓库ID
        invAreaId=None,      # 可选：仓储区ID  
        invBinId=None,       # 可选：仓位ID
        batch_id=None,       # 可选：批次ID，物料需要批次时必须传入
        remark=None,         # 可选：备注
        mat_items=None       # 可选：多物料行 [{"mat_id": xx, "qty": xx, "batch_id": xx}, ...]
    ):
        """创建销售出库移动凭证"""
        try:
            # 参数默认值处理
            mvmTypeId = mvmTypeId or self.inv_cache_data["org_info"]["inv_mvm_type_cf_sls"][0]["id"]
            comOrgId, invOrgId, invLocId = self._get_default_org_params(comOrgId, invOrgId, invLocId)
            
            # 处理物料行数据
            out_items, total_qty = self._build_voucher_items(
                mat_items, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                invWhId, invAreaId, invBinId, "sale", batch_id=batch_id
            )
            
            # 创建凭证
            result = self._create_voucher(
                mvmTypeId=mvmTypeId,
                comOrgId=comOrgId,
                show_type="OUT",
                remark=remark or f"自动化测试销售出库-{self.mock_util.get_timestamp()}",
                out_items=out_items
            )
            
            result.update({
                "batch_id": batch_id if not mat_items else None,
                "voucher_type": "sale",
                "total_qty": total_qty,
                "item_count": len(out_items)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建销售出库移动凭证失败: {str(e)}")
            raise
    
    def create_transfer_voucher(
        self,
        mat_id=None,         # 可选：物料ID，不传则使用默认成品物料
        qty=1,               # 必填：数量
        mvmTypeId=None,      # 可选：移动类型ID，不传则使用调拨类型
        comOrgId=None,       # 可选：公司组织ID，不传则使用默认
        invOrgId=None,       # 可选：库存组织ID，不传则使用默认
        invLocId=None,       # 可选：库存地点ID，不传则使用默认
        from_batch_id=None,  # 可选：出库批次ID，如果物料需要批次管理且不传则自动查找
        to_batch_code=None,  # 可选：入库批次编码，不传则自动生成
        from_wh_info=None,   # 可选：出库仓库信息 {"invWhId": xx, "invAreaId": xx, "invBinId": xx}
        to_wh_info=None,     # 可选：入库仓库信息 {"invWhId": xx, "invAreaId": xx, "invBinId": xx}
        remark=None          # 可选：备注
    ):
        """创建调拨移动凭证（一出一入）"""
        try:
            # 参数默认值处理
            mat_id = mat_id or self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            mvmTypeId = mvmTypeId or self.inv_cache_data["org_info"]["inv_mvm_type_cf_all"][0]["id"]
            comOrgId, invOrgId, invLocId = self._get_default_org_params(comOrgId, invOrgId, invLocId)
            
            # 处理出库批次：如果需要批次且未指定，自动查找可用批次
            if not from_batch_id and self._check_need_batch(mat_id):
                available_batches = self.get_available_batches(mat_id, invOrgId, invLocId)
                if not available_batches:
                    raise ValueError(f"物料{mat_id}没有可用批次进行调拨出库")
                from_batch_id = available_batches[0]["id"]
            
            # 构建出库明细（复用销售出库逻辑）
            out_items, _ = self._build_voucher_items(
                None, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                from_wh_info.get("invWhId") if from_wh_info else None,
                from_wh_info.get("invAreaId") if from_wh_info else None,
                from_wh_info.get("invBinId") if from_wh_info else None,
                "sale", batch_id=from_batch_id
            )
            
            # 构建入库明细（复用采购入库逻辑）
            in_items, total_qty = self._build_voucher_items(
                None, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                to_wh_info.get("invWhId") if to_wh_info else None,
                to_wh_info.get("invAreaId") if to_wh_info else None,
                to_wh_info.get("invBinId") if to_wh_info else None,
                "purchase", batch_code=to_batch_code
            )
            
            # 创建凭证
            result = self._create_voucher(
                mvmTypeId=mvmTypeId,
                comOrgId=comOrgId,
                show_type="ALL",
                remark=remark or f"自动化测试调拨-{self.mock_util.get_timestamp()}",
                in_items=in_items,
                out_items=out_items
            )
            
            result.update({
                "from_batch_id": from_batch_id,
                "to_batch_code": to_batch_code,
                "voucher_type": "transfer",
                "total_qty": total_qty,
                "item_count": 1
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建调拨移动凭证失败: {str(e)}")
            raise
    
    def create_special_stock_transfer_voucher(
        self,
        mat_id=None,         # 可选：物料ID，不传则使用默认成品物料
        qty=1,               # 必填：数量
        mvmTypeId=None,      # 可选：移动类型ID，不传则使用特殊库存转移类型
        comOrgId=None,       # 可选：公司组织ID，不传则使用默认
        invOrgId=None,       # 可选：库存组织ID，不传则使用默认
        invLocId=None,       # 可选：库存地点ID，不传则使用默认
        from_batch_id=None,  # 可选：出库批次ID，如果物料需要批次管理且不传则自动查找
        to_batch_code=None,  # 可选：入库批次编码，不传则自动生成
        from_wh_info=None,   # 可选：出库仓库信息 {"invWhId": xx, "invAreaId": xx, "invBinId": xx}
        to_wh_info=None,     # 可选：入库仓库信息 {"invWhId": xx, "invAreaId": xx, "invBinId": xx}
        remark=None          # 可选：备注
    ):
        """创建特殊库存转移移动凭证（一出一入，入库带特殊库存标识）"""
        try:
            # 参数默认值处理
            mat_id = mat_id or self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            mvmTypeId = mvmTypeId or self.inv_cache_data["org_info"]["inv_mvm_type_cf_spc_stk_transfer"][0]["id"]
            comOrgId, invOrgId, invLocId = self._get_default_org_params(comOrgId, invOrgId, invLocId)
            
            # 从缓存获取特殊库存参数
            spc_stk_type_info = self.inv_cache_data["org_info"]["inv_spc_stk_type_cf_spc_stk_transfer"][0]
            vend_info = self.inv_cache_data["partner_info"]["vend_info"][0]
            
            # 处理出库批次：如果需要批次且未指定，自动查找可用批次
            if not from_batch_id and self._check_need_batch(mat_id):
                available_batches = self.get_available_batches(mat_id, invOrgId, invLocId)
                if not available_batches:
                    raise ValueError(f"物料{mat_id}没有可用批次进行特殊库存转移出库")
                from_batch_id = available_batches[0]["id"]
            
            # 构建出库明细（复用销售出库逻辑）
            out_items, _ = self._build_voucher_items(
                None, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                from_wh_info.get("invWhId") if from_wh_info else None,
                from_wh_info.get("invAreaId") if from_wh_info else None,
                from_wh_info.get("invBinId") if from_wh_info else None,
                "sale", batch_id=from_batch_id
            )
            
            # 构建入库明细（使用特殊库存入库逻辑）
            in_items, total_qty = self._build_voucher_items(
                None, mat_id, qty, mvmTypeId, invOrgId, invLocId,
                to_wh_info.get("invWhId") if to_wh_info else None,
                to_wh_info.get("invAreaId") if to_wh_info else None,
                to_wh_info.get("invBinId") if to_wh_info else None,
                "purchase", batch_code=to_batch_code
            )
            
            # 为入库明细添加特殊库存相关字段
            for in_item in in_items:
                in_item["spcStkTypeId"] = {
                    "code": "V",
                    "name": spc_stk_type_info["name"],
                    "modelKey": "pur_vend_info_md",
                    "isPushInvValue": True,
                    "id": spc_stk_type_info["id"]
                }
                in_item["spcStkTypeClass"] = vend_info["id"]
                in_item["spcStkTypeClassName"] = vend_info["name"]
            
            # 创建凭证
            result = self._create_voucher(
                mvmTypeId=mvmTypeId,
                comOrgId=comOrgId,
                show_type="ALL",
                remark=remark or f"自动化测试特殊库存转移-{self.mock_util.get_timestamp()}",
                in_items=in_items,
                out_items=out_items
            )
            
            result.update({
                "from_batch_id": from_batch_id,
                "to_batch_code": to_batch_code,
                "voucher_type": "special_stock_transfer",
                "total_qty": total_qty,
                "item_count": 1,
                "spc_stk_type_id": spc_stk_type_info["id"],
                "spc_stk_type_class": vend_info["id"],
                "spc_stk_type_class_name": vend_info["name"]
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"创建特殊库存转移移动凭证失败: {str(e)}")
            raise
    
    def _get_default_org_params(self, comOrgId, invOrgId, invLocId):
        """获取默认的组织参数"""
        return (
            comOrgId or self.comOrgId,
            invOrgId or self.invOrgId,
            invLocId or self.invLocId
        )
    
    def _build_voucher_items(self, mat_items, mat_id, qty, mvmTypeId, invOrgId, invLocId, 
                           invWhId, invAreaId, invBinId, voucher_type, batch_code=None, batch_id=None):
        """构建凭证物料行数据"""
        items = []
        total_qty = 0
        
        if mat_items:
            # 多物料行模式
            for index, item in enumerate(mat_items, 1):
                item_mat_id = item.get("mat_id")
                item_qty = item.get("qty", 1)
                total_qty += item_qty
                
                if voucher_type == "purchase":
                    voucher_item = self._build_purchase_item(
                        mat_id=item_mat_id, qty=item_qty, mvmTypeId=mvmTypeId,
                        invOrgId=invOrgId, invLocId=invLocId,
                        invWhId=invWhId, invAreaId=invAreaId, invBinId=invBinId
                    )
                else:  # sale
                    item_batch_id = item.get("batch_id")
                    voucher_item = self._build_sale_item(
                        mat_id=item_mat_id, qty=item_qty, mvmTypeId=mvmTypeId,
                        invOrgId=invOrgId, invLocId=invLocId,
                        invWhId=invWhId, invAreaId=invAreaId, invBinId=invBinId,
                        batch_id=item_batch_id, ref_code=str(index)
                    )
                items.append(voucher_item)
        else:
            # 单物料行模式
            mat_id = mat_id or self.inv_cache_data["mat_info"]["mat_md"]["FINP"][0]["id"]
            total_qty = qty
            
            if voucher_type == "purchase":
                voucher_item = self._build_purchase_item(
                    mat_id=mat_id, qty=qty, mvmTypeId=mvmTypeId,
                    invOrgId=invOrgId, invLocId=invLocId,
                    invWhId=invWhId, invAreaId=invAreaId, invBinId=invBinId,
                    batch_code=batch_code
                )
            else:  # sale
                voucher_item = self._build_sale_item(
                    mat_id=mat_id, qty=qty, mvmTypeId=mvmTypeId,
                    invOrgId=invOrgId, invLocId=invLocId,
                    invWhId=invWhId, invAreaId=invAreaId, invBinId=invBinId,
                    batch_id=batch_id
                )
            items.append(voucher_item)
        
        return items, total_qty
    
    def get_available_batches(self, mat_id, inv_org_id, inv_loc_id):
        """
        查询可用批次
        
        :param mat_id: 物料ID
        :param inv_org_id: 库存组织ID
        :param inv_loc_id: 库存地点ID
        :return: 可用批次列表
        """
        try:
            # 查询库存余额表获取有库存的批次
            sql = """
                SELECT b.id, b.code, sb.stk_qty 
                FROM inv_batch_tr b
                JOIN inv_stk_ba sb ON b.id = sb.batch_id
                WHERE sb.mat_id = %s 
                AND sb.inv_org_id = %s 
                AND sb.inv_loc_id = %s 
                AND sb.stk_qty > 0
                ORDER BY b.created_at DESC
            """
            result = self.db.query(sql, params=[mat_id, inv_org_id, inv_loc_id])
            
            batches = []
            for row in result:
                batches.append({
                    "id": row.get("id"),
                    "code": row.get("code"),
                    "stk_qty": row.get("stk_qty")
                })
            
            return batches
            
        except Exception as e:
            self.logger.error(f"查询可用批次失败: {str(e)}")
            return []
    
    def _check_need_batch(self, mat_id):
        """检查物料是否需要批次管理"""
        try:
            # 简化判断：如果物料编码包含"FINP"则需要批次（根据你的测试数据）
            mat_info = self.db.query(
                "SELECT mat_code FROM gen_mat_md WHERE id = %s", 
                params=[mat_id]
            )
            if mat_info:
                mat_code = mat_info[0].get("mat_code", "")
                return "FINP" in mat_code or "AUTOTEST_MAT_FINP" in mat_code
            return False
        except Exception as e:
            self.logger.warning(f"检查批次需求失败，默认不需要批次: {str(e)}")
            return False
    
    def _generate_batch_code(self):
        """生成批次编码（确保唯一性）"""
        import time
        import random
        # 使用时间戳 + 随机数确保唯一性
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        random_suffix = random.randint(100, 999)
        return f"SQW{timestamp}{random_suffix}"
    
    def _get_batch_info(self, mat_id):
        """获取物料批次特性信息"""
        try:
            api_path = self.get_api_path("INV-批次-查询物料的批次特征服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = {
                "params": {
                    "request": {
                        "matId": mat_id,
                        "invOrgId": self.invOrgId,
                        "invLocId": self.invLocId
                    }
                }
            }
            
            response = self.http.post(url, json=filtered_params)
            if response.get("success"):
                return response.get("data", {}).get("data", {})
            return {}
        except Exception as e:
            self.logger.warning(f"获取批次特性信息失败: {str(e)}")
            return {}
    
    def _get_batch_detail(self, batch_id):
        """获取批次详细信息"""
        try:
            # 销售出库：直接引用现有批次ID
            return {"id": batch_id}
        except Exception as e:
            self.logger.warning(f"获取批次详细信息失败: {str(e)}")
            return {"id": batch_id}
    
    def _build_purchase_item(self, mat_id, qty, mvmTypeId, invOrgId=None, invLocId=None, invWhId=None, invAreaId=None, invBinId=None, batch_code=None):
        """构建采购入库明细（包含批次处理）"""
        # 构建基础明细
        in_item = self._build_move_item(mat_id, qty, mvmTypeId, invOrgId, invLocId, invWhId, invAreaId, invBinId)
        
        # 处理批次信息
        need_batch = self._check_need_batch(mat_id)
        if need_batch:
            batch_code = batch_code or self._generate_batch_code()
            batch_info = self._get_batch_info(mat_id)
            if batch_info:
                in_item["batchId"] = {
                    "batchType": "INBOUND",
                    "batchCode": batch_code,
                    "charaClassId": batch_info.get("charaClassId"),
                    "quantity": qty,
                    "charaValue": batch_info.get("batchCharaValueList", [])
                }
        
        return in_item

    def _build_sale_item(self, mat_id, qty, mvmTypeId, invOrgId=None, invLocId=None, invWhId=None, invAreaId=None, invBinId=None, batch_id=None, ref_code="1"):
        """构建销售出库明细（包含批次处理）"""
        # 构建基础明细
        out_item = self._build_move_item(mat_id, qty, mvmTypeId, invOrgId, invLocId, invWhId, invAreaId, invBinId, ref_code)
        
        # 处理批次信息（销售出库：引用现有批次）
        if batch_id:
            batch_detail = self._get_batch_detail(batch_id)
            out_item["batchId"] = batch_detail
        
        return out_item

    def _build_move_item(self, mat_id, qty, mvmTypeId, invOrgId=None, invLocId=None, invWhId=None, invAreaId=None, invBinId=None, ref_code="1"):
        """构建移动明细基础信息"""
        # 使用传入的参数，如果没有传入则使用默认值
        invOrgId = invOrgId or self.invOrgId
        invLocId = invLocId or self.invLocId
        
        item = {
            "matId": {"id": mat_id},
            "mvmQty": qty,
            "refCode": ref_code,
            "mvmTypeId": {"id": mvmTypeId},
            "unitId": {"id": self.unitId},
            "invOrgId": {"id": invOrgId},
            "invLocId": {"id": invLocId}
        }
        
        # 添加仓库信息（可选）
        if invWhId:
            item["invWhId"] = {"id": invWhId}
        if invAreaId:
            item["invAreaId"] = {"id": invAreaId}
        if invBinId:
            item["invBinId"] = {"id": invBinId}
            
        return item
    
    def verify_voucher_in_list(self, voucher_id):
        """验证移动凭证是否在列表中"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("INV-移动凭证-分页查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["moveVoucherId"], ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "moveVoucherId", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 3. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 4. 查找目标凭证
            vouchers = response.get("data", {}).get("data", {}).get("data", [])
            for voucher in vouchers:
                if voucher.get("id") == voucher_id:
                    return voucher
            
            raise AssertionError(f"移动凭证ID {voucher_id} 未在列表中找到")
            
        except Exception as e:
            self.logger.error(f"验证移动凭证列表失败: {str(e)}")
            raise

    def _create_voucher(self, mvmTypeId, show_type, remark, comOrgId=None, in_items=None, out_items=None):
        """创建移动凭证的通用方法"""
        # 生成请求数据
        doc_time = int(datetime.datetime.now().timestamp() * 1000)
        request_no = self.mock_util.generate_unique_code(tag="REQ")
        
        # 使用传入的comOrgId，如果没有传入则使用默认值
        final_comOrgId = comOrgId if comOrgId is not None else self.comOrgId
        
        # 构建请求参数
        api_path = self.get_api_path("INV-移动凭证-新版创建服务")
        params, url = self.get_api_params(api_path)
        
        request_data = {
            "comOrgId": {"id": final_comOrgId},
            "mvmTypeId": {"id": mvmTypeId},
            "showType": show_type,
            "mvmDocTimePst": doc_time,
            "remark": remark,
            "requestNo": request_no
        }
        
        if in_items:
            request_data["mvmDocInList"] = in_items
        if out_items:
            request_data["mvmDocOutList"] = out_items
        
        filtered_params = {"params": {"request": request_data}}
        
        # 发送请求
        response = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_data(response)
        
        # 返回结果
        voucher_data = response.get("data", {}).get("data", {})
        return {
            "mobile_voucher_id": voucher_data.get("moveVoucherId"),
            "mobile_voucher_code": voucher_data.get("moveVoucherCode"),
            "qty": sum(item["mvmQty"] for item in (in_items or [])),
            "response": response,
            "request_params": filtered_params
        }
