from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


class OverrideStage(DataUpdateBaseStage):
    def __init__(self, overrides: TextOverrides):
        self.overrides = overrides

    def update_question(self, question: PrebuildQuestion) -> None:
        answer_context = question.text.localizations.get(Language.EN)
        assert answer_context
        for answer in question.answers:
            self._override_text(answer.text.localizations, answer_context)
        self._override_text(question.text.localizations, "")

    def _override_text(self, text: TextLocalizations, context: str):
        # Override only english localization for now
        # We expect it to be a canonical one
        text_content = text.get(Language.EN)
        assert text_content is not None
        text_override = self.overrides.get(
            lang=Language.EN,
            text=text_content,
            context=context,
            override_lang=Language.EN,
        )
        if text_override:
            text.set(Language.EN, text_override)
