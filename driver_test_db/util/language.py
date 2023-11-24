from enum import Enum
from typing import Callable
from dataclasses import dataclass
from dataclasses_json import dataclass_json, Undefined, DataClassJsonMixin


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
    def from_id(language_id: int) -> "Language" | None:
        for lang in Language:
            if lang.value.language_id == language_id:
                return lang
        return None


StringTransformer = Callable[[str], str]


@dataclass_json
@dataclass
class TextLocalizations:
    EN: str | None = None
    FR: str | None = None
    ZH: str | None = None
    ES: str | None = None
    RU: str | None = None
    FA: str | None = None
    PA: str | None = None

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
