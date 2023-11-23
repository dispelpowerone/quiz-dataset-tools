from dataclasses import dataclass
from dataclasses_json import dataclass_json, Undefined, DataClassJsonMixin
from driver_test_db.paraphrase.types import ParaphrasedText
from driver_test_db.util.language import Language, TextLocalizations


@dataclass
class PrebuildText(DataClassJsonMixin):
    localizations: TextLocalizations | None
    paraphrase: ParaphrasedText | None


@dataclass
class PrebuildAnswer(DataClassJsonMixin):
    text: PrebuildText
    is_right_answer: bool


@dataclass
class PrebuildQuestion(DataClassJsonMixin):
    test_id: int
    question_id: int
    text: PrebuildText
    answers: list[PrebuildAnswer]


@dataclass
class PrebuildTest(DataClassJsonMixin):
    test_id: int
    title: PrebuildText
