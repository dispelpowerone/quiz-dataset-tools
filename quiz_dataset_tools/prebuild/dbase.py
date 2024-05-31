from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    sessionmaker,
)
from quiz_dataset_tools.util.language import Language
from quiz_dataset_tools.prebuild.types import (
    PrebuildQuestion,
    PrebuildTest,
)
from quiz_dataset_tools.prebuild.orm import (
    BaseOrm,
    LanguageOrm,
    TestOrm,
    QuestionOrm,
)


class PrebuildDBase:
    def __init__(self, data_dir: str):
        self.engine = create_engine(f"sqlite:///{data_dir}/prebuild.db", echo=False)

    def bootstrap(self) -> None:
        self._bootstrap_tables()
        self._bootstrap_languages()

    def add_test(self, test: PrebuildTest) -> None:
        Session = sessionmaker(self.engine)
        with Session() as session:
            session.add(TestOrm.from_obj(test))
            session.commit()

    def add_question(self, question: PrebuildQuestion) -> None:
        Session = sessionmaker(self.engine)
        with Session() as session:
            session.add(QuestionOrm.from_obj(question))
            session.commit()

    def get_tests(self) -> list[PrebuildTest]:
        Session = sessionmaker(self.engine)
        with Session() as session:
            result = session.execute(select(TestOrm))
            return [orm.to_obj() for orm in result.scalars()]

    def get_questions(self) -> list[PrebuildQuestion]:
        return []

    def _bootstrap_tables(self) -> None:
        BaseOrm.metadata.drop_all(self.engine)
        BaseOrm.metadata.create_all(self.engine)

    def _bootstrap_languages(self) -> None:
        Session = sessionmaker(self.engine)
        with Session() as session:
            for lang in Language:
                session.add(
                    LanguageOrm(
                        LanguageId=lang.value.language_id,
                        LanguageName=lang.value.name,
                    )
                )
            session.commit()
