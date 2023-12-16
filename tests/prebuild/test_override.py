import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language, TextLocalizations
from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.prebuild.stage import StageState
from driver_test_db.prebuild.stages.override import OverrideStage
from driver_test_db.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from tests.common import make_prebuild_text


class TestOverrideStage(unittest.TestCase):
    def setUp(self):
        self.override_list = [
            ("foo", "", "over-foo"),
            ("foo", "foo", "over-foo-foo"),
            ("boo", "foo", "over-foo-boo"),
            ("bar", "", "over-bar"),
        ]
        self.overrides = TextOverrides(domain="test")
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
                text=make_prebuild_text("foo"),
                answers=[
                    PrebuildAnswer(make_prebuild_text("foo"), is_right_answer=False),
                    PrebuildAnswer(make_prebuild_text("boo"), is_right_answer=True),
                    PrebuildAnswer(make_prebuild_text("bar"), is_right_answer=False),
                    PrebuildAnswer(make_prebuild_text("zee"), is_right_answer=False),
                ],
            ),
        ]
        stage = OverrideStage(overrides=self.overrides)
        state = stage.process(StageState(tests=tests, questions=questions))
        # Check test title
        self.assertEqual("Test 1", state.tests[0].title.localizations.get(Language.EN))
        # Check question text
        question_1 = state.questions[0]
        self.assertEqual("over-foo", question_1.text.localizations.get(Language.EN))
        # Check answer
        self.assertEqual(
            "over-foo-foo", question_1.answers[0].text.localizations.get(Language.EN)
        )
        self.assertEqual(
            "over-foo-boo", question_1.answers[1].text.localizations.get(Language.EN)
        )
        self.assertEqual(
            "bar", question_1.answers[2].text.localizations.get(Language.EN)
        )
        self.assertEqual(
            "zee", question_1.answers[3].text.localizations.get(Language.EN)
        )
