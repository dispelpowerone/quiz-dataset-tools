from quiz_dataset_tools.util.data import Test
from quiz_dataset_tools.util.language import Language


class Parser:
    def get_tests(self) -> list[Test]:
        return []

    def get_canonical_language(self) -> Language:
        return Language.EN
