from quiz_dataset_tools.util.language import TextLocalizations
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
)


text_sequence_id = 1000


def make_prebuild_text(
    en: str,
    fr: str = None,
    es: str = None,
    ru: str = None,
    fa: str = None,
    pa: str = None,
    orig: str = None,
):
    global text_sequence_id
    text_sequence_id += 1
    return PrebuildText(
        text_id=text_sequence_id,
        localizations=TextLocalizations(EN=en, FR=fr, ES=es, RU=ru, FA=fa, PA=pa),
        paraphrase=None,
        original=None if orig is None else TextLocalizations(EN=orig),
    )
