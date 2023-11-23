import os
import json
from typing import Callable
from driver_test_db.util.data import Question, Answer
from driver_test_db.util.language import Language
from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.usa.loader import USALoader
from driver_test_db.paraphrase.io import load_questions_chunked
from driver_test_db.paraphrase.types import ParaphrasedQuestion, ParaphrasedAnswer


def main() -> None:
    orig_questions = load_orig_questions()
    para_questions = load_questions_chunked(
        "data/usa/paraphrase", "done_{index}_paraphrase.out.json"
    )
    check_questions(orig_questions, para_questions)
    build_overrides(orig_questions, para_questions)


def load_orig_questions() -> list[Question]:
    orig_tests = USALoader().get_tests()
    questions: list[Question] = []
    for test in orig_tests[Language.EN]:
        questions.extend(test.questions)
    return questions


def check_questions(
    orig_questions: list[Question], para_questions: list[ParaphrasedQuestion]
) -> None:
    assert len(orig_questions) == len(para_questions)
    for i, orig_question in enumerate(orig_questions):
        para_question = para_questions[i]
        if para_question.text.orig != orig_question.text:
            print(
                f"Warning: question {i + 1}, '{para_question.text.orig}' != '{orig_question.text}'"
            )
        check_answers(i + 1, orig_question.answers, para_question.answers)


def check_answers(
    question_index: int,
    orig_answers: list[Answer],
    para_answers: list[ParaphrasedAnswer],
) -> None:
    assert len(orig_answers) == len(para_answers)
    for i, orig_answer in enumerate(orig_answers):
        para_answer = para_answers[i]
        if para_answer.text.orig != orig_answer.text:
            print(
                f"Warning: question {question_index} answer {i+1} isCorrect={orig_answer.is_right_answer}, '{para_answer.text.orig}' != '{orig_answer.text}'"
            )


def for_each_text(
    orig_questions: list[Question],
    para_questions: list[ParaphrasedQuestion],
    callback: Callable,
) -> None:
    for i, orig_question in enumerate(orig_questions):
        para_question = para_questions[i]
        orig_context = str(orig_question.orig_id)
        callback(
            context=orig_context,
            text=orig_question.text,
            override=para_question.text.final,
        )
        for j, orig_answer in enumerate(orig_question.answers):
            para_answer = para_question.answers[j]
            callback(
                context=orig_context,
                text=orig_answer.text,
                override=para_answer.text.final,
            )


def build_overrides(
    orig_questions: list[Question], para_questions: list[ParaphrasedQuestion]
) -> None:
    overrides = TextOverrides("usa", "ny")

    def put_override(context: str, text: str, override: str):
        if text != override and override.strip() != "":
            overrides.put(context, text, override)

    for_each_text(orig_questions, para_questions, put_override)
    overrides.save()


main()
