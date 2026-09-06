import unittest
from unittest.mock import MagicMock, patch

from quiz_dataset_tools.prebuild.extra.question_comment import (
    NO_COMMENT,
    QuestionCommentService,
)
from quiz_dataset_tools.prebuild.stages.question_comment import (
    QuestionCommentStage,
)
from quiz_dataset_tools.prebuild.types import PrebuildQuestion, PrebuildText
from tests.common import make_text


class TestQuestionCommentStage(unittest.TestCase):
    def setUp(self) -> None:
        self.service = MagicMock(spec=QuestionCommentService)
        service_patcher = patch(
            "quiz_dataset_tools.prebuild.stages.question_comment.QuestionCommentService",
            return_value=self.service,
        )
        service_patcher.start()
        self.addCleanup(service_patcher.stop)

    def _stage(self, replace: bool = False) -> QuestionCommentStage:
        stage = QuestionCommentStage("ca", "/images", replace=replace)
        self.service.reset_mock()
        return stage

    @staticmethod
    def _question(comment_text: PrebuildText | None) -> PrebuildQuestion:
        return PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text("Question"),
            answers=[],
            comment_text=comment_text,
        )

    def test_skips_existing_canonical_comment_by_default(self) -> None:
        comment_text = make_text("Existing comment", fr="Commentaire existant")
        question = self._question(comment_text)

        self._stage().update_question(question)

        self.service.get_comment.assert_not_called()
        self.assertIs(question.comment_text, comment_text)

    def test_generates_for_blank_canonical_comment(self) -> None:
        question = self._question(make_text("", fr="Ancien commentaire"))
        self.service.get_comment.return_value = "Generated comment"

        self._stage().update_question(question)

        self.service.get_comment.assert_called_once_with(question)
        self.assertEqual(
            question.comment_text.localizations.EN.content, "Generated comment"
        )
        self.assertIsNone(question.comment_text.localizations.FR)

    def test_replace_regenerates_existing_canonical_comment(self) -> None:
        question = self._question(
            make_text("Existing comment", fr="Commentaire existant")
        )
        self.service.get_comment.return_value = "Replacement comment"

        self._stage(replace=True).update_question(question)

        self.service.get_comment.assert_called_once_with(question)
        self.assertEqual(
            question.comment_text.localizations.EN.content, "Replacement comment"
        )
        self.assertIsNone(question.comment_text.localizations.FR)

    def test_replace_clears_existing_comment_when_generation_returns_no_comment(
        self,
    ) -> None:
        comment_text = make_text("Existing comment", fr="Commentaire existant")
        question = self._question(comment_text)
        self.service.get_comment.return_value = NO_COMMENT

        self._stage(replace=True).update_question(question)

        self.service.get_comment.assert_called_once_with(question)
        self.assertEqual(question.comment_text.localizations.EN.content, "")
        self.assertIsNone(question.comment_text.localizations.FR)

    def test_keeps_existing_comment_when_generation_is_empty(self) -> None:
        comment_text = make_text("Existing comment", fr="Commentaire existant")
        question = self._question(comment_text)
        self.service.get_comment.return_value = ""

        self._stage(replace=True).update_question(question)

        self.service.get_comment.assert_called_once_with(question)
        self.assertIs(question.comment_text, comment_text)
