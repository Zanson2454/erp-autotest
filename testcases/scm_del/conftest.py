# """
# scm_dn 交货单模块的 fixture 配置

# 核心职责：提供可用的采购订单数据给交货单测试使用
# 若数据库中没有可用订单，调用数据工厂直接插入数据
# 确保测试用例解耦、易维护
# """
# import pytest
# from fixtures.pur_order_fixture import PurOrderFixture

# @pytest.fixture(scope="session")
# def available_std_pur_order():
#     """获取一个可用的标准采购订单；如无则创建"""
#     return PurOrderFixture.get_or_create_std_order()

# @pytest.fixture(scope="session")
# def available_csm_pur_order():
#     """获取一个可用的寄售采购订单；如无则创建"""
#     return PurOrderFixture.get_or_create_csm_order()

# @pytest.fixture(scope="function")
# def fresh_std_pur_order():
#     """每个测试函数创建一个新的标准采购订单（用于强隔离场景）"""
#     return PurOrderFixture.create_std_order()

# @pytest.fixture(scope="function")
# def fresh_csm_pur_order():
#     """每个测试函数创建一个新的寄售采购订单"""
#     return PurOrderFixture.create_csm_order()