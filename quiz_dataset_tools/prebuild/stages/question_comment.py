from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildQuestion,
)
from quiz_dataset_tools.util.language import TextLocalization, TextLocalizations
from quiz_dataset_tools.prebuild.extra.question_comment import (
    NO_COMMENT,
    QuestionCommentService,
)


class QuestionCommentStage(DataUpdateBaseStage):
    service: QuestionCommentService
    replace: bool

    def __init__(self, domain: str, images_dir: str, replace: bool = False):
        self.service = QuestionCommentService(domain, images_dir)
        self.replace = replace
        self.service.load_cache()

    def update_question(self, question: PrebuildQuestion) -> None:
        if not self.replace and question.comment_text:
            canonical = question.comment_text.localizations.get_canonical()
            if canonical and canonical.content.strip():
                return
        content = self.service.get_comment(question)
        if content == NO_COMMENT:
            question.comment_text = PrebuildText(
                localizations=TextLocalizations(EN=TextLocalization(""))
            )
            return
        if not content:
            return
        question.comment_text = PrebuildText(
            localizations=TextLocalizations(EN=TextLocalization(content))
        )

    def flush(self):
        self.service.save_cache()
