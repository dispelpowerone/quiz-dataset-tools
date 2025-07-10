import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import StageState
from quiz_dataset_tools.prebuild.stages.format import FormatStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from tests.common import make_prebuild_text


class TestFormatStage(unittest.TestCase):
    def setUp(self):
        pass

    def test_end_to_end(self):
        tests = [
            PrebuildTest(test_id=1, title=make_prebuild_text("Test 1", fr="fr-Test 1")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=make_prebuild_text("foo", fr="fr-foo"),
                answers=[
                    PrebuildAnswer(
                        make_prebuild_text("boo", fr="fr-boo"), is_right_answer=False
                    ),
                    PrebuildAnswer(
                        make_prebuild_text("bar", fr="bar"), is_right_answer=False
                    ),
                ],
            ),
        ]
        stage = FormatStage(languages=[Language.EN, Language.FR])
        state = stage.process(
            StageState(tests=tests, questions=questions, text_warnings=[])
        )
        # Check test title
        test = state.tests[0]
        self.assertEqual("Test 1", test.title.localizations.get(Language.EN).content)
        self.assertEqual("fr-Test 1", test.title.localizations.get(Language.FR).content)
        # Check question text
        question = state.questions[0]
        self.assertEqual("foo", question.text.localizations.get(Language.EN).content)
        self.assertEqual(
            "fr-foo / foo", question.text.localizations.get(Language.FR).content
        )
        # Check answer
        answers = question.answers
        self.assertEqual("boo", answers[0].text.localizations.get(Language.EN).content)
        self.assertEqual(
            "fr-boo / boo", answers[0].text.localizations.get(Language.FR).content
        )
        self.assertEqual("bar", answers[1].text.localizations.get(Language.EN).content)
        self.assertEqual("bar", answers[1].text.localizations.get(Language.FR).content)
