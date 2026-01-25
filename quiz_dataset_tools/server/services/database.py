from fastapi import UploadFile
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.server.models.tests import GetTestsRequest, GetTestsResponse
from quiz_dataset_tools.server.models.questions import (
    GetQuestionsRequest,
    GetQuestionsResponse,
)
from quiz_dataset_tools.server.models.texts import (
    UpdateTextRequest,
    UpdateTextResponse,
)
from quiz_dataset_tools.server.models.text_warnings import (
    GetTextWarningsRequest,
    GetTextWarningsResponse,
)


class DatabaseService:
    domains_list = ["bc", "ca", "fl", "ny", "on", "tx"]

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.domain_dbase: dict[str, PrebuildDBase] = {}
        for domain in self.get_domains():
            self.domain_dbase[domain] = PrebuildDBase(
                self.get_data_dir(domain), backup=True
            )

    def get_domains(self):
        return self.domains_list

    def get_data_dir(self, domain: str):
        return f"{self.data_dir}/{domain}/prebuild"

    def get_dbase(self, domain: str):
        return self.domain_dbase[domain]

    def get_tests(self, req: GetTestsRequest) -> GetTestsResponse:
        return GetTestsResponse(
            error_code=0, payload=self.get_dbase(req.domain).get_tests()
        )

    def get_questions(self, req: GetQuestionsRequest) -> GetQuestionsResponse:
        return GetQuestionsResponse(
            error_code=0,
            payload=self.get_dbase(req.domain).get_questions_by_test(req.test_id),
        )

    def get_text_warnings(self, req: GetTextWarningsRequest) -> GetTextWarningsResponse:
        return GetTextWarningsResponse(
            error_code=0,
            payload=self.get_dbase(req.domain).get_text_warnings(req.text_id),
        )

    def update_text(self, req: UpdateTextRequest) -> UpdateTextResponse:
        self.get_dbase(req.domain).update_text(req.text)
        return UpdateTextResponse(error_code=0, payload=None)
