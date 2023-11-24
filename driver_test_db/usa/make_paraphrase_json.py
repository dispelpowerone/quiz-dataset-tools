"""
#!/usr/bin/env python3

import dataclasses
import json

from driver_test_db.paraphrase.paraphrase import Paraphrase
from driver_test_db.util.language import Language
from driver_test_db.util.data import Question, Test
from driver_test_db.usa.loader import USALoader


@dataclasses.dataclass
class ParaphrasedText:
    orig: str
    candidate_1: str
    candidate_2: str
    final: str


@dataclasses.dataclass
class ParaphrasedAnswer:
    text: ParaphrasedText
    is_correct: bool


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

    chunk_size = 20
    chunk_name_templ = "output/paraphrase.out.{index}.json"
    chunk_index = 1
    while True:
        i = (chunk_index - 1) * chunk_size
        if i >= len(para_questions):
            break
        chunk_data = [dataclasses.asdict(e) for e in para_questions[i : i + chunk_size]]
        chunk_file = chunk_name_templ.format(index=chunk_index)
        chunk_index += 1

        with open(chunk_file, "w") as output:
            json.dump(chunk_data, output, indent=4)


def get_paraphrased_tests(tests, domain: str, request_templ: str):
    paraphrase = Paraphrase(domain, request_templ=request_templ)
    paraphrase.load_cache()

    def transformer(text: str) -> str:
        return paraphrase.get(text)

    para_tests = [test.transform_texts(transformer) for test in tests]

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
                ),
                is_correct=orig_question.answers[i].is_right_answer,
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
"""
