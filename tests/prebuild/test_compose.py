import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language, TextLocalizations
from driver_test_db.prebuild.stage import StageState
from driver_test_db.prebuild.stages.compose import ComposeMode, ComposeStage
from driver_test_db.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from tests.common import make_prebuild_text


class TestComposeStage(unittest.TestCase):
    def setUp(self):
        pass

    def test_fix_missed(self):
        tests = [
            PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
            PrebuildTest(test_id=2, title=make_prebuild_text("Test 2")),
            PrebuildTest(test_id=3, title=make_prebuild_text("Test 3")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=make_prebuild_text("T1Q1"),
                answers=[],
            ),
            PrebuildQuestion(
                test_id=2,
                question_id=1,
                text=make_prebuild_text("T2Q1"),
                answers=[],
            ),
        ]
        stage = ComposeStage(ComposeMode.FIX_MISSED, questions_per_test=2)
        state = stage.process(StageState(tests=tests, questions=questions))
        self.assertEqual(3, len(state.tests))
        self.assertEqual(6, len(state.questions))
        self.assertTrue(
            state.questions[0].test_id == 1
            and state.questions[0].text.localizations.get(Language.EN) == "T1Q1"
        )
        self.assertTrue(
            state.questions[1].test_id == 1
            and state.questions[1].text.localizations.get(Language.EN) == "T2Q1"
        )
        self.assertTrue(
            state.questions[2].test_id == 2
            and state.questions[2].text.localizations.get(Language.EN) == "T2Q1"
        )
        self.assertTrue(
            state.questions[3].test_id == 2
            and state.questions[3].text.localizations.get(Language.EN) == "T1Q1"
        )
        self.assertTrue(
            state.questions[4].test_id == 3
            and state.questions[4].text.localizations.get(Language.EN)
            in ["T1Q1", "T2Q1"]
        )
        self.assertTrue(
            state.questions[5].test_id == 3
            and state.questions[5].text.localizations.get(Language.EN)
            in ["T1Q1", "T2Q1"]
        )
        self.assertTrue(
            state.questions[4].text.localizations.get(Language.EN)
            != state.questions[5].text.localizations.get(Language.EN)
        )
