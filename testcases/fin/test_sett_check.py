import pytest
import os
import sys

# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
from testcases.comm.base_test import BaseTest

class TestSettlementItem(BaseTest):
    """结算项测试用例"""
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()  # 调用父类的setup_class方法
    
    def test_search_detail(self):
        """测试查询结算项详情"""
        request_data = {
            "sceneKey": "ERP_FIN$SETT_ITEM_FROM_DS",
            "viewKey": "ERP_FIN$SETT_ITEM_FROM_DS:detail",
            "containerKey": "ERP_FIN$SETT_ITEM_FROM_DS-TERP_MIGRATE$SETT_ITEM-detailView-detail",
            "serviceKey": "ERP_FIN$SETT_ITEM_TR_FIND_DATA_BY_ID_SERVICE",
            "params": {
                "request": {
                    "id": "14499018"
                }
            }
        }
        
        response_data = self._make_request(
            self.base_url + "/api/trantor/service/engine/execute/ERP_FIN$SETT_ITEM_TR_FIND_DATA_BY_ID_SERVICE?tmodule=ERP_FIN",
            request_data
        )
        # 验证响应数据
        self.assert_util.assert_response_success(response_data)
        #self.assert_util.assert_http_status(response_data.json())
        self.log.info(f"查询结算项详情成功，响应数据: {response_data}")

if __name__ == "__main__":
    test = TestSettlementItem()
    test.setup_class()
    test.test_search_detail()