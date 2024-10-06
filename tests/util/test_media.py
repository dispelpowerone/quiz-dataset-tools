import os
import unittest
from unittest.mock import patch, mock_open, call, MagicMock
from quiz_dataset_tools.util.media import MediaIndex, MediaType


class TestMediaIndex(unittest.TestCase):
    def setUp(self):
        self.source_dir = "source"
        self.dest_dir = "destination"
        self.media_type = MediaType.IMAGE
        self.index = MediaIndex(
            media_type=self.media_type,
            source_dir=self.source_dir,
            dest_dir=self.dest_dir,
            preserve_file_names=False,
        )

    @patch("quiz_dataset_tools.util.media.convert_png_to_webp")
    def test_put_new_file(self, mock_convert):
        self.index.put("img1", "image1.png")

        # Ensure the correct file was processed with conversion
        mock_convert.assert_called_once_with(
            "source/image1.png", "destination/img1.webp"
        )

        # Check index and inverted_index
        self.assertEqual(self.index.index["img1"], "img1.webp")
        self.assertEqual(self.index.inverted_index["image1.png"], "img1.webp")

    @patch("quiz_dataset_tools.util.media.convert_png_to_webp")
    def test_put_duplicate_file(self, mock_convert):
        self.index.put("img1", "image1.png")
        self.index.put("img1", "image1.png")

        # Ensure the second put doesn't trigger a copy or conversion again
        mock_convert.assert_called_once()

    def test_put_without_filename(self):
        # Test case where filename is None
        self.index.put("img2", None)

        # Ensure nothing is written in the inverted index for this key
        self.assertEqual(self.index.index["img2"], None)

    @patch("quiz_dataset_tools.util.media.convert_png_to_webp")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_index(self, mock_open_func, mock_convert):
        self.index.put("img1", "image1.png")
        self.index.put("img2", "")
        self.index.put("img3", None)

        # Call save_index
        self.index.save_index()

        # Check that the file was opened for writing and written correctly
        mock_open_func.assert_called_once_with("destination/index.ts", "w")
        mock_open_func().write.assert_called_once_with(
            "export const Images = {\n"
            "  'img1': require('assets/img/questions/img1.webp'),\n"
            "  'img2': null,\n"
            "  'img3': null,\n"
            "};"
        )
