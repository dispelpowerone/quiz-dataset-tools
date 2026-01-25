from quiz_dataset_tools.prebuild.types import PrebuildTest
from quiz_dataset_tools.server.models.base import DomainRequest, DomainResponse


class GetTestsRequest(DomainRequest):
    pass


class GetTestsResponse(DomainResponse):
    payload: list[PrebuildTest]
