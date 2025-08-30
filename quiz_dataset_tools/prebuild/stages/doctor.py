import re
from quiz_dataset_tools.util.language import Language, TextLocalizations

# from quiz_dataset_tools.translation.translation import is_stable_text
from quiz_dataset_tools.prebuild.stage import (
    DataUpdateBaseStage,
    VerificationStage,
    StageState,
)
from quiz_dataset_tools.prebuild.doctor.canonical import TextCanonicalDoctor
from quiz_dataset_tools.prebuild.doctor.sanity import TextSanityDoctor
from quiz_dataset_tools.prebuild.doctor.translation import TextTranslationDoctor
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


ANSWERS_COUNT = 4
ANSWERS_AUTO_ADD = False


class DoctorStage(VerificationStage):
    def __init__(self, domain: str):
        self.canonical_doctor = TextCanonicalDoctor(domain)
        self.sanity_doctor = TextSanityDoctor()
        self.translation_doctor = TextTranslationDoctor(domain)

    def flush(self):
        self.canonical_doctor.save_cache()

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        result = []
        result.extend(self.canonical_doctor.check_question(question))
        result.extend(self.sanity_doctor.check_question(question))
        result.extend(self.translation_doctor.check_question(question))
        result.extend(self.translation_doctor.check_question_comment(question))
        return result

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        result = []
        result.extend(self.canonical_doctor.check_answer(question, answer))
        result.extend(self.sanity_doctor.check_answer(answer))
        result.extend(self.translation_doctor.check_answer(question, answer))
        return result


"""
class DoctorStage(DataUpdateBaseStage):
    def __init__(self):
        pass

    def update_test(self, test: PrebuildTest) -> None:
        pass

    def update_question(self, question: PrebuildQuestion) -> None:
        self._check_text(question.text, question)
        self._check_answers_count(question)

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        self._check_text(answer.text, question)

    def _check_text(self, text: PrebuildText, question: PrebuildQuestion) -> None:
        canonical_content = text.localizations.get(Language.EN)
        if not canonical_content:
            raise Exception(f"No canonical content found, {text=}")
        # Check for not uniq content
        original_content: str | None = ""
        if text.original:
            original_content = text.original.get(Language.EN)
            if not original_content:
                raise Exception(f"Malformed text: {text.original=}")
        # Check cannot
        if self._check_cannot(canonical_content):
            print(
                f"Cannot: test_id={question.test_id}, question_id={question.question_id}, text_id={text.text_id}, {canonical_content=}"
            )
        # Check that content is not the same as canonical one
        if (
            not is_stable_text(canonical_content)
            and canonical_content == original_content
        ):
            print(
                f"Non uniq content: question_id={question.question_id} text_id={text.text_id}, {canonical_content=}"
            )
        for lang in Language:
            if lang in [Language.EN]:
                continue
            content = text.localizations.get(lang)
            if content is None or content == "":
                continue
            # Check for mixed-lang content
            if is_stable_text(canonical_content):
                if content != canonical_content:
                    print(
                        f"Stable string changed: text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                    )
                    content = canonical_content
            elif content == canonical_content:
                print(
                    f"Equal content: text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                )
            if self._check_mixed_content(content):
                print(
                    f"Mixed content: text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                )
            # Check for canonical tail
            clean_content = self._strip_canonical(content, canonical_content)
            if clean_content is not None:
                print(
                    f"Strip canonical: text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                )
                content = clean_content
            elif len(content) / len(canonical_content) > 1.4 and content.count(
                "/"
            ) != canonical_content.count("/"):
                print(
                    f"Localization may be incorrect: text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                )
            if self._check_broken_numbers(content, canonical_content):
                print(
                    f"Broken number: test_id={question.test_id}, question_id={question.question_id}, text_id={text.text_id}, lang={lang.value.code}, {content=}, {canonical_content=}"
                )
            text.localizations.set(lang, content)

    def _check_mixed_content(self, content) -> bool:
        a_count = 0
        b_count = 0
        for ch in content:
            if ch.isnumeric() or ch in ["$", ".", "%", " "]:
                continue
            if ord(ch) <= 127:
                a_count += 1
            else:
                b_count += 1
        if a_count > b_count:
            a_count, b_count = b_count, a_count
        if a_count == 0:
            return False
        ab_count = a_count + b_count
        ab_ratio = a_count / b_count
        return ab_count > 3 and ab_ratio > 0.8

    def _strip_canonical(self, content, canonical_content) -> str | None:
        canonical_content_norm = canonical_content.rstrip(" .")
        content_norm = content.rstrip(" .")
        if content_norm != canonical_content_norm and content_norm.endswith(
            canonical_content_norm
        ):
            temp = content_norm.removesuffix(canonical_content_norm)
            temp = temp.rstrip(" ")
            if temp != "" and temp[-1] == "/":
                return temp.rstrip(" /")
        lower_content_norm = content_norm.lower()
        lower_canonical_norm = canonical_content_norm.lower()
        if lower_content_norm != lower_canonical_norm and lower_content_norm.endswith(
            lower_canonical_norm
        ):
            content_size = len(content_norm) - len(canonical_content_norm)
            temp = content_norm[0:content_size]
            temp = temp.rstrip(" ")
            if temp != "" and temp[-1] == "/":
                return temp.rstrip(" /")
        return None

    def _check_answers_count(self, question: PrebuildQuestion) -> None:
        if len(question.answers) == ANSWERS_COUNT:
            return
        print(
            f"There are invalid number of answers, {question.question_id=}, {len(question.answers)=}"
        )
        while ANSWERS_AUTO_ADD and len(question.answers) < ANSWERS_COUNT:
            print(f"Add empty answer to question={question.question_id}")
            question.answers.append(
                PrebuildAnswer(
                    text=PrebuildText(localizations=TextLocalizations()),
                    is_right_answer=False,
                )
            )

    def _check_broken_numbers(self, content: str, canonical_content: str) -> bool:
        def extract_numbers(text: str) -> list[int]:
            return [int(num) for num in re.findall("\\d+", text)]

        return extract_numbers(content) != extract_numbers(canonical_content)

    def _check_cannot(self, content: str) -> bool:
        return (
            content.find("can not ") != -1
            or content.find("Can not ") != -1
            or content.lower().find("licence") != -1
        )
"""
