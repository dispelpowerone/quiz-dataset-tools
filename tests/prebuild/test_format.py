import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language, TextLocalizations
from driver_test_db.prebuild.stage import StageState
from driver_test_db.prebuild.stages.format import FormatStage
from driver_test_db.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)


class TestFormatStage(unittest.TestCase):
    def setUp(self):
        pass

    def test_end_to_end(self):
        tests = [
            PrebuildTest(test_id=1, title=self._make_text("Test 1", "fr-Test 1")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=self._make_text("foo", "fr-foo"),
                answers=[
                    PrebuildAnswer(
                        self._make_text("boo", "fr-boo"), is_right_answer=False
                    ),
                    PrebuildAnswer(
                        self._make_text("bar", "bar"), is_right_answer=False
                    ),
                ],
            ),
        ]
        stage = FormatStage(languages=[Language.EN, Language.FR])
        state = stage.process(StageState(tests=tests, questions=questions))
        # Check test title
        test = state.tests[0]
        self.assertEqual("Test 1", test.title.localizations.get(Language.EN))
        self.assertEqual("fr-Test 1", test.title.localizations.get(Language.FR))
        # Check question text
        question = state.questions[0]
        self.assertEqual("foo", question.text.localizations.get(Language.EN))
        self.assertEqual("fr-foo / foo", question.text.localizations.get(Language.FR))
        # Check answer
        answers = question.answers
        self.assertEqual("boo", answers[0].text.localizations.get(Language.EN))
        self.assertEqual("fr-boo / boo", answers[0].text.localizations.get(Language.FR))
        self.assertEqual("bar", answers[1].text.localizations.get(Language.EN))
        self.assertEqual("bar", answers[1].text.localizations.get(Language.FR))

    def _make_text(self, en: str, fr: str):
        return PrebuildText(
            localizations=TextLocalizations(EN=en, FR=fr), paraphrase=None
        )
