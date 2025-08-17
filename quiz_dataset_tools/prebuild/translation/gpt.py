from typing import override
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.util.gpt import GPTServiceWithCache
from quiz_dataset_tools.prebuild.translation.base import BaseTranslator


GPT_MODEL = "gpt-4o"

DOMAIN_TEST_TYPE = {
    "on": "G1 Driving Test Ontario",
}


class GPTTranslator(BaseTranslator):
    test_type: str
    gpt_service: GPTServiceWithCache

    def __init__(self, domain: str):
        self.test_type = DOMAIN_TEST_TYPE[domain]
        self.gpt_service = GPTServiceWithCache("translation", GPT_MODEL)

    @override
    def translate_question(self, question_content: str, dest_lang: Language) -> str:
        prompt = f"""
Translate the following {self.test_type} question into {dest_lang.value.name}, using a formal tone appropriate for a driving exam and targeting an average-level audience.
Maintain consistency with standard driving terminology.
Stay as literal as possible without interpreting the meaning.
Assume that there are multiple answers provided to chose from.
```
{question_content}
```
Then, review the translation as a native language speaker and revise any phrasing that may sound unnatural. Print only the final version without comments.
        """
        return self._call_gpt(prompt)

    def translate_question_comment(
        self, question_comment_content: str, dest_lang: Language
    ) -> str:
        prompt = f"""
Translate the following {self.test_type} question comment into {dest_lang.value.name}, using a formal tone appropriate for a driving exam and targeting an average-level audience.
Maintain consistency with standard driving terminology.
Stay as literal as possible without interpreting the meaning.
```
{question_comment_content}
```
Then, review the translation as a native language speaker and revise any phrasing that may sound unnatural. Print only the final version without comments.
        """
        return self._call_gpt(prompt)

    @override
    def translate_answer(
        self,
        answer_content: str,
        question_content: str,
        dest_lang: Language,
    ) -> str:
        prompt = f"""
Translate the following {self.test_type} question answer
```
{answer_content}
```
into {dest_lang.value.name}, using a formal tone appropriate for a driving exam and targeting an average-level audience.
Maintain consistency with standard driving terminology.
Stay as literal as possible without interpreting the meaning.
Assume that the question is
```
{question_content}
```
Don't include the question in the response.
Then, review the translation as a native language speaker and revise any phrasing that may sound unnatural. Print only the final version without comments.
        """
        return self._call_gpt(prompt)

    @override
    def save_cache(self):
        self.gpt_service.save_cache()

    @override
    def load_cache(self):
        self.gpt_service.load_cache()

    def _call_gpt(self, prompt: str):
        return self.gpt_service.send_prompt(prompt).strip("\n\t '`\"«»")
