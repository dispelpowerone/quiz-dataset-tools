import sqlite3
import os
import csv
from dataclasses import dataclass
from typing import Any


class BaseDBO:
    __table__ = ""
    __key__ = ""
    __fields__: list[str] = []
    __create_table__ = ""

    @classmethod
    def get_table(cls) -> str:
        return cls.__table__

    @classmethod
    def get_key(cls) -> str:
        return cls.__key__

    @classmethod
    def get_fields(cls) -> str:
        return ", ".join(cls.__fields__)

    @classmethod
    def get_field_placeholders(cls) -> str:
        return ", ".join("?" * len(cls.__fields__))

    @classmethod
    def get_create_table(cls) -> str:
        return cls.__create_table__

    def get_field_values(self) -> tuple:
        return ()

    @staticmethod
    def make(row: list[str]) -> "BaseDBO":
        return BaseDBO()


@dataclass
class TestDBO(BaseDBO):
    test_id: int
    text_id: int

    __table__ = "Tests"
    __key__ = "TestId"
    __fields__ = ["TestId", "TextId"]
    __create_table__ = """
CREATE TABLE "Tests" (
    "TestId"    INTEGER NOT NULL UNIQUE,
    "TextId"    INTEGER,
    PRIMARY KEY("TestId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "TestDBO":
        return TestDBO(test_id=int(row[0]), text_id=int(row[1]))

    def get_key_values(self) -> tuple[int]:
        return (self.test_id,)

    def get_field_values(self) -> tuple[int, int]:
        return (self.test_id, self.text_id)


@dataclass
class QuestionDBO(BaseDBO):
    question_id: int
    test_id: int
    text_id: int
    image: str

    __table__ = "Questions"
    __key__ = "QuestionId"
    __fields__ = ["QuestionId", "TestId", "TextId", "Image"]
    __create_table__ = """
