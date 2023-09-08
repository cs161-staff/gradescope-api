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

import re
import copy

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

    def make_questions(self, assignment_id: str, questions: List[Dict]):
        # url = self._client.get_base_url() + f"/courses/{self.course_id}/assignments/{assignment_id}/outline/edit"
        url = "https://www.gradescope.com/courses/404061/assignments/2137634/outline"
        new_patch = {#"assignment": {"identification_regions": {"name": None, "sid": None}}, 
                "outline": questions,
                "base_hash": "bb6d332c7bd79731d089eabe085d2128",
                "ignore_warnings": False
                }
        # new_patch = {'assignment': {'identification_regions': {'name': None, 'sid': None}}, 
        #         'question_data': questions}
        # tried put as well, didn't work
        response = self._client.session.patch(url=url,
                                            headers = {"X-CSRF-Token": self._client._get_token("https://www.gradescope.com/courses/404061/assignments/2137634/outline/edit", meta="csrf-token"),
                                                    # "Content-Type": "application/json"},
                                                    "Accept": "application/json, text/javascript, */*; q=0.01",
                                                    "Accept-Language": "en-US,en;q=0.9",
                                                    "Accept-Encoding": "gzip, deflate, br",
                                                    "Host": "www.gradescope.com",
                                                    "Origin": "https://www.gradescope.com",
                                                    "Referer": "https://www.gradescope.com/courses/404061/assignments/2137634/outline/edit",
                                                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},      
                                            data = json.dumps(new_patch, separators=(',',':')),
                                            # json=json.dumps(new_patch, separators=(',',':')),
                                            # params = {"outline": questions},
                                            timeout=20)
        check_response(response, "failed to make questions")

    def grade_self_grade_assignment(self, assignment_id: str, regrade_all = False):
        url = self._client.get_base_url() + f"/courses/{self.course_id}/assignments/{assignment_id}/grade"
        user_response = input(f"You are about to grade {url}. Please double check that this is the correct assignment and type CONFIRM if you wish to proceed.")
        if user_response != "CONFIRM":
            print("Aborting")
            return
        response = self._client.session.get(url=url, timeout=20)
        check_response(response, "failed to access grade submissions page")
        soup = BeautifulSoup(response.content, "html.parser")

        subquestion_list = soup.find_all("div", {"class": ["gradingDashboard--subquestion", "gradingDashboard--question"]})
        for subquestion in subquestion_list:
            question_num = subquestion.find("a", {"class": "link-noUnderline"}).text.split(":")[0]
            submission_link = self._client.get_base_url() + subquestion.find("a", {"class": re.compile(r'link-gray link-noUnderline gradingDashboard--listAllLink')})["href"]
            grading_progress = float(subquestion.find("span", {"class": "gradingDashboard--progressPercent"}).text[:-1])
            if grading_progress < 100 or regrade_all:
                print(f"QUESTION {question_num}: grading, {submission_link}")
                self.grade_self_grade_question(question_num, submission_link, regrade_all)
                print()
            else:
                print(f"QUESTION {question_num}: already graded, skipping")
                print()
            
            # break 

    def grade_self_grade_question(self, question_num, submission_link, regrade_all = False):
        response = self._client.session.get(url=submission_link, timeout=20)
        check_response(response, "failed to get list of submissions for individual question")
        soup = BeautifulSoup(response.content, "html.parser")
        submission_list = soup.find_all("table", {"class":"table", "id":"question_submissions"})[0].find_all("tr")[1:]
        for submission in submission_list:
            # print(submission)
            submission_question_link = self._client.get_base_url() + submission.find("a")["href"]
            student_name = submission.find("a").text
            is_graded = len(submission.find_all("i", {"class": "fa fa-check"}))

            if is_graded and not regrade_all:
                print(f"skipping: {question_num}, {student_name}, {submission_question_link}")
            else:
                print(f"grading: {question_num}, {student_name}, {submission_question_link}")
                self.grade_self_grade_question_submission(question_num, student_name, submission_question_link)
            
            # break

        # submission_list = soup.find_all("td", {"class": "table--primaryLink table--primaryLink-small"})
        # for submission in submission_list:
        #     print(submission)
        #     submission_question_link = self._client.get_base_url() + submission.find("a")["href"]
        #     student_name = submission.find("a").text
        #     self.grade_self_grade_question_submission(question_num, student_name, submission_question_link)

        #     break

    def grade_self_grade_question_submission(self, question_num, student_name, submission_question_link):
        response = self._client.session.get(url=submission_question_link, timeout=20)
        check_response(response, "failed to access individual question submission")
        soup = BeautifulSoup(response.content, "html.parser")
        question_data = json.loads(soup.find_all("div", {"data-react-class": "SubmissionGrader"})[0]["data-react-props"])
        rubric_info = [[rubric_item['id'], int(float(rubric_item['weight']))] for rubric_item in question_data["rubric_items"]]
        answer = question_data["submission"]["answers"]
        score = -1
        if "0" in answer:
            score =  int(re.search(r"\d+", str(answer["0"])).group(0))
        else:
            score = -0.01
        assert score != -1, "failed to get score"
        # print(answer, score)
        self.save_grade_self_grade_question_submission(score, question_num, student_name, rubric_info, submission_question_link, submission_question_link[:-6] + "/save_grade")
    
    def save_grade_self_grade_question_submission(self, score, question_num, student_name, rubric_info, submission_question_link, save_grade_link):
        # print(score, save_grade_link)

        grading_dict = {
            "rubric_items":{},
            "question_submission_evaluation": {
                "points": 0,
                "comments":None
            }
        }
        score = max(0, score)
        for rubric_item in rubric_info:
            grading_dict["rubric_items"][rubric_item[0]] = {
                "score": score == rubric_item[1]
            }
        

        # grading_dict["question_submission_evaluation"]["points"] is used for manual point assignments; it works but when put to 0, the score is not marked as "graded", so we're avoiding it for now
        # grading_dict["question_submission_evaluation"]["points"] = score

        # print(grading_dict)
        headers = {
            "Host": "www.gradescope.com",
            "Origin": "https://www.gradescope.com",
            "Referer": submission_question_link,
            "X-CSRF-Token": self._client._get_token(submission_question_link, meta="csrf-token"),
        }
        response = self._client.session.post(save_grade_link, headers=headers, json=grading_dict, timeout=20)
        check_response(response, "failed to save grade")


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
