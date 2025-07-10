import re
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.prebuild.overrides import (
    make_question_context,
    make_answer_context,
)
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.translation.translation import (
    Translator,
    TranslationTextTransformer,
    PassThroughTranslator,
)


TEXT_ENDING = re.compile("[ ,.?!]*$", re.IGNORECASE)
TEXT_SEPARATOR = re.compile("[ /]*$", re.IGNORECASE)


class DumpOverridesStage(DataUpdateBaseStage):
    def __init__(self, languages: list[Language], overrides: TextOverrides):
        self.languages = languages
        self.overrides = overrides

    def update_question(self, question: PrebuildQuestion) -> None:
        self._dump_text(make_question_context(question), question.text)

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        if answer.text.original:
            self._dump_text(make_answer_context(question, answer), answer.text)

    def _dump_text(self, context: str, text: PrebuildText) -> None:
        try:
            assert text.original, f"{text=}"
            orig_local = text.original.get(Language.EN)
            assert orig_local
            for lang in self.languages:
                override_en = text.localizations.get(Language.EN)
                override = text.localizations.get(lang)
                assert override_en
                assert override
                # override_clean = self._cleanup_localization(override, override_en)
                # assert override_clean
                self.overrides.put(
                    lang=Language.EN,
                    text=orig_local.content,
                    context=context,
                    override_lang=lang,
                    override=override.content,
                )
        except Exception as e:
            raise Exception(f"Failed to dump {text=}: {e=}")

    def _cleanup_localization(self, text: str, suffix: str) -> str:
        if text == suffix or "/" not in text:
            return text
        # A naive assumption that
        # if there is only one slash then the left side
        # contains correct translation.
        if text.count("/") == 1:
            return text[0 : text.find("/")].strip()
        # Remove last unnecessary symbols
        # and make them uppercase
        suffix_norm = TEXT_ENDING.sub("", suffix).upper()
        text_norm = TEXT_ENDING.sub("", text).upper()
        if len(text_norm) < len(suffix_norm):
            raise Exception(f"String '{text}' must end with '{suffix}'")
        if text_norm == suffix_norm:
            return suffix
        if not text_norm.endswith(suffix_norm):
            raise Exception(f"String '{text}' must end with '{suffix}'")
        text_norm = text_norm.removesuffix(suffix_norm)
        text_norm = TEXT_SEPARATOR.sub("", text_norm)
        if not text_norm:
            raise Exception(f"String '{text}' is too short after normalization")
        return text[0 : len(text_norm)]
