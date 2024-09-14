import unittest
from quiz_dataset_tools.translation.translation import (
    is_stable_text,
)


class TestTranslation(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_stable_text(self):
        self.assertTrue(is_stable_text("0.08%"))
        self.assertTrue(is_stable_text("A"))
        self.assertTrue(is_stable_text("A, B, C, D"))
        self.assertTrue(is_stable_text("X=1; Y=2"))
        self.assertTrue(is_stable_text("100 km/h"))
        self.assertFalse(is_stable_text("foo boo bar"))
        self.assertFalse(is_stable_text("A, foo"))
