import unittest
from quiz_dataset_tools.prebuild.doctor.sanity import TextSanityDoctor
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
)
from tests.common import make_prebuild_text


class TestTextSanityDoctor(unittest.TestCase):
    def setUp(self):
        pass

    def test_forbidden_symbol_ok(self):
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_prebuild_text("foo"),
            answers=[
                PrebuildAnswer(
                    make_prebuild_text("boo", fr="fr-boo"), is_right_answer=True
                ),
                PrebuildAnswer(make_prebuild_text("b a r"), is_right_answer=False),
            ],
        )
        doctor = TextSanityDoctor()
        question_warnings = doctor.check_question(question)
        answer1_warnings = doctor.check_answer(question.answers[0])
        answer2_warnings = doctor.check_answer(question.answers[1])
        self.assertFalse(question_warnings)
        self.assertFalse(answer1_warnings)
        self.assertFalse(answer2_warnings)

    def test_forbidden_symbol(self):
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_prebuild_text("foo", es="es-`foo"),
            answers=[
                PrebuildAnswer(
                    make_prebuild_text("boo", fr="fr	-boo"), is_right_answer=True
                ),
                PrebuildAnswer(make_prebuild_text("b\nar"), is_right_answer=False),
            ],
        )
        doctor = TextSanityDoctor()
        question_warnings = doctor.check_question(question)
        answer1_warnings = doctor.check_answer(question.answers[0])
        answer2_warnings = doctor.check_answer(question.answers[1])
        self.assertEqual(1, len(question_warnings))
        self.assertEqual("SFS", question_warnings[0].code)
        self.assertEqual(1, len(answer1_warnings))
        self.assertEqual("SFS", answer1_warnings[0].code)
        self.assertEqual(1, len(answer2_warnings))
        self.assertEqual("SFS", answer2_warnings[0].code)

    def test_broken_numbers(self):
        doctor = TextSanityDoctor()

        answer1 = PrebuildAnswer(
            make_prebuild_text("foo 1 boo 32", es="es-foo 1 es-boo 32"),
            is_right_answer=True,
        )
        answer1_warnings = doctor.check_question(answer1)
        self.assertEqual(0, len(answer1_warnings))

        answer2 = PrebuildAnswer(
            make_prebuild_text("foo 1 boo 2", es="es-foo 1 es-boo err"),
            is_right_answer=True,
        )
        answer2_warnings = doctor.check_question(answer2)
        self.assertEqual(1, len(answer2_warnings))
        self.assertEqual("SBN", answer2_warnings[0].code)
