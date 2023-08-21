from dataclasses import dataclass


@dataclass
class Answer:
    text: str
    is_right_answer: bool

    def transform(self, text_transformer):
        return Answer(
            text=text_transformer(self.text),
            is_right_answer=self.is_right_answer,
        )


@dataclass
class Question:
    text: str
    image: str
    answers: list[Answer]

    def transform(self, text_transformer):
        return Question(
            text=text_transformer(self.text),
            image=self.image,
            answers=[answer.transform(text_transformer) for answer in self.answers],
        )

    def transform_question_text(self, text_transformer):
        return Question(
            text=text_transformer(self.text),
            image=self.image,
            answers=self.answers,
        )


@dataclass
class Test:
    title: str
    questions: list[Question]

    def transform(self, text_transformer):
        return Test(
            title=self.title,
            questions=[
                question.transform(text_transformer) for question in self.questions
            ],
        )

    def transform_question_texts(self, text_transformer):
        return Test(
            title=self.title,
            questions=[
                question.transform_question_text(text_transformer)
                for question in self.questions
            ],
        )
