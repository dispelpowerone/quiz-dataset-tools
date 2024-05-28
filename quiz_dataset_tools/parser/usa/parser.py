from quiz_dataset_tools.util.data import Test
from quiz_dataset_tools.parser.parser import Parser
from .dbase import load_tests_by_state


class USADatabaseNYParser(Parser):
    def get_tests(self) -> list[Test]:
        return load_tests_by_state(33)


class USADatabaseTXParser(Parser):
    def get_tests(self) -> list[Test]:
        return load_tests_by_state(44)
