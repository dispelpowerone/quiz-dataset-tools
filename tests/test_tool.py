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
        builder.run_question_comment.assert_called_once_with("ca", replace=False)

    @patch("quiz_dataset_tools.tool.tool.PrebuildBuilder")
    def test_question_comments_replaces_existing_comments_when_requested(
        self, builder_class
    ) -> None:
        result = CliRunner().invoke(
            main, ["prebuild-question-comments", "--domain", "ca", "--replace"]
        )

        self.assertEqual(result.exit_code, 0, result.output)
        builder = builder_class.return_value
        builder.run_question_comment.assert_called_once_with("ca", replace=True)
