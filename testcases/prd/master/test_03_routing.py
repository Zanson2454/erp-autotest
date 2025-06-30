# -*- coding: utf-8 -*-
"""
工艺路线管理测试用例
主要包含BOM信息查询相关的测试
"""
import allure
import pytest
import time
import random
import uuid
from testcases.prd import PrdBaseTest
from utils.report_util import a
from utils.param_util import ParamUtil
from utils.mysql_util import DBManager
from testcases.prd.basic.init_config import PrdConfigInitializer

@allure.epic("生产管理")
@allure.feature("主数据管理")
@allure.story("工艺路线管理")
class TestRouting(PrdBaseTest):
    """工艺路线管理测试类"""
    
    # 保存测试过程中的数据
    routing_data = {}
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("工艺路线管理测试类初始化")
        
        # 初始化配置管理器并确保基础配置存在
        cls.config_initializer = PrdConfigInitializer()
        cls.config_initializer.ensure_configs_exist()
        
        # 获取测试数据
        cls.test_org = cls.base_info["inv_org_info"]
        cls.test_material = cls.base_info["prd_mat_info"]
        
        # 获取物料基本单位ID
        sql = f"""
            SELECT base_uom_id
            FROM gen_mat_md 
            WHERE id = {cls.test_material["id"]}
            AND deleted = 0
        """
        result = DBManager.query(sql)
        assert result, "未找到物料基本单位"
        cls.base_uom_id = result[0]["base_uom_id"]
        cls.logger.info(f"物料基本单位ID: {cls.base_uom_id}")
        
        # 获取工艺路线基础配置
        cls._init_routing_configs()
        
        # 获取控制码信息
        cls._init_control_keys()
        
        # 初始化工序信息
        cls._init_operations()
    
    @classmethod
    def _init_routing_configs(cls):
        """初始化工艺路线相关配置"""
        try:
            # 查询工艺路线类型
            sql = """
                SELECT 
                    id,
                    type_code as typeCode,
                    type_name as typeName
                FROM prd_routings_type_cf 
                WHERE deleted = 0 
                AND type_name = '标准生产'
            """
            routing_type = DBManager.query(sql)[0]
            cls.ROUTING_TYPE = routing_type
            cls.logger.info(f"工艺路线类型: {routing_type['typeName']} (ID: {routing_type['id']})")
            
            # 查询工艺路线用途
            sql = """
                SELECT 
                    id,
                    usage_code as usageCode,
                    usage_name as usageName
                FROM prd_routings_usage_cf 
                WHERE deleted = 0 
                AND usage_name = '生产'
            """
            routing_usage = DBManager.query(sql)[0]
            cls.ROUTING_USAGE = routing_usage
            cls.logger.info(f"工艺路线用途: {routing_usage['usageName']} (ID: {routing_usage['id']})")
            
            # 查询工艺路线状态
            sql = """
                SELECT 
                    id,
                    status_code as statusCode,
                    status_name as statusName,
                    is_prd as isPrd,
                    is_qc as isQc,
                    is_cost as isCost
                FROM prd_routings_status_cf 
                WHERE deleted = 0 
                AND status_name = '下达'
            """
            routing_status = DBManager.query(sql)[0]
            cls.ROUTING_STATUS = routing_status
            cls.logger.info(f"工艺路线状态: {routing_status['statusName']} (ID: {routing_status['id']})")
            
        except Exception as e:
            cls.logger.error(f"初始化工艺路线配置失败: {str(e)}")
            raise

    @classmethod
    def _init_control_keys(cls):
        """初始化控制码信息"""
        try:
            # 查询关键工序和入库工序的控制码
            sql = """
                SELECT 
                    id,
                    control_key_code as controlKeyCode,
                    control_key_name as controlKeyName,
                    is_subcontracting_operation as isSubcontractingOperation,
                    is_key_operation as isKeyOperation,
                    is_aut_receipt as isAutReceipt
                FROM prd_control_keys_cf 
                WHERE deleted = 0 
                AND control_key_name IN ('关键工序', '入库工序')
                ORDER BY control_key_code
            """
            control_keys = DBManager.query(sql)
            
            # 保存控制码信息
            cls.CONTROL_KEYS = {
                'KEY': next(key for key in control_keys if key['controlKeyName'] == '关键工序'),  # 关键工序
                'RECEIPT': next(key for key in control_keys if key['controlKeyName'] == '入库工序')  # 入库工序
            }
            
            cls.logger.info("控制码信息初始化完成：")
            for key_type, key_info in cls.CONTROL_KEYS.items():
                cls.logger.info(f"{key_type}: {key_info['controlKeyName']} (ID: {key_info['id']})")
                
        except Exception as e:
            cls.logger.error(f"初始化控制码信息失败: {str(e)}")
            raise

    @classmethod
    def _init_operations(cls):
        """初始化工序信息，从数据库获取最新的工作中心数据"""
        try:
            # 查询最新创建的下料、组装、打包工作中心
            sql = """
                SELECT 
                    id, wc_code as wcCode, wc_name as wcName 
                FROM prd_work_centor_header_md 
                WHERE deleted = 0 
                AND wc_name LIKE '%下料工作中心%' 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            cutting_wc = DBManager.query(sql)[0]
            
            sql = sql.replace('下料工作中心', '组装工作中心')
            assembly_wc = DBManager.query(sql)[0]
            
            sql = sql.replace('组装工作中心', '打包工作中心')
            packing_wc = DBManager.query(sql)[0]
            
            # 定义工序信息
            cls.OPERATIONS = [
                {
                    "operationCode": 10,
                    "operationName": "工序1",
                    "wcCodeId": {
                        "id": cutting_wc["id"],
                        "wcCode": cutting_wc["wcCode"],
                        "wcName": cutting_wc["wcName"]
                    },
                    "controlKeyId": cls.CONTROL_KEYS['KEY']  # 使用查询到的关键工序控制码
                },
                {
                    "operationCode": 20,
                    "operationName": "工序2",
                    "wcCodeId": {
                        "id": assembly_wc["id"],
                        "wcCode": assembly_wc["wcCode"],
                        "wcName": assembly_wc["wcName"]
                    },
                    "controlKeyId": cls.CONTROL_KEYS['KEY']  # 使用查询到的关键工序控制码
                },
                {
                    "operationCode": 30,
                    "operationName": "工序3",
                    "wcCodeId": {
                        "id": packing_wc["id"],
                        "wcCode": packing_wc["wcCode"],
                        "wcName": packing_wc["wcName"]
                    },
                    "controlKeyId": cls.CONTROL_KEYS['RECEIPT']  # 使用查询到的入库工序控制码
                }
            ]
            
            cls.logger.info("工序信息初始化完成：")
            for op in cls.OPERATIONS:
                cls.logger.info(f"工序 {op['operationName']}: {op['wcCodeId']['wcName']}")
                
        except Exception as e:
            cls.logger.error(f"初始化工序信息失败: {str(e)}")
            raise

    @pytest.mark.run(order=3)
    @allure.title("查询BOM信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_01_query_bom(self):
        """测试查询BOM信息"""
        try:
            with a.step("1. 准备查询参数"):
                # 获取API配置
                api_path = self.get_api_path("查询BOM服务")
                params, url = self.get_api_params(api_path)
                
                # 准备请求数据
                query_data = {
                    "params": {
                        "request": {
                            "invOrgId": {"id": self.test_org["id"]},
                            "matId": {"id": self.test_material["id"]},
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 20
                            }
                        }
                    }
                }
                
                # 设置请求参数
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    list(query_data.keys()),
                    []
                )
                ParamUtil.set_request_params(filtered_params, query_data)
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                a.json(filtered_params, "请求数据")
            with a.step("2. 发送查询请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                self.logger.info("=== 响应结果详情 ===")
                self.logger.info(f"响应状态: {result.get('success')}")
                self.logger.info(f"响应消息: {result.get('message')}")
                self.logger.info(f"响应数据: {result.get('data')}")
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data is not None, "未返回数据"
                
                # 获取BOM列表
                bom_list = response_data.get("data", []) if isinstance(response_data, dict) else []
                assert len(bom_list) > 0, "未找到BOM数据"
                
                # 找到匹配的BOM记录
                matching_bom = None
                for bom in bom_list:
                    if not isinstance(bom, dict):
                        continue
                    
                    inv_org_id = bom.get("invOrgId", {}).get("id") if isinstance(bom.get("invOrgId"), dict) else None
                    mat_id = bom.get("matId", {}).get("id") if isinstance(bom.get("matId"), dict) else None
                    status_id = bom.get("statusId", {}).get("id") if isinstance(bom.get("statusId"), dict) else None
                    
                    if (inv_org_id == self.test_org["id"] and 
                        mat_id == self.test_material["id"]):  
                        matching_bom = bom
                        # 保存BOM相关信息到类变量
                        TestRouting.routing_data.update({
                            'bom_vrs': bom.get("vrsCode"),
                            'bom_header_id': bom.get("id"),
                            'bom_date_from': bom.get("dateFrom")
                        })
                        self.logger.info(f"找到匹配的BOM记录，版本号: {TestRouting.routing_data['bom_vrs']}")
                        break
                
                assert matching_bom is not None, "未找到匹配的BOM数据"
                bom_info = matching_bom
                
                assert TestRouting.routing_data['bom_vrs'], "未获取到BOM版本号"
                assert TestRouting.routing_data['bom_header_id'], "未获取到BOM头ID"
                assert TestRouting.routing_data['bom_date_from'], "未获取到BOM生效时间"
                
                self.logger.info(f"BOM信息查询成功，版本号: {TestRouting.routing_data['bom_vrs']}")
                
        except Exception as e:
            self.logger.error(f"查询BOM信息失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.title("获取物料组件")
    @allure.severity(allure.severity_level.NORMAL)
    def test_02_get_material_components(self):
        """测试获取物料组件信息"""
        try:
            with a.step("1. 准备查询参数"):
                # 获取API配置
                api_path = self.get_api_path("渲染工艺路线物料组件服务")
                params, url = self.get_api_params(api_path)
                
                # 准备请求数据
                query_data = {
                    "params": {
                        "request": {
                            "bomVrs": TestRouting.routing_data['bom_vrs'],  # 使用类变量中的BOM版本号
                            "routingHeadId": None,
                            "invOrgId": self.test_org["id"],
                            "matId": self.test_material["id"]
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {query_data}")
                a.json(query_data, "请求数据")
            
            with a.step("2. 发送查询请求"):
                # 发送请求
                result = self.http.post(url, json=query_data)
                a.json(result, "响应数据")

            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {})
                assert response_data is not None, "未返回数据"
                
                # 保存组件列表供后续使用
                data_list = response_data.get("data", [])
                components_list = []
                for item in data_list:
                    if isinstance(item, dict) and "prdBomItemMdId" in item:
                        component = {
                            "context": {},
                            "prdBomItemMdId": item["prdBomItemMdId"],
                            "isBackflush": False
                        }
                        components_list.append(component)
                
                # 保存到类变量
                TestRouting.routing_data['components_list'] = components_list
                
                assert TestRouting.routing_data['components_list'], "未获取到物料组件列表"
                
                self.logger.info(f"物料组件信息获取成功，组件数量: {len(TestRouting.routing_data['components_list'])}")
                
        except Exception as e:
            self.logger.error(f"获取物料组件失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @allure.title("创建工艺路线")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_03_create_routing(self):
        """测试创建工艺路线"""
        try:
            with a.step("1. 准备创建数据"):
                # 获取API配置
                api_path = self.get_api_path("保存工艺路线服务")
                params, url = self.get_api_params(api_path)
                
                # 生成唯一编码，使用UUID
                unique_id = str(uuid.uuid4())[:8]
                routing_code = f"test_{unique_id}"
                TestRouting.routing_data['routing_code'] = routing_code  # 保存到类变量
                routing_name = f"自动化版本_{unique_id}"
                routing_desc = f"自动化版本_{unique_id}"
                
                # 准备工序列表数据
                item_list = []
                for operation in self.OPERATIONS:
                    item = operation.copy()
                    item.update({
                        "validTo": "9999-12-30T16:00:00.000Z",
                        "routingsItemQty": 1,
                        "uomId": {"id": self.base_uom_id},
                        "validFrom": TestRouting.routing_data['bom_date_from']
                    })
                    item_list.append(item)
                
                # 准备请求数据
                query_data = {
                    "params": {
                        "request": {
                            "invOrgId": {
                                "id": self.test_org["id"]
                            },
                            "matId": {
                                "id": self.test_material["id"]
                            },
                            "routingsName": routing_name,
                            "routingsUsageId": self.ROUTING_USAGE,  # 使用查询到的用途
                            "routingsType": self.ROUTING_TYPE,  # 使用查询到的类型
                            "id": None,
                            "vrsCode": routing_code,
                            "vrsName": routing_desc,
                            "bomHeaderId": {
                                "id": TestRouting.routing_data['bom_header_id'],
                                "invOrgId": {"id": self.test_org["id"]},
                                "dateFrom": TestRouting.routing_data['bom_date_from'],
                                "dateTo": 253402185600000
                            },
                            "baseQty": 1,
                            "batchFrom": 0,
                            "batchTo": 999999,
                            "uomId": {"id": self.base_uom_id},
                            "routingsStatusId": self.ROUTING_STATUS,  # 使用查询到的状态
                            "validFrom": TestRouting.routing_data['bom_date_from'],
                            "validTo": "9999-12-30T16:00:00.000Z",
                            "itemList": item_list,
                            "componentsList": TestRouting.routing_data['components_list']
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {query_data}")
                a.json(query_data, "请求数据")
            
            with a.step("2. 发送创建请求"):
                # 发送请求
                result = self.http.post(url, json=query_data)
                self.logger.info("=== 响应结果详情 ===")
                self.logger.info(f"响应状态: {result.get('success')}")
                self.logger.info(f"响应消息: {result.get('message')}")
                self.logger.info(f"响应数据: {result.get('data')}")
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                self.logger.info("工艺路线创建成功")
                
        except Exception as e:
            self.logger.error(f"创建工艺路线失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=6)
    @allure.title("查询工艺路线详情")
    @allure.severity(allure.severity_level.NORMAL)
    def test_04_get_routing_detail(self):
        """测试查询工艺路线详情"""
        try:
            with a.step("1. 通过SQL查询工艺路线ID"):
                # SQL查询工艺路线ID
                sql = f"select id from prd_routings_header_md where deleted=0 and vrs_code='{TestRouting.routing_data['routing_code']}'"
                self.logger.info(f"查询SQL: {sql}")
                
                # 执行SQL查询
                result = DBManager.query(sql)
                assert result, f"未找到工艺路线ID，vrs_code={TestRouting.routing_data['routing_code']}"
                routing_id = result[0]["id"]
                self.logger.info(f"查询到工艺路线ID: {routing_id}")
                
            with a.step("2. 准备查询详情参数"):
                # 获取API配置
                api_path = self.get_api_path("工艺路线-抬头数据表-根据ID查找数据服务")
                params, url = self.get_api_params(api_path)
                
                # 准备请求数据
                query_data = {
                    "params": {
                        "request": {
                            "id": routing_id
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {query_data}")
                a.json(query_data, "请求数据")
            
            with a.step("3. 发送查询请求"):
                # 发送请求
                result = self.http.post(url, json=query_data)
                self.logger.info("=== 响应结果详情 ===")
                self.logger.info(f"响应状态: {result.get('success')}")
                self.logger.info(f"响应消息: {result.get('message')}")
                self.logger.info(f"响应数据: {result.get('data')}")
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 验证返回数据
                response_data = result.get("data", {}).get("data", {})
                assert response_data is not None, "未返回数据"
                
                # 保存详情数据供后续使用
                TestRouting.routing_data['routing_detail'] = response_data
                
                # 验证工艺路线基本信息
                assert response_data.get("vrsCode") == TestRouting.routing_data['routing_code'], "工艺路线编码不匹配"
                
                # 验证物料组件列表
                components_list = response_data.get("componentsList", [])
                assert len(components_list) == 3, "物料组件数量不匹配"
                
                # 验证每个物料组件的信息
                for component in components_list:
                    bom_item = component.get("prdBomItemMdId", {})
                    assert bom_item.get("id") is not None, "物料组件ID不存在"
                    assert bom_item.get("matId", {}).get("id") is not None, "物料ID不存在"
                    assert bom_item.get("qty") in [10.0, 20.0, 30.0], "物料数量不在预期范围内"
                
                # 验证工序明细列表
                item_list = response_data.get("itemList", [])
                assert len(item_list) == len(self.OPERATIONS), "工序数量不匹配"
                
                # 验证每个工序的信息
                for i, (item, expected) in enumerate(zip(item_list, self.OPERATIONS)):
                    assert item.get("operationCode") == expected["operationCode"], f"工序{i+1}编码不匹配"
                    assert item.get("operationName") == expected["operationName"], f"工序{i+1}名称不匹配"
                    assert item.get("wcCodeId", {}).get("id") == expected["wcCodeId"]["id"], f"工序{i+1}工作中心不匹配"
                    assert item.get("controlKeyId", {}).get("id") == expected["controlKeyId"]["id"], f"工序{i+1}控制码不匹配"
                    assert item.get("routingsItemQty") == 1.00, f"工序{i+1}数量不匹配"
                    assert item.get("uomId", {}).get("id") == self.base_uom_id, f"工序{i+1}单位不匹配"
                
                self.logger.info("工艺路线详情查询成功，物料组件和工序明细验证通过")
                
        except Exception as e:
            self.logger.error(f"查询工艺路线详情失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=7)
    @allure.title("分配工序并保存")
    @allure.severity(allure.severity_level.NORMAL)
    def test_05_assign_operation(self):
        """测试分配工序并保存"""
        try:
            with a.step("1. 准备保存数据"):
                # 获取API配置
                api_path = self.get_api_path("保存工艺路线服务")
                params, url = self.get_api_params(api_path)
                
                # 使用test_04中获取的详情数据
                routing_detail = TestRouting.routing_data['routing_detail']
                
                # 为每个物料组件分配工序
                components_list = routing_detail.get("componentsList", [])
                item_list = routing_detail.get("itemList", [])
                
                # 分配工序：第一个组件分配到工序1，第二个到工序2，第三个到工序3
                for i, component in enumerate(components_list):
                    component["prdRoutingsItemMdId"] = {
                        "id": item_list[i]["id"],
                        "context": {},
                        "version": 1,
                        "deleted": 0,
                        "createdAt": routing_detail["validFrom"],
                        "updatedAt": routing_detail["validFrom"],
                        "createdBy": 540175374525637,
                        "updatedBy": 540175374525637,
                        "operationCode": item_list[i]["operationCode"],
                        "operationName": item_list[i]["operationName"],
                        "wcCodeId": {"id": item_list[i]["wcCodeId"]["id"]},
                        "validFrom": routing_detail["validFrom"],
                        "validTo": routing_detail["validTo"],
                        "prdRoutingsHeaderMdId": {"id": routing_detail["id"]},
                        "controlKeyId": {"id": item_list[i]["controlKeyId"]["id"]},
                        "routingsItemQty": 1,
                        "uomId": {"id": self.base_uom_id},
                        "invOrgId": {"id": routing_detail["invOrgId"]["id"]},
                        "outsourcingMat": {"id": -1}
                    }
                
                # 准备请求数据
                query_data = {
                    "params": {
                        "request": routing_detail
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {query_data}")
                a.json(query_data, "请求数据")
            
            with a.step("2. 发送保存请求"):
                # 发送请求
                result = self.http.post(url, json=query_data)
                self.logger.info("=== 响应结果详情 ===")
                self.logger.info(f"响应状态: {result.get('success')}")
                self.logger.info(f"响应消息: {result.get('message')}")
                self.logger.info(f"响应数据: {result.get('data')}")
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                self.logger.info("工艺路线工序分配保存成功")
                
        except Exception as e:
            self.logger.error(f"工艺路线工序分配保存失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    def setup_method(self, method):
        """测试方法初始化
        在每个测试方法执行前都确保基础配置存在
        """
        super().setup_method(method)
        # 确保基础配置数据存在
        self.config_initializer.ensure_configs_exist()

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestRouting()
    test.setup_class()
    test.test_01_query_bom()     # 查询BOM信息
    test.test_02_get_material_components()  # 获取物料组件
    test.test_03_create_routing()  # 创建工艺路线
    test.test_04_get_routing_detail()  # 查询工艺路线详情
    test.test_05_assign_operation()  # 分配工序并保存 