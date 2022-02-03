import json
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from core.client import GradescopeClient
from core.errors import check_response
from core.student import GradescopeStudent
from core.utils import get_course_id


class GradescopeCourse:
    def __init__(
        self, client: GradescopeClient, course_id: Optional[str] = None, course_url: Optional[str] = None
    ) -> None:
        assert course_id or course_url
        self.course_id = course_id or get_course_id(course_url)
        self.client = client
        self.roster: List[GradescopeStudent] = []

    def get_roster(self) -> List[GradescopeStudent]:
        if self.roster:
            return self.roster

        url = self.client.get_base_url() + f"/courses/{self.course_id}/memberships"
        response = self.client.get(url=url)
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
                            user_id=user_id,
                            full_name=data_cm.get("full_name"),
                            first_name=data_cm.get("first_name"),
                            last_name=data_cm.get("last_name"),
                            sid=data_cm.get("sid"),
                            email=data_email,
                        )
                    )

        return self.roster
