# -*- coding: utf-8 -*-
"""
工作中心管理测试用例
包含工作中心的创建、查询等操作
"""
import allure
import pytest
from testcases.erp_prd import PrdBaseTest
from utils.report_util import a
from utils.param_util import ParamUtil
from datetime import datetime
import time
from enum import Enum
from testcases.erp_prd.basic.init_config import PrdConfigInitializer

class WorkCenterType(Enum):
    """工作中心类型"""
    CUTTING = "下料"      # 下料工作中心
    ASSEMBLY = "组装"     # 组装工作中心
    PACKING = "打包"      # 打包工作中心

@allure.epic("生产管理")
@allure.feature("主数据管理")
@allure.story("工作中心管理")
class TestWorkCenter(PrdBaseTest):
    """工作中心管理测试类"""
    
    # 保存测试过程中的数据
    work_center_data = {}
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("工作中心管理测试类初始化完成")
        
        # 初始化配置管理器并确保基础配置存在
        cls.config_initializer = PrdConfigInitializer()
        cls.config_initializer.ensure_configs_exist()
        
        # 获取测试数据
        cls.test_org = cls.base_info["inv_org_info"]
        
    def setup_method(self, method):
        """测试方法初始化
        在每个测试方法执行前都确保基础配置存在
        """
        super().setup_method(method)
        # 确保基础配置数据存在
        self.config_initializer.ensure_configs_exist()
    
    def _generate_work_center_code(self, wc_type: WorkCenterType) -> str:
        """
        生成工作中心编码：AUTO_月日_6位时间戳
        例如：AUTO_623_123456
        
        Args:
            wc_type: 工作中心类型
        """
        # 获取当前月日
        current_date = datetime.now().strftime("%m%d").lstrip("0")  # 去掉前导0
        
        # 获取6位时间戳（使用毫秒级时间戳的后6位）
        timestamp = str(int(time.time() * 1000))[-6:]
        
        return f"AUTO_{current_date}_{timestamp}"
    
    def _create_single_work_center(self, wc_type: WorkCenterType):
        """
        创建单个工作中心
        
        Args:
            wc_type: 工作中心类型
        """
        # 生成工作中心编码
        wc_code = self._generate_work_center_code(wc_type)
        wc_name = f"AUTO_{wc_type.value}工作中心{wc_code[-10:]}"  # 只使用日期和时间戳部分
        
        # 输出生成的编码
        self.logger.info(f"生成工作中心编码: {wc_code}")
        self.logger.info(f"生成工作中心名称: {wc_name}")
        
        # 准备请求数据
        create_data = {
            "params": {
                "request": {
                    "invOrg": self.test_org,
                    "wcCode": wc_code,
                    "wcName": wc_name,
                    "isBackflush": False,
                    "id": None,
                    "createdBy": None,
                    "updatedBy": None,
                    "createdAt": None,
                    "updatedAt": None,
                    "version": 0,
                    "deleted": 0,
                    "originOrgId": 0,
                    "prdWorkCenterActivityItemMd": []
                }
            }
        }
        
        # 获取API配置
        api_path = self.get_api_path("工作中心抬头数据表-保存数据服务")
        params, url = self.get_api_params(api_path)
        
        # 设置请求参数
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            list(create_data["params"]["request"].keys()),
            ["params", "request"]
        )
        ParamUtil.set_request_params(filtered_params, create_data["params"]["request"])
        
        self.logger.info(f"请求URL: {url}")
        self.logger.info(f"请求参数: {filtered_params}")
        a.json(filtered_params, "请求数据")
        
        with a.step(f"发送创建请求 - 工作中心 {wc_code}"):
            result = self.http.post(url, json=filtered_params)
            a.json(result, "响应数据")
            
            # 验证创建结果
            self.assert_util.assert_response_success(result)
            self.logger.info(f"工作中心 {wc_code} 创建成功")
            a.text(f"工作中心 {wc_code} 创建成功", "验证结果")
    
    @allure.title("创建工作中心")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.run(order=1)
    def test_01_create_work_center(self):
        """测试创建工作中心"""
        try:
            with a.step("1. 创建下料工作中心"):
                self._create_single_work_center(WorkCenterType.CUTTING)
                
            with a.step("2. 创建组装工作中心"):
                self._create_single_work_center(WorkCenterType.ASSEMBLY)
                
            with a.step("3. 创建打包工作中心"):
                self._create_single_work_center(WorkCenterType.PACKING)
            
            self.logger.info("所有工作中心创建完成")
            
        except Exception as e:
            self.logger.error(f"创建工作中心失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise 