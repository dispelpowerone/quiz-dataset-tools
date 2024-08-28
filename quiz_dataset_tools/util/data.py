from dataclasses import dataclass
from typing import Callable
from quiz_dataset_tools.util.language import TextLocalizations


TextTransformer = Callable[[TextLocalizations], TextLocalizations]


@dataclass
class Answer:
    text: TextLocalizations
    is_right_answer: bool
    orig_id: int | None = None

    def transform_texts(self, text_transformer: TextTransformer) -> "Answer":
        return Answer(
            text=text_transformer(self.text),
            is_right_answer=self.is_right_answer,
            orig_id=self.orig_id,
        )


@dataclass
class Question:
    text: TextLocalizations
    answers: list[Answer]
    orig_id: int | None = None
    image: str | None = None
    audio: str | None = None

    def transform_texts(self, text_transformer: TextTransformer) -> "Question":
        return Question(
            orig_id=self.orig_id,
            text=text_transformer(self.text),
            image=self.image,
            audio=self.audio,
            answers=[
                answer.transform_texts(text_transformer) for answer in self.answers
            ],
        )

    def transform_question_text(self, text_transformer: TextTransformer) -> "Question":
        return Question(
            orig_id=self.orig_id,
            text=text_transformer(self.text),
            image=self.image,
            audio=self.audio,
            answers=self.answers,
        )


@dataclass
class Test:
    title: TextLocalizations
    questions: list[Question]
    position: int | None = None
    orig_id: int | None = None

    def transform_texts(self, text_transformer: TextTransformer) -> "Test":
        return Test(
            title=self.title,
            position=self.position,
            orig_id=self.orig_id,
            questions=[
                question.transform_texts(text_transformer)
                for question in self.questions
            ],
        )

    def transform_question_texts(self, text_transformer: TextTransformer) -> "Test":
        return Test(
            title=self.title,
            position=self.position,
            orig_id=self.orig_id,
            questions=[
                question.transform_question_text(text_transformer)
                for question in self.questions
            ],
        )
