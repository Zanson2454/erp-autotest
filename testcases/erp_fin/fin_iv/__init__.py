# -*- coding: utf-8 -*-
"""
存货价值（IV）测试模块
提供统一的基类和初始化配置管理
"""
import allure
from testcases.erp_fin import FinBaseTest
from utils.report_util import a


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值模块")
class IvBaseTest(FinBaseTest):
    """
    存货价值测试基类
    
    功能说明：
    1. 继承 FinBaseTest，提供财务模块的基础能力
    2. 在 setup_class 中自动初始化存货核算配置
    3. 如果配置已存在则复用，不存在则创建并完成初始化流程
    4. 所有 fin_iv 模块下的测试类应继承此基类
    
    初始化流程：
    1. 查询是否已存在初始化配置（根据公司组织ID和iv_type）
    2. 如果不存在，则创建初始化配置
    3. 执行后处理（启用配置）
    4. 期初确认
    5. 异步执行初始化并等待完成
    
    使用示例：
        from testcases.erp_fin.fin_iv import IvBaseTest
        
        class TestMyFeature(IvBaseTest):
            def test_something(self):
                # 可以直接使用 self.continuous_method_init_cf_id
                pass
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化 - 自动初始化存货核算配置"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定存货价值模块上下文并初始化存货核算配置。"""
        # 显式复用模块上下文绑定骨架（与 FinBaseTest 保持一致，幂等）
        cls.bind_module_user_context("FIN", strict=True)

        # 映射父类已初始化的组织ID变量（避免重复获取）
        # FinBaseTest 中已初始化：
        # - cls.com_org_id = 从 gr_come_org_info 获取
        # - cls.com_org_id_2 = 从 com_org_info 获取
        # 为了保持命名一致性，映射为：
        # - cls.com_org_id = 从 com_org_info 获取（用于 CONTINUOUS_METHOD）
        # - cls.gr_com_org_id = 从 gr_come_org_info 获取（用于 PERIOD_METHOD）
        if hasattr(cls, 'com_org_id') and hasattr(cls, 'com_org_id_2'):
            # 保存父类的值
            cls.gr_com_org_id = cls.com_org_id  # 父类中 com_org_id 来自 gr_come_org_info
            cls.com_org_id = cls.com_org_id_2   # 父类中 com_org_id_2 来自 com_org_info
        else:
            # 如果父类未初始化（理论上不会发生），则从 md_cache_data 获取
            if cls.md_cache_data:
                gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
                com_org_info = cls.md_cache_data.get("org_info", {}).get("com_org_info", [])
                cls.com_org_id = com_org_info[0].get("id") if com_org_info else None
                cls.gr_com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
        
        # 初始化存货核算配置（永续成本法）
        cls.continuous_method_init_cf_id = None
        cls.period_method_init_cf_id = None
        
        # 自动初始化存货核算配置（永续成本法）
        # 如果配置已存在则复用，不存在则创建并完成初始化流程
        cls._ensure_iv_init_configuration()
        
        cls.logger.info("存货价值测试基类初始化完成")
    
    @classmethod
    def _ensure_iv_init_configuration(cls):
        """
        确保存货核算初始化配置已存在并完成初始化流程
        
        流程说明：
        1. 查询是否已存在初始化配置（根据公司组织ID和iv_type=CONTINUOUS_METHOD）
        2. 如果存在且已完成初始化（initStatus=INIT），则直接复用
        3. 如果不存在或未完成初始化，则创建并完成初始化流程：
           - 创建初始化配置
           - 执行后处理（启用）
           - 期初确认
           - 异步执行初始化并等待完成
        """
        try:
            if not cls.com_org_id:
                cls.logger.warning("com_org_id 未初始化，跳过存货核算初始化配置检查")
                return
            
            # 查询是否已存在初始化配置
            existing_config = cls._query_existing_init_config(
                com_org_id=cls.com_org_id,
                iv_type="CONTINUOUS_METHOD"
            )
            
            if existing_config:
                # 检查初始化状态
                init_status = existing_config.get("initStatus")
                async_status = existing_config.get("asyncExecutionStatus")
                
                if init_status == "INIT" and async_status == "SUCCEEDED":
                    # 配置已存在且已完成初始化，直接复用
                    cls.continuous_method_init_cf_id = existing_config.get("id")
                    cls.logger.info(
                        f"复用已存在的存货核算初始化配置，ID: {cls.continuous_method_init_cf_id}, "
                        f"状态: initStatus={init_status}, asyncStatus={async_status}"
                    )
                    return
                else:
                    # 配置存在但未完成初始化，删除后重新创建
                    cls.logger.info(
                        f"发现未完成初始化的配置（ID: {existing_config.get('id')}, "
                        f"initStatus={init_status}, asyncStatus={async_status}），将删除后重新创建"
                    )
                    cls.db.delete(
                        table="fin_iv_init_cf",
                        where="id = %s",
                        params=[existing_config.get("id")]
                    )
            
            # 创建并完成初始化流程
            cls.logger.info("开始创建存货核算初始化配置并完成初始化流程")
            cls._create_and_complete_iv_init_configuration()
            
        except Exception as e:
            cls.logger.error(f"初始化存货核算配置失败: {str(e)}")
            # 不抛出异常，允许测试继续执行（某些测试可能不需要初始化配置）
            a.text(f"初始化存货核算配置失败: {str(e)}", "初始化警告")
    
    @classmethod
    def _query_existing_init_config(cls, com_org_id, iv_type):
        """
        查询已存在的初始化配置
        
        :param com_org_id: 公司组织ID
        :param iv_type: 存货价值类型（CONTINUOUS_METHOD 或 PERIOD_METHOD）
        :return: 配置数据字典，如果不存在则返回None
        """
        try:
            config = cls.query_service.get_iv_existing_init_config(com_org_id, iv_type)
            if config:
                # 转换为API返回格式（字段名驼峰转换）
                return {
                    "id": config.get("id"),
                    "comOrgId": {"id": config.get("com_org_id")},
                    "ivType": config.get("iv_type"),
                    "initStatus": config.get("init_status"),
                    "asyncExecutionStatus": config.get("async_execution_status"),
                    "enableStatus": config.get("enable_status"),
                    "beginStatus": config.get("begin_status")
                }
            return None
        except Exception as e:
            cls.logger.error(f"查询初始化配置失败: {str(e)}")
            return None
    
    @classmethod
    def _create_and_complete_iv_init_configuration(cls):
        """
        创建并完成存货核算初始化配置的完整流程
        
        流程步骤：
        1. 创建初始化配置
        2. 执行后处理（启用配置）
        3. 期初确认
        4. 异步执行初始化并等待完成
        
        注意：由于 standard_api_call 等方法是实例方法，需要创建临时实例来调用
        """
        # 创建临时实例来执行初始化流程
        # 注意：这里不能直接创建实例，因为 pytest 的测试类实例化需要特殊处理
        # 所以我们使用类方法，但通过一个辅助方法来执行实例方法
        temp_instance = cls._create_temp_instance()
        
        # 步骤1：创建初始化配置
        cls._create_init_configuration(temp_instance)
        
        # 步骤2：执行后处理（启用配置）
        cls._execute_post_initialization(temp_instance)
        
        # 步骤3：期初确认
        cls._confirm_begin(temp_instance)
        
        # 步骤4：异步执行初始化并等待完成
        cls._execute_initialization_async_and_wait(temp_instance)
    
    @classmethod
    def _create_temp_instance(cls):
        """
        创建临时实例用于执行初始化流程
        
        注意：这个实例只用于初始化流程，不会用于实际测试
        由于 pytest 的测试类实例化需要特殊处理，我们创建一个简单的辅助对象
        """
        # 创建一个简单的对象，设置必要的类属性
        # 使用 type() 创建一个新类，继承自 cls，然后实例化
        # 但更简单的方式是直接创建一个对象，然后设置必要的属性
        instance = object.__new__(cls)
        
        # 复制必要的类属性到实例
        # 这些属性在 setup_class 中已经初始化
        necessary_attrs = [
            'db', 'http', 'assert_util', 'async_wait_util', 'wait_status',
            'logger', 'apis', 'api_params', 'yaml_util', 'mock_util',
            'com_org_id', 'gr_com_org_id', 'continuous_method_init_cf_id'
        ]
        
        for attr_name in necessary_attrs:
            if hasattr(cls, attr_name):
                setattr(instance, attr_name, getattr(cls, attr_name))
        
        return instance
    
    @classmethod
    def _create_init_configuration(cls, instance):
        """创建初始化配置"""
        try:
            com_org_obj = {"id": cls.com_org_id}
            iv_type = "CONTINUOUS_METHOD"
            
            # 构造期间对象（如果有）
            period_head_obj = None
            start_period_obj = None
            if hasattr(cls, 'calendar_head_id') and cls.calendar_head_id:
                period_head_obj = {"id": cls.calendar_head_id}
            if hasattr(cls, 'calendar_item_id') and cls.calendar_item_id:
                start_period_obj = {"id": cls.calendar_item_id}
            
            set_dict = {
                "comOrgId": com_org_obj,
                "ivType": iv_type,
                "periodHeadId": period_head_obj,
                "startPeriod": start_period_obj,
                "enableStatus": "DISABLE",
                "beginStatus": None,
                "initStatus": "NOT_INIT",
                "accountingStatus": "WAITING",
                "accountStatus": "WAITING",
                "asyncExecutionStatus": "CREATED",
                "asyncExecutionFailureReason": None,
                "currentPeriod": None
            }
            
            # 调用前先删除可能存在的初始化数据，防止触发唯一性校验
            cls.db.delete(
                table="fin_iv_init_cf",
                where="com_org_id = %s and iv_type = %s",
                params=[cls.com_org_id, iv_type]
            )
            
            # 创建初始化配置
            response, extracted_id = instance.standard_api_call(
                api_key="存货核算初始化配置-初始化配置",
                set_dict=set_dict,
                store_id_as="continuous_method_init_cf",
                param_path=["params", "reuqest"]  # 使用reuqest路径（接口定义中的拼写错误）
            )
            
            instance.assert_util.assert_response_data(response)
            cls.continuous_method_init_cf_id = extracted_id
            cls.logger.info(f"创建初始化配置成功，ID: {cls.continuous_method_init_cf_id}")
            
        except Exception as e:
            cls.logger.error(f"创建初始化配置失败: {str(e)}")
            raise
    
    @classmethod
    def _execute_post_initialization(cls, instance):
        """执行初始化后处理（启用配置）"""
        try:
            if not cls.continuous_method_init_cf_id:
                raise ValueError("continuous_method_init_cf_id 未设置，无法执行后处理")
            
            set_dict = {"id": cls.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = instance.standard_api_call(
                api_key="存货核算初始化配置-执行初始化后处理流程",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]
            )
            
            enable_status = response.get("data", {}).get("data", {}).get("enableStatus")
            instance.assert_util.assert_by_operator(enable_status, "=", "ENABLED", "启用状态应为ENABLED")
            cls.logger.info("执行初始化后处理成功，配置已启用")
            
        except Exception as e:
            cls.logger.error(f"执行初始化后处理失败: {str(e)}")
            raise
    
    @classmethod
    def _confirm_begin(cls, instance):
        """期初确认"""
        try:
            if not cls.continuous_method_init_cf_id:
                raise ValueError("continuous_method_init_cf_id 未设置，无法执行期初确认")
            
            set_dict = {"id": cls.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = instance.standard_api_call(
                api_key="存货核算初始化配置-期初确认",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None,
                param_path=["params", "reuqest"]
            )
            
            begin_status = response.get("data", {}).get("data", {}).get("beginStatus")
            instance.assert_util.assert_by_operator(begin_status, "=", "CONFIRM", "期初确认状态应为CONFIRM")
            cls.logger.info("期初确认成功")
            
        except Exception as e:
            cls.logger.error(f"期初确认失败: {str(e)}")
            raise
    
    @classmethod
    def _execute_initialization_async_and_wait(cls, instance):
        """异步执行初始化并等待完成"""
        try:
            if not cls.continuous_method_init_cf_id:
                raise ValueError("continuous_method_init_cf_id 未设置，无法执行初始化")
            
            # 步骤1：发起异步初始化任务
            set_dict = {"id": cls.continuous_method_init_cf_id}
            fields_to_filter = ["id"]
            
            response, _ = instance.standard_api_call(
                api_key="存货核算初始化配置-执行初始化-异步任务发起",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            instance.assert_util.assert_response_success(response)
            
            # 验证异步任务已创建
            async_execution_status = response.get("data", {}).get("data", {}).get("asyncExecutionStatus")
            instance.assert_util.assert_by_operator(
                async_execution_status, "=", "CREATED",
                "异步任务发起初始化状态应为CREATED"
            )
            
            # 步骤2：定义查询函数
            def query_init_status():
                """查询初始化配置状态"""
                response, _ = instance.standard_api_call(
                    api_key="存货价值初始化配置表-根据ID查找数据服务",
                    set_dict={"id": cls.continuous_method_init_cf_id},
                    fields_to_filter=["id"]
                )
                instance.assert_util.assert_response_success(response)
                return response.get("data", {}).get("data", {})
            
            # 步骤3：等待异步任务完成
            result = instance.async_wait_util.wait_for_async_status(
                query_func=query_init_status,
                status_field="asyncExecutionStatus",
                success_status="SUCCEEDED",
                failed_status="FAILED",
                failure_reason_field="asyncExecutionFailureReason",
                max_wait=60,  # 增加等待时间到60秒，因为初始化可能需要较长时间
                interval=2  # 每2秒查询一次
            )
            
            # 步骤4：断言等待结果
            if result.status == instance.wait_status.SUCCESS:
                # 验证初始化状态
                init_status = result.last_data.get("initStatus")
                instance.assert_util.assert_by_operator(
                    init_status, "=", "INIT",
                    f"初始化任务应成功完成，initStatus应为INIT，实际状态: {init_status}"
                )
                
                # 验证异步执行状态
                async_execution_status = result.last_data.get("asyncExecutionStatus")
                instance.assert_util.assert_by_operator(
                    async_execution_status, "=", "SUCCEEDED",
                    f"异步任务状态应为SUCCEEDED，实际状态: {async_execution_status}"
                )
                
                cls.logger.info(
                    f"✅ 初始化任务成功完成，总耗时: {result.total_wait_time:.2f}秒，"
                    f"检查次数: {result.attempts}次"
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
                    f"最后状态: {result.last_data.get('asyncExecutionStatus') if result.last_data else '未知'}"
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
