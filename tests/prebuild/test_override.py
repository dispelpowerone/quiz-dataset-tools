import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.prebuild.stage import StageState
from quiz_dataset_tools.prebuild.stages.override import OverrideStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from quiz_dataset_tools.prebuild.overrides import (
    make_question_context,
    make_answer_context,
)
from tests.common import make_prebuild_text


class TestOverrideStage(unittest.TestCase):
    def setUp(self):
        self.override_list = [
            ("foo", "", "over-foo"),
            ("foo", "question: foo; is_right_answer: False", "over-foo-foo"),
            ("boo", "question: foo; is_right_answer: True", "over-foo-boo"),
            ("bar", "", "over-bar"),
        ]
        self.overrides = TextOverrides(data_path="test")
        for entry in self.override_list:
            self.overrides.put(
                lang=Language.EN,
                text=entry[0],
                context=entry[1],
                override_lang=Language.EN,
                override=entry[2],
            )

    def test_end_to_end(self):
        tests = [
            PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=make_prebuild_text("foo", orig="foo"),
                answers=[
                    PrebuildAnswer(
                        make_prebuild_text("foo", orig="foo"), is_right_answer=False
                    ),
                    PrebuildAnswer(
                        make_prebuild_text("boo", orig="boo"), is_right_answer=True
                    ),
                    PrebuildAnswer(
                        make_prebuild_text("bar", orig="bar"), is_right_answer=False
                    ),
                    PrebuildAnswer(
                        make_prebuild_text("zee", orig="zee"), is_right_answer=False
                    ),
                ],
            ),
        ]
        stage = OverrideStage(languages=[Language.EN], overrides=self.overrides)
        state = stage.process(
            StageState(tests=tests, questions=questions, text_warnings=[])
        )
        # Check test title
        self.assertEqual(
            "Test 1", state.tests[0].title.localizations.get(Language.EN).content
        )
        # Check question text
        question_1 = state.questions[0]
        self.assertEqual(
            "over-foo", question_1.text.localizations.get(Language.EN).content
        )
        # Check answer
        self.assertEqual(
            "over-foo-foo",
            question_1.answers[0].text.localizations.get(Language.EN).content,
        )
        self.assertEqual(
            "over-foo-boo",
            question_1.answers[1].text.localizations.get(Language.EN).content,
        )
        self.assertEqual(
            "bar", question_1.answers[2].text.localizations.get(Language.EN).content
        )
        self.assertEqual(
            "zee", question_1.answers[3].text.localizations.get(Language.EN).content
        )
