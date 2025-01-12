from dataclasses import dataclass
from quiz_dataset_tools.util.language import Language, TextLocalizations


@dataclass
class MainText:
    localizations: TextLocalizations
    text_id: int | None = None


@dataclass
class MainAnswer:
    text: MainText
    is_correct: bool
    answer_id: int | None = None
    question_id: int | None = None


@dataclass
class MainQuestion:
    test_id: int
    question_id: int
    text: MainText
    answers: list[MainAnswer]


@dataclass
class MainTest:
    test_id: int
    title: MainText
    position: int | None = None
