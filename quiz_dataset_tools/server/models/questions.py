from dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import PrebuildQuestion, PrebuildQuestionImage
from quiz_dataset_tools.server.models.base import DomainRequest, DomainResponse


class GetQuestionsRequest(DomainRequest):
    test_id: int


class GetQuestionsResponse(DomainResponse):
    payload: list[PrebuildQuestion]


class SetQuestionsImageRequest(DomainRequest):
    question_id: int
    image: str | None


class SetQuestionsImageResponse(DomainResponse):
    payload: None


class UploadQuestionsImageResponse(DomainResponse):
    @dataclass
    class Status:
        image: str | None
        error_message: str | None

    payload: Status
