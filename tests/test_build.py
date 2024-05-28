import unittest
import os
from random import randrange
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.builder import DatabaseBuilder
from quiz_dataset_tools.util.dbase import DriverTestDBase
from quiz_dataset_tools.prebuild.types import (
    PrebuildTest,
    PrebuildQuestion,
    PrebuildAnswer,
    PrebuildText,
)
from tests.common import make_prebuild_text


class TestDatabaseBuilder(unittest.TestCase):
    def setUp(self):
        dbase_file = f"/tmp/test.main.db.{randrange(1000)}"
        self.dbase = DriverTestDBase(dbase_file)
        self.dbase.open()
        self.builder = DatabaseBuilder("./")
        self.builder.set_database(self.dbase)
        os.remove(dbase_file)

    def test_build_end_to_end(self):
        self.builder.set_prebuild_tests(
            [
                PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
                PrebuildTest(test_id=2, title=make_prebuild_text("Test 2")),
            ]
        )
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=make_prebuild_text("T1Q1"),
                    image=None,
                    answers=[
                        PrebuildAnswer(
                            make_prebuild_text("T1Q1A1"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q1A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q1A3"), is_right_answer=True
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q1A4"), is_right_answer=False
                        ),
                    ],
                ),
                PrebuildQuestion(
                    test_id=1,
                    question_id=2,
                    text=make_prebuild_text("T1Q2"),
                    image=None,
                    answers=[
                        PrebuildAnswer(
                            make_prebuild_text("T1Q2A1"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q2A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q2A3"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T1Q2A4"), is_right_answer=True
                        ),
                    ],
                ),
                PrebuildQuestion(
                    test_id=2,
                    question_id=1,
                    text=make_prebuild_text("T2Q1"),
                    image=None,
                    answers=[
                        PrebuildAnswer(
                            make_prebuild_text("T2Q1A1"), is_right_answer=True
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T2Q1A2"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T2Q1A3"), is_right_answer=False
                        ),
                        PrebuildAnswer(
                            make_prebuild_text("T2Q1A4"), is_right_answer=False
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

    def test_positions(self):
        self.builder.set_prebuild_tests(
            [
                PrebuildTest(test_id=1, title=make_prebuild_text("Test 1"), position=2),
                PrebuildTest(test_id=2, title=make_prebuild_text("Test 2")),
            ]
        )
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=make_prebuild_text("T1Q1"),
                    image=None,
                    answers=[],
                ),
            ]
        )

        self.builder.set_languages([Language.EN])
        self.builder.build()

        self.assertEqual(2, self.dbase.get_test(1).position)
        self.assertEqual(None, self.dbase.get_test(2).position)

    def test_fallback_language(self):
        self.builder.set_prebuild_tests(
            [
                PrebuildTest(
                    test_id=1, title=make_prebuild_text("Test 1", fr="fr Test 1")
                ),
                PrebuildTest(
                    test_id=2, title=make_prebuild_text("Test 2", es="es Test 2")
                ),
            ]
        )
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=make_prebuild_text("T1Q1"),
                    image=None,
                    answers=[],
                ),
            ]
        )

        self.builder.set_languages([Language.EN, Language.FR, Language.ES])
        self.builder.set_fallback_language(Language.EN)
        self.builder.build()

        txt1_id = self.dbase.get_test(1).text_id
        self._assert_localization(txt1_id, Language.EN, "Test 1")
        self._assert_localization(txt1_id, Language.FR, "fr Test 1")
        self._assert_localization(txt1_id, Language.ES, "Test 1")

        txt2_id = self.dbase.get_test(2).text_id
        self._assert_localization(txt2_id, Language.EN, "Test 2")
        self._assert_localization(txt2_id, Language.FR, "Test 2")
        self._assert_localization(txt2_id, Language.ES, "es Test 2")

    def test_missed_fallback_language(self):
        self.builder.set_prebuild_tests(
            [
                PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
            ]
        )
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=make_prebuild_text("T1Q1"),
                    image=None,
                    answers=[],
                ),
            ]
        )

        self.builder.set_languages([Language.EN, Language.FR])
        self.builder.set_fallback_language(Language.FR)
        with self.assertRaises(Exception):
            self.builder.build()

    def _assert_text(self, text_id: int, en: str):
        text_localizations = self.dbase.get_text_localizations(text_id)
        self.assertEqual(1, len(text_localizations))
        self.assertEqual(en, text_localizations[0].content)

    def _assert_localization(self, text_id: int, language: Language, content: str):
        self.assertEqual(
            content,
            self.dbase.get_text_localization(
                text_id, language.value.language_id
            ).content,
        )
