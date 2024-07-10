from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.fs import backup_file
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.prebuild.orm import (
    BaseOrm,
    LanguageOrm,
    TextOrm,
    QuestionOrm,
    TestOrm,
)


def _session_decorator(func):
    def wrapper(dbase, *args, **kwargs):
        Session = sessionmaker(dbase.engine)
        with Session() as session:
            return func(dbase, session, *args, **kwargs)

    return wrapper


class PrebuildDBase:
    def __init__(self, data_dir: str, backup: bool = False):
        database_path = f"{data_dir}/prebuild.db"
        if backup:
            self._backup_database(database_path)
        self.engine = create_engine(f"sqlite:///{database_path}", echo=False)

    def close(self):
        self.engine.dispose()

    def bootstrap(self) -> None:
        self._bootstrap_tables()
        self._bootstrap_languages()

    @_session_decorator
    def add_test(self, session, test: PrebuildTest) -> None:
        session.add(TestOrm.from_obj(test))
        session.commit()

    @_session_decorator
    def update_test(self, session, test: PrebuildTest) -> None:
        test_orm = session.query(TestOrm).where(TestOrm.TestId == test.test_id).first()
        assert (
            test_orm is not None
        ), f"Cant find test in the dbase, test_id = {test.test_id}"
        test_orm.update(test)
        session.commit()

    @_session_decorator
    def add_question(self, session, question: PrebuildQuestion) -> None:
        session.add(QuestionOrm.from_obj(question))
        session.commit()

    @_session_decorator
    def update_question(self, session, question: PrebuildQuestion) -> None:
        question_orm = (
            session.query(QuestionOrm)
            .where(QuestionOrm.QuestionId == question.question_id)
            .first()
        )
        assert (
            question_orm is not None
        ), f"Cant find question in the dbase, question_id = {question.question_id}"
        question_orm.update(question)
        session.commit()

    @_session_decorator
    def get_tests(self, session) -> list[PrebuildTest]:
        result = session.execute(select(TestOrm))
        return [orm.to_obj() for orm in result.scalars()]

    @_session_decorator
    def get_questions(self, session) -> list[PrebuildQuestion]:
        result = session.execute(select(QuestionOrm))
        return [orm.to_obj() for orm in result.scalars()]

    @_session_decorator
    def get_questions_by_test(self, session, test_id: int) -> list[PrebuildQuestion]:
        result = session.execute(
            select(QuestionOrm).where(QuestionOrm.TestId == test_id)
        )
        return [orm.to_obj() for orm in result.scalars()]

    @_session_decorator
    def update_text(self, session, text: PrebuildText) -> None:
        text_orm = session.query(TextOrm).where(TextOrm.TextId == text.text_id).first()
        assert (
            text_orm is not None
        ), f"Cant find text in the dbase, text_id = {text.text_id}"
        text_orm.update(text)
        session.commit()

    def _backup_database(self, database_path) -> None:
        backup_file(database_path)

    def _bootstrap_tables(self) -> None:
        BaseOrm.metadata.drop_all(self.engine)
        BaseOrm.metadata.create_all(self.engine)

    @_session_decorator
    def _bootstrap_languages(self, session) -> None:
        for lang in Language:
            session.add(
                LanguageOrm(
                    LanguageId=lang.value.language_id,
                    LanguageName=lang.value.name,
                )
            )
        session.commit()


"""
dbase = PrebuildDBase("/Users/d.vasilyev/Workspace/quiz-dataset-tools")
tests = dbase.get_tests()
print(tests[0])
tests[0].title.localizations.ES = "fake ES"
dbase.update_test(tests[0])
tests = dbase.get_tests()
print(tests[0])
"""
