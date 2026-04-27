import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.prebuild.doctor.canonical import TextCanonicalDoctor
from quiz_dataset_tools.prebuild.types import (
    PrebuildTextWarning,
    PrebuildAnswer,
    PrebuildQuestion,
)
from tests.common import make_prebuild_text


class TestTextCanonicalDoctor(unittest.TestCase):

    question = PrebuildQuestion(
        test_id=1,
        question_id=1,
        text=make_prebuild_text("foo"),
        answers=[
            PrebuildAnswer(make_prebuild_text("boo"), is_right_answer=True),
            PrebuildAnswer(make_prebuild_text("bar"), is_right_answer=False),
        ],
    )

    domain = "on"

    def test_check_question_prompt(self):
        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)
        doctor.check_question(self.question)
        prompt = gpt_mock.send_prompt.call_args.args[0]
        self.assertIn("```\nfoo\n```", prompt)
        self.assertIn("boo", prompt)
        self.assertIn("bar", prompt)

    def test_check_question_ok(self):
        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)

        gpt_mock.send_prompt.return_value = "OK"
        warnings = doctor.check_question(self.question)
        self.assertEqual(0, len(warnings))

    def test_check_question_warning(self):
        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)

        gpt_mock.send_prompt.return_value = "Some warning"
        warnings = doctor.check_question(self.question)

        expected_warning = PrebuildTextWarning(
            text_id=self.question.text.text_id,
            text_localization_id=self.question.text.localizations.EN.text_localization_id,
            code="CNO",
            content="Some warning",
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(expected_warning, warnings[0])

    def test_check_answer_prompt(self):
        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)
        doctor.check_answer(self.question, self.question.answers[0])
        prompt = gpt_mock.send_prompt.call_args.args[0]
        self.assertIn("```\nfoo\n```", prompt)
        self.assertIn("```\nboo\n```", prompt)

    def test_check_answer_ok(self):
        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)

        gpt_mock.send_prompt.return_value = "OK"
        warnings = doctor.check_answer(self.question, self.question.answers[0])
        self.assertEqual(0, len(warnings))

    def test_check_answer_warning(self):
        answer = self.question.answers[0]

        gpt_mock = MagicMock()
        doctor = TextCanonicalDoctor(self.domain, gpt_service=gpt_mock)

        gpt_mock.send_prompt.return_value = "Some warning"
        warnings = doctor.check_answer(self.question, answer)

        expected_warning = PrebuildTextWarning(
            text_id=answer.text.text_id,
            text_localization_id=answer.text.localizations.EN.text_localization_id,
            code="CNO",
            content="Some warning",
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(expected_warning, warnings[0])
