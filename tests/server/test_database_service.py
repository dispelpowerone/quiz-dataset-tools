import unittest
import tempfile
import shutil
import os
from quiz_dataset_tools.util.language import Language, TextLocalizations
from quiz_dataset_tools.prebuild.dbase import PrebuildDBase
from quiz_dataset_tools.prebuild.types import (
    PrebuildText,
    PrebuildTest,
)
from quiz_dataset_tools.server.services.database import DatabaseService
from quiz_dataset_tools.server.models.tests import GetTestsRequest
from quiz_dataset_tools.server.models.questions import (
    GetQuestionsRequest,
    GetQuestionsImageRequest,
)
from quiz_dataset_tools.server.models.text_warnings import GetTextWarningsRequest
from tests.common import make_text, make_question


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.domain = "test"
        domain_dir = os.path.join(self.tmpdir, self.domain, "prebuild")
        os.makedirs(domain_dir)
        # Bootstrap a database with seed data
        dbase = PrebuildDBase(domain_dir)
        dbase.bootstrap()
        dbase.add_test(PrebuildTest(test_id=1, title=make_text(100, "Test 1"), position=1))
        dbase.add_test(PrebuildTest(test_id=2, title=make_text(101, "Test 2"), position=2))
        dbase.add_question(make_question(1, 1, 200, "Q1", image="img.png"))
        dbase.add_question(make_question(1, 2, 202, "Q2", image="img.png"))
        dbase.add_question(make_question(2, 3, 204, "Q3"))
        dbase.close()

        # Override domains_list and create service
        self._original_domains = DatabaseService.domains_list
        DatabaseService.domains_list = [self.domain]
        self.service = DatabaseService(self.tmpdir)

    def tearDown(self):
        for dbase in self.service.domain_dbase.values():
            dbase.close()
        DatabaseService.domains_list = self._original_domains
        shutil.rmtree(self.tmpdir)

    def test_get_domains(self):
        self.assertEqual(self.service.get_domains(), ["test"])

    def test_get_data_dir(self):
        self.assertEqual(
            self.service.get_data_dir("test"),
            f"{self.tmpdir}/test/prebuild",
        )

    def test_get_tests(self):
        req = GetTestsRequest(domain="test")
        resp = self.service.get_tests(req)
        self.assertEqual(resp.error_code, 0)
        self.assertEqual(len(resp.payload), 2)
        self.assertEqual(resp.payload[0].test_id, 1)

    def test_get_questions(self):
        req = GetQuestionsRequest(domain="test", test_id=1)
        resp = self.service.get_questions(req)
        self.assertEqual(resp.error_code, 0)
        self.assertEqual(len(resp.payload), 2)

    def test_get_questions_empty_test(self):
        req = GetQuestionsRequest(domain="test", test_id=99)
        resp = self.service.get_questions(req)
        self.assertEqual(resp.error_code, 0)
        self.assertEqual(len(resp.payload), 0)

    def test_get_question_image(self):
        req = GetQuestionsImageRequest(domain="test", image="img.png")
        result = self.service.get_dbase("test").get_question_image("img.png")
        self.assertEqual(result.image, "img.png")
        self.assertEqual(len(result.questions), 2)

    def test_get_text_warnings_empty(self):
        req = GetTextWarningsRequest(domain="test", text_id=200)
        resp = self.service.get_text_warnings(req)
        self.assertEqual(resp.error_code, 0)
        self.assertEqual(len(resp.payload), 0)
