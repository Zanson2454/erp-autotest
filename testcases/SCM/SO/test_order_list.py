import pytest
from typing import Dict, Any
from loguru import logger
from api.common.login_manager import LoginManager
from api.common.base_api import BaseAPI
from config.config import Config

class TestOrderList:
    """销售订单列表测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置处理"""
        logger.debug("开始测试销售订单列表查询")
        self.login_manager = LoginManager()
        account, password = Config.get_auth_info()
        self.login_manager.login(account=account, password=password)
        self.session = self.login_manager.get_session()
        logger.debug("登录成功，获取到session")
        
    def test_query_orders(self):
        """测试查询销售订单列表"""
        # 准备请求数据
        base_url = "https://t-erp-portal-test.app.terminus.io"
        url = f"{base_url}/api/trantor/service/engine/execute/ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE"
        params = {"tmodule": "ERP_SCM"}
        data = {
            "sceneKey": "ERP_SCM$sls_so_730",
            "viewKey": "ERP_SCM$sls_so_730:list",
            "viewCondition": {
                "conditionKey": "gYLG-UJ0RZbOCvMez5f7D",
                "rightValues": {
                    "jYJ-mOKGX5JJkeGr274TK": [
                        {"constValue": "SALES", "fieldType": "Enum", "type": "ConstValue", "valueType": "CONST"},
                        {"constValue": "ASS", "fieldType": "Enum", "type": "ConstValue", "valueType": "CONST"}
                    ]
                }
            },
            "appId": 0,
            "teamId": 22,
            "serviceKey": "ERP_SCM$sls_so_head_tr_PAGING_DATA_SERVICE",
            "params": {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "systemParams": {
                            "viewCondition": {
                                "conditionKey": "gYLG-UJ0RZbOCvMez5f7D",
                                "rightValues": {
                                    "jYJ-mOKGX5JJkeGr274TK": [
                                        {"constValue": "SALES", "fieldType": "Enum", "type": "ConstValue", "valueType": "CONST"},
                                        {"constValue": "ASS", "fieldType": "Enum", "type": "ConstValue", "valueType": "CONST"}
                                    ]
                                }
                            }
                        },
                        "conditionGroup": None,
                        "sortOrders": [{"fieldAlias": "createdBy", "sortType": "DESC"}]
                    }
                }
            }
        }
        
        logger.debug(f"准备发送请求: URL={url}")
        logger.debug(f"请求参数: {params}")
        logger.debug(f"请求数据: {data}")
        
        # 执行测试
        response = self.session.post(url, params=params, json=data).json()
        logger.debug(f"收到响应: {response}")
        
        # 断言响应状态
        assert response["success"] is True, f"查询订单失败: {response}"
        logger.debug("响应状态检查通过")
        

        # 如果有数据，验证返回的订单数据结构
        if response["data"]['data']['data']:
            order = response["data"]["data"]["data"][0]
            assert "soCode" in order, "订单数据缺少soCode字段"
            logger.debug("订单数据结构检查通过")
        
        logger.debug("测试完成")

if __name__ == "__main__":
    pytest.main(["-v", __file__])