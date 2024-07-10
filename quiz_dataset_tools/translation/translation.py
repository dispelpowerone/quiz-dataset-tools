import copy
import csv
import os
from typing import Any, Dict
from quiz_dataset_tools.util.data import Test
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.transformer import Transformer
from .mixed import MixedTranslator


class CachedTranslator(Transformer):
    def __init__(self, domain: str, dest_lang: Language, impl: Any):
        super().__init__(domain, f"translation.{dest_lang.name}")
        self.dest_lang = dest_lang
        self.impl = impl

    def _get(self, src_text: str):
        return self.impl.get(self.dest_lang, src_text)


class Translator:
    def __init__(self, domain: str):
        self.domain = domain
        self.impl = MixedTranslator()
        self.translators: Dict[Language, Any] = {}

    def get_one(self, text: str, lang: Language) -> str:
        translator = self.translators.get(lang)
        if not translator:
            translator = CachedTranslator(self.domain, lang, self.impl)
            self.translators[lang] = translator
        return translator.get(text)

    def get_all(self, text: str, langs: list[Language]):
        return {lang: self.get_one(text, lang) for lang in langs}

    def save_cache(self):
        for lang, translator in self.translators.items():
            translator.save_cache()

    def load_cache(self):
        for lang in Language:
            translator = CachedTranslator(self.domain, lang, self.impl)
            translator.load_cache()
            self.translators[lang] = translator


class PassThroughTranslator(Translator):
    def __init__(self):
        pass

    def get_one(self, text: str, lang: Language) -> str:
        return text

    def save_cache(self):
        pass

    def load_cache(self):
        pass


class TranslationTextTransformer:
    def __init__(
        self,
        translator: Translator,
        canonical_language: Language,
        languages: list[Language],
    ):
        self.canonical_language = canonical_language
        self.translator = translator
        self.languages = languages

    def __call__(self, text: TextLocalizations) -> TextLocalizations:
        canonical_text_content = text.get(self.canonical_language)
        if canonical_text_content is None:
            raise Exception(
                f"Expected text content for canonical lang {self.canonical_language.name}, text {text}"
            )
        translated_text = copy.copy(text)
        for lang in self.languages:
            if lang == self.canonical_language:
                continue
            translated_text_content = translated_text.get(lang)
            if translated_text_content:
                continue
            translated_text_content = self.translator.get_one(
                canonical_text_content, lang
            )
            # Commented because we don't want to mix localization and
            # canonical text.
            # if (
            #     translated_text_content != canonical_text_content
            #     and lang != Language.FA
            # ):
            #     translated_text_content = (
            #         f"{translated_text_content} / {canonical_text_content}"
            #     )
            translated_text.set(lang, translated_text_content)
        return translated_text