CREATE TABLE "Questions" (
    "QuestionId"    INTEGER NOT NULL UNIQUE,
    "TestId"    INTEGER,
    "TextId"    INTEGER,
    "Image"    TEXT,
    PRIMARY KEY("QuestionId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "QuestionDBO":
        return QuestionDBO(
            question_id=int(row[0]),
            test_id=int(row[1]),
            text_id=int(row[2]),
            image=row[3],
        )

    def get_key_values(self) -> tuple[int]:
        return (self.question_id,)

    def get_field_values(self) -> tuple[int, int, int, str]:
        return (self.question_id, self.test_id, self.text_id, self.image)


@dataclass
class AnswerDBO(BaseDBO):
    answer_id: int
    question_id: int
    text_id: int
    is_correct: int

    __table__ = "Answers"
    __key__ = "AnswerId"
    __fields__ = ["AnswerId", "QuestionId", "TextId", "IsCorrect"]
    __create_table__ = """
CREATE TABLE "Answers" (
    "AnswerId"    INTEGER NOT NULL UNIQUE,
    "QuestionId"    INTEGER,
    "TextId"    INTEGER,
    "IsCorrect"    INTEGER,
    PRIMARY KEY("AnswerId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "AnswerDBO":
        return AnswerDBO(
            answer_id=int(row[0]),
            question_id=int(row[1]),
            text_id=int(row[2]),
            is_correct=int(row[3]),
        )

    def get_key_values(self) -> tuple[int]:
        return (self.answer_id,)

    def get_field_values(self) -> tuple[int, int, int, int]:
        return (self.answer_id, self.question_id, self.text_id, self.is_correct)


@dataclass
class TextDBO(BaseDBO):
    text_id: int
    description: str

    __table__ = "Texts"
    __key__ = "TextId"
    __fields__ = ["TextId", "Description"]
    __create_table__ = """
CREATE TABLE "Texts" (
    "TextId"    INTEGER NOT NULL UNIQUE,
    "Description"    TEXT,
    PRIMARY KEY("TextId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "TextDBO":
        return TextDBO(text_id=int(row[0]), description=row[1])

    def get_key_values(self) -> tuple[int]:
        return (self.text_id,)

    def get_field_values(self) -> tuple[int, str]:
        return (self.text_id, self.description)


@dataclass
class TextLocalizationDBO(BaseDBO):
    text_localization_id: int
    text_id: int
    language_id: int
    content: str

    __table__ = "TextLocalizations"
    __key__ = "TextLocalizationId"
    __fields__ = ["TextLocalizationId", "TextId", "LanguageId", "Content"]
    __create_table__ = """
CREATE TABLE "TextLocalizations" (
    "TextLocalizationId"    INTEGER NOT NULL UNIQUE,
    "TextId"    INTEGER,
    "LanguageId"    INTEGER NOT NULL,
    "Content"    TEXT,
    PRIMARY KEY("TextLocalizationId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "TextLocalizationDBO":
        return TextLocalizationDBO(
            text_localization_id=int(row[0]),
            text_id=int(row[1]),
            language_id=int(row[2]),
            content=row[3],
        )

    def get_key_values(self) -> tuple[int]:
        return (self.text_localization_id,)

    def get_field_values(self) -> tuple[int, int, int, str]:
        return (self.text_localization_id, self.text_id, self.language_id, self.content)


@dataclass
class LanguageDBO(BaseDBO):
    language_id: int
    language_name: str

    __table__ = "Languages"
    __key__ = "LanguageId"
    __fields__ = ["LanguageId", "LanguageName"]
    __create_table__ = """
CREATE TABLE "Languages" (
    "LanguageId"    INTEGER NOT NULL UNIQUE,
    "LanguageName"    TEXT,
    PRIMARY KEY("LanguageId" AUTOINCREMENT)
)
    """

    @staticmethod
    def make(row: list[str]) -> "LanguageDBO":
        return LanguageDBO(
            language_id=int(row[0]),
            language_name=row[1],
        )

    def get_key_values(self) -> tuple[int]:
        return (self.language_id,)

    def get_field_values(self) -> tuple[int, str]:
        return (self.language_id, self.language_name)


class DBase:
    def __init__(self, dbase_path: str):
        self.dbase_path = dbase_path

    def drop(self):
        if os.path.exists(self.dbase_path):
            os.remove(self.dbase_path)

    def open(self):
        self.cursor = sqlite3.connect(self.dbase_path)
        self.cursor.execute("pragma encoding=UTF8")

    def create_table(self, dbo_type: BaseDBO):
        self.cursor.execute(f"{dbo_type.get_create_table()}")

    def import_csv(self, dbo_type: BaseDBO, file_name: str):
        with open(file_name) as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                self.add(dbo_type.make(row))

    def get(self, dbo_type: BaseDBO, key: Any) -> BaseDBO | None:
        res = self.cursor.execute(
            f"SELECT {dbo_type.get_fields()} from {dbo_type.get_table()} where {dbo_type.get_key()} = ?",
            (key,),
        )
        row = res.fetchone()
        if not row:
            return None
        return dbo_type.make(row)

    def add(self, dbo: BaseDBO) -> int:
        res = self.cursor.execute(
            f"INSERT INTO {dbo.get_table()}({dbo.get_fields()}) VALUES ({dbo.get_field_placeholders()})",
            dbo.get_field_values(),
        )
        return res.lastrowid

    def select(self, dbo_type: BaseDBO, condition: str = "1") -> list[BaseDBO]:
        res = self.cursor.execute(
            f"SELECT {dbo_type.get_fields()} from {dbo_type.get_table()} where {condition}"
        )
        results = []
        for row in res.fetchall():
            results.append(dbo_type.make(row))
        return results

    def commit_and_close(self):
        self.cursor.commit()
        self.cursor.close()


class DriverTestDBase:
    def __init__(self, dbase_path="DriveTest.db"):
        self.dbase = DBase(dbase_path)

    def bootstrap(self):
        self.dbase.drop()
        self.dbase.open()

        self.dbase.create_table(TestDBO)
        self.dbase.create_table(QuestionDBO)
        self.dbase.create_table(AnswerDBO)
        self.dbase.create_table(TextDBO)
        self.dbase.create_table(TextLocalizationDBO)
        self.dbase.create_table(LanguageDBO)

        self.dbase.import_csv(TextDBO, "bootstrap_data/Texts.csv")
        self.dbase.import_csv(
            TextLocalizationDBO, "bootstrap_data/TextLocalizations.csv"
        )
        self.dbase.import_csv(LanguageDBO, "bootstrap_data/Languages.csv")

    def open(self):
        self.dbase.open()

    def add_test_if_not_exists(self, test_id):
        test = self.dbase.get(TestDBO, test_id)
        if not test:
            test = TestDBO(
                test_id=test_id, text_id=self.add_text(f"Test {test_id} title")
            )
            self.dbase.add(test)
        return test

    def add_question_if_not_exists(self, test_id, question_index, image):
        question_id = 100 * test_id + question_index
        question = self.dbase.get(QuestionDBO, question_id)
        if not question:
            question = QuestionDBO(
                question_id=question_id,
                test_id=test_id,
                text_id=self.add_text(f"Question {question_id} content"),
                image=image,
            )
            self.dbase.add(question)
        return question

    def add_answer_if_not_exists(self, question_id, answer_index, is_correct):
        answer_id = 10 * question_id + answer_index
        answer = self.dbase.get(AnswerDBO, answer_id)
        if not answer:
            answer = AnswerDBO(
                answer_id=answer_id,
                question_id=question_id,
                text_id=self.add_text(f"Answer {answer_id} content"),
                is_correct=is_correct,
            )
            self.dbase.add(answer)
        return answer

    def add_text(self, description):
        text = TextDBO(text_id=None, description=description)
        return self.dbase.add(text)

    def add_text_localization(self, text_id, language_id, content):
        text_loc = TextLocalizationDBO(
            text_localization_id=None,
            text_id=text_id,
            language_id=language_id,
            content=content,
        )
        return self.dbase.add(text_loc)

    """
    self.dbase.create_table(TestDBO)
        self.dbase.create_table()
        self.dbase.create_table(AnswerDBO)
        self.dbase.create_table(TextDBO)
        self.dbase.create_table(TextLocalizationDBO)
        self.dbase.create_table(LanguageDBO)
    """

    def get_tests(self):
        return self.dbase.select(TestDBO)

    def get_test(self, test_id):
        return self.dbase.get(TestDBO, test_id)

    def get_questions(self):
        return self.dbase.select(QuestionDBO)

    def get_test_questions(self, test_id):
        return self.dbase.select(QuestionDBO, f"TestId = {test_id}")

    def get_question(self, question_id):
        return self.dbase.get(QuestionDBO, question_id)

    def get_answer(self, answer_id):
        return self.dbase.get(AnswerDBO, answer_id)

    def get_question_answers(self, question_id):
        return self.dbase.select(AnswerDBO, f"QuestionId = {question_id}")

    def get_text(self, text_id):
        return self.dbase.get(TextDBO, text_id)

    def get_texts(self):
        return self.dbase.select(TextDBO)

    def get_text_localizations(self, text_id):
        return self.dbase.select(TextLocalizationDBO, f"TextId = {text_id}")

    def get_text_localization(self, text_id, language_id):
        return self.dbase.select(
            TextLocalizationDBO, f"TextId = {text_id} and LanguageId = {language_id}"
        )

    def get_language(self, language_id):
        return self.dbase.get(LanguageDBO, language_id)

    def commit_and_close(self):
        self.dbase.commit_and_close()
