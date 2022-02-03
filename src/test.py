from gradescope_api.client import GradescopeClient
from gradescope_api.course import GradescopeCourse
from dotenv import load_dotenv
import os

load_dotenv()

client = GradescopeClient(email=os.environ["GS_EMAIL"], password=os.environ["GS_PASSWORD"])
course = client.get_course(course_url="https://www.gradescope.com/courses/56746/")
roster = course.get_roster()
print(len(roster))
