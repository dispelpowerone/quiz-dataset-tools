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
        return self._check_text(question.text, self._format_prompt)

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        question_caonical = question.text.get_canonical()

        def format_prompt(
            canonical: TextLocalization,
            lang: Language,
            translation: TextLocalization,
        ):
            return self._format_answer_prompt(
                question_caonical, canonical, lang, translation
            )

        return self._check_text(answer.text, format_prompt)

    def check_question_comment(
        self, question: PrebuildQuestion
    ) -> list[PrebuildTextWarning]:
        if not question.comment_text:
            return []
        return self._check_text(question.comment_text, self._format_prompt)

    def _check_text(
        self, text: PrebuildText, format_prompt_fn
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
            prompt = format_prompt_fn(canonical, lang, translation)
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
        canonical: TextLocalization,
        lang: Language,
        translation: TextLocalization,
    ) -> str:
        return f"""
You are a professional translator and bilingual reviewer.
You work with {self.test_type} questions and answers.

Check if the following {lang.value.name} text:
```
{translation.content}
```
is a correct translation of the English text:
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

    def _format_answer_prompt(
        self,
        canonical_context: TextLocalization,
        canonical: TextLocalization,
        lang: Language,
        translation: TextLocalization,
    ) -> str:
        return f"""
You are a professional translator and bilingual reviewer.
You work with Florida Learner's Permit Test questions and answers.

Context (for background only, not for translation check) that can be a question or a begining of some
statement:
```
{canonical_context.content}
```

Check if the following {lang.value.name} text:
```
{translation.content}
```
is a correct translation of the English text:
```
{canonical.content}
```
Follow these rules when checking:
1. Meaning over form. The most important thing is that the translation accurately conveys the meaning
of the original.
2. Do not be overly strict. Ignore minor stylistic differences, choice of synonyms, or variations in p
hrasing if they do not distort the meaning.
3. Focus only on errors. Point out issues only if:
 - the translation conveys the wrong meaning,
 - important parts of the text are missing,
 - elements are added that are not present in the original,
 - terminology is significantly distorted.
4. Do not check whether the answer itself is factually correct or appropriate for the test. Your task is only to verify if the {lang.value.name} translation accurately matches the given English text.

If the translation is not correct, fix it and explain why.
Otherwise answer with one word: OK
        """
