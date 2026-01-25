from quiz_dataset_tools.prebuild.types import PrebuildQuestion
from quiz_dataset_tools.server.models.base import DomainRequest, DomainResponse


class GetQuestionsRequest(DomainRequest):
    test_id: int


class GetQuestionsResponse(DomainResponse):
    payload: list[PrebuildQuestion]
