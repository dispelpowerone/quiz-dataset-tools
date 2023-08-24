#!/usr/bin/env python3

import json

from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.util.images import Images


def load_tests(dbase):
    test_obj_list = []
    for test in dbase.get_tests():
        test_obj_list.append(load_test(dbase, test.test_id))
    return test_obj_list


def load_test(dbase, test_id):
    test = dbase.get_test(test_id)
    test_obj = {}
    test_obj["TestId"] = test_id
    test_obj["Text"] = load_text(dbase, test.text_id)
    return test_obj


def load_questions(dbase):
    question_obj_list = []
    for question in dbase.get_questions():
        question_obj_list.append(load_question(dbase, question.question_id))
    return question_obj_list


def load_question(dbase, question_id):
    question = dbase.get_question(question_id)
    question_obj = {}
    # question_obj["QuestionId"] = question.question_id
    question_obj["TestId"] = question.test_id
    question_obj["Text"] = load_text(dbase, question.text_id)
    question_obj["Answers"] = load_answers(dbase, question_id)
    question_obj["Tips"] = ""
    question_obj["StudyGuideQuestionId"] = None
    return question_obj


def load_answers(dbase, question_id):
    answer_obj_list = []
    for answer in dbase.get_question_answers(question_id):
        answer_obj_list.append(load_answer(dbase, answer.answer_id))
    return answer_obj_list


def load_answer(dbase, answer_id):
    answer = dbase.get_answer(answer_id)
    answer_obj = {}
    # answer_obj["AnswerId"] = answer.answer_id
    # answer_obj["QuestionId"] = answer.question_id
    answer_obj["Text"] = load_text(dbase, answer.text_id)
    if answer.is_correct:
        answer_obj["IsCorrect"] = True
    return answer_obj


def load_text(dbase, text_id):
    text = dbase.get_text(text_id)
    for localization in dbase.get_text_localizations(text_id):
        if localization.language_id == 1:
            return localization.content
    return ""
    """
    text_obj = {}
    text_obj["TextId"] = text.text_id
    text_obj["Description"] = text.description
    localizations_obj = {}
    for localization in dbase.get_text_localizations(text_id):
        language = dbase.get_language(localization.language_id)
        localizations_obj[language.language_name] = localization.content
    text_obj["Localizations"] = localizations_obj
    return text_obj
    """


def main():
    dbase = DriverTestDBase()
    dbase.open()
    tests = load_tests(dbase)
    questions = load_questions(dbase)
    print(json.dumps(questions, ensure_ascii=False, indent=4))


main()
