from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.translation.translation import (
    Translator,
    TranslationTextTransformer,
    PassThroughTranslator,
)


class TranslateStage(DataUpdateBaseStage):
    def __init__(self, translator: Translator, languages: list[Language]):
        self.translation_transformer = TranslationTextTransformer(
            translator=translator,
            canonical_language=Language.EN,
            languages=languages,
        )
        self.pass_through_transformer = TranslationTextTransformer(
            translator=PassThroughTranslator(),
            canonical_language=Language.EN,
            languages=languages,
        )

    def update_test(self, test: PrebuildTest) -> None:
        test.title.localizations = self.pass_through_transformer(
            test.title.localizations
        )

    def update_question(self, question: PrebuildQuestion) -> None:
        question.text.localizations = self.translation_transformer(
            question.text.localizations
        )

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        answer.text.localizations = self.translation_transformer(
            answer.text.localizations
        )
