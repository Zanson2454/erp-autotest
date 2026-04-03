import allure

from testcases.erp_pln import ErpPlnBaseTest
from utils.report_util import a, case_decorator


@allure.epic("计划管理")
@allure.feature("排产工序管理")
class TestPlnProcessManagement(ErpPlnBaseTest):
    """ERP_PLN 排产工序管理流程测试。"""

    MODEL_KEY = "ERP_PLN$pln_process_tr"
    TMODULE = "ERP_PLN"

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        super().bind_context()
        cls.front_process_id = None
        cls.middle_process_id = None
        cls.last_process_id = None
        cls.front_process_code = None
        cls.middle_process_code = None
        cls.last_process_code = None
        cls.logger.info("ERP_PLN 排产工序测试上下文初始化完成")

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    def _query_params(self):
        return {"tmodule": self.TMODULE, "modelKey": self.MODEL_KEY}

    def _extract_id(self, response, extracted_id):
        candidate = extracted_id
        if candidate is None and isinstance(response, dict):
            candidate = (
                response.get("data", {})
                .get("data", {})
                .get("id")
            )

        if isinstance(candidate, str) and candidate.isdigit():
            candidate = int(candidate)

        if not isinstance(candidate, int):
            raise AssertionError(f"保存后未拿到数值型 id, 当前值: {candidate}")
        return candidate

    def _build_save_payload(
        self,
        code,
        name,
        is_first,
        is_last,
        *,
        pre_process_id=None,
        post_process_id=None,
        process_id=None,
    ):
        return {
            "code": code,
            "name": name,
            "status": "ENABLED",
            "isFirst": is_first,
            "isLast": is_last,
            "preProcess": {"id": pre_process_id} if pre_process_id else None,
            "postProcess": {"id": post_process_id} if post_process_id else None,
            "terminationSeconds": 10,
            "scoringBasis": None,
            "optimizedDesc": None,
            "id": process_id,
        }

    def _save_process(
        self,
        code,
        name,
        is_first,
        is_last,
        *,
        pre_process_id=None,
        post_process_id=None,
        process_id=None,
    ):
        request_payload = self._build_save_payload(
            code=code,
            name=name,
            is_first=is_first,
            is_last=is_last,
            pre_process_id=pre_process_id,
            post_process_id=post_process_id,
            process_id=process_id,
        )
        set_dict = {
            "request": request_payload,
            "modelKey": self.MODEL_KEY,
        }
        response, extracted_id = self.standard_api_call(
            api_key="(系统)保存数据服务",
            set_dict=set_dict,
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            query_params=self._query_params(),
        )
        self.assert_util.assert_response_data(response)
        process_id = self._extract_id(response, extracted_id)
        return response, process_id

    def _query_process_list(self):
        set_dict = {
            "request": {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None,
                }
            },
            "modelKey": self.MODEL_KEY,
        }
        response, _ = self.standard_api_call(
            api_key="(系统)查询分页数据服务",
            set_dict=set_dict,
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            query_params=self._query_params(),
        )
        self.assert_util.assert_response_data(response)
        return response

    def _query_process_detail(self, process_id):
        set_dict = {
            "request": {"id": process_id},
            "modelKey": self.MODEL_KEY,
        }
        response, _ = self.standard_api_call(
            api_key="(系统)查询数据详情服务",
            set_dict=set_dict,
            store_id_as=None,
            use_param_util=False,
            param_path=["params"],
            query_params=self._query_params(),
        )
        self.assert_util.assert_response_data(response)
        return response

    @case_decorator(
        story="排产工序流程",
        title="新增前置工序并保存",
        description="创建前置工序",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["ERP_PLN", "工序", "新增"],
    )
    def test_01_create_front_process(self):
        try:
            code = self.mock_util.generate_unique_code(tag="PLN_F")
            name = f"前置工序_{self.mock_util.get_timestamp()}"
            _, process_id = self._save_process(
                code=code,
                name=name,
                is_first=True,
                is_last=False,
            )
            self.__class__.front_process_id = process_id
            self.__class__.front_process_code = code
            a.json({"front_process_id": process_id, "front_process_code": code}, "前置工序")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="排产工序流程",
        title="新增后置工序并关联前置工序",
        description="创建后置工序并关联步骤1",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["ERP_PLN", "工序", "关联"],
    )
    def test_02_create_middle_process_with_pre(self):
        try:
            if not self.front_process_id:
                raise AssertionError("前置工序 id 为空，请先执行步骤1")

            code = self.mock_util.generate_unique_code(tag="PLN_M")
            name = f"后置工序_{self.mock_util.get_timestamp()}"
            _, process_id = self._save_process(
                code=code,
                name=name,
                is_first=False,
                is_last=False,
                pre_process_id=self.front_process_id,
            )
            self.__class__.middle_process_id = process_id
            self.__class__.middle_process_code = code
            a.json(
                {
                    "middle_process_id": process_id,
                    "middle_process_code": code,
                    "pre_process_id": self.front_process_id,
                },
                "后置工序",
            )
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="排产工序流程",
        title="新增最后工序并关联后置工序",
        description="创建最后工序并关联步骤2",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["ERP_PLN", "工序", "关联"],
    )
    def test_03_create_last_process_with_middle(self):
        try:
            if not self.middle_process_id:
                raise AssertionError("后置工序 id 为空，请先执行步骤2")

            code = self.mock_util.generate_unique_code(tag="PLN_L")
            name = f"最后工序_{self.mock_util.get_timestamp()}"
            _, process_id = self._save_process(
                code=code,
                name=name,
                is_first=False,
                is_last=True,
                pre_process_id=self.middle_process_id,
            )
            self.__class__.last_process_id = process_id
            self.__class__.last_process_code = code
            a.json(
                {
                    "last_process_id": process_id,
                    "last_process_code": code,
                    "pre_process_id": self.middle_process_id,
                },
                "最后工序",
            )
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="排产工序流程",
        title="编辑前置工序并修改后置工序关联",
        description="更新步骤1工序，后置工序关联步骤2",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["ERP_PLN", "工序", "编辑"],
    )
    def test_04_update_front_process_post(self):
        try:
            if not self.front_process_id or not self.middle_process_id:
                raise AssertionError("关联工序 id 不完整，请先执行步骤1-2")

            updated_name = f"前置工序_修改_{self.mock_util.get_timestamp()}"
            response, process_id = self._save_process(
                code=self.front_process_code,
                name=updated_name,
                is_first=True,
                is_last=False,
                post_process_id=self.middle_process_id,
                process_id=self.front_process_id,
            )
            self.assert_util.assert_by_operator(process_id, "=", self.front_process_id)
            a.json(
                {
                    "front_process_id": self.front_process_id,
                    "post_process_id": self.middle_process_id,
                    "updated_name": updated_name,
                    "response": response,
                },
                "编辑前置工序",
            )
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="排产工序流程",
        title="查看工序列表",
        description="查询工序列表并校验返回结构",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["ERP_PLN", "工序", "列表"],
    )
    def test_05_view_process_list(self):
        try:
            response = self._query_process_list()
            rows = (
                response.get("data", {})
                .get("data", {})
                .get("data", [])
            )
            self.assert_util.assert_by_operator(rows, "not_empty")
            a.json({"count": len(rows)}, "工序列表数量")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="排产工序流程",
        title="查看工序详情",
        description="查询步骤3新增工序详情",
        severity="normal",
        file_level_order=6,
        smoke=True,
        tags=["ERP_PLN", "工序", "详情"],
    )
    def test_06_view_process_detail(self):
        try:
            if not self.last_process_id:
                raise AssertionError("最后工序 id 为空，请先执行步骤3")

            response = self._query_process_detail(self.last_process_id)
            detail = response.get("data", {}).get("data", {})
            if isinstance(detail, dict) and "id" in detail:
                returned_id = detail.get("id")
                if isinstance(returned_id, str) and returned_id.isdigit():
                    returned_id = int(returned_id)
                self.assert_util.assert_by_operator(returned_id, "=", self.last_process_id)
            a.json({"last_process_id": self.last_process_id, "detail": detail}, "工序详情")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
