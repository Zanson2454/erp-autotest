"""测试工具 mixin：将非核心工具从 BaseTest 拆分为按需注入。"""

from utils.async_wait_util import AsyncWaitUtil, WaitStatus
from utils.mock_util import MockData


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
