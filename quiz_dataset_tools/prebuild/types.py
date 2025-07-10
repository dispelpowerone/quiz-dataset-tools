from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from quiz_dataset_tools.paraphrase.types import ParaphrasedText
from quiz_dataset_tools.util.language import Language, TextLocalizations


@dataclass
class PrebuildTextWarning(DataClassJsonMixin):
    text_warning_id: int | None = None
    text_id: int | None = None
    text_localization_id: int | None = None
    code: str | None = None
    content: str | None = None
    is_manually_checked: bool = False
    last_update_timestamp: int | None = None


@dataclass
class PrebuildText(DataClassJsonMixin):
    localizations: TextLocalizations
    text_id: int | None = None
    original: TextLocalizations | None = None
    paraphrase: ParaphrasedText | None = None
    warnings: list[PrebuildTextWarning] = field(default_factory=lambda: [])
    is_manually_checked: bool = False
    last_update_timestamp: int | None = None


@dataclass
class PrebuildAnswer(DataClassJsonMixin):
    text: PrebuildText
    is_right_answer: bool
    answer_id: int | None = None
    question_id: int | None = None


@dataclass
class PrebuildQuestion(DataClassJsonMixin):
    test_id: int
    question_id: int
    text: PrebuildText
    answers: list[PrebuildAnswer]
    image: str | None = None
    audio: str | None = None


@dataclass
class PrebuildTest(DataClassJsonMixin):
    test_id: int
    title: PrebuildText
    position: int | None = None
