import unittest
import tempfile
import shutil
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from tests.common import make_text, make_question


class TestPrebuildDBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.dbase = PrebuildDBase(self.tmpdir)
        self.dbase.bootstrap()

    def tearDown(self):
        self.dbase.close()
        shutil.rmtree(self.tmpdir)

    def test_add_and_get_test(self):
        test = PrebuildTest(test_id=1, title=make_text("Test 1", text_id=100), position=1)
        self.dbase.add_test(test)
        tests = self.dbase.get_tests()
        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0].test_id, 1)
        self.assertEqual(tests[0].title.localizations.get(Language.EN).content, "Test 1")
        self.assertEqual(tests[0].position, 1)

    def test_add_and_get_question(self):
        test = PrebuildTest(test_id=1, title=make_text("Test 1", text_id=100))
        self.dbase.add_test(test)

        answer = PrebuildAnswer(
            answer_id=10,
            question_id=1,
            text=make_text("Answer 1", text_id=200),
            is_right_answer=True,
        )
        question = make_question(
            test_id=1,
            question_id=1,
            text_id=300,
            en="Question 1",
            answers=[answer],
            image="img.png",
        )
        self.dbase.add_question(question)

        result = self.dbase.get_question(1)
        self.assertIsNotNone(result)
        self.assertEqual(result.question_id, 1)
        self.assertEqual(result.test_id, 1)
        self.assertEqual(
            result.text.localizations.get(Language.EN).content, "Question 1"
        )
        self.assertEqual(result.image, "img.png")
        self.assertEqual(len(result.answers), 1)
        self.assertTrue(result.answers[0].is_right_answer)

    def test_get_question_not_found(self):
        result = self.dbase.get_question(999)
        self.assertIsNone(result)

    def test_get_questions(self):
        test = PrebuildTest(test_id=1, title=make_text("Test 1", text_id=100))
        self.dbase.add_test(test)

        for i in range(1, 4):
            self.dbase.add_question(
                make_question(test_id=1, question_id=i, text_id=300 + i, en=f"Q{i}")
            )

        questions = self.dbase.get_questions()
        self.assertEqual(len(questions), 3)

    def test_get_questions_by_test(self):
        test1 = PrebuildTest(test_id=1, title=make_text("Test 1", text_id=100))
        test2 = PrebuildTest(test_id=2, title=make_text("Test 2", text_id=101))
        self.dbase.add_test(test1)
        self.dbase.add_test(test2)

        self.dbase.add_question(
            make_question(test_id=1, question_id=1, text_id=200, en="Q1")
        )
        self.dbase.add_question(
            make_question(test_id=2, question_id=2, text_id=201, en="Q2")
        )
        self.dbase.add_question(
            make_question(test_id=1, question_id=3, text_id=202, en="Q3")
        )

        test1_questions = self.dbase.get_questions_by_test(1)
        self.assertEqual(len(test1_questions), 2)
        test2_questions = self.dbase.get_questions_by_test(2)
        self.assertEqual(len(test2_questions), 1)

    def test_update_test(self):
        test = PrebuildTest(test_id=1, title=make_text("Original", text_id=100), position=1)
        self.dbase.add_test(test)

        updated = PrebuildTest(
            test_id=1, title=make_text("Updated", text_id=100), position=2
        )
        self.dbase.update_test(updated)

        tests = self.dbase.get_tests()
        self.assertEqual(tests[0].position, 2)

    def test_update_question(self):
        test = PrebuildTest(test_id=1, title=make_text("Test", text_id=100))
        self.dbase.add_test(test)

        question = make_question(
            test_id=1,
            question_id=1,
            text_id=200,
            en="Original",
            answers=[
                PrebuildAnswer(
                    answer_id=10,
                    question_id=1,
                    text=make_text("A1", text_id=300),
                    is_right_answer=False,
                )
            ],
        )
        self.dbase.add_question(question)

        updated = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text("Updated", text_id=200),
            answers=[
                PrebuildAnswer(
                    answer_id=10,
                    question_id=1,
                    text=make_text("A1 Updated", text_id=300),
                    is_right_answer=True,
                )
            ],
            image="new.png",
            comment_text=question.comment_text,
        )
        self.dbase.update_question(updated)

        result = self.dbase.get_question(1)
        self.assertEqual(result.image, "new.png")
        self.assertTrue(result.answers[0].is_right_answer)

    def test_text_warnings_crud(self):
        test = PrebuildTest(test_id=1, title=make_text("Test", text_id=100))
        self.dbase.add_test(test)

        question = make_question(
            test_id=1, question_id=1, text_id=200, en="Q1"
        )
        self.dbase.add_question(question)

        stored = self.dbase.get_question(1)
        text_id = stored.text.text_id
        loc_id = stored.text.localizations.get(Language.EN).text_localization_id

        warning = PrebuildTextWarning(
            text_id=text_id,
            text_localization_id=loc_id,
            code="SPELLING",
            content="Typo found",
            is_manually_checked=False,
        )
        self.dbase.add_text_warning(warning)

        warnings = self.dbase.get_text_warnings(text_id)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].code, "SPELLING")
        self.assertEqual(warnings[0].content, "Typo found")

    def test_get_question_image(self):
        test = PrebuildTest(test_id=1, title=make_text("Test", text_id=100))
        self.dbase.add_test(test)

        self.dbase.add_question(
            make_question(
                test_id=1, question_id=1, text_id=200, en="Q1", image="sign.png"
            )
        )
        self.dbase.add_question(
            make_question(
                test_id=1, question_id=2, text_id=201, en="Q2", image="sign.png"
            )
        )

        result = self.dbase.get_question_image("sign.png")
        self.assertEqual(result.image, "sign.png")
        self.assertEqual(len(result.questions), 2)

    def test_multilingual_roundtrip(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "Hello")
        locs.set(Language.FR, "Bonjour")
        locs.set(Language.ES, "Hola")
        text = PrebuildText(text_id=100, localizations=locs)

        test = PrebuildTest(test_id=1, title=text)
        self.dbase.add_test(test)

        tests = self.dbase.get_tests()
        title_locs = tests[0].title.localizations
        self.assertEqual(title_locs.get(Language.EN).content, "Hello")
        self.assertEqual(title_locs.get(Language.FR).content, "Bonjour")
        self.assertEqual(title_locs.get(Language.ES).content, "Hola")
