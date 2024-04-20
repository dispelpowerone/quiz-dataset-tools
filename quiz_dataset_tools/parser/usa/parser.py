from quiz_dataset_tools.util.data import Test
from quiz_dataset_tools.parser.parser import Parser
from .dbase import load_ny_tests


class USADatabaseParser(Parser):
    def get_tests(self) -> list[Test]:
        return load_ny_tests()
