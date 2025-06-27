import allure
import pytest
from datetime import datetime
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from utils.assert_util import AssertHelper
from utils.log_util import Loggers

@allure.epic("主数据管理")
@allure.feature("客户管理评分模版")
class TestCustManagement(GenMdBaseTest):
    """客户管理评分模版测试类"""

    def setup_class(self):
        super().setup_class()
        self.partnerType_info = {}

    @case_decorator(
        story="评分模板创建",
        title="测试评分模版新增接口",
        description="验证评分模版新增（保存）接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["评分模板新增", "新增"]
    )    

    def test_score_type_save(self):
        """新增评分任务模版"""
        try:
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_DYNAMIC_CREATE_UPDATE_TEMPLATE_SERVICE?tmodule=GEN_MD"
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            set_dict = {
                        "serviceKey": "GEN_MD$GEN_DYNAMIC_CREATE_UPDATE_TEMPLATE_SERVICE",
            "params": {
                "request": {
                    "id": None,
                    "name": f"自动化_{current_time}",
                    "desc": None,
                    "templateType": "gen_cust_dynamic_form_record_md",
                    "templateInfo": {
                        "header": [
                            {
                                "type": "TextArea",
                                "length": "33",
                                "defaultValue": "-",
                                "showWay": "EDITABLE",
                                "required": "TRUE",
                                "name": "自动化",
                                "index": None
                            }
                        ],
                        "body": [
                            {
                                "u_id": "l9YYu5Qg",
                                "title": "问题组1",
                                "items": [
                                    {
                                        "type": "score",
                                        "u_id": "d7os6CUCu",
                                        "contentText": "111",
                                        "maxScore": 10
                                    }
                                ]
                            }
                        ]
                    }
                }
            }  
            }   
            
            # 使用http工具发送请求
            response = self.http.post(url, json=set_dict)
            
            # 断言响应成功
            AssertHelper.assert_response_success(response)
            
            # 获得模版详情
            cust_detail = response.get('data', {}).get('data')
            Loggers.info(f"评分模版: {cust_detail}")
            
            # 断言模版详情不为空
            AssertHelper.assert_by_operator(cust_detail, "not_empty", None)
            
            # 保存新增评分模板的ID
            template_id = cust_detail.get('id')
            if template_id:
                self.template_id = template_id
                Loggers.info(f"新增评分模板ID: {template_id}")
            else:
                Loggers.warning("未获取到评分模板ID")
            
            # 判断新增模版成功后的单据状态是否为DRAFT
            template_state = cust_detail.get('state')
            if template_state == 'DRAFT':
                Loggers.info(f"评分模板状态验证成功: {template_state}")
            else:
                Loggers.error(f"评分模板状态验证失败，期望状态: DRAFT，实际状态: {template_state}")
                raise AssertionError(f"评分模板状态验证失败，期望状态: DRAFT，实际状态: {template_state}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分模版",
        title="评分模版分页查询接口",
        description="验证评分模版分页查询接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分模版", "分页查询"]
    )
    def test_partner_type_query_page(self):
        """
        评分模版分页查询用例
        """
        try:
            # 获取接口路径和参数模板
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_dynamic_form_template_md"
            set_dict = {
    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
    "containerKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-TERP_MIGRATE$dynamic_form-table-container-ERP_SCM$gen_dynamic_form_template_md",
    "viewCondition": {
        "conditionKey": "XDy6ScIpLiDu0jgX-fB6F",
        "rightValues": {

        }
    },
    "appId": 0,
    "teamId": 22,
    "serviceKey": "GEN_MD$SYS_PagingDataService",
    "params": {
        "request": {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "sortOrders": None,
                "systemParams": {
                    "viewCondition": {
                        "conditionKey": "XDy6ScIpLiDu0jgX-fB6F",
                        "rightValues": {

                        }
                    }
                }
            }
        },
        "modelKey": "GEN_MD$gen_dynamic_form_template_md"
    }
}

            
            # 使用http工具发送请求
            response = self.http.post(url, json=set_dict)
            
            # 断言响应成功
            AssertHelper.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分模版启用",
        title="评分模版启用接口",
        description="验证评分模版启用接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分模版", "启用"]
    )
    def test_cust_man_type_enable(self):
        """测试评分模版启用接口"""
        try:
            if not hasattr(self, 'template_id'):
                self.test_score_type_save()
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE?tmodule=GEN_MD"
            set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
                "viewTitle": "list",
                "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-kGGJDpULirjk7ROCIFYaS",
                "buttonName": "启用",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE",
                "params": {
                    "request": {
                        "id": self.template_id 
                    }
                }
            }
            response = self.http.post(url, json=set_dict)
            AssertHelper.assert_response_success(response)
            # 获得模版详情
            cust_detail = response.get('data', {}).get('data')
            Loggers.info(f"评分模版: {cust_detail}")
                        
            # 判断新增模版启用成功后的单据状态是否为ENABLED
            template_state = cust_detail.get('state')
            if template_state == 'ENABLED':
                Loggers.info(f"评分模板状态验证成功: {template_state}")
            else:
                Loggers.error(f"评分模板状态验证失败，期望状态: ENABLED: {template_state}")
                raise AssertionError(f"评分模板状态验证失败，期望状态: ENABLED: {template_state}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分模版禁用删除",
        title="评分模版禁用删除接口",
        description="验证评分模版禁用删除接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分模版", "禁用", "删除"]
    )
    def test_cust_man_type_disable(self):
        """测试评分模版禁用接口"""
        try:
            if not hasattr(self, 'template_id'):
                self.test_score_type_save()
            
            # 先启用模板，因为只有ENABLED状态的模板才能被禁用
            if not hasattr(self, 'template_enabled'):
                enable_url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE?tmodule=GEN_MD"
                enable_dict = {
                    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
                    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
                    "viewTitle": "list",
                    "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-kGGJDpULirjk7ROCIFYaS",
                    "buttonName": "启用",
                    "appId": 0,
                    "teamId": 22,
                    "serviceKey": "GEN_MD$GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE",
                    "params": {
                        "request": {
                            "id": self.template_id 
                        }
                    }
                }
                enable_response = self.http.post(enable_url, json=enable_dict)
                AssertHelper.assert_response_success(enable_response)
                self.template_enabled = True
                Loggers.info("模板已启用，准备进行禁用操作")
            
            # 执行禁用操作
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_DYNAMIC_DISABLE_TEMPLATE_SERVICE?tmodule=GEN_MD"
            set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
                "viewTitle": "list",
                "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-5n_J7lbp7iqFXG5tA7UU2",
                "buttonName": "禁用",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$GEN_DYNAMIC_DISABLE_TEMPLATE_SERVICE",
                "params": {
                    "request": {
                        "id": self.template_id 
                    }
                }
            }
            response = self.http.post(url, json=set_dict)
            AssertHelper.assert_response_success(response)
            # 获得模版详情
            cust_detail = response.get('data', {}).get('data')
            Loggers.info(f"评分模版: {cust_detail}")
                        
            # 判断新增模版启用成功后的单据状态是否为DISABLED
            template_state = cust_detail.get('state')
            if template_state == 'DISABLED':
                Loggers.info(f"评分模板状态验证成功: {template_state}")
            else:
                Loggers.error(f"评分模板状态验证失败，期望状态: DISABLED: {template_state}")
                raise AssertionError(f"评分模板状态验证失败，期望状态: DISABLED: {template_state}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务新增",
        title="分任务新增接口",
        description="验证分任务新增接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分任务", "新增"]
    )    
    def test_cust_SCORE_type_save(self):
        """测试评分任务新增接口"""
        try:
            # 先调用用户分页查询接口验证
            user_url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24user"
            user_set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:edit",
                "containerKey": "",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$SYS_PagingDataService",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "conditionGroup": None,
                            "sortOrders": None,
                            "keyword": None
                        }
                    },
                    "modelKey": "GEN_MD$user"
                }
            }
            
            # 调用用户分页查询接口
            user_response = self.http.post(user_url, json=user_set_dict)
            
            # 断言用户分页查询接口响应成功
            AssertHelper.assert_response_success(user_response)
            
            # 获取用户数据
            user_data = user_response.get('data', {}).get('data', {}).get('data', [])
            Loggers.info(f"用户分页查询结果: {user_data}")
            
            # 断言用户数据不为空
            AssertHelper.assert_by_operator(user_data, "not_empty", None)
            
            # 验证用户数据格式
            if user_data and len(user_data) > 0:
                first_user = user_data[0]
                Loggers.info(f"第一个用户信息: {first_user}")
                # 验证用户数据包含必要字段
                if 'id' in first_user and 'username' in first_user:
                    Loggers.info("用户数据格式验证通过")
                else:
                    Loggers.warning("用户数据格式可能不完整")
            
            # 评分模板分页查询接口验证
            template_url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_dynamic_form_template_md"
            template_set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:edit",
                "containerKey": "",
                "viewCondition": {
                    "conditionKey": "vBJ8lq6CwCbcdqatgbibr",
                    "rightValues": {}
                },
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$SYS_PagingDataService",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "conditionGroup": None,
                            "sortOrders": None,
                            "keyword": None
                        }
                    },
                    "modelKey": "GEN_MD$gen_dynamic_form_template_md"
                }
            }
            # 调用评分模板分页查询接口
            template_response = self.http.post(template_url, json=template_set_dict)
            # 断言评分模板分页查询接口响应成功
            AssertHelper.assert_response_success(template_response)
            # 获取评分模板数据
            template_data = template_response.get('data', {}).get('data', {}).get('data', [])
            Loggers.info(f"评分模板分页查询结果: {template_data}")
            # 断言评分模板数据不为空
            AssertHelper.assert_by_operator(template_data, "not_empty", None)
            
            # 获取状态为ENABLED的第一个模版id
            enabled_template = None
            for template in template_data:
                if template.get('state') == 'ENABLED':
                    enabled_template = template
                    break
            
            if enabled_template:
                enabled_template_id = enabled_template.get('id')
                Loggers.info(f"获取到状态为ENABLED的模版ID: {enabled_template_id}")
                Loggers.info(f"模版名称: {enabled_template.get('name')}")
                # 保存到实例变量中，供后续使用
                self.enabled_template_id = enabled_template_id
            else:
                Loggers.warning("未找到状态为ENABLED的模版")
            
            # 继续执行评分任务新增接口
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_SURVEY_MISSION_SAVE_UPDATE_ACTION_SERVICE?tmodule=GEN_MD"
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            set_dict ={
    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:edit",
    "viewTitle": "edit",
    "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW-TERP_MIGRATE$survey_missionn_new-editView-footer-save",
    "buttonName": "提交",
    "appId": 0,
    "teamId": 22,
    "serviceKey": "GEN_MD$GEN_SURVEY_MISSION_SAVE_UPDATE_ACTION_SERVICE",
    "params": {
        "request": {
            "title": f"自动化_{current_time}",
            "surveyType": "CUST",
            "surveyObj": 2519001,
            "startDate": 1735660800000,
            "id": None,
            "endDate": 1750780800000,
            "surveyMissionItem": [
                {
                    "user": {
                        "id": 476102974181637,
                        "username": "admin",
                        "mobile": "130****0000",
                        "nickname": "admin",
                        "status": True
                    },
                    "template": {
                        "id": self.enabled_template_id,
                        "context": {

                        },
                        "version": 1,
                        "deleted": 0,
                        "createdAt": 1691572640000,
                        "updatedAt": 1691572640000,
                        "name": "string",
                        "desc": "string",
                        "templateType": "gen_vend_dynamic_form_record_md",
                        "templateInfo": {
                            "head": [
                                {
                                    "id": 1
                                }
                            ],
                            "body": [
                                {
                                    "id": 1
                                }
                            ]
                        },
                        "state": "DRAFT"
                    },
                    "weight": 1
                }
            ]
        }
    }
}
            
            # 调用评分任务新增接口
            response = self.http.post(url, json=set_dict)
            
            # 断言评分任务新增接口响应成功
            AssertHelper.assert_response_success(response)
            
            # 获得评分任务详情
            task_detail = response.get('data', {}).get('data')
            Loggers.info(f"评分任务详情: {task_detail}")
            
            # 断言评分任务详情不为空
            AssertHelper.assert_by_operator(task_detail, "not_empty", None)
            
            # 保存新增评分任务的ID
            task_id = task_detail.get('id')
            task_code = task_detail.get('missionCode')
            task_title = task_detail.get('title')
            if task_id:
                self.task_id = task_id
                self.task_code = task_code
                self.task_title = task_title
                Loggers.info(f"新增评分任务ID: {task_id}")
                Loggers.info(f"新增评分任务Code: {task_code}")
                Loggers.info(f"新增评分任务Title: {task_title}")
            else:
                Loggers.warning("未获取到评分任务ID")
                Loggers.warning("未获取到评分任务Code")
                Loggers.warning("未获取到评分任务Title")
            
            # 判断新增评分任务成功后的状态是否为DRAFT
            task_state = task_detail.get('state')
            if task_state == 'DRAFT':
                Loggers.info(f"评分任务状态验证成功: {task_state}")
            else:
                Loggers.error(f"评分任务状态验证失败，期望状态: DRAFT，实际状态: {task_state}")
                raise AssertionError(f"评分任务状态验证失败，期望状态: DRAFT，实际状态: {task_state}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务分页查询",
        title="评分任务分页查询接口",
        description="验证评分任务分页查询接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分任务", "分页查询"]
    ) 
    def test_cust_SCORE_type_query_page(self):
        """测试评分任务分页查询接口"""
        try:
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_survey_mission_md"
            set_dict = {
    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:list",
    "containerKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW-TERP_MIGRATE$survey_missionn_new-table-container-TERP_MIGRATE$gen_survey_mission_md",
    "viewCondition": {
        "conditionKey": "tSTywjzfLKwB9lktoP84W",
        "rightValues": {

        }
    },
    "appId": 0,
    "teamId": 22,
    "serviceKey": "GEN_MD$SYS_PagingDataService",
    "params": {
        "request": {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "sortOrders": None,
                "systemParams": {
                    "viewCondition": {
                        "conditionKey": "tSTywjzfLKwB9lktoP84W",
                        "rightValues": {

                        }
                    }
                },
                "conditionGroup": None
            }
        },
        "modelKey": "GEN_MD$gen_survey_mission_md"
    }
}
            # 使用http工具发送请求
            response = self.http.post(url, json=set_dict)
            
            # 断言响应成功
            AssertHelper.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="评分任务发布",
        title="评分任务发布接口",
        description="验证评分任务发布接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["评分任务", "发布"]
    )
    def test_cust_SCORE_type_publish(self):
        """测试评分任务发布接口"""
        try:
            # 确保先创建评分任务
            if not hasattr(self, 'task_code'):
                self.test_cust_SCORE_type_save()
            
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE?tmodule=GEN_MD"
            set_dict = {
    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:list",
    "viewTitle": "list",
    "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW-X1q3L5Szt7ZYTPYHqi4yI",
    "buttonName": "发布",
    "appId": 0,
    "teamId": 22,
    "serviceKey": "GEN_MD$GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE",
    "params": {
        "request": {
            "missionCode": self.task_code,
            "title": self.task_title,
            "surveyObj": 2519001,
            "startDate": 1735660800000,
            "endDate": 1750780800000,
            "state": "DRAFT",
            "id": self.task_id
        }
    }
}
            response = self.http.post(url, json=set_dict)
            AssertHelper.assert_response_success(response)
            
            # 评分任务发布接口只返回成功状态，不返回详细数据
            Loggers.info("评分任务发布成功")
            
            # 由于发布接口不返回详细数据，我们验证响应成功即可
            # 如果需要验证状态变化，可以通过查询接口重新获取任务详情
            Loggers.info("评分任务状态验证：发布接口调用成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分模版删除",
        title="评分模版删除接口",
        description="验证评分模版删除接口的功能性",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["评分模版", "删除"]
    )
    def test_cust_man_type_delete(self):
        """测试评分模版删除接口"""
        try:
            if not hasattr(self, 'template_id'):
                self.test_score_type_save()
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_BatchDeleteDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_dynamic_form_template_md"
            set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
                "viewTitle": "list",
                "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-TERP_MIGRATE$dynamic_form-batch-actions-1-button-2",
                "buttonName": "删除",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$SYS_BatchDeleteDataService",
                "params": {
                    "request": {
                        "ids": [self.template_id]
                    },
                    "modelKey": "GEN_MD$gen_dynamic_form_template_md"
                }
            }
            response = self.http.post(url, json=set_dict)
            AssertHelper.assert_response_success(response)
            
            # 删除接口通常只返回成功状态，不返回详细数据
            Loggers.info("评分模板删除成功")
            Loggers.info(f"已删除模板ID: {self.template_id}")
            
            # 删除后检查列表返回数据中有无已删除数据
            check_url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_dynamic_form_template_md"
            check_set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW:list",
                "containerKey": "GEN_MD$GEN_CUSTOMER_SCORE_TEMPLATE_VIEW-TERP_MIGRATE$dynamic_form-table-container-GEN_MD$gen_dynamic_form_template_md",
                "viewCondition": {
                    "conditionKey": "XDy6ScIpLiDu0jgX-fB6F",
                    "rightValues": {}
                },
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$SYS_PagingDataService",
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "sortOrders": None,
                            "systemParams": {
                                "viewCondition": {
                                    "conditionKey": "XDy6ScIpLiDu0jgX-fB6F",
                                    "rightValues": {}
                                }
                            }
                        }
                    },
                    "modelKey": "GEN_MD$gen_dynamic_form_template_md"
                }
            }
            
            # 调用分页查询接口检查删除结果
            check_response = self.http.post(check_url, json=check_set_dict)
            AssertHelper.assert_response_success(check_response)
            
            # 获取模板列表数据
            template_list = check_response.get('data', {}).get('data', {}).get('data', [])
            Loggers.info(f"删除后模板列表查询结果: {template_list}")
            
            # 检查已删除的模板ID是否还在列表中
            deleted_template_found = False
            for template in template_list:
                if template.get('id') == self.template_id:
                    deleted_template_found = True
                    Loggers.error(f"删除验证失败：模板ID {self.template_id} 仍然存在于列表中")
                    break
            
            if not deleted_template_found:
                Loggers.info(f"删除验证成功：模板ID {self.template_id} 已从列表中移除")
            else:
                raise AssertionError(f"删除验证失败：模板ID {self.template_id} 仍然存在于列表中")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务删除",
        title="评分任务删除接口",
        description="验证评分任务删除接口的功能性",
        severity="blocker",
        order=6,
        smoke=True,
        tags=["评分任务", "删除"]
    )
    def test_cust_SCORE_type_delete(self):
        """测试评分任务删除接口"""
        try:
            # 确保先创建评分任务
            if not hasattr(self, 'task_id'):
                self.test_cust_SCORE_type_save()
            
            url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_BatchDeleteDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_survey_mission_md"
            set_dict = {
                "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
                "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:list",
                "viewTitle": "list",
                "buttonKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW-TERP_MIGRATE$survey_missionn_new-batch-actions-1-button-2",
                "buttonName": "删除",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "GEN_MD$SYS_BatchDeleteDataService",
                "params": {
                    "request": {
                        "ids": [self.task_id]
                    },
                    "modelKey": "GEN_MD$gen_survey_mission_md"
                }
            }
            
            response = self.http.post(url, json=set_dict)
            AssertHelper.assert_response_success(response)
            
            # 删除接口通常只返回成功状态，不返回详细数据
            Loggers.info("评分任务删除成功")
            Loggers.info(f"已删除任务ID: {self.task_id}")
            
            # 删除后检查列表返回数据中有无已删除数据
            check_url = "https://t-erp-portal-test.app.terminus.io/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService?tmodule=GEN_MD&modelKey=GEN_MD%24gen_survey_mission_md"
            check_set_dict ={
    "sceneKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW",
    "viewKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW:list",
    "containerKey": "GEN_MD$GEN_CUSTOMER_SCORE_TASK_VIEW-TERP_MIGRATE$survey_missionn_new-table-container-TERP_MIGRATE$gen_survey_mission_md",
    "viewCondition": {
        "conditionKey": "tSTywjzfLKwB9lktoP84W",
        "rightValues": {

        }
    },
    "appId": 0,
    "teamId": 22,
    "serviceKey": "GEN_MD$SYS_PagingDataService",
    "params": {
        "request": {
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "systemParams": {
                    "viewCondition": {
                        "conditionKey": "tSTywjzfLKwB9lktoP84W",
                        "rightValues": {

                        }
                    }
                },
                "conditionGroup": None
            }
        },
        "modelKey": "GEN_MD$gen_survey_mission_md"
    }
}
            
            # 调用分页查询接口检查删除结果
            check_response = self.http.post(check_url, json=check_set_dict)
            AssertHelper.assert_response_success(check_response)
            
            # 获取任务列表数据
            task_list = check_response.get('data', {}).get('data', {}).get('data', [])
            Loggers.info(f"删除后任务列表查询结果: {task_list}")
            
            # 检查已删除的任务ID是否还在列表中
            deleted_task_found = False
            for task in task_list:
                if task.get('id') == self.task_id:
                    deleted_task_found = True
                    Loggers.error(f"删除验证失败：任务ID {self.task_id} 仍然存在于列表中")
                    break
            
            if not deleted_task_found:
                Loggers.info(f"删除验证成功：任务ID {self.task_id} 已从列表中移除")
            else:
                raise AssertionError(f"删除验证失败：任务ID {self.task_id} 仍然存在于列表中")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

        