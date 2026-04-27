import unittest
from quiz_dataset_tools.util.language import (
    Language,
    TextLocalization,
    TextLocalizations,
)


class TestLanguageEnum(unittest.TestCase):
    def test_from_id_valid(self):
        self.assertEqual(Language.from_id(1), Language.EN)
        self.assertEqual(Language.from_id(2), Language.FR)
        self.assertEqual(Language.from_id(5), Language.RU)

    def test_from_id_invalid(self):
        self.assertIsNone(Language.from_id(999))
        self.assertIsNone(Language.from_id(0))
        self.assertIsNone(Language.from_id(-1))

    def test_from_name_valid(self):
        self.assertEqual(Language.from_name("EN"), Language.EN)
        self.assertEqual(Language.from_name("FR"), Language.FR)
        self.assertEqual(Language.from_name("ZH"), Language.ZH)
        self.assertEqual(Language.from_name("PT"), Language.PT)

    def test_from_name_invalid(self):
        self.assertIsNone(Language.from_name("XX"))
        self.assertIsNone(Language.from_name("en"))
        self.assertIsNone(Language.from_name(""))


class TestTextLocalizations(unittest.TestCase):
    def test_set_and_get(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello", 1)
        result = locs.get(Language.EN)
        self.assertIsNotNone(result)
        self.assertEqual(result.content, "hello")
        self.assertEqual(result.text_localization_id, 1)

    def test_get_returns_none_when_unset(self):
        locs = TextLocalizations()
        self.assertIsNone(locs.get(Language.FR))

    def test_get_canonical(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "canonical text")
        result = locs.get_canonical()
        self.assertIsNotNone(result)
        self.assertEqual(result.content, "canonical text")

    def test_get_canonical_returns_none_when_no_en(self):
        locs = TextLocalizations()
        locs.set(Language.FR, "bonjour")
        self.assertIsNone(locs.get_canonical())

    def test_transform(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "  hello  ")
        locs.set(Language.FR, "  bonjour  ")
        result = locs.transform(lambda s: s.strip())
        self.assertEqual(result.get(Language.EN).content, "hello")
        self.assertEqual(result.get(Language.FR).content, "bonjour")

    def test_transform_preserves_localization_id(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello", 42)
        result = locs.transform(lambda s: s.upper())
        self.assertEqual(result.get(Language.EN).content, "HELLO")
        self.assertEqual(result.get(Language.EN).text_localization_id, 42)

    def test_transform_skips_none(self):
        locs = TextLocalizations()
        locs.set(Language.EN, "hello")
        result = locs.transform(lambda s: s.upper())
        self.assertIsNone(result.get(Language.FR))
        self.assertEqual(result.get(Language.EN).content, "HELLO")
