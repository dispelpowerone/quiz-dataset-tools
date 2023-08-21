from util.loader import Loader
from util.language import Language
from usa.parser import load_ny_tests


class USALoader(Loader):
    def get_tests(self):
        return {
            Language.EN: load_ny_tests(),
        }
