import sqlite3
from util.dbase import DriverTestDBase
from util.loader import Loader
from util.language import Language
from util.data import Test, Question, Answer


class G1Loader(Loader):
    def get_tests(self):
        dbase = DriverTestDBase(dbase_path="g1canada/data/main.db")
        dbase.open()
        return {
            Language.EN: load_tests(dbase),
        }


def load_tests(dbase):
    test_obj_list = []
    for test in dbase.get_tests():
        test_obj_list.append(load_test(dbase, test.test_id))
    return test_obj_list


def load_test(dbase, test_id):
    test = dbase.get_test(test_id)
    return Test(
        title=load_text(dbase, test.text_id),
        questions=load_questions(dbase, test_id),
    )


def load_questions(dbase, test_id):
    question_obj_list = []
    for question in dbase.get_questions(test_id):
        question_obj_list.append(load_question(dbase, question.question_id))
    return question_obj_list


def load_question(dbase, question_id):
    question = dbase.get_question(question_id)
    return Question(
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
        text=load_text(dbase, answer.text_id),
        is_right_answer=answer.is_correct,
    )


def load_text(dbase, text_id):
    text = dbase.get_text(text_id)
    for localization in dbase.get_text_localizations(text_id):
        if localization.language_id == 1:
            return localization.content
    raise Exception(
        f"Missed localization: {text_id}, {dbase.get_text_localizations(text_id)}"
    )
