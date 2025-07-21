import unittest
from quiz_dataset_tools.prebuild.doctor.sanity import TextSanityDoctor
from quiz_dataset_tools.prebuild.types import (
    PrebuildTextWarning,
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
        self.assertEqual(0, len(question_warnings))
        self.assertEqual(0, len(answer1_warnings))
        self.assertEqual(0, len(answer2_warnings))

    def test_forbidden_symbol(self):
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_prebuild_text("foo", es="es-`foo"),
            answers=[
                PrebuildAnswer(
                    make_prebuild_text("bo\no", fr="fr	-boo"), is_right_answer=True
                ),
            ],
        )
        doctor = TextSanityDoctor()

        question_warnings = doctor.check_question(question)
        expected_question_warning = PrebuildTextWarning(
            text_id=question.text.text_id,
            text_localization_id=question.text.localizations.ES.text_localization_id,
            code="SFS",
            content="Forbidden symbol: `",
        )
        self.assertEqual(1, len(question_warnings))
        self.assertEqual(expected_question_warning, question_warnings[0])

        answer_warnings = doctor.check_answer(question.answers[0])
        expected_answer_warning1 = PrebuildTextWarning(
            text_id=question.answers[0].text.text_id,
            text_localization_id=question.answers[
                0
            ].text.localizations.EN.text_localization_id,
            code="SFS",
            content="Forbidden symbol: \n",
        )
        expected_answer_warning2 = PrebuildTextWarning(
            text_id=question.answers[0].text.text_id,
            text_localization_id=question.answers[
                0
            ].text.localizations.FR.text_localization_id,
            code="SFS",
            content="Forbidden symbol: \t",
        )
        self.assertEqual(2, len(answer_warnings))
        self.assertEqual(expected_answer_warning1, answer_warnings[0])
        self.assertEqual(expected_answer_warning2, answer_warnings[1])

    def test_broken_numbers(self):
        doctor = TextSanityDoctor()

        # Simple valid case
        answer1 = PrebuildAnswer(
            make_prebuild_text("foo 1 boo 32", es="es-foo 1 es-boo 32"),
            is_right_answer=True,
        )
        answer1_warnings = doctor.check_question(answer1)
        self.assertEqual(0, len(answer1_warnings))

        # Complex valid number
        answer2 = PrebuildAnswer(
            make_prebuild_text("$1,000", es="$1000", fr="1000"),
            is_right_answer=True,
        )
        answer2_warnings = doctor.check_question(answer2)
        self.assertEqual(0, len(answer2_warnings))

        # Missed number
        answer3 = PrebuildAnswer(
            make_prebuild_text("foo 1 boo 2", es="es-foo 1 es-boo err"),
            is_right_answer=True,
        )
        answer3_warnings = doctor.check_question(answer3)
        expected_answer3_warning = PrebuildTextWarning(
            text_id=answer3.text.text_id,
            text_localization_id=answer3.text.localizations.ES.text_localization_id,
            code="SBN",
            content="Numbers in EN: [1, 2], aren't the same as in the translation: [1]",
        )
        self.assertEqual(1, len(answer3_warnings))
        self.assertEqual(expected_answer3_warning, answer3_warnings[0])
