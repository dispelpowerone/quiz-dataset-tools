from driver_test_db.util.text_overrides import TextOverrides
from driver_test_db.translation.translation import (
    Translator,
    TranslationTextTransformer,
    PassThroughTranslator,
)
from driver_test_db.parser.parser import Parser
from driver_test_db.util.language import Language, TextLocalizations
from driver_test_db.util.data import Test, Question, Answer, TextTransformer
from driver_test_db.util.fs import dump_list, load_list
from driver_test_db.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from driver_test_db.prebuild.stage import BaseStage, StageState
from driver_test_db.prebuild.stages.passthrough import PassthroughStage


class PrebuildBuilder:
    def __init__(self) -> None:
        self.output_dir: str = "out"
        self.overrides: TextOverrides | None = None
        self.translator: Translator | None = None
        self.parser: Parser | None = None
        self.languages: list[Language] = []

    def set_output_dir(self, output_dir: str) -> None:
        self.output_dir = output_dir

    def set_translator(self, translator: Translator) -> None:
        self.translator = translator

    def set_overrides(self, overrides: TextOverrides) -> None:
        self.overrides = overrides

    def set_parser(self, parser: Parser) -> None:
        self.parser = parser

    def set_languages(self, languages: list[Language]) -> None:
        self.languages = languages

    def build(self) -> None:
        stages: list[tuple[str, BaseStage]] = []
        stages.append(("init", PassthroughStage()))
        # Prerequisites

        state = self._load_initial_state()
        for stage_name, stage in stages:
            state = stage.process(state)
            self._dump_state(stage_name, state)

    @staticmethod
    def load_tests(data_dir: str) -> list[PrebuildTest]:
        return load_list(
            cls=PrebuildTest,
            source_dir=f"{data_dir}/tests",
        )

    @staticmethod
    def load_questions(data_dir: str) -> list[PrebuildQuestion]:
        return load_list(
            cls=PrebuildQuestion,
            source_dir=f"{data_dir}/questions",
        )

    def _load_initial_state(self) -> StageState:
        assert self.parser
        canonical_tests = self.parser.get_tests()
        prebuild_tests = []
        prebuild_questions = []
        for test_index, test in enumerate(canonical_tests):
            test_id = test_index + 1
            prebuild_tests.append(self._make_prebuild_test(test_id, test))
            for question_index, question in enumerate(test.questions):
                prebuild_questions.append(
                    self._make_prebuild_question(test_id, question_index + 1, question)
                )
        return StageState(tests=prebuild_tests, questions=prebuild_questions)

    def _make_prebuild_test(self, test_id, test: Test) -> PrebuildTest:
        return PrebuildTest(
            test_id=test_id,
            title=self._make_prebuild_text(test.title),
        )

    def _make_prebuild_question(
        self, test_id, question_id, question: Question
    ) -> PrebuildQuestion:
        return PrebuildQuestion(
            test_id=test_id,
            question_id=question_id,
            text=self._make_prebuild_text(question.text),
            image=question.image,
            answers=[self._make_prebuild_answer(answer) for answer in question.answers],
        )

    def _make_prebuild_answer(self, answer: Answer) -> PrebuildAnswer:
        return PrebuildAnswer(
            text=self._make_prebuild_text(answer.text),
            is_right_answer=answer.is_right_answer,
        )

    def _make_prebuild_text(self, text: TextLocalizations) -> PrebuildText:
        return PrebuildText(
            localizations=text,
            paraphrase=None,
        )

    def _dump_state(self, stage_name: str, state: StageState) -> None:
        dump_list(
            cls=PrebuildTest,
            data=state.tests,
            output_dir=f"{self.output_dir}/{stage_name}/tests",
            chunk_size=100,
        )
        dump_list(
            cls=PrebuildQuestion,
            data=state.questions,
            output_dir=f"{self.output_dir}/{stage_name}/questions",
            chunk_size=15,
        )
