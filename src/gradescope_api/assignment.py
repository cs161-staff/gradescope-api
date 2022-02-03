from datetime import datetime
from http import client
from typing import TYPE_CHECKING, Optional

from gradescope_api.course import GradescopeCourse
from gradescope_api.errors import check_response

if TYPE_CHECKING:
    from gradescope_api.client import GradescopeClient

GRADESCOPE_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class GradescopeAssignment:
    def __init__(self, _client: GradescopeClient, _course: GradescopeCourse, assignment_id: str) -> None:
        self._client = _client
        self._course = _course
        self.assignment_id = assignment_id

    def get_url(self) -> str:
        return self._course.get_url() + f"/assignments/{self.assignment_id}"

    def create_extension(self, user_id: str, due_date: datetime, hard_due_date: Optional[datetime] = None):
        """
        Create an extension for a student for this particular assignment. If a hard due date is not provided,
        the hard due date will be set to the provided due date. This behavior is temporary and should be changed
        to be the later of the current hard due date and the provided due date.
        """
        if hard_due_date:
            assert hard_due_date >= due_date

        url = self.get_url() + "/extensions"
        headers = {
            "Host": "www.gradescope.com",
            "Origin": "https://www.gradescope.com",
            "Referer": url,
            "X-CSRF-Token": self._client._get_token(url, meta="csrf-token"),
        }
        payload = {
            "override": {
                "user_id": user_id,
                "settings": {
                    "due_date": {"type": "absolute", "value": due_date.strftime(GRADESCOPE_DATETIME_FORMAT)},
                    "hard_due_date": {
                        "type": "absolute",
                        "value": (hard_due_date or due_date).strftime(GRADESCOPE_DATETIME_FORMAT),
                    },
                },
            }
        }

        response = self._client.session.post(url, headers=headers, json=payload)
        check_response(response, "creating an extension failed")
