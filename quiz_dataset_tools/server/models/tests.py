from pydantic.dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildTest


@dataclass
class GetTestsRequest:
    pass


@dataclass
class GetTestsResponse:
    error_code: int
    payload: list[PrebuildTest]
