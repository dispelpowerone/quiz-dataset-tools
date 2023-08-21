from util.language import Language
from util.translator.deepl import DeepLTranslator
from util.translator.google import GoogleTranslator


class MixedTranslator:
    def __init__(self):
        self.deepl_translator = DeepLTranslator()
        self.google_translator = GoogleTranslator()

    def get(self, dest_lang: Language, src_text: str):
        if dest_lang in [Language.PA, Language.FA]:
            return self.google_translator.get(dest_lang, src_text)
        return self.deepl_translator.get(dest_lang, src_text)
