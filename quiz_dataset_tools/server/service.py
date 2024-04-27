from ..util.dbase import DriverTestDBase
from .models.tests import GetTestsRequest, GetTestsResponse


class DatabaseService:
    db: DriverTestDBase

    def __init__(self, dbase_path="DriveTest.db"):
        self.db = DriverTestDBase(dbase_path)
        self.db.open()

    def get_tests(self, req: GetTestsRequest) -> GetTestsResponse:
        return GetTestsResponse(error_code=0, payload=self.db.get_tests())
