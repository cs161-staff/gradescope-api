def get_id(url: str, kind: str) -> str:
    return url.split(f"/{kind}/")[1].split("/")[0]


def get_course_id(url: str) -> str:
    """
    Input: https://www.gradescope.com/courses/351819/...
    Output: 351819
    """
    return get_id(url, "courses")


def get_assignment_id(url: str) -> str:
    """
    Input: https://www.gradescope.com/courses/351819/assignments/1807855/...
    Output: 1807855
    """
    return get_id(url, "assignments")


def get_submission_id(url: str) -> str:
    """
    Input: https://www.gradescope.com/courses/351819/assignments/1807855/submissions/108848552/...
    Output: 108848552
    """
    return get_id(url, "submissions")
