from typing import List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildAnswer,
    PrebuildQuestion,
    PrebuildTest,
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
    Original: Mapped[str | None]

    Localizations: Mapped[List["TextLocalizationOrm"]] = relationship()

    @staticmethod
    def from_obj(obj: PrebuildText) -> "TextOrm":
        original = None
        if obj.original:
            original = obj.original.get(Language.EN)
        return TextOrm(
            Localizations=TextLocalizationOrm.from_obj(obj.localizations),
            Original=original,
        )

    def to_obj(self) -> PrebuildText:
        original = None
        if self.Original is not None:
            original = TextLocalizations()
            original.set(Language.EN, self.Original)
        return PrebuildText(
            localizations=TextLocalizationOrm.to_obj(self.Localizations),
            original=original,
        )


class TextLocalizationOrm(BaseOrm):
    __tablename__ = "TextLocalizations"

    TextLocalizationsId: Mapped[int] = mapped_column(primary_key=True)
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    LanguageId: Mapped[int] = mapped_column(ForeignKey("Languages.LanguageId"))
    Content: Mapped[str]

    @staticmethod
    def from_obj(obj: TextLocalizations) -> list["TextLocalizationOrm"]:
        result = []
        for lang in Language:
            localization = obj.get(lang)
            if localization is None:
                continue
            result.append(
                TextLocalizationOrm(
                    LanguageId=lang.value.language_id, Content=localization
                )
            )
        return result

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
    IsRightAnswer: Mapped[bool]

    Text: Mapped["TextOrm"] = relationship()

    @staticmethod
    def from_obj(obj: PrebuildAnswer) -> "AnswerOrm":
        return AnswerOrm(
            Text=TextOrm.from_obj(obj.text),
            IsRightAnswer=obj.is_right_answer,
        )


class QuestionOrm(BaseOrm):
    __tablename__ = "Questions"

    QuestionId: Mapped[int] = mapped_column(primary_key=True)
    TestId: Mapped[int] = mapped_column(ForeignKey("Tests.TestId"))
    TextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    Image: Mapped[str | None]
    Audio: Mapped[str | None]

    Text: Mapped["TextOrm"] = relationship()
    Answers: Mapped[List["AnswerOrm"]] = relationship()

    @staticmethod
    def from_obj(obj: PrebuildQuestion) -> "QuestionOrm":
        return QuestionOrm(
            TestId=obj.test_id,
            Text=TextOrm.from_obj(obj.text),
            Answers=[AnswerOrm.from_obj(a) for a in obj.answers],
            Image=obj.image,
            Audio=obj.audio,
        )


class TestOrm(BaseOrm):
    __tablename__ = "Tests"

    TestId: Mapped[int] = mapped_column(primary_key=True)
    TitleTextId: Mapped[int] = mapped_column(ForeignKey("Texts.TextId"))
    Position: Mapped[int | None]

    Title: Mapped["TextOrm"] = relationship()

    @staticmethod
    def from_obj(obj: PrebuildTest) -> "TestOrm":
        return TestOrm(
            TestId=obj.test_id,
            Title=TextOrm.from_obj(obj.title),
            Position=obj.position,
        )

    def to_obj(self) -> PrebuildTest:
        return PrebuildTest(
            test_id=self.TestId,
            title=self.Title.to_obj(),
            position=self.Position,
        )
