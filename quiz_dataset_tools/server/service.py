from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.server.models.tests import GetTestsRequest, GetTestsResponse


class DatabaseService:
    def __init__(self, data_dir="./"):
        self.dbase = PrebuildDBase(data_dir)

    def get_tests(self, req: GetTestsRequest) -> GetTestsResponse:
        return GetTestsResponse(error_code=0, payload=self.dbase.get_tests())
