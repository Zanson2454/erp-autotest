"""
生产模块的测试初始化
提供配置加载等通用功能
"""

from pathlib import Path

from testcases.comm.base_test import BaseTest
from testcases.comm.utility_mixins import AsyncWaitMixin
from utils.mysql_util import DBManager

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent.parent


class PrdBaseTest(AsyncWaitMixin, BaseTest):
    """生产模块的基础测试类，负责加载通用配置和提供API访问方法"""

    # 保存基础配置信息的类变量
    base_info = {}

    @classmethod
    def setup_class(cls):
        """
        测试类初始化 - 加载通用配置
        完成以下工作:
        1. 调用父类初始化方法 (包括登录、数据库连接等)
        2. 初始化通用配置文件路径
        3. 加载API路径和参数配置
        """
        # 调用父类初始化方法
        super().setup_class()
        cls.load_api_configs()
        cls.bind_context()

    @classmethod
    def load_api_configs(cls):
        """加载生产模块 API 配置。"""
        # 初始化配置文件路径
        cls.base_api_path = Path(project_root) / "config" / "api" / "scm_prd" / "prd_api_path.yaml"
        cls.base_api_params = Path(project_root) / "config" / "api" / "scm_prd" / "prd_api_params.yaml"

        cls.load_module_api_configs(cls.base_api_path, cls.base_api_params)

    @classmethod
    def bind_context(cls):
        """绑定生产模块上下文并初始化基础配置数据。"""
        # 初始化基础配置数据
        cls._init_base_info()

        cls.logger.info("PrdBaseTest初始化完成")

    @classmethod
    def _init_base_info(cls):
        """初始化基础配置数据"""
        try:
            # 查询工单类型配置
            wo_type_sql = """
                SELECT id, type_code, type_name 
                FROM prd_wo_type_cf 
                WHERE deleted = 0 AND type_name = '量产生产订单'
                LIMIT 1
            """
            wo_type_info = DBManager.query(wo_type_sql)[0]

            # 查询库存组织配置
            inv_org_sql = """
                SELECT id, org_code, org_name 
                FROM org_struct_md 
                WHERE org_status='ENABLED' 
                AND org_dimension_code='SCM_ORG_GRP' 
                AND org_code LIKE 'AUTOTEST%' 
                AND org_business_type_codes = '["INV_ORG"]' 
                AND deleted=0 
                LIMIT 1
            """
            inv_org_info = DBManager.query(inv_org_sql)[0]

            # 查询生产物料配置
            prd_mat_sql = """
                SELECT id, mat_code, mat_name
                FROM gen_mat_md
                WHERE deleted = 0 AND mat_code LIKE 'FG_TEST_001%'
                ORDER BY id DESC
                LIMIT 1
            """
            prd_mat_info = DBManager.query(prd_mat_sql)[0]

            # 保存配置信息
            cls.base_info = {"wo_type_info": wo_type_info, "inv_org_info": inv_org_info, "prd_mat_info": prd_mat_info}

            cls.logger.info(f"基础配置数据初始化成功: {cls.base_info}")

        except Exception as e:
            cls.logger.error(f"基础配置数据初始化失败: {str(e)}")
            raise

    def get_cross_module_api_path(self, module_name: str, api_key: str) -> str:
        """
        获取跨模块的API路径

        Args:
            module_name: 模块名称，如 'scm', 'gen', 'fin' 等
            api_key: API的名称键值

        Returns:
            str: 对应的API路径
        """
        # SCM 模块细分为多个子模块，根据 API key 前缀路由到正确的子模块
        if module_name == "scm":
            if api_key.startswith("DEL-"):
                module_name = "scm_del"
            elif api_key.startswith("PUR-") or api_key.startswith("PR-"):
                module_name = "scm_pur"
            elif api_key.startswith("INV-") or api_key.startswith("MVM-"):
                module_name = "scm_inv"
            elif api_key.startswith("SLS-") or api_key.startswith("SO-"):
                module_name = "scm_sls"
            else:
                module_name = "scm_del"  # 默认使用 scm_del

        # 构建模块API路径配置文件路径
        api_path_file = Path(project_root) / "config" / "api" / module_name / f"{module_name}_api_path.yaml"

        # 读取API路径配置
        api_config = self.yaml_util.read_yaml(api_path_file)
        apis = api_config.get("apis", {})

        # 获取API路径
        api_path = apis.get(api_key, {}).get("path")
        if not api_path:
            raise ValueError(f"在{module_name}模块中未找到API: {api_key}")

        return api_path

    def get_cross_module_api_params(self, module_name: str, api_path: str, with_query_params: str = None) -> tuple:
        """
        获取跨模块的API请求参数和完整URL

        Args:
            module_name: 模块名称，如 'scm', 'gen', 'fin' 等
            api_path: API路径
            with_query_params: 查询参数字符串（可选）

        Returns:
            tuple: (params, url)
        """
        # SCM 模块细分为多个子模块，根据 api_path 中的模块标识路由
        if module_name == "scm":
            if "/del/" in api_path.lower() or api_path.startswith("DEL-"):
                module_name = "scm_del"
            elif "/pur/" in api_path.lower():
                module_name = "scm_pur"
            elif "/inv/" in api_path.lower():
                module_name = "scm_inv"
            elif "/sls/" in api_path.lower():
                module_name = "scm_sls"
            else:
                module_name = "scm_del"  # 默认使用 scm_del

        # 构建模块API参数配置文件路径
        api_params_file = Path(project_root) / "config" / "api" / module_name / f"{module_name}_api_params.yaml"

        # 读取API参数配置
        api_config = self.yaml_util.read_yaml(api_params_file)
        api_params = api_config.get("api_params", {})

        # 获取API参数
        params = api_params.get(api_path, {})

        # 构建完整URL
        url = api_path
        if with_query_params:
            url = f"{api_path}?{with_query_params}"

        return params, url

    def get_latest_prd_order(self, status="DRAFT"):
        """
        获取最新的生产订单信息

        参数：
            status (str): 生产订单状态，默认为'DRAFT'
        返回:
            dict: 包含生产订单ID和编号的字典
        """
        try:
            # 查询最新的指定状态生产订单
            sql = f"""
                SELECT id, wo_code, status, confirm_status, delivered_status
                FROM prd_order_header_tr
                WHERE deleted = 0
                AND status = '{status}'
                AND confirm_status = 'UNCONFIRMED'
                AND delivered_status = 'UNDELIVERED'
                ORDER BY id DESC
                LIMIT 1
            """
            result = self.query_service.query(sql)
            assert result, f"未找到状态为{status}的生产订单"

            # 返回生产订单信息
            order_info = {
                "id": result[0]["id"],
                "wo_code": result[0]["wo_code"],
                "status": result[0]["status"],
                "confirm_status": result[0]["confirm_status"],
                "delivered_status": result[0]["delivered_status"],
            }

            self.logger.info(f"获取到生产订单信息: {order_info}")
            return order_info

        except Exception as e:
            self.logger.error(f"获取生产订单信息失败: {str(e)}")
            raise

    def get_prd_order_pending_issue_bom_items(self):
        """
        获取已下达生产订单的待领料BOM行信息
        Returns:
            list: 包含待领料BOM行ID的列表
                [{'id': xxx}, {'id': xxx}]
        """
        # 获取最新的已下达生产订单ID
        latest_order = self.get_latest_prd_order(status="SUBMITTED")
        order_id = latest_order.get("id")

        sql = f"""
            SELECT id
            FROM prd_order_bom_item_tr
            WHERE deleted = 0 
            AND is_backflush = 0
            AND consumed_qty = 0
            AND prd_order_header_tr_id = {order_id}  #需确保前面用例执行成功否则可能取到没有领料的BOM行
            ORDER BY id DESC
        """
        result = self.query_service.query(sql)
        self.logger.info(f"获取到已下达生产订单待领料BOM行信息: {result}")
        return result
