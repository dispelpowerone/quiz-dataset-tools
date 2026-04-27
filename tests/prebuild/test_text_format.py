import unittest
from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)
from quiz_dataset_tools.prebuild.text_format import (
    strip_text,
    remove_echo_text,
    _remove_echo_from_string,
)


class TestStripText(unittest.TestCase):
    def test_strips_whitespace(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "  hello  ")
        locs.set(Language.FR, "\tbonjour\n")
        result = strip_text(locs)
        self.assertEqual(result.get(Language.EN).content, "hello")
        self.assertEqual(result.get(Language.FR).content, "bonjour")

    def test_no_change_when_clean(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello")
        result = strip_text(locs)
        self.assertEqual(result.get(Language.EN).content, "hello")


class TestRemoveEchoFromString(unittest.TestCase):
    def test_removes_echo(self):
        self.assertEqual(_remove_echo_from_string("hello/hello"), "hello")

    def test_removes_echo_with_spaces(self):
        # slash must be at exact midpoint; spaces around halves are stripped after split
        self.assertEqual(_remove_echo_from_string("hello/hello"), "hello")

    def test_odd_length_echo(self):
        # "hi / hi" has length 7, midpoint char is '/'
        self.assertEqual(_remove_echo_from_string("hi / hi"), "hi")

    def test_no_echo_different_halves(self):
        self.assertEqual(_remove_echo_from_string("hello/world"), "hello/world")

    def test_short_string_unchanged(self):
        self.assertEqual(_remove_echo_from_string("ab"), "ab")
        self.assertEqual(_remove_echo_from_string("a"), "a")
        self.assertEqual(_remove_echo_from_string(""), "")

    def test_no_slash_unchanged(self):
        self.assertEqual(_remove_echo_from_string("hello hello"), "hello hello")

    def test_slash_not_at_midpoint(self):
        self.assertEqual(_remove_echo_from_string("hi/there/hi"), "hi/there/hi")


class TestRemoveEchoText(unittest.TestCase):
    def test_removes_echo_from_localizations(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello/hello")
        locs.set(Language.FR, "bonjour/bonjour")
        result = remove_echo_text(locs)
        self.assertEqual(result.get(Language.EN).content, "hello")
        self.assertEqual(result.get(Language.FR).content, "bonjour")
