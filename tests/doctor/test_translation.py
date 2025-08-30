import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.doctor.translation import TextTranslationDoctor
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
        text=make_prebuild_text("foo", fr="foo-fr"),
        answers=[
            PrebuildAnswer(
                make_prebuild_text("boo", es="boo-es"), is_right_answer=True
            ),
            PrebuildAnswer(
                make_prebuild_text("bar", ru="bar-ru"), is_right_answer=False
            ),
        ],
    )

    domain = "on"

    def test_check_question_prompt(self):
        gpt_mock = MagicMock()
        gpt_mock.send_prompt.return_value = "OK"
        doctor = TextTranslationDoctor(self.domain, gpt_service=gpt_mock)
        warnings = doctor.check_question(self.question)
        prompt = gpt_mock.send_prompt.call_args.args[0]
        self.assertIn("```\nfoo\n```", prompt)
        self.assertIn("```\nfoo-fr\n```", prompt)
        self.assertIn("French", prompt)
        self.assertEqual(warnings, [])

    def test_check_answer_prompt(self):
        gpt_mock = MagicMock()
        gpt_mock.send_prompt.return_value = "OK"
        doctor = TextTranslationDoctor(self.domain, gpt_service=gpt_mock)

        warnings = doctor.check_question(self.question.answers[0])
        prompt1 = gpt_mock.send_prompt.call_args.args[0]
        self.assertIn("```\nboo\n```", prompt1)
        self.assertIn("```\nboo-es\n```", prompt1)
        self.assertIn("Spanish", prompt1)
        self.assertEqual(warnings, [])

        warnings = doctor.check_question(self.question.answers[1])
        prompt2 = gpt_mock.send_prompt.call_args.args[0]
        self.assertIn("```\nbar\n```", prompt2)
        self.assertIn("```\nbar-ru\n```", prompt2)
        self.assertIn("Russian", prompt2)
        self.assertEqual(warnings, [])

    def test_multiple_warnings(self):
        gpt_mock = MagicMock()
        gpt_mock.send_prompt.side_effect = ["reason1", "OK", "reason2"]
        doctor = TextTranslationDoctor(self.domain, gpt_service=gpt_mock)

        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_prebuild_text("foo", fr="foo-fr", es="foo-es", ru="foo-ru"),
            answers=[],
        )
        warnings = doctor.check_question(question)
        self.assertEqual(
            warnings,
            [
                PrebuildTextWarning(
                    text_id=question.text.text_id,
                    text_localization_id=question.text.localizations.get(
                        Language.FR
                    ).text_localization_id,
                    code="TRN",
                    content="reason1",
                ),
                PrebuildTextWarning(
                    text_id=question.text.text_id,
                    text_localization_id=question.text.localizations.get(
                        Language.RU
                    ).text_localization_id,
                    code="TRN",
                    content="reason2",
                ),
            ],
        )
