from util.loader import Loader
from util.language import Language
from icbc.parser import load_tests


class ICBCLoader(Loader):
    def get_tests(self):
        return {
            Language.EN: load_tests("eng"),
            # Language.ZH: load_tests("ch"),
            # Language.PA: load_tests("pn"),
        }
