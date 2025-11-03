import copy
from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.prebuild.types import (
    PrebuildQuestion,
    PrebuildAnswer,
    PrebuildText,
)


type QuestionKey = tuple[str, str | None]
type QuestionsIndex = dict[QuestionKey, PrebuildText]
type AnswerKey = tuple[str, bool]
type AnswersIndex = dict[AnswerKey, PrebuildText]


class TextMimicService:

    questions: list[PrebuildQuestion] = []
    question_text_origin_index: QuestionsIndex = {}
    question_text_local_index: QuestionsIndex = {}
    answer_origin_index: AnswersIndex = {}
    answer_local_index: AnswersIndex = {}

    def __init__(self):
        pass

    def load_source_data(self, data_dir: str) -> None:
        self.questions = PrebuildDBase(data_dir).get_questions()
        for question in self.questions:
            self._index_question(question)
            for answer in question.answers:
                self._index_answer(answer)
        """
        with open("/tmp/origin", "w") as fd:
            for key in sorted(self.answer_origin_index):
                fd.write(str(key) + "\n")
        with open("/tmp/local", "w") as fd:
            for key in sorted(self.answer_local_index):
                fd.write(str(key) + "\n")
        """

    def find_mimic_test_texts(
        self, questions: list[PrebuildQuestion]
    ) -> dict[int, PrebuildText]:
        test_mimics = {}
        for question in questions:
            mimic = self.find_mimic_question_text(question)
            if mimic:
                assert question.text.text_id
                test_mimics[question.text.text_id] = mimic
            for answer in question.answers:
                mimic = self.find_mimic_answer_text(answer)
                if mimic:
                    assert answer.text.text_id
                    test_mimics[answer.text.text_id] = mimic
        return test_mimics

    def find_mimic_question_text(
        self, question: PrebuildQuestion
    ) -> PrebuildText | None:
        def _find(content, image):
            original = self.question_text_origin_index.get((content, image))
            if original:
                return original
            return self.question_text_local_index.get((content, image))

        original_content = question.text.get_original_canonical().content
        text = _find(original_content, question.image)
        if text:
            return text
        text = _find(original_content, None)
        if text:
            return text
        local_content = question.text.get_canonical().content
        text = _find(local_content, question.image)
        if text:
            return text
        return _find(local_content, None)

    def find_mimic_answer_text(self, answer: PrebuildAnswer) -> PrebuildText | None:
        def _find(content, is_right):
            original = self.answer_origin_index.get((content, is_right))
            if original:
                return original
            return self.answer_local_index.get((content, is_right))

        original_content = self._normalize_content(
            answer.text.get_original_canonical().content
        )
        local_content = self._normalize_content(answer.text.get_canonical().content)
        # By original content we can search
        # only across records for right answers
        # because we don't change the meaning for
        # these texts
        text = _find(original_content, True)
        if text:
            return text
        text = _find(local_content, True)
        if text:
            return text
        # By local content we can search
        # across incorrect answers but only
        # in local index.
        return self.answer_local_index.get((local_content, False))

    def _index_question(self, question: PrebuildQuestion) -> None:
        # Index origin text
        original_content = question.text.get_original_canonical().content
        self._index_question_text(
            self.question_text_origin_index,
            (original_content, question.image),
            question.text,
        )
        self._index_question_text(
            self.question_text_origin_index, (original_content, None), question.text
        )
        # Index local text
        local_content = question.text.get_canonical().content
        self._index_question_text(
            self.question_text_origin_index,
            (local_content, question.image),
            question.text,
        )
        self._index_question_text(
            self.question_text_origin_index, (local_content, None), question.text
        )

    def _index_answer(self, answer: PrebuildAnswer) -> None:
        # Index origin text
        original_content = self._normalize_content(
            answer.text.get_original_canonical().content
        )
        self._index_answer_text(
            self.answer_origin_index,
            (original_content, answer.is_right_answer),
            answer.text,
        )
        self._index_answer_text(
            self.answer_origin_index, (original_content, False), answer.text
        )
        # Index local text
        local_content = self._normalize_content(answer.text.get_canonical().content)
        self._index_answer_text(
            self.answer_local_index,
            (local_content, answer.is_right_answer),
            answer.text,
        )
        self._index_answer_text(
            self.answer_local_index, (local_content, False), answer.text
        )

    @staticmethod
    def _index_question_text(
        index: QuestionsIndex, key: QuestionKey, text: PrebuildText
    ) -> None:
        value = index.get(key)
        if (
            value
            and value.last_update_timestamp
            and (
                not text.last_update_timestamp
                or value.last_update_timestamp > text.last_update_timestamp
            )
        ):
            return
        index[key] = text

    @staticmethod
    def _index_answer_text(
        index: AnswersIndex, key: AnswerKey, text: PrebuildText
    ) -> None:
        value = index.get(key)
        if (
            value
            and value.last_update_timestamp
            and (
                not text.last_update_timestamp
                or value.last_update_timestamp > text.last_update_timestamp
            )
        ):
            return
        index[key] = text

    @staticmethod
    def _clone_text_localizations(source: TextLocalizations) -> TextLocalizations:
        result = TextLocalizations()
        for lang in Language:
            local = source.get(lang)
            if local is not None:
                result.set(lang, local.content)
        return result

    @staticmethod
    def _normalize_content(content: str) -> str:
        content = content.lower()
        content = content.strip(" .")
        return content
