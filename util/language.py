from enum import Enum
from dataclasses import dataclass


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
