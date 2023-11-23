import deepl  # type: ignore
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from driver_test_db.config import config
from driver_test_db.util.language import Language


class DeepLTranslator:
    def __init__(self):
        self.translator = deepl.Translator(config["deepl"]["auth_key"])

    def get(self, dest_lang: Language, src_text: str):
        return _call_with_backoff(self.translator, dest_lang, src_text)


"""
@retry(
    retry=retry_if_exception_type((Exception)),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(10)
)
"""


def _call_with_backoff(translator, dest_lang: Language, src_text: str):
    print(f"HACK_DeepLTranslator_call: {dest_lang}")
    result = translator.translate_text(
        src_text, source_lang="EN", target_lang=dest_lang.name
    )
    print(f"HACK_DeepLTranslator_result: {src_text} -> {result.text}")
    return result.text
