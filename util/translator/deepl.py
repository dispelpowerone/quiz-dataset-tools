import deepl
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)
from util.language import Language

auth_key = "77fe6289-3e09-813a-abec-691c4ad32462:fx"


class DeepLTranslator:
    def __init__(self):
        self.translator = deepl.Translator(auth_key)

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
    print(f"HACK_call_with_backoff: {dest_lang}")
    result = translator.translate_text(
        src_text, source_lang="EN", target_lang=dest_lang.name
    )
    print(f"HACK_call_with_backoff: {src_text} -> {result.text}")
    return result.text
