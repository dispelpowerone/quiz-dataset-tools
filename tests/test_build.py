import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language
from driver_test_db.util.builder import DatabaseBuilder
from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.prebuild.types import (
    PrebuildTest,
    PrebuildQuestion,
    PrebuildAnswer,
    PrebuildText,
)


class TestDatabaseBuilder(unittest.TestCase):
    def setUp(self):
        self.dbase = DriverTestDBase("/tmp/test_main.db")
        self.dbase.open()
        self.builder = DatabaseBuilder()
        self.builder.set_database(self.dbase)

    def test_build_end_to_end(self):
        self.builder.set_prebuild_tests(
            [
                PrebuildTest(test_id=1, title=self._make_text("Test 1")),
                PrebuildTest(test_id=2, title=self._make_text("Test 2")),
            ]
        )
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=self._make_text("T1Q1"),
                    image=None,
                    answers=[
                        PrebuildAnswer(
                            self._make_text("T1Q1A1"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            self._make_text("T1Q1A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(self._make_text("T1Q1A3"), is_right_answer=True),
                        PrebuildAnswer(
                            self._make_text("T1Q1A4"), is_right_answer=False
                        ),
                    ],
                ),
                PrebuildQuestion(
                    test_id=1,
                    question_id=2,
                    text=self._make_text("T1Q2"),
                    image=None,
                    answers=[
                        PrebuildAnswer(
                            self._make_text("T1Q2A1"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            self._make_text("T1Q2A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            self._make_text("T1Q2A3"), is_right_answer=False
                        ),
                        PrebuildAnswer(self._make_text("T1Q2A4"), is_right_answer=True),
                    ],
                ),
                PrebuildQuestion(
                    test_id=2,
                    question_id=1,
                    text=self._make_text("T2Q1"),
                    image=None,
                    answers=[
                        PrebuildAnswer(self._make_text("T2Q1A1"), is_right_answer=True),
                        PrebuildAnswer(
                            self._make_text("T2Q1A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            self._make_text("T2Q1A3"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            self._make_text("T2Q1A4"), is_right_answer=False
                        ),
                    ],
                ),
            ]
        )

        self.builder.set_languages([Language.EN])
        self.builder.build()

        self.assertEqual(2, len(self.dbase.get_tests()))
        self.assertEqual(3, len(self.dbase.get_questions()))
        # Test 1
        test1_questions = self.dbase.get_test_questions(1)
        self.assertEqual(2, len(test1_questions))
        # Test 1 Question 1
        test1_question1 = test1_questions[0]
        self.assertEqual(1, test1_question1.test_id)
        test1_question1_text = self.dbase.get_text(test1_question1.text_id)
        self.assertEqual("Question 101 content", test1_question1_text.description)
        self._assert_text(test1_question1.text_id, "T1Q1")
        test1_question1_answers = self.dbase.get_question_answers(
            test1_question1.question_id
        )
        self.assertEqual(4, len(test1_question1_answers))
        self.assertFalse(test1_question1_answers[0].is_correct)
        self.assertFalse(test1_question1_answers[1].is_correct)
        self.assertTrue(test1_question1_answers[2].is_correct)
        self.assertFalse(test1_question1_answers[3].is_correct)
        self._assert_text(test1_question1_answers[1].text_id, "T1Q1A2")
        # Test 2
        test2_questions = self.dbase.get_test_questions(2)
        self.assertEqual(1, len(test2_questions))

    def _make_text(self, en: str, fr: str = None):
        return PrebuildText(
            localizations={Language.EN: en, Language.FR: fr}, paraphrase=None
        )

    def _assert_text(self, text_id: int, en: str):
        text_localizations = self.dbase.get_text_localizations(text_id)
        self.assertEqual(1, len(text_localizations))
        self.assertEqual(en, text_localizations[0].content)
