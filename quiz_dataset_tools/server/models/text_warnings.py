from pydantic.dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildTextWarning


@dataclass
class GetTextWarningsRequest:
    text_id: int


@dataclass
class GetTextWarningsResponse:
    error_code: int
    payload: list[PrebuildTextWarning]
