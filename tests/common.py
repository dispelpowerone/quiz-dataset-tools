from quiz_dataset_tools.util.language import TextLocalizations
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
)


def make_prebuild_text(
    en: str,
    fr: str = None,
    es: str = None,
    ru: str = None,
    fa: str = None,
    pa: str = None,
    orig: str = None,
):
    return PrebuildText(
        localizations=TextLocalizations(EN=en, FR=fr, ES=es, RU=ru, FA=fa, PA=pa),
        paraphrase=None,
        original=None if orig is None else TextLocalizations(EN=orig),
    )
