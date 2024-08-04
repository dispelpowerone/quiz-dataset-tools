from quiz_dataset_tools.util.language import TextLocalizations
from quiz_dataset_tools.prebuild.stage import DataUpdateBaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


ANSWERS_COUNT = 4


class DoctorStage(DataUpdateBaseStage):
    def __init__(self):
        pass

    def update_test(self, test: PrebuildTest) -> None:
        pass

    def update_question(self, question: PrebuildQuestion) -> None:
        while len(question.answers) < ANSWERS_COUNT:
            print(f"Add empty answer to question={question.question_id}")
            question.answers.append(
                PrebuildAnswer(
                    text=PrebuildText(localizations=TextLocalizations()),
                    is_right_answer=False,
                )
            )

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        pass
