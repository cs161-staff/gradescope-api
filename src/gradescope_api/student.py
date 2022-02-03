from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from gradescope_api.client import GradescopeClient


class GradescopeStudent:
    def __init__(
        self,
        _client: GradescopeClient,
        user_id: str,
        full_name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        sid: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self._client = _client
        self.user_id = user_id
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.sid = sid
        self.email = email

    def get_user_id(self) -> str:
        return self.user_id
