import unittest
from quiz_dataset_tools.prebuild.stages.compose import ComposeMode, _question_hash
from quiz_dataset_tools.prebuild.types import (
    PrebuildQuestion,
    PrebuildText,
)
from quiz_dataset_tools.util.language import TextLocalizations


class TestQuestionHash(unittest.TestCase):
    def test_hash_formula(self):
        text = PrebuildText(localizations=TextLocalizations())
        question = PrebuildQuestion(test_id=3, question_id=7, text=text, answers=[])
        self.assertEqual(_question_hash(question), 3 * 100 + 7)

    def test_different_questions_different_hashes(self):
        text = PrebuildText(localizations=TextLocalizations())
        q1 = PrebuildQuestion(test_id=1, question_id=1, text=text, answers=[])
        q2 = PrebuildQuestion(test_id=1, question_id=2, text=text, answers=[])
        self.assertNotEqual(_question_hash(q1), _question_hash(q2))
