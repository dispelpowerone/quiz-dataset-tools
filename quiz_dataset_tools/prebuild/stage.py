import copy
from dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


@dataclass
class StageState:
    tests: list[PrebuildTest]
    questions: list[PrebuildQuestion]


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
