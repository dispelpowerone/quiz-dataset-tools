from quiz_dataset_tools.constants import (
    DOMAIN_TEST_TYPE,
    GPT_MODEL,
)
from quiz_dataset_tools.util.gpt import GPTServiceWithCache
from quiz_dataset_tools.util.language import Language, TextLocalization
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildQuestion,
    PrebuildAnswer,
)
from .common import is_ok_response

WC_TRANSLATION = "TRN"


class TextTranslationDoctor:

    test_type: str
    gpt: GPTServiceWithCache

    def __init__(self, domain: str, gpt_service: GPTServiceWithCache | None = None):
        self.test_type = DOMAIN_TEST_TYPE[domain]
        if gpt_service:
            self.gpt = gpt_service
        else:
            self.gpt = GPTServiceWithCache("doctor-translation", model=GPT_MODEL)
            self.gpt.load_cache()

    def save_cache(self):
        self.gpt.save_cache()

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        return self._check_text("question", "", question.text)

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        question_caonical = question.text.get_canonical()
        context = f"""For question
```
{question_caonical}
```
        """
        return self._check_text("answer to the question", context, answer.text)

    def check_question_comment(
        self, question: PrebuildQuestion
    ) -> list[PrebuildTextWarning]:
        if not question.comment_text:
            return []
        return self._check_text("text", "", question.comment_text)

    def _check_text(
        self, text_type: str, context: str, text: PrebuildText
    ) -> list[PrebuildTextWarning]:
        warnings: list[PrebuildTextWarning] = []
        canonical = text.localizations.get_canonical()
        assert canonical
        for lang in Language:
            translation = text.localizations.get(lang)
            if (
                translation is None
                or not translation.content
                or translation.content == canonical.content
            ):
                continue
            prompt = self._format_prompt(
                text_type, context, canonical, lang, translation
            )
            warning = self._get_warning(text, translation, prompt)
            if warning:
                warnings.append(warning)
        return warnings

    def _get_warning(
        self, text: PrebuildText, translation: TextLocalization, prompt: str
    ) -> PrebuildTextWarning | None:
        response = self.gpt.send_prompt(prompt)
        assert text.text_id
        assert translation.text_localization_id
        return self._format_warning(
            text.text_id,
            translation.text_localization_id,
            response,
        )

    def _format_warning(
        self, text_id: int, text_localization_id: int, response: str
    ) -> PrebuildTextWarning | None:
        if is_ok_response(response):
            return None
        return PrebuildTextWarning(
            text_id=text_id,
            text_localization_id=text_localization_id,
            code=WC_TRANSLATION,
            content=response.strip(),
        )

    def _format_prompt(
        self,
        text_type: str,
        context: str,
        canonical: TextLocalization,
        lang: Language,
        translation: TextLocalization,
    ) -> str:
        return f"""
You are a professional translator and bilingual reviewer.
You work with {self.test_type} questions and answers.
{context}
Check if text
```
{translation.content}
```
is the correct {lang.value.name} translation of {text_type}:
```
{canonical.content}
```
Follow these rules when checking:
1. Meaning over form. The most important thing is that the translation accurately conveys the meaning of the original.
2. Do not be overly strict. Ignore minor stylistic differences, choice of synonyms, or variations in phrasing if they do not distort the meaning.
3. Focus only on errors. Point out issues only if:
 - the translation conveys the wrong meaning,
 - important parts of the text are missing,
 - elements are added that are not present in the original,
 - terminology is significantly distorted.

If the translation is not correct, fix it and explain why.
Otherwise answer with one word: OK
        """
