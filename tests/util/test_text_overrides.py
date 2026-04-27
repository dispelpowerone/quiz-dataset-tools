import unittest
import os
import tempfile
from quiz_dataset_tools.util.text_overrides import TextOverrides
from quiz_dataset_tools.util.language import Language


class TestTextOverridesInMemory(unittest.TestCase):
    def setUp(self):
        self.overrides = TextOverrides(data_path="/tmp/test")

    def test_get_returns_none_when_empty(self):
        result = self.overrides.get(Language.EN, "hello", "ctx", Language.FR)
        self.assertIsNone(result)

    def test_put_and_get(self):
        self.overrides.put(Language.EN, "hello", "ctx", Language.FR, "bonjour")
        result = self.overrides.get(Language.EN, "hello", "ctx", Language.FR)
        self.assertEqual(result, "bonjour")

    def test_different_languages_are_independent(self):
        self.overrides.put(Language.EN, "hello", "ctx", Language.FR, "bonjour")
        self.overrides.put(Language.EN, "hello", "ctx", Language.ES, "hola")
        self.assertEqual(
            self.overrides.get(Language.EN, "hello", "ctx", Language.FR), "bonjour"
        )
        self.assertEqual(
            self.overrides.get(Language.EN, "hello", "ctx", Language.ES), "hola"
        )

    def test_different_contexts_are_independent(self):
        self.overrides.put(Language.EN, "hello", "ctx1", Language.FR, "bonjour1")
        self.overrides.put(Language.EN, "hello", "ctx2", Language.FR, "bonjour2")
        self.assertEqual(
            self.overrides.get(Language.EN, "hello", "ctx1", Language.FR), "bonjour1"
        )
        self.assertEqual(
            self.overrides.get(Language.EN, "hello", "ctx2", Language.FR), "bonjour2"
        )

    def test_put_overwrites(self):
        self.overrides.put(Language.EN, "hello", "ctx", Language.FR, "v1")
        self.overrides.put(Language.EN, "hello", "ctx", Language.FR, "v2")
        self.assertEqual(
            self.overrides.get(Language.EN, "hello", "ctx", Language.FR), "v2"
        )


class TestTextOverridesSaveLoad(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overrides1 = TextOverrides(data_path=tmpdir)
            overrides1.put(Language.EN, "hello", "ctx", Language.FR, "bonjour")
            overrides1.put(Language.EN, "world", "ctx2", Language.ES, "mundo")
            overrides1.save()

            overrides2 = TextOverrides(data_path=tmpdir)
            overrides2.load()
            self.assertEqual(
                overrides2.get(Language.EN, "hello", "ctx", Language.FR), "bonjour"
            )
            self.assertEqual(
                overrides2.get(Language.EN, "world", "ctx2", Language.ES), "mundo"
            )

    def test_load_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            overrides = TextOverrides(data_path=tmpdir)
            overrides.load()
            self.assertEqual(len(overrides.overrides), 0)
