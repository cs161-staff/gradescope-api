from gradescope_api.client import GradescopeClient
from gradescope_api.course import GradescopeCourse
from dotenv import load_dotenv
import os

load_dotenv()

client = GradescopeClient(email=os.environ["GS_EMAIL"], password=os.environ["GS_PASSWORD"])
course = client.get_course(course_url="https://www.gradescope.com/courses/56746/")
assignment = course.get_assignment(assignment_url="https://www.gradescope.com/courses/56746/assignments/942482/review_grades")
assignment.apply_extension('shomil+cs161test@berkeley.edu', 10)

# roster = course.get_roster()
# print(len(roster))
