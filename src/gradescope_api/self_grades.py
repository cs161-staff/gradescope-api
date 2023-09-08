import json
import copy

QUESTION_DICT = {
    "children": None,
    "id": None,
    "parent_id": None,
    "index": None,
    "content": [],
    "type": "QuestionGroup",
    "title": "",
    "weight": None
}
SUBPART_DICT = {
    "id": None, #16872982,
    "type": "OnlineQuestion",
    "title":  None, #"2 (a)",
    "parent_id": None, # 16872981,
    "index": None,
    "weight": "10.0",
    "content": [
        {
            "type": "text",
            "value": ""
        },
        {
            "type": "radio_input",
            "choices": [
                {
                    "value": "**0**: Didn't attempt or very very wrong)",
                    "answer": False
                },
                {
                    "value": "**2**: Got started and made some progress, but went off in the wrong direction or with no clear direction",
                    "answer": False
                },
                {
                    "value": "**5**: Right direction and got halfway there",
                    "answer": False
                },
                {
                    "value": "**8**: Mostly right but a minor thing missing or wrong",
                    "answer": False
                },
                {
                    "value": "**10**: 100% correct",
                    "answer": False
                }
            ]
        },
        {
            "type": "text",
            "value": "Comments:"
        },
        {
            "type": "free_response_input"
        }
    ]
}

def create_assignment_json(num_questions, num_parts):
    "num_questions: int, number of questions in the assignment; 1 indexed"
    "num_parts: array of ints, number of parts in each question; 1 indexed"
    index = 0;
    assert num_questions == len(num_parts)
    assert num_questions > 0
    for num_part in num_parts:
        assert num_part > 0
    questions_arr = []
    for question_num in range(1, num_questions + 1):
        children_arr = []
        for part_num in range(1, num_parts[question_num - 1] + 1):
            children_arr.append(create_subpart_json(question_num, part_num))
        question_dict = create_question_json(question_num, children_arr)
        questions_arr.append(question_dict)
    return questions_arr


def create_question_json(question_num, children_arr):
    question_dict = copy.deepcopy(QUESTION_DICT)
    question_dict["children"] = copy.deepcopy(children_arr)
    question_dict["id"] = question_num
    question_dict["index"] = question_num
    if question_num == 1:
        question_dict["content"] = [{
            "type": "text",
            "value": "something something instructions \nsub 2 shreytechtips"
        }]
    question_dict["weight"] = (10 * len(children_arr))
    return question_dict


def create_subpart_json(question_num, part_num):
    subpart_dict = copy.deepcopy(SUBPART_DICT)
    subpart_dict["id"] = int(str(question_num) + "00" + str(part_num))
    subpart_dict["title"] = str(question_num) + " (" + str(chr(ord('`') + part_num)) + ")"
    subpart_dict["parent_id"] = question_num
    subpart_dict["index"] = part_num
    return subpart_dict

#  output_json = json.dumps(create_assignment_json(9, [1, 2, 6, 6, 3, 2, 4, 1, 3]))
#  print(output_json)
