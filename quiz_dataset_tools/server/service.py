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


class DatabaseService:
    def __init__(self, data_dir="./"):
        self.dbase = PrebuildDBase(data_dir)
        self.images_dir = f"{data_dir}/images"

    def get_tests(self, req: GetTestsRequest) -> GetTestsResponse:
        return GetTestsResponse(error_code=0, payload=self.dbase.get_tests())

    def get_questions(self, req: GetQuestionsRequest) -> GetQuestionsResponse:
        return GetQuestionsResponse(
            error_code=0, payload=self.dbase.get_questions_by_test(req.test_id)
        )

    def update_text(self, req: UpdateTextRequest) -> UpdateTextResponse:
        print(f"Update text: {req.text}")
        self.dbase.update_text(req.text)
        return UpdateTextResponse(error_code=0, payload=None)

    def update_question_image(self, file: UploadFile):
        print(f"Update image: {file}")
        file_path = f"{self.images_dir}/{file.filename}"
        with open(file_path, "wb") as fd:
            fd.write(file.file.read())
