from quiz_dataset_tools.prebuild.types import PrebuildText, PrebuildQuestion
from quiz_dataset_tools.server.models.base import DomainRequest, DomainResponse


class UpdateTextRequest(DomainRequest):
    text: PrebuildText


class UpdateTextResponse(DomainResponse):
    payload: None


class SearchTestMimicTextsRequest(DomainRequest):
    test_id: int


class SearchTestMimicTextsResponse(DomainResponse):
    payload: dict[int, PrebuildText]


class SearchQuestionMimicTextRequest(DomainRequest):
    question_id: int


class SearchQuestionMimicTextResponse(DomainResponse):
    payload: PrebuildText | None


class SearchAnswerMimicTextRequest(DomainRequest):
    answer_id: int


class SearchAnswerMimicTextResponse(DomainResponse):
    payload: PrebuildText | None
