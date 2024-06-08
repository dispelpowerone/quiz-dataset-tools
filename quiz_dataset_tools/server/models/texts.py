from pydantic.dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildText


@dataclass
class UpdateTextRequest:
    text: PrebuildText


@dataclass
class UpdateTextResponse:
    error_code: int
    payload: None
