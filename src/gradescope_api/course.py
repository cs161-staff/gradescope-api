import json
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from src.client import GradescopeClient
from src.errors import check_response
from src.student import GradescopeStudent


class GradescopeCourse:
    def __init__(self, _client: GradescopeClient, course_id: str) -> None:
        self._client = _client
        self.course_id = course_id
        self.roster: List[GradescopeStudent] = []

    def get_url(self) -> str:
        return self._client.get_base_url() + f"/courses/{self.course_id}"

    def get_roster(self) -> List[GradescopeStudent]:
        if self.roster:
            return self.roster

        url = self._client.get_base_url() + f"/courses/{self.course_id}/memberships"
        response = self._client.session.get(url=url)
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
                            client=self._client,
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
