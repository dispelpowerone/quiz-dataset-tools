from pydantic.dataclasses import dataclass
from ...util.dbase import TestDBO


@dataclass
class GetTestsRequest:
    pass


@dataclass
class GetTestsResponse:
    error_code: int
    payload: list[TestDBO]
