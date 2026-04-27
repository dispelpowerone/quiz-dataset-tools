import unittest
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.stage import StageState
from quiz_dataset_tools.prebuild.stages.format import FormatStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


def make_text(en: str, fr: str = None, es: str = None) -> PrebuildText:
    locs = TextLocalizations()
    locs.set(Language.EN, en)
    if fr:
        locs.set(Language.FR, fr)
    if es:
        locs.set(Language.ES, es)
    return PrebuildText(localizations=locs)


class TestFormatStage(unittest.TestCase):
    def test_appends_canonical_when_different(self):
        languages = [Language.EN, Language.FR]
        stage = FormatStage(languages=languages)
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text(en="Stop", fr="Arrêt"),
            answers=[],
        )
        state = StageState(tests=[], questions=[question], text_warnings=[])
        result = stage.process(state)
        fr_content = result.questions[0].text.localizations.get(Language.FR).content
        self.assertEqual(fr_content, "Arrêt / Stop")

    def test_no_change_when_same_as_canonical(self):
        languages = [Language.EN, Language.FR]
        stage = FormatStage(languages=languages)
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text(en="OK", fr="OK"),
            answers=[],
        )
        state = StageState(tests=[], questions=[question], text_warnings=[])
        result = stage.process(state)
        fr_content = result.questions[0].text.localizations.get(Language.FR).content
        self.assertEqual(fr_content, "OK")

    def test_farsi_excluded_from_format(self):
        languages = [Language.EN, Language.FA]
        stage = FormatStage(languages=languages)
        locs = TextLocalizations()
        locs.set(Language.EN, "Stop")
        locs.set(Language.FA, "ایست")
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=PrebuildText(localizations=locs),
            answers=[],
        )
        state = StageState(tests=[], questions=[question], text_warnings=[])
        result = stage.process(state)
        fa_content = result.questions[0].text.localizations.get(Language.FA).content
        self.assertEqual(fa_content, "ایست")

    def test_formats_answers_too(self):
        languages = [Language.EN, Language.ES]
        stage = FormatStage(languages=languages)
        answer = PrebuildAnswer(
            text=make_text(en="Yes", es="Sí"),
            is_right_answer=True,
        )
        question = PrebuildQuestion(
            test_id=1,
            question_id=1,
            text=make_text(en="Q?", es="P?"),
            answers=[answer],
        )
        state = StageState(tests=[], questions=[question], text_warnings=[])
        result = stage.process(state)
        es_answer = (
            result.questions[0].answers[0].text.localizations.get(Language.ES).content
        )
        self.assertEqual(es_answer, "Sí / Yes")
