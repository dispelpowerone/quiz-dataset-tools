from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.prebuild.extra.text_mimic import TextMimicService
from quiz_dataset_tools.server.models.texts import (
    SearchTestMimicTextsRequest,
    SearchTestMimicTextsResponse,
    SearchQuestionMimicTextRequest,
    SearchQuestionMimicTextResponse,
    SearchAnswerMimicTextRequest,
    SearchAnswerMimicTextResponse,
)


class MimicService:
    text_mimic_service = TextMimicService()

    def __init__(self, dbase: PrebuildDBase, data_dir_list: list[str] = []):
        self.dbase = dbase
        for data_dir in data_dir_list:
            self.text_mimic_service.load_source_data(data_dir)

    def search_test_texts(
        self, req: SearchTestMimicTextsRequest
    ) -> SearchTestMimicTextsResponse:
        questions = self.dbase.get_questions_by_test(req.test_id)
        return SearchTestMimicTextsResponse(
            error_code=0,
            payload=self.text_mimic_service.find_mimic_test_texts(questions),
        )

    def search_question_text(
        self, req: SearchQuestionMimicTextRequest
    ) -> SearchQuestionMimicTextResponse:
        question = self.dbase.get_question(req.question_id)
        assert question
        return SearchQuestionMimicTextResponse(
            error_code=0,
            payload=self.text_mimic_service.find_mimic_question_text(question),
        )

    def search_answer_text(
        self, req: SearchAnswerMimicTextRequest
    ) -> SearchAnswerMimicTextResponse:
        answer = self.dbase.get_answer(req.answer_id)
        assert answer
        return SearchAnswerMimicTextResponse(
            error_code=0,
            payload=self.text_mimic_service.find_mimic_answer_text(answer),
        )
