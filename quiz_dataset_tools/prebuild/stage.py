import copy
from dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import (
    PrebuildTextWarning,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


@dataclass
class StageState:
    tests: list[PrebuildTest]
    questions: list[PrebuildQuestion]
    text_warnings: list[PrebuildTextWarning]


class BaseStage:
    def setup(self):
        pass

    def process(self, state: StageState) -> StageState:
        return state


class DataUpdateBaseStage(BaseStage):
    def process(self, state: StageState) -> StageState:
        result_state = copy.deepcopy(state)
        for test in result_state.tests:
            self.update_test(test)
        for question in result_state.questions:
            question_copy = copy.deepcopy(question)
            for answer in question.answers:
                self.update_answer(question_copy, answer)
            self.update_question(question)
        return result_state

    def update_test(self, test: PrebuildTest) -> None:
        pass

    def update_question(self, question: PrebuildQuestion) -> None:
        pass

    def update_answer(self, question: PrebuildQuestion, answer: PrebuildAnswer) -> None:
        pass


class VerificationStage(BaseStage):
    def process(self, state: StageState) -> StageState:
        result_state = copy.deepcopy(state)
        for question in result_state.questions:
            question_copy = copy.deepcopy(question)
            for answer in question.answers:
                result_state.text_warnings.extend(
                    self.check_answer(question_copy, answer)
                )
            result_state.text_warnings.extend(self.check_question(question))
        return result_state

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        return []

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        return []
