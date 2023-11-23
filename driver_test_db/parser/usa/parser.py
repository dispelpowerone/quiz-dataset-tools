from driver_test_db.util.data import Test
from driver_test_db.parser.parser import Parser
from .dbase import load_ny_tests


class USADatabaseParser(Parser):
    def get_tests(self) -> list[Test]:
        return load_ny_tests()
