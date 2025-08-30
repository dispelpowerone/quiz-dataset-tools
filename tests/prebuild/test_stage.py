import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import StageState, VerificationStage
from quiz_dataset_tools.prebuild.stages.compose import ComposeMode, ComposeStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildTextWarning,
)
from tests.common import make_prebuild_text


class TestVerificationStage(unittest.TestCase):

    tests = [
        PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
        PrebuildTest(test_id=2, title=make_prebuild_text("Test 2")),
        PrebuildTest(test_id=3, title=make_prebuild_text("Test 3")),
    ]
    questions = [
        PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_prebuild_text("T1Q1"),
            answers=[
                PrebuildAnswer(
                    answer_id=1, text=make_prebuild_text("T1Q1A1"), is_right_answer=True
                ),
                PrebuildAnswer(
                    answer_id=2,
                    text=make_prebuild_text("T1Q1A2"),
                    is_right_answer=False,
                ),
            ],
        ),
        PrebuildQuestion(
            test_id=2,
            question_id=1,
            text=make_prebuild_text("T2Q1"),
            answers=[
                PrebuildAnswer(
                    answer_id=1, text=make_prebuild_text("T2Q1A1"), is_right_answer=True
                ),
            ],
        ),
    ]

    def setUp(self):
        self.stage = VerificationStage()

    def test_process_returns_new_state(self):
        state = StageState(tests=self.tests, questions=self.questions, text_warnings=[])
        result = self.stage.process(state)

        # Should not mutate input
        self.assertTrue(result is not state)
        self.assertTrue(result.questions[0] is not state.questions[0])
        # Should have empty warnings since defaults return []
        self.assertEqual([], result.text_warnings)

    def test_check_methods_are_called(self):
        state = StageState(tests=self.tests, questions=self.questions, text_warnings=[])

        self.stage.check_answer = MagicMock(
            side_effect=lambda q, a: [
                PrebuildTextWarning(
                    content=f"t{q.test_id}_q{q.question_id}_a{a.answer_id}"
                )
            ]
        )
        self.stage.check_question = MagicMock(
            side_effect=lambda q: [
                PrebuildTextWarning(content=f"t{q.test_id}_q{q.question_id}")
            ]
        )

        result = self.stage.process(state)

        # 3 answers → 3 calls
        self.assertEqual(3, self.stage.check_answer.call_count)
        self.stage.check_answer.assert_any_call(
            self.questions[0], self.questions[0].answers[0]
        )
        self.stage.check_answer.assert_any_call(
            self.questions[0], self.questions[0].answers[1]
        )
        self.stage.check_answer.assert_any_call(
            self.questions[1], self.questions[1].answers[0]
        )

        # 2 questions → 2 calls
        self.assertEqual(2, self.stage.check_question.call_count)
        self.stage.check_question.assert_any_call(self.questions[0])
        self.stage.check_question.assert_any_call(self.questions[1])

        # Check warnings
        expected_warnings = [
            PrebuildTextWarning(content=f"t1_q1"),
            PrebuildTextWarning(content=f"t1_q1_a1"),
            PrebuildTextWarning(content=f"t1_q1_a2"),
            PrebuildTextWarning(content=f"t2_q1"),
            PrebuildTextWarning(content=f"t2_q1_a1"),
        ]
        self.assertEqual(
            expected_warnings, sorted(result.text_warnings, key=lambda w: w.content)
        )
