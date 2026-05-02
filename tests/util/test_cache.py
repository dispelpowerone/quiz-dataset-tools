import unittest
import os
import tempfile
from unittest.mock import patch
from quiz_dataset_tools.util.cache import StringCache


class TestStringCache(unittest.TestCase):
    def test_empty_string_returns_empty(self):
        cache = StringCache(domain="test", name="test")
        result = cache.get_or_retrieve("", lambda s: "should not be called")
        self.assertEqual(result, "")

    def test_cache_miss_calls_retriever(self):
        cache = StringCache(domain="test", name="test")
        result = cache.get_or_retrieve("hello", lambda s: s.upper())
        self.assertEqual(result, "HELLO")

    def test_cache_hit_skips_retriever(self):
        cache = StringCache(domain="test", name="test")
        cache.cache["hello"] = "cached_value"
        result = cache.get_or_retrieve("hello", lambda s: "should not be called")
        self.assertEqual(result, "cached_value")

    def test_cache_stores_result(self):
        cache = StringCache(domain="test", name="test")
        cache.get_or_retrieve("key", lambda s: "value")
        self.assertEqual(cache.cache["key"], "value")

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "test.cache")
            with (
                patch.object(
                    StringCache,
                    "CACHE_FILE_TEMPL",
                    os.path.join(tmpdir, "{}/{}.cache"),
                ),
                patch.object(
                    StringCache,
                    "CACHE_FILE_TEMP_TEMPL",
                    os.path.join(tmpdir, "{}/{}.cache.tmp"),
                ),
            ):
                cache1 = StringCache(domain="d", name="n")
                cache1.cache = {"key1": "val1", "key2": "val2"}
                cache1.save()

                cache2 = StringCache(domain="d", name="n")
                cache2.load()
                self.assertEqual(cache2.cache["key1"], "val1")
                self.assertEqual(cache2.cache["key2"], "val2")
