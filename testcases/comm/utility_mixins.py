"""测试工具 mixin：将非核心工具从 BaseTest 拆分为按需注入。"""

from testcases.comm.query_service import QueryService
from utils.async_wait_util import AsyncWaitUtil, WaitStatus
from utils.mock_util import MockData
from utils.yaml_util import YamlUtil


class MockUtilMixin:
    """按需注入 MockData。"""

    @classmethod
    def _initialize_optional_utilities(cls) -> None:
        super()._initialize_optional_utilities()
        cls.mock_util = MockData()


class AsyncWaitMixin:
    """按需注入 AsyncWaitUtil / WaitStatus。"""

    @classmethod
    def _initialize_optional_utilities(cls) -> None:
        super()._initialize_optional_utilities()
        cls.async_wait_util = AsyncWaitUtil
        cls.wait_status = WaitStatus


class YamlUtilMixin:
    """按需注入 YamlUtil。"""

    @classmethod
    def _initialize_optional_utilities(cls) -> None:
        super()._initialize_optional_utilities()
        cls.yaml_util = YamlUtil()


class QueryServiceMixin:
    """按需注入 QueryService（依赖 cls.db）。"""

    @classmethod
    def _initialize_optional_utilities(cls) -> None:
        super()._initialize_optional_utilities()
        cls.query_service = QueryService(cls.db)
