from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildQuestion,
)


text_sequence_id = 1000
text_local_sequence_id = 1000


def _make_text_localization(content: str | None) -> TextLocalization | None:
    if content is None:
        return None
    global text_local_sequence_id
    text_local_sequence_id += 1
    return TextLocalization(content, text_local_sequence_id)


def make_text(
    en: str,
    *,
    text_id: int = None,
    fr: str = None,
    es: str = None,
    ru: str = None,
    fa: str = None,
    pa: str = None,
    orig: str = None,
) -> PrebuildText:
    global text_sequence_id
    if text_id is None:
        text_sequence_id += 1
        text_id = text_sequence_id
    return PrebuildText(
        text_id=text_id,
        localizations=TextLocalizations(
            EN=_make_text_localization(en),
            FR=_make_text_localization(fr),
            ES=_make_text_localization(es),
            RU=_make_text_localization(ru),
            FA=_make_text_localization(fa),
            PA=_make_text_localization(pa),
        ),
        paraphrase=None,
        original=(
            None if orig is None else TextLocalizations(EN=TextLocalization(orig))
        ),
    )


def make_question(
    test_id: int,
    question_id: int,
    text_id: int,
    en: str,
    answers: list = None,
    image: str = None,
) -> PrebuildQuestion:
    comment = make_text("", text_id=text_id + 5000)
    return PrebuildQuestion(
        test_id=test_id,
        question_id=question_id,
        text=make_text(en, text_id=text_id),
        answers=answers or [],
        image=image,
        comment_text=comment,
    )
