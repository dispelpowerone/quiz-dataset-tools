from driver_test_db.util.dbase import DriverTestDBase
from driver_test_db.util.images import Images
from driver_test_db.util.language import Language
from driver_test_db.prebuild.types import PrebuildTest, PrebuildQuestion, PrebuildText


class DatabaseBuilder:
    def __init__(self) -> None:
        self.output_dir: str = "out"
        self.images: Images | None = None
        self.languages: list[Language] = []
        self.tests: list[PrebuildTest] | None = None
        self.questions: list[PrebuildQuestion] | None = None

    def set_output_dir(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def set_images(self, images: Images) -> None:
        self.images = images

    def set_languages(self, languages: list[Language]) -> None:
        self.languages = languages

    def set_prebuild_tests(self, tests: list[PrebuildTest]) -> None:
        self.tests = tests

    def set_prebuild_questions(self, questions: list[PrebuildQuestion]) -> None:
        self.questions = questions

    def build(self) -> None:
        dbase = self._make_database_connection()
        dbase.bootstrap()

        self._pack_tests(dbase)
        self._pack_questions(dbase)

        dbase.commit_and_close()

    def _make_database_connection(self):
        return DriverTestDBase()

    def _pack_tests(self, dbase: DriverTestDBase) -> None:
        assert self.tests
        for test in self.tests:
            test_dbo = dbase.add_test_if_not_exists(test.test_id)
            self._pack_text(dbase, test_dbo.text_id, test.title)

    def _pack_text(
        self, dbase: DriverTestDBase, text_id: int, text: PrebuildText
    ) -> None:
        for lang in self.languages:
            text_content = text.localizations.get(lang)
            if text_content is None:
                raise Exception("Missed localization")
            dbase.add_text_localization(text_id, lang.value.language_id, text_content)

    def _pack_questions(self, dbase: DriverTestDBase) -> None:
        assert self.questions
        for question_index, question in enumerate(self.questions):
            question_dbo = dbase.add_question_if_not_exists(
                question.test_id, question.question_id, None
            )
            self._pack_text(dbase, question_dbo.text_id, question.text)

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
