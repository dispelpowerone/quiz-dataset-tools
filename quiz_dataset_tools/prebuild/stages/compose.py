import copy
import random
from enum import Enum
from quiz_dataset_tools.prebuild.stage import BaseStage, StageState
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)


class ComposeMode(Enum):
    SKIP = 0
    FIX_MISSED = 1

    @staticmethod
    def from_str(mode: str) -> "ComposeMode":
        mode = mode.upper()
        if mode == "skip":
            return ComposeMode.SKIP
        elif mode == "fix_missed":
            return ComposeMode.FIX_MISSED
        else:
            raise Exception(f"Unknown ComposeMode: {mode}")


class ComposeStage(BaseStage):
    def __init__(
        self, mode: ComposeMode, questions_per_test: int = 0, random_seed: int = 0
    ):
        self.mode = mode
        self.questions_per_test = questions_per_test
        self.random_seed = random_seed

    def process(self, state: StageState) -> StageState:
        result_state = copy.deepcopy(state)
        if self.mode == ComposeMode.SKIP:
            pass
        elif self.mode == ComposeMode.FIX_MISSED:
            result_state.questions = _fill_tests(
                tests=result_state.tests,
                questions_pool=result_state.questions,
                questions_per_test=self.questions_per_test,
                questions_base=result_state.questions,
            )
        return result_state


def _fill_tests(
    tests: list[PrebuildTest],
    questions_pool: list[PrebuildQuestion],
    questions_per_test: int,
    questions_base: list[PrebuildQuestion],
) -> list[PrebuildQuestion]:
    # Init base test question buckets
    test_questions: dict[int, list[PrebuildQuestion]] = {}
    test_question_hashes: dict[int, set[int]] = {}
    for test in tests:
        test_questions[test.test_id] = []
        test_question_hashes[test.test_id] = set()
    # Push base questions we already have
    for question in questions_base:
        question_hash = _question_hash(question)
        test_questions[question.test_id].append(question)
        test_question_hashes[question.test_id].add(question_hash)
    # Create a cop of the pool to shuffle locally
    local_questions_pool = copy.copy(questions_pool)
    # Fill in missed questions
    for test in tests:
        questions = test_questions[test.test_id]
        question_hashes = test_question_hashes[test.test_id]
        # Trim extra questions
        # while len(questions_set) > questions_per_test:
        #     questions_set.pop(random.choice(questions_set.keys()))
        if len(questions) > questions_per_test:
            raise Exception(
                f"Number of questions is expected lower than {questions_per_test}, got {questions}"
            )
        # Add missing questions
        pool_end = len(local_questions_pool)
        while len(questions) < questions_per_test and pool_end > 0:
            question_index = random.randrange(0, pool_end)
            question_hash = _question_hash(local_questions_pool[question_index])
            if question_hash not in question_hashes:
                question = copy.deepcopy(local_questions_pool[question_index])
                question.test_id = test.test_id
                question.question_id = len(questions) + 1
                questions.append(question)
                question_hashes.add(question_hash)
            pool_end -= 1
            local_questions_pool[question_index], local_questions_pool[pool_end] = (
                local_questions_pool[pool_end],
                local_questions_pool[question_index],
            )
    # Build result list
    result_questions: list[PrebuildQuestion] = []
    for test in tests:
        result_questions.extend(test_questions[test.test_id])
    return result_questions


def _question_hash(question: PrebuildQuestion) -> int:
    return question.test_id * 100 + question.question_id


"""
def _rebuild_tests_with_shuffle(tests: list[Test], questions_per_test: int):
    questions_pool = []
    for test in tests:
        questions_pool.extend(test.questions)
    expected_questions_count = len(tests) * questions_per_test
    base_questions_count = len(questions_pool)
    if base_questions_count < questions_per_test:
        raise Exception(f"Not enough questions: {base_questions_count}")
    if base_questions_count > expected_questions_count:
        raise Exception(
            f"Too many questions: {base_questions_count}, tests: {len(tests)}"
        )

    while len(questions_pool) < expected_questions_count:
        question_index = random.randrange(0, base_questions_count)
        questions_pool.append(questions_pool[question_index])

    random.shuffle(questions_pool)

    final_tests = copy.deepcopy(tests)
    for i, test in enumerate(final_tests):
        begin_index = i * questions_per_test
        end_index = begin_index + questions_per_test
        test.questions = questions_pool[begin_index:end_index]

    return final_tests
"""
