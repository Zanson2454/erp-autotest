"""移动类型配置的新增、查询、详情、删除测试"""
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("库存管理")
@allure.feature("移动类型配置")
class TestMvmTypeManagement(ScmInvBaseTest):
    """移动类型配置管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mvm_type_id = None
        
        # 查询现有数据获取关联ID
        try:
            sql = """
            SELECT 
                bs_type_id, fb_type_id, inv_type_trans_id, 
                remark, mvm_ext_type_id, name
            FROM inv_mvm_type_cf 
            WHERE name = '初始化-无正逆向-非限制-非限制-常规业务'
            LIMIT 1
            """
            result = cls.db.select(sql)
            if result and len(result) > 0:
                row = result[0]  # 取第一行数据
                cls.reference_data = {
                    'bs_type_id': row[0],
                    'fb_type_id': row[1], 
                    'inv_type_trans_id': row[2],
                    'remark': row[3],
                    'mvm_ext_type_id': row[4],
                    'name': row[5]
                }
                cls.logger.info(f"获取参考数据成功: {cls.reference_data}")
            else:
                cls.logger.warning("未找到参考数据，将使用默认配置")
                cls.reference_data = {}
        except Exception as e:
            cls.logger.error(f"获取参考数据失败: {str(e)}")
            cls.reference_data = {}
            
        cls.logger.info("移动类型配置管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="inv_mvm_type_cf",
                where="remark = %s",
                params=["自动化测试"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="移动类型配置",
        title="测试保存移动类型",
        description="验证移动类型的保存功能",
        severity="critical",
        order=1,
        tags=["库存", "移动类型", "配置"]
    )
    def test_save_mvm_type(self):
        """测试保存移动类型"""
        try:
            # 1. 准备测试数据
            mvm_type_code = self.mock_util.generate_unique_code(tag="AT")
            mvm_type_name = f"移动类型_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("INV-移动类型-保存服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["params", "request"]
            )
            
            set_dict = {
                "id": None,
                "createdBy": None,
                "updatedBy": None,
                "createdAt": None,
                "updatedAt": None,
                "version": 0,
                "deleted": 0,
                "code": mvm_type_code,
                "bsTypeId": {
                    "id": self.reference_data.get('bs_type_id', 2000005)
                },
                "fbTypeId": {
                    "id": self.reference_data.get('fb_type_id', 2002002)
                },
                "invTypeTransId": {
                    "id": self.reference_data.get('inv_type_trans_id', 2001002)
                },
                "name": mvm_type_name,
                "status": "INACTIVE",
                "remark": "自动化测试",
                "mvmExtTypeId": {
                    "id": self.reference_data.get('mvm_ext_type_id', 2001003)
                },
                "batchCodeRuleKey": None,
                "originOrgId": 0,
                "mvmRule": [
                    {
                        "isSpcStk": False,
                        "invOrgIdSource": "NONE",
                        "invTypeId": {
                            "id": 2000001  # 固定使用"非限制"库存类型ID
                        },
                        "mvmPosNeg": "INCREASE"
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 5. 保存数据和报告
            # 注意：移动类型保存接口只返回success，不返回具体数据
            self.__class__.mvm_type_id = "保存成功"  # 标记保存成功
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            self.logger.info(f"移动类型保存成功，ID: {self.mvm_type_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    # @case_decorator(
    #     story="移动类型配置",
    #     title="测试查询移动类型分页",
    #     description="验证移动类型的分页查询功能",
    #     severity="normal",
    #     order=3,
    #     tags=["库存", "移动类型", "查询"]
    # )
    # def test_query_mvm_type_page(self):
    #     """测试查询移动类型分页"""
    #     try:
    #         # 1. 调用API
    #         api_path = self.get_api_path("INV-移动类型-查询分页服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 2. 参数处理
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["params", "request"]
    #         )
            
    #         # 3. 设置分页查询参数（基于curl请求结构）
    #         query_params = {
    #             "request": {
    #                 "pageable": {
    #                     "pageNo": 1,
    #                     "pageSize": 20,
    #                     "needTotal": True,
    #                     "sortOrders": None,
    #                     "conditionItems": {
    #                         "type": "ConditionItems",
    #                         "conditions": {
    #                             "code": {
    #                                 "operator": "CONTAINS",
    #                                 "value": "AT"
    #                             }
    #                         },
    #                         "logicOperator": "AND"
    #                     }
    #                 },
    #                 "fields": [
    #                     {"name": "code", "type": "TEXT"},
    #                     {"name": "name", "type": "TEXT"},
    #                     {"name": "bsTypeId", "type": "OBJECT"},
    #                     {"name": "fbTypeId", "type": "OBJECT"},
    #                     {"name": "invTypeTransId", "type": "OBJECT"},
    #                     {"name": "mvmExtTypeId", "type": "OBJECT"},
    #                     {"name": "status", "type": "SELECT"}
    #                 ],
    #                 "systemParams": None
    #             }
    #         }
    #         ParamUtil.set_request_params(filtered_params, query_params)
            
    #         # 4. 发送请求和断言
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)
            
    #         # 5. 验证返回数据结构
    #         data = response.get("data", {}).get("data", {})
    #         total = data.get("total", 0)
    #         data_list = data.get("data", [])
            
    #         # 基础断言：验证分页查询结构
    #         assert total >= 0, f"总记录数不能为负数，actual: {total}"
    #         assert isinstance(data_list, list), f"数据列表类型错误，expected: list, actual: {type(data_list)}"
            
    #         # 6. 报告记录
    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #         self.logger.info("移动类型分页查询成功")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="移动类型配置",
    #     title="测试启用移动类型",
    #     description="验证移动类型的启用功能",
    #     severity="normal",
    #     order=4,
    #     tags=["库存", "移动类型", "启用"]
    # )
    # def test_enable_mvm_type(self):
    #     """测试启用移动类型"""
    #     try:
    #         # 依赖保存方法创建的数据
    #         assert self.mvm_type_id is not None, "请先执行 test_save_mvm_type 创建测试数据"
            
    #         # 1. 调用API
    #         api_path = self.get_api_path("INV-移动类型-启用服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 2. 参数处理
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["params", "request"]
    #         )
    #         ParamUtil.set_request_params(filtered_params, {"id": self.mvm_type_id})
            
    #         # 3. 发送请求和断言
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 4. 报告记录
    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #         self.logger.info(f"移动类型启用成功，ID: {self.mvm_type_id}")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="移动类型配置",
    #     title="测试禁用移动类型",
    #     description="验证移动类型的禁用功能",
    #     severity="normal",
    #     order=5,
    #     tags=["库存", "移动类型", "禁用"]
    # )
    # def test_disable_mvm_type(self):
    #     """测试禁用移动类型"""
    #     try:
    #         # 依赖保存方法创建的数据
    #         assert self.mvm_type_id is not None, "请先执行 test_save_mvm_type 创建测试数据"
            
    #         # 1. 调用API
    #         api_path = self.get_api_path("INV-移动类型-禁用服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 2. 参数处理
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["params", "request"]
    #         )
    #         ParamUtil.set_request_params(filtered_params, {"id": self.mvm_type_id})
            
    #         # 3. 发送请求和断言
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 4. 报告记录
    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #         self.logger.info(f"移动类型禁用成功，ID: {self.mvm_type_id}")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @pytest.mark.skip(reason="导出功能需要完整的业务流程支持，暂时跳过")
    # @case_decorator(
    #     story="移动类型配置",
    #     title="测试导出移动类型",
    #     description="验证移动类型的导出功能",
    #     severity="normal",
    #     order=6,
    #     tags=["库存", "移动类型", "导出"]
    # )
    # def test_export_mvm_type(self):
    #     """测试导出移动类型"""
    #     try:
    #         # 依赖保存方法创建的数据
    #         if not self.mvm_type_id:
    #             self.test_save_mvm_type()
            
    #         # 1. 调用API
    #         api_path = self.get_api_path("移动类型定义表-导入导出任务管理接口-提交导出任务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 2. 构造导出参数
    #         timestamp = self.mock_util.get_timestamp()
    #         export_params = {
    #             "serviceKey": "SCM_INV$INV_MVM_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
    #             "teamId": 22,
    #             "params": {
    #                 "taskName": f"移动类型-{self.nickname}-{timestamp}-导出",
    #                 "multiSheetConfig": [
    #                     {
    #                         "modelKey": "SCM_INV$inv_mvm_type_cf",
    #                         "modelName": "移动类型定义表",
    #                         "sheetNo": 0,
    #                         "sheetName": "移动类型定义表",
    #                         "headerConfigList": [
    #                             {
    #                                 "name": "简码",
    #                                 "type": "TEXT",
    #                                 "field": "code"
    #                             },
    #                             {
    #                                 "name": "名称",
    #                                 "type": "TEXT",
    #                                 "field": "name"
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         }
            
    #         # 3. 发送请求和断言
    #         response = self.http.post(url, json=export_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 4. 报告记录
    #         a.json(export_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #         self.logger.info("移动类型导出任务提交成功")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="移动类型配置",
    #     title="测试删除移动类型",
    #     description="验证移动类型的删除功能",
    #     severity="normal",
    #     order=7,
    #     tags=["库存", "移动类型", "删除"]
    # )
    # def test_delete_mvm_type(self):
    #     """测试删除移动类型"""
    #     try:
    #         # 依赖保存方法创建的数据
    #         assert self.mvm_type_id is not None, "请先执行 test_save_mvm_type 创建测试数据"
            
    #         # 1. 调用API
    #         api_path = self.get_api_path("INV-移动类型-删除服务")
    #         params, url = self.get_api_params(api_path)
            
    #         # 2. 参数处理
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params, ["params", "request"]
    #         )
    #         ParamUtil.set_request_params(filtered_params, {"id": self.mvm_type_id})
            
    #         # 3. 发送请求和断言
    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)
            
    #         # 4. 报告记录
    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")
            
    #         self.logger.info(f"移动类型删除成功，ID: {self.mvm_type_id}")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
