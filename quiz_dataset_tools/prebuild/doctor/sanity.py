import re
from typing import Callable
from quiz_dataset_tools.util.language import Language, TextLocalization
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildQuestion,
    PrebuildAnswer,
)

WC_SANITY_FORBIDDEN_SYMBOL = "SFS"
WC_SANITY_BROKEN_NUMBERS = "SBN"

FORBIDDEN_SYMBOL_QUESTION_RE = re.compile("[\n\t`«»]")
FORBIDDEN_SYMBOL_ANSWER_RE = re.compile("[\n\t`«»\\?]")
NUMBER_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+\b")


class TextSanityDoctor:

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        warnings = []
        warnings.extend(
            self._check_forbidden_symbols(question.text, FORBIDDEN_SYMBOL_QUESTION_RE)
        )
        warnings.extend(self._check_broken_numbers(question.text))
        return warnings

    def check_answer(self, answer: PrebuildAnswer) -> list[PrebuildTextWarning]:
        warnings = []
        warnings.extend(
            self._check_forbidden_symbols(answer.text, FORBIDDEN_SYMBOL_ANSWER_RE)
        )
        warnings.extend(self._check_broken_numbers(answer.text))
        return warnings

    def _check_text(
        self,
        text: PrebuildText,
        check_fn: Callable[[TextLocalization], PrebuildTextWarning | None],
    ) -> list[PrebuildTextWarning]:
        warnings: list[PrebuildTextWarning] = []
        for lang in Language:
            translated_local = text.localizations.get(lang)
            if not translated_local:
                continue
            check_result = check_fn(translated_local)
            if check_result:
                warnings.append(check_result)
        return warnings

    def _check_forbidden_symbols(
        self, text: PrebuildText, regex
    ) -> list[PrebuildTextWarning]:
        def check_fn(local: TextLocalization):
            forbidden_entry = regex.search(local.content)
            if forbidden_entry:
                return PrebuildTextWarning(
                    text_id=text.text_id,
                    text_localization_id=local.text_localization_id,
                    code=WC_SANITY_FORBIDDEN_SYMBOL,
                    content=f"Forbidden symbol: {forbidden_entry.group()}",
                )
            return None

        return self._check_text(text, check_fn)

    def _check_broken_numbers(self, text: PrebuildText) -> list[PrebuildTextWarning]:
        canonical_local = text.localizations.get(Language.EN)
        assert canonical_local

        def extract_numbers(local: TextLocalization) -> list[int]:
            matches = NUMBER_RE.findall(local.content)
            cleaned = [int(m.replace(",", "")) for m in matches]
            return sorted(cleaned)

        canonical_numbers = extract_numbers(canonical_local)

        def check_fn(local: TextLocalization):
            # Skip canonical
            if local == canonical_local:
                return None
            local_numbers = extract_numbers(local)
            if local_numbers != canonical_numbers:
                return PrebuildTextWarning(
                    text_id=text.text_id,
                    text_localization_id=local.text_localization_id,
                    code=WC_SANITY_BROKEN_NUMBERS,
                    content=f"Numbers in EN: {canonical_numbers}, aren't the same as in the translation: {local_numbers}",
                )
            return None

        return self._check_text(text, check_fn)
