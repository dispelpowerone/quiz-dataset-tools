from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
)


def make_question_context(question: PrebuildQuestion) -> str:
    return ""


def make_answer_context(question: PrebuildQuestion, answer: PrebuildAnswer) -> str:
    assert question.text.original
    question_en = question.text.original.get(Language.EN)
    assert question_en
    assert question_en.content
    return f"question: {question_en.content}; is_right_answer: {answer.is_right_answer}"
