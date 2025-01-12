from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.build.orm import (
    BaseOrm,
    LanguageOrm,
    TextLocalizationOrm,
    TextOrm,
    QuestionOrm,
    TestOrm,
)
from quiz_dataset_tools.build.types import (
    MainText,
    MainAnswer,
    MainQuestion,
    MainTest,
)


def _session_decorator(func):
    def wrapper(dbase, *args, **kwargs):
        Session = sessionmaker(dbase.engine)
        with Session() as session:
            return func(dbase, session, *args, **kwargs)

    return wrapper


class MainDBase:
    def __init__(self, data_dir: str):
        database_path = f"{data_dir}/main.db"
        self.engine = create_engine(f"sqlite:///{database_path}", echo=False)

    def close(self):
        self.engine.dispose()

    def bootstrap(self) -> None:
        self._bootstrap_tables()
        self._bootstrap_languages()

    @_session_decorator
    def get_questions(self, session) -> list[MainQuestion]:
        result = session.execute(select(QuestionOrm))
        return [entry.to_obj() for entry in result.scalars()]

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
