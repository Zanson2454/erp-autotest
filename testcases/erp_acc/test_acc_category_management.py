import allure
import pytest
import sys
from pathlib import Path

# 项目根目录添加路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_acc import ErpAccBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("财务模块 - 信用管理")
@allure.feature("账户类别管理")
class TestAccCategoryManagement(ErpAccBaseTest):
    """账户类别管理测试类 - 覆盖账户类别抬头CRUD和标准导入导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.category_head_id = None
        cls.parent_category_id = None  # 父类别ID，用于层级测试
        cls.logger.info("账户类别管理测试类初始化完成")
        
        # 初始化依赖数据（类别可能依赖组织、档案等）
        if cls.acc_cache_data:
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理账户类别抬头主表（注意层级删除顺序：先删子类再删父类）
            if cls.category_head_id:
                cls.db.delete(
                    table="adv_cm_acc_class_head",  # 账户类别抬头表，实际表名需确认
                    where="id = %s",
                    params=[cls.category_head_id]
                )
                cls.logger.info(f"子类别ID {cls.category_head_id} 测试数据清理完成")
            
            if cls.parent_category_id:
                cls.db.delete(
                    table="adv_cm_acc_class_head",
                    where="id = %s",
                    params=[cls.parent_category_id]
                )
                cls.logger.info(f"父类别ID {cls.parent_category_id} 测试数据清理完成")
            
            # 清理所有AT_前缀的类别（兜底清理）
            cls.db.delete(
                table="adv_cm_acc_class_head",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("账户类别测试数据清理完成")
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="账户类别管理",
        title="测试创建父账户类别",
        description="验证账户类别创建功能，支持层级结构（父类别）",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "category", "create", "parent"]
    )
    def test_save_category_parent(self):
        """测试创建父账户类别"""
        try:
            # 1. 检查基础依赖数据
            if not self.com_org_id:
                self.logger.warning("缺少组织ID依赖，跳过创建测试")
                pytest.skip("缺少组织基础数据")
            
            # 2. 准备测试数据 - 父类别
            parent_code = self.mock_util.generate_unique_code(tag="CAT_P")
            parent_name = f"自动化测试父类别_{self.mock_util.get_timestamp()}"
            parent_remark = self.mock_util.get_mock_remark()
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("SYS_CreateDataService")  # (系统)新增数据服务
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "parent_id", "org_id", "level", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            parent_data = {
                "code": parent_code,
                "name": parent_name,
                "parent_id": None,  # 顶级类别
                "org_id": self.com_org_id,
                "level": 1,  # 层级1（顶级）
                "enabled": True,
                "remark": parent_remark
            }
            ParamUtil.set_request_params(filtered_params, parent_data)
            
            # 5. 发送创建父类别请求
            response = self.http.post(url, json=filtered_params)
            
            # 6. 断言和验证
            self.assert_util.assert_response_data(response)
            data = response.get("data", {}).get("data", {})
            assert data, "创建父类别响应数据为空"
            
            self.parent_category_id = data.get("id")
            assert self.parent_category_id, "未获取到父类别ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", parent_code, "父类别编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", parent_name, "父类别名称验证失败")
            self.assert_util.assert_by_operator(data.get("parent_id"), "=", None, "父类别父ID验证失败")
            self.assert_util.assert_by_operator(data.get("level"), "=", 1, "父类别层级验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "父类别启用状态验证失败")
            
            # 7. Allure报告
            a.json(filtered_params, "创建父类别请求参数")
            a.json(response, "创建父类别响应结果")
            self.logger.info(f"父账户类别创建成功，ID: {self.parent_category_id}, Code: {parent_code}")
            
        except Exception as e:
            a.text(str(e), "创建父账户类别失败原因")
            self.logger.error(f"创建父账户类别失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试创建子账户类别",
        description="验证子账户类别创建功能，关联父类别形成层级结构",
        severity="critical",
        order=2,
        tags=["erp_acc", "category", "create", "child"]
    )
    def test_save_category_child(self):
        """测试创建子账户类别"""
        try:
            # 确保父类别存在
            if not self.parent_category_id:
                self.test_save_category_parent()
            
            # 1. 准备测试数据 - 子类别
            child_code = self.mock_util.generate_unique_code(tag="CAT_C")
            child_name = f"自动化测试子类别_{self.mock_util.get_timestamp()}"
            child_remark = self.mock_util.get_mock_remark()
            
            # 2. 获取创建API配置
            api_path = self.get_api_path("SYS_CreateDataService")  # (系统)新增数据服务
            params, url = self.get_api_params(api_path)
            
            # 3. 参数过滤和设置
            fields_to_filter = ["code", "name", "parent_id", "org_id", "level", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            child_data = {
                "code": child_code,
                "name": child_name,
                "parent_id": self.parent_category_id,  # 关联父类别
                "org_id": self.com_org_id,
                "level": 2,  # 层级2（子级）
                "enabled": True,
                "remark": child_remark
            }
            ParamUtil.set_request_params(filtered_params, child_data)
            
            # 4. 发送创建子类别请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 断言和验证
            self.assert_util.assert_response_data(response)
            data = response.get("data", {}).get("data", {})
            assert data, "创建子类别响应数据为空"
            
            self.category_head_id = data.get("id")
            assert self.category_head_id, "未获取到子类别ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", child_code, "子类别编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", child_name, "子类别名称验证失败")
            self.assert_util.assert_by_operator(data.get("parent_id"), "=", self.parent_category_id, "子类别父ID验证失败")
            self.assert_util.assert_by_operator(data.get("level"), "=", 2, "子类别层级验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "子类别启用状态验证失败")
            
            # 6. Allure报告
            a.json(filtered_params, "创建子类别请求参数")
            a.json(response, "创建子类别响应结果")
            a.text(f"层级结构: 父类别[{self.parent_category_id}] -> 子类别[{self.category_head_id}]", "层级关系")
            self.logger.info(f"子账户类别创建成功，ID: {self.category_head_id}, 父ID: {self.parent_category_id}")
            
        except Exception as e:
            a.text(str(e), "创建子账户类别失败原因")
            self.logger.error(f"创建子账户类别失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试查询账户类别列表",
        description="验证账户类别分页查询功能，支持层级过滤和树形展开",
        severity="normal",
        order=4,
        tags=["erp_acc", "category", "query"]
    )
    def test_query_category_head(self):
        """测试查询账户类别列表"""
        try:
            # 确保有测试数据（父子类别）
            if not self.category_head_id:
                self.test_save_category_child()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("SYS_PagingDataService")  # (系统)查询分页数据服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数（支持层级查询）
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [{"field": "level", "direction": "ASC"}, {"field": "code", "direction": "ASC"}],
                    "conditionItems": [
                        {"field": "org_id", "operator": "eq", "value": self.com_org_id},
                        {"field": "enabled", "operator": "eq", "value": True}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "parent_id", "type": "NUMBER"},
                    {"name": "level", "type": "NUMBER"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "org_id", "type": "NUMBER"},
                    {"name": "children_count", "type": "NUMBER"},  # 子类别数量
                    {"name": "path", "type": "TEXT"}  # 类别路径
                ],
                "systemParams": None,
                "hierarchy": {  # 层级查询配置
                    "include_children": True,  # 包含子类别
                    "max_depth": 3,            # 最大层级深度
                    "build_tree": True         # 构建树形结构
                }
            }
            
            # 添加具体条件查询测试数据
            if self.parent_category_id:
                query_params["pageable"]["conditionItems"].append(
                    {"field": "parent_id", "operator": "in", "value": [None, self.parent_category_id]}
                )
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "hierarchy"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 3. 发送查询请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证查询结果
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            
            assert total >= 2, "未查询到足够的类别记录（期望父子2条）"
            assert len(records) >= 2, "查询记录列表不足"
            
            # 验证父类别存在
            parent_found = False
            child_found = False
            for record in records:
                if record.get("id") == self.parent_category_id:
                    parent_found = True
                    self.assert_util.assert_by_operator(record.get("level"), "=", 1, "父类别层级验证失败")
                    self.assert_util.assert_by_operator(record.get("parent_id"), "=", None, "父类别父ID验证失败")
                    self.assert_util.assert_by_operator(record.get("children_count", 0), ">=", 1, "父类别子数量验证失败")
                elif record.get("id") == self.category_head_id:
                    child_found = True
                    self.assert_util.assert_by_operator(record.get("level"), "=", 2, "子类别层级验证失败")
                    self.assert_util.assert_by_operator(record.get("parent_id"), "=", self.parent_category_id, "子类别父ID验证失败")
                
                self.assert_util.assert_by_operator(record.get("enabled"), "=", True, "类别启用状态验证失败")
                self.assert_util.assert_by_operator(record.get("org_id"), "=", self.com_org_id, "组织ID验证失败")
            
            assert parent_found and child_found, "未找到测试的父子类别记录"
            
            # 如果支持树形结构，验证树节点
            if "tree_data" in query_data:
                tree_records = query_data["tree_data"]
                assert len(tree_records) >= 1, "树形数据为空"
                root_node = tree_records[0]
                self.assert_util.assert_by_operator(root_node.get("id"), "=", self.parent_category_id, "树根节点ID验证失败")
                self.assert_util.assert_by_operator(len(root_node.get("children", [])), ">=", 1, "树子节点数量验证失败")
            
            # 5. Allure报告
            a.json(filtered_params, "查询账户类别参数")
            a.json(response, "查询账户类别结果")
            a.text(f"类别层级查询: 共{total}条记录，层级1: {sum(1 for r in records if r.get('level') == 1)}, 层级2: {sum(1 for r in records if r.get('level') == 2)}", "层级统计")
            self.logger.info(f"账户类别查询成功，共{total}条记录，包含父子层级结构")
            
        except Exception as e:
            a.text(str(e), "查询账户类别失败原因")
            self.logger.error(f"查询账户类别失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试更新账户类别",
        description="验证账户类别更新功能，修改名称、层级关系和启用状态",
        severity="normal",
        order=7,
        tags=["erp_acc", "category", "update"]
    )
    def test_update_category_head(self):
        """测试更新账户类别"""
        try:
            # 确保有测试数据（子类别）
            if not self.category_head_id:
                self.test_save_category_child()
            
            # 1. 准备更新数据
            new_child_name = f"更新后子类别名称_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            new_level = 2  # 保持层级
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("SYS_UpdateDataByIdService")  # (系统)更新数据服务
            params, url = self.get_api_params(api_path)
            
            # 3. 参数设置
            update_data = {
                "id": self.category_head_id,
                "name": new_child_name,
                "parent_id": self.parent_category_id,  # 保持父关系
                "org_id": self.com_org_id,
                "level": new_level,
                "enabled": True,  # 保持启用
                "remark": new_remark
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "name", "parent_id", "org_id", "level", "enabled", "remark"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, update_data)
            
            # 4. 发送更新请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 断言验证
            self.assert_util.assert_response_success(response)
            update_result = response.get("data", {})
            assert update_result.get("success"), "更新操作未成功"
            
            # 6. 查询验证更新效果
            self.test_query_category_head()  # 重新查询验证
            
            # 7. 记录报告
            a.json(filtered_params, "更新账户类别参数")
            a.json(response, "更新账户类别结果")
            a.text(f"类别更新: 名称变更, 保持层级关系 (父ID: {self.parent_category_id})", "更新详情")
            self.logger.info(f"账户类别更新成功，ID: {self.category_head_id}, 新名称: {new_child_name}")
            
        except Exception as e:
            a.text(str(e), "更新账户类别失败原因")
            self.logger.error(f"更新账户类别失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试删除账户类别",
        description="验证单个账户类别删除功能，支持层级级联删除检查",
        severity="critical",
        order=16,
        tags=["erp_acc", "category", "delete"]
    )
    def test_delete_category_head(self):
        """测试删除账户类别"""
        try:
            # 确保有测试数据（子类别）
            if not self.category_head_id:
                self.test_save_category_child()
            
            # 1. 获取删除API配置
            api_path = self.get_api_path("SYS_DeleteDataByIdService")  # (系统)删除数据服务
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数（先删子类）
            delete_data = {"id": self.category_head_id}
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, delete_data)
            
            # 3. 发送删除子类别请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证子类别删除结果
            self.assert_util.assert_response_success(response)
            delete_result = response.get("data", {})
            assert delete_result.get("success"), "子类别删除操作失败"
            assert delete_result.get("deleted_count", 1) >= 1, "子类别删除数量异常"
            
            # 5. 验证子类别删除效果
            saved_child_id = self.category_head_id
            self.category_head_id = None
            
            # 尝试查询已删除的子类别
            api_path_query = self.get_api_path("SYS_PagingDataService")
            query_params, query_url = self.get_api_params(api_path_query)
            
            verify_query = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": saved_child_id}]
                }
            }
            
            filtered_query = ParamUtil.filter_post_body_fields(query_params, ["pageable"], ["params", "request"])
            ParamUtil.set_request_params(filtered_query, verify_query)
            
            query_response = self.http.post(query_url, json=filtered_query)
            query_records = query_response.get("data", {}).get("data", {}).get("records", [])
            
            assert len(query_records) == 0, f"子类别删除后仍能查询到 ID: {saved_child_id}"
            
            # 6. 删除父类别（如果需要完整清理）
            if self.parent_category_id:
                parent_delete_data = {"id": self.parent_category_id}
                parent_filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"]
                )
                ParamUtil.set_request_params(parent_filtered_params, parent_delete_data)
                
                parent_response = self.http.post(url, json=parent_filtered_params)
                self.assert_util.assert_response_success(parent_response)
                parent_delete_result = parent_response.get("data", {})
                assert parent_delete_result.get("success"), "父类别删除操作失败"
                assert parent_delete_result.get("cascade_deleted", 0) >= 0, "父类别级联删除异常"
            
            # 7. Allure报告
            a.json(filtered_params, "删除子账户类别参数")
            a.json(response, "删除子账户类别结果")
            if self.parent_category_id:
                a.json(parent_filtered_params, "删除父账户类别参数")
                a.json(parent_response, "删除父账户类别结果")
            a.text(f"层级删除: 子类别[{saved_child_id}] (直接删除), 父类别[{self.parent_category_id}] (可选级联)", "删除策略")
            self.logger.info(f"账户类别删除成功，子ID: {saved_child_id}")
            
        except Exception as e:
            a.text(str(e), "删除账户类别失败原因")
            self.logger.error(f"删除账户类别失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试账户类别标准导入",
        description="验证ADV_CM_ACC_CLASS_HEAD_CF_GEI_IMPORT_SERVICE标准导入服务，支持层级导入",
        severity="normal",
        order=13,
        tags=["erp_acc", "category", "import"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import_acc_class(self):
        """测试账户类别标准导入服务"""
        try:
            # 1. 获取导入API配置
            api_path = self.get_api_path("ADV_CM_ACC_CLASS_HEAD_CF_GEI_IMPORT_SERVICE")  # 账户类别抬头标准导入服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导入参数（支持层级结构导入）
            import_data = {
                "serviceKey": "ADV_CM_ACC_CLASS_HEAD_CF_GEI_IMPORT_SERVICE",
                "teamId": 22,
                "params": {
                    "taskName": f"CAT_CLASS_IMPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "filePath": "/tmp/category_hierarchy_template.xlsx",
                    "modelKey": "ADV_CM_ACC_CLASS_HEAD",
                    "importConfig": {
                        "headerRow": 1,
                        "dataStartRow": 2,
                        "fieldMapping": {
                            "code": "A",
                            "name": "B",
                            "parent_code": "C",  # 通过编码关联父类别
                            "org_id": "D",
                            "level": "E",
                            "enabled": "F",
                            "remark": "G"
                        },
                        "validationRules": {
                            "code": {"type": "STRING", "max_length": 50, "unique": True, "required": True},
                            "name": {"type": "STRING", "max_length": 100, "required": True},
                            "parent_code": {"type": "STRING", "required": False, "foreign_key": "code"},
                            "level": {"type": "NUMBER", "min": 1, "max": 5, "required": True},
                            "org_id": {"type": "NUMBER", "required": True, "foreign_key": "org.id"},
                            "enabled": {"type": "BOOLEAN", "default": True}
                        },
                        "hierarchyConfig": {  # 层级导入配置
                            "parent_field": "parent_code",
                            "auto_build_tree": True,  # 自动构建树结构
                            "validate_hierarchy": True,  # 验证层级完整性
                            "max_depth": 5,  # 最大层级深度
                            "root_level": 1  # 根节点层级
                        },
                        "defaultValues": {
                            "org_id": self.com_org_id,
                            "enabled": True,
                            "remark": "批量导入类别"
                        },
                        "relatedValidation": {
                            "parent_code": {
                                "resolve_by": "code",  # 通过编码解析父节点
                                "must_exist": True,    # 父节点必须存在
                                "circular_check": True  # 检查循环引用
                            }
                        },
                        "batchSize": 100,
                        "errorHandle": "LOG_CONTINUE",  # 记录错误继续导入
                        "duplicateHandle": "UPDATE",  # 重复更新
                        "importMode": "MERGE"  # 合并模式
                    },
                    "preImportValidation": {  # 导入前验证
                        "check_org_access": True,  # 检查组织权限
                        "validate_level_sequence": True  # 验证层级顺序
                    },
                    "postImportProcessing": {  # 导入后处理
                        "build_category_tree": True,  # 重新构建类别树
                        "update_cache": True,  # 更新缓存
                        "notify_category_change": True  # 通知类别变更
                    }
                }
            }
            
            filtered_params = params.copy()
            ParamUtil.set_request_params(filtered_params, import_data)
            
            # 3. 发送导入请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导入任务
            self.assert_util.assert_response_data(response)
            import_result = response.get("data", {})
            assert import_result.get("success"), "导入任务创建失败"
            task_id = import_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导入任务ID"
            
            # 验证导入统计
            expected_count = import_result.get("data", {}).get("expected_count", 0)
            processed_count = import_result.get("data", {}).get("processed_count", 0)
            success_count = import_result.get("data", {}).get("success_count", 0)
            error_count = import_result.get("data", {}).get("error_count", 0)
            hierarchy_valid = import_result.get("data", {}).get("hierarchy_valid", False)
            
            self.assert_util.assert_by_operator(processed_count, ">=", 0, "处理数量异常")
            self.assert_util.assert_by_operator(success_count, ">=", 0, "成功数量异常")
            self.assert_util.assert_by_operator(hierarchy_valid, "=", True, "层级结构验证失败")
            
            # 5. Allure报告
            a.json(filtered_params, "标准导入请求参数")
            a.json(response, "标准导入响应结果")
            a.text(f"类别层级导入: 预期{expected_count}条, 处理{processed_count}条, 成功{success_count}条, 错误{error_count}条, 层级有效: {hierarchy_valid}", "导入层级统计")
            self.logger.info(f"账户类别标准导入任务创建成功，Task ID: {task_id}, 层级有效: {hierarchy_valid}")
            
        except Exception as e:
            a.text(str(e), "标准导入账户类别失败原因")
            self.logger.error(f"标准导入失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试提交账户类别导入任务",
        description="验证ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST导入任务提交服务",
        severity="normal",
        order=14,
        tags=["erp_acc", "category", "import_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_import_task_class(self):
        """测试提交账户类别导入任务"""
        try:
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST")  # 账户类别抬头-导入导出任务管理接口-通过OSS提交导入任务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "IMPORT",
                "taskName": f"CAT_CLASS_IMPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_CLASS_HEAD",
                "fileInfo": {
                    "fileName": "category_hierarchy_batch.xlsx",
                    "fileSize": 102400,
                    "filePath": "/oss/category_import/hierarchy_batch.xlsx",
                    "fileType": "EXCEL",
                    "charset": "UTF-8"
                },
                "importFields": [
                    "code", "name", "parent_code", "org_id", "level", "enabled", "remark"
                ],
                "validationRules": {
                    "parent_code": {
                        "type": "STRING", 
                        "required": False,
                        "resolve_by": "code",
                        "foreign_key_validation": True
                    },
                    "level": {
                        "type": "NUMBER", 
                        "min": 1, 
                        "max": 5, 
                        "required": True,
                        "parent_level_check": True  # 父级层级验证
                    },
                    "code": {
                        "type": "STRING", 
                        "max_length": 50, 
                        "unique": True, 
                        "pattern": "^CAT_[A-Z0-9_]+$",
                        "required": True
                    },
                    "org_id": {
                        "type": "NUMBER", 
                        "required": True, 
                        "foreign_key": "org.id",
                        "access_check": True  # 权限检查
                    }
                },
                "hierarchyValidation": {  # 层级验证规则
                    "no_circular": True,       # 无循环引用
                    "level_sequence": True,    # 层级顺序正确
                    "parent_exists": True,     # 父节点存在
                    "orphan_check": True,      # 孤儿节点检查
                    "max_depth": 5             # 最大深度限制
                },
                "batchSize": 500,
                "errorHandle": "DETAILED_REPORT",  # 详细错误报告
                "duplicateHandle": "MERGE",  # 合并处理
                "importMode": "HIERARCHY_BUILD",  # 层级构建模式
                "preProcessing": {  # 前处理
                    "sort_by_level": True,  # 按层级排序导入
                    "validate_structure": True,  # 验证结构完整性
                    "build_temp_tree": True  # 构建临时树
                },
                "postProcessing": {  # 后处理
                    "rebuild_tree_index": True,  # 重建树索引
                    "update_category_cache": True,  # 更新类别缓存
                    "sync_to_related": True,  # 同步到关联模块
                    "notify_structure_change": True  # 通知结构变更
                },
                "progressTracking": {  # 进度跟踪
                    "enable": True,
                    "interval": 100,  # 每100条报告进度
                    "metrics": ["imported_count", "error_count", "hierarchy_valid"]
                }
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(task_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, task_data)
            
            # 3. 提交任务
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证任务提交
            self.assert_util.assert_response_success(response)
            task_result = response.get("data", {})
            assert task_result.get("success"), "导入任务提交失败"
            task_id = task_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导入任务ID"
            
            # 5. Allure报告
            a.json(filtered_params, "导入任务提交参数")
            a.json(response, "导入任务提交结果")
            self.logger.info(f"账户类别导入任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导入任务失败原因")
            self.logger.error(f"提交导入任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试账户类别标准导出",
        description="验证ADV_CM_ACC_CLASS_HEAD_CF_GEI_EXPORT_SERVICE标准导出服务，支持树形结构导出",
        severity="normal",
        order=10,
        tags=["erp_acc", "category", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_acc_class(self):
        """测试账户类别标准导出服务"""
        try:
            # 确保有测试数据
            if not self.category_head_id:
                self.test_save_category_child()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_ACC_CLASS_HEAD_CF_GEI_EXPORT_SERVICE")  # 账户类别抬头标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数（支持树形结构）
            export_data = {
                "serviceKey": "ADV_CM_ACC_CLASS_HEAD_CF_GEI_EXPORT_SERVICE",
                "teamId": 22,
                "params": {
                    "taskName": f"CAT_CLASS_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_ACC_CLASS_HEAD",
                            "modelName": "账户类别配置",
                            "sheetNo": 0,
                            "sheetName": "类别层级列表",
                            "headerConfigList": [
                                {"name": "类别ID", "type": "TEXT", "field": "id"},
                                {"name": "类别编码", "type": "TEXT", "field": "code"},
                                {"name": "类别名称", "type": "TEXT", "field": "name"},
                                {"name": "父类别ID", "type": "NUMBER", "field": "parent_id"},
                                {"name": "父类别编码", "type": "TEXT", "field": "parent_code"},
                                {"name": "层级", "type": "NUMBER", "field": "level"},
                                {"name": "组织ID", "type": "NUMBER", "field": "org_id"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "enabled"},
                                {"name": "子类别数量", "type": "NUMBER", "field": "children_count"},
                                {"name": "类别路径", "type": "TEXT", "field": "path"},
                                {"name": "创建时间", "type": "DATETIME", "field": "create_time"},
                                {"name": "更新时间", "type": "DATETIME", "field": "update_time"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_CLASS_HIERARCHY",
                            "modelName": "类别层级关系",
                            "sheetNo": 1,
                            "sheetName": "层级关系",
                            "headerConfigList": [
                                {"name": "子类别ID", "type": "NUMBER", "field": "child_id"},
                                {"name": "父类别ID", "type": "NUMBER", "field": "parent_id"},
                                {"name": "层级差", "type": "NUMBER", "field": "level_diff"},
                                {"name": "关系类型", "type": "TEXT", "field": "relation_type"},
                                {"name": "路径标识", "type": "TEXT", "field": "path_id"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_ACC_CLASS",
                        "viewKey": "ADV_CM_ACC_CLASS_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_CLASS_HEAD",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 1000,  # 导出时取较多数据
                                    "needTotal": True,
                                    "sortOrders": [
                                        {"field": "level", "direction": "ASC"},
                                        {"field": "parent_id", "direction": "ASC"},
                                        {"field": "code", "direction": "ASC"}
                                    ],
                                    "conditionItems": [
                                        {"field": "org_id", "operator": "eq", "value": self.com_org_id},
                                        {"field": "enabled", "operator": "eq", "value": True}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "parent_id"}, {"field": "level"}, {"field": "org_id"},
                                {"field": "enabled"}, {"field": "children_count"}, {"field": "path"},
                                {"field": "create_time"}, {"field": "update_time"}, {"field": "remark"}
                            ],
                            "modelKey": "ADV_CM_ACC_CLASS_HEAD",
                            "hierarchy": {
                                "include_children": True,
                                "build_path": True,  # 构建完整路径
                                "max_depth": 5,
                                "root_filter": {"parent_id": None}  # 根节点过滤
                            }
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_ACC_CLASS_HEAD",
                        "modelName": "账户类别配置",
                        "containerKey": "ADV_CM_ACC_CLASS",
                        "viewKey": "ADV_CM_ACC_CLASS_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_CLASS_HEAD",
                        "dataTransform": {
                            "path": "build_hierarchy_path",  # 构建层级路径
                            "children_count": "recursive_count",  # 递归统计子节点
                            "level": "calculate_from_parent",  # 从父级计算层级
                            "parent_code": "resolve_by_id"  # 通过ID解析父编码
                        },
                        "exportOptions": {
                            "tree_structure": True,  # 导出树形结构
                            "indentation": 2,  # 缩进显示层级
                            "include_hierarchy_relations": True,  # 包含层级关系
                            "format_for_excel": True  # Excel格式优化
                        }
                    }
                }
            }
            
            filtered_params = params.copy()
            ParamUtil.set_request_params(filtered_params, export_data)
            
            # 3. 发送导出请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导出任务
            self.assert_util.assert_response_data(response)
            export_result = response.get("data", {})
            assert export_result.get("success"), "导出任务创建失败"
            task_id = export_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导出任务ID"
            
            # 5. Allure报告
            a.json(filtered_params, "标准导出请求参数")
            a.json(response, "标准导出响应结果")
            a.text(f"导出配置: {expected_sheets}个工作表 (抬头+规则+事件)", "导出结构")
            self.logger.info(f"账户类别标准导出任务创建成功，Task ID: {task_id}, 工作表: {expected_sheets}")
            
        except Exception as e:
            a.text(str(e), "标准导出账户类别失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类别管理",
        title="测试提交账户类别导出任务",
        description="验证ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "category", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task_class(self):
        """测试提交账户类别导出任务"""
        try:
            # 确保有测试数据
            if not self.category_head_id:
                self.test_save_category_child()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_CLASS_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST")  # 账户类别抬头-导入导出任务管理接口-提交导出任务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"CAT_CLASS_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_CLASS_HEAD",
                "filterCondition": {
                    "enabled": True,
                    "level": {"min": 1, "max": 3}
                },
                "exportFields": ["id", "code", "name", "parent_id", "level", "org_id", "enabled"],
                "expandFields": ["children"],  # 导出时展开子类别
                "exportFormat": "EXCEL",
                "includeHeader": True,
                "separateSheets": True  # 条件明细单独工作表
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(task_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, task_data)
            
            # 3. 提交任务
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证任务提交
            self.assert_util.assert_response_success(response)
            task_result = response.get("data", {})
            assert task_result.get("success"), "导出任务提交失败"
            task_id = task_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导出任务ID"
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            self.logger.info(f"账户类别导出任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    def _get_current_category_info(self):
        """辅助方法：获取当前账户类别信息"""
        try:
            api_path = self.get_api_path("SYS_PagingDataService")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.category_head_id}]
                },
                "fields": [
                    {"name": "name", "type": "TEXT"},
                    {"name": "parent_id", "type": "NUMBER"},
                    {"name": "level", "type": "NUMBER"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "children_count", "type": "NUMBER"},
                    {"name": "path", "type": "TEXT"}
                ],
                "hierarchy": {"include_children": False}  # 不展开子节点
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["pageable", "fields", "hierarchy"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, query_params)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            records = response.get("data", {}).get("data", {}).get("records", [])
            if records:
                return records[0]
            return {}
            
        except Exception as e:
            self.logger.error(f"获取类别信息失败: {str(e)}")
            return {}
