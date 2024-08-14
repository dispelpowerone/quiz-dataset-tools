from quiz_dataset_tools.util.dbase import DriverTestDBase
from quiz_dataset_tools.util.media import MediaIndex, MediaType
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.types import (
    PrebuildTest,
    PrebuildQuestion,
    PrebuildText,
)


class DatabaseBuilder:
    def __init__(self, data_path: str, output_dir: str) -> None:
        self.output_dir = output_dir
        self.images = MediaIndex(
            MediaType.IMAGE,
            f"{data_path}/images",
            f"{output_dir}/images",
            preserve_file_names=False,
        )
        self.audio = MediaIndex(
            MediaType.AUDIO,
            f"{data_path}/audio",
            f"{output_dir}/audio",
            preserve_file_names=True,
        )
        self.dbase: DriverTestDBase | None = None
        self.languages: list[Language] = []
        self.fallback_language: Language | None = None
        self.tests: list[PrebuildTest] | None = None
        self.questions: list[PrebuildQuestion] | None = None

    def set_database(self, dbase: DriverTestDBase) -> None:
        self.dbase = dbase

    def set_languages(self, languages: list[Language]) -> None:
        self.languages = languages

    def set_fallback_language(self, language: Language) -> None:
        self.fallback_language = language

    def set_prebuild_tests(self, tests: list[PrebuildTest]) -> None:
        self.tests = tests

    def set_prebuild_questions(self, questions: list[PrebuildQuestion]) -> None:
        self.questions = questions

    def build(self) -> None:
        assert self.dbase
        self.dbase.bootstrap()
        self.images.clean()
        self.audio.clean()

        self._pack_tests(self.dbase)
        self._pack_questions(self.dbase)

        self.dbase.commit()
        self.images.save_index()
        self.audio.save_index()

    def _pack_tests(self, dbase: DriverTestDBase) -> None:
        assert self.tests
        for test in self.tests:
            assert test.position
            test_dbo = dbase.add_test_if_not_exists(test.test_id, test.position)
            # self._pack_text(dbase, test_dbo.text_id, test.title)
            for lang in self.languages:
                dbase.add_text_localization(
                    test_dbo.text_id, lang.value.language_id, f"Test {test.position}"
                )

    def _pack_text(
        self, dbase: DriverTestDBase, text_id: int, text: PrebuildText
    ) -> None:
        canonical_lang = Language.EN
        canonical_content = text.localizations.get(canonical_lang)
        for lang in self.languages:
            text_content = text.localizations.get(lang)
            if text_content is None:
                if self.fallback_language:
                    text_content = text.localizations.get(self.fallback_language)
                    if text_content is None:
                        raise Exception("Missed fallback localization")
                else:
                    raise Exception(f"Missed localization, {text=}, {lang=}")
            if text_content != canonical_content and lang != Language.FA:
                text_content = f"{text_content} / {canonical_content}"
            dbase.add_text_localization(text_id, lang.value.language_id, text_content)

    def _pack_questions(self, dbase: DriverTestDBase) -> None:
        assert self.questions
        for question_index, question in enumerate(self.questions):
            question_dbo = dbase.add_question_if_not_exists(
                question.test_id, question.question_id, None
            )
            self._pack_text(dbase, question_dbo.text_id, question.text)
            self.images.put(str(question_dbo.question_id), question.image)
            self.audio.put(str(question_dbo.question_id), question.audio)

            for answer_index, answer in enumerate(question.answers):
                answer_dbo = dbase.add_answer_if_not_exists(
                    question_dbo.question_id, answer_index + 1, answer.is_right_answer
                )
                self._pack_text(dbase, answer_dbo.text_id, answer.text)


"""
def fix_missed_localizations(
    dbase: DriverTestDBase,
    translator: Translator,
    languages: list[Language],
    canonical_lang: Language,
) -> None:
    expected_localizations_map = dict(
        [(lang.value.language_id, lang) for lang in languages]
    )
    expected_localizations_set = set(expected_localizations_map.keys())

    for text in dbase.get_texts():
        localizations = dbase.get_text_localizations(text.text_id)
        localizations_set = set()
        for localization in localizations:
            localizations_set.add(localization.language_id)
        canonical_localization = dbase.get_text_localization(
            text.text_id, canonical_lang.value.language_id
        )
        if not canonical_localization:
            raise Exception(f"Missed canonical localization: {text}")
        missed_localizations = expected_localizations_set.difference(localizations_set)
        for localization_id in missed_localizations:
            lang = expected_localizations_map[localization_id]
            content = translator.get_one(canonical_localization.content, lang)
            dbase.add_text_localization(text.text_id, lang.value.language_id, content)
"""
