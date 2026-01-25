from quiz_dataset_tools.constants import (
    DOMAIN_TEST_TYPE,
    GPT_MODEL,
)
from quiz_dataset_tools.util.gpt import GPTServiceWithCache
from quiz_dataset_tools.prebuild.types import PrebuildQuestion, PrebuildText


prompt_pure_text_header = "Give a concise explanation why for the question"
prompt_image_text_header = (
    "Give a concise explanation why for the given image attached and for the question"
)


class QuestionCommentService:
    test_type: str
    images_dir: str
    gpt_service: GPTServiceWithCache

    def __init__(self, domain: str, images_dir: str):
        self.test_type = DOMAIN_TEST_TYPE[domain]
        self.images_dir = images_dir
        self.gpt_service = GPTServiceWithCache("question-comment", GPT_MODEL)

    def get_comment(self, question: PrebuildQuestion) -> str | None:
        prompt_header = prompt_pure_text_header
        prompt_image_path = None
        if question.image:
            prompt_header = prompt_image_text_header
            prompt_image_path = f"{self.images_dir}/{question.image}"
        question_content = self._get_text_content(question.text)
        answers_content = [
            f"{index + 1}. {self._get_text_content(answer.text)}"
            for index, answer in enumerate(question.answers)
        ]
        right_answer = self._find_right_answer(question)
        prompt = f"""
You are a {self.test_type} examiner. You work on a list of questions to assess knowledge of driving rules.
{prompt_header}
```
{question_content}
```
among the following answers
```
{"\n".join(answers_content)}
```
the right answer is
```
{answers_content[right_answer]}
```
Use a formal tone targeting an average-level audience.
Make your response as short as possible.
Do not include the answer in the response.
Give an advice on how to remember the right answer.
Start the advice with '💡' symbol.
        """
        return self._call_gpt(prompt, prompt_image_path)

    def save_cache(self):
        self.gpt_service.save_cache()

    def load_cache(self):
        self.gpt_service.load_cache()

    def _call_gpt(self, prompt: str, prompt_image_path: str | None):
        return self.gpt_service.send_prompt(prompt, prompt_image_path).strip(
            "\n\t '`\"«»"
        )

    def _get_text_content(self, text: PrebuildText) -> str:
        assert text.text_id != None
        assert text.localizations.EN != None
        assert text.localizations.EN.content
        assert text.localizations.EN.text_localization_id != None
        return text.localizations.EN.content

    def _find_right_answer(self, question: PrebuildQuestion) -> int:
        for index, answer in enumerate(question.answers):
            if answer.is_right_answer:
                return index
        raise Exception(f"No right answer found: {question}")
