import copy
import tqdm
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from quiz_dataset_tools.prebuild.types import (
    PrebuildTextWarning,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


WORKERS_COUNT = 10


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
        for test in tqdm.tqdm(result_state.tests):
            self.update_test(test)
        for question in tqdm.tqdm(result_state.questions):
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
        with ThreadPoolExecutor(max_workers=WORKERS_COUNT) as executor:
            for result in tqdm.tqdm(
                executor.map(self._process_question, result_state.questions),
                total=len(result_state.questions),
            ):
                result_state.text_warnings.extend(result)
        return result_state

    def check_question(self, question: PrebuildQuestion) -> list[PrebuildTextWarning]:
        return []

    def check_answer(
        self, question: PrebuildQuestion, answer: PrebuildAnswer
    ) -> list[PrebuildTextWarning]:
        return []

    def _process_question(self, question: PrebuildQuestion):
        question_copy = copy.deepcopy(question)
        warnings = []
        for answer in question.answers:
            warnings.extend(self.check_answer(question_copy, answer))
        warnings.extend(self.check_question(question))
        return warnings
