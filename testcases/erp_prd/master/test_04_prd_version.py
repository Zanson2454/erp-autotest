# -*- coding: utf-8 -*-
"""
生产版本管理测试用例
主要包含生产版本的创建、查询等功能测试
"""

import time
import uuid

import allure

from testcases.erp_prd import PrdBaseTest
from testcases.erp_prd.basic.init_config import PrdConfigInitializer
from utils.mysql_util import DBManager
from utils.report_util import a, case_decorator


@allure.epic("生产管理")
@allure.feature("主数据管理")
@allure.story("生产版本管理")
class TestPrdVersion(PrdBaseTest):
    """生产版本管理测试类"""

    # 保存测试过程中的数据
    version_data = {}

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("生产版本管理测试类初始化完成")

        # 初始化配置管理器并确保基础配置存在
        cls.config_initializer = PrdConfigInitializer()
        cls.config_initializer.ensure_configs_exist()

        # 获取测试数据
        cls.test_org = cls.base_info["inv_org_info"]
        cls.test_material = cls.base_info["prd_mat_info"]

    def setup_method(self, method):
        """测试方法初始化
        在每个测试方法执行前都确保基础配置存在
        """
        super().setup_method(method)
        # 确保基础配置数据存在
        self.config_initializer.ensure_configs_exist()

    @case_decorator(
        story="生产版本管理", title="创建生产版本", description="创建生产版本", severity="blocker", file_level_order=1
    )
    def test_create_prd_version(self):
        """测试创建生产版本"""
        try:
            with a.step("1. 准备创建数据"):
                # 获取工艺路线版本
                routing_sql = f"""
                    SELECT id
                    FROM prd_routings_header_md 
                    WHERE deleted = 0 
                    AND inv_org_id = {self.test_org["id"]}
                    AND mat_id = {self.test_material["id"]}
                    ORDER BY id DESC 
                    LIMIT 1
                """
                routing_result = DBManager.query(routing_sql)
                assert routing_result, "未找到可用的工艺路线版本"
                routing_vrs = routing_result[0]
                self.logger.info(f"获取到工艺路线版本: {routing_vrs}")

                # 获取BOM版本
                bom_sql = f"""
                    SELECT id
                    FROM gen_bom_head_md 
                    WHERE deleted = 0 
                    AND inv_org_id = {self.test_org["id"]}
                    AND mat_id = {self.test_material["id"]}
                    ORDER BY id DESC 
                    LIMIT 1
                """
                bom_result = DBManager.query(bom_sql)
                assert bom_result, "未找到可用的BOM版本"
                bom_vrs = bom_result[0]
                self.logger.info(f"获取到BOM版本: {bom_vrs}")

                # 获取API配置
                api_path = self.get_api_path("生产_生产版本保存服务")
                params, url = self.get_api_params(api_path)

                # 生成唯一编码
                unique_id = str(uuid.uuid4())[:8]
                prd_vrs_code = f"test_{unique_id}"
                prd_vrs_name = f"自动化版本_{unique_id}"

                # 保存版本信息到类变量
                TestPrdVersion.version_data.update(
                    {
                        "prd_vrs_code": prd_vrs_code,
                        "prd_vrs_name": prd_vrs_name,
                        "routing_vrs": routing_vrs,
                        "bom_vrs": bom_vrs,
                    }
                )

                # 准备请求数据
                request_data = {
                    "params": {
                        "request": {
                            "invOrgId": {"id": self.test_org["id"]},
                            "matId": {"id": self.test_material["id"]},
                            "itemList": [
                                {
                                    "lotSizeFrom": 0,
                                    "lotSizeTo": 999999999,
                                    "validTo": "9999-12-30T16:00:00.000Z",
                                    "prdVrsName": TestPrdVersion.version_data["prd_vrs_name"],
                                    "routingsVrsId": {"id": TestPrdVersion.version_data["routing_vrs"]["id"]},
                                    "bomVrsId": {"id": TestPrdVersion.version_data["bom_vrs"]["id"]},
                                    "validFrom": int(time.time() * 1000),
                                    "prdVrsCode": TestPrdVersion.version_data["prd_vrs_code"],
                                }
                            ],
                        }
                    }
                }

                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {request_data}")
                a.json(request_data, "请求数据")

            with a.step("2. 发送创建请求"):
                # 发送请求
                result, _ = self.standard_api_call(
                    api_key="生产_生产版本保存服务",
                    set_dict=(request_data.get("params", {}) if isinstance(request_data, dict) else request_data),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"],
                )
                self.logger.info("=== 响应结果详情 ===")
                self.logger.info(f"响应状态: {result.get('success')}")
                self.logger.info(f"响应消息: {result.get('message')}")
                self.logger.info(f"响应数据: {result.get('data')}")
                a.json(result, "响应数据")

            with a.step("3. 验证响应结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                self.logger.info("生产版本创建成功")

        except Exception as e:
            self.logger.error(f"创建生产版本失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdVersion()
    test.setup_class()
    test.test_create_prd_version()  # 创建生产版本
