import unittest
from quiz_dataset_tools.prebuild.translation.translation import is_stable_text


class TestIsStableText(unittest.TestCase):
    def test_percentage(self):
        self.assertTrue(is_stable_text("0.08%"))

    def test_single_letter(self):
        self.assertTrue(is_stable_text("A"))
        self.assertTrue(is_stable_text("B"))

    def test_comma_separated_letters(self):
        self.assertTrue(is_stable_text("A, B, C, D"))

    def test_semicolon_separated(self):
        self.assertTrue(is_stable_text("X=1; Y=2"))

    def test_kmh(self):
        self.assertTrue(is_stable_text("60 km/h"))
        self.assertTrue(is_stable_text("100 km/h"))

    def test_mph(self):
        self.assertTrue(is_stable_text("30 mph"))
        self.assertTrue(is_stable_text("65 mph"))

    def test_numbers_only(self):
        self.assertTrue(is_stable_text("123"))
        self.assertTrue(is_stable_text("3.14"))

    def test_dollar_amount(self):
        self.assertTrue(is_stable_text("$100"))

    def test_regular_text_not_stable(self):
        self.assertFalse(is_stable_text("What does this sign mean?"))
        self.assertFalse(is_stable_text("Turn left at the intersection"))
        self.assertFalse(is_stable_text("Always check your mirrors"))

    def test_short_words_not_stable(self):
        self.assertFalse(is_stable_text("Yes"))
        self.assertFalse(is_stable_text("No"))

    def test_whitespace_handling(self):
        self.assertTrue(is_stable_text("  0.08%  "))
        self.assertTrue(is_stable_text("  A  "))
