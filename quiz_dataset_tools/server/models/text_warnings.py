from quiz_dataset_tools.prebuild.types import PrebuildTextWarning
from quiz_dataset_tools.server.models.base import DomainRequest, DomainResponse


class GetTextWarningsRequest(DomainRequest):
    text_id: int


class GetTextWarningsResponse(DomainResponse):
    payload: list[PrebuildTextWarning]
