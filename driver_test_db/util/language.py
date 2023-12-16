from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, LetterCase


@dataclass
class _Language:
    language_id: int
    name: str


class Language(Enum):
    EN = _Language(1, "English")
    FR = _Language(2, "French")
    ZH = _Language(3, "Chinese")
    ES = _Language(4, "Spanish")
    RU = _Language(5, "Russian")
    FA = _Language(6, "Farsi")
    PA = _Language(7, "Punjabi")

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

    def set(self, lang: Language, text: str) -> None:
        if not hasattr(self, lang.name):
            raise Exception(f"No field for {lang} in TextLocalizations")
        setattr(self, lang.name, text)

    def get(self, lang: Language) -> str | None:
        return getattr(self, lang.name)

    def transform(self, transformer: StringTransformer) -> "TextLocalizations":
        result = TextLocalizations()
        for lang in Language:
            string = self.get(lang)
            if string is not None:
                result.set(lang, transformer(string))
        return result
