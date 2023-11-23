from google.cloud import translate
from driver_test_db.util.language import Language
from driver_test_db.config import config


class GoogleTranslator:
    def __init__(self):
        self.client = translate.TranslationServiceClient()

    def get(self, dest_lang: Language, src_text: str):
        return _call_with_backoff(self.client, dest_lang, src_text)


def _call_with_backoff(client, dest_lang: Language, src_text: str):
    print(f"HACK_GoogleTranslator_call: '{src_text}'")
    project_id = config["google_translate"]["project_id"]
    api_key = config["google_translate"]["api_key"]
    response = client.translate_text(
        request={
            "parent": f"projects/{project_id}/locations/global",
            "contents": [src_text],
            "mime_type": "text/plain",
            "source_language_code": "en-US",
            "target_language_code": dest_lang.name,
        }
    )
    if not response.translations or len(response.translations) != 1:
        raise Exception(f"Bad Google response {response}")
    print(
        f"HACK_GoogleTranslator_result: {src_text} -> {response.translations[0].translated_text}"
    )
    return response.translations[0].translated_text
