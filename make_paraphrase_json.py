#!/usr/bin/env python3

import dataclasses
import json

from util.paraphrase import Paraphrase
from util.language import Language
from util.data import Question
from usa.loader import USALoader


@dataclasses.dataclass
class ParaphrasedText:
    orig: str
    candidate_1: str
    candidate_2: str
    final: str


@dataclasses.dataclass
class ParaphrasedAnswer:
    text: ParaphrasedText


@dataclasses.dataclass
class ParaphrasedQuestion:
    id: int
    text: ParaphrasedText
    image: str
    answers: list[ParaphrasedAnswer]


def main():
    orig_tests = USALoader().get_tests()
    orig_en_tests = orig_tests[Language.EN]

    para_tests_1 = get_paraphrased_tests(
        orig_en_tests, "usa_r_1", Paraphrase.REQUEST_TEMPL_1
    )
    para_tests_2 = get_paraphrased_tests(
        orig_en_tests, "usa_r_2", Paraphrase.REQUEST_TEMPL_2
    )

    para_questions = get_paraphrased_questions(
        orig_en_tests, para_tests_1, para_tests_2
    )
    para_questions_dict = [dataclasses.asdict(e) for e in para_questions]

    with open("paraphrase.out.json", "w") as output:
        json.dump(para_questions_dict, output, indent=4)


def get_paraphrased_tests(tests, domain: str, request_templ: str):
    paraphrase = Paraphrase(domain, request_templ=request_templ)
    paraphrase.load_cache()
    para_tests = paraphrase.paraphrase_tests(tests)
    paraphrase.save_cache()
    return para_tests


def get_paraphrased_questions(orig_tests, para_tests_1, para_tests_2):
    para_questions = list()
    for i in range(len(orig_tests)):
        orig_test = orig_tests[i]
        para_test_1 = para_tests_1[i]
        para_test_2 = para_tests_2[i]
        for j in range(len(orig_test.questions)):
            orig_question = orig_test.questions[j]
            para_question_1 = para_test_1.questions[j]
            para_question_2 = para_test_2.questions[j]
            para_questions.append(
                pack_paraphrased_question(
                    len(para_questions) + 1,
                    orig_question,
                    para_question_1,
                    para_question_2,
                )
            )
    return para_questions


def pack_paraphrased_question(
    id: int,
    orig_question: Question,
    para_question_1: Question,
    para_question_2: Question,
):
    answers = list()
    for i in range(len(orig_question.answers)):
        answers.append(
            ParaphrasedAnswer(
                text=ParaphrasedText(
                    orig=orig_question.answers[i].text,
                    candidate_1=para_question_1.answers[i].text,
                    candidate_2=para_question_2.answers[i].text,
                    final="",
                )
            )
        )
    return ParaphrasedQuestion(
        id=id,
        text=ParaphrasedText(
            orig=orig_question.text,
            candidate_1=para_question_1.text,
            candidate_2=para_question_2.text,
            final="",
        ),
        image=orig_question.image,
        answers=answers,
    )


main()
