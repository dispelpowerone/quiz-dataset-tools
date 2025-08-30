import copy
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.parser.parser import Parser
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.data import Test, Question, Answer, TextTransformer
from quiz_dataset_tools.util.fs import dump_list, load_list
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.prebuild.translation.translation import Translator
from quiz_dataset_tools.prebuild.stage import BaseStage, StageState
from quiz_dataset_tools.prebuild.stages.passthrough import PassthroughStage
from quiz_dataset_tools.prebuild.stages.compose import ComposeMode, ComposeStage
from quiz_dataset_tools.prebuild.stages.override import OverrideStage
from quiz_dataset_tools.prebuild.stages.dump_overrides import DumpOverridesStage
from quiz_dataset_tools.prebuild.stages.translate import TranslateStage
from quiz_dataset_tools.prebuild.stages.final import FinalStage
from quiz_dataset_tools.prebuild.stages.doctor import DoctorStage
from quiz_dataset_tools.prebuild.stages.question_comment import (
    QuestionCommentStage,
)


class PrebuildBuilder:
    def __init__(self) -> None:
        self.data_path: str = "data"
        self.output_dir: str = "out"
        self.overrides: TextOverrides | None = None
        self.translator: Translator | None = None
        self.parser: Parser | None = None
        self.languages: list[Language] = []
        self.compose_mode: ComposeMode = ComposeMode.SKIP
        self.questions_per_test: int = 15

    def set_data_path(self, data_path: str) -> None:
        self.data_path = data_path

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

    def set_compose_mode(self, mode: str) -> None:
        self.compose_mode = ComposeMode.from_str(mode)

    def run_init(self) -> None:
        state = self._load_initial_state()
        create_db_stage = FinalStage(self.data_path, self.output_dir)
        create_db_stage.setup()
        create_db_stage.process(state)

    def run_translate(self) -> None:
        assert self.translator
        self._run_stage_on_dbase(TranslateStage(self.translator))

    def run_override(self) -> None:
        assert self.languages
        assert self.overrides
        self._run_stage_on_dbase(OverrideStage(self.languages, self.overrides))

    def run_dump_overrides(self) -> None:
        assert self.languages
        assert self.overrides
        self._run_stage_on_dbase(DumpOverridesStage(self.languages, self.overrides))

    def run_doctor(self, domain: str) -> None:
        doctor_stage = DoctorStage(domain)
        self._run_stage_on_dbase(doctor_stage)
        doctor_stage.flush()

    def run_question_comment(self, domain: str) -> None:
        question_comment_stage = QuestionCommentStage(domain)
        self._run_stage_on_dbase(question_comment_stage)
        question_comment_stage.flush()

    @staticmethod
    def load_tests(data_dir: str) -> list[PrebuildTest]:
        return PrebuildDBase(data_dir).get_tests()

    @staticmethod
    def load_questions(data_dir: str) -> list[PrebuildQuestion]:
        return PrebuildDBase(data_dir).get_questions()

    def _run_stage_on_dbase(self, stage: BaseStage) -> None:
        stage.setup()
        state = self._load_stage_state_from_dbase()
        state = stage.process(state)
        self._save_stage_state_to_dbase(state)

    def _load_initial_state(self) -> StageState:
        assert self.parser
        canonical_tests = self.parser.get_tests()
        prebuild_tests = []
        prebuild_questions: list[PrebuildQuestion] = []
        for test_index, test in enumerate(canonical_tests):
            test_id = test_index + 1
            # Use original test id if available
            if test.orig_id is not None:
                test_id = test.orig_id
            prebuild_tests.append(self._make_prebuild_test(test_id, test))
            for question_index, question in enumerate(test.questions):
                question_id = len(prebuild_questions) + 1
                # Use original question id if available
                if question.orig_id is not None:
                    question_id = question.orig_id
                prebuild_questions.append(
                    self._make_prebuild_question(test_id, question_id, question)
                )
        return StageState(
            tests=prebuild_tests, questions=prebuild_questions, text_warnings=[]
        )

    def _load_stage_state(self, stage_name: str) -> StageState:
        raise Exception("_load_stage_state is deprecated")
        """
        return StageState(
            tests=load_list(
                cls=PrebuildTest,
                source_dir=f"{self.output_dir}/{stage_name}/tests",
            ),
            questions=load_list(
                cls=PrebuildQuestion,
                source_dir=f"{self.output_dir}/{stage_name}/questions",
            ),
        )
        """

    def _load_stage_state_from_dbase(self) -> StageState:
        dbase = PrebuildDBase(f"{self.output_dir}")
        return StageState(
            tests=dbase.get_tests(),
            questions=dbase.get_questions(),
            text_warnings=[],
        )

    def _save_stage_state_to_dbase(self, state: StageState) -> None:
        dbase = PrebuildDBase(f"{self.output_dir}", backup=True)
        for test in state.tests:
            dbase.update_test(test)
        for question in state.questions:
            dbase.update_question(question)
        for text_warning in state.text_warnings:
            if text_warning.content:
                dbase.add_text_warning(text_warning)
            else:
                dbase.delete_text_warning(text_warning)
        dbase.close()

    def _make_prebuild_test(self, test_id, test: Test) -> PrebuildTest:
        return PrebuildTest(
            test_id=test_id,
            title=self._make_prebuild_text(test.title),
            position=test.position,
        )

    def _make_prebuild_question(
        self, test_id, question_id, question: Question
    ) -> PrebuildQuestion:
        return PrebuildQuestion(
            test_id=test_id,
            question_id=question_id,
            text=self._make_prebuild_text(question.text),
            image=question.image,
            audio=question.audio,
            answers=[self._make_prebuild_answer(answer) for answer in question.answers],
        )

    def _make_prebuild_answer(self, answer: Answer) -> PrebuildAnswer:
        return PrebuildAnswer(
            answer_id=answer.orig_id,
            text=self._make_prebuild_text(answer.text),
            is_right_answer=answer.is_right_answer,
        )

    def _make_prebuild_text(self, text: TextLocalizations) -> PrebuildText:
        return PrebuildText(
            localizations=text,
            original=copy.deepcopy(text),
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
