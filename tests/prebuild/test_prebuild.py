import unittest
from unittest.mock import patch

from quiz_dataset_tools.prebuild.prebuild import PrebuildBuilder
from quiz_dataset_tools.prebuild.types import PrebuildQuestion, PrebuildTest
from tests.common import make_text


class TestPrebuildBuilder(unittest.TestCase):
    @patch("quiz_dataset_tools.prebuild.prebuild.PrebuildDBase")
    def test_loads_only_the_selected_test_state(self, dbase_class) -> None:
        test_one = PrebuildTest(test_id=1, title=make_text("Test one"))
        test_two = PrebuildTest(test_id=2, title=make_text("Test two"))
        question_two = PrebuildQuestion(
            test_id=2,
            question_id=2,
            text=make_text("Question two"),
            answers=[],
        )
        dbase = dbase_class.return_value
        dbase.get_tests.return_value = [test_one, test_two]
        dbase.get_questions_by_test.return_value = [question_two]

        state = PrebuildBuilder()._load_stage_state_from_dbase(test_id=2)

        self.assertEqual(state.tests, [test_two])
        self.assertEqual(state.questions, [question_two])
        self.assertEqual(state.text_warnings, [])
        dbase.get_questions_by_test.assert_called_once_with(2)
        dbase.get_questions.assert_not_called()

    @patch("quiz_dataset_tools.prebuild.prebuild.PrebuildDBase")
    def test_loads_all_state_without_a_test_filter(self, dbase_class) -> None:
        test_one = PrebuildTest(test_id=1, title=make_text("Test one"))
        question_one = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text("Question one"),
            answers=[],
        )
        dbase = dbase_class.return_value
        dbase.get_tests.return_value = [test_one]
        dbase.get_questions.return_value = [question_one]

        state = PrebuildBuilder()._load_stage_state_from_dbase()

        self.assertEqual(state.tests, [test_one])
        self.assertEqual(state.questions, [question_one])
        dbase.get_questions.assert_called_once_with()
        dbase.get_questions_by_test.assert_not_called()

    @patch("quiz_dataset_tools.prebuild.prebuild.PrebuildDBase")
    def test_rejects_an_unknown_test_id(self, dbase_class) -> None:
        dbase_class.return_value.get_tests.return_value = []

        with self.assertRaisesRegex(ValueError, "No test found with test_id=99"):
            PrebuildBuilder()._load_stage_state_from_dbase(test_id=99)
