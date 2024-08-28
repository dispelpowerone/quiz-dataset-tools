import sqlite3
import re
from quiz_dataset_tools.util.dbase import DriverTestDBase
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.data import Test, Question, Answer
from quiz_dataset_tools.parser.parser import Parser


class DatabaseParser(Parser):
    def __init__(self, assets_path: str):
        self.assets_path = assets_path

    def get_tests(self) -> list[Test]:
        dbase_path = f"{self.assets_path}/main.db"
        dbase = DriverTestDBase(dbase_path=dbase_path)
        dbase.open()
        tests = load_tests(dbase)
        images = load_images_index(self.assets_path)
        for test in tests:
            for question in test.questions:
                question.image = images.get(question.orig_id)
        return tests


def load_images_index(assets_path: str) -> dict[int, str]:
    # Records format
    # '102': require('assets/img/questions/102.png'),
    record_re = re.compile("\\s+'(\\d+)':\\s+require\\('([^'/]+/?)+'\\)")
    index_path = f"{assets_path}/images/index.ts"
    index = {}
    with open(index_path) as file:
        for line in file:
            match = record_re.match(line)
            if not match:
                continue
            groups = match.groups()
            index[int(groups[0])] = groups[1]
    return index


def load_tests(dbase):
    test_obj_list = []
    for test in dbase.get_tests():
        test_obj_list.append(load_test(dbase, test.test_id))
    return test_obj_list


def load_test(dbase, test_id):
    test = dbase.get_test(test_id)
    return Test(
        orig_id=test_id,
        title=load_text(dbase, test.text_id),
        questions=load_questions(dbase, test_id),
        position=test.position,
    )


def load_questions(dbase, test_id):
    question_obj_list = []
    for question in dbase.get_test_questions(test_id):
        question_obj_list.append(load_question(dbase, question.question_id))
    return question_obj_list


def load_question(dbase, question_id):
    question = dbase.get_question(question_id)
    return Question(
        orig_id=question_id,
        text=load_text(dbase, question.text_id),
        answers=load_answers(dbase, question_id),
        image=None,
    )


def load_answers(dbase, question_id):
    answer_obj_list = []
    for answer in dbase.get_question_answers(question_id):
        answer_obj_list.append(load_answer(dbase, answer.answer_id))
    return answer_obj_list


def load_answer(dbase, answer_id):
    answer = dbase.get_answer(answer_id)
    return Answer(
        orig_id=answer_id,
        text=load_text(dbase, answer.text_id),
        is_right_answer=answer.is_correct,
    )


def load_text(dbase, text_id):
    # text = dbase.get_text(text_id)
    text_localizations = TextLocalizations(
        orig_id=text_id,
    )
    for localization in dbase.get_text_localizations(text_id):
        text_localizations.set(
            Language.from_id(localization.language_id), localization.content
        )
    # raise Exception(
    #    f"Missed localization: {text_id}, {dbase.get_text_localizations(text_id)}"
    # )
    # print(f"Missed localization: {text_id}, {dbase.get_text_localizations(text_id)}")
    return text_localizations
