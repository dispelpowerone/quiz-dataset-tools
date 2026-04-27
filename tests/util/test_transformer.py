import unittest
from quiz_dataset_tools.util.transformer import Transformer


class MockTransformer(Transformer):
    def _get(self, src_text: str):
        return src_text.upper()


class TestTransformer(unittest.TestCase):
    def test_empty_string_returns_empty(self):
        t = MockTransformer(domain="test", name="test")
        self.assertEqual(t.get(""), "")

    def test_calls_impl_on_miss(self):
        t = MockTransformer(domain="test", name="test")
        result = t.get("hello")
        self.assertEqual(result, "HELLO")

    def test_cache_hit(self):
        t = MockTransformer(domain="test", name="test")
        t.cache["hello"] = "cached"
        result = t.get("hello")
        self.assertEqual(result, "cached")

    def test_override_takes_priority(self):
        t = MockTransformer(domain="test", name="test")
        t.cache["hello"] = "cached"
        t.overrides["hello"] = "override"
        result = t.get("hello")
        self.assertEqual(result, "override")

    def test_result_stored_in_cache(self):
        t = MockTransformer(domain="test", name="test")
        t.get("world")
        self.assertEqual(t.cache["world"], "WORLD")

    def test_unimplemented_get_raises(self):
        t = Transformer(domain="test", name="test")
        with self.assertRaises(Exception):
            t.get("hello")
