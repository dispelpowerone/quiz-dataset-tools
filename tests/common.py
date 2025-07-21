from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
)


text_sequence_id = 1000
text_local_sequence_id = 1000


def make_text_localization(content: str | None) -> TextLocalization | None:
    if content is None:
        return None
    global text_local_sequence_id
    text_local_sequence_id += 1
    return TextLocalization(content, text_local_sequence_id)


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
        localizations=TextLocalizations(
            EN=make_text_localization(en),
            FR=make_text_localization(fr),
            ES=make_text_localization(es),
            RU=make_text_localization(ru),
            FA=make_text_localization(fa),
            PA=make_text_localization(pa),
        ),
        paraphrase=None,
        original=(
            None if orig is None else TextLocalizations(EN=TextLocalization(orig))
        ),
    )
