import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language, TextLocalizations
from driver_test_db.prebuild.stage import StageState
from driver_test_db.prebuild.stages.translate import TranslateStage
from driver_test_db.translation.translation import Translator
from driver_test_db.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)


class FakeTranslator(Translator):
    def __init__(self):
        self.data = {
            ("boo", Language.FR): "fr-boo",
            ("foo", Language.FR): "fr-foo",
            ("bar", Language.FR): "fr-bar",
        }

    def get_one(self, text: str, lang: Language) -> str:
        return self.data.get((text, lang), f"un-{text}")


class TestTranslateStage(unittest.TestCase):
    def setUp(self):
        pass

    def test_end_to_end(self):
        tests = [
            PrebuildTest(test_id=1, title=self._make_text("Test 1")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=self._make_text("foo"),
                answers=[
                    PrebuildAnswer(self._make_text("boo"), is_right_answer=False),
                    PrebuildAnswer(self._make_text("bar"), is_right_answer=False),
                    PrebuildAnswer(self._make_text("boo"), is_right_answer=True),
                    PrebuildAnswer(self._make_text("bar"), is_right_answer=False),
                ],
            ),
        ]
        stage = TranslateStage(
            translator=FakeTranslator(), languages=[Language.FR, Language.ES]
        )
        state = stage.process(StageState(tests=tests, questions=questions))
        # Check test title
        test = state.tests[0]
        self.assertEqual("Test 1", test.title.localizations.get(Language.EN))
        self.assertEqual("Test 1", test.title.localizations.get(Language.FR))
        self.assertEqual("Test 1", test.title.localizations.get(Language.ES))
        self.assertIsNone(test.title.localizations.get(Language.ZH))
        # Check question text
        question = state.questions[0]
        self.assertEqual("foo", question.text.localizations.get(Language.EN))
        self.assertEqual("fr-foo / foo", question.text.localizations.get(Language.FR))
        self.assertEqual("un-foo / foo", question.text.localizations.get(Language.ES))
        self.assertIsNone(question.text.localizations.get(Language.ZH))
        # Check answer
        answer = question.answers[1]
        self.assertEqual("bar", answer.text.localizations.get(Language.EN))
        self.assertEqual("fr-bar / bar", answer.text.localizations.get(Language.FR))
        self.assertEqual("un-bar / bar", answer.text.localizations.get(Language.ES))
        self.assertIsNone(answer.text.localizations.get(Language.ZH))

    def _make_text(self, en: str):
        return PrebuildText(localizations=TextLocalizations(EN=en), paraphrase=None)
