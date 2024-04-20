import dataclasses
from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class ParaphrasedText(DataClassJsonMixin):
    orig: str
    candidate_1: str
    candidate_2: str
    final: str


@dataclasses.dataclass
class ParaphrasedAnswer(DataClassJsonMixin):
    text: ParaphrasedText
    is_correct: bool


@dataclasses.dataclass
class ParaphrasedQuestion(DataClassJsonMixin):
    id: int
    text: ParaphrasedText
    image: str
    answers: list[ParaphrasedAnswer]
