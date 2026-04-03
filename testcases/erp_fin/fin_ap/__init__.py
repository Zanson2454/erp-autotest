# -*- coding: utf-8 -*-
"""
应付单（AP）测试模块
提供统一的基类和初始化配置管理
"""

import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from erp_data_factory.compat.fin_ap_factory import FinApFactory
from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付单模块")
class ApBaseTest(FinBaseTest):
    """
    应付单测试基类

    功能说明：
    1. 继承 FinBaseTest，提供财务模块的基础能力
    2. 在 setup_class 中自动初始化财务初始化配置
    3. 如果配置已存在且已完成初始化则复用，不存在或未完成则创建并完成初始化流程
    4. 所有 fin_ap 模块下的测试类应继承此基类

    初始化流程：
    1. 查询是否已存在初始化配置（根据gr_com_org_id和moduleCode=AP）
    2. 如果存在且已完成初始化（initializationType=INITIALIZED），则直接复用
    3. 如果不存在或未完成初始化，则执行完整流程：
       - 创建初始化配置
       - 启用配置
       - 异步执行初始化并等待完成

    使用示例：
        from testcases.erp_fin.fin_ap import ApBaseTest

        class TestMyFeature(ApBaseTest):
            def test_something(self):
                # 可以直接使用 self.ap_init_id
                pass
    """

    @classmethod
    def setup_class(cls):
        """测试类初始化 - 自动初始化财务初始化配置"""
        super().setup_class()

    @classmethod
    def bind_context(cls):
        """绑定应付模块上下文并初始化应付配置。"""
        # 先执行父类上下文绑定，确保 ap_type_info / 组织ID / 用户上下文等基础字段就绪。
        super().bind_context()
        cls.ap_factory = FinApFactory()

        # 初始化MD数据（从md_cache_data获取主数据）
        # 使用安全获取方式，先判断列表是否存在且非空，再获取第一个元素
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            com_org_info = cls.md_cache_data.get("org_info", {}).get("com_org_info", [])

            # 安全获取公司组织ID
            if com_org_info and len(com_org_info) > 0:
                cls.com_org_id = com_org_info[0].get("id")
            else:
                cls.com_org_id = None
                cls.logger.warning(
                    "⚠️ 未找到公司组织信息（com_org_info），请检查 md_init_cache.json 中的 org_info.com_org_info 数据"
                )

            # 安全获取集团公司组织ID
            if gr_come_org_info and len(gr_come_org_info) > 0:
                cls.gr_com_org_id = gr_come_org_info[0].get("id")
            else:
                cls.gr_com_org_id = None
                cls.logger.warning(
                    "⚠️ 未找到集团公司组织信息（gr_come_org_info），请检查 md_init_cache.json 中的 org_info.gr_come_org_info 数据"
                )
        else:
            cls.com_org_id = None
            cls.gr_com_org_id = None
            cls.logger.warning("⚠️ md_cache_data 未初始化，请检查主数据缓存是否正常加载")

        # 获取应付单类型
        if cls.ap_type_info:
            # 检查并获取 STND 应付单类型
            ar_type_stnd_list = cls.ap_type_info.get("ar_type_STND", [])
            if not ar_type_stnd_list or len(ar_type_stnd_list) == 0:
                raise ValueError("请检查STND应付单类型是否配置")
            cls.ap_type_stnd_id = ar_type_stnd_list[0].get("id")

            # 检查并获取 INIT 应付单类型
            ar_type_init_list = cls.ap_type_info.get("ar_type_INIT", [])
            if not ar_type_init_list or len(ar_type_init_list) == 0:
                raise ValueError("请检查INIT应付单类型是否配置")
            cls.ap_type_init_id = ar_type_init_list[0].get("id")

            cls.logger.info(f"获取到 ap_type_stnd_id: {cls.ap_type_stnd_id}, ap_type_init_id: {cls.ap_type_init_id}")

        # 获取结算项类型
        if cls.fin_cache_data:
            sett_item_type_info_list = cls.fin_cache_data.get("sett_item_info", {}).get("sett_item_type_info", [])
            cls.logger.info(f"获取到 sett_item_type_info_list: {sett_item_type_info_list}")
            for i in sett_item_type_info_list:
                if i.get("sett_item_type_code") == "E_PUR_GOODS":
                    cls.sett_item_type_E_PUR_GOODS_id = i.get("id")
                    cls.logger.info(f"获取到 sett_item_type_E_PUR_GOODS_id: {cls.sett_item_type_E_PUR_GOODS_id}")
                elif i.get("sett_item_type_code") == "E_PUR_GODS_ACCR":
                    cls.sett_item_type_E_PUR_GODS_ACCR_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_PUR_FRET_P":
                    cls.sett_item_type_E_PUR_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_PUR_INSP":
                    cls.sett_item_type_E_PUR_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_GOODS":
                    cls.sett_item_type_E_SLS_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_FRET_P":
                    cls.sett_item_type_E_SLS_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_INSP":
                    cls.sett_item_type_E_SLS_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_GOODS":
                    cls.sett_item_type_I_PUR_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_FRET_P":
                    cls.sett_item_type_I_PUR_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_INSP":
                    cls.sett_item_type_I_PUR_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_SLS_GOODS":
                    cls.sett_item_type_I_SLS_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_SLS_FRET_P":
                    cls.sett_item_type_I_SLS_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_SLS_INSP":
                    cls.sett_item_type_I_SLS_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_PUR_GOODS":
                    cls.sett_item_type_C_PUR_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_PUR_FRET_P":
                    cls.sett_item_type_C_PUR_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_PUR_INSP":
                    cls.sett_item_type_C_PUR_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_SLS_GOODS":
                    cls.sett_item_type_C_SLS_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_SLS_FRET_P":
                    cls.sett_item_type_C_SLS_FRET_P_id = i.get("id")
                elif i.get("sett_item_type_code") == "C_SLS_INSP":
                    cls.sett_item_type_C_SLS_INSP_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_PUR_FRET_C":
                    cls.sett_item_type_E_PUR_FRET_C_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_FRET_C":
                    cls.sett_item_type_E_SLS_FRET_C_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_REBATE":
                    cls.sett_item_type_E_SLS_REBATE_id = i.get("id")
                elif i.get("sett_item_type_code") == "INTERNAL-SLS-TEST001":
                    cls.sett_item_type_INTERNAL_SLS_TEST001_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_GOODS":
                    cls.sett_item_type_I_PUR_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_STORAGE_FEE":
                    cls.sett_item_type_E_SLS_STORAGE_FEE_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_PUR_STORAGE_FEE":
                    cls.sett_item_type_E_PUR_STORAGE_FEE_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_INTEREST":
                    cls.sett_item_type_E_SLS_INTEREST_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_DEFAULT":
                    cls.sett_item_type_E_SLS_DEFAULT_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_GOODS":
                    cls.sett_item_type_I_PUR_GOODS_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_STORAGE_FEE":
                    cls.sett_item_type_E_SLS_STORAGE_FEE_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_PUR_STORAGE_FEE":
                    cls.sett_item_type_E_PUR_STORAGE_FEE_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_INTEREST":
                    cls.sett_item_type_E_SLS_INTEREST_id = i.get("id")
                elif i.get("sett_item_type_code") == "E_SLS_DEFAULT":
                    cls.sett_item_type_E_SLS_DEFAULT_id = i.get("id")
                elif i.get("sett_item_type_code") == "I_PUR_GOODS":
                    cls.sett_item_type_I_PUR_GOODS_id = i.get("id")
        if not hasattr(cls, "sett_item_type_E_PUR_GOODS_id"):
            e_pur_goods = (getattr(cls, "sett_item_type_info", {}) or {}).get("E_PUR_GOODS")
            if isinstance(e_pur_goods, dict):
                cls.sett_item_type_E_PUR_GOODS_id = e_pur_goods.get("id")
        # 初始化应付初始化配置ID
        cls.ap_init_id = None

        # 自动初始化应付初始化配置
        # 如果配置已存在且已完成初始化则复用，否则创建并完成初始化流程
        cls._ensure_ap_init_configuration()

        cls.logger.info("应付单测试基类初始化完成")

    @classmethod
    def _ensure_ap_init_configuration(cls):
        """
        确保应付初始化配置已存在并完成初始化流程

        流程说明：
        1. 查询是否已存在初始化配置（根据gr_com_org_id和moduleCode=AP）
        2. 如果存在且已完成初始化（initializationType=INITIALIZED），则直接复用
        3. 如果不存在或未完成初始化，则创建并完成初始化流程：
           - 创建初始化配置
           - 启用配置
           - 异步执行初始化并等待完成
        """
        try:
            if not cls.gr_com_org_id:
                cls.logger.warning("gr_com_org_id 未初始化，跳过应付初始化配置检查")
                return

            # 查询是否已存在初始化配置
            existing_config = cls._query_existing_init_config(gr_com_org_id=cls.gr_com_org_id, module_code="AP")

            if existing_config:
                # 检查初始化状态
                initialization_type = existing_config.get("initializationType")

                if initialization_type == "INITIALIZED":
                    # 配置已存在且已完成初始化，直接复用
                    cls.ap_init_id = existing_config.get("id")
                    cls.logger.info(
                        f"复用已存在的应付初始化配置，ID: {cls.ap_init_id}, "
                        f"状态: initializationType={initialization_type}"
                    )
                    return
                else:
                    # 配置存在但未完成初始化，删除后重新创建
                    cls.logger.info(
                        f"发现未完成初始化的配置（ID: {existing_config.get('id')}, "
                        f"initializationType={initialization_type}），将删除后重新创建"
                    )
                    cls.db.delete(table="fin_gen_im_head_tr", where="id = %s", params=[existing_config.get("id")])

            # 创建并完成初始化流程
            cls.logger.info("开始创建应付初始化配置并完成初始化流程")
            cls._create_and_complete_ap_init_configuration()

        except Exception as e:
            cls.logger.error(f"初始化应付初始化配置失败: {str(e)}")
            # 不抛出异常，允许测试继续执行（某些测试可能不需要初始化配置）
            a.text(f"初始化应付初始化配置失败: {str(e)}", "初始化警告")

    @classmethod
    def _query_existing_init_config(cls, gr_com_org_id, module_code):
        """
        查询已存在的初始化配置

        :param gr_com_org_id: 集团公司组织ID
        :param module_code: 模块代码（如"AP"）
        :return: 配置数据字典，如果不存在则返回None
        """
        try:
            config = cls.query_service.get_ap_existing_init_config(gr_com_org_id, module_code)
            if config:
                # 转换为API返回格式（字段名驼峰转换）
                return {
                    "id": config.get("id"),
                    "comOrg": {"id": config.get("com_org")},
                    "moduleCode": config.get("module_code"),
                    "initializationType": config.get("initialization_type"),
                    "startType": config.get("start_type"),
                }
            return None
        except Exception as e:
            cls.logger.error(f"查询初始化配置失败: {str(e)}")
            return None

    @classmethod
    def _create_and_complete_ap_init_configuration(cls):
        """
        创建并完成应付初始化配置的完整流程

        流程步骤：
        1. 创建初始化配置
        2. 启用配置
        3. 异步执行初始化并等待完成

        注意：由于 standard_api_call 等方法是实例方法，需要创建临时实例来调用
        """
        # 创建临时实例来执行初始化流程
        temp_instance = cls._create_temp_instance()

        # 步骤1：创建初始化配置
        cls._create_init_configuration(temp_instance)

        # 步骤2：启用配置
        cls._enable_configuration(temp_instance)

        # 步骤3：异步执行初始化并等待完成
        cls._execute_initialization_async_and_wait(temp_instance)

    @classmethod
    def _create_temp_instance(cls):
        """
        创建临时实例用于执行初始化流程

        注意：这个实例只用于初始化流程，不会用于实际测试
        """
        # 创建一个简单的对象，设置必要的类属性
        instance = object.__new__(cls)

        # 复制必要的类属性到实例
        # 这些属性在 setup_class 中已经初始化
        necessary_attrs = [
            "db",
            "http",
            "assert_util",
            "async_wait_util",
            "wait_status",
            "logger",
            "apis",
            "api_params",
            "yaml_util",
            "mock_util",
            "gr_com_org_id",
            "com_org_id",
            "ap_init_id",
        ]

        for attr_name in necessary_attrs:
            if hasattr(cls, attr_name):
                setattr(instance, attr_name, getattr(cls, attr_name))

        return instance

    @classmethod
    def _create_init_configuration(cls, instance):
        """创建初始化配置"""
        try:
            # 检查依赖数据
            if not instance.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")

            # 准备初始化参数
            com_org_obj = {"id": instance.gr_com_org_id}
            start_date = instance.mock_util.get_timestamp(timestamp=True)

            # 调用前先删除初始化数据，防止触发唯一性校验
            cls.db.delete(
                table="fin_gen_im_head_tr",
                where="com_org = %s and module_code = %s",
                params=[instance.gr_com_org_id, "AP"],
            )

            # 保存数据到 fin_gen_im_head_tr 表
            save_set_dict = {
                "moduleCode": "AP",
                "comOrg": com_org_obj,
                "startDate": start_date,
                "initialBalanceType": "UNRECORDED",
                "startType": "DISABLED",
                "initializationType": "UNINITIALIZED",
            }

            save_response, saved_id = instance.standard_api_call(
                api_key="财务域通用模块初始化表-保存数据服务",
                set_dict=save_set_dict,
                store_id_as="ap_init",
                query_params="modelKey=ERP_FIN$fin_gen_im_head_tr",
            )

            instance.assert_util.assert_response_data(save_response)
            cls.ap_init_id = saved_id
            cls.logger.info(f"创建初始化配置成功，ID: {cls.ap_init_id}")

        except Exception as e:
            cls.logger.error(f"创建初始化配置失败: {str(e)}")
            raise

    @classmethod
    def _enable_configuration(cls, instance):
        """启用初始化配置"""
        try:
            if not cls.ap_init_id:
                raise ValueError("ap_init_id 未设置，无法启用配置")

            set_dict = {"id": cls.ap_init_id}

            response, _ = instance.standard_api_call(
                api_key="IM-财务初始化管理-启用服务", set_dict=set_dict, store_id_as=None
            )

            # 业务断言（只验证响应成功，不校验状态）
            instance.assert_util.assert_response_success(response)
            cls.logger.info("启用配置成功")

        except Exception as e:
            cls.logger.error(f"启用配置失败: {str(e)}")
            raise

    @classmethod
    def _execute_initialization_async_and_wait(cls, instance):
        """异步执行初始化并等待完成"""
        try:
            if not cls.ap_init_id:
                raise ValueError("ap_init_id 未设置，无法执行初始化")

            # 检查依赖数据
            if not instance.gr_com_org_id:
                raise ValueError("gr_com_org_id 未初始化，请检查 md_cache_data")

            # 步骤1：发起异步初始化任务
            com_org_obj = {"id": instance.gr_com_org_id}
            start_date = instance.mock_util.get_timestamp(timestamp=True)

            set_dict = {
                "id": cls.ap_init_id,
                "moduleCode": "AP",
                "initialBalanceType": "UNRECORDED",
                "initializationType": "UNINITIALIZED",
                "startDate": start_date,
                "startType": "ENABLED",
                "comOrg": com_org_obj,
            }

            response, _ = instance.standard_api_call(
                api_key="IM-财务初始化管理-初始化服务", set_dict=set_dict, store_id_as=None
            )

            # 验证接口调用成功
            instance.assert_util.assert_response_success(response)

            # 步骤2：定义查询函数
            def query_init_status():
                """查询初始化配置状态"""
                response, _ = instance.standard_api_call(
                    api_key="财务域通用模块初始化表-根据ID查找数据服务",
                    set_dict={"id": cls.ap_init_id},
                    store_id_as=None,
                    query_params="modelKey=ERP_FIN$fin_gen_im_head_tr",
                )
                instance.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})

            # 步骤3：等待初始化完成
            result = instance.async_wait_util.wait_for_async_status(
                query_func=query_init_status,
                status_field="initializationType",
                success_status="INITIALIZED",
                failed_status=None,
                failure_reason_field=None,
                max_wait=60,  # 最大等待时间（秒），初始化可能需要较长时间
                interval=2,  # 轮询间隔（秒），每2秒查询一次状态
            )

            # 步骤4：断言等待结果
            if result.status == instance.wait_status.SUCCESS:
                # 验证初始化状态
                initialization_type = result.last_data.get("initializationType")
                instance.assert_util.assert_by_operator(
                    initialization_type,
                    "=",
                    "INITIALIZED",
                    f"初始化任务应成功完成，initializationType应为INITIALIZED，实际状态: {initialization_type}",
                )

                cls.logger.info(
                    f"✅ 初始化任务成功完成，总耗时: {result.total_wait_time:.2f}秒，"
                    f"检查次数: {result.attempts}次，初始化状态: {initialization_type}"
                )
            elif result.status == instance.wait_status.FAILED:
                failure_reason = result.error_message or "未知原因"
                raise AssertionError(
                    f"❌ 异步初始化任务失败: {failure_reason}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次"
                )
            elif result.status == instance.wait_status.TIMEOUT:
                raise AssertionError(
                    f"⚠️ 等待异步初始化任务超时\n"
                    f"最大等待时间: 60秒\n"
                    f"实际等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次\n"
                    f"最后状态: {result.last_data.get('initializationType') if result.last_data else '未知'}"
                )
            else:
                raise AssertionError(
                    f"等待异步初始化任务时发生错误: {result.error_message}\n"
                    f"等待时间: {result.total_wait_time:.2f}秒\n"
                    f"检查次数: {result.attempts}次"
                )

        except Exception as e:
            cls.logger.error(f"异步执行初始化失败: {str(e)}")
            raise

    @staticmethod
    def convert_decimal_to_float(obj: Any) -> Any:
        """将 Decimal/datetime 递归转换为 JSON 可序列化结构。"""
        if obj is None:
            return None
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, dict):
            return {k: ApBaseTest.convert_decimal_to_float(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [ApBaseTest.convert_decimal_to_float(i) for i in obj]
        return obj

    def send_api_request(self, api_key: str, request_data: Dict[str, Any], fields: list[str]) -> Dict[str, Any]:
        """历史通用请求封装：构建参数并调用 standard_api_call。"""
        api_path = ParamUtil.get_api_path(self.apis, api_key)
        params, _ = ParamUtil.get_api_params(self.api_params, api_path)
        filtered_params = ParamUtil.filter_post_body_fields(params, fields, ["params", "request"])
        ParamUtil.set_request_params(filtered_params, request_data)
        filtered_params = self.convert_decimal_to_float(filtered_params)
        result, _ = self.standard_api_call(
            api_key=api_key,
            set_dict=filtered_params.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)
        return {"result": result, "request_params": filtered_params}

    def create_ap_request_body(self, doc_type_id: int = 2002001, account_type: str = "FIN") -> Dict[str, Any]:
        """兼容历史 AP 用例：生成标准应付单请求体与基础数据。"""
        base_data = self.ap_factory.get_base_data_for_fin_doc("AP")
        mat = self.ap_factory.create_material()
        tax_code = self.ap_factory.create_tax_code(13)
        ap_items = self.ap_factory.create_ap_items_full([mat], [tax_code])

        gross_doc_amt = sum((item.get("grossDocAmt") or 0) for item in ap_items)
        net_doc_amt = sum((item.get("netDocAmt") or 0) for item in ap_items)
        gross_base_amt = sum((item.get("grossBaseAmt") or 0) for item in ap_items)
        net_base_amt = sum((item.get("netBaseAmt") or 0) for item in ap_items)
        ap_schls = [self.ap_factory.create_ap_schl(amount=gross_doc_amt, due_date=int(time.time() * 1000))]

        request_body = {
            "docTypeId": {"id": doc_type_id},
            "apDate": int(time.time() * 1000),
            "comOrgId": base_data["com_org"],
            "purOrgId": base_data["pur_org"],
            "payOrgId": base_data["pay_org"],
            "apHeadCode": self.mock_util.generate_unique_code("APD"),
            "remark": self.mock_util.get_mock_remark() or f"自动化测试提交-{account_type}",
            "settPartnerType": "SUPPLIER",
            "settPartnerId": base_data["vend"],
            "docCurrId": base_data["currency"],
            "baseCurrId": base_data["currency"],
            "exchRate": 1,
            "grossDocAmt": gross_doc_amt,
            "netDocAmt": net_doc_amt,
            "grossBaseAmt": gross_base_amt,
            "netBaseAmt": net_base_amt,
            "payClearingStatus": "UNCLEARED",
            "invClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "apItems": ap_items,
            "apSchls": ap_schls,
        }

        base_data.update(
            {
                "total_amt": gross_doc_amt,
                "net_doc_amt": net_doc_amt,
                "gross_base_amt": gross_base_amt,
                "net_base_amt": net_base_amt,
            }
        )
        return {"request_body": request_body, "base_data": base_data}

    def query_ap_detail(self, ap_doc_id, ap_detail=None):
        """查询应付单详情；兼容旧签名，支持传入外部dict或直接返回详情。"""
        api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
        params, _ = ParamUtil.get_api_params(self.api_params, api_path)

        query_params = {
            "containerKey": "ERP_FIN$FIN_APM_FROM_DS-TERP_MIGRATE$FIN_APM_230706-detailView-detail",
            "params": {"request": {"id": str(ap_doc_id)}},
        }

        result, _ = self.standard_api_call(
            api_key="应付单头表-根据ID查找数据服务",
            set_dict=query_params.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)
        detail = result.get("data", {}).get("data", {}) or {}
        if isinstance(ap_detail, dict):
            ap_detail.update(detail)
        return detail

    def wait_for_ap_status(
        self, ap_head_code: str, target_status: str, max_wait: int = 15, interval: float = 2.0
    ) -> Dict[str, Any]:
        """轮询应付单状态，兼容历史 AP 用例。"""
        sql = (
            "SELECT ap_status, async_execution_status FROM fin_apm_ap_head_tr "
            "WHERE deleted = 0 AND ap_head_code = %s ORDER BY updated_at DESC LIMIT 1"
        )
        end_at = time.time() + max_wait
        last_row: Dict[str, Any] = {}
        while time.time() < end_at:
            rows = self.query_service.query(sql, [ap_head_code])
            if rows:
                last_row = rows[0]
                if last_row.get("ap_status") == target_status:
                    return last_row
            time.sleep(interval)
        return last_row


if __name__ == "__main__":
    cls = ApBaseTest()
    cls.setup_class()
