# -*- coding: utf-8 -*-
"""
生产主数据管理测试基类
提供主数据管理相关的通用方法和数据准备接口
"""

import time
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from testcases.erp_prd import PrdBaseTest
from testcases.erp_prd.basic.init_config import PrdConfigInitializer
from utils.mysql_util import DBManager


class MaterialType(Enum):
    """物料类型"""

    FINISHED = "FINP"  # 成品
    RAW = "RAWM"  # 原材料
    SEMI = "SEMI"  # 半成品
    PACKAGE = "PCKG"  # 包装材料


class PrdMasterBaseTest(PrdBaseTest):
    """生产主数据管理测试基类"""

    # 物料类型ID映射
    MAT_TYPE_ID_MAP = {
        MaterialType.FINISHED: 2000001,  # 成品
        MaterialType.RAW: 2503002,  # 原材料
        MaterialType.PACKAGE: 2503003,  # 包装品
    }

    # 物料编码序号计数器
    _material_code_counter = 0

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定生产主数据模块上下文。"""
        cls.logger.info("生产主数据管理测试基类初始化完成")

        # 初始化配置管理器
        cls.config_initializer = PrdConfigInitializer()

        # 准备基础物料数据
        cls._prepare_base_materials()

    @classmethod
    def _generate_material_code_suffix(cls) -> str:
        """
        生成物料编码后缀：月日+6位时间戳
        例如：623_123456
        """
        # 获取当前月日
        current_date = datetime.now().strftime("%m%d").lstrip("0")  # 去掉前导0

        # 获取6位时间戳（使用毫秒级时间戳的后6位）
        timestamp = str(int(time.time() * 1000))[-6:]

        return f"{current_date}_{timestamp}"

    def teardown_method(self, method):
        """测试方法执行后的清理工作"""
        # 如果是创建生产视图的测试用例执行完成，则创建BOM
        if method.__name__ == "test_01_create_material_view":
            self.logger.info("开始创建BOM数据")
            self.bom_data = self._create_bom()
            self.logger.info("BOM数据创建完成")

    def _create_bom(self) -> Dict:
        """
        创建BOM数据
        使用已创建的成品作为父项，原材料作为子项
        """
        # 获取当前时间戳
        timestamp = int(time.time())

        # 准备BOM数据
        bom_data = {
            "params": {
                "request": {
                    "id": None,
                    "invOrgId": self.base_info["inv_org_info"],  # 使用基类中的库存组织
                    "matId": {
                        "id": self.finished_material["id"],
                        "matCode": self.finished_material["mat_code"],
                        "matName": self.finished_material["mat_name"],
                    },
                    "bomUseId": {"id": 1, "useCode": "1", "useName": "标准生产", "prdIs": True},
                    "vrsCode": f"test_{timestamp}",
                    "vrsName": f"自动化版本_{timestamp}",
                    "baseQty": 1,
                    "batchFrom": 0,
                    "batchTo": 99999999999,
                    "uomId": {"id": 14048001, "uomType": "QTY", "uomCode": "HANDLE", "uomDesc": "把"},
                    "statusId": {"id": 2000002, "statusCode": "1", "statusName": "已全部激活"},
                    "dateFrom": int(time.time() * 1000),  # 当前时间戳（毫秒）
                    "dateTo": "9999-12-30T16:00:00.000Z",
                    "bomItems": [],
                }
            }
        }

        # 添加BOM子项（原材料）
        for idx, raw_material in enumerate(self.raw_materials, 1):
            bom_item = {
                "faxQtyIs": False,
                "isCoproduct": False,
                "isByproduct": False,
                "specialized": False,
                "matId": {
                    "id": raw_material["id"],
                    "matCode": raw_material["mat_code"],
                    "matName": raw_material["mat_name"],
                    "genMatTypeCfId": {"id": self.MAT_TYPE_ID_MAP[MaterialType.RAW]},
                    "baseUomId": {"id": 14048001},
                },
                "itemTypeId": {"id": 2000001, "itemType": "L", "itemName": "库存项目", "matIs": True},
                "qty": idx * 10,  # 数量递增：10, 20, 30
                "uomId": {"id": 14048001, "uomType": "QTY", "uomCode": "HANDLE", "uomDesc": "把"},
                "invOrgId": self.base_info["inv_org_info"],
                "invLocId": self.base_info["inv_loc_info"],
                "scrapType": "SINGLE",
                "costElementId": 2007003,
            }
            bom_data["params"]["request"]["bomItems"].append(bom_item)

        # 调用API创建BOM
        result, _ = self.standard_api_call(
            api_key="GEN-物料BOM头-保存服务",
            set_dict=bom_data.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
        )
        self.assert_util.assert_response_success(result)

        # 添加创建成功的BOM ID
        if isinstance(result, dict):
            bom_data["id"] = result["data"]["data"]
        else:
            bom_data["id"] = result.json()["data"]["data"]
        self.logger.info(f"BOM创建成功，ID: {bom_data['id']}")

        return bom_data

    @classmethod
    def _prepare_base_materials(cls):
        """准备基础物料数据"""
        # 准备一个成品物料
        cls.finished_material = cls.prepare_material(
            mat_code="FG_TEST_001", mat_name="测试成品001", mat_type=MaterialType.FINISHED
        )

        # 准备三个原材料
        cls.raw_materials = [
            cls.prepare_material(mat_code="RAW_TEST_001", mat_name="测试原材料001", mat_type=MaterialType.RAW),
            cls.prepare_material(mat_code="RAW_TEST_002", mat_name="测试原材料002", mat_type=MaterialType.RAW),
            cls.prepare_material(mat_code="RAW_TEST_003", mat_name="测试原材料003", mat_type=MaterialType.RAW),
        ]

    @classmethod
    def prepare_material(
        cls,
        mat_code: str,
        mat_name: str,
        mat_type: MaterialType,
        uom_code: str = "HANDLE",
        extra_data: Optional[Dict] = None,
    ) -> Dict:
        """
        准备物料数据

        Args:
            mat_code: 物料编码基础名
            mat_name: 物料名称基础名
            mat_type: 物料类型
            uom_code: 单位编码，默认HANDLE
            extra_data: 额外的物料属性数据

        Returns:
            物料数据字典
        """
        # 生成唯一物料编码和名称
        code_suffix = cls._generate_material_code_suffix()
        unique_mat_code = f"{mat_code}_{code_suffix}"
        unique_mat_name = f"{mat_name}_{code_suffix}"

        # 准备物料数据，分类和单位先硬编码
        material_data = {
            "params": {
                "request": {
                    "imageUrl": None,
                    "matCode": unique_mat_code,
                    "matName": unique_mat_name,
                    "cateId": {"matCateName": "汽油", "id": 2001001},
                    "genMatTypeCfId": {
                        "matTypeCode": mat_type.value,
                        "matTypeName": "成品" if mat_type == MaterialType.FINISHED else "原材料",
                        "id": cls.MAT_TYPE_ID_MAP[mat_type],
                    },
                    "baseUomId": {"uomDesc": "把", "uomDigit": 3, "id": 14048001},
                }
            }
        }

        # 合并额外数据
        if extra_data:
            material_data["params"]["request"].update(extra_data)

        # 调用API创建物料
        url = "/api/trantor/service/engine/execute/GEN_MD$GEN_MAT_MD_SAVE_ACTION_SERVICE?tmodule=GEN_MD"
        result = cls.http.post(url, json=material_data)
        cls.assert_util.assert_response_success(result)

        # 查询创建的物料ID
        query_sql = """
        SELECT id, mat_code, mat_name, created_at, deleted 
        FROM gen_mat_md 
        WHERE mat_code = %(mat_code)s AND deleted = 0
        """
        db_result = DBManager.query(query_sql, {"mat_code": unique_mat_code})
        if not db_result:
            raise Exception(f"物料创建失败: {unique_mat_code}")

        material_data["id"] = db_result[0]["id"]
        material_data["mat_code"] = unique_mat_code
        material_data["mat_name"] = unique_mat_name
        material_data["mat_type"] = mat_type.value
        material_data["uom_code"] = uom_code
        material_data["status"] = "ENABLED"
        material_data["is_manufactured"] = mat_type == MaterialType.FINISHED
        material_data["is_purchased"] = mat_type == MaterialType.RAW

        # 只为原材料设置价格
        if mat_type == MaterialType.RAW:
            try:
                # 准备价格数据
                price_data = {
                    "sceneKey": "ERP_FIN$IV_PRICE_MD_VIEW",
                    "viewKey": "ERP_FIN$IV_PRICE_MD_VIEW:edit",
                    "viewTitle": "edit",
                    "buttonKey": "ERP_FIN$IV_PRICE_MD_VIEW-editView-footer-save",
                    "buttonName": "保存",
                    "appId": 0,
                    "teamId": 22,
                    "serviceKey": "ERP_FIN$IV_PRICE_SUBMIT_EVENT_SERVICE",
                    "params": {
                        "request": {
                            "comOrgId": cls.base_info["com_org_info"],
                            "invOrgId": cls.base_info["inv_org_info"],
                            "matId": {
                                "id": material_data["id"],
                                "matCode": unique_mat_code,
                                "matName": unique_mat_name,
                                "genMatTypeCfId": material_data["params"]["request"]["genMatTypeCfId"],
                                "baseUomId": material_data["params"]["request"]["baseUomId"],
                                "cateId": material_data["params"]["request"]["cateId"],
                                "status": "INACTIVE",
                            },
                            "batchCode": None,
                            "currId": None,
                            "costPrice": 100.00,  # 设置成本价格
                            "enableStatus": "ENABLE",
                            "id": None,
                            "createdBy": None,
                            "updatedBy": None,
                            "createdAt": None,
                            "updatedAt": None,
                            "version": 0,
                            "deleted": 0,
                            "originOrgId": 0,
                        }
                    },
                }

                # 调用API设置价格
                price_url = "/api/trantor/service/engine/execute/ERP_FIN$IV_PRICE_SUBMIT_EVENT_SERVICE?tmodule=ERP_FIN"
                price_result = cls.http.post(price_url, json=price_data)
                if not price_result.get("success"):
                    cls.logger.warning(f"设置物料 {unique_mat_code} 价格失败: {price_result.get('message')}")
                else:
                    cls.logger.info(f"成功设置物料 {unique_mat_code} 的价格")

            except Exception as e:
                cls.logger.error(f"设置物料 {unique_mat_code} 价格失败: {str(e)}")
                # 不抛出异常，继续执行
                pass

        return material_data

    @classmethod
    def get_test_material(cls, mat_type: Optional[MaterialType] = None) -> Dict:
        """
        获取测试物料数据

        Args:
            mat_type: 物料类型，如果指定则返回对应类型的物料

        Returns:
            物料数据字典
        """
        if mat_type == MaterialType.FINISHED or mat_type is None:
            return cls.finished_material
        elif mat_type == MaterialType.RAW:
            return cls.raw_materials[0]
        else:
            raise ValueError(f"未找到类型为 {mat_type.value} 的测试物料")

    def get_test_bom(self):
        """
        获取测试BOM数据
        """
        return self.bom_data

    def get_test_routing(self):
        """
        获取测试工艺路线数据
        后续可以改为从数据工厂获取
        """
        return self.test_data["routing_info"]

    def get_test_version(self):
        """
        获取测试生产版本数据
        后续可以改为从数据工厂获取
        """
        return self.test_data["version_info"]

    def get_test_work_center(self) -> Dict:
        """
        获取不同类型的工作中心信息
        按照工作中心类型（下料、组件、打包）获取最新创建的工作中心

        Returns:
            dict: 包含三种类型工作中心ID的字典
                {
                    "cutting": {"id": xxx},
                    "assembly": {"id": xxx},
                    "packing": {"id": xxx}
                }
        """
        try:
            # 查询三种类型的工作中心
            sql = """
                SELECT id, wc_code, wc_name
                FROM prd_work_centor_header_md
                WHERE deleted = 0
                AND inv_org = %(inv_org)s
                AND wc_name LIKE %(wc_name_pattern)s
                ORDER BY id DESC
                LIMIT 1
            """

            # 查询下料工作中心
            cutting_wc = self.db.query_one(sql, {"inv_org": self.test_org, "wc_name_pattern": "%下料工作中心%"})
            if not cutting_wc:
                raise Exception("未找到下料工作中心")

            # 查询组件工作中心
            assembly_wc = self.db.query_one(sql, {"inv_org": self.test_org, "wc_name_pattern": "%组件工作中心%"})
            if not assembly_wc:
                raise Exception("未找到组件工作中心")

            # 查询打包工作中心
            packing_wc = self.db.query_one(sql, {"inv_org": self.test_org, "wc_name_pattern": "%打包工作中心%"})
            if not packing_wc:
                raise Exception("未找到打包工作中心")

            # 返回工作中心信息
            return {
                "cutting": {"id": cutting_wc["id"]},
                "assembly": {"id": assembly_wc["id"]},
                "packing": {"id": packing_wc["id"]},
            }

        except Exception as e:
            self.logger.error(f"获取工作中心信息失败: {str(e)}")
            raise
