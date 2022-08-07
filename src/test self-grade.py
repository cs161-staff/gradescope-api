from datetime import datetime, timedelta
from gradescope_api.client import GradescopeClient
from gradescope_api.course import GradescopeCourse
from gradescope_api.self_grades import *
from dotenv import load_dotenv
import os

load_dotenv()

test_questions = [
    {
    "id": 16873156,
    "type": "OnlineQuestion",
    "title": "abcdefg",
    "parent_id": None,
    "index": 1,
    "weight": "5",
    "content": [
      {
        "type": "text",
        "value": "hijklmnop"
      }
    ]
  }
]

client = GradescopeClient(email=os.environ["GS_EMAIL"], password=os.environ["GS_PASSWORD"])
course = client.get_course(course_url="https://www.gradescope.com/courses/404061")

assignment_name = "sub to shrey"
course.create_assignment(assignment_name, datetime.now(), datetime.now() + timedelta(days=1))
# temp = course.make_questions(2137634, create_assignment_json(9, [1, 2, 6, 6, 3, 2, 4, 1, 3]))
temp = course.make_questions(2153137, test_questions)

# print(temp)

# roster = course.get_roster()
# print(len(roster))
