from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AuthContext:
    """认证上下文，聚合 BaseTest 认证阶段产生的核心会话信息。"""

    user_info: Optional[Dict[str, Any]]
    session: Any
    portal_url: str
    iam_url: str
    portal_headers: Optional[Dict[str, str]]
    iam_headers: Optional[Dict[str, str]]

    @classmethod
    def from_login_result(cls, login_result: Any) -> "AuthContext":
        return cls(
            user_info=getattr(login_result, "user_info", None),
            session=getattr(login_result, "session", None),
            portal_url=getattr(login_result, "portal_url", "") or "",
            iam_url=getattr(login_result, "iam_url", "") or "",
            portal_headers=getattr(login_result, "portal_headers", None),
            iam_headers=getattr(login_result, "iam_headers", None),
        )
