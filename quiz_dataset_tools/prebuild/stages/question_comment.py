from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildQuestion,
)
from quiz_dataset_tools.util.language import TextLocalization, TextLocalizations
from quiz_dataset_tools.prebuild.extra.question_comment import (
    QuestionCommentService,
)


class QuestionCommentStage(DataUpdateBaseStage):
    service: QuestionCommentService

    def __init__(self, domain: str):
        self.service = QuestionCommentService(domain)
        self.service.load_cache()

    def update_question(self, question: PrebuildQuestion) -> None:
        content = self.service.get_comment(question)
        if not content:
            return
        question.comment_text = PrebuildText(
            localizations=TextLocalizations(EN=TextLocalization(content))
        )

    def flush(self):
        self.service.save_cache()
