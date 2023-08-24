from driver_test_db.util.loader import Loader
from driver_test_db.util.language import Language
from .parser import load_ny_tests


class USALoader(Loader):
    def get_tests(self):
        return {
            Language.EN: load_ny_tests(),
        }
