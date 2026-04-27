import unittest
import os
import tempfile
import json
from quiz_dataset_tools.util.fs import (
    prepare_output_dir,
    list_partial_files,
    backup_file,
)


class TestPrepareOutputDir(unittest.TestCase):
    def test_creates_new_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "new_dir")
            prepare_output_dir(target)
            self.assertTrue(os.path.isdir(target))

    def test_cleans_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "existing")
            os.makedirs(target)
            # Create a file inside
            with open(os.path.join(target, "file.txt"), "w") as f:
                f.write("data")
            prepare_output_dir(target)
            self.assertTrue(os.path.isdir(target))
            self.assertEqual(os.listdir(target), [])


class TestListPartialFiles(unittest.TestCase):
    def test_finds_sequential_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(1, 4):
                with open(os.path.join(tmpdir, f"out.{i}.json"), "w") as f:
                    f.write("{}")
            template = os.path.join(tmpdir, "out.__INDEX__.json")
            result = list_partial_files(template)
            self.assertEqual(len(result), 3)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template = os.path.join(tmpdir, "out.__INDEX__.json")
            result = list_partial_files(template)
            self.assertEqual(result, [])

    def test_gap_in_sequence_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files 1 and 3 (skip 2)
            for i in [1, 3]:
                with open(os.path.join(tmpdir, f"out.{i}.json"), "w") as f:
                    f.write("{}")
            template = os.path.join(tmpdir, "out.__INDEX__.json")
            with self.assertRaises(Exception):
                list_partial_files(template)


class TestBackupFile(unittest.TestCase):
    def test_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original = os.path.join(tmpdir, "data.json")
            with open(original, "w") as f:
                f.write("content")
            backup_path = backup_file(original)
            self.assertTrue(os.path.exists(backup_path))
            with open(backup_path, "r") as f:
                self.assertEqual(f.read(), "content")
            # Original still exists
            self.assertTrue(os.path.exists(original))
