from src.client import GradescopeClient
from dotenv import load_dotenv
import os

from src.course import GradescopeCourse

load_dotenv()

client = GradescopeClient(email=os.environ["GS_EMAIL"], password=os.environ["GS_PASSWORD"])
course = GradescopeCourse(client=client, course_url="https://www.gradescope.com/courses/56746/")

print(vars(course.get_roster()))
