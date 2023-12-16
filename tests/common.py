from driver_test_db.util.language import TextLocalizations
from driver_test_db.prebuild.types import (
    PrebuildText,
)


def make_prebuild_text(
    en: str,
    fr: str = None,
    es: str = None,
    ru: str = None,
    fa: str = None,
    pa: str = None,
):
    return PrebuildText(
        localizations=TextLocalizations(EN=en, FR=fr, ES=es, RU=ru, FA=fa, PA=pa),
        paraphrase=None,
        original=None,
    )
