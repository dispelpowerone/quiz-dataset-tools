import unittest
from quiz_dataset_tools.prebuild.doctor.common import is_ok_response


class TestIsOkResponse(unittest.TestCase):
    def test_exact_ok(self):
        self.assertTrue(is_ok_response("OK"))

    def test_case_insensitive(self):
        self.assertTrue(is_ok_response("ok"))
        self.assertTrue(is_ok_response("Ok"))

    def test_with_whitespace(self):
        self.assertTrue(is_ok_response("  OK  "))
        self.assertTrue(is_ok_response("\nOK\n"))
        self.assertTrue(is_ok_response("\t OK \t"))

    def test_with_quotes(self):
        self.assertTrue(is_ok_response("'OK'"))
        self.assertTrue(is_ok_response('"OK"'))
        self.assertTrue(is_ok_response("`OK`"))
        self.assertTrue(is_ok_response("«OK»"))

    def test_with_punctuation(self):
        self.assertTrue(is_ok_response(".OK."))
        self.assertTrue(is_ok_response("...OK..."))

    def test_ends_with_ok_space_separated(self):
        self.assertTrue(is_ok_response("is OK"))
        self.assertTrue(is_ok_response("looks OK"))

    def test_ends_with_ok_newline(self):
        self.assertTrue(is_ok_response("result\nOK"))

    def test_invalid_responses(self):
        self.assertFalse(is_ok_response("OKAY"))
        self.assertFalse(is_ok_response("NOT OK AT ALL"))
        self.assertFalse(is_ok_response(""))
        self.assertFalse(is_ok_response("NO"))
        self.assertFalse(is_ok_response("bad"))
