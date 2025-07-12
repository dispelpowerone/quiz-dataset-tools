import unittest
from unittest.mock import MagicMock
from typing import override
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import StageState
from quiz_dataset_tools.prebuild.stages.translate import TranslateStage
from quiz_dataset_tools.prebuild.translation.translation import (
    BaseTranslator,
    Translator,
)
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from tests.common import make_prebuild_text


class FakeTranslator(BaseTranslator):
    def __init__(self):
        self.data = {
            ("boo", Language.FR): "fr-boo",
            ("foo", Language.FR): "fr-foo",
            ("bar", Language.FR): "fr-bar",
        }

    @override
    def translate_question(self, question_content: str, lang: Language) -> str:
        return self.data.get((question_content, lang), f"un-{question_content}")

    @override
    def translate_answer(
        self,
        answer_content: str,
        question_content: str,
        lang: Language,
    ) -> str:
        return self.data.get((answer_content, lang), f"un-{answer_content}")


class TestTranslateStage(unittest.TestCase):
    def setUp(self):
        pass

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
                    PrebuildAnswer(make_prebuild_text("boo"), is_right_answer=False),
                    PrebuildAnswer(make_prebuild_text("bar"), is_right_answer=False),
                    PrebuildAnswer(make_prebuild_text("boo"), is_right_answer=True),
                    PrebuildAnswer(make_prebuild_text("bar"), is_right_answer=False),
                ],
            ),
        ]
        translator = Translator(
            impl=FakeTranslator(), languages=[Language.FR, Language.ES]
        )
        stage = TranslateStage(translator=translator)
        state = stage.process(
            StageState(tests=tests, questions=questions, text_warnings=[])
        )
        # Check test title
        test = state.tests[0]
        self.assertEqual("Test 1", test.title.localizations.get(Language.EN).content)
        self.assertEqual("Test 1", test.title.localizations.get(Language.FR).content)
        self.assertEqual("Test 1", test.title.localizations.get(Language.ES).content)
        self.assertIsNone(test.title.localizations.get(Language.ZH))
        # Check question text
        question = state.questions[0]
        self.assertEqual("foo", question.text.localizations.get(Language.EN).content)
        self.assertEqual("fr-foo", question.text.localizations.get(Language.FR).content)
        self.assertEqual("un-foo", question.text.localizations.get(Language.ES).content)
        self.assertIsNone(question.text.localizations.get(Language.ZH))
        # Check answer
        answer = question.answers[1]
        self.assertEqual("bar", answer.text.localizations.get(Language.EN).content)
        self.assertEqual("fr-bar", answer.text.localizations.get(Language.FR).content)
        self.assertEqual("un-bar", answer.text.localizations.get(Language.ES).content)
        self.assertIsNone(answer.text.localizations.get(Language.ZH))
