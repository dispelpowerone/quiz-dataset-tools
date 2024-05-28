from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


class FormatStage(DataUpdateBaseStage):
    def __init__(self, languages: list[Language]):
        self.languages = languages

    def update_question(self, question: PrebuildQuestion) -> None:
        self._format_localizations(question.text.localizations)

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        self._format_localizations(answer.text.localizations)

    def _format_localizations(self, text: TextLocalizations):
        # We expect EN to be a canonical language
        canonical = text.get(Language.EN)
        for lang in self.languages:
            if lang == Language.EN or lang == Language.FA:
                continue
            localization = text.get(lang)
            if localization is None:
                raise Exception(f"Localization for {lang} is expected")
            if localization != canonical:
                text.set(lang, f"{localization} / {canonical}")
