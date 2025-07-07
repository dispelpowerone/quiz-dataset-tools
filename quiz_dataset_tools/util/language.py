from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase


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


class TextLocalization:
    langauge: Language
    content: str
    text_localization_id: int | None


@dataclass_json
@dataclass
class TextLocalizations:
    EN: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    FR: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    ZH: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    ES: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    RU: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    FA: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    PA: str | None = field(default=None, metadata=config(exclude=lambda x: x is None))  # type: ignore
    PT: str | None = None

    # DB ids
    ENId: int | None = None
    FRId: int | None = None
    ZHId: int | None = None
    ESId: int | None = None
    RUId: int | None = None
    FAId: int | None = None
    PAId: int | None = None
    PTId: int | None = None

    def set(
        self, lang: Language, text: str, localization_id: int | None = None
    ) -> None:
        if not hasattr(self, lang.name):
            raise Exception(f"No field for {lang} in TextLocalizations")
        setattr(self, lang.name, text)
        setattr(self, lang.name + "Id", localization_id)

    def get(self, lang: Language) -> str | None:
        return getattr(self, lang.name)

    def get_id(self, lang: Language) -> int | None:
        return getattr(self, lang.name + "Id")

    def transform(self, transformer: StringTransformer) -> "TextLocalizations":
        result = TextLocalizations()
        for lang in Language:
            string = self.get(lang)
            if string is not None:
                result.set(lang, transformer(string))
        return result
