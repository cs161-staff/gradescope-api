from __future__ import annotations

import json
from datetime import datetime
from os.path import join
from typing import TYPE_CHECKING, Dict, List, Optional

from bs4 import BeautifulSoup
from gradescope_api.errors import check_response
from gradescope_api.student import GradescopeStudent
from gradescope_api.assignment import GradescopeAssignment
from gradescope_api.utils import get_url_id

if TYPE_CHECKING:
    from gradescope_api.client import GradescopeClient


class GradescopeCourse:
    def __init__(self, _client: GradescopeClient, course_id: str) -> None:
        self._client = _client
        self.course_id = course_id
        self.roster: List[GradescopeStudent] = []
    
    def create_assignment(self, name, start_date, due_date, late_due_date = None):
        """
        creates an assignment with given date/s
        name          : name of assignment, must be unique
        start_date    : assignment start datetime
        due_date      : assignment due datetime
        late_due_date : if the assignment canbe due late, datetime for that
        """
        STRFMT = '%b %d %G %I:%M %p'
        assert isinstance(start_date, datetime) and isinstance(due_date, datetime)
        if late_due_date:
            assert isinstance(late_due_date, datetime)
        start_date = start_date.strftime(STRFMT)
        due_date = due_date.strftime(STRFMT)
        late_due_date = late_due_date.strftime(STRFMT) if late_due_date else late_due_date
        form_data = {
            'authenticity_token': self._client._get_token(self._client.get_base_url(), meta="csrf-token"),
            'assignment[type]': "OnlineAssignment",
            'assignment[title]': name,
            'assignment[submissions_anonymized]': 0,
            'assignment[student_submission]': 'true',
            'assignment[release_date_string]': start_date,
            "assignment[due_date_string]": due_date,
            'assignment[allow_late_submissions]': bool(late_due_date),
            **({"assignment[hard_due_date_string]": late_due_date} if late_due_date else {}),
            "assignment[enforce_time_limit]": 0,
            "assignment[group_submission]": 0,
            "assignment[group_size]": "",
            "assignment[when_to_create_rubric]": "while_grading"
        }
        response = self._client.session.post(join(self.get_url(),'assignments'), data=form_data, timeout=20)
        return response

    def get_url(self) -> str:
        return self._client.get_base_url() + f"/courses/{self.course_id}"

    def get_roster(self) -> List[GradescopeStudent]:
        if self.roster:
            return self.roster

        url = self._client.get_base_url() + f"/courses/{self.course_id}/memberships"
        response = self._client.session.get(url=url, timeout=20)
        check_response(response, "failed to get roster")

        soup = BeautifulSoup(response.content, "html.parser")
        for row in soup.find_all("tr", class_="rosterRow"):
            nameButton = row.find("button", class_="js-rosterName")
            role = row.find("option", selected=True).text
            if nameButton and role == "Student":
                user_id = nameButton["data-url"].split("?user_id=")[1]
                editButton = row.find("button", class_="rosterCell--editIcon")
                if editButton:
                    data_email = editButton["data-email"]
                    data_cm: Dict = json.loads(editButton["data-cm"])
                    self.roster.append(
                        GradescopeStudent(
                            _client=self._client,
                            user_id=user_id,
                            full_name=data_cm.get("full_name"),
                            first_name=data_cm.get("first_name"),
                            last_name=data_cm.get("last_name"),
                            sid=data_cm.get("sid"),
                            email=data_email,
                        )
                    )

        return self.roster

    def get_student(self, sid: Optional[str] = None, email: Optional[str] = None) -> Optional[GradescopeStudent]:
        assert sid or email
        roster = self.get_roster()
        for student in roster:
            if sid != None and student.sid == sid:
                return student
            if email != None and student.email == email:
                return student
        return None

    def get_assignment(
        self, assignment_id: Optional[str] = None, assignment_url: Optional[str] = None
    ) -> Optional[GradescopeAssignment]:
        assert assignment_id or assignment_url
        assignment_id = assignment_id or get_url_id(url=assignment_url, kind="assignments")
        return GradescopeAssignment(_client=self._client, _course=self, assignment_id=assignment_id)
