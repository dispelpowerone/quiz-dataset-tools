from driver_test_db.util.language import Language
from driver_test_db.util.dbase import (
    DriverTestDBase,
    TestDBO,
    TextDBO,
    QuestionDBO,
    AnswerDBO,
    TextLocalizationDBO,
)


class FakeDriverTestDBase(DriverTestDBase):
    def __init__(self):
        self.tests = {}
        self.questions = {}
        self.answers = {}
        self.texts = {}
        self.text_localizations = {}
        self.languages = {
            1: Language.EN,
        }

    def bootstrap(self):
        pass

    def open(self):
        pass

    def add_test_if_not_exists(self, test_id):
        if test_id not in self.tests:
            self.tests[test_id] = TestDBO(
                test_id=test_id, text_id=self.add_text(f"Test {test_id} title")
            )
        return self.tests[test_id]

    def add_question_if_not_exists(self, test_id, question_index, image):
        question_id = 100 * test_id + question_index
        if question_id not in self.questions:
            self.questions[question_id] = QuestionDBO(
                question_id=question_id,
                test_id=test_id,
                text_id=self.add_text(f"Question {question_id}"),
                image=None,
            )
        return self.questions[question_id]

    def add_answer_if_not_exists(self, question_id, answer_index, is_correct):
        answer_id = 100 * question_id + answer_index
        if answer_id not in self.answers:
            self.answers[answer_id] = AnswerDBO(
                answer_id=answer_id,
                question_id=question_id,
                text_id=self.add_text(f"Answer {answer_id}"),
                is_correct=is_correct,
            )
        return self.answers[answer_id]

    def add_text(self, description):
        text_id = len(self.texts) + 1
        self.texts[text_id] = TextDBO(text_id=text_id, description=description)
        return text_id

    def add_text_localization(self, text_id, language_id, content):
        text_localization_id = len(self.text_localizations) + 1
        self.text_localizations[text_localization_id] = TextLocalizationDBO(
            text_localization_id=text_localization_id,
            text_id=text_id,
            language_id=language_id,
            content=content,
        )
        return text_localization_id

    def get_tests(self):
        return list(self.tests.values())

    def get_test(self, test_id):
        return self.tests.get(test_id)

    def get_questions(self):
        return list(self.questions.values())

    def get_test_questions(self, test_id):
        return [q for q in self.questions.values() if q.test_id == test_id]

    def get_question(self, question_id):
        return self.questions.get(question_id)

    def get_answer(self, answer_id):
        return self.answers.get(answer_id)

    def get_question_answers(self, question_id):
        return [a for a in self.answers.values() if a.question_id == question_id]

    def get_text(self, text_id):
        return self.texts.get(text_id)

    def get_texts(self):
        return list(self.texts.values())

    def get_text_localizations(self, text_id):
        return [t for t in self.text_localizations.values() if t.text_id == text_id]

    def get_text_localization(self, text_id, language_id):
        for t in self.text_localizations.values():
            if t.text_id == text_id and t.language_id == language_id:
                return t
        return None

    def get_language(self, language_id):
        return self.languages.get(language_id)

    def commit_and_close(self):
        pass
