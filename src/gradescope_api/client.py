from time import time
from typing import Any, Optional
from bs4 import BeautifulSoup
import requests
from requests import Response
from gradescope_api.course import GradescopeCourse

from gradescope_api.errors import check_response
from gradescope_api.utils import get_url_id

USER_AGENT = "gradescope-api"
BASE_URL = "https://gradescope.com"


class GradescopeClient:
    def __init__(self, email: str, password: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._log_in(email=email, password=password)

    def get_base_url(self) -> str:
        return BASE_URL

    def _get_token(
        self, url: str, action: Optional[Any] = None, meta: Optional[Any] = None, content: Optional[Any] = None
    ) -> str:
        """
        Return the Gradescope authenticity token.
        """
        if not content:
            response = self.session.get(url, timeout=20)
            content = response.content

        soup = BeautifulSoup(content, "html.parser")
        form = None
        if action:
            form = soup.find("form", {"action": action})
        elif meta:
            return soup.find("meta", {"name": meta})["content"]
        else:
            form = soup.find("form")

        return form.find("input", {"name": "authenticity_token"})["value"]

    def submit_form(
        self,
        url: str,
        referer_url: Optional[str] = None,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        header_token: Optional[Any] = None,
        json: Optional[Any] = None,
    ) -> Response:
        if not referer_url:
            referer_url = url
        headers = {"Host": "www.gradescope.com", "Origin": "https://www.gradescope.com", "Referer": referer_url}
        if header_token is not None:
            headers["X-CSRF-Token"] = header_token
        return self.session.post(url, data=data, json=json, files=files, headers=headers, timeout=20)

    def _log_in(self, email: str, password: str):
        url = BASE_URL + "/login"
        token = self._get_token(url)
        payload = {
            "utf8": "✓",
            "authenticity_token": token,
            "session[email]": email,
            "session[password]": password,
            "session[remember_me]": 1,
            "commit": "Log In",
            "session[remember_me_sso]": 0,
        }
        response = self.submit_form(url=url, data=payload)
        check_response(response, error="failed to log in")

    def get_course(self, course_url: Optional[str] = None, course_id: Optional[str] = None):
        course_id = course_id or get_url_id(course_url, "courses")
        return GradescopeCourse(_client=self, course_id=course_id)
