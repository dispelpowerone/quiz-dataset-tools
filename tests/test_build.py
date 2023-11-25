import unittest
from unittest.mock import MagicMock
from driver_test_db.util.language import Language
from driver_test_db.util.builder import DatabaseBuilder
from driver_test_db.prebuild.types import PrebuildTest, PrebuildQuestion, PrebuildText
from driver_test_db.fakes.dbase import FakeDriverTestDBase


class TestDatabaseBuilder(unittest.TestCase):
    def setUp(self):
        self.dbase = FakeDriverTestDBase()
        self.builder = DatabaseBuilder()
        self._make_database_connection = MagicMock(return_value=self.dbase)

    def test_build(self):
        self.builder.set_prebuild_tests([PrebuildTest(test_id=1, title="Test 1")])
        self.builder.set_prebuild_questions(
            [
                PrebuildQuestion(
                    test_id=1,
                    question_id=1,
                    text=PrebuildText(
                        localizations={Language.EN: "Question 1"}, paraphrase=None
                    ),
                    answers=[],
                )
            ]
        )
        self.builder.build()
