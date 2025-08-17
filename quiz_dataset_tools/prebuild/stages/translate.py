from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.translation.translation import (
    Translator,
)


class TranslateStage(DataUpdateBaseStage):
    translator: Translator

    def __init__(self, translator: Translator):
        self.translator = translator

    def update_test(self, test: PrebuildTest) -> None:
        test.title = self.translator.translate_test(test.title)

    def update_question(self, question: PrebuildQuestion) -> None:
        question.text = self.translator.translate_question(question.text)
        if question.comment_text:
            question.comment_text = self.translator.translate_question_comment(
                question.comment_text
            )

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        answer.text = self.translator.translate_answer(question.text, answer.text)
