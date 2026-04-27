import unittest
from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
)
from quiz_dataset_tools.prebuild.overrides import make_question_context, make_answer_context


class TestMakeQuestionContext(unittest.TestCase):
    def test_returns_empty_string(self):
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=PrebuildText(localizations=TextLocalizations()),
            answers=[],
        )
        self.assertEqual(make_question_context(question), "")


class TestMakeAnswerContext(unittest.TestCase):
    def setUp(self):
        original = TextLocalizations()
        original.set(Language.EN, "What color is the sky?")
        self.question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=PrebuildText(
                localizations=TextLocalizations(),
                original=original,
            ),
            answers=[],
        )

    def test_right_answer(self):
        answer = PrebuildAnswer(
            text=PrebuildText(localizations=TextLocalizations()),
            is_right_answer=True,
        )
        result = make_answer_context(self.question, answer)
        self.assertIn("What color is the sky?", result)
        self.assertIn("is_right_answer: True", result)

    def test_wrong_answer(self):
        answer = PrebuildAnswer(
            text=PrebuildText(localizations=TextLocalizations()),
            is_right_answer=False,
        )
        result = make_answer_context(self.question, answer)
        self.assertIn("is_right_answer: False", result)


class TestPrebuildText(unittest.TestCase):
    def test_get_canonical(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello", 1)
        text = PrebuildText(localizations=locs)
        canonical = text.get_canonical()
        self.assertEqual(canonical.content, "hello")

    def test_get_canonical_asserts_on_none(self):
        text = PrebuildText(localizations=TextLocalizations())
        with self.assertRaises(AssertionError):
            text.get_canonical()

    def test_get_original_canonical(self):
        original = TextLocalizations()
        original.set(Language.EN, "original text")
        text = PrebuildText(localizations=TextLocalizations(), original=original)
        result = text.get_original_canonical()
        self.assertEqual(result.content, "original text")

    def test_get_original_canonical_asserts_on_no_original(self):
        text = PrebuildText(localizations=TextLocalizations())
        with self.assertRaises(AssertionError):
            text.get_original_canonical()
