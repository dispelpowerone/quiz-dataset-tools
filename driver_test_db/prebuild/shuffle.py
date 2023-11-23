import copy
import random
from driver_test_db.util.data import Test


class TestsShuffler:
    def __init__(self, questions_per_test: int, random_shuffle: bool):
        self.questions_per_test = questions_per_test
        self.random_shuffle = random_shuffle

    def shuffle(self, tests: list[Test]):
        if self.random_shuffle:
            return _rebuild_tests_with_shuffle(tests, self.questions_per_test)


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
