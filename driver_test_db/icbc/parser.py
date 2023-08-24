import json
from typing import Any, List
from driver_test_db.util.data import Test, Question, Answer

TEST_SIZE = 15


def load_tests(language: str):
    data = None
    with open(f"icbc/data/{language}.json") as file:
        data = json.load(file)
    tests: List[Test] = []
    current_test = None
    for question_data in data:
        if not current_test:
            current_test = Test(
                title=f"Test {len(tests) + 1}",
                questions=[],
            )
        current_test.questions.append(parse_question(question_data))
        if len(current_test.questions) >= TEST_SIZE:
            tests.append(current_test)
            current_test = None
    if current_test and len(current_test.questions) > 4:
        tests.append(current_test)
    return tests


def parse_question(data: Any):
    question = Question(
        text=data["title"],
        image=data["image"],
        answers=[],
    )
    answer_correct_key = data["correct"]["answer"]
    for answer_key, answer_text in data["answers"].items():
        answer = Answer(
            text=answer_text,
            is_right_answer=(answer_key == answer_correct_key),
        )
        question.answers.append(answer)
    return question
