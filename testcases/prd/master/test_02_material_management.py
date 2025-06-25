# -*- coding: utf-8 -*-
"""
物料生产视图管理测试用例
包含物料生产视图创建操作
"""
import allure
import pytest
from testcases.prd.master import PrdMasterBaseTest, MaterialType
from utils.report_util import a
from utils.param_util import ParamUtil
from testcases.prd.basic.init_config import PrdConfigInitializer

@allure.epic("生产管理")
@allure.feature("主数据管理")
@allure.story("物料生产视图管理")
class TestMaterialManagement(PrdMasterBaseTest):
    """物料生产视图管理测试类"""
    
    # 保存测试过程中的数据
    material_data = {}
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("物料生产视图管理测试类初始化完成")
        
        # 初始化配置管理器并确保基础配置存在
        cls.config_initializer = PrdConfigInitializer()
        cls.config_initializer.ensure_configs_exist()
        
        # 获取测试数据
        cls.test_org = cls.base_info["inv_org_info"]
        cls.test_inv_loc = cls.base_info["inv_loc_info"]
        cls.test_inv_type = cls.base_info["inv_type_info"]
        # 获取所有测试物料（成品和原材料）
        cls.test_materials = [
            cls.finished_material,  # 成品
            *cls.raw_materials     # 原材料列表
        ]
        cls.logger.info(f"测试物料列表: {cls.test_materials}")
    
    def setup_method(self, method):
        """测试方法初始化
        在每个测试方法执行前都确保基础配置存在
        """
        super().setup_method(method)
        # 确保基础配置数据存在
        self.config_initializer.ensure_configs_exist()
    
    def _get_procurement_type(self, material):
        """根据物料类型获取采购类型"""
        material_type = material["params"]["request"]["genMatTypeCfId"]["matTypeCode"]
        return "E" if material_type == MaterialType.FINISHED.value else "F"
    
    @allure.title("创建物料生产视图")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.run(order=1)
    def test_01_create_material_view(self):
        """测试创建物料生产视图"""
        try:
            # 获取API配置
            api_path = self.get_api_path("物料生产视图创建服务")
            params, url = self.get_api_params(api_path)
            
            with a.step("1. 为所有物料创建生产视图"):
                for material in self.test_materials:
                    self.logger.info(f"正在为物料 {material['id']} 创建生产视图")
                    
                    # 从物料数据中获取单位ID
                    base_uom_id = material["params"]["request"]["baseUomId"]["id"]
                    
                    # 根据物料类型获取采购类型
                    procurement_type = self._get_procurement_type(material)
                    self.logger.info(f"物料 {material['id']} 的采购类型为: {procurement_type}")
                    
                    # 设置请求参数
                    create_data = {
                        "genMatMdId": material["id"],         # 物料主数据ID
                        "invOrgId": self.test_org["id"],      # 库存组织ID
                        "prdUomId": base_uom_id,              # 生产单位ID，从物料数据中获取
                        "factoryStatusId": None,              # 工厂状态ID
                        "invLocId": {"id": self.test_inv_loc["id"]},  # 库存地点ID
                        "productionCycle": 2,              # 生产周期
                        "inspectionCycle": None,              # 检验周期
                        "componentScrap": None,               # 组件损耗
                        "procurementType": procurement_type,   # 采购类型：成品为E，原材料为F
                        "individualColl": None,               # 个体收集
                        "scrapType": "SINGLE",                # 报废类型
                        "insufficientDeliveryTolerance": None,# 欠交容差
                        "excessiveDeliveryTolerance": None,   # 超交容差
                        "componentCostElementId": None,       # 组件成本要素ID
                        "outputCostElementId": None,          # 产出成本要素ID
                        "prdvrsList": [],                      # 生产版本列表
                        "postInvTypeId": {"id": self.test_inv_type["id"]}  # 库存类型（非限制）
                    }
                    
                    filtered_params = ParamUtil.filter_post_body_fields(
                        params,
                        list(create_data.keys()),
                        ["params", "request"]
                    )
                    ParamUtil.set_request_params(filtered_params, create_data)
                    
                    self.logger.info(f"请求URL: {url}")
                    self.logger.info(f"请求参数: {filtered_params}")
                    a.json(filtered_params, "请求数据")
                    
                    with a.step(f"2. 发送创建请求 - 物料 {material['id']}"):
                        result = self.http.post(url, json=filtered_params)
                        a.json(result, "响应数据")
                        
                        # 验证创建结果
                        self.assert_util.assert_response_success(result)
                        self.logger.info(f"物料 {material['id']} 生产视图创建成功")
                        a.text(f"物料 {material['id']} 生产视图创建成功", "验证结果")
                        
                        # 保存创建结果到类变量
                        TestMaterialManagement.material_data[material['id']] = {
                            'procurement_type': procurement_type,
                            'base_uom_id': base_uom_id
                        }
                
            self.logger.info("所有物料的生产视图创建完成")
            
        except Exception as e:
            self.logger.error(f"创建物料生产视图失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    """本地调试入口"""
    test = TestMaterialManagement()
    test.setup_class()
    test.test_01_create_material_view()    # 创建物料生产视图