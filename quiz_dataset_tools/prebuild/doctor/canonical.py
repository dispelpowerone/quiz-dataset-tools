from quiz_dataset_tools.util.gpt import GPTServiceWithCache
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildQuestion,
    PrebuildAnswer,
)

GPT_MODEL = "gpt-4o"
WC_CANONICAL_NO_ORIG = "CNO"


class TextCanonicalDoctor:

    gpt: GPTServiceWithCache

    def __init__(self, gpt_service: GPTServiceWithCache | None = None):
        if gpt_service:
            self.gpt = gpt_service
        else:
            self.gpt = GPTServiceWithCache("doctor", model=GPT_MODEL)
            self.gpt.load_cache()

    def save_cache(self):
        self.gpt.save_cache()

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        prompt = self._format_question_prompt(question)
        return self._get_warnings(question.text, prompt)

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        prompt = self._format_answer_prompt(question, answer)
        return self._get_warnings(answer.text, prompt)

    def _get_warnings(
        self, text: PrebuildText, prompt: str
    ) -> list[PrebuildTextWarning]:
        assert text.text_id
        assert text.localizations
        assert text.localizations.EN
        assert text.localizations.EN.text_localization_id
        response = self.gpt.send_prompt(prompt)
        warning = self._format_warning(
            text.text_id,
            text.localizations.EN.text_localization_id,
            response,
        )
        return [warning] if warning else []

    def _format_warning(
        self, text_id: int, text_localization_id: int, response: str
    ) -> PrebuildTextWarning | None:
        clean_respone = response.strip().upper().strip("\n\t '`\"«»")
        if clean_respone == "OK":
            return None
        return PrebuildTextWarning(
            text_id=text_id,
            text_localization_id=text_localization_id,
            code=WC_CANONICAL_NO_ORIG,
            content=response.strip(),
        )

    def _format_question_prompt(self, question: PrebuildQuestion) -> str:
        question_content = self._get_text_content(question.text)
        answers_content = [
            f"{index + 1}. {self._get_text_content(answer.text)}"
            for index, answer in enumerate(question.answers)
        ]
        return f"""
Check the following G1 driving test question. Assume that {"there is an image attached." if question.image else "no image attached."}
```
{question_content}
```
The following answers are provided:
```
{"\n".join(answers_content)}
```
If there are any typos, grammatical, or logical errors in the question, fix them and explain why. The answers are not relevant for this prompt.
Otherwise answer with one word: OK
        """

    def _format_answer_prompt(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> str:
        question_content = self._get_text_content(question.text)
        answer_content = self._get_text_content(answer.text)
        return f"""
You are a G1 driving test examiner. You create a list of questions to assess knowledge of driving rules.
For the following G1 driving test question:
```
{question_content}
```
Assume that {"there is an image attached." if question.image else "no image attached."}
Check the following answer option that will be provided to a student as one of the choices:
```
{answer_content}
```
This answer is {"correct" if answer.is_right_answer else "incorrect"}, but you only need to check for typos, grammatical, or stylistic errors. Do not evaluate whether the answer is correct.
If the answer is good, respond with one word: OK
"""

    def _get_text_content(self, text: PrebuildText) -> str:
        assert text.text_id != None
        assert text.localizations.EN != None
        assert text.localizations.EN.content
        assert text.localizations.EN.text_localization_id != None
        return text.localizations.EN.content
