from quiz_dataset_tools.util.language import Language


class BaseTranslator:
    def translate_question(self, question_content: str, lang: Language) -> str:
        return question_content

    def translate_answer(
        self,
        answer_content: str,
        question_content: str,
        lang: Language,
    ) -> str:
        return answer_content

    def save_cache(self):
        pass

    def load_cache(self):
        pass
