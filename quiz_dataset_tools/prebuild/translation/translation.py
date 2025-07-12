import copy
import csv
import os
import re
from typing import Callable
from quiz_dataset_tools.util.data import Test
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.types import PrebuildText
from quiz_dataset_tools.prebuild.translation.base import BaseTranslator
from quiz_dataset_tools.prebuild.translation.gpt import GPTTranslator


class Translator:
    def __init__(self, impl: BaseTranslator, languages: list[Language]):
        self.impl = impl
        self.canonical_lang = Language.EN
        self.languages = set(languages)

    def translate_test(self, test_text: PrebuildText) -> PrebuildText:
        def translate_fn(content: str, lang: Language) -> str:
            return content

        return self._translate_text(test_text, translate_fn)

    def translate_question(self, question_text: PrebuildText) -> PrebuildText:
        def translate_fn(content: str, lang: Language) -> str:
            return self.impl.translate_question(content, lang)

        return self._translate_text(question_text, translate_fn)

    def translate_answer(
        self, question_text: PrebuildText, answer_text: PrebuildText
    ) -> PrebuildText:
        question_content = self._get_canonical_content(question_text)

        def translate_fn(content: str, lang: Language) -> str:
            return self.impl.translate_answer(content, question_content, lang)

        return self._translate_text(answer_text, translate_fn)

    def save_cache(self):
        pass

    def load_cache(self):
        pass

    def _get_canonical_content(self, text: PrebuildText) -> str:
        canonical_local = text.localizations.get(self.canonical_lang)
        if canonical_local is None or not canonical_local.content:
            raise Exception(
                f"Expected text content for canonical lang {self.canonical_lang.name}, {text=}"
            )
        return canonical_local.content

    def _translate_text(
        self, text: PrebuildText, translate_fn: Callable[[str, Language], str]
    ) -> PrebuildText:
        canonical_local_content = self._get_canonical_content(text)
        if is_stable_text(canonical_local_content):
            return text
        translated_text = copy.copy(text)
        for lang in self.languages:
            if lang == self.canonical_lang:
                continue
            translated_local = translated_text.localizations.get(lang)
            if translated_local and translated_local.content:
                continue
            translated_local_content = translate_fn(canonical_local_content, lang)
            translated_local_id = (
                translated_local.text_localization_id if translated_local else None
            )
            translated_text.localizations.set(
                lang, translated_local_content, translated_local_id
            )
        return translated_text


# Check if word is worth to translate
StableChars = set(["$", ".", "%", "="])
StableRe = set([re.compile(r"\d+ km/h"), re.compile(r"\d+ mph")])


# For example:
#   0.08%
#   A
#   A, B, C, D
#   X=1; Y=2
#   60 km/h
def is_stable_text(content) -> bool:
    # Normalize
    content = content.strip()
    # Check regex
    for rule in StableRe:
        if rule.match(content):
            return True
    # Check alpha chars
    alpha_count = 0
    stable_count = 0
    for ch in content:
        if ch in StableChars or ch.isnumeric():
            stable_count += 1
        elif ch.isalpha():
            alpha_count += 1
    if alpha_count <= 1:
        return True
    if stable_count / (stable_count + alpha_count) > 0.8:
        return True
    # Recursively check parts
    parts = content.split(",")
    if len(parts) == 1:
        parts = content.split(";")
    if len(parts) > 1:
        all_stable = True
        for part in parts:
            all_stable = all_stable and is_stable_text(part)
        if all_stable:
            return True
    return False
