import unittest
from unittest.mock import MagicMock
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.prebuild.stage import StageState
from quiz_dataset_tools.prebuild.stages.dump_overrides import DumpOverridesStage
from quiz_dataset_tools.prebuild.types import (
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
    PrebuildText,
)
from quiz_dataset_tools.prebuild.overrides import (
    make_question_context,
    make_answer_context,
)
from tests.common import make_prebuild_text


class TestDumpOverridesStage(unittest.TestCase):
    def setUp(self):
        pass

    def test_end_to_end(self):
        tests = [
            PrebuildTest(test_id=1, title=make_prebuild_text("Test 1")),
        ]
        questions = [
            PrebuildQuestion(
                test_id=1,
                question_id=1,
                text=make_prebuild_text("foo", es="foo-es", orig="orig-foo"),
                answers=[
                    PrebuildAnswer(
                        make_prebuild_text("boo", es="boo-es", orig="orig-boo"),
                        is_right_answer=True,
                    ),
                    PrebuildAnswer(
                        make_prebuild_text("bar mph", es="bar-es", orig="orig-bar"),
                        is_right_answer=False,
                    ),
                ],
            ),
        ]
        overrides = TextOverrides(data_path="test")
        stage = DumpOverridesStage(
            overrides=overrides, languages=[Language.EN, Language.ES]
        )
        state = stage.process(
            StageState(tests=tests, questions=questions, text_warnings=[])
        )

        self.assertEqual(
            "foo",
            overrides.get(
                Language.EN,
                "orig-foo",
                make_question_context(questions[0]),
                Language.EN,
            ),
        )
        self.assertEqual(
            "foo-es",
            overrides.get(
                Language.EN,
                "orig-foo",
                make_question_context(questions[0]),
                Language.ES,
            ),
        )
        self.assertEqual(
            "boo",
            overrides.get(
                Language.EN,
                "orig-boo",
                make_answer_context(questions[0], questions[0].answers[0]),
                Language.EN,
            ),
        )
        self.assertEqual(
            "boo-es",
            overrides.get(
                Language.EN,
                "orig-boo",
                make_answer_context(questions[0], questions[0].answers[0]),
                Language.ES,
            ),
        )
        self.assertEqual(
            "bar mph",
            overrides.get(
                Language.EN,
                "orig-bar",
                make_answer_context(questions[0], questions[0].answers[1]),
                Language.EN,
            ),
        )
        self.assertEqual(
            "bar-es",
            overrides.get(
                Language.EN,
                "orig-bar",
                make_answer_context(questions[0], questions[0].answers[1]),
                Language.ES,
            ),
        )
