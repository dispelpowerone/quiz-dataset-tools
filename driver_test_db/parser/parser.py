from driver_test_db.util.data import Test
from driver_test_db.util.language import Language


class Parser:
    def get_tests(self) -> list[Test]:
        return []

    def get_canonical_language(self) -> Language:
        return Language.EN
