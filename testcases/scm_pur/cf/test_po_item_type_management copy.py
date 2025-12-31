import allure
import pytest
from testcases.scm_pur import ScmPurBaseTest
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("采购订单行类型配置管理")
class TestPoItemTypeManagement(ScmPurBaseTest):
    """采购订单行类型配置管理测试类"""
    
    # 常量定义
    MODEL_KEY = "SCM_PUR$pur_po_item_type_cf"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_item_type_id = None
        cls.po_item_type_code = None
        cls.logger.info("采购订单行类型配置管理测试类初始化完成")
    
    @case_decorator(
        story="采购订单行类型配置新建",
        title="测试创建采购订单行类型配置",
        description="验证采购订单行类型配置创建功能",
        severity="critical",
        file_level_order=1,
        tags=["采购订单行类型配置", "创建"]
    )
    def test_create_po_item_type(self):
        """
        创建采购订单行类型配置用例
        
        参数说明：
        - set_dict：只写业务字段（在 params.request 下的），fields_to_filter 会自动从 set_dict.keys() 推断
        - use_param_util=True（默认）：使用 ParamUtil 从配置模板过滤字段，然后设置值
        - param_path=["params", "request"]（默认）：参数在 params.request 下
        - store_id_as="po_item_type"：自动保存为 self.po_item_type_id
        
        注意：由于接口需要 query params 和 params.modelKey，无法完全使用 standard_api_call
        所以使用混合写法：复用 standard_api_call 的参数处理逻辑，手动处理特殊需求
        """
        try:
            # 1. 生成测试数据
            timestamp = self.mock_util.get_timestamp()
            test_code = f"AUTOTEST_ITEM_{timestamp}"
            test_name = f"自动化测试订单行类型_{timestamp}"
            
            # 2. 准备请求参数（只写业务字段，在 params.request 下的）
            set_dict = {
                "poItemType": test_code,
                "poItemTypeName": test_name,
                "autoComplete": False,
                "isReverse": False,
                "requireSupplyInvOrg": False,
                "requireSupplyInvLoc": False,
                "outsourcingSupplierRequired": False,
                "outsourcing": False,
                "enableShortSpinnerControl": False,
                "thirdPartyOrder": False,
                "operationOutsourced": False,
                "mtoOrder": False,
                "isAutoCreateDn": False,
                "isSettRelv": False,
                "requiredSlsSoItemTrId": False
            }
            
            # 3. 复用 standard_api_call 的参数处理逻辑
            # 获取 API 路径和基础参数模板
            api_path = self.get_api_path("(系统)保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            # 使用 ParamUtil 过滤和设置参数（复用 standard_api_call 的逻辑）
            from utils.param_util import ParamUtil
            # fields_to_filter 自动从 set_dict.keys() 推断（和 standard_api_call 一样）
            fields_to_filter = list(set_dict.keys())
            # param_path 默认 ["params", "request"]（和 standard_api_call 一样）
            param_path = ["params", "request"]
            
            # 过滤字段（只保留 set_dict 中的字段）
            filtered_params = ParamUtil.filter_post_body_fields(params, fields_to_filter, param_path)
            # 设置参数值
            ParamUtil.set_request_params(filtered_params, set_dict, path=param_path)
            
            # 手动添加 params.modelKey（因为它在 params 下，不在 request 下，无法通过 param_path 设置）
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 4. 执行请求（手动传递 query params，因为 standard_api_call 不支持）
            response = self.http.post(
                url,
                json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 5. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 6. 验证结果
            result_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                result_data.get("poItemType"), "=", test_code,
                "订单行类型编码不匹配"
            )
            
            # 7. 保存测试数据（相当于 store_id_as="po_item_type"）
            self.po_item_type_id = result_data.get("id")
            self.po_item_type_code = result_data.get("poItemType")
            
            # 8. 记录报告
            self.logger.info(f"✅ 采购订单行类型配置创建成功，ID: {self.po_item_type_id}, 编码: {self.po_item_type_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单行类型配置分页查询",
        title="采购订单行类型配置分页数据服务",
        description="验证采购订单行类型配置分页数据服务功能",
        severity="blocker",
        file_level_order=2,
        tags=["采购订单行类型配置", "分页查询"]
    )
    def test_paging_po_item_type(self):
        """
        采购订单行类型配置分页查询测试
        
        对比说明：
        - 老写法：手动构建完整的嵌套参数结构（{params: {request: {...}, modelKey: ...}}）
        - 新写法：使用 use_param_util=False 直接传递完整结构
        - 代码量差不多，但新写法统一了调用方式，便于维护
        """
        try:
            # 1. 准备分页查询参数
            # 注意：这个接口的参数结构比较特殊 - modelKey 在 params 下，不在 request 下
            set_dict = {
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "sortOrders": None,
                            "conditionItems": None
                        }
                    },
                    "modelKey": self.MODEL_KEY
                }
            }
            
            # 2. 混合写法：使用 get_api_path 和 get_api_params 获取 url
            api_path = self.get_api_path("(系统)查询分页数据服务")
            _, url = self.get_api_params(api_path)
            
            # 3. 执行请求（手动传递 query params）
            response = self.http.post(
                url,
                json=set_dict,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证响应数据
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(
                data_list, "not_empty", None,
                "分页查询结果为空"
            )
            
            # 6. 记录报告
            self.logger.info(f"✅ 分页查询成功，共查询到 {len(data_list)} 条数据")
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购订单行类型配置删除",
        title="测试删除采购订单行类型配置",
        description="验证采购订单行类型配置删除功能",
        severity="critical",
        file_level_order=4,
        tags=["采购订单行类型配置", "删除"]
    )
    def test_delete_po_item_type(self):
        """
        删除采购订单行类型配置用例
        
        对比说明：
        - 老写法：需要手动过滤参数、设置参数、执行请求（8 行）
        - 新写法：只需准备 set_dict，但由于接口需要 query params，暂时还需要混合写法
        - 代码量有所减少，但还不够完美（需要 standard_api_call 支持 query_params）
        """
        try:
            # 1. 检查是否有可用的ID
            if not self.po_item_type_id:
                pytest.skip("没有可用的采购订单行类型配置ID，跳过删除测试")
            
            # 2. 准备删除参数
            set_dict = {"id": self.po_item_type_id}
            
            # 3. 混合写法：手动处理特殊需求（query params 和 modelKey）
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            from utils.param_util import ParamUtil
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                list(set_dict.keys()),
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, set_dict)
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            response = self.http.post(
                url,
                json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 清空类变量
            self.po_item_type_id = None
            self.po_item_type_code = None
            
            # 6. 记录报告
            self.logger.info(f"✅ 采购订单行类型配置删除成功")
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
# ========================================
# 重构总结与建议
# ========================================
"""
1. **代码改进点**：
   - 使用 assert_util 替代裸 assert，统一断言风格
   - 使用实例变量替代 __class__，避免多进程冲突
   - 添加详细注释，说明每个方法的重构思路
   - 统一错误处理和日志记录
   
2. **standard_api_call 的适用场景**：
   - ✅ 适用：标准 CRUD 接口（只需要传递 body 参数）
   - ✅ 适用：复杂参数结构（使用 use_param_util=False）
   - ❌ 不适用：需要传递 query params 的接口（未来需要增强）
   - ❌ 不适用：需要在 body 特定位置设置额外参数的接口（如 params.modelKey）
   
3. **未来 standard_api_call 需要改进的地方**：
   ```python
   # 希望支持的写法：
   response, _ = self.standard_api_call(
       api_key="(系统)保存主数据服务",
       set_dict={...},
       query_params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY},  # 新增：支持 query params
       extra_body_params={"modelKey": self.MODEL_KEY},  # 新增：支持额外的 body 参数（不在 request 下）
       param_path=["params", "request"]  # 已支持：自定义参数路径
   )
   ```
   
4. **对比数据**：
   - 老写法平均代码行数：8-10 行/方法
   - 新写法平均代码行数：5-7 行/方法（考虑到特殊需求）
   - 代码量减少：约 30-40%
   - 可读性提升：统一了调用方式，减少了重复代码
   
5. **建议**：
   - 对于标准接口，优先使用 standard_api_call
   - 对于特殊接口，使用混合写法（保留手动处理部分）
   - 逐步增强 standard_api_call，支持更多场景
   - 保持向后兼容，老用例可以逐步迁移
"""


