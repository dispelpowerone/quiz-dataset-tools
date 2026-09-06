import unittest
from unittest.mock import patch

from click.testing import CliRunner

from quiz_dataset_tools.tool.tool import main


class TestTool(unittest.TestCase):
    @patch("quiz_dataset_tools.tool.tool.PrebuildBuilder")
    def test_question_comments_skips_existing_comments_by_default(
        self, builder_class
    ) -> None:
        result = CliRunner().invoke(
            main, ["prebuild-question-comments", "--domain", "ca"]
        )

        self.assertEqual(result.exit_code, 0, result.output)
        builder = builder_class.return_value
        builder.set_output_dir.assert_called_once_with("output/domains/ca/prebuild")
        builder.run_question_comment.assert_called_once_with(
            "ca", replace=False, test_id=None
        )

    @patch("quiz_dataset_tools.tool.tool.PrebuildBuilder")
    def test_question_comments_replaces_existing_comments_when_requested(
        self, builder_class
    ) -> None:
        result = CliRunner().invoke(
            main, ["prebuild-question-comments", "--domain", "ca", "--replace"]
        )

        self.assertEqual(result.exit_code, 0, result.output)
        builder = builder_class.return_value
        builder.run_question_comment.assert_called_once_with(
            "ca", replace=True, test_id=None
        )

    @patch("quiz_dataset_tools.tool.tool.PrebuildBuilder")
    def test_question_comments_filters_to_test(self, builder_class) -> None:
        result = CliRunner().invoke(
            main,
            ["prebuild-question-comments", "--domain", "ca", "--test", "3"],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        builder_class.return_value.run_question_comment.assert_called_once_with(
            "ca", replace=False, test_id=3
        )

    @patch("quiz_dataset_tools.tool.tool.PrebuildBuilder")
    def test_doctor_filters_to_test(self, builder_class) -> None:
        result = CliRunner().invoke(
            main, ["prebuild-doctor", "--domain", "ca", "--test", "3"]
        )

        self.assertEqual(result.exit_code, 0, result.output)
        builder_class.return_value.run_doctor.assert_called_once_with("ca", test_id=3)

    def test_translate_filters_to_test(self) -> None:
        with (
            patch("quiz_dataset_tools.tool.tool.PrebuildBuilder") as builder_class,
            patch("quiz_dataset_tools.tool.tool.GPTTranslator"),
            patch("quiz_dataset_tools.tool.tool.Translator"),
        ):
            result = CliRunner().invoke(
                main, ["prebuild-translate", "--domain", "ca", "--test", "3"]
            )

        self.assertEqual(result.exit_code, 0, result.output)
        builder_class.return_value.run_translate.assert_called_once_with(test_id=3)
