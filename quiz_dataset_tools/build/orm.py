import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.build.types import (
    MainText,
    MainAnswer,
    MainQuestion,
    MainTest,
)


# declarative base class
class BaseOrm(DeclarativeBase):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class LanguageOrm(BaseOrm):
    __tablename__ = "Languages"

    LanguageId: Mapped[int] = mapped_column(primary_key=True)
    LanguageName: Mapped[str]


class TextOrm(BaseOrm):
    __tablename__ = "Texts"

    TextId: Mapped[int] = mapped_column(primary_key=True)
    Description: Mapped[str | None]

    Localizations: Mapped[List["TextLocalizationOrm"]] = relationship(
        back_populates="Text"
    )

    def to_obj(self) -> MainText:
        return MainText(
            text_id=self.TextId,
            localizations=TextLocalizationOrm.to_obj(self.Localizations),
        )


class TextLocalizationOrm(BaseOrm):
    __tablename__ = "TextLocalizations"

    TextLocalizationId: Mapped[int] = mapped_column(primary_key=True)
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    LanguageId: Mapped[int] = mapped_column(ForeignKey("Languages.LanguageId"))
    Content: Mapped[str]

    Text: Mapped["TextOrm"] = relationship(back_populates="Localizations")

    @staticmethod
    def to_obj(orms: list["TextLocalizationOrm"]) -> TextLocalizations:
        obj = TextLocalizations()
        for orm in orms:
            lang = Language.from_id(orm.LanguageId)
            assert lang
            obj.set(lang, orm.Content)
        return obj


class AnswerOrm(BaseOrm):
    __tablename__ = "Answers"

    AnswerId: Mapped[int] = mapped_column(primary_key=True)
    QuestionId: Mapped[int] = mapped_column(ForeignKey("Questions.QuestionId"))
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    IsCorrect: Mapped[bool]

    Text: Mapped["TextOrm"] = relationship()

    def to_obj(self) -> MainAnswer:
        return MainAnswer(
            answer_id=self.AnswerId,
            question_id=self.QuestionId,
            text=self.Text.to_obj(),
            is_correct=self.IsCorrect,
        )


class QuestionOrm(BaseOrm):
    __tablename__ = "Questions"

    QuestionId: Mapped[int] = mapped_column(primary_key=True)
    TestId: Mapped[int] = mapped_column(ForeignKey("Tests.TestId"))
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    Image: Mapped[str | None]

    Text: Mapped["TextOrm"] = relationship()
    Answers: Mapped[List["AnswerOrm"]] = relationship()

    def to_obj(self) -> MainQuestion:
        return MainQuestion(
            test_id=self.TestId,
            question_id=self.QuestionId,
            text=self.Text.to_obj(),
            answers=[a.to_obj() for a in self.Answers],
        )


class TestOrm(BaseOrm):
    __tablename__ = "Tests"

    TestId: Mapped[int] = mapped_column(primary_key=True)
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    Position: Mapped[int | None]

    Title: Mapped["TextOrm"] = relationship()
