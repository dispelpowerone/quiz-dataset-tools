from pydantic.dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildQuestion


@dataclass
class GetQuestionsRequest:
    test_id: int


@dataclass
class GetQuestionsResponse:
    error_code: int
    payload: list[PrebuildQuestion]
