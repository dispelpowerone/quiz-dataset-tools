from quiz_dataset_tools.util.gpt import GPTService
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.cache import StringCache
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildQuestion,
    PrebuildTest,
)

gpt_model = "gpt-4"
gpt = GPTService(model=gpt_model)

wcCanonicalNoOrig = "CNO"


class TextCanonicalDoctor:

    def __init__(self):
        self.cache = StringCache(gpt_model, "doctor")
        self.cache.load()

    def save_cache(self):
        self.cache.save()

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        assert question.text.text_id
        assert question.text.localizations.ENId
        prompt = TextCanonicalDoctor._format_question_prompt(question)
        print("-----")
        print(prompt)
        response = self.cache.get_or_retrieve(
            prompt, lambda prompt: TextCanonicalDoctor._send_request(prompt)
        )
        warning = TextCanonicalDoctor._format_warning(
            question.text.text_id, question.text.localizations.ENId, response
        )
        return [warning] if warning else []

    @staticmethod
    def _send_request(prompt: str) -> str:
        return gpt.send_prompt(prompt)

    @staticmethod
    def _format_warning(
        text_id: int, text_localization_id: int, response: str
    ) -> PrebuildTextWarning | None:
        clean_respone = response.strip().upper().strip(".'")
        content = None
        if clean_respone != "OK":
            content = response.strip()
        return PrebuildTextWarning(
            text_id=text_id,
            text_localization_id=text_localization_id,
            code=wcCanonicalNoOrig,
            content=content,
        )

    @staticmethod
    def _format_question_prompt(question: PrebuildQuestion) -> str:
        assert question.text.text_id != None
        assert question.text.localizations.EN != None
        assert question.text.localizations.ENId != None
        answers = [
            f"{index + 1}. {answer.text.localizations.EN}"
            for index, answer in enumerate(question.answers)
        ]
        return f"""
Check the following G1 driving test question. Assume that {"there is an image attached." if question.image else "no image attached."}
```
{question.text.localizations.EN}
```
The following answers are provided:
```
{"\n".join(answers)}
```
If there are any typos, grammatical, or logical errors in the question, fix them and explain why. The answers are not relevant for this prompt.
Otherwise answer with one word: OK
        """


"""
test = TextCanonicalDoctor()


def test_fn(content: str):
    text = PrebuildText(
        text_id=123, localizations=TextLocalizations(EN=content, ENId=123122)
    )
    test.check_question(text)


#test_fn("What does this road sign mean?")
test_fn("A G2 driver age 190 or younger who has more than 6 months of driving experience can carry ____ unrelated passenger(s) age 19 or younger between midnight and 5:00 a.m.")
test.save_cache()
"""
