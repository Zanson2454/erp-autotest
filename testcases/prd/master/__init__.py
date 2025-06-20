import allure
from testcases.prd.basic import PrdBasicBaseTest

@allure.epic("生产管理")
@allure.feature("主数据管理")
class PrdMasterBaseTest(PrdBasicBaseTest):
    """生产主数据测试基类"""
    
    # 存储主数据相关信息
    master_info = {
        "bom": {},           # BOM主数据
        "routing": {},       # 工艺路线主数据
        "version": {}        # 生产版本主数据
    }
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class() 