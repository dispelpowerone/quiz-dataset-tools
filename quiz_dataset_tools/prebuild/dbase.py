from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.util.fs import backup_file
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTextWarning,
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.prebuild.orm import (
    BaseOrm,
    LanguageOrm,
    TextOrm,
    TextWarningOrm,
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
        self._drop_tables()
        self._bootstrap_tables()
        self._bootstrap_languages()

    def bootstrap_tables(self) -> None:
        self._bootstrap_tables()

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

    @_session_decorator
    def add_text_warning(self, session, text_warning: PrebuildTextWarning) -> None:
        assert (
            text_warning.text_localization_id is not None
            and text_warning.code is not None
        ), f"Cant add text warning, {text_warning.text_localization_id=}, {text_warning.code=}"
        text_warning_orm = (
            session.query(TextWarningOrm)
            .where(
                (
                    TextWarningOrm.TextLocalizationsId
                    == text_warning.text_localization_id
                )
                & (TextWarningOrm.Code == text_warning.code)
            )
            .first()
        )
        if text_warning_orm:
            text_warning_orm.update(text_warning)
        else:
            session.add(TextWarningOrm.from_obj(text_warning))
        session.commit()

    @_session_decorator
    def update_text_warning(self, session, text_warning: PrebuildTextWarning) -> None:
        text_warning_orm = (
            session.query(TextWarningOrm)
            .where(TextWarningOrm.TextWarningId == text_warning.text_warning_id)
            .first()
        )
        assert (
            text_warning_orm is not None
        ), f"Cant find text warning in the dbase, text_warning_id = {text_warning.text_warning_id}"
        text_warning_orm.update(text_warning)
        session.commit()

    @_session_decorator
    def delete_text_warning(self, session, text_warning: PrebuildTextWarning) -> None:
        session.query(TextWarningOrm).filter(
            (TextWarningOrm.TextLocalizationsId == text_warning.text_localization_id)
            & (TextWarningOrm.Code == text_warning.code)
        ).delete(synchronize_session=False)
        session.commit()

    @_session_decorator
    def get_text_warnings(self, session, text_id: int) -> list[PrebuildTextWarning]:
        result = session.execute(
            select(TextWarningOrm).where(TextWarningOrm.TextId == text_id)
        )
        return [orm.to_obj() for orm in result.scalars()]

    def _backup_database(self, database_path) -> None:
        backup_file(database_path)

    def _drop_tables(self) -> None:
        BaseOrm.metadata.drop_all(self.engine)

    def _bootstrap_tables(self) -> None:
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
dbase = PrebuildDBase(
    "/Volumes/External/Workspace/quiz-dataset-tools/output/domains/on/prebuild/"
)
dbase.bootstrap_tables()
"""
