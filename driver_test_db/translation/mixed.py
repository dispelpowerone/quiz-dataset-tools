from driver_test_db.util.language import Language
from .deepl import DeepLTranslator
from .google import GoogleTranslator


class MixedTranslator:
    def __init__(self):
        self.deepl_translator = DeepLTranslator()
        self.google_translator = GoogleTranslator()

    def get(self, dest_lang: Language, src_text: str):
        if dest_lang in [Language.PA, Language.FA]:
            return self.google_translator.get(dest_lang, src_text)
        return self.deepl_translator.get(dest_lang, src_text)
