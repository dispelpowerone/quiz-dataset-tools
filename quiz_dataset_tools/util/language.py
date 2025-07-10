from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass, field


@dataclass
class _Language:
    language_id: int
    name: str
    code: str


class Language(Enum):
    EN = _Language(1, "English", "EN")
    FR = _Language(2, "French", "FR")
    ZH = _Language(3, "Chinese", "ZH")
    ES = _Language(4, "Spanish", "ES")
    RU = _Language(5, "Russian", "RU")
    FA = _Language(6, "Farsi", "FA")
    PA = _Language(7, "Punjabi", "PA")
    PT = _Language(9, "Portuguese", "PT-BR")

    @staticmethod
    def from_id(language_id: int) -> Optional["Language"]:
        for lang in Language:
            if lang.value.language_id == language_id:
                return lang
        return None

    @staticmethod
    def from_name(language_name: str) -> Optional["Language"]:
        for lang in Language:
            if lang.name == language_name:
                return lang
        return None


StringTransformer = Callable[[str], str]


@dataclass
class TextLocalization:
    content: str
    text_localization_id: int | None = None


@dataclass
class TextLocalizations:
    EN: TextLocalization | None = None
    FR: TextLocalization | None = None
    ZH: TextLocalization | None = None
    ES: TextLocalization | None = None
    RU: TextLocalization | None = None
    FA: TextLocalization | None = None
    PA: TextLocalization | None = None
    PT: TextLocalization | None = None

    def set(
        self, lang: Language, text: str, localization_id: int | None = None
    ) -> None:
        if not hasattr(self, lang.name):
            raise Exception(f"No field for {lang} in TextLocalizations")
        setattr(self, lang.name, TextLocalization(text, localization_id))

    def get(self, lang: Language) -> TextLocalization | None:
        return getattr(self, lang.name)

    def transform(self, transformer: StringTransformer) -> "TextLocalizations":
        result = TextLocalizations()
        for lang in Language:
            localization = self.get(lang)
            if localization is not None:
                result.set(
                    lang,
                    transformer(localization.content),
                    localization.text_localization_id,
                )
        return result
