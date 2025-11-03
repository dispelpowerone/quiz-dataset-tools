from pydantic.dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildText, PrebuildQuestion


@dataclass
class UpdateTextRequest:
    text: PrebuildText


@dataclass
class UpdateTextResponse:
    error_code: int
    payload: None


@dataclass
class SearchTestMimicTextsRequest:
    test_id: int


@dataclass
class SearchTestMimicTextsResponse:
    error_code: int
    payload: dict[int, PrebuildText]


@dataclass
class SearchQuestionMimicTextRequest:
    question_id: int


@dataclass
class SearchQuestionMimicTextResponse:
    error_code: int
    payload: PrebuildText | None


@dataclass
class SearchAnswerMimicTextRequest:
    answer_id: int


@dataclass
class SearchAnswerMimicTextResponse:
    error_code: int
    payload: PrebuildText | None
