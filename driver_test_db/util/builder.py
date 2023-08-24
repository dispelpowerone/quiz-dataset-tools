from .dbase import DriverTestDBase
from .images import Images
from .translation import Translator
from .paraphrase import Paraphrase
from .loader import Loader
from .language import Language


class DBBuilder:
    def __init__(self):
        self.paraphrase = None
        self.images = None
        self.translator = None
        self.loader = None
        self.shuffle_answers = False

    def set_images(self, images: Images):
        self.images = images

    def set_translator(self, translator: Translator):
        self.translator = translator

    def set_paraphrase(self, paraphrase: Paraphrase):
        self.paraphrase = paraphrase

    def set_loader(self, loader: Loader):
        self.loader = loader

    def set_languages(self, languages: list):
        self.languages = languages

    def set_shuffle_answers(self, value: bool):
        self.shuffle_answers = value

    def build(self):
        dbase = DriverTestDBase()
        dbase.bootstrap()

        canonical_lang = self.loader.get_canonical_language()
        canonical_tests = None

        fix_missed_localizations(dbase, self.translator, self.languages, canonical_lang)

        tests_data = self.loader.get_tests()
        for language, tests in tests_data.items():
            if self.paraphrase:
                tests = self.paraphrase.paraphrase_tests(tests)
                self.paraphrase.save_cache()
            if language == canonical_lang:
                canonical_tests = tests
            pack_language_data(dbase, self.images, language.value.language_id, tests)

        for language in self.languages:
            if language in tests_data:
                continue
            tests = self.translator.translate_tests(language, canonical_tests)
            pack_language_data(dbase, self.images, language.value.language_id, tests)
            self.translator.save_cache()

        dbase.commit_and_close()


def pack_language_data(
    dbase: DriverTestDBase, images: Images, language_id: int, tests: list
):
    for test_index, test in enumerate(tests):
        test_id = test_index + 1
        test_dbo = dbase.add_test_if_not_exists(test_id)
        test_text_loc_id = dbase.add_text_localization(
            test_dbo.text_id, language_id, test.title
        )

        for question_index, question in enumerate(test.questions):
            question_dbo = dbase.add_question_if_not_exists(
                test_id, question_index + 1, question.image
            )
            question_text_loc_id = dbase.add_text_localization(
                question_dbo.text_id, language_id, question.text
            )

            for answer_index, answer in enumerate(question.answers):
                answer_dbo = dbase.add_answer_if_not_exists(
                    question_dbo.question_id, answer_index + 1, answer.is_right_answer
                )
                answer_text_loc_id = dbase.add_text_localization(
                    answer_dbo.text_id, language_id, answer.text
                )

            images.put(question.image)
            """
            if question.image and question.image != 'default.png':
                print(f"  '{question_dbo.question_id}': require('assets/img/questions/{question.image}'),")
            else:
                print(f"  '{question_dbo.question_id}': null,")
            """


def fix_missed_localizations(
    dbase: DriverTestDBase,
    translator: Translator,
    languages: list,
    canonical_lang: Language,
):
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
            content = translator.get(lang, canonical_localization.content)
            dbase.add_text_localization(text.text_id, lang.value.language_id, content)
