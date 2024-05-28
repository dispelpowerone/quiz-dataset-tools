from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildText,
)
from quiz_dataset_tools.prebuild.overrides import (
    make_question_context,
    make_answer_context,
)


class OverrideStage(DataUpdateBaseStage):
    def __init__(self, languages: list[Language], overrides: TextOverrides):
        self.languages = languages
        self.overrides = overrides
        self.matched_count = 0
        self.missed_count = 0

    def update_question(self, question: PrebuildQuestion) -> None:
        self._override_text(question.text, make_question_context(question))
        for answer in question.answers:
            self._override_text(answer.text, make_answer_context(question, answer))

    def _override_text(self, text: PrebuildText, context: str):
        try:
            assert text.original
            # We expect english version to be a canonical one
            orig_text = text.original.get(Language.EN)
            assert orig_text
            for lang in self.languages:
                override = self.overrides.get(
                    context=context,
                    lang=Language.EN,
                    text=orig_text,
                    override_lang=lang,
                )
                if override:
                    self.matched_count += 1
                    text.localizations.set(lang, override)
                else:
                    self.missed_count += 1
        except Exception as e:
            raise Exception(f"Failed to override text[{text}]: {e}")
