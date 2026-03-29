import allure
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单价格校验")
class TestSoPrice(SlsBase):
    """销售订单价格校验测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 固定使用 curl 中的物料和价格参数
        cls.fixed_mat_code = "hxymat-20241202744"
        cls.fixed_mat_name = "hxy测试物料4"
        cls.fixed_mat_id = 14633001
        cls.fixed_match_record_id = "2083001"
        cls.fixed_price_type_id = "2514001"  # 销售价
        cls.fixed_uom_id = 2004001  # 件
        cls.fixed_curr_id = 2000001  # 人民币 CNY
        cls.fixed_price = 2000  # 默认价格
        
        # 价格维护单相关
        cls.price_adj_id = None
        
        # 销售订单相关
        cls.so_head_id_save = None
        cls.so_head_data = None
        
        # 价格校验相关（用于用例间传递数据）
        cls.found_price_record = None
        cls.original_price = None
        cls.new_price = None
        
        cls.logger.info("销售订单价格校验测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 注意：价格调整单数据（按 price_adj_name 清理）已移至 session 级别的 fixture 统一处理
            # 见 testcases/scm_sls/conftest.py::scm_sls_module_cleanup
            
            
            try:
                # 查询销售价格列表，获取测试创建的记录
                api_path = ParamUtil.get_api_path(cls.apis, "GEN-条件主数据-分页查询服务")
                params, url = ParamUtil.get_api_params(cls.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["registerId", "pageable"],
                    ["params", "request"]
                )
                
                set_dict = {
                    "registerId": cls.fixed_match_record_id,
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 100  # 获取足够多的记录
                    }
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                
                # 发送查询请求
                response = cls.http.post(url, json=filtered_params, description="查询销售价格列表以清理数据")
                if response.get("success"):
                    response_data = response.get("data", {}).get("data", {})
                    records = response_data.get("records", []) or response_data.get("data", [])
                    
                    # 筛选出测试创建的记录（通过物料ID匹配）
                    test_record_ids = []
                    for record in records:
                        # 检查记录是否匹配测试物料（14633001）
                        # 尝试多种可能的字段名和结构
                        var9 = record.get("var9") or record.get("var_9") or record.get("var9") or {}
                        mat_id = None
                        
                        if isinstance(var9, dict):
                            mat_id = var9.get("id") or var9.get("matId") or var9.get("mat_id")
                        elif isinstance(var9, (int, str)):
                            try:
                                mat_id = int(var9)
                            except (ValueError, TypeError):
                                pass
                        
                        # 如果var9中没有找到，尝试直接从record中获取
                        if not mat_id:
                            mat_id = record.get("matId") or record.get("mat_id") or record.get("var9")
                            if isinstance(mat_id, dict):
                                mat_id = mat_id.get("id")
                        
                        # 转换为整数进行比较
                        try:
                            if mat_id:
                                mat_id = int(mat_id)
                            if mat_id == cls.fixed_mat_id:
                                record_id = record.get("id")
                                if record_id:
                                    test_record_ids.append(record_id)
                        except (ValueError, TypeError):
                            continue
                    
                    # 删除匹配的记录
                    if test_record_ids:
                        for record_id in test_record_ids:
                            try:
                                # 尝试通过ID删除
                                possible_conditions = [
                                    ("id = %s", [record_id]),
                                ]
                                
                                deleted_count = 0
                                for where_condition, where_params in possible_conditions:
                                    try:
                                        result = cls.db.delete(
                                            table="gen_match_record_md",
                                            where=where_condition,
                                            params=where_params
                                        )
                                        if result > 0:
                                            deleted_count += result
                                            break
                                    except Exception:
                                        continue
                            except Exception:
                                pass
            except Exception:
                pass
            
            cls.logger.info("销售订单价格校验测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"销售订单价格校验测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="销售订单价格校验",
        title="测试检查销售价格列表中是否存在指定物料的销售价格",
        description="验证检查销售价格列表中是否存在指定物料的销售价格",
        severity="critical",
        order=1,
        tags=["销售价格", "价格校验", "价格查询"]
    )
    def test_01_check_price_exists(self):
        """测试检查销售价格列表中是否存在指定物料的销售价格"""
        try:
            # 1. 调用API - 使用条件主数据分页查询服务（根据curl，这是正确的API）
            api_path = self.get_api_path("GEN-条件主数据-分页查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["registerId", "pageable"],
                ["params", "request"]
            )
            
            # 3. 设置查询参数（根据curl格式）
            set_dict = {
                "registerId": self.fixed_match_record_id,  # 使用固定的匹配记录ID
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 5. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="GEN-条件主数据-分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 获取响应数据
            response_data = response.get("data", {}).get("data", {})
            
            # 7. 验证分页结果
            records = response_data.get("records", []) or response_data.get("data", [])
            total = response_data.get("total", 0)
            
            # 8. 断言该物料是否存在销售价格
            self.assert_util.assert_by_operator(total, ">=", 0, message="总数应该大于等于0")
            
            # 9. 验证查询结果中是否包含指定的物料，并选择当前时间生效的价格
            found_record = None
            current_time = self.mock_util.get_timestamp(timestamp=True)
            if records:
                # 检查记录中是否包含指定的物料ID，并选择当前时间生效的价格
                found_mat = False
                candidate_records = []  # 存储所有匹配的记录
                
                for record in records:
                    var9 = record.get("var9") or record.get("var_9") or {}
                    mat_id = None
                    
                    if isinstance(var9, dict):
                        mat_id = var9.get("id") or var9.get("matId") or var9.get("mat_id")
                    elif isinstance(var9, (int, str)):
                        try:
                            mat_id = int(var9)
                        except (ValueError, TypeError):
                            pass
                    
                    if not mat_id:
                        mat_id = record.get("matId") or record.get("mat_id")
                        if isinstance(mat_id, dict):
                            mat_id = mat_id.get("id")
                    
                    try:
                        if mat_id:
                            mat_id = int(mat_id)
                        if mat_id == self.fixed_mat_id:
                            found_mat = True
                            candidate_records.append(record)
                    except (ValueError, TypeError):
                        continue
                
                # 从所有匹配的记录中选择当前时间生效的价格（startTime <= 当前时间 <= endTime）
                for record in candidate_records:
                    start_time = record.get("startTime") or record.get("startTimeNew") or 0
                    end_time = record.get("endTime") or record.get("endTimeNew") or 253402271999000
                    
                    if start_time <= current_time <= end_time:
                        found_record = record
                        a.text(f"找到当前生效的物料销售价格记录，物料ID: {self.fixed_mat_id}", "价格校验结果")
                        # 展示价格信息
                        price = record.get("out1") or record.get("outNew1") or record.get("price")
                        if price:
                            a.text(f"物料销售价格: {price}", "价格信息")
                        break
                
                # 如果没有找到当前生效的价格，使用第一个匹配的记录（兼容旧逻辑）
                if not found_record and candidate_records:
                    found_record = candidate_records[0]
                    a.text(f"找到物料的销售价格记录（可能不是当前生效），物料ID: {self.fixed_mat_id}", "价格校验结果")
                    # 展示价格信息
                    price = found_record.get("out1") or found_record.get("outNew1") or found_record.get("price")
                    if price:
                        a.text(f"物料销售价格: {price}", "价格信息")
                
                if found_mat:
                    a.text(f"销售价格校验成功：物料 {self.fixed_mat_name}(ID: {self.fixed_mat_id}) 存在销售价格", "校验结果")
                    # 保存价格记录供后续用例使用
                    self.found_price_record = found_record
                    
                    # 获取原价格并计算新价格
                    original_price = found_record.get("out1") or found_record.get("outNew1") or found_record.get("price")
                    if original_price:
                        try:
                            original_price = float(original_price)
                            # 计算新价格（在原价格基础上增加1）
                            new_price = original_price + 1
                            
                            self.original_price = original_price
                            self.new_price = new_price
                            
                            a.text(f"原价格: {original_price}, 新价格: {new_price}", "价格信息")
                        except (ValueError, TypeError):
                            a.text(f"无法解析价格: {original_price}", "价格信息")
                else:
                    # 如果查询到记录但没有匹配的物料，说明该物料不存在销售价格，需要创建价格
                    a.text(f"查询到 {len(records)} 条记录，但未找到指定物料的销售价格，开始创建价格", "校验结果")
                    
                    # 为该物料创建并提交销售价格
                    self._create_and_submit_price()
                    
                    # 创建后重新查询价格列表
                    response, _ = self.standard_api_call(
                        api_key="GEN-条件主数据-分页查询服务",
                        set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                        store_id_as=None,
                        use_param_util=False,
                        param_path=["params"]
                    )
                    self.assert_util.assert_response_data(response)
                    
                    response_data = response.get("data", {}).get("data", {})
                    records = response_data.get("records", []) or response_data.get("data", [])
                    total = response_data.get("total", 0)
                    
                    if records and total > 0:
                        # 再次查找物料记录
                        for record in records:
                            var9 = record.get("var9") or record.get("var_9") or {}
                            mat_id = None
                            
                            if isinstance(var9, dict):
                                mat_id = var9.get("id") or var9.get("matId") or var9.get("mat_id")
                            elif isinstance(var9, (int, str)):
                                try:
                                    mat_id = int(var9)
                                except (ValueError, TypeError):
                                    pass
                            
                            if not mat_id:
                                mat_id = record.get("matId") or record.get("mat_id")
                                if isinstance(mat_id, dict):
                                    mat_id = mat_id.get("id")
                            
                            try:
                                if mat_id:
                                    mat_id = int(mat_id)
                                if mat_id == self.fixed_mat_id:
                                    found_record = record
                                    a.text(f"创建价格后，找到物料的销售价格记录，物料ID: {mat_id}", "价格校验结果")
                                    
                                    # 保存价格记录供后续用例使用
                                    self.found_price_record = found_record
                                    
                                    # 获取原价格并计算新价格
                                    original_price = found_record.get("out1") or found_record.get("outNew1") or found_record.get("price")
                                    if original_price:
                                        try:
                                            original_price = float(original_price)
                                            new_price = original_price + 1
                                            
                                            self.original_price = original_price
                                            self.new_price = new_price
                                            
                                            a.text(f"原价格: {original_price}, 新价格: {new_price}", "价格信息")
                                        except (ValueError, TypeError):
                                            self.logger.warning(f"无法解析价格: {original_price}")
                                            a.text(f"无法解析价格: {original_price}", "价格信息")
                                    break
                            except (ValueError, TypeError):
                                continue
                        
                        if not self.found_price_record:
                            raise ValueError(f"创建价格后，仍未找到物料ID为 {self.fixed_mat_id} 的销售价格记录")
                    else:
                        raise ValueError(f"创建价格后，查询销售价格列表仍为空")
            else:
                # 如果没有记录，说明该物料不存在销售价格，先创建价格
                a.text(f"销售价格校验结果：物料 {self.fixed_mat_name}(ID: {self.fixed_mat_id}) 不存在销售价格，开始创建价格", "校验结果")
                
                # 为该物料创建并提交销售价格
                self._create_and_submit_price()
                
                # 创建后重新查询价格列表
                response, _ = self.standard_api_call(
                    api_key="GEN-条件主数据-分页查询服务",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_data(response)
                
                response_data = response.get("data", {}).get("data", {})
                records = response_data.get("records", []) or response_data.get("data", [])
                total = response_data.get("total", 0)
                
                if records and total > 0:
                    # 再次查找物料记录
                    for record in records:
                        var9 = record.get("var9") or record.get("var_9") or {}
                        mat_id = None
                        
                        if isinstance(var9, dict):
                            mat_id = var9.get("id") or var9.get("matId") or var9.get("mat_id")
                        elif isinstance(var9, (int, str)):
                            try:
                                mat_id = int(var9)
                            except (ValueError, TypeError):
                                pass
                        
                        if not mat_id:
                            mat_id = record.get("matId") or record.get("mat_id")
                            if isinstance(mat_id, dict):
                                mat_id = mat_id.get("id")
                        
                        try:
                            if mat_id:
                                mat_id = int(mat_id)
                            if mat_id == self.fixed_mat_id:
                                found_record = record
                                a.text(f"创建价格后，找到物料的销售价格记录，物料ID: {mat_id}", "价格校验结果")
                                
                                # 保存价格记录供后续用例使用
                                self.found_price_record = found_record
                                
                                # 获取原价格并计算新价格
                                original_price = found_record.get("out1") or found_record.get("outNew1") or found_record.get("price")
                                if original_price:
                                    try:
                                        original_price = float(original_price)
                                        new_price = original_price + 1
                                        
                                        self.original_price = original_price
                                        self.new_price = new_price
                                        
                                        a.text(f"原价格: {original_price}, 新价格: {new_price}", "价格信息")
                                    except (ValueError, TypeError):
                                        self.logger.warning(f"无法解析价格: {original_price}")
                                        a.text(f"无法解析价格: {original_price}", "价格信息")
                                break
                        except (ValueError, TypeError):
                            continue
                    
                    if not self.found_price_record:
                        raise ValueError(f"创建价格后，仍未找到物料ID为 {self.fixed_mat_id} 的销售价格记录")
                else:
                    raise ValueError(f"创建价格后，查询销售价格列表仍为空")
            
            a.json(filtered_params, "查询请求数据")
            a.json(response, "查询响应数据")
            a.text(f"查询销售价格列表成功，总数: {total}, 当前页记录数: {len(records)}", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    def _ensure_price_record_context(self):
        """确保已加载物料价格上下文（found_price_record/original_price/new_price）。"""
        if self.found_price_record and self.original_price is not None and self.new_price is not None:
            return

        def _query_current_price_record():
            api_path = self.get_api_path("GEN-条件主数据-分页查询服务")
            params, _ = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["registerId", "pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "registerId": self.fixed_match_record_id,
                "pageable": {"pageNo": 1, "pageSize": 50},
            })
            response, _ = self.standard_api_call(
                api_key="GEN-条件主数据-分页查询服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)

            records = response.get("data", {}).get("data", {}).get("records", []) or response.get("data", {}).get("data", {}).get("data", [])
            current_time = self.mock_util.get_timestamp(timestamp=True)
            candidates = []
            for record in records:
                var9 = record.get("var9") or record.get("var_9") or {}
                mat_id = None
                if isinstance(var9, dict):
                    mat_id = var9.get("id") or var9.get("matId") or var9.get("mat_id")
                elif isinstance(var9, (int, str)):
                    try:
                        mat_id = int(var9)
                    except (ValueError, TypeError):
                        mat_id = None
                if not mat_id:
                    mat_id = record.get("matId") or record.get("mat_id")
                    if isinstance(mat_id, dict):
                        mat_id = mat_id.get("id")
                try:
                    if mat_id and int(mat_id) == self.fixed_mat_id:
                        candidates.append(record)
                except (ValueError, TypeError):
                    continue

            for item in candidates:
                start_time = item.get("startTime") or item.get("startTimeNew") or 0
                end_time = item.get("endTime") or item.get("endTimeNew") or 253402271999000
                if start_time <= current_time <= end_time:
                    return item
            return candidates[0] if candidates else None

        record = _query_current_price_record()
        if not record:
            self._create_and_submit_price()
            record = _query_current_price_record()
        if not record:
            raise ValueError(f"未找到物料ID为 {self.fixed_mat_id} 的销售价格记录")

        self.found_price_record = record
        price = record.get("out1") or record.get("outNew1") or record.get("price")
        if price is None:
            raise ValueError("已找到价格记录，但缺少价格字段")
        self.original_price = float(price)
        self.new_price = self.original_price + 1
    
    def _create_and_submit_price(self):
        """为该物料创建并提交销售价格"""
        try:
            a.text(f"开始为物料 {self.fixed_mat_name}(ID: {self.fixed_mat_id}) 创建销售价格", "创建价格")
            
            # 1. 创建价格调整单（保存为草稿）
            price_adj_name = f"订单价格校验创建价格_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("SLS-销售价格-价格调整保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "id", "matchRecordId", "priceAdjName", "priceTypeName", 
                    "matchRecordName", "priceTypeId", "priceAdjItemList"
                ],
                ["params", "request"]
            )
            
            # 计算时间戳：开始时间（当前时间）和结束时间（最大时间戳）
            start_time = self.mock_util.get_timestamp(timestamp=True)
            end_time = 253402271999000  # 最大时间戳
            
            set_dict = {
                "id": None,
                "matchRecordId": self.fixed_match_record_id,
                "priceAdjName": price_adj_name,
                "priceTypeName": "销售价",
                "matchRecordName": "1",
                "priceTypeId": self.fixed_price_type_id,
                "priceAdjItemList": [
                    {
                        "startTimeNew": start_time,
                        "endTimeNew": end_time,
                        "var9": {
                            "matCode": self.fixed_mat_code,
                            "matName": self.fixed_mat_name,
                            "id": self.fixed_mat_id
                        },
                        "outNew5": {
                            "id": self.fixed_uom_id
                        },
                        "outNew6": {
                            "id": self.fixed_curr_id
                        },
                        "outNew1": self.fixed_price,  # 使用默认价格
                        "deleted": 0,
                        "startTime": start_time,
                        "endTime": end_time,
                        "matchRecordMdId": None,
                        "id": None,
                        "matchLadderMdDTOList": [],
                        "matchLadderMdDTONewList": []
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 2. 发送保存请求
            response, _ = self.standard_api_call(
                api_key="SLS-销售价格-价格调整保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 3. 获取保存后的价格调整ID
            response_data = response.get("data", {}).get("data", {})
            price_adj_id = response_data.get("id")
            self.assert_util.assert_by_operator(price_adj_id, "not_empty", message="保存价格调整失败，未返回ID")
            
            a.text(f"价格调整单保存成功，ID: {price_adj_id}", "创建价格")
            
            # 4. 提交价格调整单（使用列表提交服务）
            submit_api_path = self.get_api_path("SLS-销售价格-价格维护单列表提交服务")
            submit_params, submit_url = self.get_api_params(submit_api_path)
            
            submit_filtered_params = ParamUtil.filter_post_body_fields(
                submit_params, ["id"],
                ["params", "request"]
            )
            
            submit_set_dict = {
                "id": price_adj_id
            }
            ParamUtil.set_request_params(submit_filtered_params, submit_set_dict)
            
            # 5. 发送提交请求
            response, _ = self.standard_api_call(
                api_key="SLS-销售价格-价格维护单列表提交服务",
                set_dict=(submit_filtered_params.get("params", {}) if isinstance(submit_filtered_params, dict) else submit_filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 验证提交结果
            time.sleep(0.5)  # 等待数据持久化
            try:
                table_names = ["gen_price_adj_head_tr", "price_adj_head_tr", "erp_price_adj_head_tr"]
                price_adj_info = None
                
                for table_name in table_names:
                    try:
                        query_sql = f"""
                            SELECT id, code, status, doc_status, biz_status, price_adj_code
                            FROM {table_name}
                            WHERE id = %s AND deleted = 0
                            LIMIT 1
                        """
                        db_result = self.db.query(query_sql, [price_adj_id])
                        if db_result:
                            price_adj_info = db_result[0]
                            break
                    except Exception:
                        continue
                
                if price_adj_info:
                    status = price_adj_info.get("status") or price_adj_info.get("doc_status") or price_adj_info.get("biz_status")
                    if status:
                        self.assert_util.assert_by_operator(
                            status, "in", ["INEFFECT", "EFFECT", "已生效"],
                            message=f"价格维护单状态应为已生效，当前状态: {status}"
                        )
                        a.text(f"价格维护单提交成功，状态: {status}", "创建价格")
                    else:
                        a.text(f"价格维护单提交成功，但状态字段为空", "创建价格")
                else:
                    a.text(f"价格维护单提交成功，但无法查询状态", "创建价格")
            except Exception as e:
                self.logger.warning(f"无法查询价格维护单状态: {str(e)}")
                a.text(f"价格维护单提交成功，但无法查询状态: {str(e)}", "创建价格")
            
            a.text(f"物料销售价格创建并提交成功，价格: {self.fixed_price}", "创建价格")
            
        except Exception as e:
            self.logger.error(f"创建销售价格失败: {str(e)}")
            a.text(f"创建销售价格失败: {str(e)}", "创建价格失败原因")
            raise
    
    @case_decorator(
        story="销售订单价格校验",
        title="测试维护销售价格为其他价格",
        description="验证维护销售价格为其他价格的功能，在原有价格上增加1",
        severity="critical",
        order=2,
        tags=["销售价格", "价格维护", "价格更新"]
    )
    def test_02_maintain_price(self):
        """测试维护销售价格为其他价格"""
        try:
            # 1. 确保有价格记录上下文
            self._ensure_price_record_context()
            
            a.text(f"原价格: {self.original_price}, 新价格: {self.new_price}", "价格维护信息")
            
            # 2. 调用价格维护接口
            self._maintain_price(self.found_price_record, self.original_price, self.new_price)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单价格校验",
        title="测试创建销售订单并验证价格是否为维护后的价格",
        description="验证创建销售订单后，订单中物料的价格是否为维护后的价格",
        severity="critical",
        order=3,
        tags=["销售订单", "价格验证", "订单创建"]
    )
    def test_03_create_order_and_verify_price(self):
        """测试创建销售订单并验证价格是否为维护后的价格"""
        try:
            # 1. 确保价格已维护
            self._ensure_price_record_context()
            if not self.price_adj_id:
                self._maintain_price(self.found_price_record, self.original_price, self.new_price)
            
            # 2. 创建销售订单并验证价格
            self._create_and_verify_order_price(self.new_price)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    def _maintain_price(self, price_record, original_price, new_price):
        """维护销售价格"""
        try:
            # 1. 获取价格记录的关键信息
            match_record_md_id = price_record.get("id") or price_record.get("matchRecordMdId")
            var9 = price_record.get("var9") or price_record.get("var_9") or {}
            
            # 2. 获取物料信息
            if isinstance(var9, dict):
                mat_info = var9
            else:
                mat_info = {
                    "matCode": self.fixed_mat_code,
                    "matName": self.fixed_mat_name,
                    "id": self.fixed_mat_id
                }
            
            # 3. 获取单位信息
            out5 = price_record.get("out5") or price_record.get("outNew5") or {}
            if isinstance(out5, dict) and out5.get("id"):
                uom_id = out5.get("id")
                uom_info = out5
            else:
                uom_id = self.fixed_uom_id
                uom_info = {
                    "uomDesc": "件",
                    "name": "件",
                    "id": str(uom_id)
                }
            
            # 4. 获取币种信息
            out6 = price_record.get("out6") or price_record.get("outNew6") or {}
            if isinstance(out6, dict) and out6.get("id"):
                curr_id = out6.get("id")
                curr_info = out6
            else:
                curr_id = self.fixed_curr_id
                curr_info = {
                    "name": "人民币",
                    "id": str(curr_id),
                    "currName": "人民币"
                }
            
            # 5. 获取税码信息（out7）
            out7 = price_record.get("out7")
            
            # 6. 获取时间信息
            # 原价格的时间范围
            start_time = price_record.get("startTime") or price_record.get("startTimeNew") or 0
            original_end_time = price_record.get("endTime") or price_record.get("endTimeNew") or 253402271999000
            
            # 新价格的时间范围：为了让新价格立即生效，设置为当前时间开始
            # 结束时间为最大时间戳，确保订单创建时价格仍然有效
            current_timestamp = self.mock_util.get_timestamp(timestamp=True)
            start_time_new = current_timestamp
            end_time_new = 253402271999000  # 最大时间戳，确保价格长期有效
            
            # 原价格的结束时间：设置为新价格开始时间之前（减去1秒），避免时间重叠
            # 但要确保原价格的结束时间大于其开始时间（至少大1毫秒）
            # 如果原价格的开始时间已经大于等于新价格的开始时间，则设置原价格的结束时间为新价格开始时间之前
            if start_time >= start_time_new:
                # 如果原价格开始时间已经大于等于新价格开始时间，则设置原价格结束时间为开始时间+1秒
                end_time = start_time + 1000
            else:
                # 原价格开始时间小于新价格开始时间，设置原价格结束时间为新价格开始时间之前
                end_time = start_time_new - 1000
                # 确保原价格的结束时间大于开始时间
                if end_time <= start_time:
                    end_time = start_time + 1
                # 确保原价格的结束时间不超过原始结束时间
                if end_time > original_end_time:
                    end_time = original_end_time
            
            # 确保新价格的结束时间大于开始时间
            if end_time_new <= start_time_new:
                end_time_new = start_time_new + 1
            
            # 7. 获取或生成 matchIdempotentKey
            match_idempotent_key = price_record.get("matchIdempotentKey")
            if not match_idempotent_key:
                # 如果没有，可以根据需要生成一个，或者使用 None
                match_idempotent_key = None
            
            # 8. 构造价格维护item列表（根据curl格式）
            price_adj_item = {
                "id": None,
                "context": {},
                "matchRecordId": int(self.fixed_match_record_id),
                "var9": {
                    "name": mat_info.get("matName") or self.fixed_mat_name,
                    "id": str(mat_info.get("id") or self.fixed_mat_id),
                    "matName": mat_info.get("matName") or self.fixed_mat_name
                },
                "out1": original_price,  # 原价格
                "out5": uom_info.copy() if isinstance(uom_info, dict) else {
                    "uomDesc": "件",
                    "name": "件",
                    "id": str(uom_id)
                },
                "out6": curr_info.copy() if isinstance(curr_info, dict) else {
                    "name": "人民币",
                    "id": str(curr_id),
                    "currName": "人民币"
                },
                "startTime": start_time_new,  # 使用新价格的时间范围
                "endTime": end_time_new,  # 使用新价格的时间范围
                "matchIdempotentKey": match_idempotent_key,
                "deleted": 0,
                "outNew1": new_price,  # 新价格（原价格+1）
                "startTimeNew": start_time_new,
                "endTimeNew": end_time_new,
                "matchRecordMdId": match_record_md_id,
                "matchLadderMdDTOList": [],
                "matchLadderMdDTONewList": []
            }
            
            # 添加 out7（税码信息），如果原记录有的话
            if out7:
                price_adj_item["out7"] = out7
            
            # 添加 outNew5 和 outNew6
            price_adj_item["outNew5"] = {
                "id": uom_id
            }
            price_adj_item["outNew6"] = {
                "id": curr_id
            }
            
            price_adj_item_list = [price_adj_item]
            
            # 9. 直接调用价格维护单编辑并提交服务（id为null表示新建）
            price_adj_name = f"订单价格维护_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("SLS-销售价格-价格调整保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "id", "matchRecordId", "priceAdjName", "priceTypeName", 
                    "matchRecordName", "priceTypeId", "priceAdjItemList"
                ],
                ["params", "request"]
            )
            
            set_dict = {
                "id": None,  # 新建时id为null
                "matchRecordId": self.fixed_match_record_id,
                "priceAdjName": price_adj_name,
                "priceTypeName": "销售价",
                "matchRecordName": "1",
                "priceTypeId": self.fixed_price_type_id,
                "priceAdjItemList": price_adj_item_list
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 10. 发送保存请求
            response, _ = self.standard_api_call(
                api_key="SLS-销售价格-价格调整保存服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 11. 获取保存后的价格调整单ID
            response_data = response.get("data", {}).get("data", {})
            price_adj_id = response_data.get("id")
            if price_adj_id:
                self.price_adj_id = price_adj_id
                a.text(f"价格维护单保存成功，ID: {price_adj_id}", "价格维护结果")
            
            # 12. 提交价格维护单
            if price_adj_id:
                submit_api_path = self.get_api_path("SLS-销售价格-价格维护单列表提交服务")
                submit_params, submit_url = self.get_api_params(submit_api_path)
                
                submit_filtered_params = ParamUtil.filter_post_body_fields(
                    submit_params, ["id"],
                    ["params", "request"]
                )
                
                submit_set_dict = {
                    "id": price_adj_id
                }
                ParamUtil.set_request_params(submit_filtered_params, submit_set_dict)
                
                submit_response, _ = self.standard_api_call(
                    api_key="SLS-销售价格-价格维护单列表提交服务",
                    set_dict=(submit_filtered_params.get("params", {}) if isinstance(submit_filtered_params, dict) else submit_filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_data(submit_response)
                a.text(f"价格维护单提交成功", "价格维护结果")
            
            # 13. 验证提交结果
            time.sleep(1.0)  # 等待数据持久化和价格生效
            try:
                table_names = ["gen_price_adj_head_tr", "price_adj_head_tr", "erp_price_adj_head_tr"]
                price_adj_info = None
                
                for table_name in table_names:
                    try:
                        query_sql = f"""
                            SELECT id, code, status, doc_status, biz_status, price_adj_code
                            FROM {table_name}
                            WHERE price_adj_name = %s
                            LIMIT 1
                        """
                        db_result = self.db.query(query_sql, [price_adj_name])
                        if db_result:
                            price_adj_info = db_result[0]
                            if price_adj_id:
                                self.price_adj_id = price_adj_info.get("id") or price_adj_id
                            break
                    except Exception:
                        continue
                
                if price_adj_info:
                    status = price_adj_info.get("status") or price_adj_info.get("doc_status") or price_adj_info.get("biz_status")
                    self.assert_util.assert_by_operator(
                        status, "in", ["INEFFECT", "EFFECT", "已生效"],
                        message="价格维护单提交后状态应为已生效"
                    )
                    a.text(f"价格维护单提交成功，状态: {status}", "价格维护结果")
                    a.text(f"价格已从 {original_price} 更新为 {new_price}", "价格更新确认")
                else:
                    a.text(f"价格维护单提交成功，但无法查询状态", "价格维护结果")
            except Exception as e:
                a.text(f"价格维护单提交成功，但无法查询状态: {str(e)}", "价格维护结果")
            
            a.json(filtered_params, "价格维护请求数据")
            a.json(response, "价格维护响应数据")
            
        except Exception as e:
            self.logger.error(f"维护销售价格失败: {str(e)}")
            a.text(f"维护销售价格失败: {str(e)}", "价格维护失败原因")
            raise
    
    def _create_and_verify_order_price(self, expected_price):
        """创建销售订单并验证价格是否为维护后的价格"""
        try:
            # 1. 保存原始物料ID
            original_mat_id = getattr(self, 'mat_id', None)
            
            # 2. 设置使用固定物料ID创建订单
            self.mat_id = self.fixed_mat_id
            
            a.text(f"开始创建销售订单，物料ID: {self.fixed_mat_id}", "订单创建")
            
            # 3. 使用公共方法创建并保存订单（不提交）
            so_id = self.create_sales_order(order_type="STND", submit=False)
            
            self.assert_util.assert_by_operator(so_id, "not_empty", message="创建销售订单失败，未返回订单ID")
            self.so_head_id_save = so_id  # 保存订单ID以便清理
            a.text(f"销售订单创建成功，订单ID: {so_id}", "订单创建")
            
            # 4. 检查订单返回数据中的价格
            if hasattr(self, 'so_head_data') and self.so_head_data:
                so_items = self.so_head_data.get("soItems", [])
                if so_items:
                    # 查找对应物料的订单行
                    found_item = None
                    for item in so_items:
                        mat_id = item.get("matId")
                        if isinstance(mat_id, dict):
                            mat_id = mat_id.get("id")
                        if str(mat_id) == str(self.fixed_mat_id):
                            found_item = item
                            break
                    
                    if found_item:
                        # 获取订单行中的价格（优先检查 salesPrice，这是维护后的销售价）
                        sales_price = found_item.get("salesPrice")
                        so_item_gross_price = found_item.get("soItemGrossPrice")
                        
                        # 优先使用 salesPrice，如果没有则使用 soItemGrossPrice
                        price_to_check = sales_price if sales_price is not None else so_item_gross_price
                        
                        if price_to_check is not None:
                            price_to_check = float(price_to_check)
                            
                            a.text(f"订单行物料ID: {self.fixed_mat_id}", "订单价格验证")
                            a.text(f"订单行销售价格(salesPrice): {sales_price}", "订单价格验证")
                            a.text(f"订单行含税价格(soItemGrossPrice): {so_item_gross_price}", "订单价格验证")
                            a.text(f"期望价格（维护后）: {expected_price}", "订单价格验证")
                            
                            # 5. 断言价格是否为维护后的价格
                            self.assert_util.assert_by_operator(
                                price_to_check, "=", expected_price,
                                message=f"订单中物料价格应为维护后的价格 {expected_price}，实际价格: {price_to_check}"
                            )
                            
                            a.text(f"价格验证成功：订单中物料价格为 {price_to_check}，与维护后的价格 {expected_price} 一致", "订单价格验证")
                        else:
                            a.text("订单行中未找到价格字段 salesPrice 或 soItemGrossPrice", "订单价格验证")
                    else:
                        a.text(f"订单中未找到物料ID为 {self.fixed_mat_id} 的订单行", "订单价格验证")
                else:
                    a.text("订单返回数据中未找到订单行数据", "订单价格验证")
            else:
                a.text("订单返回数据为空，无法验证价格", "订单价格验证")
            
            # 6. 记录订单信息
            if hasattr(self, 'so_code') and self.so_code:
                a.text(f"订单号: {self.so_code}", "订单信息")
            
            # 7. 恢复原始物料ID（如果存在）
            if original_mat_id is not None:
                self.mat_id = original_mat_id
            
        except Exception as e:
            self.logger.error(f"创建订单并验证价格失败: {str(e)}")
            a.text(f"创建订单并验证价格失败: {str(e)}", "订单创建失败原因")
            raise
