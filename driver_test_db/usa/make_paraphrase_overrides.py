import os
import json
from typing import Callable
from driver_test_db.util.data import Question, Answer
from driver_test_db.util.language import Language
from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.parser.usa.parser import USADatabaseParser
from driver_test_db.paraphrase.io import load_questions_chunked
from driver_test_db.paraphrase.types import ParaphrasedQuestion, ParaphrasedAnswer
from pprint import pprint


def main() -> None:
    orig_questions = load_orig_questions()
    para_questions = load_questions_chunked(
        "data/usa/paraphrase", "done_{index}_paraphrase.out.json"
    )
    print(
        f"Loaded {len(orig_questions)} orig and {len(para_questions)} paraphrased questions"
    )
    # check_questions(orig_questions, para_questions)
    build_overrides(para_questions)


def load_orig_questions() -> list[Question]:
    orig_tests = USADatabaseParser().get_tests()
    questions: list[Question] = []
    for test in orig_tests:
        questions.extend(test.questions)
    return questions


def check_questions(
    orig_questions: list[Question], para_questions: list[ParaphrasedQuestion]
) -> None:
    for i, orig_question in enumerate(orig_questions):
        if i >= len(para_questions):
            break
        orig_question_text = orig_question.text.get(Language.EN)
        para_question = para_questions[i]
        if para_question.text.orig != orig_question_text:
            print("para_question.id: ", para_question.id)
            print("para_question.text.orig: ", para_question.text.orig)
            print("orig_question_text: ", orig_question_text)
            raise Exception(f"No orig question found")
        check_answers(orig_question, para_question)


def check_answers(
    orig_question: Question,
    para_question: ParaphrasedQuestion,
) -> None:
    assert len(orig_question.answers) == len(para_question.answers)
    for i, orig_answer in enumerate(orig_question.answers):
        para_answer = para_question.answers[i]
        if not orig_answer.is_right_answer:
            if not para_answer.text.final:
                print("para_question.id:", para_question.id)
                print("orig_answer.text:", orig_answer.text.get(Language.EN))
                raise Exception(
                    f"No final text: index={i},\norig_question={orig_question},\npara_question={para_question}"
                )
        else:
            if para_answer.text.orig != orig_answer.text.get(Language.EN):
                pprint(orig_question)
                pprint(para_question)
                raise Exception(
                    f"Answer missmatch: index={i},\norig_question={orig_question},\npara_question={para_question}"
                )


def for_each_text(
    para_questions: list[ParaphrasedQuestion],
    callback: Callable,
) -> None:
    for para_question in para_questions:
        callback(
            context="",
            text=para_question.text.orig,
            override=para_question.text.final,
        )
        for para_answer in para_question.answers:
            callback(
                context=para_question.text.orig,
                text=para_answer.text.orig,
                override=para_answer.text.final,
            )


def build_overrides(para_questions: list[ParaphrasedQuestion]) -> None:
    overrides = TextOverrides("ny")

    def put_override(context: str, text: str, override: str):
        if override.strip() != "":
            overrides.put(
                lang=Language.EN,
                text=text,
                context=context,
                override_lang=Language.EN,
                override=override,
            )

    for_each_text(para_questions, put_override)
    overrides.save()


main()
